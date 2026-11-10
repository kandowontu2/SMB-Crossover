# Donkey Kong Jr. crosses the second pipe in 1‑1

Choose Donkey Kong on row four, column four, then press Select once for
Donkey Kong Jr. The MMC5 nightly is
`a20d254d4730583ee1f039b10abcf873559987e4f989968037a38e17427faac1`.
The 2,099,510-byte IPS is
`a1621d5ef67b60d5a617651a3cb0260d56141160376454a5db2c9d6a53a13852`.

Two stock vertical girders carry Jr. across the 48-pixel second pipe,
whose cap starts at world X608 and top Y160. The first pair keeps its
previous positions and native movement center. The new pair uses the
stock actor’s Y177 motion center. The left lift ends at X592, leaving
16 pixels before the pipe so Jr. can clear the girder with his original
jump. The right lift starts over the far side of the cap and carries him
down once he moves right beyond the pipe.

| 1‑1 girder | World left X | World center X | Initial top Y | Width |
| --- | ---: | ---: | ---: | ---: |
| First pipe, ascent | 416 | 432 | 192 | 32 |
| First pipe, descent | 480 | 496 | 192 | 32 |
| Second pipe, ascent | 560 | 576 | 192 | 32 |
| Second pipe, descent | 624 | 640 | 192 | 32 |

The actual compiled CPU checker covers 3,840 camera/cursor combinations,
48 full-slot retries with an actual native constructor in each possible
released slot, loaded-area rejection, and warm life reset. The loader-owned
area pointer uniquely selects the authored 1‑1 map even when the parser
queues an underground destination. Each girder appears offscreen 287
pixels right of camera-left and scrolls into view. All source changes fit
in the existing private DK Jr. carrier and authentication record.

The same controller-only Mesen replay starts from the title on both the
candidate and installed Downloads ROM. It clears the first pipe at
X517/Y176. On the second ascent, it jumps from X589/Y126 with the girder
top at Y158, stands on the cap at X612/Y128, then rides the other girder
and reaches ordinary ground at X660/Y176 with both lives. The four
girders produce 45, 46, 45 and 11 native carries respectively. The replay
ends at physical frame 5698.

| Evidence | SHA-256 |
| --- | --- |
| Physical controller | `e782a077485520ed8832587acd8af31839bbf58096b5b6cee4c89641bd11f43f` |
| Candidate and Downloads Mesen receipt | `a3cd3ef76fb2b6423f833c2b6b4348344c15c416ad911789296a234864a3523f` |

The earlier ascent at X576 let the rising lift recapture Jr. at the pipe
edge. That candidate reached the cap with fatal original fall damage,
even on a no-jump controller. The final clearance between the lift and
the cap allows a normal jump and safe landing. The later pipes, full
stage and earned powerups remain open.
