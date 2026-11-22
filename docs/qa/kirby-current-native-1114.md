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

Separate Mesen fixtures verified the Star and 1-UP effects after staging the
items. Natural pickup tests for both items are still open.
