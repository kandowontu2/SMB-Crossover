# Arthur foreground admission optimization

Private candidate `build/arthur-auth-fast-1101-v2/candidate.nes`, SHA256
`d14c5b2ee0653168240f6edda188f50841b71c9958724ad4ddcf3181dcca2c98`.
Based on installed Metal v41 (`27dee145...7318`). Not installed by this agent.

## Current evidence

The controller-only baseline selected Arthur through the actual menu and ran
120 physical idle frames, then 120 walking frames. It observed 1,200 complete
cookie checks per phase: about 15 per foreground update. Repeated admission,
rather than the original actor's movement calculation alone, is a significant
part of the cost.

| Measurement | Baseline | Candidate |
|---|---:|---:|
| Idle mean foreground-loop elapsed cycles | 34,516.68 | 32,629.67 |
| Walk mean foreground-loop elapsed cycles | 34,883.65 | 32,998.20 |
| Completed idle updates /120 physical frames | 80 | 80 |
| Completed walk updates /120 physical frames | 79 | 79 |
| Source steps per phase | 40 | 40 |
| Final world X | 160 | 160 |

The loop measurement includes interrupt time. The roughly 1,887-cycle / 5.4%
reduction is real in this same-controller observation, but does not produce
60fps or remove Arthur's remaining lag. Draw timing changes with the shorter
loop; do not sum nested service spans or label their totals pure CPU time.

## Implementation and resource proof

Every one of the sixteen header bytes remains checked in its original order,
before any cache execution. The foreground check now uses immediate comparisons
instead of an indexed loop. NMI's independent full-cookie check is untouched.
No validity latch, source-clock reduction or new RAM allocation was introduced.

The exact archived current `own-services.s` was assembled first and compared
byte-for-byte against the installed 768-byte physical-bank-70 owner interval.
Within that same interval, removing six dead incoming policy scratch copies,
two redundant read/write pairs, factoring policy pointer setup and sharing a tail recovered
106 bytes. The 105-byte check continuation occupies C-view `$DF10..$DF78`.
Its A-view storage is `$BF10..$BF78`; `$BF79` remains unused. Existing public
table, menu-name, clock and component-end addresses remain fixed. The ordinary
foreground check changes only `$C7B9..$C7E2`. Other characters' resources and
Arthur's cache/header/graphics data remain unchanged.

The dropped temporary copies are overwritten before any policy reads them.
The removed R0/R1 stores wrote their existing values back. Final memory and
register contracts are preserved; intermediate ordered write streams are
intentionally different and are not claimed identical.

## Verification

- 1,224 actual public policy-call comparisons preserve AXYP, non-stack native
  RAM, every WRAM bank and mapper state, with valid and all sixteen corrupted
  header positions. Valid policy calls save 159–171 cycles.
- 1,530 direct full-predicate cases cover constructor/menu paths, ordinary
  checks, incoming flags, and multiple bit corruptions at every byte position.
- 294 actual IRQ/lag-NMI cuts cover 147 reached changed instruction boundaries.
  Foreground AXYP/PC/SP, live stack, all 33 SMC bytes, mapper state, scratch and
  all WRAM are retained. This fixture has no active source-clock mailbox;
  native tests separately exercise the real source clock.
- Actual cold menu/idle/walk launches pass before and after the change.

The first-enemy/first-pipe controller under
`build/arthur-auth-fast-1101-v2/terrain/` fails at world X239 without losing a
life. The end image shows Arthur at the right screen edge, with the camera not
following; the controller never reaches its X385 jump trigger. An unchanged
baseline comparison is prepared under `terrain-baseline/` before assigning
this failure to the optimization. Paired early jump/fire checks are prepared
under `actions/` and `actions-baseline/`. Full 1-1, upgrades and a broader
Arthur gameplay review remain open; do not present the terrain attempt as a pass.

Outputs are bounded: no video or frame sequence; at most two screenshots per
native run. The root owns emulator launches and nightly delivery.

## Camera successor

Private `build/arthur-camera-1101-v3/candidate.nes`, SHA256
`23cbd0a389dfa869b70dc61fa2b613e72d2423bbae78e2b81dd8706dea91ebfe`,
retains the authenticated optimization. The installed baseline also failed the
unchanged terrain controller at X239, confirming the camera block predates v2.
Arthur's movement ingress now publishes
`lowbyte(Player_X_Position - ScreenLeft_X_Pos)` to `Player_Pos_ForScroll`
before movement. Native scrolling and terrain parsing remain the owners of
camera progression. No helper or new RAM allocation was introduced.

Two own-service fallthroughs and a shared transport high-byte store recover
exactly nine bytes for the nine-byte publisher. Normal and probe dispatch retain
their different high bytes (`BF01` and `B9BE`). All 248 changed ROM bytes lie in
the existing physical-bank-70 `BD00..C000` own-service interval. The 105-byte
authentication continuation, menu name, clock workers and externally referenced
entry addresses retain their bytes/locations.

`camera-CPU.json` records 252 genuine FarCallCommon/table transport comparisons,
1,536 camera arithmetic cases, and 78 IRQ/lag-NMI cuts across 39 reached
normal/probe transport boundaries. AXYP/PC/SP, live stack, mapping and WRAM
contracts pass; the intended movement-only native camera byte is accounted for.
`CPU.json` repeats all 1,224 policy and 1,530 full-cookie comparisons against v2;
`ISR.json` repeats 294 policy/authentication interrupt cuts on this exact hash.
These are source CPU checks, with an inactive source-clock mailbox in the
interrupt fixture.

The unchanged controller packets are ready under `terrain/` and `actions/`.
Run each through the bounded wrapper, for example:
`python tools/audit/run_bounded_build_v1.py --output build/arthur-camera-1101-v3/terrain --resume -- python build/arthur-camera-1101-v3/terrain/run.py`.
The root ran both packets on the exact v3 hash. The unchanged terrain controller
now reaches X429 with camera scrolling, minimum Y144 and lives 2→2, then remains
at the first pipe. Its single A pulse began too early at X385. The unchanged
action packet passes at X142, minimum Y126 and lives 2→2. The terrain profile
records 40 source steps per 120 physical frames (20 Hz source cadence), with
80 idle and 79 walking foreground loops (about 40 Hz).

The controller-only successor `terrain-double/` starts at X409, holds A for six
physical frames, releases it for twelve, then holds it for nine. The root ran
that packet successfully: X522 after 1,104 total physical frames, minimum Y112,
two consumed jump edges, and lives 2→2. This verifies the first-pipe crossing
with Arthur's existing authored double jump and the camera fix. No helper was
added or needed for this crossing. It is not full 1-1, upgrade, full attack or
hardware qualification; the candidate remains private and uninstalled.

`full11/` is a prepared full-stage discovery packet on the same hash. It reads
the native metatile buffers and enemy positions, starts obstacle jumps with
terrain 40 pixels ahead and gap jumps with missing ground 24 pixels ahead, and
uses the proven two-edge A sequence. B pulses for 12 physical frames and releases
for nine. It does not seed outcomes or player, source, terrain or helper state.
The pass condition requires all four opening pipes, all three gaps, and actual
1-2 gameplay (`WorldNumber=0`, `LevelNumber=1`, engine 8, mode task 3) without
losing a life. Its limits are 9,500 total physical frames, 240 host seconds, four
PNGs and one compact trace sampled every 12 physical frames. This was the
initial discovery packet; its negative and the later passing successor are
distinguished below.

## Full-stage discovery and death progression

The root's original `full11/` run passed all four opening pipes and two gaps,
then fell into the third stair valley at X2476. The trace shows the climbing
double jump peaked before the valley; `full11-stairs/` is a controller successor
that uses single jumps to settle on the left peak, then doubles across. No
helper has been added. The original failing run and its 12-frame trace remain
intact.

That original run also exposed a separate death defect: engine 11 remained
active for more than 5,400 physical frames without losing a life. The root's
independent `pit-death/` replay intentionally walks into the first pit using
only controller inputs. After 600 physical frames in death it still had no
restart: 600 calls each to `ArHostNativeDeath` and `NativePlayerDeath`, maximum
`MmDeathAge=0`, `MmDeathPit=1`, `ArDead=1`, high Y page 2 and TimerControl 247.
This is a genuine lifecycle defect, not a passing route or a seeded fixture.

Arthur delegated death to `NativePlayerDeath`, whose movement path repeatedly
re-enters `MegaManCheckPit` and reloads TimerControl FF while below the room.
The existing guest pit hook expects the timed `MegaManDeathUpdate` consumer.
Private `build/arthur-death-1101-v4/candidate.nes`, SHA256
`9071233dc68d49363d8e19219d36ab79642c73bf0e1f3dd3207e3d1b5ae76963`,
changes only three immediate bytes in Arthur's existing bank-63
`DF7F..DF92` death farcall leaf to that worker. Its previous 19-byte source
reproduces the old leaf exactly. No shared hook, new state, cache, camera or
physics change is made.

The v4 CPU receipt passes 1,272 actual HuDeath updates across eight sequences:
the native worker reaches engine 6 at 150 pit or 168 ordinary death updates.
Sixteen IRQ/lag-NMI cuts across all eight reached leaf boundaries preserve the
foreground ABI, live stack, SMC, mapper state and WRAM. This CPU fixture seeds
death context; it does not replace the separate native controller-earned
pit/life/restart qualification.

In the baseline pit CSV the 12-frame samples cycle through TimerControl
F9→FD→F1→F5 while engine 11 remains active and low Y advances slowly into page
2. Together with the actual source's F0 threshold and FF reload this identifies
a 16-Main reset cycle; the CSV is not a per-instruction timer-write trace.

The root ran the unchanged controller-earned pit packet on v4 successfully.
It recorded exactly 150 calls to both `ArHostNativeDeath` and
`MegaManDeathUpdate`, maximum death age 150, and lives 2→1. After 2,500 total
physical frames (374 after the initial engine-11 observation), native gameplay
has resumed with engine 8, TimerControl 0, high Y 1/low Y176, `ArDead=0`,
`MmDeathPit=0`, and `DeathMusicLoaded=0`. The observer also requires 60 physical
frames of resumed rightward movement after the actual next-life parser and
entrance. This qualifies pit death, one-life handoff and next-life control on
the exact v4 hash. Ordinary enemy-caused fatal death is covered only by the
native timer-worker CPU sequence, not a controller-earned native replay.
The root's v4 `full11-stairs/` run passes on that same hash: 6,108 total physical
frames, 5,608 play frames, all four opening pipes and all three gaps crossed,
maximum world X3264, camera X3119, and actual 1-2 gameplay (world 0, level 1,
engine 8, mode task 3). Lives remain 2→2 and the maximum consumed jump count is
two. This qualifies ordinary 1-1 completion with controller inputs and Arthur's
existing double jump, with no helpers. The captured third-stair crossing and
1-2 entry show native scenery and coherent Arthur sprites. The run stayed
within its four-PNG capture budget.

These native results belong to v4, based on the installed-at-start Metal v41
baseline. They do not qualify a later composed or Downloads ROM automatically.
Root owns composition into newer installed roster updates, exact-byte delivery,
patch-guard checks and Downloads-context verification. No install or Git commit
was performed by this agent. Upgrade coverage, native enemy-earned fatal death,
broader attack review and extended cosmetic review remain open; this pass does
not claim zero lag or 60 Hz.
