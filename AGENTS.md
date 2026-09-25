# Mi agüita amarilla

Explores whether Claude Code can one-shot a faithful remake of the 2010 MS Paint
fan video for "Mi agüita amarilla" (Los Toreros Muertos), keeping its crude,
mouse-drawn look.

- `prompt.md` is the one-shot prompt. Its file paths assume the working
  directory holds `song.mp3`, `frames.md` and `style.md`; copy them from
  `reference/` or point the prompt there.
- `reference/` holds the source analysis: 44 distinct drawings, the cut-by-cut
  timeline with lyrics (`frames.md`), and the style guide (`style.md`).
- `reference/video.mp4` and `reference/song.mp3` are copyrighted and ignored.
  Rebuild them as described in the README.
- Put renders in `out/` (ignored).
