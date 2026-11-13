# Karnov stock fifth-item route, November 13

This is controller development on unmodified stock image
`526ef1df172c3172fccbd35aa0471a9ff9a5a256a416acba8f7530d147a5b3f2`.
The public Ladder implementation and its strict composer/inverse are unchanged.
No Mesen run, ROM/data patch, native-state grant, new allocation, or generated
output is part of this helper's work.

## Inputs and ownership

- New binder/CPU runner: `tools/audit/replay_karnov_ladder_fifth_1113.py`.
- New controller suffix: `tools/reference/karnov_ladder_fifth_1113.lua`.
- Frozen four-item controller: `replay_karnov_ladder_stock_1113.controller(raw,
  wait_for_entry=True)`, SHA-256
  `00187419e40f04b1d60f16792a1359ffae1caea4614f6d6ae30d3ff8c20e0f62`.
- Root owns the Mesen queue, public delivery, shared helper inventory and the
  frozen four-item replay. This work does not edit those files.

The frozen prefix already has root's actual native stock proof: 12,915 physical
frames, four ordinary items, original Boots activation/expiry, Bomb use and
retirement, full 1-1 and grounded 1-2, healthy with both lives. Receipt
`a16cfb29945b938e4d1af9e13b1f06260b036c98802b7ac9a373585230df5a15`.
The private DATA-only five-item fixture has separate native proof
`9015fad6c7c7e690044a92bca33a104cda6325e59d3e61b0a8cffd8f798162ba`;
that fixture was never installed and does not establish this stock route.

## Stock item census

The current native small-object streams decode as follows. Coordinates are the
authored block's world-pixel left edge and top, not the emerging item's pose.

| Stage | Ordinary powerup blocks | Stream |
| --- | --- | --- |
| 1-1 | 336/144, 1248/144, 1744/80 | `L_GroundArea6`, file offset 20956 |
| 1-2 | 160/144, 1104/128, 2400/128 | `L_UndergroundArea1`, file offset 22403 |

The retained prefix collects the first two 1-1 blocks and first two 1-2 blocks;
it skips the high 1744 block. The new target is the authored 2400/128 block.
The stream census alone is not native parser/collection proof for that target.

## Development evidence and limits

One unbroken actual Main/NMI CPU replay reached four genuine native collectors
in 11,000 updates, with full health and two lives. The fourth collector was at
epoch 7044, player 1116/91 and mature flower 1104/103. Boots had genuinely
expired: stock zero and inactive. The selected Bomb was then used and retired.

The initial new suffix stalled at player 1557/176. Actual actors showed a
Piranha Plant (ID 13) at 1656/136. The old controller's ground-enemy override
kept crouch-firing below it. This was a controller targeting error; it did not
demonstrate a ROM defect. The new suffix excludes that pipe-top enemy from both
of its crouch-shot overrides and retains ordinary pipe/jump control.

Three in-memory forks from that genuinely earned four-item state tested only
ordinary input. Standing fire and an immediate jump reached the first pipe's
wall at 1633; the immediate A edge was consumed while exiting the prior crouch.
An Up+Select fork created the existing native girder in slot 1, stage 1-2,
left 1549, center 1565, initial top 208, width 32, and carried Karnov upward.
That exploratory placement is not a final proposed stock-route helper.

Further suffix forks restore only Lua observer/controller history alongside a
copy of the genuinely earned CPU model. No native/source gameplay field is
changed. They are development probes and cannot establish a final unbroken
replay. A final controller-only run from the normal menu remains required,
followed by root's independent native verification.

The first timed-pipe fork cleared the 1656 plant after observing its actual
fully-down Y160. At the next plant, X1752/down Y144, the ordinary jump reached
the wall at player1729/176 without injury. The subsequent assisted fork used
the existing vertical girder: slot3, left1714/center1730/top208/width32,
108 observed carries and player176 to80. It crossed the second and third
plants with unchanged health/lives. This fork had backed from X1729; the final
route's observed placement must be recorded independently.

That fork then failed at the stock moving-platform pit, player2313/Y209,
engine11. It still had four earned items, triple shot, inactive/empty Boots,
used/retired Bomb, full source health and both lives before entering death.
The current controller development uses the already delivered Down+Select
horizontal girder for this crossing. Its native actor is `$28`/40 with state
`$42`/66, whereas the vertical actor is `$25`/37 with state `$41`/65. The
horizontal helper has an initial right-side left edge of playerX+24, center
left+16, initial top playerY+32, width32 and original112-pixel travel. No new
ROM helper is allocated.

An exploratory fork initially chose a farther Piranha because it iterated
native slots rather than choosing the closest forward plant. The new suffix
now chooses the nearest eligible plant. This was a controller error and did
not require a runtime change.

The first bounded development process reached its600-second lifetime after
returning these branch results. The wrapper stopped only that owned process;
there were zero disposable output files. The next bounded process advances
the same unbroken ordinary prefix to the pit before retaining its model.

Active output budget: bounded root `build/karnov-equipment-1113`, maximum one
file; tests currently create zero files and no output directory. Long stock
CPU work uses root's explicitly authorized 600-second timeout. No captures.

## Checkpoint: separate early route

After the late route's further controller negative (healthy X1687/176,
timed-pipe bound while the new ground-enemy clear paused movement), root
directed work to the skipped third 1-1 question. The late route is exploratory
and has no complete CPU or native pass. Its process was closed normally.

New source files `tools/audit/replay_karnov_ladder_early_1113.py` and
`tools/reference/karnov_ladder_early_1113.lua` build a separately named readonly
controller. Planned earned sequence: 1-1 mushroom336, flower1248, high
flower1744; then 1-2 flower160 and flower1104. Those later three would earn
Boots, Bomb and Ladder respectively. The source requests the existing
Up+Select girder below the high question, requires a fresh original jump for
its actual native head, and uses native preparation/maturity/collector
observations. No source/gear/health/position/actor fields are granted.

At this checkpoint the bounded early-route process is still computing its
genuine two-item prefix to X1680. Its high-question reveal/collection, later
items, final unbroken route and root native run are **pending**. The new
controller includes strict sound/popup/erasure/progression checks and final
physical PPU pattern/attribute restoration checks; these are assertions to be
executed, not passing evidence at this checkpoint.

The input adapter continues to return only frozen526. If Downloads has advanced
to exact Prince7ef2de35, it uses the explicit authenticated
`compose_prince_entrance_current_1113.reverse` to reconstruct526. Unknown ROM
identities reject. This does not relax either the strict feature proposal or
the readonly controller's526 input pin and is not a native7ef stock-five claim.

## Completed finite early approach sweep

`replay_karnov_ladder_early_1113.py --sweep-high` completed normally in one
bounded process, with one genuine two-item prefix (2347 Main updates,
player1680/176) followed by nine in-memory controller forks. It authenticated
actual Downloads7ef through the exact inverse above and tested frozen526.

| Adjacent native player X | Carry native Y values | Main updates per fork | Result |
| --- | --- | --- | --- |
| 1720 | 64, 80, 96 | 381 each | No native C1 head, no third item |
| 1724 | 64, 80, 96 | 385 each | No native C1 head, no third item |
| 1728 | 64, 80, 96 | 389 each | No native C1 head, no third item |

All nine ended healthy, source damage0/lives2, original shot2, cycle0 and no
equipment grant, at player1737/179 after the finite lower-block landing
assertion. The aggregate remains a **negative**, not a full route pass.
Native block-buffer observations confirm C1 at1744/80, C0 at1744/144 and
clear adjacent columns1712/1728/1760/1776 at64..128. The traced helper was the
existing native vertical actor in slot2; no fixed helper or ROM change was
made. These exploratory CPU-only placements are not new native-qualified
inventory entries.

The trace passes through player1737/Y52 with native grounded0, then the side
response moves him to1729 while the girder carries him down. The original
selector23 at the end of those updates does not alone establish a support
defect: the existing ground bridge reconciles the earlier native support
before the next original source update, whereas BG collision precedes the
later native platform carry. No runtime patch is justified by these traces.

The incoming-A suspicion was checked against the retained owning source and
its authenticated live bridge bytes. BFCB starts immediate far-target
construction (`A9 78 8D 6C 01 ...`), so it overwrites entry A before any read.
Its8B:B378 worker starts PHP/TYA/PHA then loads KrHeld. BFC5 stores its own
caller-supplied A2 to C08B and jumps to KrPostTerrain; the caller supplies A2
in movement's grounded setup before the later options/Ladder dispatcher.
This supports retaining the public code; it is not a new interrupt/ABI gate.

Both exploratory memory servers were bounded and retained zero files. A final
400-update probe in the first early server was interrupted by its600-second
lifetime and has **no result claim**. The later nine-case sweep above exited
normally. No process or Mesen instance from another task was touched.

Next useful ordinary-input probes are lower takeoff heights112/128 or an east
approach. A real high-question head, mature third flower/Boots grant, later
Bomb/Ladder, final uninterrupted run and root native replay remain pending.

## Lower takeoff result

The completed nine-case table above is pinned by source checkpoint03b74a8c.
The subsequent `--sweep-lower` changed the controller to hold A through the
attempted impact and retained the first40 motion samples instead of the last
32. It completed normally after one genuine2347-Main two-item prefix:

| Adjacent X | Carry Y | Fork Main updates | Actual result |
| --- | --- | --- | --- |
| 1720 | 112 | 381 | Healthy negative, no head/third item |
| 1720 | 128 | 156 | Real native C1 head at player1737/Y87 |

The sweep stopped at its first successful head, so the other four lower
combinations were not run. The positive actual head callback observed tile193,
native A128, native vertical speedFF and state1, source held1 and full source
health0/lives2. Its motion starts with source fresh pressed129 (Right+A),
original rising selector8 and original air timer32, then reaches1737/87.
This is a genuine prefix-derived **CPU head component** result, with no
native/source fields granted. The current test has not yet collected the high
flower and does not establish a complete stock-five route or native Mesen
result.

Those first motion samples also confirm ordinary jumping off the girder.
The apparent end-frame source/native support difference did not prevent the
original fresh jump; there is no demonstrated runtime defect and no runtime
patch. Next, keep the measured1720/128 head approach, retain its earned model
in memory and test the existing east-side1776/Y80 girder/flower collector.

## Earned high flower / Boots component

The next actual CPU run used the measured1720/128 controls as its default.
Without a VM/history restart it reached the C1 head at Main2512, player1737/87,
and a genuine native flower in slot5, kind1/state1 at1744/72. The head callback
again saw native A128/VYFF/state1, full source health0 and two lives.

A fork of that earned head state then ran the existing generic east-side
flower route1776/Y80. After387 ordinary-input updates, the real mature flower
kind1/state128 at1744/55 was collected at player1756/43. The exact native
collector return erased the actor/preparation inventory, queued sound32 and
popup6, kept shot2, and changed cycle0 to1, selectedFF to0, owned0 to1 and
Boots stock0 to1. Health0/lives2 remained. Only the genuine observer head
history and controller pickup history were copied into the fork's Lua VM;
no cartridge/source gameplay field was changed. The runner's top-level
`passed=false` there means it stopped at the requested third collector; it
is not a complete route assertion or a third-collector failure.

Actual native constructor/carry callbacks in these CPU components observed:

| Character / alternate | Stage | Control | Initial left | Center | Initial top | Width | Observed carries |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Karnov, Rygar Select alternate / raw34 | 1-1 | Up+Select, retained first-flower helper | 1201 | 1217 | 208 | 32 | 71 through head checkpoint |
| Karnov, Rygar Select alternate / raw34 | 1-1 | Up+Select, high-question head helper | 1712 | 1728 | 208 | 32 | 71 through head checkpoint |
| Karnov, Rygar Select alternate / raw34 | 1-1 | Up+Select, high-flower east helper | 1767 | 1783 | 208 | 32 | 105 through third collector |

These are dynamic existing user controls, not new authored stage placements.
The last two are CPU-qualified components; root's native replay and shared
inventory update remain pending. Other characters/alternates are untouched.

A further3000 ordinary-input updates from the earned third-collector state
cleared1-1 and reached healthy1-2 entry40/171, state2/engine8, shot2/cycle1,
damage0/lives2. Boots stock and owned were already0; this receipt does not
prove a reset bug or regrant. Later Down+B ground combat can legitimately
activate equipped Boots, so the next uninterrupted report exposes the actual
first activation record. That memory server subsequently reached its600s
owned lifetime. No state dump/output files were retained.

The next single uninterrupted attempt uses the measured head and high-flower
collector, preserves the original west120 approach for the first cave flower
at160, then targets1104 for the fifth item. It adds strict fourth native
sound/popup/erasure/Bomb progression checks and requires the complete Ladder
PPU lifecycle before a full pass. Fourth/fifth/full/native results are still
pending at this source checkpoint.

## Uninterrupted four-item prefix and post-four negative

The next uninterrupted generated-controller CPU run reached all four actual
collectors, with strict native effects and original progression checks:

| Item | Actual actor | Collector epoch | Player | Original result |
| --- | --- | --- | --- | --- |
| 1 | mushroom413/164, stateC0 | 442 | 402/176 | shot0 to1 |
| 2 | flower1248/119, state80 | 1786 | 1250/97 | shot1 to2 |
| 3 | flower1744/55, state80 | 2898 | 1756/43 | cycle1, Boots stock1, owned1, selected0 |
| 4 | flower160/119, state80 | 6277 | 162/97 | cycle2, Bomb stock1, owned2, selected1 |

The generated Lua SHA-256 was
`590993853b33e7dc94484750e8e37fbad2eeaca73f9766adb8853f38c4135a14`.
Third and fourth returns had native sound32/popup6, erased inventory0 and
actual erased actor flags. Health0/lives2 remained throughout. The fourth
was subsequently armed, blasted and retired by ordinary Down+B input.

Boots were genuinely activated during later1-1 ground combat at epoch3145,
player1866/176, with stock0/owned0 and the source active bit set. They expired
before1-2. This directly explains the earlier empty Boots receipt; it does
not show a scene-reset defect and no equipment was restored by the test.

The full route then stalled at player530/144 on terrain, while the remaining
Goomba was behind him at464/184. The new suffix's generic abs(dY)<48 test kept
crouch-firing40 pixels above the enemy's lane. It had moved the enemy return
ahead of its local finite guard, so the outer14,000-update source ceiling
ended the run and `--require-pass` correctly failed. Terminal health0/lives2,
shot2/cycle2, empty used Boots/Bomb and no fifth item. This is a controller
targeting/bound-ordering negative, with no demonstrated runtime defect.

The uninterrupted run's actual manual helper births/carries were:

| Stage | Initial left | Center | Initial top | Width | Actual carries |
| --- | --- | --- | --- | --- | --- |
| 1-1 | 1201 | 1217 | 208 | 32 | 71 |
| 1-1 | 1712 | 1728 | 208 | 32 | 296 |
| 1-1 | 1767 | 1783 | 208 | 32 | 203 |
| 1-2 | 113 | 129 | 208 | 32 | 71 |

All are Karnov/raw34 existing Up+Select vertical actors. The different1-2
left113 here is the actual constructor observation, distinct from the older
four-item route's left112. No authored placements changed.

## Final uninterrupted source qualification

The subsequent source controller fixes only the demonstrated decisions:
both new ground-enemy checks require abs(dY)<24 instead of48, and the finite
travel guard runs before an enemy return. This lets the ordinary original
movement pass above the lower Goomba. No additional traversal platform,
runtime patch, physics change or allocation was needed.

An earned-four-prefix fork then collected the real fifth flower1104/103,
state80, at player1106/80, with native sound32/popup6/inventory0/actor erasure.
It changed cycle2 to3, selected1 to2 and owned0 to4, keeping shot2, health0 and
two lives. Its first Ladder site1248 was rejected before activation because
the authored brick row144 occupies1232/1248/1264. Readonly target1200 is a
genuinely clear stock column. A further earned-state fork passed eight-cell
growth, Up176 to154, Down/retraction, ownership return and all32 physical PPU
pattern cells plus5 attributes restored. These were development components;
the uninterrupted qualification below supersedes them as the complete CPU
route evidence.

Exact final command, stdout only:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/karnov-equipment-1113 --max-files 1 --timeout 600 -- python -B tools/audit/replay_karnov_ladder_early_1113.py --limit 12000 --require-pass --summary
```

This passed in233.18 seconds /8214 actual Main/NMI updates, with no Lua VM
restart, observer-history insertion, cartridge/source gameplay field grant,
ROM/data edits or generated files. It begins with the actual native
menu/constructor and the retained harness's60 ordinary opening updates; it is
a CPU route qualification, not a native Mesen timing/visual claim.

The five actual collector epochs were442,1786,2898,6277,7953. The last was the
real mature flower1104/103 at player1106/80. Boots activation was recorded at
epoch3145, player1866/176; Bomb was armed, blasted and retired before the
fifth traversal. Final source fields: shot2, damage0, cycle3, selected2,
owned4, Boots/Bomb stocks0, scene0. Terminal: active1-2, player1200/176,
native state0, both lives.

At1200 the original Ladder grew8 cells. Physical PPU proof observed32 glyph
cells44/45 with palette quadrant2, then original Up moved176 to154 over24
Main updates. Held Down descended/retracted; source ownership4 returned, and
all32 original PPU pattern cells and5 exact attribute bytes were restored.
Actual stock cave palette2 colors were `$21/$1c` (33/28), whereas the earlier
ground fixture had `$21/$0f`. No global palette entry was written or changed
by this work; this is the existing stage palette adaptation, not exact donor
color parity. The runtime still owns/restores only its qualified attribute
quadrants. Root should review the actual cave art during native replay.

Final uninterrupted helper callbacks, all Karnov/Rygar Select alternate/raw34,
all existing Up+Select vertical actors, width32 and initial top208:

| Stage | Initial left | Center | Actual carries |
| --- | --- | --- | --- |
| 1-1 | 1201 | 1217 | 71 |
| 1-1 | 1712 | 1728 | 296 |
| 1-1 | 1767 | 1783 | 203 |
| 1-2 | 113 | 129 | 71 |
| 1-2 | 1127 | 1143 | 82 |

These are CPU observations of ordinary dynamic constructors. Root owns the
native repeat and shared inventory update; they are not new authored helpers.
No other character or alternate is affected.

## Frozen binding for root's native queue

- Strict frozen526 factory: `replay_karnov_ladder_early_1113.controller(raw)`.
  Lua SHA-256
  `3ec55ec6041e6daef135bd736a357ca764e07f7a7d3f3358b54b829f73fdcc66`.
- Exact current7ef factory:
  `replay_karnov_ladder_early_1113.current_controller(raw)`.
  Lua SHA-256
  `7d1ea719a760ac0dedb17fedde3705d5ccfdc67d1af34018efc017f859c79091`.
- Current image:
  `7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc`.
  The adapter uses the exact authenticated Prince inverse to526. A separate
  zero-output gate compiled both scripts and proved that only the ROM identity
  label differs; all controller logic and bindings are identical. Unknown
  ROM hashes reject. Strict feature proposal/inverse pins remain untouched.

Native Mesen qualification of this full stock route remains pending. The
private DATA-only fixture and old four-item regression remain frozen and
separately qualified. This work does not claim Karnov's remaining Clapper,
Glasses, Swimming Mask, Shield, Star or1UP coverage. No public ROM/IPS change
was made by this controller task. All source tests used the bounded owned
root, retained zero outputs, and no helper launched Mesen.
