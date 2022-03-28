import math
import pickle
import random
import sys
import time
import pygame

from typing import List, Union

maze: List[List[int]]
paikat: List[List[int]]
kädessä: List[Union[int, "esine"]]
pelaaja_pisteet: List[int]
salaiset_numerot: List[int]
alotus_aika: int
printattava: str
seinät: List["esine"]
window: pygame.Surface
font: pygame.font
koko: List[int]
koko2: List[int]
pelaajamäärä: int
esineet: List["esine"]
personal_esineet: List["esine"]


class esine:
    def __init__(self, nimi, väri, kuva="ore_coal_1", kuvan_käyttö=0, koko=0):
        self.nimi = nimi
        self.väri = väri
        self.numero = 0
        self.alku_image = pygame.image.load(r"items/" + kuva + ".png")
        if koko == 0:
            self.kuva = pygame.transform.scale(self.alku_image, (zoom * 3, zoom * 3))
        else:
            self.kuva = pygame.transform.scale(self.alku_image, (koko, koko))
        self.kuvan_käyttö = kuvan_käyttö


def tee_kartta(koot):
    global tyhjien_määrä, täysien_määrä
    koot = ((koot[0] * 2 + 1) * 3, (koot[1] * 2 + 1) * 3)
    kartta = [[1 for i in range(koot[1])] for i in range(koot[0])]
    for x in range(1, koot[0], 3):
        for y in range(1, koot[1], 3):
            kartta[x][y] = 3
    for x in range(1, koot[0], 6):
        for y in range(1, koot[1], 6):
            for i, j in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if i > 0 and i < koot[0] - 1 and j > 0 and j < koot[1] - 1:
                    kartta[i][j] = 3

    f_paikka = [7, 7]
    for i in range((koot[0] // 6 - 2) * 6):
        f_paikka[0] += 1
        kartta[f_paikka[0]][f_paikka[1]] = 3
    kartta[f_paikka[0] + 1][f_paikka[1]] = 3
    kartta[f_paikka[0]][f_paikka[1] - 1] = 1
    for i in range((koot[1] // 6 - 2) * 6):
        f_paikka[1] += 1
        kartta[f_paikka[0]][f_paikka[1]] = 3
    kartta[f_paikka[0]][f_paikka[1] + 1] = 3
    kartta[f_paikka[0] + 1][f_paikka[1]] = 1
    for i in range((koot[0] // 6 - 2) * 6):
        f_paikka[0] -= 1
        kartta[f_paikka[0]][f_paikka[1]] = 3
    kartta[f_paikka[0] - 1][f_paikka[1]] = 3
    kartta[f_paikka[0]][f_paikka[1] + 1] = 1
    for i in range((koot[1] // 6 - 2) * 6):
        f_paikka[1] -= 1
        kartta[f_paikka[0]][f_paikka[1]] = 3
    kartta[f_paikka[0]][f_paikka[1] - 1] = 3
    kartta[f_paikka[0] - 1][f_paikka[1]] = 1

    palikat = [[1, 1, 3, 3, 3]] * 6 + [[1, 3, 1, 3, 3]] * 8 + [[1, 3, 3, 3, 3]] * 3
    if koot == (15, 15):  # 2*2 mapin korjaus
        palikat = [[1, 1, 3, 3, 3]] * 2 + [[1, 3, 1, 3, 3]] * 7 + [[1, 3, 3, 3, 3]] * 7
    palikat2 = palikat.copy()
    palikat2 += [[3, 3, 3, 3, 3]] * tyhjien_määrä
    palikat2 += [[1, 1, 1, 1, 1]] * täysien_määrä
    for x in range(1, koot[0], 3):
        for y in range(1, koot[1], 3):
            if not (x % 6 == 1 and y % 6 == 1):
                if len(palikat2) == 0:
                    palikat2 = palikat.copy()
                a = random.choice(palikat2)

                palikat2.remove(a)
                if random.random() < 0.5:
                    a = a[3::-1] + [a[4]]
                if random.random() < 0.5:
                    a = käännä(random.randint(0, 1), a)
                Z = ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), (x, y))
                for i in range(len(Z)):
                    kartta[Z[i][0]][Z[i][1]] = a[i]

    if koot == (15, 15):  # 2*2 mapin korjaus
        kartta[7][8] = 3
    if koot == (9, 9):
        kartta[6][7] = 3

    return kartta


def reset():
    global paikat, nopeus, maze, koko, koko2, zoom, kädessä, pelaaja, window, font, esineet, personal_esineet, näytä_objektiivi
    global pelaaja_pisteet, salaiset_numerot, sekotus, alotus_aika, printattava, jumissa, seinät, pelaajamäärä, kierros_numero, aarteiden_määrä

    maze = tee_kartta([koko2[0], koko2[1]])
    koko = koko2.copy()
    koko[0] = (koko2[0] * 2 + 1) * 3
    koko[1] = (koko2[1] * 2 + 1) * 3

    font = pygame.font.Font(None, int(zoom * 1.5))
    printattava = "Tervetulo seikkailemaan"
    window = pygame.display.set_mode(
        (int(koko[0] * zoom + math.sqrt(koko[0] * koko[1]) * zoom), int(koko[1] * zoom * 1.2)), pygame.RESIZABLE)
    alotus_aika = time.time()
    jumissa = 0
    kierros_numero = 0

    pelaaja = 0
    paikat = [[1, 1], [1, koko[1] - 2], [koko[0] - 2, koko[1] - 2], [koko[0] - 2, 1], [7, 7], [7, koko[1] - 8],
              [koko[0] - 8, koko[1] - 8], [koko[0] - 8, 7]]
    if pelaajamäärä == 2:
        paikat = [paikat[0]] + [paikat[2]]
    elif pelaajamäärä == 4:
        paikat = [paikat[0]] + [paikat[1]] + [paikat[2]] + [paikat[3]]
    elif pelaajamäärä == 6:
        paikat = [paikat[0]] + [paikat[1]] + [paikat[2]] + [paikat[3]] + [paikat[4]] + [paikat[6]]
    else:
        paikat = paikat[:pelaajamäärä]

    for i in range(len(paikat)):  # mazen kotipesien laitto
        a = paikat[i]
        maze[a[0]][a[1]] = esine(pelaajan_väri_str(i) + " Koti", pelaajan_väri(i))
        print(pelaajan_väri_str(i) + " Koti", pelaajan_väri(i))

    if salaus:
        salaiset_numerot = [random.randint(5, 20) for i in range(len(paikat))]
    else:
        salaiset_numerot = [0 for i in range(len(paikat))]
    sekotus = 1000 + random.randint(0, len(paikat) + 1)
    # paikat += [paikat[0]]
    """
    with open("maze aito.dump", "rb") as f:
      maze = pickle.load(f)
    """

    esineet = [esine("Rubiini", (240, 0, 0), "ruby_1", 1), esine("Rautamiekka", (0, 0, 0), "sword_iron", 1),
               esine("Avain", (0, 0, 0), "key", 1),
               esine("Leipä", (0, 0, 0), "bread", 1), esine("Aarrearkku", (0, 0, 0), "chest", 1),
               esine("Omena", (0, 0, 0), "apple_green", 1),
               esine("Kirja", (0, 0, 0), "book", 1), esine("Kanankoipi", (0, 0, 0), "chicken", 1),
               esine("Moukari", (0, 0, 0), "warhammer_iron", 1),
               esine("Ruoska", (0, 0, 0), "whip", 1), esine("Porkkana", (0, 0, 0), "carrot", 1),
               esine("Banaani", (0, 0, 0), "banana", 1),
               esine("Luut", (0, 0, 0), "bones", 1), esine("Aarrepussi", (0, 0, 0), "bag", 1),
               esine("Pihvi", (0, 0, 0), "beef", 1),
               esine("Kruunu", (0, 0, 0), "crown", 1), esine("Sieni", (0, 0, 0), "mushroom", 1),
               esine("Marjat", (0, 0, 0), "berries", 1),
               esine("Kengkä", (0, 0, 0), "boot", 1), esine("Kypärä", (0, 0, 0), "helmet_royal_iron", 1),
               esine("Sormus", (0, 0, 0), "ring_ruby", 1), esine("Sarvi", (0, 0, 0), "horn", 1),
               esine("Muna", (0, 0, 0), "egg", 1), esine("Amuletti", (0, 0, 0), "amulet_sapphire", 1)]

    esineet += [esine("Juusto", (255, 255, 0)), esine("Oltermanni", (200, 200, 20)),
                esine("Meetvursti", (255, 100, 100)), esine("Nakki", (180, 30, 80)),
                esine("Gouda", (100, 100, 0)), esine("Kala", (2, 2, 200)), esine("Kurkku", (0, 200, 50)),
                esine("Tomaatti", (200, 2, 20)),
                esine("Muna", (100, 100, 100)), esine("Lehtikaali", (0, 250, 20)),
                esine("Riisi", (240, 180, 160)), esine("Mursu", (50, 50, 50)), esine("Marsu", (100, 100, 100))]

    esineet = esineet[0:aarteiden_määrä]

    for o in range(aarteiden_määrä - len(esineet)):
        esineet += [esine("öö" + str(o), random_color())]

    esineiden_numerot = list(range(1, len(esineet) + 10))
    random.shuffle(esineiden_numerot)
    for i in range(len(esineet)):
        esineet[i].numero = esineiden_numerot[i]

    random.shuffle(esineet)
    esineet2 = esineet.copy()

    pelaaja_pisteet = [0 for i in range(len(paikat))]

    a1 = list(range(1, (koko[0]), 6))
    b1 = list(range(1, koko[1], 6))
    c1 = []
    for x in a1:
        for y in b1:
            c1 += [[x, y]]

    a2 = list(range(1, koko[0], 3))
    b2 = list(range(1, koko[1], 3))
    c2 = []
    for x in a2:
        for y in b2:
            c2 += [[x, y]]
    random.shuffle(c1)
    random.shuffle(c2)
    for x, y in c1:
        if maze[x][y] == 3:
            if len(esineet2) > 0:
                maze[x][y] = esineet2.pop(0)
    for x, y in c2:
        if mikä_pala(x, y) == "risteys":
            if len(esineet2) > 0 and type(maze[x][y]) == int:
                maze[x][y] = esineet2.pop(0)
    for x in a2:
        for y in b2:
            if mikä_pala(x, y) != "suora":
                if len(esineet2) > 0 and type(maze[x][y]) == int and koko[0] != 15 and koko[1] != 15:
                    maze[x][y] = esineet2.pop(0)
    for i in esineet2:
        esineet.remove(i)

    personal_esineet = []
    for i in range(len(paikat)):
        personal_esineet += [esineet.pop()]
    kädessä = [1, 1, 3, 3, 3]

    näytä_objektiivi = 0

    nopeus = [0, 0]
    seinä1 = esine("Seinä1", (0, 0, 0), "Seinä1", 1, zoom)
    seinä2 = esine("Seinä2", (0, 0, 0), "Seinä2", 1, zoom)
    lattia = esine("Lattia", (0, 0, 0), "Lattia", 1, zoom)
    seinät = [seinä1, seinä2, lattia]


def mikä_pala(x, y):
    Z = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    A = [0, 0, 0, 0]
    summa = 0
    for i in range(len(Z)):
        if maze[Z[i][0]][Z[i][1]] == 3:
            summa += 1
        A[i] = maze[Z[i][0]][Z[i][1]]
    if (A[0] == 3 and A[1] == 3 and A[2] != 3 and A[3] != 3) or (A[2] == 3 and A[3] == 3 and A[0] != 3 and A[1] != 3):
        return "suora"
    elif summa == 2:
        return "kulma"
    elif summa == 3:
        return "risteys"

    return "x"


def random_color():
    levels = range(32, 256, 32)
    return tuple(random.choice(levels) for _ in range(3))


def pelaajan_väri(i):
    if i < 0:
        i = len(paikat) - 1
    if i >= len(paikat):
        i = 0

    if i == 0:
        väri = (255, 0, 0)  # p
    elif i == 1:
        väri = (0, 255, 0)  # v
    elif i == 2:
        väri = (0, 0, 255)  # s
    elif i == 3:
        väri = (255, 255, 0)  # k
    elif i == 4:
        väri = (100, 0, 100)  # liila
    elif i == 5:
        väri = (102, 51, 0)  # ruskea
    elif i == 6:
        väri = (255, 102, 0)  # oranssi
    elif i == 7:
        väri = (255, 102, 179)  # vaalean punainen
    elif i == 8:
        väri = (240, 248, 255)  # lime
    elif i == 9:
        väri = (0, 255, 255)  # cyan
    else:
        väri = (100, 100, 100)
    return väri


def pelaajan_väri_str(i):
    if i < 0:
        i = len(paikat) - 1
    if i >= len(paikat):
        i = 0

    if i == 0:
        väri = "Punainen"
    elif i == 1:
        väri = "Vihreä"
    elif i == 2:
        väri = "Sininen"
    elif i == 3:
        väri = "Keltainen"
    elif i == 4:
        väri = "Liila"
    elif i == 5:
        väri = "Ruskea"
    elif i == 6:
        väri = "Oranssi"
    elif i == 7:
        väri = "Vaaleanpunainen"
    elif i == 8:
        väri = "Lime"
    elif i == 9:
        väri = "Cyan"
    else:
        väri = "ylimääräinen harmaa"
    return väri


def piirrä():
    global kädessä
    window.fill((255, 255, 255))
    for x in range(koko[0]):
        for y in range(koko[1]):
            a = maze[x][y]
            if a == 1:
                if not (x // 3 % 4 == 1 and y // 3 % 4 == 1) and (x // 3 % 2 == 0 and y // 3 % 2 == 0):
                    pygame.draw.rect(window, (0, 0, 0), pygame.Rect(x * zoom, y * zoom, zoom, zoom))
                    window.blit(seinät[1].kuva, (x * zoom, y * zoom))
                else:
                    pygame.draw.rect(window, (40, 40, 40), pygame.Rect(x * zoom, y * zoom, zoom, zoom))
                    window.blit(seinät[0].kuva, (x * zoom, y * zoom))
            elif a == 2:
                pygame.draw.rect(window, (0, 255, 0), pygame.Rect(x * zoom, y * zoom, zoom, zoom), 3)
            elif a == 0:
                pygame.draw.rect(window, (0, 0, 0), pygame.Rect(x * zoom, y * zoom, zoom, zoom), 3)
            elif a == 3:
                pygame.draw.rect(window, (200, 200, 200), pygame.Rect(x * zoom, y * zoom, zoom, zoom))
                window.blit(seinät[2].kuva, (x * zoom, y * zoom))
            else:
                if type(a) == int:
                    pygame.draw.rect(window, (a * 1.1 % 100, a * 1.2 % 100 + 100, a * 1.3 % 55 + 200),
                                     pygame.Rect(x * zoom, y * zoom, zoom, zoom))
                else:
                    pygame.draw.rect(window, (200, 200, 200), pygame.Rect(x * zoom, y * zoom, zoom, zoom))
                    window.blit(seinät[2].kuva, (x * zoom, y * zoom))
                    if not a.kuvan_käyttö:
                        k = 0.6  # koko ÄLÄ MUUTA TOIMII VAIN K = 0
                        pygame.draw.rect(window, a.väri,
                                         pygame.Rect(x * zoom + zoom * k / 3, y * zoom + zoom * k / 3, zoom * k,
                                                     zoom * k))

    e = 0  # etäisyys
    väri = pelaajan_väri(pelaaja + 1)
    for x in range(koko[0]):
        for y in range(koko[1]):
            a = maze[x][y]
            if type(a) != int:
                if a.kuvan_käyttö:
                    window.blit(a.kuva, (x * zoom - zoom, y * zoom - zoom))
                else:
                    pygame.draw.rect(window, a.väri,
                                     pygame.Rect(x * zoom + zoom * k / 3, y * zoom + zoom * k / 3, zoom * k, zoom * k))

            if (x % 3 == 0 and y % 3 == 0):
                pygame.draw.rect(window, väri,
                                 pygame.Rect(x * zoom + zoom * e, y * zoom + zoom * e, zoom * 3 - zoom * e * 2,
                                             zoom * 3 - zoom * e * 2), 5)

    # pelaajan piirto
    for i in range(len(paikat)):
        a = [paikat[i][0], paikat[i][1]]
        väri = pelaajan_väri(i)
        pygame.draw.circle(window, väri, (int(a[0] * zoom + zoom / 2.1), int(a[1] * zoom + zoom / 2.1)), zoom // 2)
        # pygame.draw.rect(window ,väri,pygame.Rect(a[0]*zoom,a[1]*zoom, zoom,zoom))

    # kädessä piirtö iso neliö
    x, y = pygame.mouse.get_pos()
    px = x - x % (zoom * 3)
    py = y - y % (zoom * 3)
    if (((x < zoom * 3 or x > zoom * 3 * 6) and y // (zoom * 3) % 2 == 1) or (
            (y < zoom * 3 or y > zoom * 3 * 6) and x // (zoom * 3) % 2 == 1)) and y < koko[1] * zoom and x < koko[
        0] * zoom:  # valitsemen väri ehto
        pygame.draw.rect(window, (100, 100, 255), pygame.Rect(px, py, zoom * 3, zoom * 3), 5)
    else:
        pygame.draw.rect(window, (255, 100, 100), pygame.Rect(px, py, zoom * 3, zoom * 3), 5)

    for i in range(3):
        for j in range(3):
            window.blit(seinät[0].kuva, ((px + i * zoom), (py + j * zoom)))

    x = int((px + zoom) / zoom)
    y = int((py + zoom) / zoom)

    Z = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), (x, y)]  # kädessä piirto pienet neliöt
    for i in range(5):
        x = Z[i][0]
        y = Z[i][1]
        if kädessä[i] == 3:
            pygame.draw.rect(window, (200, 200, 200), pygame.Rect(x * zoom, y * zoom, zoom, zoom))
            window.blit(seinät[2].kuva, (x * zoom, y * zoom))
        elif kädessä[i] == 1:
            pygame.draw.rect(window, (50, 50, 50), pygame.Rect(x * zoom, y * zoom, zoom, zoom))
            window.blit(seinät[0].kuva, (x * zoom, y * zoom))
        else:
            if kädessä[i].kuvan_käyttö:
                # pygame.draw.rect(window ,(200,200,200),pygame.Rect(x*zoom,y*zoom, zoom,zoom))
                window.blit(seinät[2].kuva, (x * zoom, y * zoom))
                window.blit(kädessä[i].kuva, (x * zoom - zoom, y * zoom - zoom))
            else:
                pygame.draw.rect(window, kädessä[i].väri, pygame.Rect(x * zoom, y * zoom, zoom, zoom))

    # hiiri objektiivin näyttö
    x, y = pygame.mouse.get_pos()
    x //= zoom
    y //= zoom
    try:
        a = maze[x][y]
    except:
        a = 0

    if type(a) != int:
        text = font.render(a.nimi, 1, a.väri)
        textpos = text.get_rect()
        textpos.x = 0
        textpos.centery = zoom * koko[1] * 1.2 - zoom * 3.5
        window.blit(text, textpos)

    # oman salasen numeron näyttö
    if näytä_objektiivi:
        b = pelaaja + 1
        if b >= len(paikat):
            b = 0
        a = personal_esineet[b]  # näyttää objektiivin
        text = font.render("Salainen Numerosi on " + str(salaiset_numerot[b]), 1, (255, 50, 50))
        textpos = text.get_rect()
        textpos.x = 0
        textpos.centery = zoom * koko[1] * 1.2 - zoom * 2.5
        window.blit(text, textpos)

    # objektiivien näyttö pelin sivussa
    a = personal_esineet + esineet[:30]
    a.sort(key=lambda x: x.nimi)
    for i in range(len(a)):
        text = font.render(a[i].nimi + " " + str(a[i].numero), 1, a[i].väri)
        textpos = text.get_rect()
        textpos.centerx = koko[0] * zoom + math.sqrt(koko[0] * koko[1]) * zoom * 0.25
        textpos.centery = zoom * i + zoom
        window.blit(text, textpos)
    # targetin näytöö
    a = personal_esineet
    for j in range(len(a)):
        text = font.render(pelaajan_väri_str(j) + " " + str(a[j].numero + salaiset_numerot[j]), 1, pelaajan_väri(j))
        textpos = text.get_rect()
        textpos.centerx = koko[0] * zoom + math.sqrt(koko[0] * koko[1]) * zoom * 0.75
        textpos.centery = zoom * j + zoom
        window.blit(text, textpos)

    for k in range(len(paikat)):
        text = font.render(str(pelaajan_väri_str(k)) + ":" + str(pelaaja_pisteet[k]), 1, pelaajan_väri(k))
        textpos = text.get_rect()
        textpos.centerx = koko[0] * zoom + math.sqrt(koko[0] * koko[1]) * zoom * 0.75
        textpos.centery = zoom * j + zoom + zoom * k + zoom + zoom * 2
        window.blit(text, textpos)

    aika = (time.time() - alotus_aika)

    sekuntti = int(aika % 60)
    minuutti = int((aika / 60) % 60)
    tunti = int(aika / 60 ** 2)

    text = font.render(
        "Tunti: " + str(tunti) + " Minuutti: " + str(minuutti) + " Sekuntti: " + str(sekuntti) + " Kierros: " + str(
            round(kierros_numero / len(paikat), 2)), 1, (0, 0, 0))
    textpos = text.get_rect()
    textpos.x = 0
    textpos.centery = zoom * koko[1] * 1.2 - zoom / 2
    window.blit(text, textpos)

    text = font.render(printattava, 1, (0, 0, 0))
    textpos = text.get_rect()
    textpos.x = 0
    textpos.centery = zoom * koko[1] * 1.2 - zoom * 1.5
    window.blit(text, textpos)

    pygame.display.flip()


def vaihda(x, y):
    if x < koko[0] * zoom:
        x = x - x % (zoom * 3)
        y = y - y % (zoom * 3)
        x = int((x + zoom) / zoom)
        y = int((y + zoom) / zoom)
        Z = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        a = kädessä[4]
        kädessä[4] = maze[x][y]
        maze[x][y] = a
        A = [0, 0, 0, 0]
        for i in range(4):
            x = Z[i][0]
            y = Z[i][1]
            A[i] = maze[x][y]
            maze[x][y] = kädessä[i]
            kädessä[i] = A[i]


def käännä(vasen=1, a=0):
    global kädessä
    if a == 0:
        a = kädessä

    if vasen:
        a = [a[2]] + [a[3]] + [a[1]] + [a[0]] + [a[4]]
    else:
        a = [a[2]] + [a[3]] + [a[1]] + [a[0]] + [a[4]]
        a = [a[2]] + [a[3]] + [a[1]] + [a[0]] + [a[4]]
        a = [a[2]] + [a[3]] + [a[1]] + [a[0]] + [a[4]]

    kädessä = a
    return a


def pisteen_saaminen():
    global printattava
    for p in range(len(paikat)):  # pisteen saaminen
        a = paikat[p]
        if type(maze[a[0]][a[1]]) != int:
            if personal_esineet[p].nimi == maze[a[0]][a[1]].nimi:
                if len(esineet) > 0:
                    printattava = (pelaajan_väri_str(p) + " On Saanut: " + personal_esineet[p].nimi)
                    personal_esineet[p] = esineet.pop(0)
                else:
                    personal_esineet[p] = esine("Ei enään esineitä", (0, 0, 0))
                pelaaja_pisteet[p] += 1
                return True
    return False


koko2 = [3, 3]  # leveys ,korkeus
tyhjien_määrä = 2
täysien_määrä = 2
aarteiden_määrä = 24
pelaajamäärä = 2
zoom = 30
GOD = False
vapaus = 1
salaus = 1  # käytetäänkö salausta vai ei
pygame.init()
clock = pygame.time.Clock()
Hiiri = [0, 0, 0]
reset()
piirrä()
päällä = True
sekotus = 0
while päällä:

    # Näppäimet
    for event in pygame.event.get():
        if event.type == pygame.VIDEORESIZE:
            old_surface_saved = window
            surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            # On the next line, if only part of the window
            # needs to be copied, there's some other options.
            surface.blit(old_surface_saved, (0, 0))
            del old_surface_saved
        if event.type == pygame.QUIT:
            päällä = False
            pygame.display.quit()
            pygame.quit()
            break

        if event.type == pygame.KEYDOWN:
            try:
                if (event.key == pygame.K_s or event.key == pygame.K_DOWN) and maze[paikat[pelaaja][0]][
                    paikat[pelaaja][1] + 1] != 1:
                    nopeus = [0, 1]
                if (event.key == pygame.K_w or event.key == pygame.K_UP) and maze[paikat[pelaaja][0]][
                    paikat[pelaaja][1] - 1] != 1:
                    nopeus = [0, -1]
                if (event.key == pygame.K_d or event.key == pygame.K_RIGHT) and maze[paikat[pelaaja][0] + 1][
                    paikat[pelaaja][1]] != 1:
                    nopeus = [1, 0]
                if (event.key == pygame.K_a or event.key == pygame.K_LEFT) and maze[paikat[pelaaja][0] - 1][
                    paikat[pelaaja][1]] != 1:
                    nopeus = [-1, 0]
            except:
                pass
            if event.key == pygame.K_p:
                reset()
            if event.key == pygame.K_o:
                sekotus = random.randint(1000, 1300)
            if event.key == pygame.K_x and GOD:  # kentän muokkaus
                x, y = pygame.mouse.get_pos()
                if maze[x // zoom][y // zoom] == 3:
                    maze[x // zoom][y // zoom] = 1
                else:
                    maze[x // zoom][y // zoom] = 3
            if event.key == pygame.K_SPACE:
                näytä_objektiivi = 1

            for i in range(len(paikat[pelaaja])):  # rajotus
                if paikat[pelaaja][i] >= koko[i]:
                    paikat[pelaaja][i] = koko[i] - 1
                if paikat[pelaaja][i] < 0:
                    paikat[pelaaja][i] = 0
        if event.type == pygame.KEYUP:
            nopeus = [0, 0]
            näytä_objektiivi = 0

    if not päällä:
        break

    # hiiri
    if sekotus > 0:
        x, y = random.randint(0, koko[0] * zoom - 1), random.randint(0, koko[0] * zoom - 1)
        käännä()
        sekotus -= 1
    else:
        x, y = pygame.mouse.get_pos()

    if pygame.mouse.get_pressed()[0] or sekotus > 0:
        if (Hiiri[0] or sekotus > 0) and y < koko[1] * zoom and x < koko[0] * zoom:
            Hiiri[0] = 0
            Pelaajan_vaihto = 0
            if x < zoom * 3 and y // (zoom * 3) % 2 == 1:
                for i in range(len(paikat)):
                    if y // (zoom * 3) == paikat[i][1] // 3:
                        paikat[i][0] += 3
                for i in range(koko[0] // 3):
                    vaihda(x, y)
                    x += zoom * 3
                Pelaajan_vaihto = 1


            elif x > zoom * 3 * (koko[0] // 3 - 1) and y // (zoom * 3) % 2 == 1:
                for i in range(len(paikat)):
                    if y // (zoom * 3) == paikat[i][1] // 3:
                        paikat[i][0] -= 3
                for i in range(koko[0] // 3):
                    vaihda(x, y)
                    x -= zoom * 3
                Pelaajan_vaihto = 1


            elif y < zoom * 3 and x // (zoom * 3) % 2 == 1:
                for i in range(len(paikat)):
                    if x // (zoom * 3) == paikat[i][0] // 3:
                        paikat[i][1] += 3
                for i in range(koko[1] // 3):
                    vaihda(x, y)
                    y += zoom * 3
                Pelaajan_vaihto = 1

            elif y > zoom * 3 * (koko[1] // 3 - 1) and x // (zoom * 3) % 2 == 1:
                for i in range(len(paikat)):
                    if x // (zoom * 3) == paikat[i][0] // 3:
                        paikat[i][1] -= 3
                for i in range(koko[1] // 3):
                    vaihda(x, y)
                    y -= zoom * 3
                Pelaajan_vaihto = 1

            for i in range(len(paikat)):
                paikat[i][0] = paikat[i][0] % (koko[0])
                paikat[i][1] = paikat[i][1] % (koko[1])
                if maze[paikat[i][0]][paikat[i][1]] == 1:
                    paikat[i][1] = paikat[i][1] // 3 * 3 + 1
                    paikat[i][0] = paikat[i][0] // 3 * 3 + 1
            # pelaajan vaihto
            if Pelaajan_vaihto:
                kierros_numero += 1
                pelaaja += 1
                jumissa = 0
                if pelaaja >= len(paikat):
                    pelaaja = 0
                Pelaajan_vaihto = 0

    else:
        Hiiri[0] = 1

    if pygame.mouse.get_pressed()[2]:
        if Hiiri[2]:
            Hiiri[2] = 0
            käännä(0)

    else:
        Hiiri[2] = 1
    try:
        a: List[int] = list(map(sum, list(zip(paikat[pelaaja], nopeus))))  # nopeuden lisääminen
        if (maze[a[0]][a[1]] != 1 and not jumissa) or GOD:
            paikat[pelaaja] = list(map(sum, list(zip(paikat[pelaaja], nopeus))))
    except:
        pass
    # piirtäminen

    if pisteen_saaminen():
        jumissa = 1

    if sekotus <= 0:

        piirrä()
        clock.tick(10)
    else:
        kierros_numero = 0
