# Bowser: genuine 1-UP followed by full 1-1, source qualification

Both identities pass on exact candidate `6a3ff7c9a60b5ff5906d38f7815f021062006e0817d43e7ed139f47589c4eee2`.
This is a new ordinary-control continuation, with no game changes. It retains the
complete frozen natural Mushroom/hidden 1-UP assertions, including delayed life
increase, cue 64, current HP/tier preservation and 25 completed original core and
outer-tail returns. It then clears the non-shortcut 1-1 route, flagpole, castle and
actual 1-2 entrance, followed by 25 living grounded completed core/tail pairs.

| Source run | SMB1 Bowser, identity 1 | SMB3 Bowser, identity 0 |
| --- | --- | --- |
| Bounded session | 97842 | 94752 |
| Exact input | Composed 6a3 in memory from exact bc5 | Loaded actual installed 6a3 |
| Source receipt SHA-256 | `b4b10942a6a6e22d95078958267ecf9a11bd4d09a564e54d443bbe735789fa8a` | `47ba3b4cdf31d4b11c16d305e7d0d6725bd640d825caac782e3846def1cdb04c` |
| LF controller SHA-256 | `2bbf0988e986fd968b4fb1339f1bbcfe055505bf542984d6ad9b0c7baa4890ed` | `27743badc9ddaee53b60e764ff53d7aa3af913ca5491a6be7d9c21f25ea7f96b` |
| Item handoff / actual landing Main | 1313 / 1389 | 1053 / 1088 |
| Flag / castle / entrance Main | 3570 / 3631 / 4300 | 2512 / 2573 / 3292 |
| Actual next-area constructor Main | 4137, 4635 | 3129, 3627 |
| First / last grounded returned Main | 4734 / 4758 | 3699 / 3723 |
| Balanced core entries/returns | 3592 | 2507 |
| Balanced outer-tail entries/returns | 4570 | 3535 |
| Balanced movement entries/returns | 3593 | 2508 |
| Terminal HP / native tier / lives | 3 / 1 / 3 | 33 / 1 / 3 |

Both endpoints are actual world 0, level 1, area 2, engine 8, x40/y176,
native state 0 and Y-high 1. Both retain saved life 3 and the earned tier 1.
The final observation occurs at actual Main return `$82BE`, SP252, with no
pending Main, movement, core or tail return. Each of the final 25 observations
adds exactly one returned original core and one returned outer tail. Repeated
lag samples do not add a pair or erase a still-valid grounded count.

The route first releases ordinary input and waits for the genuine post-collection
jump to land on the authored floor at x1057. It then uses the existing full-stage
traversal controls. HP decreases during normal traversal (4 to 3 for SMB1, 34 to
33 for SMB3); this is not an injury-free claim. Life or tier loss before the
castle is a hard failure. Later construction is admitted only after the observed
flag/castle chain and entry into the actual next level. Both next-area constructor
events execute `$A071`, SP206, preserving the earned tier, HP and third life.

## Frozen inputs and API

`tools/audit/replay_bowser_life_full11_1116.py` exports
`controller(raw6a3, identity=0|1)` and `metadata(raw6a3, identity=0|1)`.
The controller requires exact 6a3; unknown images remain rejected. The source
checker explicitly accepts exact bc5 only to compose 6a3 in memory, or verifies
the portable inverse of actual exact 6a3 before executing those actual bytes.
Historical parent preservation metadata is reference evidence, not parent
gameplay execution.

| File | SHA-256 |
| --- | --- |
| New full-route factory | `c540e8d54acfef9050f9e43ef0e88898253226c6ce3daf6306cb23cb413b12c4` |
| New full-route control body | `ff955397522b24be85cb29b96b038453183f78dd71492daf5aadec03a92856c8` |
| New source checker | `07660940eb62a7f608d0664f97871c3288b6401384d69c523bd9f81926edb49d` |
| Unchanged item factory | `7db841a2828ae02ac3927f129fe72fa6da6c323700c3e870d38be11223ce7d7c` |
| Unchanged candidate composer | `2b5d81f056991636bf2498d4871645ea1cd80b003d2d986504b46b89d8b013b7` |
| Canonical source CPU driver | `9f56378f3e7ac12765927ebfef824ba7de70805c4105b6a68d89a00280a9d87f` |

Candidate repair/cold/ISR/lifecycle/header-fault scopes and their retained
negatives remain in `bowser-life-gain-candidate-source-1116.md`. The new route
does not replace those gates or modify the frozen item controllers.

## Executed callbacks and scope

Compilation alone does not establish callback registration. The canonical source
driver executes the complete generated Lua text with `LuaRuntime.execute`,
records its actual `addMemoryCallback` registrations, then invokes them at the
original CPU's reached PCs. The full dispatcher is defined before the Main-return
observer is registered, so that observer reaches the new continuation rather
than retaining the old item-only function. Successful item handoff, both real
area constructor callbacks and the balanced final core/tail return counts are
executed evidence of that path.

Private hooks authenticate work bank 3 and current instruction preimages; they
do not use a RAM address converted to a bogus ROM offset. The candidate changes
only the Ensure interior: public callback entries have not moved. The actual
cold path verifies all 8192 loaded bytes and the complete 16-byte cookie before
the first constructor, then authenticates the 2615-byte executable prefix.
Dynamic return witnesses use the actual callee stack PC/SP. Both normal and
catch-up Main callers are supported, but these source runs exercised `$82BE`;
native timing remains root's separate authority. A future moved hook requires
updating and exercising its registration as well as its byte binding: a new hash
or textual callback name alone is insufficient.

The compiled grid, Select, Start, parser and constructor execute in the source
model. Its bus lacks real title vblank and physical APU/video timing. These are
source gameplay receipts, not fresh native full-route claims. Root owns native
tests, delivery QA and the current continuation/checklist.

Both jobs used `run_bounded_build_v1.py`, `-B`, a 600-second bound, max one file
and zero generated files. `build/bowser1-life-full11-1116` and
`build/bowser3-life-full11-1116` remain absent. File/native-launch traps remained
active. No gameplay, health, ability, actor, terrain, position or outcome seeds,
new helpers, ROM writes or captures were used.
