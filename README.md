# Mi agüita amarilla, remade by Claude

A one-shot prompt for Claude Code to make a music video for "Mi agüita amarilla"
from its lyrics, in the half-assed MS Paint style of
[Alex Párraga Ferrer's 2010 fan video](https://www.youtube.com/watch?v=S0qt3w1Qo0g).

- [`prompt.md`](prompt.md): the prompt.
- [`reference/style.md`](reference/style.md) and four drawings from the original in
  [`reference/frames/`](reference/frames/): style hints.

## The remake

- [`paint.py`](paint.py): a fake MS Paint with a mouse-shaky brush, perfect shape
  tools, a pixel bucket fill, a seeded spray can, and handwritten or typed text.
- [`scenes.py`](scenes.py): one function per drawing (67 of them), each seeded
  from its name.
- [`render.py`](render.py): the cut list timed to the lyrics. It renders each
  drawing once into `out/frames/`, writes `out/contact.png`, and muxes the song
  into `out/aguita.mp4`.

```sh
uv run python render.py           # everything
uv run python render.py pee dog   # redraw a few, refresh the contact sheet
```

The timings came from `whisper-cli` (whisper.cpp, `ggml-large-v3-turbo`) word
timestamps, checked against the
[published lyrics](https://lyricsondemand.com/los_toreros_muertos/mi_agita_amarilla).

## Rebuilding the ignored media

```sh
yt-dlp -f 'bv*[height<=720]+ba' --merge-output-format mp4 -o reference/video.mp4 S0qt3w1Qo0g
ffmpeg -i reference/video.mp4 -vn -q:a 2 reference/song.mp3
```
