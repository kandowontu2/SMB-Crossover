# Final Fantasy head/side corners and pipe entry — November 10

This is a private fix pending physical Mesen verification. The public Downloads
ROM remains `c10b7d87f466bf028096bddd33b7ac2baee242870ee83ccc4eebd529af57bd7f`.
All four FF classes already start in that public ROM. Starting alone does not
establish that their movement, attacks, powerups or stage transitions work.

## Reproduced faults

The natural earned mushroom → flower → attack route repeatedly stopped at
world X 2225 in 1-1. The actor rose alongside a staircase; its right head probe
entered a new lateral column, which the FF head adapter classified as a ceiling.
The resulting vertical correction stopped every subsequent hop. The previous
14-pixel body had not overlapped that column. This requires a contact fix,
not stronger jump physics or a helper platform.

After the flagpole, the same route exposed a separate existing fault in the
automatic 1-2 side-pipe entrance. Native PRG 126:$9CFA set sprite attribute bit
$20, but FF graphics at RAM3:$B3D5 cleared it before PlayerEntrance read it.
ChangeAreaTimer consequently never advanced to the underground area. See
`ff-intro-priority-diagnostic-1110.md` for the paired instruction/write trace.

## Minimal v2 repair

`tools/reference/ff_head_corner_1110_v2.s` retains the existing movement and body.
It snapshots the previous full world X in two previously unused bytes of the
existing render scratch and excludes solid-only head probes entering a column
that the previous body did not overlap. Native side collision remains active.
Actual coin tiles $C2/$C3 bypass this exclusion and use the original reader.
The graphics reset now preserves native pipe-priority bit $20.

Retired FF palette-pointer routines fund 79 bytes at $B620 and nine bytes at
$B670. Existing declared unused space funds the 14-byte snapshot at $BB47.
The actual 37 ROM gateways, public veneers, FX and art pointers were audited;
the live portrait path and mux beginning $B68B are unchanged. No new carrier
page or global state allocation is required.

The original proposal is retained as a negative: v1 (`db20d5a5…`) missed coins
in four directed corner cases. The immutable v2 has exact native coin effects
in all 16 directed comparisons. Do not install the earlier proposal.

## Exact private image

- ROM: `96e09ab1b67a7c75b89d49219e8e529582b9a05b7dd82dd3cd570fdb239212bd`
- Eight-kilobyte FF kernel: `72064c09f5a7198e30aa267c69c52a7e78f5f16728e823ed6ef8a0cf1f0498b3`
- Authentic full-image cookie: `a716000b72064c09f5a7198e30aa267c`
- Source: `6e58b2460852e808031f64ce733545ca0bffc78da05e5b68860d929e98c7f0cd`
- Builder/checker: `e508771dbac9dfb42c33ca41b3d3af4c07f98f81fd2f742205f6e4a3ce690665`
- Full-stage checker: `054a0e4fbcbf3ccc84e15240383cc0c546fee234343cddc2a84461e9fa8aedee`

The private file is `build/ff-head-corner-native-1110/candidate.nes`.
It is the sole new build file: 2,097,168 bytes. No capture files, videos,
per-frame dumps or copied source trees were created.

## Verification already completed

All four classes passed the unchanged natural cold-menu controller, earned
both upgrades and used the earned tier-two attack. They then traversed the
non-shortcut 1-1 route, entered the flagpole/score sequence and automatically
entered active underground 1-2 with two lives, Power/Earned 2 and no injury.
Fighter, White Mage and Thief reached it at route step 2177; Black Mage at 2204.
The actual loaded kernel and full cookie were compared, normalizing only its
runtime header bytes back to their hashed placeholders.

These are CPU/controller/native-NMI model results, not physical Mesen footage.
The frozen route is `check_ff_full_stage_current_1110.py` SHA
`4081ddb23a5e1c5dd5a59bfa87ae0058b108dc27f0b7fa2c1bb158ed98124439`.
No terrain, actor state, health, gear or position was granted after startup.

The maximum logical camera advance was three pixels. A separate observer
located its single maximum immediately after a wall hold. Existing
GuestCameraCatchUp deliberately adds one pixel at that point; the first
two-pixel bound was an invalid observer assumption. No camera code changed.
This does not establish physical-frame cadence or general camera smoothness.

`check_ff_head_lifetime_irq_1110.py` SHA
`6f9923f55828fed58d3098d479b437d2bd55822dffe37bf2228bc069203586ae`
also passed genuine old/new cold loading, complete-cookie rejection, actual
readback faults, warm ownership, 9,216 reader ABI cases, 256 priority values,
96 real head callbacks, 24 life/area/world/unready callbacks and all 54 new or
changed instruction boundaries. Reached cuts exercised 166 actual-vector NMIs,
87 unmasked scanline IRQs, 79 masked requests and a nested IRQ. Foreground
resumption and paired native ISR effects remained exact within the stated
intended head/attribute differences. This is CPU execution of actual vectors.

Physical Mesen route tests, exact Downloads delivery and updated Current IPS
remain pending. A separate stdout-only Mesen transport probe passed with zero
files created, retaining the shared queue, storage preflight and live watchdog.

## First physical controls: explicit negative results

The original Lua observer (`1e11e260…`) stopped at first active play because it
incorrectly required global `PlayerOutlinesOff=0`. Actual cold startup sets
that option to one; the logical CPU seed starts it at zero. The derivative v2
(`40f5f3e521d14a3facd80b95a2ba21466e375d5f5f3a140818ee74be2fc55a9e`)
corrects only that observer assumption and records the real option value.
This does not satisfy or redefine the separate always-on FF-shadow request.

The identical v2 controller on the private and public images earned the first
mushroom, verified its native collection sound/erasure, all 60 freeze updates,
recovery and body palette. Both subsequently exhausted the flower-controller
bound at exactly X593/Y176, camera483, Main1869, flower step1100, two lives and
Power/Earned1, with no injury. This earlier replay failure predates the repair;
it is not evidence of a new v2 ROM regression. The one-shot pipe-jump controls
need physical input-edge investigation before the complete route is accepted.

| Exact image | Physical terminal frame | Receipt SHA256 |
|---|---:|---|
| Private `96e09ab1…` | 3396 | `1c36745384f36a98dbadfbbe6f2deaac940e21eabcec9ad1de6be8b1b0489eb2` |
| Public `c10b7d87…` | 3394 | `8130576dbcb79c3cd7cf37bf6873463ddba28ebac8ce602e457135e0d7b20306` |

Both used Mesen executable SHA
`8b92daa209ee5052845e02a663aeb1afd6194eca55d86e6628c51114c61da0a9`,
the actual cold title/menu, no RAM writes/cheats/saves, and zero capture files.
The public run counted 1,506 zero-completion physical frames out of 3,054
gameplay frames. These are measured lag symptoms, not a zero-lag claim; the
full-route and empty-area cost investigation remains open.
