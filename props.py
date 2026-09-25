"""Characters and props, posable for animation. Each helper reseeds the brush so its
wobble only changes on boil steps, not whenever something else appears on screen."""

import functools
import math

from paint import *

BEAT = 0.4592  # seconds per beat, 130.7 BPM, measured from the song's onsets
BEAT0 = 0.31   # time of a downbeat


def stable(fn):
    @functools.wraps(fn)
    def wrap(p, *a, **k):
        p.part(fn.__name__)
        return fn(p, *a, **k)
    return wrap


# ---- timing helpers ---------------------------------------------------------

def ph(t, a, b):
    """0 before a, 1 after b, linear in between."""
    if b <= a:
        return 1.0 if t >= a else 0.0
    return max(0.0, min(1.0, (t - a) / (b - a)))


def ease(u):
    return u * u * (3 - 2 * u)


def lerp(a, b, u):
    return a + (b - a) * u


def path_at(keys, t):
    """Piecewise-linear value from [(time, value), ...]; values may be tuples."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            u = ph(t, t0, t1)
            if isinstance(v0, tuple):
                return tuple(lerp(a, b, u) for a, b in zip(v0, v1))
            return lerp(v0, v1, u)
    return keys[-1][1]


def beat(T):
    """Phase within the current beat, 0..1."""
    return ((T - BEAT0) / BEAT) % 1.0


def bob(T, amp=10):
    """A little hop on every beat."""
    return -amp * abs(math.sin(math.pi * beat(T)))


def pulse(T, times, decay=0.35):
    """1 right at any of `times`, fading out after it."""
    best = 0.0
    for s in times:
        if 0 <= T - s < decay:
            best = max(best, 1 - (T - s) / decay)
    return best


def say(p, text, x, y, size, T, t0, t1=None, hold=None, **kw):
    """Handwritten caption that writes itself on between t0 and t1, then stays (for `hold` seconds)."""
    if T < t0 or (hold is not None and T > (t1 or t0) + hold):
        return
    t1 = t0 + 0.05 * len(text) if t1 is None else t1
    p.part("say:" + text)
    n = len(text) if T >= t1 else int(len(text) * ph(T, t0, t1)) + 1
    p.hand(text, x, y, size, upto=n, **kw)


def xf(x, y, s=1.0, rot=0.0, flip=False):
    """Local-to-canvas transform: scale, mirror, rotate (degrees) around the anchor."""
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    f = -1 if flip else 1

    def T(px, py):
        px, py = px * s * f, py * s
        return (x + px * c - py * sn, y + px * sn + py * c)
    return T


def limb(T, base, ang, length):
    """Point `length` from `base` at angle `ang` (0 = straight down, positive = to the right)."""
    a = math.radians(ang)
    return T(base[0] + length * math.sin(a), base[1] + length * math.cos(a))


# ---- characters -------------------------------------------------------------

ARMS = {"out": (-85, 85), "up": (-150, 150), "down": (-25, 25), "hips": (-40, 40)}


@stable
def stick(p, x, y, s=1.0, face="smile", arms="out", legs=0.0, lean=0.0, width=6, color=BLACK,
          walk=None, head_dy=0.0):
    """Stick figure with feet at (x, y). `arms` is a preset or (left, right) angles;
    `walk` is a walk-cycle phase (None = standing). Returns head centre and hand points."""
    T = xf(x, y, s, lean)
    la, ra = ARMS.get(arms, arms) if isinstance(arms, str) else arms
    hip, neck = (0, -90), (0, -222)
    head = T(0, -250 + head_dy)
    p.loop(head[0], head[1], 30 * s, 28 * s, width, color, n=12)
    hx, hy = head
    for ex in (-10, 8):
        p.brush([(hx + ex * s, hy - 4 * s)], max(3, width - 1), color, 0.2)
    if face == "smile":
        p.brush([(hx - 12 * s, hy + 10 * s), (hx, hy + 15 * s), (hx + 12 * s, hy + 9 * s)], 4, color, 0.5)
    elif face == "flat":
        p.brush([(hx - 10 * s, hy + 12 * s), (hx + 10 * s, hy + 11 * s)], 4, color, 0.5)
    elif face == "angry":
        p.brush([(hx - 12 * s, hy + 15 * s), (hx, hy + 9 * s), (hx + 12 * s, hy + 15 * s)], 4, color, 0.5)
        p.brush([(hx - 18 * s, hy - 16 * s), (hx - 4 * s, hy - 10 * s)], 4, color, 0.3)
        p.brush([(hx + 16 * s, hy - 16 * s), (hx + 3 * s, hy - 10 * s)], 4, color, 0.3)
    elif face == "laugh":
        p.brush([(hx - 14 * s, hy + 6 * s), (hx, hy + 20 * s), (hx + 14 * s, hy + 6 * s), (hx - 14 * s, hy + 6 * s)], 4, color, 0.5)
    elif face == "o":
        p.loop(hx, hy + 13 * s, 5 * s, 6 * s, 3)
    elif face == "chew":
        p.brush([(hx - 10 * s, hy + 12 * s), (hx - 4 * s, hy + 16 * s), (hx + 2 * s, hy + 11 * s), (hx + 10 * s, hy + 15 * s)], 4, color, 0.5)
    p.brush([T(*neck), T(p.rng.uniform(-5, 5), -156), T(*hip)], width, color)
    sh = (0, -182)
    hands = []
    for ang in (la, ra):
        if ang is None:
            hands.append(None)
            continue
        hand = limb(T, sh, ang, 68)
        p.brush([T(*sh), hand], width, color)
        hands.append(hand)
    if walk is None:
        spread = 18 + legs
        l_ang, r_ang = -spread, spread
    else:
        sw = 28 * math.sin(2 * math.pi * walk)
        l_ang, r_ang = -sw, sw
    for ang in (l_ang, r_ang):
        knee = limb(T, hip, ang * 0.6, 48)
        p.brush([T(*hip), knee, limb(T, hip, ang, 92)], width, color)
    return head, hands


@stable
def drop(p, x, y, s=1.0, face="smile", arms=None, legs=True, walk=None, rot=0.0, squash=1.0, mouth=0.0,
         color=YELLOW):
    """The agüita: a freehand yellow drop with a face. (x, y) = belly centre.
    `arms` is None or (left, right) angles; `mouth` opens the singing mouth 0..1."""
    T = xf(x, y, s, rot)
    r = 55
    sx, sy = 1 / squash ** 0.5, squash
    pts = [T(p.rng.uniform(-3, 3), -r * 2.1 * sy)]
    for i in range(11):
        a = -0.35 * math.pi + (1.7 * math.pi) * i / 10
        pts.append(T(r * math.cos(a) * sx, r * math.sin(a) * sy))
    pts.append((pts[0][0] + 2, pts[0][1] + 3))
    pts.append((pts[1][0] - 3, pts[1][1] - 2))
    # opaque white underneath, so the bucket stays inside even when the drop walks over lines
    cx, cy = T(0, -20 * sy)
    ImageDraw.Draw(p.img).polygon([(cx + (px - cx) * 0.94, cy + (py - cy) * 0.94) for px, py in pts[:12]], fill=WHITE)
    p.brush(pts, 6, shake=0.7)
    p.fill(*T(0, 10 * sy), color)
    for ex in (-18, 14):
        if face == "sleep":
            p.brush([T(ex - 8, -12), T(ex + 8, -10)], 4)
        else:
            p.brush([T(ex, -12)], 8, BLACK, 0.2)
    if face == "smile":
        p.brush([T(-22, 12), T(0, 26), T(22, 10)], 5, BLACK, 0.6)
    elif face == "sing":
        m = 4 + 12 * mouth
        mx, my = T(0, 20)
        p.loop(mx, my, 9 * s, m * s, 5, n=10)
    elif face == "hot":
        p.brush([T(-20, 20), T(-8, 14), T(4, 22), T(18, 14)], 5)
    elif face == "sleep":
        p.brush([T(-10, 18), T(10, 18)], 4)
    elif face == "ouch":
        p.brush([T(-26, -24), T(-10, -16)], 4)
        p.brush([T(22, -24), T(6, -16)], 4)
        mx, my = T(0, 20)
        p.loop(mx, my, 10 * s, 12 * s, 5, n=10)
    if arms:
        la, ra = arms
        p.brush([T(-r * sx, 0), limb(T, (-r * sx, 0), la, 50)], 5)
        p.brush([T(r * sx, 0), limb(T, (r * sx, 0), ra, 50)], 5)
    if legs:
        sw = 0 if walk is None else 30 * math.sin(2 * math.pi * walk)
        for side, a in ((-20, -10 - sw), (20, 10 + sw)):
            base = (side, r * sy - 4)
            foot = limb(T, base, a, 36)
            p.brush([T(*base), foot, (foot[0] + side * 0.8 * s, foot[1] + 2)], 5)


@stable
def toilet(p, x, y, s=1.0):
    """Paint-shape toilet: tank rectangle, perfect-ellipse rim, chord bowl, box base. (x, y) = floor centre."""
    d = ImageDraw.Draw(p.img)
    tw, th = 60 * s, 90 * s
    p.rect((int(x + 40 * s), int(y - 230 * s), int(x + 40 * s + tw), int(y - 230 * s + th)), width=3, fill=WHITE)
    p.rect((int(x - 20 * s), int(y - 60 * s), int(x + 50 * s), int(y)), width=3, fill=WHITE)
    d.chord((int(x - 90 * s), int(y - 190 * s), int(x + 70 * s), int(y - 40 * s)), 0, 180, outline=BLACK, width=3, fill=WHITE)
    p.ellipse((int(x - 90 * s), int(y - 135 * s), int(x + 70 * s), int(y - 95 * s)), width=3, fill=WHITE)
    p.ellipse((int(x - 75 * s), int(y - 128 * s), int(x + 55 * s), int(y - 102 * s)), width=3, fill=YELLOW)


@stable
def beer(p, x, y, s=1.0, level=1.0):
    """A pint drawn with the rectangle tool, freehand handle and foam."""
    x, y = int(x), int(y)
    w, h = int(34 * s), int(60 * s)
    p.rect((x, y, x + w, y + h), width=3, fill=WHITE)
    if level > 0:
        top = int(y + h - (h - 3) * level)
        p.rect((x + 2, top, x + w - 2, y + h - 2), width=0, fill=YELLOW)
    p.brush([(x + w, y + 12 * s), (x + w + 16 * s, y + 18 * s), (x + w + 15 * s, y + 42 * s), (x + w, y + 46 * s)], 4)
    if level > 0.9:
        p.brush([(x - 3, y), (x + 5, y - 10 * s), (x + 14 * s, y - 6 * s), (x + 22 * s, y - 12 * s), (x + w + 2, y - 2)], 4)


@stable
def cow(p, x, y, s=1.0, head=0.0):
    """`head` 0 = looking ahead, 1 = head down drinking."""
    p.loop(x, y, 60 * s, 34 * s, 6)
    hx, hy = lerp(x - 75 * s, x - 80 * s, head), lerp(y - 25 * s, y + 30 * s, head)
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


@stable
def fish(p, x, y, s=1.0, color=ORANGE, flip=False, tail=0.0):
    f = -1 if flip else 1
    p.loop(x, y, 40 * s, 22 * s, 5, n=12, closed=True)
    w = 20 * tail
    p.brush([(x - f * 38 * s, y), (x - f * 70 * s, y - 20 * s + w), (x - f * 66 * s, y + 22 * s + w), (x - f * 38 * s, y + 2 * s)], 5)
    p.brush([(x + f * 20 * s, y - 6 * s)], 6, BLACK, 0.2)
    p.fill(x, y + 4 * s, color)


@stable
def house(p, x, y, w, h, label=None, fill=WHITE, upto=None):
    p.block_arrow(x, y, w, h, fill=fill)
    if label:
        p.hand_lines(label, x + w * 0.28, y + h * 0.5, 26)


@stable
def building(p, x0, x1, top, bottom=540, fill=LGRAY, windows=6):
    p.rect((x0, top, x1, bottom), width=3, fill=fill)
    for i in range(windows):
        wx = int(p.rng.uniform(x0 + 8, x1 - 30))
        wy = int(p.rng.uniform(top + 10, bottom - 40))
        ww, wh = int(p.rng.choice([14, 18, 26, 40])), int(p.rng.choice([10, 18, 26]))
        p.rect((wx, wy, min(wx + ww, x1 - 6), wy + wh), width=3, fill=WHITE)


def city(p, x0=0, x1=960, top=260):
    """A skyline. Building layout uses its own RNG so it doesn't move between boils."""
    lay = random.Random(x0 * 7 + top)
    xs = list(range(x0, x1 + 1, 120))
    for a, b in zip(xs, xs[1:]):
        building(p, a + lay.randint(0, 15), b - lay.randint(5, 20), top + lay.randint(-60, 80))


@stable
def cloud(p, x, y, w=260, color=WHITE, pee=True, face=False, dots=1800):
    lay = random.Random(int(w))
    for i in range(7):
        p.spray(x + lay.uniform(-w / 2, w / 2), y + lay.uniform(-25, 25), 55, color, dots)
    if pee:
        for i in range(2):
            p.spray(x + lay.uniform(-w / 4, w / 4), y + lay.uniform(-10, 10), 30, YELLOW, 300, wander=6)
    if face:
        p.brush([(x - 22, y - 8)], 9, BLACK, 0.2)
        p.brush([(x + 18, y - 8)], 9, BLACK, 0.2)
        p.brush([(x - 20, y + 14), (x, y + 24), (x + 20, y + 12)], 5, BLACK, 0.5)


def rain(p, T, x0, x1, y0, y1, n=40, color=YELLOW, density=1.0, speed=700):
    """Falling streaks. Each has a fixed lane and phase, so they fall instead of flickering."""
    lay = random.Random(n + x0)
    for i in range(int(n * density)):
        x = lay.uniform(x0, x1)
        ph0 = lay.random()
        y = y0 + ((ph0 + T * speed / (y1 - y0)) % 1.0) * (y1 - y0)
        p.brush([(x, y), (x - 6, y + 24)], 4, color, shake=0.3)


@stable
def note(p, x, y, s=1.0, color=BLACK):
    p.ellipse((int(x), int(y), int(x + 30 * s), int(y + 22 * s)), width=3, fill=color)
    p.brush([(x + 28 * s, y + 10 * s), (x + 30 * s, y - 70 * s), (x + 55 * s, y - 50 * s)], 5, color)


@stable
def heart(p, x, y, s=1.0, color=RED):
    pts = [(x, y + 20 * s), (x - 25 * s, y - 5 * s), (x - 12 * s, y - 20 * s), (x, y - 8 * s),
           (x + 12 * s, y - 20 * s), (x + 25 * s, y - 5 * s), (x, y + 20 * s)]
    p.brush(pts, 5, color)
    p.fill(x, y, color)


@stable
def splash(p, x, y, u, s=1.0, color=YELLOW):
    """A ring of droplets flying out and falling back, u = 0..1 through the splash."""
    if not 0 < u < 1:
        return
    for k in range(7):
        a = math.pi * (0.1 + 0.8 * k / 6)
        d = 60 * s * u
        px, py = x - d * math.cos(a), y - d * math.sin(a) * 1.3 + 90 * s * u * u
        p.brush([(px, py)], 8 * s, color, 0.3)
