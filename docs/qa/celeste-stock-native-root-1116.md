# Current Celeste stock powerups and earned abilities

Actual Downloads00bb passes hidden-life69031, Star27797 and Flower/dash26052
tests, each with a genuine Mushroom prefix. The executed ROM is
`00bb2664647a4ef47b5dfa01c96d50549581d215a33d19a2a6390d1e09078e21`.
No ROM, physics or helper placement changed. Celeste remains PlayerSize1
at tiers0 and1, including after the native delayed life increase.

Strict factory `replay_celeste_head_cell_00bb_1116.py` is
`3c9cf7bf8c159756cf113c596daabe62b88e2eebe47a0ab76ad6a7236e17031b`.
Life Lua `a5636ce8a6982f713b8eec4507729f63f19b25665f2218ab0587aa94c3d3cfe3`;
Star Lua `f08fa1e9adc1fcd5981d350b453ebc915b8257f9c05ca8d08831f82cebc214a0`.
Source9f2add1c records the separate7430b349/f5696bf8 proofs. The compiled
native menu really selects Mario slot0/Select6/raw0/variant4. Both complete
resident host8192 and core3595 byte views are authenticated. Sixteen neutral
returned updates precede policy activation; the source frontend model has
its own separately reported opening. Native/global Main and owner counts
below are not relabeled as source counters or identical UI timing.

The retained old head negative is an input alignment issue: hero1015 put
the native small head at1023, one pixel left of hidden cell1024. Measured
head143 reached its correct height. Corrected ordinary centering at1017
puts the head inside the cell without changing physics or collision code.

## Mushroom prefix

Both native tests genuinely spawn the Mushroom at336/135, witness mature
state80, and physically collect the walking actor296/184 while Celeste is
285/162. Native boxes overlap1x2 at9B28/SP243. CmPickup returnsC1 to
016E/SP234, consumes it without native fallback, gives tier1/small1, then
erases/cue32/popup6. Delayed score0→1000 occurs at Main793;25 later
CmMovement/post-BG/clock returns finish at completed Main819/82BE/SP252,
285/176, tier1/size1/lives2. This is earned wall-grip inventory proof;
the initial life/Star tests do not themselves demonstrate wall-grip or dash.
The later passive visual run below directly witnesses the tier1 wall jump.

## Hidden life

Receipt `5648f4d90e405de7395d660b645e44206a4b4ff5c0f8fc67d4e7364cb808bafb`
has1421 balanced Main and1107 balanced CmMovement/CmAfterBG/clock updates,
1433 physical frames, with every tracked scope complete.

Real hidden60 head precedes kind3 birth Main1302 at1024/120 and maturity
1369 at1024/103. Collector1390 meets matureC0 actor1046/125 while Celeste
is1042/126, positive8x1 overlap. CmPickup returnsC0 and native fallback
executes exactly once; erasure/popup11/cue32 precede the actual8987→898F
INC at1395, lives2→3/cue64. Exactly25 later returned owner updates finish
at Main1421/82BE/SP252,1043/176, size1/tier1/lives3/CmLife3.

## Star

Receipt `d1f7754171fe3b7e53d6c29dcda8d371164bfccd00658ede80c4e8aa0be9ebd2`
has1655 balanced Main and1341 balanced CmMovement/CmAfterBG/clock updates,
1667 physical frames, with every tracked scope complete.

Authored57 head precedes kind2 birth1535 at1616/136 and maturity1601 at
1616/119. Collector1624 meets mature80 actor1640/149 while Celeste is
1637/145, positive9x6 overlap. CmPickupC0 invokes native fallback exactly
once; AF88 and the real35 writer/music64, erasure/cue32/popup6 pass.
The actual score writer awards1200→2200 at1629, followed by25 completed
owner updates at Main1655/82BE/SP252,1638/176, size1/tier1/lives2/Star34.
Terminal score2400 includes later ordinary points; the Star award is1000.

## Flower and earned dash

Actual Downloads26052 passes receipt
`083deff3a20a0d3a2fe10f6a2e5d8c8acf8729348c7ab12c84b2566ed52782a4`:
1844 balanced Main/1530 CmMovement/post-BG/clock updates,1856 physical frames.
Factory `528c17f0896d79744058ea6941d41b13f2c600d832629b4141ec16b34a646179`,
Lua `05b6e7c41db900ab6bc8827ee4d83136bdd761483ba945b385af0a7a1a5ec976`.
Source50653a74/d5cbf7ba precedes native execution.

Real kind1 birth1396 at1248/136 matures1461 at1248/119. Existing retained
side-rise/wall-grip inputs collect it1757 at1249/99, positive11x4 overlap.
CmPickupC1 consumes it without native fallback, tier2/small1/erasure/cue32.
Actual score1200→2200 at1762 precedes25 completed owner updates at1788,
1249/112. No60-frame growth is imposed on the original immediate upgrade.

After that checkpoint, ordinary left descent lands1173/176 and brakes1170.
Eight measured cells show floor54/empty head across112px, with no enemy96.
Fresh Right+B reaches actual CmWeapons:016E/SP237 return consumes stock1→0,
sets State6/Timer12/Ready4. Eight actual CmDash B802/SP220→B1AF/SP222 returns
produce three6px horizontal steps,18px total. Completed Main1844/82BE/SP252
ends1188/175, size1/tier2/lives2, stock0/State6/Timer10. Immediate stock
consumption is separate from any later valid ground refill. The old long
travel's later Goomba injury is preserved as a controller negative, not a
dash failure. See `celeste-natural-flower-00bb-source-1116.md`.

## Two actual rendered scenes and wall-jump witness

Native51563 passes receipt
`f9efcbbb60a1ba69bf34e4fe0c32614319afecb410cb15533c8b6b712cac6844`.
Removing only its added `visual` field recovers the exact functional083deff
receipt. Root viewed both actual RAM PNGs: mature Flower with small Celeste,
and active earned dash. The small sprite, Flower, nearby Goombas, HUD and
scenery look coherent in those scenes. This is two-scene review, not a
frame-by-frame or whole-stage graphical claim. The visible ground gap is
the authored pit; its pixels retain the sky color.

| Scene | PNG bytes | SHA256 |
| --- | ---: | --- |
| Mature Flower, Main1461/frame1474 |2726|a963c3501ac86e203e75c59c6ff9ecdb63e4106c3080640b73eb3c6f0b7b887c|
| Active dash, Main1842/frame1855 |2401|33e5cde0336a9fdec2923e9f36a048054cee59abc8f4c5bdd3fdf4025dca69f6|

Physical OAM has two8x16 sprite columns from owning CHR742, retaining a
16x16 hero. MMC5 mode3/banks/palette/pattern bytes accompany both pictures.
Logical versus displayed positions retain the ordinary one-frame OAM lag.
The optional observer also reaches actual tier1 CmWallJump B3EF/SP220 at
Main836,306/130 with freshA+Up+Right: returnB145/SP222 changes FootPhysics0→1,
WallKick0→1, stamina high2→1 and VX0→E0. This directly tests the Mushroom's
wall-jump behavior. Neither screenshot nor state was synthesized or saved.

Root reused only existing candidate.nes/controller.lua. The two pictured PNGs
remained in memory; zero capture files, videos, actor/position/health/inventory
seeds or game-state writes were created. Installed/shared bytes remain exact and the patch guard is
clear. No helpers were used or added. Root's queue is free. All four stock
families and the demonstrated wall jump/dash now have current00bb native
coverage. Wider moves/refill/dash directions, Star expiry/protected hits,
full-stage regression, broader audio/art and cadence remain separate.
