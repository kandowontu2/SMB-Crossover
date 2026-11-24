# Prince of Persia’s first pipe approach

On `e5cb1367`, holding Up+Right from the real X404 approach to the first pipe
in 1-1 reached the left face at X434. The Prince repeatedly recoiled to X417
while the direction continued to take priority over Up. He kept both lives
and all five HP. Mesen receipt
`0ef5f8eea4685a280752777504e44f165f19a3566c442145487ea928d6f246f9`.

The Prince now checks for a real pipe tile ahead when Up and the facing
direction are held together. That input keeps the existing ledge action
active through braking and the grab. Directional movement resumes above the
pipe. Up alone and the running jump inputs retain their normal handling.
The Prince uses the existing geometry and animation. The new controls and
state fit in the Prince’s own RAM packet, with cold storage extended by one
previously unused CHR page (931). The encoder round trip restores the
original nightly byte for byte.

| Mesen replay | Outcome | Receipt SHA-256 |
| --- | --- | --- |
| Continuous Up+Right from X404 | Grabbed and crossed the first pipe, reaching X563/Y176 with five HP and two lives | `1f4cda2e7d069cb35dc72c3ff2b4370742e5847385cc89700c0fb0483e312002` |
| Full 1-1 with sword pickup | Reached 1-2 with the sword, five HP and both lives, then completed 25 grounded game updates | `18752d751a3fef60d7e4ed38932db77b53d553c3120273dff355d974c39c2e15` |

The actual Downloads launch reproduced both candidate receipts on
`d38c42bf5073b3b81a9cbc39bbf5e5b82c4316a5521970f6f0cc9583ac2c6ba8`.
The automatic patch checks found no matching sidecar. No backup, capture or
release was created.

## Landing after the pipe

The first change still let the Prince’s foot cross Y208 between updates.
Mesen observed the foot go from Y206 to Y224. The native side probe read
ground tile `$54` at Y208 under the body and in both adjacent samples. Its
wall handler pushed the Prince from X511 to X527 with zero horizontal speed.
The installed-input trace is `d48e5f8c71c9c3b12b0d9d0d4627516eead4347b61a6714b701e27a8af0e838b`.

The follow-up checks for exposed ground when a falling pose has overshot the
surface by at least 16 pixels. It corrects the native Y position before the
side probe. The existing source landing routine then settles the character.
Twelve compiled-helper fixtures cover both block buffers, shallow and rising
motion, covered tiles, empty columns, and the original geometry fallback.

On `fcb67a68`, the same Mesen climb ends at X514/Y176 with the wall timer at
zero. The native wall callbacks at the actual pipe wall remain. The full
Easy replay earns the sword, clears 1-1 with five HP and both lives, and
completes 25 grounded updates in 1-2.

| Mesen replay | Receipt SHA-256 |
| --- | --- |
| First pipe and landing | `5bad9c624f6db272377f93cccc24f4266c1b789e111cccb4e9aee2f2587296e6` |
| Full Easy 1-1 and sword | `fde5119f518de8ba421d0d26636af19b94e570d39cad30f2226b96192abecd25` |

Both receipts matched from the actual Downloads path. Its ROM is
`fcb67a68cfd2aadcf0fc68fb8dbf8152204796cdb58d5caf98bb0127f96f3c01`.

The empty opening took 146 video frames for 96 standing and walking game
updates, one more frame than the measured earlier nightly. Fifty video
frames had no game update. Mesen receipt
`ea715b1dcd21db4a2f70e71d49de297173ff8c9715ff1c49a8ee9df7bd993fad`.

## Climbing back from the right

On `fcb67a68`, a return approach with Up+Left admitted the original Up action
28 at X479/Y176. The first lookup found the real pipe top at Y176. The next
lookup advanced the donor grid from column 9 to row 1, column 0. It sampled
X152 and X168 even though the pipe was at X448–479. The ground in those
columns was treated as blocked headroom. Mesen trace
`ace850240f3f17cd8cfe64a35971b0bd5f2589523aa832ef81f94e621b7daf47`.

The follow-up uses the authored native pipe lip and tests two rows of
clearance over the lip and the body. It applies while facing left during
the original standing Up action. The rest of the ledge routine still uses
its original decisions and animations. Fourteen compiled checks cover
both block buffers, a lip at a page edge, a 64-pixel pipe, covered tiles,
missing lips, and inactive controls.

Mesen crossed the first pipe with Up+Right, turned back, and crossed it with
Up+Left. The original climb action 10 started at X480/Y173 during the return.
The Prince kept five HP and both lives. The separate Easy 1-1 replay kept the
earned sword through 25 grounded updates in 1-2.

| Mesen replay on `c674004a` | Receipt SHA-256 |
| --- | --- |
| First pipe in both directions | `252b1fde2ac609cc2aa5bd2a84f8e8be3f66fc52f117f5959174a87f0399d24e` |
| Full Easy 1-1 with the earned sword | `71a2887007382456ba516b5e30630f52b73082b949dc588ae710652fd8767bbb` |

The actual Downloads nightly reproduced both receipts on
`c674004ad12133ce5d4181ea613450bdddc3726a79adb69d4f9ab40c0dca44c0`.
The automatic patch check is clear. In a linked comparison with the previous
nightly, 48 standing and 48 walking updates matched the Prince's state and
instruction cycles on every update.

The empty opening still takes 146 video frames for 96 standing and walking
game updates. Fifty frames have no game update. Mesen receipt
`1b33a6cd4cfb851e58faafcb51b7f33f2bd76a3e04ea88cd488284d25e10a281`.
