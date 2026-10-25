# Private OA: TMNT world-sprite drawing

The private 37-identity MMC5 candidate is
`06908a38ac7c658c40f6c064b82e71f84ecc0b5f4617ed8b9a17fba6ad677701`.
Its parent is the frozen `tmnt-empty-render-nz` checkpoint. This is an
incremental performance repair, with the full final verification gate still
open. Public ROMs are preserved.

## Change and ownership

Only TMNT CORE PRG bank87 changes. `TnWorldDraw` uses a local drawing helper
for the interior of the viewport, avoiding a bank trip and repeated per-part
page checks. Every existing linked label retains its address. All CHR bytes,
physics, equipment rules and gameplay state allocations are unchanged.

The actual linked 168 right/left world-table entries resolve to 27 unique
records, including empty. Every nonempty record has signed X offsets -8..0
and Y offsets -24..0. The helper admits only main-page origins with X>=8,
Y>=24 and no requested palette override. It retains record order, software
attribute masking, OAM rotation and capacity rules. Other positions, unusual
headers and palette overrides use the existing renderer. An explicit MMC3
compile branch retains that mapper's generic HUD bookkeeping.

The old call footprint is padded and jumped over, preserving every prior
address. No new RAM is borrowed. Primary weapons, body rendering and the
health HUD retain their previous renderer.

## Measured result

Evidence is retained outside the workspace at
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-render-oa`.
The accepted source stage is `candidate-v1`; native profiles are
`performance-candidate-v1`, compared with the exact NZ
`performance-candidate-v5`. Fixture and observer hashes are unchanged.

Each representative turtle executes 600 native game updates after real
menus: 120 idle, walking, two live Goombas, primary attacks and triple shots.
Inventory/targets are explicitly arranged. The 120 enemy samples retain live
native actors in each version.

| Triple-shot measurement | Leonardo Easy | Donatello Hard |
| --- | ---: | ---: |
| Whole drawing CPU saved | 2.41% | 2.52% |
| Equipment drawing mean, before → after | 2311.53 → 2120.04 cycles | 2311.54 → 2113.01 cycles |
| Lag NMIs per 120 updates, before → after | 52 → 51 | 52 → 50 |
| Constructed draws, before → after | 68 → 69 | 68 → 70 |

Recorded gameplay-state fields match throughout both 600-update runs.
Leonardo's complete gameplay CSV is byte-identical. Donatello has two
controller sample differences, at updates544 and576, from the changed native
sampling schedule; the other recorded fields match. This comparison uses
the same input policy and does not claim byte-identical Donatello controls.
Fresh discovery/replay pairs below independently use exact saved inputs.

Idle/walk/live-enemy/primary drawing means and lag counts are unchanged.
The enclosing GameLoop is tagged before the fixture changes component at
TnMovement; its last primary span therefore includes secondary setup. Its
reported primary mean rises0.275 cycles, reflecting a33-cycle first HUD
fallback difference over120 calls. An initial reporting assertion incorrectly
required that enclosing span to remain identical; the failed report tool and
explanation are retained. Measured spans are retained rather than masked.
Routine spans exclude interrupts and nest; they must not be added together.

Heavy-shot lag remains substantial. This is not a constant60Hz claim.

## Exact-candidate checks

The assembled original/new `TnWorldDraw` differential passes18,704 cases.
It compares A/X/Y, meaningful flags, all written application RAM and ordered
OAM writes. Only stack, bank registers, SMC operands and safecall bookkeeping
are excluded. It includes all linked records, screen/page edges, capacity,
rotation, palette overrides, empty and malformed headers:1628 fast cases
and17076 generic fallback cases. Another960 aggregate equipment renderer
cases pass, as do13708 source equipment cases and456 non-TMNT shared-hook cases.

All four turtles pass Easy/Hard cold-menu1-1 discovery and independent
byte-identical saved-input/trace replays, zero deaths, into movable1-2:

| Turtle | Easy frames | Hard frames |
| --- | ---: | ---: |
| Leonardo | 4748 | 4716 |
| Raphael | 5210 | 5251 |
| Michelangelo | 4646 | 4896 |
| Donatello | 4796 | 4894 |

All37557 complete lossless route PNGs are retained. All26237 measured body
CHR frames match;101840 recorded visible scroll writes retain the native
bank126 scanline31 split. Root viewed all eight24-frame overviews plus eight
neighboring loading-transition frames. The eight overview files are
byte-identical to NZ. Human inspection is sampled, not an exhaustive manual
review of every retained frame.

All32 native equipment/primary/boss/ammo components pass. Actual hardware DMA
checks pass across30780 source equipment parts and9091 draws, retaining source
pixel geometry, flips and physical page628. The declared shared palette
adaptation remains. Transient13–15 sprites per scanline still cause overload;
all observed parts receive admission over time. The first graphics-check
attempt accidentally included an instruction-test folder through its broad
equipment glob; the folder was renamed, the failure retained, and the full
eight native captures passed the unchanged checker in `graphics-v2`.

All37 cold menu/lives/gameplay entries pass. Ordinary14-character MMC3/MMC5
outputs remain byte-identical to their existing builds. The private source
ZIP must rebuild the candidate exactly.

To keep the workspace below30GB, the superseded initial MN turtle checkpoint
was moved to the existing external archive. All14 files,57729505 bytes, were
verified before/after; nothing was deleted. Current NZ/NY sources and active
guide references remain local. The archive receipt and lookup are updated.

The final every-identity/every-applicable-item matrix, original audio for
unfinished families, remaining gameplay/terrain/HUD work, lag/overload and
the full37-identity MMC3 port remain open. This checkpoint does not complete
the user's active goal.
