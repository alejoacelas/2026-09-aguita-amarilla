Make a music video for `song.mp3` ("Mi agüita amarilla", Los Toreros Muertos, 5:39) that looks like a bored teenager drew it in Windows 7 MS Paint with a mouse in 2010. Work autonomously; use any tools you need.

`frames.md` is the timeline: 77 slide cuts with start times, durations, the lyric at each moment, and a one-line description of each of the 44 distinct drawings. Follow it exactly: same cuts, same timing, same drawings, same reuse. `style.md` describes the look. Read both fully before writing code.

The whole joke is that it's half-assed. Do not make it good. Hard rules:

1. Canvas: 960x720 output, 30 fps, black letterbox with the drawing in a 960x414 band at y=154. Hard cuts only. The one motion effect is the Movie Maker-style spin of the intro stick figure card (0:05–0:33, 4:17–4:22).
2. Colours: only the Windows 7 Paint default swatches listed in style.md. No gradients, no shading, no transparency, no drop shadows.
3. Freehand lines: a ~5 px round black brush driven by simulated mouse input. Generate each stroke as a polyline sampled like a real mouse drag (uneven spacing, small jitter, slight overshoot at corners, joints that don't quite meet). People, animals, speech bubbles, arrows and handwritten capitals are all freehand.
4. Shape-tool props: toilet, sun, washing machine, buildings, windows and block arrows are perfect ellipses, rectangles and polygons. The contrast between shaky freehand people and geometrically perfect props is essential.
5. Fills: implement a real pixel flood fill (bucket tool) on the raster, so fills stop at outlines and leave the white gaps real Paint leaves. Soft things (clouds, vapour, pee in the river/sea, rain on buildings) use a spray-can tool: seeded random dots in a circle.
6. Text: most words are handwritten capitals in the freehand brush, uneven letter sizes, often with a hand-drawn arrow to the thing labelled. The few typed labels listed in style.md use a small plain system font. Frame 042 is bold Comic Sans on a solid yellow canvas. The beer mug in frame 003 is a pasted realistic photo: draw the most realistic beer mug you can, next to a hand-drawn "X 40".
7. Reuse: draw the base scene (stick figure peeing a yellow arc into the ellipse toilet) once and reuse it pixel-identical in all 43 appearances, swapping only the speech bubble or mouth. Background sets (river, sea) are drawn once and props get added on top, like editing the same .bmp.
8. Determinism: every drawing is a pure function of a fixed seed. Render each distinct drawing once to a PNG, then assemble the video from the timeline with ffmpeg and mux in song.mp3. No per-frame randomness, so nothing shimmers.

Check your work: after rendering the 44 PNGs, make a contact sheet, look at it, and fix anything that looks too clean, too designed, or inconsistent with style.md. Then render stills at 10 random timestamps from the final mp4 and confirm each matches the lyric in frames.md. Deliver `aguita.mp4` plus the source.
