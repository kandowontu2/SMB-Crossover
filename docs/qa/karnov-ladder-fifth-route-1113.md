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
