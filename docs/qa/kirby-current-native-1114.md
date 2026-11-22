# Kirby: current native inhale and shell verification

Root75507 runs six separate real Mesen launches using the installed Downloads
ROM5715bb7e3c772350a2a7420ec9061eabd948964a8789e5d348c49d3cfb3c57ee.
All six pass. The generator authenticates the entire delivered Kirby PRG74
(`119a6fe415a914c415a51bc46f0cc22569cd4c7e1282d83f512c3b2031573e9d`),
every retained RAM address and every hook preimage. Only the already delivered
five-byte capture-hook authentication is rebound in the Lua metadata.
No game code or ROM bytes change.

| Ordinary controller run | Physical frames | Outcome | Native receipt SHA256 |
| --- | ---: | --- | --- |
| Close right inhale, Easy |527|HP6/lives2, mouth7/copy1, no injury|`da29eff7eacf78d31a4b79517551aea8114b5d6b46e07f0183d1a3545f85f638`|
| Close right inhale, Hard |614|HP6/lives2, mouth7/copy1, no injury|`266411e73bbcee033c3378116762584aaa9e4eb08f4e366acad6b35e269be013`|
| Close left inhale, Easy |731|HP6/lives2, mouth7/copy1, no injury|`9b581ca685dfcfa78f4b7bd8ed1a66474f873e02da4151dca5bb82f1aba13e53`|
| Close left inhale, Hard |818|HP6/lives2, mouth7/copy1, no injury|`7063537d14484aa4b8282a061af6cb72aea273480a305dcddefebc5d3b1a42b5`|
| Earned green shell, combat and full1-1 |6296|Copy2, intended Goomba defeated, full flag/1-2 entrance, HP5/lives2|`91478ad85fc5a24ada73d590875e3e994ab5db79b3ae55a3d17dbba0f7ebe38d`|
| Earned red shell, combat and clean catch |1852|Copy3, intended RedKoopa defeated, clean return, HP6/lives2|`bbab09571b7dc7b488b5a76f5519695c6912c0180befde859d2371bc84475e20`|

All four inhale runs select Kirby through the roster. Hard runs select the
difficulty through Options; Easy runs retain the cold default. They use the
first authored Goomba; left-facing runs
jump past it, deflate, land and turn. They observe fresh B, actual capture,
native actor removal, health and injury callbacks. No actor, terrain, health,
position, ability, mouth, copy or outcome is seeded. No cheats are used in
those four runs or the green-shell run.

The green run inhales the authored GreenKoopa at player1554/176, target1565/184,
then uses normal Down to acquire copy2. A grounded fresh B at1757/176 fires at
a separate naturally spawned Goomba. Ages1..6 move shellX1776,1779,1782,1785,
1788,1791: exactly3px per weapon update, horizontal fraction0. At age6 its
rectangle[1783,190,1798,205] overlaps native[1795,198,1805,204]. The genuine
native defeat executes and the target becomes state34. This is the14-pixel
Y-origin difference that the old radius-only helper missed. The one earlier
route injury is retained; this is not an injury-free full clear. The run ends
in1-2 at40/48/state2, falling: it does not claim25 grounded1-2 updates.

The red run selects4-3 using the existing level-select cheat through normal
menu controls; invincibility stays off. It earns copy3 from the authored Red
Koopa using inhale and Down, then defeats a different authored RedKoopa with
an outbound3px/update shot. A second shot returns at3px/update and is caught
at age67, X601 versus KirbyX600. It retires at frame1852 before the89-update
expiry; there is no old oscillation. It is not a full4-3 clear.

The exact generated script hashes are recorded by
`tools/audit/replay_kirby_current_checks_1114.py`: right Easy d86a4efa…,
right Hard248c060b…, left Easy0574bce4…, left Hardab88ad92…,
green21006897…, red2e8b0e1a…. The old source factories stay unchanged.
The source header's historical observer ROM is retained; actual output ROM
provenance is bound and checked as571 by the runner.

The bounded existing two-file `build/smb2-flag-native-1113` slot is reused;
only its controller is replaced for each sequential run. Shared Mesen queue,
capture watchdog and pre/post Downloads sidecar/hash guards all pass. There
are zero capture files, images, videos, backups, patches or releases. These
results confirm the delivered reported repairs on this build; exhaustive
copy/enemy/water/pool-pressure/visual/audio coverage remains separate.

## Checks carried forward on November 22

The six tests above remain completed. The November 16 nightly has the same
Kirby code bank and the same RAM addresses and hook bytes used by the tests.
A read-only check regenerated all six scripts with identical hashes. The
November 22 Rogue Dawn change only touches her HUD lifecycle routine.

Kirby's natural mushroom and Fire Flower checks passed in Mesen on `e6b152e2`.
Both pickups came from their World 1-1 blocks and restored Kirby to six HP.
The test verified each item's graphics and the heal animation. The same
food replay still authenticates its code and graphics table in the November 16
nightly. See [Kirby's food pickup tests](kirby-natural-food-1111.md).

## All four natural pickups verified in the November 22 nightly

Two [controller replays](../../tools/audit/replay_kirby_stock_native_1122.py)
passed in Mesen from the installed `79fd089f` nightly. Both started at the
title and selected Easy Kirby. The Star route also collected the mushroom and
Fire Flower from their regular blocks at X336 and X1248. Both food pickups
played the heal animation and restored Kirby to six HP.

- **Hidden 1-UP.** A normal jump reached Y127, leaving Kirby's head probe at
  Y144, one pixel short of the hidden block's row. Jumping and holding Up to
  float reached the block at X1024/Y128. The item emerged and matured before
  Kirby collected it. The delayed 1-UP popup raised his lives from two to
  three and queued the extra-life sound. Kirby finished alive after another
  25 active updates. 2,105 physical frames, receipt
  `daf44f75fae019d9c24af652f731df2313df6c84ccb16e4acdac5d024b1ad1c4`.
- **Star.** After the two food pickups, Kirby crossed the first pit with his
  jump and float and struck the brick at X1616/Y144. He collected the mature
  Star, which set the native invincibility timer to 35, queued Star music
  and awarded 1,000 points. Both stock pickups preserved his health, mouth,
  copy ability and food state at collection. The replay continued for
  25 active updates after the score award with the Star still active.
  3,138 physical frames, receipt
  `fe72a3eb1d1dca836d3d4dc8b56e33b744b5e89ee9e7f240968509a65925b333`.

The replays used controller input and read-only emulator callbacks. They
created zero capture files and reused the existing two-file test slot.

### Star protection and expiry

The `star-lifecycle` controller replay passed in Mesen from the Downloads
nightly `a6d91e36`. Kirby used the same earned Star route and ran into a
Goomba at X1785 while the timer was 30. The native body-contact path defeated
the Goomba and Kirby kept five HP. The game called its area-music routine at
timer 4. The timer reached zero with Kirby still at five HP.

Kirby then ran into a different Goomba at X1949 and lost one HP. He remained
alive and playable for another 25 game updates. The replay took 4,048 physical
frames and produced no capture files. Receipt
`e81b0e417472227ff622cb7f110bd16201a37882ee58d4c37c362e00ede0968f`.
The full graphics, sound and lag reviews are still open.

### Goomba ground charge

The `ground-charge` replay passed on the Downloads nightly `a6d91e36`. Easy
Kirby inhaled the first Goomba in 1-1 and pressed Down to swallow it, with
six HP throughout. After jumping the first two pipes, Kirby pressed B at
X679/Y176. The native charge moved him three pixels per game update and
defeated a second Goomba at X711/Y184. Kirby kept the copy ability and
completed 25 more game updates without taking damage.

The replay took 922 physical frames and produced no capture files. Receipt
`e0e73de599f8df100f3db21bf372e54e628a90f46059210e3e83988e6a240d4a`.
Controller SHA-256 is
`48083aac951292d2af633016ed98582faf9d86d3861928a1666cf7baa8052337`.

### Spitting an inhaled Goomba as a star

In a separate Easy 1-1 replay, Kirby inhaled the first Goomba and carried it
past two pipes with ordinary jumps. He pressed B while descending at
X665/Y156. The star travelled right at four pixels per update and hit a
second Goomba at X712/Y184 on its fifth update. The game removed the shot
and defeated the enemy. Kirby kept all six HP and both lives, gained no
copy ability, and completed 25 more weapon updates.

The Downloads replay on `a6d91e36` took 911 physical frames and created no
capture files. Receipt
`79c2dc20f2617f88c360ea44c78b92460dcc82ea55d13e09b14fabc7d3799a8b`.
Controller SHA-256
`2ba8e3674b4b486d182522704d40a2094de4311ac6ee141bdea92266850a877a`.
