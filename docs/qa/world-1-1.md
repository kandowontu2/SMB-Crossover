# World 1-1 replay audit

All 12 fresh-power-on fixed-controller replays for the original six characters passed on the palette-fix checkpoint pinned below. The review decoded 60,364 native video frames. That checkpoint's emulator suite passed 147 cases across MMC3 and MMC5. Later character-select, audio, OAM and block fixes have separate regression coverage; these videos do not validate those later builds.

Each surface run defeats all 17 enemies and collects all five power-ups, including the hidden 1-up. Each shortcut-pipe run defeats all six enemies encountered along that route and collects its mushroom. Every run survives and verifies movement under controller input in World 1-2. These replays inspect memory but do not write game RAM or registers.

| Character | Route/video | Frames | Enemies | Pickups | Lag frames | Overloaded sprite frames |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Mario | [surface](../../build/playthroughs/palette-fixed-0-surface/playthrough.mp4) | 5,653 | 17 | 5 | 2 | 44 |
| Mario | [pipe](../../build/playthroughs/palette-fixed-0-pipe/playthrough.mp4) | 4,430 | 6 | 1 | 4 | 0 |
| Mega Man | [surface](../../build/playthroughs/palette-fixed-1-surface/playthrough.mp4) | 6,056 | 17 | 5 | 148 | 742 |
| Mega Man | [pipe](../../build/playthroughs/palette-fixed-1-pipe/playthrough.mp4) | 4,142 | 6 | 1 | 70 | 350 |
| Samus | [surface](../../build/playthroughs/palette-fixed-2-surface/playthrough.mp4) | 6,404 | 17 | 5 | 20 | 321 |
| Samus | [pipe](../../build/playthroughs/palette-fixed-2-pipe/playthrough.mp4) | 4,076 | 6 | 1 | 32 | 377 |
| Bill | [surface](../../build/playthroughs/palette-fixed-3-surface/playthrough.mp4) | 5,854 | 17 | 5 | 166 | 571 |
| Bill | [pipe](../../build/playthroughs/palette-fixed-3-pipe/playthrough.mp4) | 4,100 | 6 | 1 | 87 | 357 |
| Link | [surface](../../build/playthroughs/palette-fixed-4-surface/playthrough.mp4) | 5,974 | 17 | 5 | 12 | 76 |
| Link | [pipe](../../build/playthroughs/palette-fixed-4-pipe/playthrough.mp4) | 4,114 | 6 | 1 | 16 | 45 |
| Simon | [surface](../../build/playthroughs/palette-fixed-5-surface/playthrough.mp4) | 5,520 | 17 | 5 | 19 | 138 |
| Simon | [pipe](../../build/playthroughs/palette-fixed-5-pipe/playthrough.mp4) | 4,041 | 6 | 1 | 18 | 44 |

Every AVI frame was decoded for the floor-row vertical-shift check; hardware scroll-register writes were audited at the HUD split, and queued common SFX were checked against voice ownership. These checks raised zero flags. Event contact sheets and frame sequences around power-up emergence support visual inspection; this is not a claim that every frame was watched manually.

Native lossless AVI video and PCM audio were captured together in each replay. The MP4 is a viewing copy. The final emulator stop callback is one frame after AVI capture stops; the saved final screenshot and trace contain that last control-confirmation frame.

Each run directory contains `manifest.json`, `review.json`, `applied-inputs.csv`, `trace.csv`, `objects.csv`, `events.csv`, `apu.csv`, `scroll-writes.csv`, `native.avi`, `end.png`, `review-contact-sheet.png`, and `reveal-*.png`. The manifest pins the ROM, policy, and input hashes.

Lag and the NES eight-sprites-per-scanline limit remain visible in the counts above. Priority rotation shares visibility during sprite overload; these checks do not establish complete website parity or waveform identity for every sound.

The latest Bill palette correction restores the shared mushroom tan ($27) in place of black ($0F). The hosted red/white bullet frames never use that third color, so their single-sprite layout is unchanged. The emulator checks preserve the item colors through both upgrade animations.

Water was verified separately with explicit fixtures in the actual 2-2 room for all six characters on both mappers. Those checks cover source movement, surface/pose boundaries, jump rules, weapons, music and whirlpools; they are not full water-level completion replays. See [the water reference](../reference/water.md).

## Reproduce

```sh
python tools/verify.py --mmc5
python tools/playthroughs/verify_routes.py --tag replay-check
python tools/playthroughs/review.py build/playthroughs/replay-check-3-surface
```

The default route prefixes use the accepted recordings above. The runner copies each ROM and its symbols into the run directory before starting the emulator. Captures use Mesen 2 with native sprite limits.

## Tested ROM SHA-256

- MMC3: `f120472562ad996e5133919a229dcfb940f08be6a4cbff542507b2944e11f5e0`
- MMC5: `3d8041aee8367f4548a67f590b61e17cec69a4675b8a343af5aaa2ef10604501`
