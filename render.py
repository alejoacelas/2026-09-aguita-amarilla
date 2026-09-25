"""Render the animation frame by frame and cut it to the song.

    uv run python render.py              # every frame, then out/aguita.mp4
    uv run python render.py sheet        # out/contact.png: three frames from every shot
    uv run python render.py strip pipes  # out/work/strip-pipes.png: eight frames across one shot
    uv run python render.py clip 72 90   # out/work/clip.mp4: just that stretch, with sound
"""

import bisect
import math
import subprocess
import sys
import zlib
from multiprocessing import Pool
from pathlib import Path

from PIL import Image, ImageDraw

from paint import Paint, W, H
from shots import END, SHOTS, TIMELINE

FPS = 12          # choppy on purpose
BOIL_EVERY = 2    # frames per boil step: lines get redrawn 6 times a second
BOILS = 3         # redrawn versions to cycle through
OUT = Path("out")
FRAMES = OUT / "anim"
SONG = Path("reference/song.mp3")
STARTS = [t for t, _, _ in TIMELINE]


class Ctx:
    def __init__(self, T, start, end, args):
        self.T, self.t, self.dur, self.a = T, T - start, end - start, args


_bg = {}


def background(shot, boil):
    key = (shot.name, boil)
    if key not in _bg:
        if len(_bg) > 12:
            _bg.clear()
        p = Paint(zlib.crc32(shot.name.encode()), shot.bgcolor, shot.w, shot.h, boil)
        if shot.bgfn:
            shot.bgfn(p)
        _bg[key] = p.img
    return _bg[key]


def frame(i):
    T = i / FPS
    k = max(0, bisect.bisect_right(STARTS, T) - 1)
    start, name, args = TIMELINE[k]
    end = STARTS[k + 1] if k + 1 < len(STARTS) else END
    shot = SHOTS[name]
    boil = (i // BOIL_EVERY) % BOILS
    p = Paint(zlib.crc32(name.encode()) + 1, w=shot.w, h=shot.h, boil=boil, img=background(shot, boil).copy())
    cam = shot.fn(p, Ctx(T, start, end, args))
    cx, cy = cam if cam else (0, 0)
    return p.img.crop((int(cx), int(cy), int(cx) + W, int(cy) + H))


def save(i):
    frame(i).save(FRAMES / f"{i:05d}.png", compress_level=1)
    return i


def render(first, last):
    FRAMES.mkdir(parents=True, exist_ok=True)
    idx = list(range(first, last))
    with Pool() as pool:
        for n, _ in enumerate(pool.imap(save, idx, chunksize=12)):
            if n % 240 == 0:
                print(f"frame {n}/{len(idx)}", flush=True)


def encode(first, last, out):
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-start_number", str(first),
        "-i", str(FRAMES / "%05d.png"), "-ss", f"{first / FPS:.3f}", "-i", str(SONG),
        "-frames:v", str(2 * (last - first)), "-vf", "fps=24,format=yuv420p", "-c:v", "libx264", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k", "-shortest", str(out),
    ], check=True)


def grid(frames, labels, cols, out):
    tw, th = 320, 180
    rows = math.ceil(len(frames) / cols)
    sheet = Image.new("RGB", (cols * tw, rows * (th + 18)), (60, 60, 60))
    d = ImageDraw.Draw(sheet)
    for n, (im, lab) in enumerate(zip(frames, labels)):
        x, y = (n % cols) * tw, (n // cols) * (th + 18)
        sheet.paste(im.resize((tw - 4, th - 4)), (x + 2, y + 2))
        d.text((x + 4, y + th), lab, fill=(255, 255, 255))
    sheet.save(out)


def shot_frames(name, n):
    for k, (start, nm, _) in enumerate(TIMELINE):
        if nm == name:
            end = STARTS[k + 1] if k + 1 < len(STARTS) else END
            return [int((start + (end - start) * (j + 0.5) / n) * FPS) for j in range(n)]
    raise SystemExit(f"no shot {name}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    total = int(END * FPS)
    if cmd == "sheet":
        idx = []
        for k, (start, _, _) in enumerate(TIMELINE):
            end = STARTS[k + 1] if k + 1 < len(STARTS) else END
            idx += [int((start + (end - start) * f) * FPS) for f in (0.2, 0.55, 0.9)]
        with Pool() as pool:
            ims = pool.map(frame, idx)
        grid(ims, [f"{i / FPS:.1f}s" for i in idx], 6, OUT / "contact.png")
    elif cmd == "strip":
        idx = shot_frames(sys.argv[2], 8)
        with Pool() as pool:
            ims = pool.map(frame, idx)
        grid(ims, [f"{i / FPS:.1f}s" for i in idx], 4, OUT / "work" / f"strip-{sys.argv[2]}.png")
    elif cmd == "clip":
        a, b = int(float(sys.argv[2]) * FPS), int(float(sys.argv[3]) * FPS)
        render(a, b)
        encode(a, b, OUT / "work" / "clip.mp4")
    else:
        render(0, total)
        encode(0, total, OUT / "aguita.mp4")
