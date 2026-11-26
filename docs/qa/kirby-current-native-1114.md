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

## Current-byte shell pool regression, November 26

The installed `83b38793` ROM passed the new
[`check_kirby_shell_slots_current_1126.py`](../../tools/audit/check_kirby_shell_slots_current_1126.py)
linked CPU regression. No new inhale-damage or shell pass-through defect was
demonstrated, and no game bytes changed. The earlier directional inhale,
grounded green hit and red catch native receipts above retain their versions.

The current PRG74 hash is
`ba13d6e1c5ea9f8c4ce293fec5e4d3048ad72f8c7cd244b8ad370a7b45ce7a66`.
It differs from the older `119a6fe4` bank by the delivered eleven-byte needle
cue change and two shared Sonic body spans: 64 bytes at ABDC and 49 bytes at
BF03. Restoring their typed original preimages in memory recovers the complete
older bank hash. All other bytes are exact, including Kirby's inhale, shell
rectangle/sweep and red-catch repairs. The fixture executes the actual current
ROM, including its relocated native PauseRoutine at 8359; restored bytes serve
only to authenticate retained metadata.

Four copies are earned with inhale and Down: green/red in both facings. Three
actual source allocations then populate each projectile slot, and a fourth
allocation preserves the full pool. Across 36 cases, twelve page-one targets
take the actual native defeat and only the selected shell is consumed. The
other two shots survive. All 108 observed shot updates advance exactly three
pixels with zero horizontal fraction. Twenty-four synthetic off-page targets
are rejected. Kirby retains six HP, two lives and the earned copy.

These are flat-scene and NPC-data fixtures. Direct source attack/shot calls
bypass input cooldown to isolate slots 0, 1 and 2; they do not establish a
natural three-shell route or new Mesen coverage. Initial authentication failures
were stale metadata: PRG74 also contains the later Sonic body ingress, and
Contra Force moved the common pause entry. The first hit fixture placed the
target three pixels beyond rectangle overlap; correcting the NPC placement
left the native-hit assertion intact. No gameplay patch followed those failures.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/kirby-shell-slots-current-1126 --max-files 1 --timeout 600 -- python -B tools/audit/check_kirby_shell_slots_current_1126.py
```

The final bounded run exits zero and creates no files or captures. Receipt
`4c22f792c75dbd9f21f1163a37184707dc915d7c4844b37ff9560eabb41fc818`;
source `fdf8b4579bdb94c2d673845326ef5f3f844b775f44e815fd34904fd6110ed046`.
The generic non-shell spit Y-page concern remains separate and fixture-only
as documented in [inhale safety](kirby-inhale-safety-1113.md); no naturally
reachable witness has been established here.

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

### Buzzy Beetle guard

The Mesen replay on `32eaf178` used the Start Level menu to enter 8-1.
Kirby stopped to start inhaling before the opening Buzzy Beetle reached him.
The Beetle spawned at X288/Y184, walked left and was captured at X195.
Pressing Down gave Kirby the Buzzy guard at six HP.

Kirby held B and guarded a real Goomba contact at X312/Y184. The native
contact handler returned protection and Kirby kept all six HP. After
releasing B he continued for 25 further movement updates with both lives
and the copied ability. The replay took 1,143 physical frames and created
no captures.

- Receipt `b9eaa4f3e4bbbde8197ac7dc768394084c31d93dd0ca4e9f1fa6b6714ab9370f`
- Controller `ae588b542ca0b9b0bf75f4d51329a18662d22dd1400b85b73bc21cdca053d5de`

### Discard, recover and reuse the Goomba copy

The `copy-recovery` replay passed in Mesen from the Downloads nightly
`59e1a591`. Kirby inhaled the first Goomba in Easy 1-1 and swallowed it.
Select discarded the charge at X298. The copy star rose from Y196 and
bounced off the ground at X318/Y200 after 40 game updates. Kirby inhaled it,
pressed Down to recover the same charge, and then crossed the first two
pipes. He used the recovered charge to defeat another live Goomba at
X712/Y184 and kept six HP and two lives through 25 more updates.

The replay used ordinary controller input with cheats off. It took 992
physical frames and produced no captures.

- Receipt `cbf1d46a9347c47c396045d7a15c9f9f103a8ed37be5b9db8eebe3a33b28956a`
- Controller `40224a77cb6a401cd2e68a32db47012138f8149ebc23288d6f557686ff499968`

### Spiny needles and the launch sound

In 4-1, Kirby inhaled a live Spiny thrown by Lakitu, pressed Down to gain
the needle copy, and launched a needle fan to defeat a second Spiny.
Easy and Hard both passed with six HP and two lives through 25 additional
weapon updates. The replay used Start Level to select 4-1, with
invincibility off and ordinary controller inputs throughout the encounter.

A second B press exposed an audio bug on `ae28a3ec`. One needle from the
first shot still occupied a slot. The second press launched two needles
and left the sound queue empty. The native failure receipt is
`43541fd51031fa7e9e713bc9ed0239ace96001f99fe6bcce8815edf9d6061bc0`.

Nightly `2f1e4b8d` queues the launch sound after a needle is created, so
one or two available slots still produce a cue. The 32 linked CPU cases
cover every three-slot occupancy pattern, both facings, and two initial
sound-queue values. Every successful partial fan queues the cue. A full
pool keeps the previous queue. The projectiles and other checked gameplay
state match. The full fan costs up to 12 more cycles on its launch update.
Linked receipt `63a15a25334e4f06ee3deb3be4a7a8e63cb31ef82f001c258832f544a07f4bae`.

| Controller replay | Video frames | Native result receipt |
| --- | ---: | --- |
| Easy, capture and full fan | 2,084 | `6dc188e2e47a2a5ee83b03cdbb2399059466ea53ecb80d033853b995070df1a4` |
| Hard, capture and full fan | 1,982 | `0059ff95a40d0283b718bff3ed57dbfa9560fbafcf53cdd850fd7efd7477bd4f` |
| Easy, partial fan and sound, also from Downloads | 2,084 | `cded8f0d48c09210e954b869560379b546424f416e123265e26190f6fac5ac7f` |

On the partial-fan replay, the actual guest sound routine processed the
first cue at frame 2,009 and the second at frame 2,042. The Downloads ROM
matched the tested candidate and the replay receipt. No captures were
written. The four earlier inhale and two shell controller hashes still
match after accounting for the separate Sonic routing bytes and this
needle-only change. Their prior passing results carry forward.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/kirby-spiny-audio-source-1123 --max-files 1 --timeout 140 -- python -B tools/audit/check_kirby_spiny_sound_1123.py
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 8 --timeout 575 -- python -B tools/audit/replay_kirby_spiny_native_1123.py --install
```
