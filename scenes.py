"""One function per drawing. Each gets a Paint canvas seeded from its name."""

import math

from paint import *

SCENES = {}


def scene(fn):
    SCENES[fn.__name__] = fn
    return fn


# ---- reusable props ---------------------------------------------------------

def toilet(p, x, y, s=1.0):
    """Paint-shape toilet: tank rectangle, perfect-ellipse rim, chord bowl, box base. (x, y) = floor centre."""
    d = ImageDraw.Draw(p.img)
    tw, th = 60 * s, 90 * s
    p.rect((int(x + 40 * s), int(y - 230 * s), int(x + 40 * s + tw), int(y - 230 * s + th)), width=3, fill=WHITE)
    p.rect((int(x - 20 * s), int(y - 60 * s), int(x + 50 * s), int(y)), width=3, fill=WHITE)
    d.chord((int(x - 90 * s), int(y - 190 * s), int(x + 70 * s), int(y - 40 * s)), 0, 180, outline=BLACK, width=3, fill=WHITE)
    p.ellipse((int(x - 90 * s), int(y - 135 * s), int(x + 70 * s), int(y - 95 * s)), width=3, fill=WHITE)
    p.ellipse((int(x - 75 * s), int(y - 128 * s), int(x + 55 * s), int(y - 102 * s)), width=3, fill=YELLOW)


def beer(p, x, y, s=1.0):
    """A pint drawn with the rectangle tool, freehand handle and foam."""
    w, h = int(34 * s), int(60 * s)
    p.rect((x, y, x + w, y + h), width=3, fill=YELLOW)
    p.brush([(x + w, y + 12 * s), (x + w + 16 * s, y + 18 * s), (x + w + 15 * s, y + 42 * s), (x + w, y + 46 * s)], 4)
    p.brush([(x - 3, y), (x + 5, y - 10 * s), (x + 14 * s, y - 6 * s), (x + 22 * s, y - 12 * s), (x + w + 2, y - 2)], 4)


def drop(p, x, y, s=1.0, face="smile", arms=None):
    """The agüita: a freehand yellow drop with a face. (x, y) = belly centre."""
    r = 55 * s
    pts = [(x + p.rng.uniform(-3, 3), y - r * 2.1)]
    for i in range(11):
        a = -0.35 * math.pi + (1.7 * math.pi) * i / 10
        pts.append((x + r * math.cos(a), y + r * math.sin(a)))
    pts.append((pts[0][0] + 2, pts[0][1] + 3))
    pts.append((pts[1][0] - 3, pts[1][1] - 2))
    p.brush(pts, 6, shake=0.7)
    p.fill(x, y + 10 * s, YELLOW)
    for ex in (-18, 14):
        p.brush([(x + ex * s, y - 12 * s)], 8, BLACK, 0.2)
    if face == "smile":
        p.brush([(x - 22 * s, y + 12 * s), (x, y + 26 * s), (x + 22 * s, y + 10 * s)], 5, BLACK, 0.6)
    elif face == "sing":
        p.loop(x, y + 20 * s, 12 * s, 14 * s, 5)
    elif face == "hot":
        p.brush([(x - 20 * s, y + 20 * s), (x - 8 * s, y + 14 * s), (x + 4 * s, y + 22 * s), (x + 18 * s, y + 14 * s)], 5)
        p.brush([(x - 34 * s, y - 30 * s), (x - 38 * s, y - 12 * s)], 4, DBLUE)
    elif face == "sleep":
        for ex in (-18, 14):
            p.brush([(x + ex * s - 8, y - 12 * s), (x + ex * s + 8, y - 12 * s)], 5, YELLOW)
            p.brush([(x + ex * s - 9, y - 13 * s), (x + ex * s + 9, y - 10 * s)], 4)
        p.brush([(x - 10 * s, y + 18 * s), (x + 10 * s, y + 18 * s)], 4)
    if arms == "wave":
        p.brush([(x - r, y), (x - r - 40 * s, y - 20 * s)], 5)
        p.brush([(x + r, y), (x + r + 30 * s, y - 50 * s), (x + r + 50 * s, y - 70 * s)], 5)
    elif arms == "up":
        p.brush([(x - r, y), (x - r - 30 * s, y - 60 * s)], 5)
        p.brush([(x + r, y), (x + r + 30 * s, y - 60 * s)], 5)
    elif arms == "dance":
        p.brush([(x - r, y + 5), (x - r - 45 * s, y - 10 * s), (x - r - 60 * s, y - 45 * s)], 5)
        p.brush([(x + r, y + 5), (x + r + 40 * s, y + 30 * s)], 5)
    if arms:
        p.brush([(x - 20 * s, y + r - 4), (x - 30 * s, y + r + 35 * s), (x - 45 * s, y + r + 38 * s)], 5)
        p.brush([(x + 20 * s, y + r - 4), (x + 28 * s, y + r + 35 * s), (x + 45 * s, y + r + 36 * s)], 5)


def water_band(p, y0, y1, color=TURQ, shake=1.0):
    pts0 = [(-10, y0), (240, y0 + p.rng.uniform(-15, 15)), (480, y0 + p.rng.uniform(-15, 15)), (720, y0 + p.rng.uniform(-15, 15)), (970, y0)]
    p.brush(pts0, 6, shake=shake)
    p.fill(480, (y0 + y1) // 2 + 10, color)


def pee_speckles(p, x, y, n=3, spread=120):
    for i in range(n):
        p.spray(x + p.rng.uniform(-spread, spread), y + p.rng.uniform(-spread / 3, spread / 3), 30, YELLOW, 260, wander=6)


def cow(p, x, y, s=1.0, drink=False):
    p.loop(x, y, 60 * s, 34 * s, 6)
    hx, hy = (x - 78 * s, y + 20 * s) if drink else (x - 75 * s, y - 25 * s)
    p.loop(hx, hy, 22 * s, 17 * s, 6, n=10)
    p.brush([(hx - 12 * s, hy - 14 * s), (hx - 20 * s, hy - 32 * s)], 5)
    p.brush([(hx + 10 * s, hy - 14 * s), (hx + 18 * s, hy - 32 * s)], 5)
    p.brush([(hx - 8 * s, hy - 3 * s)], 6, BLACK, 0.2)
    for lx in (-40, -20, 20, 40):
        p.brush([(x + lx * s, y + 30 * s), (x + lx * s + p.rng.uniform(-4, 4), y + 75 * s)], 6)
    p.brush([(x + 58 * s, y - 5 * s), (x + 85 * s, y - 25 * s), (x + 80 * s, y + 5 * s)], 5)
    p.brush([(x - 20 * s, y - 10 * s), (x - 5 * s, y - 15 * s), (x - 10 * s, y + 5 * s)], 14)
    p.brush([(x + 25 * s, y + 5 * s), (x + 35 * s, y - 5 * s)], 16)
    p.ellipse((int(x + 5 * s), int(y + 25 * s), int(x + 25 * s), int(y + 42 * s)), width=2, fill=PINK)


def house(p, x, y, w, h, label=None, typed=False, fill=None):
    p.block_arrow(x, y, w, h, fill=fill)
    if label:
        if typed:
            p.typed(label, int(x + w * 0.24), int(y + h * 0.5), 22)
        else:
            p.hand_lines(label, x + w * 0.28, y + h * 0.5, 26)


def building(p, x0, x1, top, bottom=540, fill=LGRAY, windows=6):
    p.rect((x0, top, x1, bottom), width=3, fill=fill)
    for i in range(windows):
        wx = int(p.rng.uniform(x0 + 8, x1 - 30))
        wy = int(p.rng.uniform(top + 10, bottom - 40))
        ww, wh = int(p.rng.choice([14, 18, 26, 40])), int(p.rng.choice([10, 18, 26]))
        p.rect((wx, wy, min(wx + ww, x1 - 6), wy + wh), width=3, fill=WHITE)


def city(p, top=260):
    xs = [0, 110, 230, 350, 470, 590, 720, 840, 960]
    for a, b in zip(xs, xs[1:]):
        building(p, a + p.rng.randint(0, 15), b - p.rng.randint(5, 20), top + p.rng.randint(-60, 80))


def cloud(p, x, y, w=260, dark=False, pee=True):
    col = GRAY if dark else WHITE
    for i in range(7):
        p.spray(x + p.rng.uniform(-w / 2, w / 2), y + p.rng.uniform(-25, 25), 55, col, 1800)
    if pee:
        pee_speckles(p, x, y, 2, w / 3)


def rain(p, x0, x1, y0, y1, n=40, color=YELLOW):
    for i in range(n):
        x = p.rng.uniform(x0, x1)
        y = p.rng.uniform(y0, y1)
        p.brush([(x, y), (x - 6, y + 24)], 4, color, shake=0.3)


def sky(p):
    p.fill(5, 5, TURQ)


def bar(p, words, face="smile"):
    # counter and bottles behind the bartender
    p.rect((0, 360, 960, 400), width=3, fill=BROWN)
    p.rect((0, 400, 960, 540), width=3, fill=BROWN)
    p.brush([(0, 150), (960, 150)], 5)
    for bx in (560, 610, 660, 760, 820):
        p.rect((bx, 90, bx + 26, 150), width=3, fill=p.rng.choice([GREEN, DRED, BROWN]))
        p.rect((bx + 8, 70, bx + 18, 90), width=3)
    # narrator at the counter, bartender behind it
    p.stick(260, 470, 0.9, arms="out", face=face)
    p.stick(700, 440, 0.8, arms="down", face="flat")
    p.typed("BAR", 850, 20, 34)
    p.hand("EL CAMARERO", 610, 180, 24)
    p.bubble(300, 90, (275, 200), words, 28)


# ---- the bar ----------------------------------------------------------------

@scene
def bar_please(p):
    bar(p, ["POR FAVOR,", "¿ME DAS UNA", "CERVEZA?"])


@scene
def bar_dame(p):
    bar(p, ["DAME UNA", "CERVEZA!!"], face="flat")
    beer(p, 560, 300)


@scene
def title(p):
    p.hand("MI AGÜITA", 120, 120, 90, width=9)
    p.hand("AMARILLA", 180, 250, 90, width=9, color=YELLOW)
    p.typed("Los Toreros Muertos", 560, 430, 30)
    p.typed("(hecho en paint)", 600, 470, 18)
    drop(p, 110, 420, 0.6)


@scene
def beers40(p):
    p.stick(150, 480, 0.9, face="smile", arms="out", beer=True)
    for i in range(40):
        col, row = i % 10, i // 10
        bx = 320 + col * 56 + p.rng.randint(-14, 14) + row * 9
        by = 230 + row * 58 + p.rng.randint(-12, 12)
        beer(p, bx, by, p.rng.uniform(0.45, 0.62))
    p.hand("40 CERVEZAS", 360, 70, 50, width=5)
    p.arrow(520, 140, 560, 230)
    p.hand("HOY", 800, 150, 34)


@scene
def expel(p):
    hy = p.stick(420, 500, 1.2, arms="down", face="o")
    # a huge belly, the forty beers
    p.loop(420, 330, 85, 75, 6, closed=True)
    p.fill(370, 360, YELLOW)
    p.hand("40", 385, 310, 40)
    p.bubble(700, 120, (470, 150), ["TENGO QUE", "EXPULSARLAS"], 28)
    p.hand("¡¡!!", 180, 150, 60)


@scene
def stairs(p):
    for i in range(6):
        p.rect((120 + i * 90, 420 - i * 60, 960, 480 - i * 60), width=3, fill=LGRAY)
    p.rect((0, 480, 960, 540), width=3, fill=BROWN)
    p.typed("BAR", 40, 490, 26)
    p.rect((690, 40, 820, 100), width=3, fill=WHITE)
    p.typed("WC  ->", 715, 55, 26)
    p.stick(420, 240, 0.7, arms="up", face="smile")
    p.hand("ARRIBA", 80, 100, 44)
    p.arrow(200, 170, 340, 190, bend=-0.2)


@scene
def pee(p):
    p.stick(330, 470, 1.1, arms="pee", face="smile")
    toilet(p, 620, 470, 1.1)
    p.brush([(345, 275), (400, 240), (470, 250), (560, 330)], 5, YELLOW)
    p.rect((0, 470, 960, 540), width=3, fill=WHITE)
    p.brush([(0, 470), (960, 470)], 4)


@scene
def pee_laugh(p):
    p.stick(330, 470, 1.1, arms="pee", face="laugh")
    toilet(p, 620, 470, 1.1)
    p.brush([(345, 275), (400, 240), (470, 250), (560, 330)], 5, YELLOW)
    p.brush([(0, 470), (960, 470)], 4)
    p.bubble(170, 90, (290, 180), ["JAJAJAJA"], 34)
    p.hand("JAJA", 760, 60, 30)


# ---- out it comes -----------------------------------------------------------

@scene
def comes_out(p):
    toilet(p, 480, 520, 2.2)
    p.brush([(0, 60), (180, 120), (300, 200), (330, 250)], 12, YELLOW)
    p.brush([(0, 90), (160, 150), (290, 230), (340, 260)], 10, YELLOW)
    p.hand_lines(["MI AGÜITA", "AMARILLA"], 560, 30, 46, width=5)
    p.arrow(560, 110, 380, 160, bend=0.2)


@scene
def warm(p):
    drop(p, 380, 300, 1.4, face="smile")
    # thermometer from shapes
    p.rect((700, 90, 740, 380), width=3, fill=WHITE)
    p.ellipse((685, 370, 755, 440), width=3, fill=RED)
    p.rect((712, 250, 728, 380), width=0, fill=RED)
    for i in range(3):
        x = 250 + i * 110
        p.brush([(x, 150), (x + 15, 120), (x - 5, 95), (x + 12, 60)], 5, RED)
    p.hand("CÁLIDA", 90, 440, 44)
    p.hand("Y TIBIA", 520, 460, 44)


@scene
def flush_down(p):
    toilet(p, 330, 330, 1.0)
    p.rect((300, 330, 360, 540), width=3, fill=LGRAY)
    p.spray(330, 380, 18, YELLOW, 200)
    p.spray(330, 470, 18, YELLOW, 200)
    p.arrow(470, 280, 470, 500, width=7)
    p.hand("Y BAJA...", 530, 360, 50)


def pipe_base(p):
    p.brush([(-10, 300), (960, 300)], 5)
    p.fill(480, 520, BROWN)
    # the pipe is two rectangles: a straight run under the ground
    p.rect((-5, 380, 965, 440), width=4, fill=LGRAY)
    pee_speckles(p, 150, 410, 2, 60)
    p.typed("tubería", 820, 450, 22)
    p.arrow(850, 480, 800, 440, width=4)


@scene
def pipe(p):
    pipe_base(p)
    p.hand("POR UNA TUBERÍA", 200, 100, 50)


@scene
def pipe_casa(p):
    pipe_base(p)
    house(p, 70, 120, 200, 180, ["TU", "CASA"], fill=WHITE)
    p.arrow(170, 320, 170, 385, width=5)


@scene
def pipe_familia(p):
    pipe_base(p)
    house(p, 70, 120, 200, 180, ["TU", "CASA"], fill=WHITE)
    for i in range(5):
        p.stick(330 + i * 38, 295, 0.3, arms="out", width=4, face="flat")
    p.hand("TU FAMILIA", 310, 150, 30)
    p.spray(400, 410, 30, YELLOW, 400)


@scene
def pipe_trabajo(p):
    pipe_base(p)
    house(p, 70, 120, 200, 180, ["TU", "CASA"], fill=WHITE)
    for i in range(5):
        p.stick(330 + i * 38, 295, 0.3, arms="out", width=4, face="flat")
    p.hand("TU FAMILIA", 310, 150, 30)
    p.rect((620, 60, 900, 300), width=3, fill=LGRAY)
    for wx in range(640, 880, 60):
        for wy in (80, 150, 220):
            p.rect((wx, wy, wx + 36, wy + 40), width=3, fill=WHITE)
    p.typed("Tu lugar de trabajo", 600, 20, 26)
    p.spray(700, 410, 30, YELLOW, 400)


# ---- river, shepherd, cows, fields -----------------------------------------

@scene
def river(p):
    p.brush([(-10, 250), (200, 300), (400, 280), (600, 330), (970, 300)], 6)
    p.brush([(-10, 400), (250, 440), (500, 410), (700, 460), (970, 440)], 6)
    p.fill(480, 370, TURQ)
    p.rect((0, 120, 120, 170), width=4, fill=LGRAY)
    p.brush([(125, 150), (170, 190), (200, 280)], 8, YELLOW)
    pee_speckles(p, 350, 360, 3, 130)
    p.hand("UN RÍO", 400, 110, 50)
    p.typed("(la tubería)", 10, 90, 18)


@scene
def shepherd(p):
    water_band(p, 380, 540)
    pee_speckles(p, 500, 460, 3, 200)
    p.stick(300, 370, 0.95, arms="down", face="smile")
    p.brush([(380, 380), (395, 120), (370, 95), (350, 110)], 6, BROWN)
    p.ellipse((250, 120, 350, 140), width=3, fill=BROWN)
    p.brush([(260, 128), (340, 128)], 5, BROWN)
    p.hand("EL PASTOR", 480, 80, 44)
    p.arrow(470, 120, 360, 170)
    p.bubble(640, 250, (360, 190), ["QUÉ RICA"], 30)
    # a sheep: spray-can wool
    p.spray(760, 360, 45, LGRAY, 800)
    p.brush([(740, 390), (740, 420)], 5)
    p.brush([(780, 390), (782, 420)], 5)
    p.loop(715, 345, 13, 11, 5, n=8)


@scene
def cows(p):
    p.brush([(-10, 330), (300, 380), (600, 350), (970, 400)], 6)
    p.fill(480, 480, TURQ)
    pee_speckles(p, 300, 460, 4, 250)
    cow(p, 330, 250, 1.0, drink=True)
    cow(p, 700, 270, 0.9, drink=True)
    p.hand("LAS VAQUITAS", 470, 50, 40)
    p.brush([(620, 100), (620, 150), (390, 190)], 4)
    p.brush([(620, 150), (700, 200)], 4)


@scene
def fields(p):
    p.brush([(-10, 230), (960, 250)], 5)
    p.fill(480, 400, LIME)
    for row in range(5):
        y = 290 + row * 50
        p.brush([(0, y), (320, y + 5), (650, y - 6), (960, y + 4)], 4, GREEN)
    p.rect((80, 150, 110, 240), width=3, fill=LGRAY)
    p.brush([(95, 150), (160, 90), (300, 160), (420, 280)], 5, YELLOW)
    p.brush([(95, 150), (40, 90), (0, 130)], 5, YELLOW)
    for i in range(6):
        pee_speckles(p, 160 + i * 130, 330 + (i % 2) * 90, 1, 30)
    p.hand("RIEGA LOS CAMPOS", 250, 70, 44)


# ---- chorus mascot ----------------------------------------------------------

@scene
def drop_chorus(p):
    drop(p, 480, 320, 1.8, arms="wave")
    p.hand("MI AGÜITA AMARILLA", 150, 50, 48, width=5)


@scene
def drop_chorus_hola(p):
    drop(p, 480, 320, 1.8, arms="wave")
    p.hand("MI AGÜITA AMARILLA", 150, 50, 48, width=5)
    p.bubble(790, 230, (600, 280), ["HOLA"], 36)


@scene
def drop_chorus_otra(p):
    drop(p, 480, 320, 1.8, arms="wave")
    p.hand("MI AGÜITA AMARILLA", 150, 50, 48, width=5)
    p.bubble(790, 230, (600, 280), ["OTRA VEZ", "YO"], 32)


# ---- the sea ----------------------------------------------------------------

@scene
def sea(p):
    p.brush([(-10, 250), (970, 250)], 5, shake=0.5)
    p.fill(480, 400, DBLUE)
    p.brush([(0, 300), (150, 360), (260, 540)], 6)
    p.fill(40, 450, TAN)
    p.brush([(200, 540), (220, 420), (320, 300)], 26, TURQ)
    pee_speckles(p, 400, 320, 3, 120)
    # sailboat
    p.polygon([(640, 240), (760, 240), (740, 262), (660, 262)], width=3, fill=BROWN)
    p.polygon([(700, 110), (700, 235), (770, 235)], width=3, fill=WHITE)
    p.hand("EL MAR", 380, 90, 60)
    p.arrow(560, 150, 610, 300)


def underwater(p):
    sky(p)
    p.fill(5, 5, DBLUE)
    p.brush([(-10, 480), (300, 470), (620, 500), (970, 470)], 5)
    p.fill(480, 525, TAN)
    for x in (80, 850):
        p.brush([(x, 490), (x - 12, 430), (x + 8, 380), (x - 10, 330)], 7, GREEN)
    for i in range(6):
        p.loop(p.rng.uniform(50, 910), p.rng.uniform(40, 300), 8, 8, 3, WHITE, n=8)


@scene
def fishes(p):
    underwater(p)
    drop(p, 250, 280, 1.0, arms="up")
    for i, (x, y) in enumerate([(560, 200), (720, 300), (600, 400), (820, 150)]):
        p.fish(x, y, 0.8, color=[ORANGE, RED, LIME, PINK][i], flip=True)
    p.ellipse((420, 370, 470, 420), width=3, fill=RED)
    p.hand("PECECILLOS", 500, 40, 40, color=WHITE)


@scene
def squid(p):
    underwater(p)
    drop(p, 230, 280, 1.0, arms="wave")
    # squid: rectangle-ish body plus freehand tentacles
    p.polygon([(620, 60), (690, 150), (690, 320), (550, 320), (550, 150)], width=4, fill=PINK)
    for i in range(6):
        x = 560 + i * 25
        p.brush([(x, 320), (x + p.rng.uniform(-20, 20), 380), (x + p.rng.uniform(-25, 25), 440)], 6)
    p.brush([(590, 230)], 10, BLACK, 0.2)
    p.brush([(650, 230)], 10, BLACK, 0.2)
    p.hand("CALAMARES", 360, 40, 36, color=WHITE)
    p.hand("JUEGA CON", 30, 460, 30)


@scene
def jelly(p):
    underwater(p)
    drop(p, 200, 250, 1.0, arms="dance")
    for i, (x, y) in enumerate([(500, 160), (700, 240), (830, 120)]):
        d = ImageDraw.Draw(p.img)
        d.chord((x - 55, y - 45, x + 55, y + 45), 180, 360, outline=BLACK, width=3, fill=PURPLE if i else PINK)
        d.line((x - 55, y, x + 55, y), fill=BLACK, width=3)
        for k in range(5):
            tx = x - 40 + k * 20
            p.brush([(tx, y), (tx + 10, y + 50), (tx - 5, y + 100), (tx + 8, y + 150)], 4)
    p.hand("MEDUSAS", 450, 400, 50, color=WHITE)
    p.hand("AU", 280, 130, 30, color=RED)


@scene
def hake(p):
    underwater(p)
    drop(p, 200, 280, 1.0, arms="up")
    p.brush([(420, 250), (520, 190), (700, 200), (800, 260), (700, 320), (520, 320), (420, 250)], 6)
    p.brush([(800, 260), (880, 200), (870, 320), (800, 260)], 6)
    p.fill(620, 260, LGRAY)
    p.brush([(470, 240)], 9, BLACK, 0.2)
    p.hand("MERLUZA", 520, 60, 50, color=WHITE)


@scene
def you_eat(p):
    p.rect((0, 380, 960, 540), width=3, fill=BROWN)
    p.stick(260, 380, 0.9, arms="out", face="o")
    p.ellipse((420, 320, 740, 400), width=3, fill=WHITE)
    p.ellipse((450, 330, 710, 390), width=3, fill=WHITE)
    p.brush([(480, 360), (540, 335), (640, 340), (680, 360), (640, 380), (540, 380), (480, 360)], 5)
    p.fill(580, 360, LGRAY)
    p.brush([(680, 360), (705, 340), (705, 380), (680, 360)], 5)
    p.spray(580, 360, 40, YELLOW, 150)
    p.hand("TÚ", 180, 60, 60)
    p.arrow(230, 130, 250, 180)
    p.hand("QUE TE COMES", 470, 170, 40)
    p.bubble(790, 90, None, ["ÑAM"], 30)


@scene
def drop_sing(p):
    drop(p, 380, 330, 1.7, face="sing", arms="up")
    p.hand("MI AGÜITA AMARILLA", 150, 40, 48, width=5)
    note(p, 700, 250)


def note(p, x, y, s=1.0):
    p.ellipse((int(x), int(y), int(x + 30 * s), int(y + 22 * s)), width=3, fill=BLACK)
    p.brush([(x + 28 * s, y + 10 * s), (x + 30 * s, y - 70 * s), (x + 55 * s, y - 50 * s)], 5)


@scene
def drop_la1(p):
    drop(p, 380, 330, 1.7, face="sing", arms="up")
    note(p, 700, 250)
    p.hand("LA LA LA", 580, 120, 50)


@scene
def drop_la2(p):
    drop(p, 380, 330, 1.7, face="sing", arms="up")
    note(p, 700, 250)
    note(p, 820, 380, 0.8)
    p.hand("LA LA LA", 580, 120, 50)
    p.hand("LA LA", 60, 80, 40)


@scene
def drop_la3(p):
    drop(p, 380, 330, 1.7, face="sing", arms="up")
    note(p, 700, 250)
    note(p, 820, 380, 0.8)
    note(p, 100, 420, 0.7)
    p.hand("LA LA LA", 580, 120, 50)
    p.hand("LA LA", 60, 80, 40)
    p.hand("LAAAA", 560, 460, 40)


# ---- sun and vapour ---------------------------------------------------------

def sea_line(p, y=400):
    p.brush([(-10, y), (970, y + 5)], 5, shake=0.4)
    p.fill(480, 530, DBLUE)
    sky(p)


@scene
def sun(p):
    sea_line(p)
    p.ellipse((620, 40, 820, 240), width=3, fill=YELLOW)
    for a in range(0, 360, 30):
        r = math.radians(a)
        p.brush([(720 + 115 * math.cos(r), 140 + 115 * math.sin(r)), (720 + 170 * math.cos(r), 140 + 170 * math.sin(r))], 5, ORANGE)
    p.brush([(680, 120)], 10, BLACK, 0.2)
    p.brush([(760, 120)], 10, BLACK, 0.2)
    p.brush([(680, 180), (720, 200), (765, 178)], 5)
    drop(p, 250, 440, 0.6, face="hot")
    p.hand("EL SOL CALIENTA", 40, 60, 40)


@scene
def hundred(p):
    sea_line(p)
    for i in range(10):
        p.loop(p.rng.uniform(50, 910), p.rng.uniform(420, 520), 12, 10, 4, WHITE, n=8)
    p.rect((650, 60, 700, 330), width=3, fill=WHITE)
    p.rect((662, 70, 688, 330), width=0, fill=RED)
    p.ellipse((635, 310, 715, 390), width=3, fill=RED)
    p.hand("100°", 740, 80, 60, color=RED)
    drop(p, 300, 280, 1.2, face="hot")
    p.hand("¡QUEMA!", 60, 60, 44)


@scene
def up(p):
    sea_line(p)
    for i in range(6):
        p.spray(300 + p.rng.uniform(-60, 60), 330 - i * 50, 50, WHITE, 1500)
        p.spray(300 + p.rng.uniform(-60, 60), 330 - i * 50, 30, YELLOW, 300)
    p.arrow(560, 380, 560, 60, width=8)
    p.hand("PARA ARRIBA", 590, 200, 34)


@scene
def sky_trip(p):
    sky(p)
    cloud(p, 380, 250, 360)
    p.brush([(130, 120), (150, 110), (170, 120)], 4)
    p.brush([(200, 90), (220, 80), (240, 90)], 4)
    p.brush([(720, 380), (880, 360)], 6)
    p.polygon([(760, 372), (800, 330), (820, 368)], width=3, fill=WHITE)
    p.hand("VIAJA POR EL CIELO", 60, 40, 44)
    p.typed("avión", 790, 395, 20)


@scene
def city_arrive(p):
    sky(p)
    city(p)
    cloud(p, 480, 110, 300)
    p.hand("TU CIUDAD", 60, 40, 40)
    p.arrow(250, 90, 300, 250)


@scene
def rain_start(p):
    sky(p)
    city(p)
    cloud(p, 350, 90, 320, dark=True)
    cloud(p, 700, 70, 260, dark=True)
    rain(p, 150, 860, 140, 520, 55)
    p.hand("¡A DILUVIAR!", 560, 180, 40)


@scene
def rain_chorus(p):
    sky(p)
    city(p, 330)
    cloud(p, 480, 80, 500, dark=True)
    rain(p, 60, 900, 130, 520, 70)
    drop(p, 480, 250, 0.9, arms="wave")
    p.hand("MI AGÜITA AMARILLA", 170, 460, 40, color=RED)


# ---- getting everyone wet ---------------------------------------------------

@scene
def streets(p):
    p.brush([(-10, 330), (970, 320)], 5)
    p.fill(480, 440, GRAY)
    p.brush([(0, 430), (120, 430)], 6, WHITE)
    p.brush([(260, 432), (380, 428)], 6, WHITE)
    p.brush([(520, 430), (640, 434)], 6, WHITE)
    p.brush([(780, 430), (900, 428)], 6, WHITE)
    for x in (200, 610):
        p.rect((x, 250, x + 180, 320), width=3, fill=p.rng.choice([RED, BLUE]))
        p.rect((x + 40, 210, x + 140, 250), width=3, fill=WHITE)
        p.ellipse((x + 20, 300, x + 60, 340), width=3, fill=BLACK)
        p.ellipse((x + 120, 300, x + 160, 340), width=3, fill=BLACK)
    for x in (100, 450, 800):
        p.ellipse((x, 470, x + 110, 500), width=0, fill=YELLOW)
    rain(p, 0, 960, 20, 300, 45)
    p.hand("LAS CALLES", 60, 60, 44)


@scene
def dad(p):
    rain(p, 0, 960, 0, 520, 60)
    hy = p.stick(420, 500, 1.2, arms="up", face="o")
    p.brush([(395, hy + 22), (410, hy + 16), (420, hy + 20), (432, hy + 16), (447, hy + 22)], 6)
    p.rect((380, hy - 70, 460, hy - 30), width=3, fill=BLACK)
    p.rect((360, hy - 34, 480, hy - 26), width=3, fill=BLACK)
    p.hand("TU PADRE", 560, 120, 50)
    p.arrow(600, 190, 490, 250)
    p.bubble(720, 360, (500, 300), ["¿PERO QUÉ?"], 30)


def kitchen(p):
    p.rect((0, 330, 960, 540), width=3, fill=BROWN)
    p.rect((480, 300, 760, 340), width=3, fill=LGRAY)
    p.rect((600, 220, 615, 300), width=3, fill=LGRAY)
    p.rect((600, 220, 680, 235), width=3, fill=LGRAY)
    p.brush([(672, 238), (670, 300)], 7, YELLOW)
    for i in range(3):
        p.ellipse((500 + i * 50, 250 + i * 6, 560 + i * 50, 300), width=3, fill=WHITE)
    hy = p.stick(330, 450, 1.1, arms="out", face="smile")
    # hair and skirt, freehand
    p.brush([(300, hy - 25), (275, hy + 10), (270, hy + 60)], 7)
    p.brush([(360, hy - 25), (385, hy + 10), (390, hy + 60)], 7)
    p.polygon([(330, 360), (290, 410), (370, 410)], width=3, fill=RED)
    p.hand("TU MADRE", 60, 60, 44)


@scene
def mom(p):
    kitchen(p)
    p.hand("LAVA LA VAJILLA", 400, 90, 36)


@scene
def mom_aguita(p):
    kitchen(p)
    p.hand("LAVA LA VAJILLA", 400, 90, 36)
    p.hand("CON MI AGÜITA", 560, 380, 32, color=WHITE)
    p.hand("AMARILLA", 600, 430, 32, color=WHITE)
    p.arrow(700, 375, 675, 290, width=5)


@scene
def school(p):
    sky(p)
    p.brush([(-10, 420), (970, 415)], 5)
    p.fill(480, 480, GRAY)
    p.rect((250, 120, 710, 420), width=3, fill=ORANGE)
    for wx in range(280, 690, 90):
        for wy in (150, 240):
            p.rect((wx, wy, wx + 50, wy + 50), width=3, fill=TURQ)
    p.rect((440, 330, 520, 420), width=3, fill=BROWN)
    p.typed("COLEGIO", 420, 125, 26)
    for x in (100, 160, 800, 860):
        p.stick(x, 500, 0.35, arms="up", width=4, face="laugh")
    for x in (120, 480, 830):
        p.ellipse((x - 60, 470, x + 60, 495), width=0, fill=YELLOW)
    rain(p, 0, 960, 10, 400, 45)
    p.hand("EL PATIO DEL COLEGIO", 60, 30, 36)


@scene
def townhall(p):
    sky(p)
    p.rect((180, 180, 780, 480), width=3, fill=TAN)
    p.polygon([(180, 180), (480, 60), (780, 180)], width=3, fill=RED)
    for cx in (250, 350, 610, 710):
        p.rect((cx - 15, 220, cx + 15, 480), width=3, fill=WHITE)
    p.ellipse((440, 100, 520, 170), width=3, fill=WHITE)
    p.brush([(480, 135), (480, 110)], 4)
    p.brush([(480, 135), (500, 140)], 4)
    p.rect((440, 380, 520, 480), width=3, fill=BROWN)
    p.brush([(480, 60), (480, 10)], 5)
    p.rect((480, 10, 540, 30), width=0, fill=RED)
    p.rect((480, 30, 540, 50), width=0, fill=YELLOW)
    p.typed("AYUNTAMIENTO", 390, 190, 24)
    p.brush([(-10, 480), (970, 480)], 5)
    p.fill(480, 520, GRAY)
    rain(p, 0, 960, 0, 470, 55)
    p.hand("MOJA EL", 20, 40, 34)


@scene
def beer_again(p):
    beer(p, 360, 150, 4.0)
    p.hand("CERVEZA", 60, 60, 44)
    p.arrow(150, 120, 340, 250)
    p.typed("(hecha con agua...)", 620, 440, 24)
    p.hand("¿¿??", 700, 150, 60)


@scene
def dance1(p):
    drop(p, 380, 300, 1.5, arms="dance")
    p.hand("LELE LELE", 580, 110, 50)


@scene
def dance2(p):
    drop(p, 520, 300, 1.5, arms="wave", face="sing")
    p.hand("LELE LELE", 580, 110, 50)
    p.hand("LELE", 60, 400, 50)


def dog_body(p, x, y):
    p.brush([(x, y), (x + 150, y + 5), (x + 150, y + 60), (x, y + 55), (x, y)], 6)
    p.fill(x + 75, y + 30, BROWN)
    p.loop(x - 25, y - 30, 38, 30, 6, n=10)
    p.fill(x - 25, y - 30, BROWN)
    p.brush([(x - 45, y - 55), (x - 60, y - 10)], 12, BLACK)
    p.brush([(x - 35, y - 35)], 7, BLACK, 0.2)
    for lx in (10, 40, 110, 140):
        p.brush([(x + lx, y + 55), (x + lx, y + 110)], 6)
    p.brush([(x + 150, y + 10), (x + 185, y - 30)], 6)


@scene
def dog(p):
    p.brush([(-10, 440), (970, 440)], 5)
    p.fill(480, 500, LIME)
    dog_body(p, 300, 320)
    p.bubble(150, 120, (250, 280), ["GUAU GUAU"], 34)


@scene
def dog_pee(p):
    p.brush([(-10, 440), (970, 440)], 5)
    p.fill(480, 500, LIME)
    dog_body(p, 300, 320)
    p.brush([(600, 440), (610, 250), (590, 150)], 20, BROWN)
    p.spray(600, 120, 80, GREEN, 1400)
    p.brush([(455, 390), (520, 350), (585, 360), (595, 430)], 5, YELLOW)
    p.bubble(150, 120, (250, 280), ["GUAU"], 34)
    p.hand("OTRA AGÜITA", 560, 470, 34)


# ---- thinking and the ending ------------------------------------------------

@scene
def think(p):
    toilet(p, 620, 480, 1.0)
    p.stick(330, 480, 1.0, arms="pee", face="flat")
    p.brush([(0, 480), (960, 480)], 4)
    p.thought(250, 100, (320, 200), ["MMM..."], 34)


@scene
def where1(p):
    toilet(p, 620, 480, 1.0)
    p.stick(330, 480, 1.0, arms="pee", face="flat")
    p.brush([(0, 480), (960, 480)], 4)
    p.thought(250, 100, (320, 200), ["¿DÓNDE IRÁ?"], 34)


@scene
def where2(p):
    toilet(p, 620, 480, 1.0)
    p.stick(330, 480, 1.0, arms="pee", face="o")
    p.brush([(0, 480), (960, 480)], 4)
    p.thought(250, 100, (320, 200), ["¿DÓNDE IRÁ?"], 34)
    p.hand("¿DÓNDE IRÁ?", 580, 60, 34)
    p.hand("¿¿DÓNDE??", 640, 150, 30)


@scene
def world(p):
    p.ellipse((300, 60, 720, 480), width=3, fill=DBLUE)
    p.brush([(380, 150), (450, 120), (500, 180), (450, 250), (400, 230), (380, 150)], 5)
    p.fill(440, 185, GREEN)
    p.brush([(560, 250), (650, 230), (680, 320), (600, 400), (560, 330), (560, 250)], 5)
    p.fill(605, 310, GREEN)
    for i in range(9):
        a = p.rng.uniform(0, 2 * math.pi)
        rr = p.rng.uniform(0, 180)
        p.spray(510 + rr * math.cos(a), 270 + rr * math.sin(a), 35, YELLOW, 700)
    p.hand("EL MUNDO", 40, 40, 50)


@scene
def jungle(p):
    p.brush([(-10, 450), (970, 445)], 5)
    p.fill(480, 500, BROWN)
    for i, x in enumerate(range(60, 960, 150)):
        p.brush([(x, 450), (x + p.rng.uniform(-10, 10), 300)], 16, BROWN)
        p.spray(x, 260, 90, GREEN, 4500)
        p.spray(x, 250, 50, LIME, 900)
    p.brush([(440, 330), (480, 300), (520, 330)], 5)
    p.loop(480, 285, 18, 16, 5, n=8)
    p.hand("LA SELVA", 60, 40, 50)
    p.hand("MÁS VERDE", 560, 40, 40, color=GREEN)


@scene
def happy(p):
    p.stick(480, 500, 1.3, arms="up", face="laugh")
    for (x, y) in ((200, 150), (760, 180), (300, 400), (700, 420)):
        p.brush([(x, y + 20), (x - 25, y - 5), (x - 12, y - 20), (x, y - 8), (x + 12, y - 20), (x + 25, y - 5), (x, y + 20)], 5, RED)
        p.fill(x, y, RED)
    p.hand("¡QUÉ ALEGRÍA!", 180, 30, 50)


@scene
def filthy(p):
    p.rect((380, 180, 580, 480), width=3, fill=YELLOW)
    p.spray(480, 330, 90, BROWN, 6000)
    p.spray(480, 400, 70, GREEN, 1200)
    for (x, y) in ((340, 150), (620, 200), (560, 120)):
        p.ellipse((x - 8, y - 6, x + 8, y + 6), width=0, fill=BLACK)
        p.brush([(x - 12, y - 12), (x - 2, y - 6)], 3)
        p.brush([(x + 12, y - 12), (x + 2, y - 6)], 3)
    p.hand("UN LÍQUIDO", 60, 40, 50)
    p.hand("INMUNDO", 560, 470, 50)
    p.hand("PUAJ", 680, 280, 40, color=GREEN)


@scene
def outro_oh(p):
    drop(p, 480, 330, 2.2, face="sing")
    p.hand("OH OH OH OH", 200, 30, 50)


@scene
def outro_friends(p):
    p.stick(280, 480, 1.0, arms="out", face="smile")
    drop(p, 620, 360, 1.3, arms="wave")
    p.hand("MI AGÜITA AMARILLA", 160, 40, 44)
    p.hand("Y YO", 400, 480, 40)


@scene
def fin(p):
    p.hand("FIN", 360, 150, 120, width=10)
    p.typed("¡Gracias!", 420, 330, 36)
    drop(p, 780, 350, 0.6, face="sleep")
