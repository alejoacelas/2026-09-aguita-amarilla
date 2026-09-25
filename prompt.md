Make a music video for `reference/song.mp3` ("Mi agüita amarilla", Los Toreros Muertos, 5:39) that looks like a bored teenager drew it in MS Paint with a mouse in 2010. Work autonomously; use any tools you need.

The visuals come from the lyrics. Transcribe the song with timestamps (e.g. whisper), check the words against published lyrics, and decide what to draw for each line. The song follows the pee from a bar toilet through the pipes, rivers, sea, sky and rain back into everyone's life; illustrate that literally and comically.

For the look, read `reference/style.md` and the four example drawings in `reference/frames/`. Treat them as hints about the spirit, not a spec. The one firm rule: it must look half-assed. Resist making it polished, designed or pretty. Some approaches that tend to get there:

- Draw with simulated Paint tools rather than vector art: a thick brush fed by jittery, mouse-like stroke paths; perfect ellipses and rectangles for props; a real pixel flood fill for the bucket; a seeded spray can.
- Hard cuts timed to the lyrics, mostly static slides. Reusing a drawing with a small change (a new speech bubble) is in character.
- Keep every drawing deterministic (fixed seeds), render each once, and assemble the video with ffmpeg, muxing in the song.

Check your work: make a contact sheet of all drawings, look at it, and redo anything that looks too clean or too designed. Then pull stills at 10 random timestamps from the final video and confirm each matches what's being sung. Deliver `out/aguita.mp4` plus the source.
