"""Render every drawing once, build a contact sheet, and cut the video to the song.

    uv run python render.py            # everything
    uv run python render.py pee dog    # just these drawings (plus the sheet)
"""

import subprocess
import sys
import zlib
from pathlib import Path

from PIL import Image, ImageDraw

from paint import Paint
from scenes import SCENES

OUT = Path("out")
FRAMES = OUT / "frames"
SONG = Path("reference/song.mp3")
END = 338.83

# (start in seconds, drawing). Times come from whisper word timestamps; 3:04-3:32 uses
# re-transcribed clips because the full pass drifted ~5 s early there.
TIMELINE = [
    (0.0, "bar_please"),
    (18.9, "bar_dame"),
    (24.5, "title"),
    (30.1, "beers40"),
    (37.5, "expel"),
    (45.4, "stairs"),
    (50.8, "pee"),
    (52.8, "pee_laugh"),
    (60.2, "comes_out"),
    (64.7, "warm"),
    (72.0, "flush_down"),
    (74.8, "pipe"),
    (76.3, "pipe_casa"),
    (81.2, "pipe_familia"),
    (85.7, "pipe_trabajo"),
    (89.7, "river"),
    (93.6, "shepherd"),
    (98.3, "cows"),
    (104.2, "fields"),
    (109.7, "drop_chorus"),
    (113.2, "drop_chorus_hola"),
    (117.0, "sea"),
    (122.6, "fishes"),
    (126.3, "squid"),
    (129.9, "jelly"),
    (133.5, "hake"),
    (135.4, "you_eat"),
    (140.7, "drop_sing"),
    (146.1, "drop_la1"),
    (150.8, "drop_la2"),
    (154.4, "drop_la3"),
    (158.7, "sun"),
    (167.1, "hundred"),
    (172.3, "up"),
    (177.6, "sky_trip"),
    (179.5, "city_arrive"),
    (181.2, "rain_start"),
    (185.0, "rain_chorus"),
    (190.5, "streets"),
    (194.7, "dad"),
    (198.0, "mom"),
    (200.8, "mom_aguita"),
    (206.8, "school"),
    (210.8, "townhall"),
    (213.7, "drop_chorus"),
    (223.6, "drop_chorus_otra"),
    (227.5, "beer_again"),
    (243.7, "dance1"),
    (247.7, "dance2"),
    (251.9, "dog"),
    (255.4, "dog_pee"),
    (258.4, "beers40"),
    (266.6, "expel"),
    (273.6, "stairs"),
    (279.4, "pee"),
    (280.9, "pee_laugh"),
    (282.4, "think"),
    (284.4, "where1"),
    (286.9, "where2"),
    (288.4, "world"),
    (291.6, "jungle"),
    (294.4, "happy"),
    (296.9, "filthy"),
    (303.7, "outro_oh"),
    (318.6, "outro_friends"),
    (331.6, "fin"),
]


def render(name):
    p = Paint(zlib.crc32(name.encode()))
    SCENES[name](p)
    p.save(FRAMES / f"{name}.png")


def contact_sheet(names, cols=6):
    tw, th = 320, 180
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 18)), (60, 60, 60))
    d = ImageDraw.Draw(sheet)
    for i, n in enumerate(names):
        im = Image.open(FRAMES / f"{n}.png").resize((tw - 4, th - 4))
        x, y = (i % cols) * tw, (i // cols) * (th + 18)
        sheet.paste(im, (x + 2, y + 2))
        d.text((x + 4, y + th), n, fill=(255, 255, 255))
    sheet.save(OUT / "contact.png")


def video():
    lst = OUT / "work" / "concat.txt"
    lst.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    ends = [t for t, _ in TIMELINE[1:]] + [END]
    for (t, n), e in zip(TIMELINE, ends):
        lines += [f"file '{(FRAMES / (n + '.png')).resolve()}'", f"duration {e - t:.3f}"]
    lines.append(f"file '{(FRAMES / (TIMELINE[-1][1] + '.png')).resolve()}'")
    lst.write_text("\n".join(lines) + "\n")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(SONG),
        "-vf", "fps=25,format=yuv420p", "-c:v", "libx264", "-tune", "stillimage", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k", "-shortest", str(OUT / "aguita.mp4"),
    ], check=True)


if __name__ == "__main__":
    FRAMES.mkdir(parents=True, exist_ok=True)
    order = list(dict.fromkeys(n for _, n in TIMELINE))
    missing = set(SCENES) - set(order)
    if missing:
        print("unused drawings:", sorted(missing))
    todo = sys.argv[1:] or order
    for n in todo:
        render(n)
    contact_sheet(order)
    if not sys.argv[1:]:
        video()
