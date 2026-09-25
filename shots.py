"""The animation, shot by shot.

Each shot has a foreground function `fn(p, c)` drawn every frame and an optional
background drawn once per boil step. `c.T` is song time, `c.t` time since the
shot started, `c.a` the shot's arguments from the timeline. A shot on a canvas
wider than the screen returns the camera's left edge.
"""

from props import *

SHOTS = {}


class Shot:
    def __init__(self, fn, w, h, bg):
        self.name, self.fn, self.w, self.h, self.bgcolor, self.bgfn = fn.__name__, fn, w, h, bg, None

    def bg(self, fn):
        self.bgfn = fn
        return fn


def shot(w=W, h=H, bg=WHITE):
    def deco(fn):
        s = Shot(fn, w, h, bg)
        SHOTS[s.name] = s
        return s
    return deco


def cam(x, lead, world):
    return max(0, min(world - W, x - lead))


def point_on(path, u):
    seg = [math.dist(a, b) for a, b in zip(path, path[1:])]
    goal = sum(seg) * (u % 1.0)
    for (a, b), L in zip(zip(path, path[1:]), seg):
        if goal <= L:
            k = goal / L if L else 0
            return (lerp(a[0], b[0], k), lerp(a[1], b[1], k))
        goal -= L
    return path[-1]


def flow(p, path, T, color=ORANGE, n=6, speed=0.8, width=4):
    """Little dashes sliding along a stream, so the pee visibly runs."""
    for k in range(n):
        u = (k / n + T * speed) % 1.0
        a, b = point_on(path, u), point_on(path, min(1, u + 0.03))
        p.brush([a, b], width, color, 0.3)


def rot_pts(pts, cx, cy, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [(int(cx + (x - cx) * c - (y - cy) * s), int(cy + (x - cx) * s + (y - cy) * c)) for x, y in pts]


def reveal(T, parts):
    """Characters shown for a bubble whose lines are sung in pieces: [(t0, t1, nchars), ...]."""
    n = 0
    for t0, t1, k in parts:
        n += int(k * ph(T, t0, t1))
    return n


def pops(p, T, times, words, spots, life=1.0, size=40, color=BLACK, rise=30):
    """Words that appear at `times` and float up a little before vanishing."""
    for k, t0 in enumerate(times):
        age = T - t0
        if 0 <= age < life:
            x, y = spots[k % len(spots)]
            p.part(f"pop{k}")
            p.hand(words[k % len(words)], x, y - rise * age / life, size, color=color)


def sweat(p, x, y, T, period=1.1, color=DBLUE):
    u = (T / period) % 1.0
    p.brush([(x, y + 40 * u), (x - 3, y + 40 * u + 10)], 5, color, 0.2)


def sea_front(p, T, y=400):
    p.rect((0, y, W, H), width=0, fill=DBLUE)
    p.brush([(-10, y), (970, y + 4)], 5, shake=0.4)
    for k in range(8):
        x = (k * 130 + T * 50) % 1040 - 40
        p.brush([(x, y + 40 + (k % 3) * 35), (x + 15, y + 32 + (k % 3) * 35), (x + 30, y + 40 + (k % 3) * 35)], 3, WHITE, 0.3)


# ---- the bar ----------------------------------------------------------------

@shot()
def bar(p, c):
    T = c.T
    # the bartender polishes a glass until he's shouted at, then slides a beer over
    if T < 19.6:
        wipe = 70 + 30 * math.sin(2 * math.pi * T / 0.9)
        _, (_, hand) = stick(p, 700, 440, 0.8, face="flat", arms=(-25, wipe))
        beer(p, hand[0] - 12, hand[1] - 30, 0.55, level=0)
    else:
        stick(p, 700, 440, 0.8, face="o" if T < 21 else "flat", arms=(-25, -100 if T < 20.8 else 25))
    face = "smile" if T < 14.6 else "flat"
    jump = 0.0
    if 18.9 <= T < 21.3:
        face = "angry"
        jump = -30 * math.sin(math.pi * ph(T, 18.9, 19.4))
    if T >= 22.0:
        face = "o" if T < 24.1 else "smile"
    if T < 21.3:
        arm = 60
    else:
        arm = path_at([(21.3, 100), (21.9, 165)], T)
    _, (_, hand) = stick(p, 260, 470 + jump, 0.9, face=face, arms=(-60, arm))
    if 19.6 <= T < 21.3:
        beer(p, lerp(640, 320, ease(ph(T, 19.6, 20.8))), 300, 0.7)
    elif T >= 21.3:
        beer(p, hand[0] - 8, hand[1] - 40, 0.7, level=1 - ph(T, 22.0, 24.0))
    if 0.27 <= T < 14.6:
        n = reveal(T, [(0.27, 1.7, 10), (4.86, 8.3, 11), (8.3, 9.9, 8)])
        p.bubble(300, 90, (275, 200), ["POR FAVOR,", "¿ME DAS UNA", "CERVEZA?"], 28, upto=n)
    elif 15.8 <= T < 18.9:
        p.bubble(300, 110, (275, 200), ["..."], 28)
    elif T >= 18.9:
        j = 4 * math.sin(T * 60) if T < 19.8 else 0
        p.bubble(300 + j, 90, (275, 200), ["DAME UNA", "CERVEZA!!"], 30)


@bar.bg
def _(p):
    p.rect((0, 360, 960, 400), width=3, fill=BROWN)
    p.rect((0, 400, 960, 540), width=3, fill=BROWN)
    p.brush([(0, 150), (960, 150)], 5)
    lay = random.Random(5)
    for bx in (560, 610, 660, 760, 820):
        p.rect((bx, 90, bx + 26, 150), width=3, fill=lay.choice([GREEN, DRED, BROWN]))
        p.rect((bx + 8, 70, bx + 18, 90), width=3)
    p.typed("BAR", 850, 20, 34)
    p.hand("EL CAMARERO", 610, 180, 24)


@shot()
def title(p, c):
    T = c.T
    say(p, "MI AGÜITA", 120, 120, 90, T, 24.6, 25.8, width=9)
    say(p, "AMARILLA", 180, 250, 90, T, 25.9, 27.3, width=9, color=YELLOW)
    if T > 27.6:
        p.typed("Los Toreros Muertos", 560, 430, 30)
    if T > 28.2:
        p.typed("(hecho en paint)", 600, 470, 18)
    x = path_at([(24.5, -80), (26.5, 110)], T)
    hop = bob(T, 30) if T < 26.5 else bob(T, 6)
    drop(p, x, 420 + hop, 0.6, walk=T * 2 if T < 26.5 else None)


# ---- drinking and peeing (verse 1 and verse 2 both use these) --------------

BEER_SPOTS = [(320 + (i % 10) * 56 + random.Random(i).randint(-14, 14) + (i // 10) * 9,
               230 + (i // 10) * 58 + random.Random(i + 99).randint(-12, 12),
               random.Random(i + 7).uniform(0.45, 0.62)) for i in range(40)]


@shot()
def beers(p, c):
    t, T = c.t, c.T
    n = min(40, int(t / 0.13) + 1)
    for x, y, s in BEER_SPOTS[:n]:
        beer(p, x, y, s)
    p.part("count")
    p.hand(f"{n} CERVEZAS", 360, 70, 50, width=5)
    if t > c.a["hoy"]:
        p.hand("HOY", 800, 150, 34)
        p.arrow(520, 140, 560, 230)
    sway = 6 * math.sin(2 * math.pi * t / 2.2)
    lift = 110 + 55 * abs(math.sin(math.pi * beat(T)))
    _, (_, hand) = stick(p, 150, 480, 0.9, face="smile", arms=(-70, lift), lean=sway)
    beer(p, hand[0] - 6, hand[1] - 42, 0.6, level=0.7)


@shot()
def expel(p, c):
    t = c.t
    stick(p, 420, 500, 1.2, arms="down", face="o", walk=t * 2.2)
    rr = lerp(20, 85, ease(ph(t, 0, 2.5))) + 4 * math.sin(2 * math.pi * t * 3)
    p.part("belly")
    p.loop(420, 330, rr, rr * 0.9, 6, closed=True)
    if rr > 40:
        p.fill(420 - rr * 0.5, 335, YELLOW)
    if rr > 50:
        p.hand("40", 385, 310, 40)
    n = int(20 * ph(t, c.a["bt0"], c.a["bt1"]))
    if n:
        p.bubble(700, 120, (470, 150), ["TENGO QUE", "EXPULSARLAS"], 28, upto=n)
    if t > c.a["bt1"] + 0.3:
        p.hand("¡¡!!", 180 + 5 * math.sin(t * 50), 150, 60)


@shot()
def stairs(p, c):
    t = c.t
    keys = [(0, (40, 480)), (0.6, (120, 480))]
    for k in range(6):
        keys.append((0.6 + 0.62 * (k + 1), (165 + 90 * k, 420 - 60 * k)))
    top = keys[-1][0]
    keys.append((top + 1.3, (865, 120)))
    x, y = path_at(keys, t)
    if 0.6 < t < top:
        u = ((t - 0.6) / 0.62) % 1.0
        y -= 40 * math.sin(math.pi * u)
    if t < top + 1.3:
        sw = 25 * math.sin(t * 9)
        stick(p, x, y, 0.45, arms=(-30 + sw, 30 + sw), walk=t * 2.5, face="smile")
    else:
        p.hand("OCUPADO", 740, 140, 22)


@stairs.bg
def _(p):
    for i in range(6):
        p.rect((120 + i * 90, 420 - i * 60, 960, 480 - i * 60), width=3, fill=LGRAY)
    p.rect((0, 480, 960, 540), width=3, fill=BROWN)
    p.typed("BAR", 40, 490, 26)
    p.rect((830, 10, 900, 120), width=3, fill=BROWN)
    p.typed("WC", 848, 40, 24)
    p.hand("ARRIBA", 80, 100, 44)
    p.arrow(200, 170, 340, 190, bend=-0.2)


PEE_PATH = [(345, 372), (420, 320), (500, 305), (570, 322), (608, 350)]


@shot()
def pee(p, c):
    t, T = c.t, c.T
    laughing = t >= c.a["laugh"]
    shake = 3 * math.sin(t * 40) if laughing else 0
    stick(p, 330 + shake, 470, 1.1, arms=(-30, 15), face="laugh" if laughing else "smile")
    path = [(x, y + (8 * math.sin(T * 14) if 0 < i < 4 else 0)) for i, (x, y) in enumerate(PEE_PATH)]
    path[0] = (path[0][0] + shake, path[0][1])
    p.brush(path, 5, YELLOW, upto=ph(t, 0, 0.5))
    if t > 0.5:
        flow(p, path, T, n=4, speed=1.5, width=3)
        for k in range(3):
            p.brush([(600 + p.rng.uniform(-25, 25), 340 - p.rng.uniform(0, 20))], 5, YELLOW, 0.2)
    if laughing:
        times = [c.a["laugh"] + 0.35 * k for k in range(30)]
        spots = [(random.Random(k).randint(80, 560), random.Random(k + 50).randint(60, 250)) for k in range(30)]
        pops(p, t, times, ["JA"], spots, life=1.1, size=34)


@pee.bg
def _(p):
    toilet(p, 620, 470, 1.1)
    p.brush([(0, 470), (960, 470)], 4)


# ---- out it comes -----------------------------------------------------------

STREAM = [(0, 60), (180, 120), (300, 200), (335, 255)]


@shot()
def comes_out(p, c):
    T = c.T
    for dy in (0, 30):
        path = [(x, y + dy + (6 * math.sin(T * 9 + i) if i else 0)) for i, (x, y) in enumerate(STREAM)]
        p.brush(path, 12 - dy // 10, YELLOW)
        flow(p, path, T + dy, n=5, speed=1.2)
    say(p, "SALE DE MÍ", 60, 440, 40, T, 60.27, 61.4)
    say(p, "MI AGÜITA", 560, 30, 46, T, 61.67, 62.9, width=5)
    say(p, "AMARILLA", 560, 95, 46, T, 63.0, 63.9, width=5, color=ORANGE)
    if T > 62.4:
        p.part("arrow")
        p.arrow(560, 170, 380, 200, bend=0.2)


@comes_out.bg
def _(p):
    toilet(p, 480, 520, 2.2)


@shot()
def warm(p, c):
    T, t = c.T, c.t
    squash = 1 + 0.3 * math.sin(t * 14) * max(0, 1 - t / 0.9)
    rot = 8 * math.sin(2 * math.pi * T / 1.8) if T > 68 else 0
    drop(p, 380, 300 + bob(T, 6), 1.4, squash=squash, rot=rot, arms=(-60, 60))
    sweat(p, 330, 250, T)
    sweat(p, 440, 240, T + 0.5)
    for i in range(3):
        x = 250 + i * 110 + 8 * math.sin(T * 5 + i)
        p.brush([(x, 150), (x + 15, 120), (x - 5, 95), (x + 12, 60)], 5, RED)
    top = lerp(370, 190, ease(ph(T, 64.8, 67.5)))
    p.rect((712, int(top), 728, 380), width=0, fill=RED)
    say(p, "CÁLIDA", 90, 440, 44, T, 64.83, 65.9)
    say(p, "Y TIBIA", 520, 460, 44, T, 65.99, 67.2)
    if T > 69.0:
        p.bubble(160, 110, (320, 190), ["¿Y AHORA", "QUÉ?"], 28)


@warm.bg
def _(p):
    p.rect((700, 90, 740, 380), width=3, fill=WHITE)
    p.ellipse((685, 370, 755, 440), width=3, fill=RED)


# ---- through the pipes, one long canvas the camera follows ------------------

PIPE_W = 4200


@shot(w=PIPE_W)
def pipes(p, c):
    T = c.T
    if T < 74.4:
        # the flush: a spinning swirl in the bowl, with the drop going round in it
        pts = [(292 + (40 - k * 2.2) * math.cos(k * 0.6 + T * 9), 158 + (14 - k * 0.7) * math.sin(k * 0.6 + T * 9)) for k in range(18)]
        p.brush(pts, 3)
        say(p, "FLUSH!!", 360, 40, 40, T, 72.3, 72.9)
        x, y = 292 + 25 * math.cos(T * 9), 145 + 6 * math.sin(T * 9)
        drop(p, x, y, 0.28, face="ouch", rot=(T * 500) % 360, legs=False)
    elif T < 75.4:
        u = ph(T, 74.4, 75.4)
        drop(p, 300, lerp(170, 425, u * u), 0.28, face="ouch", legs=False)
        x = 300
    else:
        x = path_at([(75.4, 300), (79.3, 1380), (84.2, 2180), (88.3, 3100), (89.7, 3700)], T)
        drop(p, x, 425, 0.28, walk=T * 3)
    say(p, "Y BAJA POR UNA TUBERÍA", cam(x, 320, PIPE_W) + 560, 60, 36, T, 74.36, 76.0, hold=3)
    say(p, "TU", 1330, 140, 30, T, 78.7, 78.9)
    say(p, "CASA", 1315, 185, 30, T, 79.0, 79.5)
    for k in range(5):
        up = (int((T - BEAT0) / BEAT) + k) % 2
        stick(p, 2050 + 60 * k, 248, 0.35, arms="up" if up else "out", width=4, face="smile")
    say(p, "TU FAMILIA", 2030, 110, 36, T, 83.8, 84.5)
    if T > 87.3:
        p.typed("Tu lugar de trabajo", 2900, 30, 30)
    return (cam(x, 320, PIPE_W), 0)


@pipes.bg
def _(p):
    p.brush([(-10, 250), (1400, 252), (2800, 248), (PIPE_W + 10, 250)], 5)
    p.rect((270, 250, 330, 450), width=4, fill=LGRAY)
    p.rect((270, 400, PIPE_W + 5, 450), width=4, fill=LGRAY)
    p.rect((278, 244, 322, 404), width=0, fill=LGRAY)
    p.fill(100, 500, BROWN)
    p.fill(600, 320, BROWN)
    p.rect((60, 20, 520, 250), width=3)
    p.typed("BAR (el váter de arriba)", 70, 26, 18)
    toilet(p, 300, 250, 0.8)
    house(p, 1250, 40, 260, 210)
    p.rect((2850, 70, 3350, 250), width=3, fill=LGRAY)
    for wx in range(2880, 3320, 70):
        for wy in (90, 160):
            p.rect((wx, wy, wx + 40, wy + 45), width=3, fill=WHITE)
    p.brush([(1800, 480), (1815, 470), (1830, 485), (1845, 472), (1860, 482)], 6, PINK)
    p.typed("gusano", 1790, 495, 16)
    p.brush([(2600, 505), (2650, 500)], 8, WHITE)
    p.hand("AL RÍO", 3650, 120, 44)
    p.arrow(3700, 190, 3900, 230)


# ---- river, shepherd, cows ---------------------------------------------------

RIVER_W = 2900


@shot(w=RIVER_W)
def river(p, c):
    T = c.T
    for k in range(30):
        x = (k * 97 + T * 60) % RIVER_W
        y = 385 + (k % 3) * 50
        p.brush([(x, y), (x + 15, y - 8), (x + 30, y)], 3, WHITE, 0.3)
    p.brush([(120, 170), (170 + 5 * math.sin(T * 8), 240), (200, 400)], 7, YELLOW)
    if T < 90.5:
        u = ph(T, 89.7, 90.5)
        x, y = lerp(130, 220, u), lerp(170, 400, u * u)
        drop(p, x, y, 0.45, face="ouch", legs=False, rot=u * 200)
    else:
        x = path_at([(90.5, 220), (93.6, 950), (98.3, 1700), (104.2, 2500)], T)
        y = 405 + 6 * math.sin(2 * math.pi * T / 1.3)
        p.spray(x - 70, y + 10, 30, YELLOW, 250)
        drop(p, x, y, 0.45, rot=6 * math.sin(2 * math.pi * T / 1.3), arms=(-110, 110), legs=False)
        splash(p, 220, 400, ph(T, 90.5, 91.1), 0.8)
    say(p, "Y LLEGA A UN RÍO", cam(x, 380, RIVER_W) + 260, 60, 44, T, 89.74, 91.9, hold=1.5)
    # the shepherd bends down, scoops, drinks
    bend = path_at([(93.6, 0), (94.4, 35), (95.4, 35), (96.0, 0)], T)
    arm_r = path_at([(93.6, 30), (94.4, 10), (95.4, 10), (96.0, 170)], T)
    head, (_, hand) = stick(p, 1050, 330, 0.8, face="o" if 94.4 < T < 96.3 else "smile", arms=(-30, arm_r), lean=bend)
    p.part("hat")
    p.ellipse((int(head[0] - 50), int(head[1] - 30), int(head[0] + 50), int(head[1] - 12)), width=3, fill=BROWN)
    p.brush([(head[0] - 28, head[1] - 22), (head[0] - 20, head[1] - 45), (head[0] + 20, head[1] - 45), (head[0] + 28, head[1] - 22)], 5, BROWN)
    p.brush([(1000, 330), (985, 120), (1005, 95), (1025, 110)], 6, BROWN)
    say(p, "LA BEBE EL PASTOR", 760, 50, 40, T, 93.6, 96.0)
    if T > 96.3:
        p.bubble(1260, 170, (head[0] + 30, head[1]), ["¡QUÉ RICA!"], 30)
    for k, cx in enumerate((1800, 2150)):
        cow(p, cx, 255, 0.9, head=0.5 + 0.5 * math.sin(2 * math.pi * T / 1.6 + k * 2))
    say(p, "LAS VAQUITAS", 1850, 50, 40, T, 98.3, 101.3)
    if T > 101.3:
        p.part("pointer")
        p.brush([(1990, 100), (1990, 150), (1760, 190)], 4)
        p.brush([(1990, 150), (2090, 200)], 4)
    return (cam(x, 380, RIVER_W), 0)


@river.bg
def _(p):
    p.brush([(-10, 330), (500, 350), (1000, 322), (1500, 352), (2000, 330), (2500, 352), (RIVER_W + 10, 330)], 6)
    p.fill(500, 500, TURQ)
    p.rect((-5, 150, 120, 190), width=4, fill=LGRAY)
    p.typed("(la tubería)", 10, 125, 18)
    for tx in (600, 2600):
        p.brush([(tx, 330), (tx + 5, 230)], 16, BROWN)
        p.spray(tx, 200, 70, GREEN, 3000)
    p.spray(1250, 300, 40, LGRAY, 900)
    p.loop(1210, 290, 13, 11, 5, n=8)
    p.brush([(1235, 325), (1235, 340)], 5)
    p.brush([(1265, 325), (1267, 340)], 5)


SPROUTS = [(random.Random(k).randint(40, 920), 290 + 50 * random.Random(k + 3).randint(0, 4), random.Random(k + 9).uniform(0, 2))
           for k in range(28)]


@shot()
def fields(p, c):
    T = c.T
    a = math.radians(70 * math.sin(T * 1.5))
    dx = math.sin(a)
    nozzle = (480, 150)
    p.brush([nozzle, (480 + dx * 150, 80), (480 + dx * 300, 180), (480 + dx * 330, 250)], 5, YELLOW)
    p.spray(480 + dx * 330, 260, 35, YELLOW, 250)
    for x, y, d in SPROUTS:
        h = 40 * ph(T, 104.5 + d, 106.5 + d)
        if h > 2:
            p.part(f"sprout{x}")
            p.brush([(x, y), (x + 2, y - h)], 4, GREEN)
            if h > 20:
                p.brush([(x + 2, y - h * 0.6), (x + 14, y - h * 0.8)], 4, GREEN)
                p.brush([(x + 2, y - h * 0.5), (x - 12, y - h * 0.7)], 4, GREEN)
            if T > 108.3 + d / 2:
                p.brush([(x + 2, y - h)], 10, RED, 0.2)
    say(p, "RIEGA LOS CAMPOS", 250, 60, 44, T, 104.26, 106.9)


@fields.bg
def _(p):
    p.brush([(-10, 230), (960, 250)], 5)
    p.fill(480, 400, LIME)
    for row in range(5):
        y = 290 + row * 50
        p.brush([(0, y), (320, y + 5), (650, y - 6), (960, y + 4)], 4, GREEN)
    p.rect((470, 150, 490, 240), width=3, fill=LGRAY)


# ---- chorus -----------------------------------------------------------------

@shot()
def chorus(p, c):
    T = c.T
    sw = math.sin(2 * math.pi * T / (2 * BEAT))
    drop(p, 480, 300 + bob(T, 18), 1.5, arms=(-110 + 45 * sw, 110 + 45 * sw), walk=T / (2 * BEAT),
         squash=1 - 0.08 * abs(math.sin(math.pi * beat(T))), rot=8 * math.sin(2 * math.pi * T / (4 * BEAT)))
    for text, t0, t1, x, y, size in c.a["lines"]:
        say(p, text, x, y, size, T, t0, t1, width=5)
    words, t0 = c.a["bubble"]
    if T > t0:
        p.bubble(790, 230, (580, 280), words, 32)


# ---- the sea ----------------------------------------------------------------

@shot()
def sea(p, c):
    T = c.T
    for k in range(8):
        x = (k * 140 + T * 40) % 1100 - 60
        p.brush([(x, 300 + (k % 4) * 55), (x + 15, 292 + (k % 4) * 55), (x + 30, 300 + (k % 4) * 55)], 3, WHITE, 0.3)
    bx = 700 + 10 * (T - 117)
    tilt = 6 * math.sin(2 * math.pi * T / 2)
    p.polygon(rot_pts([(bx - 60, 240), (bx + 60, 240), (bx + 40, 262), (bx - 40, 262)], bx, 250, tilt), width=3, fill=BROWN)
    p.polygon(rot_pts([(bx, 110), (bx, 235), (bx + 70, 235)], bx, 250, tilt), width=3, fill=WHITE)
    if T < 122.3:
        x, y = path_at([(117.0, (240, 470)), (118.8, (350, 330)), (120.5, (500, 300))], T)
        y += 5 * math.sin(T * 5)
        if T > 121.9:
            y -= 70 * math.sin(math.pi * ph(T, 121.9, 122.3))
        drop(p, x, y, 0.45, arms=(-120, 120), legs=T > 121.9)
    splash(p, 500, 300, ph(T, 122.25, 122.6), 0.8, WHITE)
    if T > 122.25:
        p.hand("¡PLAF!", 440, 190, 40)
    say(p, "Y BAJA AL MAR", 330, 80, 56, T, 117.06, 119.3)


@sea.bg
def _(p):
    p.brush([(-10, 250), (970, 250)], 5, shake=0.5)
    p.fill(480, 400, DBLUE)
    p.brush([(0, 300), (150, 360), (260, 540)], 6)
    p.fill(40, 450, TAN)
    p.brush([(200, 540), (220, 420), (320, 300)], 26, TURQ)


# ---- under the sea, another long canvas -------------------------------------

SEA_W = 3300
BUBBLES = [(random.Random(k).uniform(0, SEA_W), random.Random(k + 1).random()) for k in range(40)]


@shot(w=SEA_W)
def underwater(p, c):
    T = c.T
    x = path_at([(122.6, 200), (126.3, 1000), (129.9, 1850), (133.5, 2650), (135.4, 2800)], T)
    cx = cam(x, 300, SEA_W)
    for wx in (80, 700, 1150, 1750, 2300, 2850, 3200):
        s = math.sin(T * 2 + wx)
        p.part(f"weed{wx}")
        p.brush([(wx, 490), (wx - 12 + 8 * s, 430), (wx + 8 + 12 * s, 380), (wx - 10 + 16 * s, 330)], 7, GREEN)
    for bx, b0 in BUBBLES:
        y = 480 - ((b0 + T * 0.25) % 1) * 480
        p.part(f"bub{bx}")
        p.loop(bx + 6 * math.sin(T * 3 + bx), y, 7, 7, 3, WHITE, n=8)
    # pececillos going round in circles
    for k in range(5):
        a = T * 1.2 + k * 1.26
        fish(p, 650 + 220 * math.cos(a), 250 + 90 * math.sin(a), 0.7, color=[ORANGE, RED, LIME, PINK, YELLOW][k],
             flip=math.sin(a) > 0, tail=math.sin(T * 12 + k))
    say(p, "JUEGA CON LOS PECECILLOS", cx + 40, 40, 40, T, 122.6, 124.6, hold=1.6, color=WHITE)
    # the squid bobs, waves and squirts ink
    sy = 180 + 25 * math.sin(T * 2)
    if T > 128.4:
        p.spray(1450, sy + 260, 30 + 120 * ph(T, 128.4, 129.8), BLACK, 1500 * ph(T, 128.4, 129.8) + 50)
    p.polygon([(1450, sy - 120), (1520, sy - 30), (1520, sy + 140), (1380, sy + 140), (1380, sy - 30)], width=4, fill=PINK)
    for k in range(6):
        x = 1390 + k * 25
        s = math.sin(T * 4 + k)
        p.part(f"tent{k}")
        p.brush([(x, sy + 140), (x + 15 * s, sy + 200), (x - 20 * s, sy + 260)], 6)
    p.brush([(1420, sy + 50)], 10, BLACK, 0.2)
    p.brush([(1480, sy + 50)], 10, BLACK, 0.2)
    say(p, "JUEGA CON LOS CALAMARES", cx + 40, 40, 40, T, 126.33, 128.5, hold=1.3, color=WHITE)
    # jellyfish pulse
    d = ImageDraw.Draw(p.img)
    for k, (jx, jy) in enumerate([(2000, 200), (2200, 300), (2400, 160)]):
        pu = math.sin(T * 5 + k)
        jy -= 20 * pu
        hh = 45 * (1 + 0.15 * pu)
        d.chord((jx - 55, jy - hh, jx + 55, jy + hh), 180, 360, outline=BLACK, width=3, fill=PURPLE if k else PINK)
        d.line((jx - 55, jy, jx + 55, jy), fill=BLACK, width=3)
        for m in range(5):
            tx = jx - 40 + m * 20
            s = math.sin(T * 5 + m + k)
            p.part(f"jt{k}{m}")
            p.brush([(tx, jy), (tx + 10 * s, jy + 50), (tx - 8 * s, jy + 100), (tx + 8 * s, jy + 150)], 4)
    say(p, "JUEGA CON LAS MEDUSAS", cx + 40, 40, 40, T, 129.91, 131.9, hold=0.8, color=WHITE)
    # the merluza takes the hook and gets pulled out
    hy = path_at([(133.0, -60), (134.2, 250), (134.8, 250), (135.4, -120)], T)
    p.brush([(2950, -10), (2950, hy)], 3, BLACK, 0.2)
    p.brush([(2950, hy), (2950, hy + 25), (2935, hy + 30), (2928, hy + 18)], 4, GRAY, 0.3)
    if T < 134.8:
        mx, my = path_at([(133.5, 3250), (134.6, 2980)], T), 275
    else:
        mx, my = 2980, hy + 25
    p.part("merluza")
    p.brush([(mx, my), (mx + 60, my - 45), (mx + 190, my - 40), (mx + 280, my), (mx + 190, my + 50), (mx + 60, my + 50), (mx, my)], 6)
    p.brush([(mx + 280, my), (mx + 330, my - 45 + 10 * math.sin(T * 10)), (mx + 325, my + 50), (mx + 280, my)], 6)
    p.fill(mx + 150, my, LGRAY)
    p.brush([(mx + 40, my - 10)], 9, BLACK, 0.2)
    say(p, "Y CON LAS MERLUZAS", cx + 40, 40, 40, T, 132.83, 134.5, color=WHITE)
    # our drop swims along
    stung = 131.0 < T < 132.4
    sw = 40 * math.sin(2 * math.pi * T / 0.8)
    drop(p, x + (5 * math.sin(T * 50) if stung else 0), 270 + 30 * math.sin(T), 0.9,
         face="ouch" if stung else "smile", arms=(-90 - sw, 90 + sw), walk=T * 1.5)
    if stung:
        p.hand("¡AU!", x - 20, 130, 40, color=RED)
    return (cx, 0)


@underwater.bg
def _(p):
    p.fill(5, 5, DBLUE)
    p.brush([(-10, 480), (800, 470), (1600, 500), (2400, 470), (SEA_W + 10, 485)], 5)
    p.fill(100, 525, TAN)
    for x in (400, 1300, 2600):
        p.ellipse((x, 450, x + 90, 500), width=3, fill=GRAY)


@shot()
def eat(p, c):
    T, t = c.T, c.t
    u = 0.5 - 0.5 * math.cos(2 * math.pi * t / 1.3)
    bites = int((t + 0.65) / 1.3)
    fork = (lerp(560, 300, u), lerp(345, 180, u))
    head, _ = stick(p, 260, 380, 0.9, face="o" if u > 0.8 else "chew", arms=(-40, None))
    p.part("arm")
    p.brush([(260, 216), (fork[0] + 20, fork[1] + 30)], 6)
    L = max(30, 200 - 40 * bites)
    p.part("plate-fish")
    p.brush([(480, 360), (500, 340), (480 + L, 345), (480 + L + 30, 330), (480 + L + 30, 385), (480 + L, 372), (500, 380), (480, 360)], 5)
    p.fill(500 + L / 2, 360, LGRAY)
    p.brush([fork, (fork[0] + 60, fork[1] + 40)], 5, GRAY)
    for k in range(3):
        p.brush([(fork[0] - 4 + k * 5, fork[1] - 12), (fork[0] - 4 + k * 5, fork[1])], 3, GRAY, 0.2)
    times = [135.4 + 1.3 * k + 0.65 for k in range(5)]
    pops(p, T, times, ["ÑAM"], [(330, 120), (350, 100), (320, 130)], life=0.8, size=34)
    say(p, "QUE TÚ TE COMES", 470, 170, 40, T, 135.44, 137.9)
    say(p, "TÚ", 150, 40, 60, T, 136.2, 136.5)
    if T > 136.5:
        p.part("arrow")
        p.arrow(200, 110, 235, 160)


@eat.bg
def _(p):
    p.rect((0, 380, 960, 540), width=3, fill=BROWN)
    p.ellipse((420, 320, 760, 400), width=3, fill=WHITE)
    p.ellipse((450, 330, 730, 390), width=3, fill=WHITE)


@shot()
def sing(p, c):
    T = c.T
    las = [146.10 + 1.19 * k for k in range(10)]
    mouth = max(pulse(T, las, 0.6), 0.6 * pulse(T, [140.7, 141.0, 141.6, 142.1, 142.6], 0.4))
    sw = 20 * math.sin(2 * math.pi * T / (2 * BEAT))
    drop(p, 380, 320, 1.6, face="sing", mouth=mouth, arms=(-150 + sw, 150 - sw), rot=6 * math.sin(2 * math.pi * T / (4 * BEAT)))
    say(p, "MI AGÜITA AMARILLA", 150, 40, 48, T, 140.71, 143.4, width=5)
    for k, t0 in enumerate(las):
        if T >= t0:
            r = random.Random(k)
            x = r.randint(600, 840) if k % 2 == 0 else r.randint(30, 180)
            p.part(f"la{k}")
            p.hand("LA", x, r.randint(130, 470), 44)
    for i in range(40):
        tb = 141 + i * 2 * BEAT
        age = T - tb
        if 0 <= age < 3:
            note(p, 470 + 60 * age + 20 * math.sin(age * 3), 250 - 70 * age, 0.7)


# ---- sun, boiling, vapour, sky, city ----------------------------------------

@shot(bg=TURQ)
def sun(p, c):
    T = c.T
    sy = lerp(560, 150, ease(ph(T, 158.7, 161.2)))
    p.ellipse((620, int(sy - 100), 820, int(sy + 100)), width=3, fill=YELLOW)
    for a in range(0, 360, 30):
        r = math.radians(a + T * 40)
        p.part(f"ray{a}")
        p.brush([(720 + 115 * math.cos(r), sy + 115 * math.sin(r)), (720 + 170 * math.cos(r), sy + 170 * math.sin(r))], 5, ORANGE)
    p.part("sunface")
    p.brush([(680, sy - 20)], 10, BLACK, 0.2)
    p.brush([(760, sy - 20)], 10, BLACK, 0.2)
    p.brush([(680, sy + 40), (720, sy + 60), (765, sy + 38)], 5)
    sea_front(p, T)
    hot = T > 161.5
    drop(p, 250, 430 + bob(T, 4), 0.6, face="hot" if hot else "smile", legs=False)
    if hot:
        sweat(p, 225, 400, T, 0.8)
        for k in range(3):
            pts = [(lerp(620, 320, j / 8), lerp(230 + 40 * k, 380 + 10 * k, j / 8) + 10 * math.sin(j * 1.4 - T * 8)) for j in range(9)]
            p.part(f"heat{k}")
            p.brush(pts, 3, ORANGE)
    say(p, "EL SOL CALIENTA", 40, 60, 40, T, 158.99, 161.99)
    say(p, "MI AGÜITA AMARILLA", 40, 300, 28, T, 162.0, 164.4)
    if T > 164.4:
        p.part("arrow")
        p.arrow(160, 335, 225, 390)


@shot(bg=TURQ)
def hundred(p, c):
    T = c.T
    sea_front(p, T)
    for k in range(14):
        r = random.Random(k)
        bx, b0 = r.uniform(40, 920), r.random()
        y = 530 - ((b0 + T * 0.9) % 1) * 140
        p.part(f"boil{k}")
        p.loop(bx, y, 10, 9, 4, WHITE, n=8)
    heat = ph(T, 167.2, 170.2)
    p.rect((650, 60, 700, 330), width=3, fill=WHITE)
    p.rect((662, int(lerp(320, 70, ease(heat))), 688, 330), width=0, fill=RED)
    p.ellipse((635, 310, 715, 390), width=3, fill=RED)
    say(p, "100°", 740, 80, 60, T, 169.14, 170.2, color=RED)
    amp = 6 * ph(T, 168, 170)
    drop(p, 300 + amp * math.sin(T * 50), 280, 1.2, face="hot", arms=(-60, 60))
    sweat(p, 250, 230, T, 0.6)
    sweat(p, 350, 220, T + 0.3, 0.6)
    say(p, "LA PONE A CIEN GRADOS", 40, 470, 34, T, 167.17, 170.2)
    if T > 170.4:
        p.hand("¡QUEMA!", 60 + 5 * math.sin(T * 40), 60, 44)


@shot(bg=TURQ)
def up(p, c):
    T = c.T
    sea_front(p, T)
    if T < 173.2:
        drop(p, 300 + 6 * math.sin(T * 60), 330, 1.0, face="hot", arms=(-60, 60))
    else:
        u = ph(T, 173.2, 177.4)
        vy, vx = lerp(330, -150, u), 300 + 30 * math.sin(T * 2)
        for k in range(3):
            p.spray(vx + 40 * (k - 1), vy + 20 * (k % 2), 70, WHITE, 1500)
        p.spray(vx, vy, 50, YELLOW, 400)
        p.part("ghost")
        p.brush([(vx - 22, vy - 8)], 9, BLACK, 0.2)
        p.brush([(vx + 18, vy - 8)], 9, BLACK, 0.2)
        p.brush([(vx - 20, vy + 14), (vx, vy + 24), (vx + 20, vy + 12)], 5, BLACK, 0.5)
        for k in range(1, 4):
            p.spray(vx - 10 * k, vy + 110 * k, 40 - 8 * k, WHITE, 500)
        if u < 0.1:
            p.hand("¡PUF!", 360, 200, 44)
    say(p, "LA MANDA", 590, 150, 34, T, 172.34, 173.6)
    if T > 174.25:
        p.part("arrow")
        u = ph(T, 174.25, 175.0)
        p.arrow(560, 380, 560, lerp(380, 60, u), width=8)
    say(p, "PARA ARRIBA", 590, 200, 34, T, 174.25, 175.9)


SKY_W = 2200


@shot(w=SKY_W, bg=TURQ)
def skycity(p, c):
    T = c.T
    x = path_at([(177.6, 400), (180.9, 1700)], T)
    cloud(p, x, 130, 280, face=True, dots=1400)
    px = 1100 - 250 * (T - 177.6)
    p.part("plane")
    p.brush([(px, 330), (px + 160, 320)], 6)
    p.polygon([(px + 40, 326), (px + 80, 290), (px + 100, 322)], width=3, fill=WHITE)
    p.typed("avión", px + 70, 340, 20)
    for k, (bx, by) in enumerate([(300, 280), (360, 250), (420, 290)]):
        f = 10 * math.sin(T * 12 + k)
        p.part(f"bird{k}")
        p.brush([(bx - 20, by + f), (bx, by + 10), (bx + 20, by + f)], 4)
    cx = cam(x, 480, SKY_W)
    say(p, "VIAJA POR EL CIELO", cx + 60, 40, 44, T, 177.63, 179.2, hold=0.2)
    say(p, "LLEGA A TU CIUDAD", cx + 60, 40, 44, T, 179.44, 180.6)
    return (cam(x, 480, SKY_W), 0)


@skycity.bg
def _(p):
    city(p, 1200, SKY_W, 300)


@shot(bg=TURQ)
def rain_city(p, c):
    T = c.T
    rain(p, T, 60, 900, 130, 540, 70, density=ph(T, 181.99, 182.6))
    grey = T > 181.99
    if grey:
        cloud(p, 200, 70, 220, GRAY, pee=False, dots=900)
        cloud(p, 780, 70, 220, GRAY, pee=False, dots=900)
    cloud(p, 480, 90, 300, GRAY if grey else WHITE, face=True, dots=1400)
    say(p, "¡EMPIEZA A DILUVIAR!", 100, 180, 40, T, 181.17, 183.1)
    if T > 184.5:
        y = lerp(150, 380, ph(T, 184.5, 190.3))
        x = 480 + 60 * math.sin(T)
        d = ImageDraw.Draw(p.img)
        d.chord((int(x - 70), int(y - 180), int(x + 70), int(y - 80)), 180, 360, outline=BLACK, width=3, fill=RED)
        p.part("handle")
        p.brush([(x, y - 130), (x, y - 70)], 4)
        drop(p, x, y, 0.6, arms=(-160, 160), legs=True)
        if T > 185.5:
            p.hand("¡WIII!", x + 60, y - 60, 30)


@rain_city.bg
def _(p):
    city(p, 0, 960, 330)


# ---- getting everyone wet ---------------------------------------------------

def car(p, x, y, color, key):
    p.part(key)
    p.rect((int(x), y, int(x + 180), y + 70), width=3, fill=color)
    p.rect((int(x + 40), y - 40, int(x + 140), y), width=3, fill=WHITE)
    for wx in (x + 40, x + 140):
        p.ellipse((int(wx - 20), y + 50, int(wx + 20), y + 90), width=3, fill=BLACK)
        a = -wx / 20
        p.line((wx, y + 70), (wx + 16 * math.cos(a), y + 70 + 16 * math.sin(a)), WHITE, 3)


PUDDLES = (150, 500, 850)


@shot()
def streets(p, c):
    T = c.T
    rain(p, T, 0, 960, 0, 470, 45)
    for key, x, y, col in (("car1", lerp(-200, 1100, ph(T, 190.5, 194.7)), 250, RED),
                           ("car2", lerp(1100, -250, ph(T, 190.5, 194.7)), 360, BLUE)):
        car(p, x, y, col, key)
        for px in PUDDLES:
            if abs(x + 90 - px) < 90:
                p.spray(px, 440, 60, YELLOW, 400)
    say(p, "MOJA LAS CALLES", 60, 60, 44, T, 190.5, 192.6)


@streets.bg
def _(p):
    p.brush([(-10, 330), (970, 320)], 5)
    p.fill(480, 440, GRAY)
    for x in (0, 260, 520, 780):
        p.brush([(x, 430), (x + 120, 430)], 6, WHITE)
    for x in PUDDLES:
        p.ellipse((x - 55, 470, x + 55, 500), width=0, fill=YELLOW)


@shot()
def dad(p, c):
    T = c.T
    rain(p, T, 0, 960, 0, 520, 60)
    x = lerp(1050, 420, ease(ph(T, 194.7, 196.0)))
    moving = T < 196.0
    head, _ = stick(p, x, 500, 1.2, face="flat" if moving else "o", arms=(-30, 30) if moving else (-140, 140),
                    walk=T * 2 if moving else None)
    hx, hy = head
    p.part("tash")
    p.brush([(hx - 25, hy + 22), (hx - 10, hy + 16), (hx, hy + 20), (hx + 12, hy + 16), (hx + 27, hy + 22)], 6)
    u = ph(T, 196.4, 197.6)
    hat_x, hat_y, spin = hx + 200 * u, hy - 50 - 260 * u, 200 * u
    p.polygon(rot_pts([(hat_x - 40, hat_y - 40), (hat_x + 40, hat_y - 40), (hat_x + 40, hat_y), (hat_x - 40, hat_y)], hat_x, hat_y, spin), width=3, fill=BLACK)
    p.polygon(rot_pts([(hat_x - 60, hat_y - 4), (hat_x + 60, hat_y - 4), (hat_x + 60, hat_y + 4), (hat_x - 60, hat_y + 4)], hat_x, hat_y, spin), width=3, fill=BLACK)
    say(p, "MOJA A TU PADRE", 60, 60, 44, T, 195.0, 196.9)
    if T > 197.0:
        p.bubble(720, 330, (hx + 40, hy + 20), ["¿PERO QUÉ?"], 30)


@shot()
def mom(p, c):
    T = c.T
    path = [(672, 238), (670 + 3 * math.sin(T * 10), 270), (670, 300)]
    p.brush(path, 7, YELLOW)
    flow(p, path, T, n=3, speed=2.0, width=3)
    plate = (560 + 40 * math.cos(2 * math.pi * T / 0.7), 285 + 12 * math.sin(2 * math.pi * T / 0.7))
    head, _ = stick(p, 330, 450, 1.1, face="smile", arms=(-40, None))
    hx, hy = head
    p.part("hair")
    p.brush([(hx - 30, hy - 25), (hx - 55, hy + 10), (hx - 60, hy + 60)], 7)
    p.brush([(hx + 30, hy - 25), (hx + 55, hy + 10), (hx + 60, hy + 60)], 7)
    p.polygon([(330, 360), (290, 410), (370, 410)], width=3, fill=RED)
    p.brush([(330, 250), (plate[0] - 25, plate[1])], 6)
    p.ellipse((int(plate[0] - 30), int(plate[1] - 25), int(plate[0] + 30), int(plate[1] + 25)), width=3, fill=WHITE)
    n = 1 + int((T - 198) / 1.6)
    for k in range(n):
        p.ellipse((780, 320 - 10 * k, 880, 336 - 10 * k), width=3, fill=WHITE)
    if n > 1:
        p.part("sparkle")
        tw = 10 + 6 * math.sin(T * 12)
        p.brush([(860, 300 - 10 * n - tw), (860, 300 - 10 * n + tw)], 4, YELLOW)
        p.brush([(860 - tw, 300 - 10 * n), (860 + tw, 300 - 10 * n)], 4, YELLOW)
    say(p, "TU MADRE", 60, 60, 44, T, 198.02, 198.8)
    say(p, "LAVA LA VAJILLA", 430, 120, 36, T, 199.0, 200.5)
    say(p, "CON MI AGÜITA", 540, 380, 32, T, 200.8, 202.0, color=WHITE)
    say(p, "AMARILLA", 580, 430, 32, T, 202.0, 203.0, color=WHITE)
    if T > 203.0:
        p.part("arrow")
        p.arrow(690, 375, 675, 300, width=5)
    if T > 204.3:
        p.bubble(820, 175, (hx + 40, hy), ["¡QUÉ", "LIMPIO!"], 26)


@mom.bg
def _(p):
    p.rect((0, 330, 960, 540), width=3, fill=BROWN)
    p.rect((480, 300, 760, 340), width=3, fill=LGRAY)
    p.rect((600, 220, 615, 300), width=3, fill=LGRAY)
    p.rect((600, 220, 680, 235), width=3, fill=LGRAY)


@shot(bg=TURQ)
def school(p, c):
    T = c.T
    for k, x in enumerate((100, 170, 790, 860)):
        off = k * BEAT / 2
        y = 500 + bob(T + off, 40)
        stick(p, x, y, 0.35, arms="up", width=4, face="laugh")
        if beat(T + off) < 0.2:
            p.spray(x, 485, 45, YELLOW, 300)
    rain(p, T, 0, 960, 10, 400, 45)
    say(p, "MOJA EL PATIO DEL COLEGIO", 40, 20, 34, T, 207.0, 208.9)


@school.bg
def _(p):
    p.brush([(-10, 420), (970, 415)], 5)
    p.fill(480, 480, GRAY)
    p.rect((250, 120, 710, 420), width=3, fill=ORANGE)
    for wx in range(280, 690, 90):
        for wy in (150, 240):
            p.rect((wx, wy, wx + 50, wy + 50), width=3, fill=TURQ)
    p.rect((440, 330, 520, 420), width=3, fill=BROWN)
    p.typed("COLEGIO", 420, 125, 26)
    for x in (130, 480, 830):
        p.ellipse((x - 60, 470, x + 60, 495), width=0, fill=YELLOW)


@shot(bg=TURQ)
def townhall(p, c):
    T = c.T
    top = [(480 + 12 * k, 10 + 6 * math.sin(k - T * 8)) for k in range(6)]
    mid = [(x, y + 20) for x, y in top]
    bot = [(x, y + 40) for x, y in top]
    p.polygon([(int(x), int(y)) for x, y in top + mid[::-1]], width=2, fill=RED)
    p.polygon([(int(x), int(y)) for x, y in mid + bot[::-1]], width=2, fill=YELLOW)
    for ang, L, wdt in ((T * 360 / 2, 28, 3), (T * 30, 18, 5)):
        a = math.radians(ang)
        p.line((480, 135), (480 + L * math.sin(a), 135 - L * math.cos(a)), BLACK, wdt)
    rain(p, T, 0, 960, 0, 470, 55)
    say(p, "MOJA EL AYUNTAMIENTO", 60, 490, 34, T, 210.6, 212.6, color=WHITE)


@townhall.bg
def _(p):
    p.rect((180, 180, 780, 480), width=3, fill=TAN)
    p.polygon([(180, 180), (480, 60), (780, 180)], width=3, fill=RED)
    for cx in (250, 350, 610, 710):
        p.rect((cx - 15, 220, cx + 15, 480), width=3, fill=WHITE)
    p.ellipse((440, 100, 520, 170), width=3, fill=WHITE)
    p.rect((440, 380, 520, 480), width=3, fill=BROWN)
    p.brush([(480, 60), (480, 5)], 5)
    p.typed("AYUNTAMIENTO", 390, 190, 24)
    p.brush([(-10, 480), (970, 480)], 5)
    p.fill(480, 520, GRAY)


# ---- instrumental: round and round -------------------------------------------

CX, CY, RX, RY = 480, 290, 300, 190


def on_ring(deg):
    a = math.radians(deg)
    return (CX + RX * math.cos(a), CY + RY * math.sin(a))


@shot()
def cycle(p, c):
    T = c.T
    speed = (1170 - 90) / 12.5
    deg = 90 + speed * min(T, 240.0) - speed * 227.5
    x, y = on_ring(deg)
    dizzy = T > 240.0
    drop(p, x, y - 20, 0.4, face="ouch" if dizzy else "smile", walk=None if dizzy else T * 4,
         rot=8 * math.sin(T * 6) if dizzy else 0)
    if dizzy:
        for k in range(3):
            a = T * 5 + k * 2.1
            p.part(f"star{k}")
            p.hand("*", x - 10 + 40 * math.cos(a), y - 110 + 10 * math.sin(a), 24, color=ORANGE)
        p.typed("(y vuelta a empezar)", 600, 505, 22)


@cycle.bg
def _(p):
    p.loop(CX, CY, RX, RY, 5, n=24)
    for deg in range(0, 360, 60):
        a0, a1 = on_ring(deg + 22), on_ring(deg + 32)
        p.arrow(*a0, *a1, width=4)
    # (angle on the ring, label, where the label goes relative to the ring point)
    stations = [
        (90, "BAR", (20, 0)), (150, "TUBERÍA", (-150, 25)), (210, "RÍO", (-90, -60)),
        (270, "CIELO", (40, -50)), (330, "CIUDAD", (-40, 20)), (30, "GRIFO", (40, 20)),
    ]
    for deg, label, (ox, oy) in stations:
        x, y = on_ring(deg)
        lx, ly = x + ox, y + oy
        if deg == 90:
            beer(p, x - 80, y - 50, 0.7)
        elif deg == 150:
            p.rect((int(x - 60), int(y - 20), int(x - 10), int(y + 5)), width=3, fill=LGRAY)
        elif deg == 210:
            p.brush([(x - 100, y + 10), (x - 70, y), (x - 40, y + 12)], 12, TURQ)
        elif deg == 270:
            p.spray(x - 80, y, 30, LGRAY, 700)
        elif deg == 330:
            p.rect((int(x + 10), int(y - 60), int(x + 40), int(y)), width=3, fill=LGRAY)
            p.rect((int(x + 45), int(y - 40), int(x + 70), int(y)), width=3, fill=LGRAY)
        elif deg == 30:
            p.rect((int(x + 20), int(y - 10), int(x + 70), int(y)), width=3, fill=LGRAY)
            p.brush([(x + 65, y + 2), (x + 65, y + 25)], 6, YELLOW)
        p.hand(label, lx, ly, 26)
    p.hand_lines(["EL CICLO DE", "MI AGÜITA"], 330, 240, 36)


# ---- dancing, a dog, and thinking about it all ------------------------------

@shot()
def lele(p, c):
    T = c.T
    n = int((T - BEAT0) / BEAT)
    lay = random.Random(n)
    for k in range(10):
        p.spray(lay.randint(20, 940), lay.randint(20, 520), 40, lay.choice([RED, LIME, DBLUE, PINK, ORANGE, PURPLE]), 500)
    sw = math.sin(2 * math.pi * T / BEAT)
    drop(p, 480, 300 + bob(T, 25), 1.5, face="sing", mouth=abs(sw), arms=(-120 + 60 * sw, 120 + 60 * sw),
         walk=T / BEAT, rot=10 * math.sin(2 * math.pi * T / (2 * BEAT)))
    times = [243.71, 245.99, 247.71, 249.29, 250.82]
    pops(p, T, times, ["LELE"], [(60, 120), (660, 110), (80, 420), (680, 430), (320, 60)], life=1.6, size=50)


GUAU = [251.97 + 1.15 * k for k in range(6)]


@stable
def dog_body(p, x, y, leg_up=0.0, bark=0.0, walk=None):
    p.brush([(x, y), (x + 150, y + 5), (x + 150, y + 60), (x, y + 55), (x, y)], 6)
    p.fill(x + 75, y + 30, BROWN)
    hy = y - 30 - 8 * bark
    p.loop(x - 25, hy, 38, 30, 6, n=10, closed=True)
    p.fill(x - 25, hy, BROWN)
    p.brush([(x - 45, hy - 25), (x - 60, hy + 20)], 12, BLACK)
    p.brush([(x - 35, hy - 5)], 7, BLACK, 0.2)
    if bark > 0.2:
        p.brush([(x - 62, hy + 10), (x - 85, hy + 5)], 5)
        p.brush([(x - 62, hy + 18), (x - 82, hy + 30)], 5)
    sw = 0 if walk is None else 15 * math.sin(2 * math.pi * walk)
    for k, lx in enumerate((10, 40, 110, 140)):
        s = sw if k % 2 else -sw
        if lx == 140 and leg_up:
            p.brush([(x + lx, y + 55), (x + lx + 50 * leg_up, y + 55 - 30 * leg_up)], 6)
        else:
            p.brush([(x + lx, y + 55), (x + lx + s, y + 110)], 6)
    p.brush([(x + 150, y + 10), (x + 185, y - 30 + 8 * math.sin(p.boil * 2))], 6)


@shot()
def dog(p, c):
    T = c.T
    x = path_at([(255.4, 300), (256.3, 430)], T)
    leg = ph(T, 256.3, 256.6)
    b = pulse(T, GUAU, 0.4)
    dog_body(p, x, 320, leg_up=leg, bark=b, walk=T * 2.5 if 255.4 < T < 256.3 else None)
    if T > 256.6:
        p.part("pee")
        p.brush([(x + 190, 350), (x + 230, 330), (x + 260, 370), (x + 270, 430)], 5, YELLOW, upto=ph(T, 256.6, 257.0))
        r = 50 * ph(T, 257.0, 258.3)
        if r > 3:
            p.ellipse((int(x + 270 - r), 425, int(x + 270 + r), 445), width=0, fill=YELLOW)
    pops(p, T, GUAU, ["GUAU", "GUAU!", "GUAU"], [(x - 190, 200), (x - 230, 150), (x - 180, 230)], life=0.8, size=40)
    say(p, "OTRA AGÜITA", 560, 470, 34, T, 257.2, 258.0)


@dog.bg
def _(p):
    p.brush([(-10, 440), (970, 440)], 5)
    p.fill(480, 500, LIME)
    p.brush([(740, 440), (750, 250), (730, 150)], 20, BROWN)
    p.spray(740, 120, 80, GREEN, 3500)


@shot()
def think(p, c):
    T = c.T
    face = "flat" if T < 286.9 else "o"
    stick(p, 330, 470, 1.1, arms=(-165 + 12 * math.sin(T * 12), 15), face=face)
    p.brush(PEE_PATH, 5, YELLOW)
    flow(p, PEE_PATH, T, n=4, speed=1.5, width=3)
    size = lerp(8, 34, ph(T, 282.5, 283.2))
    p.part("thought")
    if T < 284.44:
        p.thought(250, 100, (320, 200), ["MMM..."], size)
    else:
        p.thought(250, 100, (320, 200), ["¿DÓNDE IRÁ?"], 34)
    say(p, "¿DÓNDE IRÁ?", 580, 60, 34, T, 285.44, 286.2)
    say(p, "¿¿DÓNDE??", 640, 150, 30, T, 286.9, 287.8)
    say(p, "¿DÓNDE?", 620, 250, 44, T, 288.0, 288.4)


@think.bg
def _(p):
    toilet(p, 620, 470, 1.1)
    p.brush([(0, 470), (960, 470)], 4)


CONTINENTS = [(0.3, 200, 60, 50), (1.9, 330, 70, 60), (3.4, 250, 50, 70), (4.9, 360, 45, 35)]


@shot()
def world(p, c):
    T = c.T
    p.ellipse((300, 90, 700, 490), width=3, fill=DBLUE)
    for k, (lon, y, rx, ry) in enumerate(CONTINENTS):
        a = lon + T * 1.2
        if math.cos(a) > 0.2:
            x = 500 + 185 * math.sin(a)
            p.part(f"land{k}")
            p.loop(x, y, rx * math.cos(a), ry, 5, closed=True, n=10)
            p.fill(x, y, GREEN)
    n = int(12 * ph(T, 288.6, 291.3))
    for k in range(n):
        r = random.Random(k)
        a, d = r.uniform(0, 2 * math.pi), r.uniform(0, 170)
        p.spray(500 + d * math.cos(a), 290 + d * math.sin(a), 35, YELLOW, 600)
    drop(p, 500, 45 + bob(T, 5), 0.35, rot=12 * math.sin(T * 4), arms=(-120, 120))
    say(p, "SE ESPARCIRÁ POR EL MUNDO", 20, 30, 32, T, 288.44, 290.9)


@shot()
def jungle(p, c):
    T = c.T
    for k in range(7):
        x = 60 + 140 * k
        h = 150 * ph(T, 291.7 + 0.15 * k, 292.5 + 0.15 * k)
        if h > 2:
            p.part(f"trunk{k}")
            p.brush([(x, 450), (x + 5, 450 - h)], 16, BROWN)
        g = ph(T, 292.2 + 0.15 * k, 293.2 + 0.15 * k)
        if g > 0:
            p.spray(x, 300, 90 * g, GREEN, 4500 * g)
            p.spray(x, 290, 50 * g, LIME, 900 * g)
    if T > 293.3:
        sw = 30 * math.sin(T * 4)
        p.part("monkey")
        p.brush([(480, 330), (480 + sw, 390)], 5)
        p.loop(480 + sw, 410, 18, 16, 5, n=8)
        p.brush([(480 + sw - 10, 430), (480 + sw - 20, 470)], 5)
        p.brush([(480 + sw + 10, 430), (480 + sw + 20, 470)], 5)
    say(p, "PONDRÁ VERDE LA SELVA", 40, 30, 40, T, 291.59, 293.6)


@jungle.bg
def _(p):
    p.brush([(-10, 450), (970, 445)], 5)
    p.fill(480, 500, BROWN)


@shot()
def happy(p, c):
    T, t = c.T, c.t
    jump = -60 * abs(math.sin(math.pi * t / 0.5))
    up = int(t / 0.5) % 2
    stick(p, 480, 500 + jump, 1.3, arms=(-150, 150) if up else (-100, 100), face="laugh")
    for k in range(7):
        age = T - (294.5 + 0.35 * k)
        if age >= 0:
            r = random.Random(k)
            heart(p, r.choice([r.randint(120, 330), r.randint(630, 850)]), 480 - 120 * age, 1.0)
    say(p, "¡LO QUE MÁS ME ALEGRA!", 100, 30, 40, T, 294.44, 295.5)


@shot()
def filthy(p, c):
    T = c.T
    for k in range(6):
        r = random.Random(k)
        bx, b0 = r.randint(400, 560), r.random()
        by = 470 - ((b0 + T * 0.4) % 1) * 270
        p.part(f"fb{k}")
        p.loop(bx, by, 6, 6, 3, BROWN, n=8)
    for k in range(3):
        w = 1.7 + k * 0.4
        fx, fy = 480 + 190 * math.sin(w * T + k), 150 + 50 * math.sin(2 * w * T + k)
        p.ellipse((int(fx - 8), int(fy - 6), int(fx + 8), int(fy + 6)), width=0, fill=BLACK)
        f = 6 * math.sin(T * 40)
        p.part(f"wing{k}")
        p.brush([(fx - 12, fy - 12 + f), (fx - 2, fy - 6)], 3)
        p.brush([(fx + 12, fy - 12 + f), (fx + 2, fy - 6)], 3)
    say(p, "MI AGÜITA AMARILLA", 40, 30, 36, T, 296.9, 297.7)
    say(p, "SERÁ UN LÍQUIDO", 40, 90, 36, T, 298.44, 299.2)
    say(p, "INMUNDO", 560, 470, 50, T, 299.2, 300.0)
    if T > 300.6:
        g = 1 + 0.15 * math.sin(T * 10)
        p.hand("PUAJ", 680, 280, 40 * g, color=GREEN)


@filthy.bg
def _(p):
    p.rect((380, 180, 580, 480), width=3, fill=YELLOW)
    p.spray(480, 330, 90, BROWN, 6000)
    p.spray(480, 400, 70, GREEN, 1200)


# ---- the end ------------------------------------------------------------------

OHS = [303.71, 307.71, 311.98, 316.25, 318.44]


@shot()
def oh(p, c):
    T = c.T
    mouth = pulse(T, OHS, 1.5)
    sw = 15 * math.sin(2 * math.pi * T / (4 * BEAT))
    drop(p, 480, 290, 1.9, face="sing", mouth=mouth, arms=(-130 + sw, 130 + sw), rot=sw / 3)
    spots = [(80, 80), (700, 90), (90, 400), (720, 400), (380, 470)]
    for k, t0 in enumerate(OHS):
        if T >= t0:
            p.part(f"oh{k}")
            p.hand("OH", *spots[k], 60 + 10 * k)
    for i in range(40):
        age = T - (304 + i * 2 * BEAT)
        if 0 <= age < 3:
            note(p, 600 + 50 * age, 250 - 60 * age + 20 * math.sin(age * 4), 0.6)


UMS = [322.36 + 0.87 * k for k in range(10)]


@shot()
def friends(p, c):
    T = c.T
    nx = lerp(-100, 320, ease(ph(T, 318.6, 322.5)))
    moving = T < 322.5
    waving = T > 327.0
    wv = 30 * math.sin(T * 8)
    stick(p, nx, 480, 1.0, arms=(-40, 100 if not waving else -150 + wv), walk=T * 2 if moving else None, face="smile")
    drop(p, nx + 240, 380, 1.1, arms=(-80, 60) if not waving else (-150 - wv, 60), walk=T * 2 if moving else None)
    say(p, "MI AGÜITA AMARILLA", 160, 40, 44, T, 318.66, 320.2)
    say(p, "Y YO", 400, 110, 40, T, 321.0, 321.5)
    for k, t0 in enumerate(UMS):
        age = T - t0
        if 0 <= age < 2:
            base = (nx + 20, 200) if k % 2 else (nx + 250, 230)
            note(p, base[0] + 40 * age, base[1] - 60 * age, 0.5)
    if T > 330.0:
        p.bubble(nx + 400, 150, (nx + 300, 250), ["¡ADIÓS!"], 30)


@friends.bg
def _(p):
    p.brush([(-10, 480), (970, 480)], 4)


@shot()
def fin(p, c):
    T = c.T
    say(p, "FIN", 360, 150, 120, T, 331.7, 332.6, width=10)
    if T > 331.8:
        p.typed("¡Gracias!", 420, 330, 36)
    drop(p, 780, 350, 0.6, face="sleep")
    for k in range(10):
        age = T - (332 + 0.9 * k)
        if 0 <= age < 2.5:
            p.part(f"z{k}")
            p.hand("Z", 800 + 25 * age + 8 * math.sin(age * 3), 250 - 50 * age, 20 + 8 * age)


# ---- the cut list -------------------------------------------------------------

CHORUS_1 = {"lines": [("MI AGÜITA AMARILLA", 109.71, 111.8, 150, 40, 48),
                      ("MI AGÜITA AMARILLA", 113.24, 115.4, 150, 470, 48)],
            "bubble": (["HOLA"], 115.6)}
CHORUS_2 = {"lines": [("MI AGÜITA AMARILLA", 213.71, 219.2, 150, 40, 48),
                      ("MI AGÜITA AMARILLA", 223.65, 225.0, 150, 470, 48),
                      ("MI AGÜITA", 225.64, 226.1, 30, 230, 30),
                      ("AMARILLA", 226.1, 226.7, 30, 275, 30)],
              "bubble": (["OTRA VEZ", "YO"], 219.8)}

# (start in seconds, shot, arguments). Times come from whisper word timestamps;
# 3:04-3:32 uses re-transcribed clips because the full pass drifted ~5 s early there.
TIMELINE = [
    (0.0, "bar", {}),
    (24.5, "title", {}),
    (30.1, "beers", {"hoy": 5.5}),
    (37.5, "expel", {"bt0": 0.25, "bt1": 4.9}),
    (45.4, "stairs", {}),
    (50.8, "pee", {"laugh": 2.0}),
    (60.2, "comes_out", {}),
    (64.7, "warm", {}),
    (72.0, "pipes", {}),
    (89.7, "river", {}),
    (104.2, "fields", {}),
    (109.7, "chorus", CHORUS_1),
    (117.0, "sea", {}),
    (122.6, "underwater", {}),
    (135.4, "eat", {}),
    (140.7, "sing", {}),
    (158.7, "sun", {}),
    (167.1, "hundred", {}),
    (172.3, "up", {}),
    (177.6, "skycity", {}),
    (181.2, "rain_city", {}),
    (190.5, "streets", {}),
    (194.7, "dad", {}),
    (198.0, "mom", {}),
    (206.8, "school", {}),
    (210.5, "townhall", {}),
    (213.7, "chorus", CHORUS_2),
    (227.5, "cycle", {}),
    (243.7, "lele", {}),
    (251.9, "dog", {}),
    (258.4, "beers", {"hoy": 7.4}),
    (266.6, "expel", {"bt0": 1.1, "bt1": 4.9}),
    (273.6, "stairs", {}),
    (279.4, "pee", {"laugh": 1.5}),
    (282.4, "think", {}),
    (288.4, "world", {}),
    (291.6, "jungle", {}),
    (294.4, "happy", {}),
    (296.9, "filthy", {}),
    (303.7, "oh", {}),
    (318.6, "friends", {}),
    (331.6, "fin", {}),
]
END = 338.83
