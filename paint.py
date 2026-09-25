"""A tiny fake MS Paint: mouse-shaky brush, shape tools, bucket fill, spray can, text.

Everything random comes from a seeded RNG so renders are repeatable. `part(key)`
reseeds it per element, so one element's wobble doesn't depend on what was drawn
before it, and `boil` picks which of the redrawn versions of a frame we're on.
"""

import math
import random
import zlib

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 960, 540
SS = 3  # supersampling for the brush, so edges get a grey fringe the bucket can't reach

# Paint's default swatches
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (127, 127, 127)
LGRAY = (195, 195, 195)
RED = (237, 28, 36)
ORANGE = (255, 127, 39)
YELLOW = (255, 242, 0)
GREEN = (34, 177, 76)
LIME = (181, 230, 29)
TURQ = (153, 217, 234)
BLUE = (63, 72, 204)
DBLUE = (0, 162, 232)
BROWN = (185, 122, 87)
PINK = (255, 174, 201)
PURPLE = (163, 73, 164)
DRED = (136, 0, 21)
TAN = (239, 228, 176)

TYPED_FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"


# Single-stroke capitals on a 0..1 box (x right, y down). Each glyph is a list of strokes.
GLYPHS = {
    "A": [[(0, 1), (0.5, 0), (1, 1)], [(0.2, 0.6), (0.8, 0.6)]],
    "B": [[(0, 1), (0, 0), (0.7, 0.05), (0.8, 0.25), (0.6, 0.48), (0, 0.5)],
          [(0.6, 0.48), (0.95, 0.7), (0.8, 0.95), (0, 1)]],
    "C": [[(0.95, 0.15), (0.6, 0), (0.2, 0.1), (0, 0.5), (0.2, 0.9), (0.6, 1), (0.95, 0.85)]],
    "D": [[(0, 0), (0, 1), (0.6, 0.95), (0.95, 0.5), (0.6, 0.05), (0, 0)]],
    "E": [[(0.9, 0), (0, 0), (0, 1), (0.9, 1)], [(0, 0.5), (0.7, 0.5)]],
    "F": [[(0.9, 0), (0, 0), (0, 1)], [(0, 0.5), (0.7, 0.5)]],
    "G": [[(0.95, 0.15), (0.6, 0), (0.2, 0.1), (0, 0.5), (0.2, 0.9), (0.6, 1), (0.95, 0.8), (0.95, 0.55), (0.55, 0.55)]],
    "H": [[(0, 0), (0, 1)], [(1, 0), (1, 1)], [(0, 0.5), (1, 0.5)]],
    "I": [[(0.5, 0), (0.5, 1)]],
    "J": [[(0.8, 0), (0.8, 0.8), (0.5, 1), (0.1, 0.85)]],
    "K": [[(0, 0), (0, 1)], [(0.9, 0), (0, 0.55), (0.95, 1)]],
    "L": [[(0, 0), (0, 1), (0.85, 1)]],
    "M": [[(0, 1), (0.05, 0), (0.5, 0.6), (0.95, 0), (1, 1)]],
    "N": [[(0, 1), (0, 0), (1, 1), (1, 0)]],
    "Ñ": [[(0, 1), (0, 0.2), (1, 1), (1, 0.2)], [(0.1, -0.1), (0.35, -0.2), (0.65, -0.05), (0.9, -0.15)]],
    "O": [[(0.5, 0), (0.1, 0.15), (0, 0.55), (0.25, 0.95), (0.7, 0.95), (1, 0.5), (0.8, 0.1), (0.45, 0.02)]],
    "P": [[(0, 1), (0, 0), (0.75, 0.05), (0.9, 0.3), (0.7, 0.5), (0, 0.5)]],
    "Q": [[(0.5, 0), (0.1, 0.15), (0, 0.55), (0.25, 0.95), (0.7, 0.95), (1, 0.5), (0.8, 0.1), (0.45, 0.02)],
          [(0.6, 0.7), (1, 1.05)]],
    "R": [[(0, 1), (0, 0), (0.75, 0.05), (0.9, 0.3), (0.7, 0.5), (0, 0.5), (0.95, 1)]],
    "S": [[(0.9, 0.1), (0.5, 0), (0.1, 0.15), (0.2, 0.45), (0.8, 0.55), (0.95, 0.85), (0.5, 1), (0.05, 0.9)]],
    "T": [[(0, 0), (1, 0)], [(0.5, 0), (0.5, 1)]],
    "U": [[(0, 0), (0, 0.75), (0.3, 1), (0.7, 1), (1, 0.75), (1, 0)]],
    "V": [[(0, 0), (0.5, 1), (1, 0)]],
    "W": [[(0, 0), (0.25, 1), (0.5, 0.35), (0.75, 1), (1, 0)]],
    "X": [[(0, 0), (1, 1)], [(1, 0), (0, 1)]],
    "Y": [[(0, 0), (0.5, 0.5), (1, 0)], [(0.5, 0.5), (0.5, 1)]],
    "Z": [[(0, 0), (1, 0), (0, 1), (1, 1)]],
    "0": [[(0.5, 0), (0.05, 0.3), (0.1, 0.8), (0.5, 1), (0.9, 0.75), (0.95, 0.25), (0.5, 0)]],
    "1": [[(0.2, 0.25), (0.6, 0), (0.6, 1)]],
    "2": [[(0.05, 0.2), (0.4, 0), (0.85, 0.15), (0.8, 0.45), (0, 1), (1, 1)]],
    "3": [[(0.05, 0.1), (0.7, 0), (0.85, 0.25), (0.4, 0.48), (0.9, 0.7), (0.7, 1), (0.05, 0.9)]],
    "4": [[(0.7, 1), (0.7, 0), (0, 0.7), (1, 0.7)]],
    "5": [[(0.9, 0), (0.1, 0), (0.05, 0.45), (0.7, 0.4), (0.95, 0.7), (0.6, 1), (0.05, 0.9)]],
    "6": [[(0.8, 0), (0.2, 0.3), (0.05, 0.75), (0.4, 1), (0.9, 0.8), (0.7, 0.5), (0.1, 0.6)]],
    "7": [[(0, 0), (1, 0), (0.35, 1)]],
    "8": [[(0.5, 0.48), (0.1, 0.25), (0.5, 0), (0.9, 0.25), (0.5, 0.48), (0.05, 0.75), (0.5, 1), (0.95, 0.75), (0.5, 0.48)]],
    "9": [[(0.9, 0.4), (0.2, 0.45), (0.1, 0.15), (0.6, 0), (0.9, 0.3), (0.8, 1)]],
    "!": [[(0.5, 0), (0.5, 0.7)], [(0.5, 0.92), (0.5, 0.97)]],
    "¡": [[(0.5, 0.3), (0.5, 1)], [(0.5, 0.03), (0.5, 0.08)]],
    "?": [[(0.1, 0.2), (0.5, 0), (0.9, 0.2), (0.5, 0.5), (0.5, 0.7)], [(0.5, 0.92), (0.5, 0.97)]],
    "¿": [[(0.9, 0.8), (0.5, 1), (0.1, 0.8), (0.5, 0.5), (0.5, 0.3)], [(0.5, 0.03), (0.5, 0.08)]],
    ".": [[(0.5, 0.92), (0.5, 0.97)]],
    ",": [[(0.55, 0.85), (0.4, 1.1)]],
    "-": [[(0.1, 0.5), (0.9, 0.5)]],
    "=": [[(0.1, 0.35), (0.9, 0.35)], [(0.1, 0.65), (0.9, 0.65)]],
    "+": [[(0.1, 0.5), (0.9, 0.5)], [(0.5, 0.15), (0.5, 0.85)]],
    ":": [[(0.5, 0.3), (0.5, 0.35)], [(0.5, 0.85), (0.5, 0.9)]],
    "°": [[(0.4, 0), (0.2, 0.12), (0.4, 0.28), (0.6, 0.12), (0.4, 0)]],
    "'": [[(0.5, 0), (0.45, 0.25)]],
    "/": [[(0.9, 0), (0.1, 1)]],
}
ACCENTS = {"Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U", "Ü": "U"}


class Paint:
    def __init__(self, seed, bg=WHITE, w=W, h=H, boil=0, img=None):
        self.seed, self.boil, self.w, self.h = seed, boil, w, h
        self.rng = random.Random(f"{seed}:{boil}")
        self.img = img if img is not None else Image.new("RGB", (w, h), bg)
        self.calls = {}

    def part(self, key):
        """Reseed from a name, so this element keeps its shape within a boil step."""
        n = self.calls.get(key, 0)
        self.calls[key] = n + 1
        self.rng = random.Random(zlib.crc32(f"{self.seed}:{self.boil}:{key}:{n}".encode()))

    # ---- the brush ----------------------------------------------------------

    def _mouse_path(self, pts, shake=1.0, closed=False):
        """Resample control points into a dense path that wobbles like a mouse."""
        r = self.rng
        pts = [(x + r.gauss(0, 1.5 * shake), y + r.gauss(0, 1.5 * shake)) for x, y in pts]
        if closed:
            pts = pts + [pts[0]]
        if len(pts) == 1:
            pts = pts * 2
        dense = []
        # piecewise linear with a little Catmull-Rom rounding, like a hand dragging
        ext = [pts[0]] + pts + [pts[-1]]
        for i in range(1, len(ext) - 2):
            p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
            seg = math.dist(p1, p2)
            n = max(2, int(seg / 2))
            for k in range(n):
                t = k / n
                t2, t3 = t * t, t * t * t
                x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                           + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
                y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                           + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
                dense.append((x, y))
        dense.append(pts[-1])
        # low-frequency drift plus pixel jitter, perpendicular-ish in any direction
        out = []
        dx = dy = 0.0
        for x, y in dense:
            dx = dx * 0.93 + r.gauss(0, 0.55 * shake)
            dy = dy * 0.93 + r.gauss(0, 0.55 * shake)
            out.append((x + dx + r.gauss(0, 0.35 * shake), y + dy + r.gauss(0, 0.35 * shake)))
        # overshoot the end a bit, the mouse button lets go late
        if len(out) >= 3 and not closed and r.random() < 0.6:
            (ax, ay), (bx, by) = out[-3], out[-1]
            L = math.dist((ax, ay), (bx, by)) or 1
            k = r.uniform(2, 7) / L
            out.append((bx + (bx - ax) * k, by + (by - ay) * k))
        return out

    def brush(self, pts, width=6, color=BLACK, shake=1.0, closed=False, upto=1.0):
        """Drag the brush along `pts`. `upto` < 1 draws only the first part, for write-on."""
        if upto <= 0:
            return
        path = self._mouse_path(pts, shake, closed)
        if upto < 1:
            seg = [math.dist(a, b) for a, b in zip(path, path[1:])]
            goal, acc, keep = sum(seg) * upto, 0.0, 1
            for L in seg:
                if acc + L > goal:
                    break
                acc += L
                keep += 1
            path = path[:max(1, keep)]
        pad = width + 3
        x0 = max(0, int(min(x for x, _ in path) - pad))
        y0 = max(0, int(min(y for _, y in path) - pad))
        x1 = min(self.w, int(max(x for x, _ in path) + pad) + 1)
        y1 = min(self.h, int(max(y for _, y in path) + pad) + 1)
        if x1 <= x0 or y1 <= y0:
            return
        big = Image.new("L", ((x1 - x0) * SS, (y1 - y0) * SS), 0)
        d = ImageDraw.Draw(big)
        rad = width * SS / 2
        sp = [((x - x0) * SS, (y - y0) * SS) for x, y in path]
        if len(sp) > 1:
            d.line(sp, fill=255, width=int(width * SS), joint="curve")
        for x, y in sp[:: max(1, len(sp) // 400)] + [sp[0], sp[-1]]:
            d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=255)
        mask = big.resize((x1 - x0, y1 - y0), Image.BILINEAR)
        self.img.paste(color, (x0, y0, x1, y1), mask)

    def loop(self, cx, cy, rx, ry, width=6, color=BLACK, shake=1.0, n=14, closed=False):
        """A freehand ellipse that doesn't quite close (unless it has to hold a fill)."""
        r = self.rng
        a0 = r.uniform(0, 2 * math.pi)
        extra = r.uniform(0.05, 0.35) if closed else r.uniform(-0.25, 0.35)
        pts = []
        for i in range(n + 1):
            a = a0 + (2 * math.pi + extra) * i / n
            k = 1 + r.gauss(0, 0.06)
            pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
        self.brush(pts, width, color, shake)

    def arrow(self, x0, y0, x1, y1, width=5, color=BLACK, bend=0.0):
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        nx, ny = -(y1 - y0), x1 - x0
        mid = (mx + nx * bend, my + ny * bend)
        self.brush([(x0, y0), mid, (x1, y1)], width, color)
        ang = math.atan2(y1 - mid[1], x1 - mid[0])
        L = 18 + self.rng.uniform(-4, 6)
        for s in (-1, 1):
            a = ang + math.pi + s * self.rng.uniform(0.45, 0.7)
            self.brush([(x1, y1), (x1 + L * math.cos(a), y1 + L * math.sin(a))], width, color)

    # ---- shape tools (perfect, aliased) ------------------------------------

    def ellipse(self, box, outline=BLACK, width=3, fill=None):
        ImageDraw.Draw(self.img).ellipse(box, outline=outline, width=width, fill=fill)

    def rect(self, box, outline=BLACK, width=3, fill=None):
        ImageDraw.Draw(self.img).rectangle(box, outline=outline, width=width, fill=fill)

    def polygon(self, pts, outline=BLACK, width=3, fill=None):
        d = ImageDraw.Draw(self.img)
        if fill:
            d.polygon(pts, fill=fill)
        d.line(list(pts) + [pts[0]], fill=outline, width=width, joint=None)

    def line(self, p0, p1, color=BLACK, width=3):
        ImageDraw.Draw(self.img).line([p0, p1], fill=color, width=width)

    def block_arrow(self, x, y, w, h, fill=None, up=True):
        """Paint's 'up arrow' shape: a triangle roof on a box."""
        bw = w * 0.62
        head = h * 0.42
        pts = [(x + w / 2, y), (x + w, y + head), (x + w / 2 + bw / 2, y + head),
               (x + w / 2 + bw / 2, y + h), (x + w / 2 - bw / 2, y + h), (x + w / 2 - bw / 2, y + head), (x, y + head)]
        if not up:
            pts = [(px, 2 * y + h - py) for px, py in pts]
        pts = [(int(px), int(py)) for px, py in pts]
        self.polygon(pts, width=3, fill=fill)

    # ---- bucket and spray --------------------------------------------------

    def fill(self, x, y, color, tol=40):
        """Pixel flood fill that stops at anything not close to the clicked colour."""
        W, H = self.w, self.h
        x, y = int(x), int(y)
        if not (0 <= x < W and 0 <= y < H):
            return
        a = np.asarray(self.img).astype(np.int16)
        target = a[y, x].copy()
        same = np.abs(a - target).sum(axis=2) <= tol
        seen = np.zeros((H, W), bool)
        stack = [(x, y)]
        while stack:
            px, py = stack.pop()
            if px < 0 or py < 0 or px >= W or py >= H or seen[py, px] or not same[py, px]:
                continue
            # scanline
            l = px
            while l > 0 and same[py, l - 1] and not seen[py, l - 1]:
                l -= 1
            rr = px
            while rr < W - 1 and same[py, rr + 1] and not seen[py, rr + 1]:
                rr += 1
            seen[py, l:rr + 1] = True
            for ny in (py - 1, py + 1):
                if 0 <= ny < H:
                    row = same[ny, l:rr + 1] & ~seen[ny, l:rr + 1]
                    xs = np.nonzero(row)[0]
                    prev = -2
                    for xi in xs:
                        if xi != prev + 1:
                            stack.append((l + xi, ny))
                        prev = xi
        out = np.asarray(self.img).copy()
        out[seen] = color
        self.img = Image.fromarray(out)

    def spray(self, cx, cy, radius, color, dots=400, wander=0.0):
        """Paint's airbrush: uniform speckles in a disc, dragged around a bit."""
        a = np.asarray(self.img).copy()
        W, H = self.w, self.h
        r = self.rng
        x, y = cx, cy
        for i in range(int(dots)):
            if wander and i % 25 == 0:
                x += r.uniform(-wander, wander)
                y += r.uniform(-wander * 0.5, wander * 0.5)
            ang = r.uniform(0, 2 * math.pi)
            d = radius * math.sqrt(r.random())
            px, py = int(x + d * math.cos(ang)), int(y + d * math.sin(ang))
            if 0 <= px < W and 0 <= py < H:
                a[py, px] = color
        self.img = Image.fromarray(a)

    def spray_path(self, pts, radius, color, dots_per_step=40):
        for x, y in pts:
            self.spray(x, y, radius, color, dots_per_step)

    # ---- text --------------------------------------------------------------

    def hand(self, text, x, y, size=36, width=4, color=BLACK, spacing=0.35, slope=0.0, upto=None):
        """Shaky handwritten capitals, the first `upto` characters. Returns the x where the text ends."""
        r = self.rng
        cx = x
        shown = len(text) if upto is None else upto
        for i, ch in enumerate(text.upper()):
            if i >= shown:
                break
            if ch == " ":
                cx += size * 0.6
                continue
            if ch == "\n":
                continue
            base = ACCENTS.get(ch, ch)
            strokes = GLYPHS.get(base)
            if strokes is None:
                cx += size * 0.6
                continue
            gw = size * (0.25 if base in "I!¡.,:'" else r.uniform(0.62, 0.8))
            gh = size * r.uniform(0.9, 1.12)
            gy = y + r.gauss(0, size * 0.05) + slope * (cx - x)
            for s in strokes:
                pts = [(cx + px * gw, gy + py * gh) for px, py in s]
                self.brush(pts, width, color, shake=0.7)
            if ch in "ÁÉÍÓÚ":
                self.brush([(cx + gw * 0.45, gy - gh * 0.12), (cx + gw * 0.7, gy - gh * 0.3)], width, color, 0.4)
            if ch == "Ü":
                for px in (0.3, 0.7):
                    self.brush([(cx + gw * px, gy - gh * 0.2)], width, color, 0.2)
            cx += gw + size * spacing * r.uniform(0.7, 1.3)
        return cx

    def hand_lines(self, lines, x, y, size=36, lh=1.35, **kw):
        for i, ln in enumerate(lines):
            self.hand(ln, x, y + i * size * lh, size, **kw)

    def typed(self, text, x, y, size=22, color=BLACK, font=TYPED_FONT):
        """Paint's text tool: a plain system font, no antialiasing."""
        f = ImageFont.truetype(font, size)
        d = ImageDraw.Draw(self.img)
        d.fontmode = "1"
        d.multiline_text((x, y), text, fill=color, font=f, spacing=2)

    def bubble(self, x, y, tail, lines, size=30, width=4, upto=None):
        """Freehand speech bubble centred on (x, y), sized to its text, tail pointing at `tail`."""
        tw = max(len(ln) for ln in lines) * size * 0.95
        w, h = tw + size * 1.6, len(lines) * size * 1.4 + size * 1.2
        cx, cy = x, y
        self.loop(cx, cy, w / 2, h / 2, width, n=16)
        if tail:
            tx, ty = tail
            a = math.atan2((ty - cy) / h, (tx - cx) / w)
            b0 = (cx + w / 2 * 0.97 * math.cos(a - 0.3), cy + h / 2 * 0.97 * math.sin(a - 0.3))
            b1 = (cx + w / 2 * 0.97 * math.cos(a + 0.3), cy + h / 2 * 0.97 * math.sin(a + 0.3))
            self.brush([b0, tail, b1], width)
        n = len(lines)
        left = sum(map(len, lines)) if upto is None else upto
        for i, ln in enumerate(lines):
            est = len(ln) * size * 0.92
            self.hand(ln, cx - est / 2, cy - n * size * 0.68 + i * size * 1.35, size, width=width - 1,
                      upto=max(0, min(len(ln), left)))
            left -= len(ln)

    def thought(self, x, y, tail, lines, size=30, width=4, upto=None):
        """Cloud-ish thought bubble: a loop plus a trail of little circles."""
        self.bubble(x, y, None, lines, size, width, upto)
        tx, ty = tail
        for k, rr in ((0.55, 16), (0.75, 11), (0.9, 7)):
            self.loop(x + (tx - x) * k, y + (ty - y) * k, rr, rr * 0.8, width - 1, n=8)

    def save(self, path):
        self.img.save(path)
