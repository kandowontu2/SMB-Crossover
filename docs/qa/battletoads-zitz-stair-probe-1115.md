# Frozen Zitz stair negative and passive observer — November 15

Status: **native cause unresolved; candidatebc5 must not be delivered yet**.
No game-code, controller decision, endpoint or physics change is proposed here.
Root alone owns Mesen, physical candidates and delivery. The HotNew118 C/F,
old Zitz6334 controller and source qualifications remain frozen.

## Preserved actual-native evidence

Exact private candidate:
`bc5e275d1dd4dabab4b5b2def66f7643ae46aee17a31ab37887528b791594040`.
Original Zitz LF controller:
`6334b3e385ef93f56d482c834d59c30137d5169a5e832eb8609ed77af0186870`.

Root43350 Rash passed native full1-1 and25 living grounded1-2:
4,254 Main/4,644 physical, HP39/lives2, variant0, receipt
`ba148da382877f4192d40f7cf548be3bf15e4c2560d5448ad2d7716db50d138f`.
The separate Zitz run failed with `bounded-route-timeout`:10,000 Main entries
=returns/10,322 physical, alive HP39/lives2, variant32, x2178/y128/state0,
source pose45, area1/level0, no flag/full/next-area evidence. Receipt
`eae3a901a9aa0cb9e0d1b227093d96ed475146e7795575181ba05e142c587d86`.
Positive source full routes do not close this hardware negative.

Root71185 reran the **unchanged** Zitz6334 and reproduced that exact receipt.
Only root's output printer exposed existing checkpoint data:

| World X | Main | Physical frame | Native state |
|---:|---:|---:|---|
| 257 | 412 | 454 | grounded |
| 512 | 1260 | 1330 | airborne, Y143 |
| 769 | 1419 | 1525 | Y114, HP43 |
| 1024 | 1559 | 1695 | grounded |
| 1280 | 1686 | 1852 | grounded |
| 1536 | 1871 | 2071 | grounded |
| 1792 | 2082 | 2329 | grounded |
| 2048 | 2547 | 2856 | grounded |

First active is Main293/frame317/HP47. Actual Select occurs frame131 from the
base variant0 to terminal variant32. Checkpoints alone expose no requested or
consumed input at2178, so they do not establish a jump, terrain or game defect.

## Read-only source finding

The frozen BT factory removes the SMB1 alternate's separate stairPhase wrapper.
Its unchanged generic policy tests `Player_State==0`, `not lastA`, obstacle /
support / nearby enemy / still>16. `lastA` is `btHeld`, sampled from global
SavedJoypadBits at BtCoreStep entry; decisions run after completed Main.
The actual adapter loads SavedJoypadBits into CPU A before `JSR BtCoreStep`,
runs original source physics, then exports its Z-floor to native state.

Requested A versus actual worker A, source jump/ground state and actual tile
queries must therefore be observed separately. A missed one-update pulse,
input-clock mismatch or an eligibility/terrain condition is a hypothesis only.
There is no justification for a game patch, helper actor or control change yet.

## Exact passive observer

New factory: `tools/audit/replay_battletoads_zitz_stair_probe_1115.py`.
SHA256 `5ef661256cfb35c7eda5d0c31db6bd10a86a266e594b8639acac53c9448e41a7`.
API `controller(exactbc5)` returns LF Lua
`1050a790d7951b71a382a58495a1c670e36cf2c34e3493f93ee03fb07ace0da9`.
It refuses parent67, dirty/truncated and unknown images. It pins the frozen
HotNew F source and original6334 text before adding read-only observations.

There are at most **eight specific witnesses**: three first stair decisions,
four recent decision transitions and one optional first stair A/Saved mismatch.
At most32 aggregate groups and scalar counters are retained. No per-Main/frame
state arrays, OAM/PPU dumps, images, files or game-state writes are added.

Actual code authentication and source transport:

- RAM3:AED2 entry, physical work offset28370,
  bytes `8EF8BE4C94A020E6`.
- Actual caller AEAD is the single `JSR AED2` in BtMovement.
- Actual worker return AEB0, physical work offset28336,
  bytes `209EAF68850A6885`, directly before BtExportNative.
- Each entry reads the actual stack return word, checks AEB0, then acknowledges
  return only at that mapped PC with SP=entrySP+2.
- Full unchanged cache SHA256:
  `8605ac5665158653b677e7e12f44f712afb9b003c9d8a7998a632aeaedaf5c66`.

Witnesses record requested/applied A, actual worker CPU A versus global Saved
and btHeld, native movement/contact state, source Zpos/speed/floor/flags and
FrameCounter/Even before and after the acknowledged worker, policy phase/
jumpAge/still, and the actual front/support tile values. The source player
slot is actual worker X; global source clocks are not accidentally indexed.
The source fields read physical RAM3, not the current nesDebug bank alias.

The original choose call still executes exactly once at its original completed
Main point. Original setInput calls, success condition and16,000-physical /
10,000-Main timeout are unchanged. The observer does not return a substitute
clear or infer game success from diagnostic data.

## Source qualification and limits

Bounded source22858 terminated PASS, receipt
`00d44e79844c94ac9a27740e44c147912262455279a4ce34b6ad7ae801273e4e`.
The actual callback harness authenticated2,863 worker entries=returns, matched
the original source route's Main4003/flag2805/castle2868/entrance3406, HP43/
lives2, x40/y176 and25 living grounded1-2 updates. Original source controls
and route milestones remain identical. Source A/Saved mismatches were zero;
this scheduler does not reproduce arbitrary hardware NMI interleaving, so
neither the source positive nor that zero count establishes the native cause.

The initial16-witness metadata prototype was superseded before native use by
the final eight-witness observer. It produced zero files and no emulator run.
All tests used absent `build/battletoads-zitz-stair-probe-1115`, max-files1,
600 seconds, stdout aggregate only. The root was absent after terminal source
qualification. No helper Mesen, candidate file, Downloads modification,
installation, patch or release occurred.

Root may run the frozen passive observer next. Keep both original native
negatives and all old factories unchanged while reviewing its actual evidence.
