# Donkey Kong Jr. four-pipe route

Donkey Kong Jr., the Select alternate on Donkey Kong’s slot, clears the first
four pipes and the first gap of 1-1 in one Mesen replay with both lives. The
third and fourth pipes use four added stock `$25` vertical girders. All eight
girders were created 287 pixels right of the camera, then scrolled into view.

| Pipe | Girder | World left X | Center X | Initial top Y | Oscillator center Y |
|---|---|---:|---:|---:|---:|
| 3 | Ascent | 688 | 704 | 192 | 169 |
| 3 | Descent | 752 | 768 | 192 | 169 |
| 4 | Ascent | 880 | 896 | 192 | 161 |
| 4 | Descent | 944 | 960 | 192 | 161 |

The controller reached far ground at X516, X661, X788 and X980, all at
Y176. The fourth ascent reached the cap at X917/Y112. An ordinary A jump
from X940/Y112 reached the descending girder at X954/Y91. The controller
then waited near the center and walked off near the right edge as the lift
returned to ground level. Earlier replays showed that stepping off high or
catching the lift only at its left edge could trigger the original fatal fall.
The first gap used Right+A for eight source updates from X1094/Y176, then
Right to the far bank at X1136/Y176. No helper was needed at that gap.

The route used 10,319 physical frames and 4,320 observed original Main
entries, including waits for the girders. That timing leaves performance
work open. The replay verifies the route through the first gap. The second
gap, the rest of 1-1, and earned powerups remain separate.

The stock constructor, camera window, and carry service remain in use.
The [funding and CPU checks](dkjr-four-pipe-funding-1110.md) cover actual
cold readback, 9,216 camera/ordinal cases, 96 full-pool retry and birth
cases, and 810 paired refresh checks. All 100 named menu entries retained
Start/A admission. The separate CPU replay uses a different timing model
and failed on the third descent; the full route evidence is the actual
Mesen replay.

The Downloads ROM was replaced directly, then reproduced the candidate’s
native receipt byte for byte. Automatic patch checks passed before and after
the replacement. No backup or capture files were created.

- Parent ROM SHA-256 `a20d254d4730583ee1f039b10abcf873559987e4f989968037a38e17427faac1`
- Candidate ROM SHA-256 `b031802c7bc4f4e9596683e66f2f53c124b3a3ac155b80bbec03c5965b8e4e65`
- Reconstructed IPS SHA-256 `f797c2adee4f7170bfd75264480179545464547c6cedb55257978475000a3fae`
- Controller source SHA-256 `ca2c7429cbc9198ffff21a733b39234469cdebffb89143d899b95a4c4af37eb8`
- Native receipt SHA-256 `6b38ff7c623440ddca990760c2f3d59dd98691ddc3681a82553304f5ea21ba20`
