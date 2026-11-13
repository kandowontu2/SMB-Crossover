# Thomas hidden 1UP lift

## Proposed source change

Parent ROM SHA256 is
`318a087735b4204c74274b4107efbc302bc15a674a7f6f9d3bed598cea90d08d`.
The in-memory candidate SHA256 is
`65ee94ca9ac6e1b5ad44303d08f76ecbc175a88232c82ef8c32712edf150a643`.
Source SHA256 for `tools/reference/thomas_oneup_lift_1113.s` is
`7d1e5a51d72ebd39f9cf5dbdd0aecdb8e51f7f8d53941b45da6ff13e2d1ce9fb`.

Thomas receives the eighth record in his existing stage-1-1 vertical
platform manager. Its left edge is X1008, center X1024, initial top Y192
and width 32. The actor is the existing native vertical platform `$25`.
It spawns beyond camera right at relative left 256 through 287, using the
highest free enemy slot. Full slots defer creation. Native actors retain
their existing priority.

The record uses bit `$80` in the manager's existing seen byte. The existing
seven records keep their positions, behavior and native constructor. The
table grows from 21 to 24 bytes within the same authenticated retired query
tail at `$B5D2..$B60C`. The three added table bytes replace source-owned
retired bytes `03 20 a0`. Seven existing table references and the record
limit are updated. The existing kernel cookie advances to
`a70a4004c467b554490966b328cc9e0a`.

The original seven stage-1-1 left/center pairs remain 400/416, 560/576,
688/704, 864/880, 1200/1216, 2560/2576 and 2816/2832. Each has initial
top Y192 and width 32. The affected Select alternate is Thomas.

## Finite CPU checks

The compositor authenticates current 318a087, reconstructs its exact
15a683 parent in memory through the delivery helper, checks the complete
old Thomas carrier/cookie, compiles both table versions and verifies every
edited preimage. A direct-call scan excludes live JSR/JMP entries into the
retired tail.

| Check | Completed cases |
| --- | --- |
| Existing seven placement pairs | 126 |
| New camera boundary and slot-pressure cases | 18 |
| New native platform carry cases | 6 |
| Other-stage or frozen rejection | 4 |
| Foreign owner or Ryu-family alternate pairs | 7 |
| Genuine NMI cuts | 21 |
| Genuine IRQ cuts | 21 |
| Nested IRQ continuation | 1, deepest parent SP209 |

The interrupt comparisons retain the existing audio-scratch exclusions.
Gameplay RAM, live stack, mapper state and both owner pages match the
uninterrupted continuation.

## Natural controller CPU route

The route starts through the real menu, native parser and source-backed
opening. Ordinary input earns the mushroom, completes its 60 hosted
updates and crosses the four original pipes. It then uses the new native
platform below the authored hidden block.

At epoch 2494, Thomas X1022/Y150 boards native slot 3, left X1008/top182.
At 2495 he requests a fresh original Up jump while still boarded, at
X1023/Y149 with platform top181. The actual `$60` hidden-block head
collision runs at epoch 2497, Thomas X1025/Y138. The handler observes Up,
negative native Y speed, original source air state 5 and displacement
`$7C`. This records the original rising jump at the head hit.

The authored 1UP starts at epoch 2498, slot 4, X1024/Y119. After native
emergence and motion it reaches the real collector at epoch 2639, actor
X1102/Y187 and Thomas X1093/Y165. Native popup `$0B` awards the life at
epoch 2645, changing the counter from 2 to 3. Eight further updates retain
status 1, active gameplay and three lives. The route records two head
collisions, two `SetupPowerUp` calls, two collectors and 60 hosted updates.

## Native controller

The new `tools/audit/replay_thomas_oneup_1113.py` derives its opening and
first four pipe controls from the frozen flower fixture. It requires an
offscreen native lift birth, boarding, a fresh Up request, original rising
source state at the actual hidden head collision, authored 1UP emergence,
mature native collection, popup `$0B` and exactly one awarded life.

Lua 5.4 syntax and the 60-update opening mock pass. Controller SHA256 is
`66de68b126ddf089e27861f33d44600216b6752c578c9c70714ac675afb6d352`.

The first native attempt reaches the real hidden head contact but fails
the observer's current-Up assertion after its three-update input pulse.
Its receipt is
`a3308797f1fd7e99ec0517fd9923a80e9d12bcb2ec4bf3d74feb9e47ece66c1e`.
The corrected controller records all head fields before asserting and
holds the original Up input through that contact, with a 24-update bound.
The strict source-air and negative-speed checks remain in force. The
matching CPU route repeats successfully with the same head and award
epochs.

Root's actual native candidate run passes at physical frame 3248. Receipt
SHA256 is
`3035b17ea05fa4600ea64238fbbd59dc03a83fd680404c210e597392b5565cf3`.
The native constructor observes left X1008/top192 beyond camera right at
relative left 287. At frame 2970, actual head tile `$60` is hit at Thomas
X1026/Y139, with saved input 9, original source air state 5, displacement
`$7C` and native Y speed `$F8`. The mature authored 1UP in slot 2 reaches
the collector at frame 3228, yielding popup 11 and one native pickup sound
write. The native life award changes 2 to 3 at frame 3236, and eight
subsequent logical updates retain the result. The original jump arc is
preserved. The candidate remains private pending a full-stage regression.

## Composable API

`compose_thomas_oneup_lift_1113.proposal(parent_bytes)` returns candidate
bytes and an information dictionary containing exact edits, kernel,
cookie and source hash. The parent must be exact 318a087.

`compose_thomas_oneup_lift_1113.inverse(candidate_bytes)` reconstructs exact
318a087 using compiled prior table/reference bytes and the authenticated
old cookie. It verifies the complete parent hash and recomposes the
candidate byte-for-byte. It writes no files and requires no parent ROM
copy. The forward/inverse round trip passes on 65ee94.

## Reproduction

These CPU invocations produce zero files.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/thomas-oneup-lift-1113 --max-files 1 --timeout 180 -- python -B tools/audit/compose_thomas_oneup_lift_1113.py
python -B tools/audit/run_bounded_build_v1.py --output build/thomas-oneup-route-1113 --max-files 1 --timeout 600 -- python -B tools/audit/check_thomas_oneup_route_1113.py
python -B tools/audit/run_bounded_build_v1.py --output build/thomas-oneup-lua-1113 --max-files 1 --timeout 180 -- python -B tools/audit/replay_thomas_oneup_1113.py --check-only
```

Root can reuse its two-file private output after the prior run has ended.
The producer writes one candidate and one Lua controller.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/metal-flower-native-1112 --resume --max-files 2 --timeout 300 -- python -B tools/audit/replay_thomas_oneup_1113.py --output build/metal-flower-native-1112
```
