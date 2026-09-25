# Mi agüita amarilla, remade by Claude

A one-shot prompt for Claude Code to make a music video for "Mi agüita amarilla"
from its lyrics, in the half-assed MS Paint style of
[Alex Párraga Ferrer's 2010 fan video](https://www.youtube.com/watch?v=S0qt3w1Qo0g).

- [`prompt.md`](prompt.md): the prompt.
- [`reference/style.md`](reference/style.md) and four drawings from the original in
  [`reference/frames/`](reference/frames/): style hints.

## Rebuilding the ignored media

```sh
yt-dlp -f 'bv*[height<=720]+ba' --merge-output-format mp4 -o reference/video.mp4 S0qt3w1Qo0g
ffmpeg -i reference/video.mp4 -vn -q:a 2 reference/song.mp3
```
