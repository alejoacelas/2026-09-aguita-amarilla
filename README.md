# Mi agüita amarilla, remade by Claude

A one-shot prompt for Claude Code to remake the
[MS Paint video for "Mi agüita amarilla"](https://www.youtube.com/watch?v=S0qt3w1Qo0g)
(by Alex Párraga Ferrer, 2010), preserving its half-assed Windows 7 Paint look.

- [`prompt.md`](prompt.md): the prompt.
- [`reference/frames.md`](reference/frames.md): 77 cuts with timings, lyrics and
  descriptions of the 44 distinct drawings in [`reference/frames/`](reference/frames/).
  Lyrics were transcribed with whisper.cpp; timing is ±1 s.
- [`reference/style.md`](reference/style.md): palette, line, fill and text rules.

## Rebuilding the ignored media

```sh
yt-dlp -f 'bv*[height<=720]+ba' --merge-output-format mp4 -o reference/video.mp4 S0qt3w1Qo0g
ffmpeg -i reference/video.mp4 -vn -q:a 2 reference/song.mp3
```
