# Mi agüita amarilla, remade by Claude

A one-shot prompt for Claude Code to make a music video for "Mi agüita amarilla"
from its lyrics, in the half-assed MS Paint style of
[Alex Párraga Ferrer's 2010 fan video](https://www.youtube.com/watch?v=S0qt3w1Qo0g).

- [`prompt.md`](prompt.md): the prompt.
- [`reference/style.md`](reference/style.md) and four drawings from the original in
  [`reference/frames/`](reference/frames/): style hints.

## The remake

A 12 fps animation, at 5:39 as long as the song. The lines "boil": every frame is redrawn slightly differently
six times a second, cycling through three versions, the way hand-drawn animation wobbles.

- [`paint.py`](paint.py): a fake MS Paint with a mouse-shaky brush (which can
  draw part of a stroke, for write-on), perfect shape tools, a pixel bucket fill, a seeded
  spray can, and handwritten or typed text.
- [`props.py`](props.py): posable characters and props (the stick narrator, the
  drop, cows, toilet, rain) plus timing helpers. `BEAT` is the song's measured tempo.
- [`shots.py`](shots.py): the 33 shots and the timeline. The pipes, the river,
  the sea floor and the sky are canvases wider than the screen that the camera
  pans across. Verse 2 reuses verse 1's shots at its own timings.
- [`render.py`](render.py): renders frames to `out/anim/` in parallel (about 35 s
  on 10 cores) and muxes the song into `out/aguita.mp4`.

```sh
uv run python render.py              # the whole video
uv run python render.py sheet        # out/contact.png: three frames per shot
uv run python render.py strip river  # eight frames across one shot
uv run python render.py clip 72 90   # a stretch with sound, in out/work/clip.mp4
```

The timings came from `whisper-cli` (whisper.cpp, `ggml-large-v3-turbo`) word
timestamps, checked against the
[published lyrics](https://lyricsondemand.com/los_toreros_muertos/mi_agita_amarilla).

## Rebuilding the ignored media

```sh
yt-dlp -f 'bv*[height<=720]+ba' --merge-output-format mp4 -o reference/video.mp4 S0qt3w1Qo0g
ffmpeg -i reference/video.mp4 -vn -q:a 2 reference/song.mp3
```
