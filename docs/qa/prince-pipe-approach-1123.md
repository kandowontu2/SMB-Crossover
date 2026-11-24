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

Climbing the first pipe from its right side still needs work. The linked
controller replay successfully crossed it going right and turned back with
Up+Left. It continued to recoil at X479/Y176 throughout the return attempt.
