# Battletoads current camera diagnosis — November 14

Scope: exact delivered1daca before the later Gimmick-only cf7 delivery.
Rash and Zitz remain stage-U; no full clear, repair or speed improvement is
claimed here. Root owns Mesen. All source runs use bounded zero-output roots;
native uses the existing two-file flag slot and writes no captures.

Root46929 genuine compiled menu/Select/Start and cold source calibration:

| Choice | Slot / resolved owner | Select | FmGroups | Physical RAM3 BtVariant | Starting source life |
|---|---|---:|---:|---:|---:|
| Rash |23 /33 |0 |64 |0 |47 |
| Zitz |23 /33 |1 |96 |32 |47 |

Both constructors take167 source scheduler calls to reach native1-1,
Ready1/lives2/death-timer0. Their source data lives at physical RAM3,
including ReadyBF60, variantBF61, lifeBF3C and source clocksBEE0/BEE1.
Reading these through the restored CPU debug mapping returns unrelated
bytes; the checker and native controller use `nesWorkRam` with bank3 instead.
This is an observer correction, not a game-code change.

## Ordinary controls and retained negatives

- Initial discovery factory/checker frozen in root commit592bf8dc uses the
 generic full-roster route. Its B cadence presses attack every8 donor steps.
 Rash repeatedly enters his original stationary punch, greatly reducing
 walking progress. Root85329 was explicitly stopped after6000 sourceMain
 with X239; this is an incomplete diagnostic, not a natural game crash or
 full-stage receipt. Only its verified owned child34440 was stopped; the
 ADOFAI Mesen process was left untouched.
- Root80427 bounded1200Main source trace retains Ready1/HP47/death-timer0,
 source clocks advancing and repeated punch poses25/29. It reaches239 and
 does not progress. No final stage receipt is produced at this deliberate
 diagnostic bound. No invincibility, health, terrain or actor seeds.
- Root79559 actual Downloads1daca native ordinary opening is explicitly
 bounded at1000 totalMain. Lua
 `d9d60e390ed7abaef8af967a9c15d143877cc887f5147283cc3e77b653737451`,
 receipt `4badbd487b94acba568e0984a4bb69e0cf2983860b1ef9d373b11f55cac9972e`.
 At1388physical frames/1000 completedMain,728 genuine BtCoreStep calls,
 Rash is217/Y176/HP47/lives2. Its false stage result is expected at the
 observation bound; this run establishes the actual menu/source state and
 slow generic-control behavior, not a completed stage or hardware idle rate.
- The root factory then changes only the test controller's attack cadence:
 B is requested at most2 of32 donor steps when an enemy is within48px.
 It preserves ordinary walking elsewhere. Root23888 reaches239 quickly,
 but remains there while jumping through8500 completed sourceMain, HP47.
 This separates the camera defect from the earlier test's attack spam.

## Camera handoff defect

Root90630 runs260 ordinary sourceMain after the real Rash constructor:
Right for180, then Right+A. Native snapshots show:

| CompletedMain | World X | Y | Player_X_Scroll | Player_Pos_ForScroll | Camera left | ScrollLock / side timer |
|---:|---:|---:|---:|---:|---:|---|
|80 |179 |176 |0 |0 |0 |0 /0 |
|120 |239 |176 |0 |0 |0 |0 /0 |
|180 |239 |176 |0 |0 |0 |0 /0 |
|200 |239 |111 |0 |0 |0 |0 /0 |
|230 |239 |127 |0 |0 |0 |0 /0 |
|260 |239 |176 |0 |0 |0 |0 /0 |

Lives remain2. `Player_Rel_XPos` tracks179/239, so a valid pre-step screen
position exists. Actual current BtImportNative/BtExportNative never publish
the native scroll delta or scroll-position cache. Native ScrollHandler reads
both, leaves the camera at0, and the offscreen boundary clamps X239 even in
midair. This is a real functional scrolling defect; no new helper is proposed
to conceal it.

The source-only helper is now researching a small import/export bridge with
exact result/carry preservation. Current BT_CACHE_HOST isAD9C..B5E6,
including live status/lives code after old BtUnavailableB546. B548 is live
code and must not be reused. The original selected33 RAM3 partition and cold
copy cover the later tail; exact unused bytes/aliases, helper size and caller/
IRQ contracts must be verified before Root grants placement or a candidate.
No cache, instruction, ROM, cookie or geometry change is qualified here.

The new Gimmick cf7 remap changes192 other bytes only. Existing1daca factories
stay strict; future Battletoads work must explicitly normalize cf7 through
the frozen Gimmick inverse or add a preserving typed composition. Do not
silently accept changed ROMs or install a1daca-based private child overcf7.

## Root-funded camera proposal

Root58825 independently verifies12288 additional prefix cases with every
valid initial status combination (unused bit5 fixed1), eight low-byte corners,
both player slots and signed wrap directions. A/X/Y/SP and all architectural
flags match; only the intended camera fields change. Root also repeats24
actually reached unmasked IRQ and24 busy-NMI cuts, minimumSP177. Receipt
`a45e85227263d30f05e94928b63531353d04eac509a701263521e0c0540a9f8e`.

Earlier57309 deliberately exhaustive raw-status input also included impossible
unused-bit5-zero values and stopped at that artificial mismatch. Root5161
isolates it: PHP/PLP normalizes only unused/B copy bits, while I/D and real
flags retain their values. Valid U1 cases differ only in nonarchitectural B
copy, as the frozen research matrix already specifies. No proposed game
instruction changed to bypass a live flag failure.

Root grant `allocations/battletoads-camera-handoff-1114.json`, SHA256
`a6cf8e2291c92d03077cdf6b5172d0f2a8876ae74562fc2cccbceeadb3db92bf`,
now authorizes the exact40 cache bytes plus12 existing cookie digest bytes
over currentcf7, in memory only. Native physics, palettes, sprites, health,
helpers and levels remain exact. Candidate composition/cold transport and
full-route qualification follow separately; this is not an installed repair.
