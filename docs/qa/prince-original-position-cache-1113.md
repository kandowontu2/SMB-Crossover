# Independent Prince position-cache oracle

The earned-sword investigation observed native X1455→1340 after auto-draw
near a genuine grounded Goomba. The captured source state had X1463 but
cached X0. The helper traced original7:DAFA restoring that empty cache;
original4:AF57 normally saves the coordinate before animation, and the host
skipped that bookkeeping. The natural-route diagnostic and placement repair
remain separately owned by `prince_pickup_reach_1112`.

Root independently authenticated the original Prince ROM SHA256
`5f14d4d31cc588ddcdfb2b4d46eb7051b06d02655c9208037ef7ae137c4740e4`
and executed its actual save/restore instructions for all65536 coordinate
values. The save bytes at4:AF57 are
`ad0f068ddb04ad10068ddc04`; the first12 bytes at7:DAFA are
`addb048d0f06addc048d1006`. Their exact source-RAM2 translation is
`ad0fc68ddbc4ad10c68ddcc4`.

All65536 comparisons preserve source coordinate, X/Y/SP and all unrelated
flags. The translated save matches the actual donor's resulting A/P and
cached word. The actual donor restore recovers every saved word after the
current coordinate is deliberately changed in the reference machine. This
includes X1463 and both byte/page boundaries. No host gameplay state or ROM
was modified. Output files:0.

Checker: `tools/audit/check_prince_original_position_cache_1113.py`, run with
Python `-B` through the bounded runner under the existing
`build/metal-flower-native-1112` root, two-file cap. It is a small CPU
instruction oracle, not a host placement, full animation, interrupt, physical
gameplay or delivery claim. The12-byte save still needs a qualified source
location, correct once-before-animation scheduling, complete identities and
full lifecycle/native verification.
