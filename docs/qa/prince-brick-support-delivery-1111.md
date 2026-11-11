# Prince keeps his footing on the coin brick

The MMC5 nightly keeps Prince supported when he steps right after climbing
the exposed coin brick at X1504–1519, top Y144 in World 1-1. The exact
Downloads replay starts at the title, crosses four pipes and two gaps,
lures both Goombas into the second gap, and climbs the brick with Up. Prince
walks from X1491 to X1507 and X1513, then starts his original running jump at
X1513/Y112 with four HP and both lives. The candidate and installed replays
produced identical receipts. No helper actors or level data changed.

The actual raw query trace identified the original running foot probe at
donor bank 7 `$D279`. It deliberately queries 32 pixels behind a right-facing
actor. The translated donor support call at `$A6F6` used its native-coordinate
fallback, which accepted the four pipe-cap types and rejected the exposed
coin brick `$58`. That routed the original empty-floor response through
donor `$D35C`, translated call site `$A7BB`. The store at RAM2 `$C427`
(post-write PC `$C42A`) changed source X1499 to X1476. The following native
export moved Prince from X1491 to X1468. [Previous Mesen trace](prince-native-brick-route-1111.md)

The 133-byte replacement retains the existing sole, facing, pose, native
grounding, exposed-surface, and solidity checks. It admits `$58` alongside
the original `$10–$13` only through that same physical check. The other
255 metatiles matched the exact parent in CPU comparisons. Eight negative
controls include a covered brick, an unsupported edge, airborne movement,
and mismatched sole positions. An actually empty tile still follows the
original unarmed fall and relocation. The tests passed 261 real IRQ cuts
and 261 lag-NMI cuts across exposed brick, legacy pipe, and empty tile.

Only the Prince metadata worker and authenticated packet changed. The
runtime and state streams retain their original decoded bytes. The metadata
stream grew two compressed bytes, leaving 748 bytes in the existing carrier.
Reapplying the old worker reconstructs the exact parent. The generated IPS
reconstructs the tested ROM from the clean source image.

- ROM `17122790d711b905c681dced1fd9b3a0e69e1364cb039d514ba635c31a1e4fed`
- IPS `5849b2801e71b6d91fead73827949b3c193802e0aa79be4bfc80d9482374797e`
- Mesen receipt `94740623dbb75a06864c257913d121e82f2cce96d1dfea11014e97354ad0e002`
- Controller tail `02e56e7daf78158f61adfa9fca9245b240a614a13671c5317b244d285cab540c`
- Assembled controller `64f523757c6f35949f2a0b22977dc1dfb41bb7f9d3e73c73eae1cf7bfab507dd`

The running jump starts correctly. Reaching the next brick, passing the
Koopa, clearing 1-1, and earning the power-ups remain open.
