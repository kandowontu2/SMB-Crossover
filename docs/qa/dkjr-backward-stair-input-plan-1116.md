# DK Jr stair handoff: existing backward-jump input plan

Prefer an ordinary source ability before any terrain, collision or helper
change. A rightward jump while **facing left** retains the same right support
edge after landing. Root owns the new controller and genuine stair/native
qualification. This plan adds no control text, code, RAM or helper geometry.

Root's actuala3fb61283 query trace, receipt
`3fa5bf5784f955a45d1c10331a620e41804d307e79aa019794a86ace085d4426`,
now proves the loss query has stable current/cached camera2047, delta0 and
sourceX72. The previous query lands with jump body `[81,178,97,193]` against
fresh terrain `[97,192,112,207]`. The next ground body `[79,175,96,190]`
has fresh support window `[79,96,191,192]` and an empty rebuilt list; source4
follows. This is the one-pixel pose-edge retraction, not a stale list or camera
epoch. Original ground checks support before it can advance right, as proved
in [the order contract](dkjr-static-stair-order-source-1116.md).

The first table review considered only the right-facing jump. The actual
original table is facing-dependent:

| Phase / facing | Pointer entry | Record | Shape `[L,T,R,B]` |
|---|---|---|---|
| Ground/right C06D1 | AFF5 | B005 | `[7,0,24,15]` |
| Ground/left C06D0 | AFF7 | B005 | `[7,0,24,15]` |
| Jump/right C06D1 | AFFD | B015 | `[9,0,25,15]` |
| Jump/left C06D0 | AFFF | B019 | `[5,0,24,15]` |

Thus the left-facing jump's right edge is sourceX+24, identical to ground.
For the observed2144-world tile, first right contact at player2128 remains
supported after landing. This only removes the demonstrated edge retraction;
it does not assert a completed stair or grant forgiveness for another contact.
Special pose C0712 is outside this ordinary ground/jump table contract.

`plan_dkjr_backward_stair_input_1116.detached(exacta3fb)` is frozen at SHA256
`2ede0a2fcd5bd2314c6e7dd3b40b8794e0acce5fa4e1eb355eade097c8c77cf4`.
Its final source receipt is
`6e2812c123265f888dfb5e19964ee0d2d0c2b47ac9dc1484faede5f33ab23d3c`.
It authenticates the actual current pointer/record bytes and byte-exact input,
transition, airborne movement and Phase fragments. Original input writes
direction C054 and fresh-jump state3, but does not write facing C06D. The
airborne horizontal routine A734 reads direction independently, advances right
for direction4 and passes the unchanged facing to the pose publisher. The
transition resets age/fraction but does not replace facing. Already-airborne
Phase skips ground input, preserving that direction/facing pair.

A small declared callback component starts at real compiled opening cold and
uses only native SavedJoypadBits input values with actual HuMovement/FullBox.
Right input sets grounded facing1; Left input sets grounded facing0 while the
integer native X remains40; neutral preserves0. Fresh Right+A then produces
source3/direction4/facing0/age1 and fresh129. Continued Right+A produces age2,
direction4/facing0, fresh1, and moves native X40→41. Both actual jump boxes have
right=sourceX+24. This proves the source API accepts the intended original
backward jump. It is **not** a physical pad-polling witness or a natural stair
traversal, and it does not seed the facing, pose, actor, health or terrain.

The root controller should actually obtain grounded C06D0 even when it arrives
exactly at the takeoff target, release A through its normal input path, wait
its existing neutral preparation, then request Right+A together. Its old
clear-head branch retreats only when `player>takeoff`; arriving exactly at the
target can preserve right facing through the neutral wait. A fixed neutral
wait alone is not a Left-facing acknowledgement. Each new stair preparation
must qualify its actual facing rather than assume the previous one survived
ordinary grounded Right movement.

No jump/gravity, fall threshold, player/enemy body table, terrain window,
height or placement is changed. All13 existing helpers stay unchanged. The
first descriptor assertion accidentally required adjacent instructions across
source labels/comments; correcting that source-text binding changed no game
fixture. An intermediate1cab receipt started with constructor facing already0;
the final component explicitly verifies Right1→Left0 before the fresh jump.
The bounded absent root `build/dkjr-backward-stair-input-1116` uses max-files1/
600seconds and produces zero output files. All handles are terminal.
