# WWF earned pickup adaptation, November 10

The source CPU proposal lets all six WWF characters collect the first authored
1-1 mushroom, complete the native 60-tick powerup interval, and resume movement.
This is an interim SMB pickup and armor adaptation. It does not implement or
claim original WWF endurance, gear, or weapon upgrades. Original motor, jump,
combat, renderer, palettes, private state layout, and music code are unchanged.

Parent ROM: `6d83dea872b42cd39c14d756334a801c8f7da7dfa63ecea16d9f13835c63638d`.
Proposal: `62c9a3d212659c1447afcb561113fa4ce1c2703fe6cd6be357a8b97ba20deb3c`.
No ROM, emulator output, or build file was written by these checks. Physical
Mesen qualification and delivery are separate, owned by root.

## Failure and narrow repair

The actual controller route on the earlier a76 parent releases the mushroom
from the authored block at world X336. The mature item crosses the player,
but 361 actual pickup-admission calls never reach native collection. The WWF
resolver still points admission, collection, and progression to `WfNoop`.
Thomas-only changes from a76 to the declared 6d83 parent do not change those
WWF resolver entries. This is a normal-caller failure, beyond the earlier
direct-leaf diagnostic.

Only five existing three-byte resolver tuples change. All other ROM bytes,
including every private kernel, data page, art page, and cookie, are exact.
There is no new code, RAM allocation, or inferred padding lease.

| Policy | Existing native worker selected |
| --- | --- |
| 5: injury | `GuestInjuryStart`, bank187, A113 |
| 6: remaining armor | `RemainingPower::EasyPower`, bank134, A6DB |
| 23: mature pickup | pure native rule after its entry PLA/PLP, bank252, A7DB |
| 24: collection | `MarioSourcePowerupCollision`, bank131, AF71 |
| 33: powerup interval | `GuestPowerupUpdate`, bank138, B299 |

The native collector supplies item erasure, score floatey, and sound queue.
Mushroom/flower tiers provide one extra native contact hit, then return to
tier0. The original WWF damage/endurance system still needs its own integration.

## Verified scope

| Actual menu identity | Naturally earned first mushroom | Recovery and resume | Directed native armor hit |
| --- | --- | --- | --- |
| HULK HOGAN | PASS | 60 ticks, tier1, lives2, 16px | survives, tier0, recovers |
| TED DIBIASE | PASS | 60 ticks, tier1, lives2, 16px | survives, tier0, recovers |
| BAM BAM BIGELOW | PASS | 60 ticks, tier1, lives2, 16px | survives, tier0, recovers |
| HONKY TONK MAN | PASS | 60 ticks, tier1, lives2, 16px | survives, tier0, recovers |
| RANDY SAVAGE | PASS | 60 ticks, tier1, lives2, 16px | survives, tier0, recovers |
| ANDRE THE GIANT | PASS | 60 ticks, tier1, lives2, 16px | survives, tier0, recovers |

All six runs use real title/menu selection and the current 1-1 parser, original
punch/jump controls, natural item birth and maturity, and ordinary Main/NMI
updates. They grant no terrain, actor, power, health, or movement state after
menu setup. Native collection erases the actual actor, produces floatey6 and
sound32, and returns carry set. These are source CPU results, not physical
Mesen observations.

Separate directed callbacks after the earned mushroom pass for flower tier2,
Star timer35, and 1UP floatey11 for all six roles. Those callbacks use explicit
mature actor fixtures: they do not establish natural flower, Star, or 1UP routes.
The damage check invokes the actual native damage caller after genuinely earned
armor; it does not establish a natural enemy-hit route.

The narrow lifetime checker also passes cold start, earned hit/recovery,
unpowered death and ordinary respawn (lives1/tier0), pause/resume, five maturity
cases, tier0/1/2 status returns, and three unchanged foreign Mario public routes.
The real interrupt proof covers each of the five changed worker entries with
NMI and IRQ, plus nested scanline IRQ during the actual CLI lag-NMI path:
22 paired ISR executions. AXYP/SP, live stack, R0..7, SMC, native gameplay state,
all non-audio private RAM, and mappings remain intact; complete hardware/audio
writes match the unchanged parent.

The original WWF lag-NMI music tick legitimately advances donor audio state
at C2:C500..C5BF, A1:BFA7..BFB0, and its saved-call scratch at A1:BFF8..BFFD.
These declared audio owners are compared exactly against the unchanged parent,
and excluded only from the separate comparison against a foreground run with
no audio tick. No other private writes are accepted. The initial reused FF
checker incorrectly required WWF music state to stay unchanged; the dedicated
checker preserves the gameplay assertion while allowing this original audio
work.

The standalone stdout Lua supports `SMB_TEST_VARIANT=0..5` at the actual WWF
menu slot. It reads source fields from physical work-RAM2, snapshots the actual
drawn body before DMA, checks consumed CHR/OAM/palette and HUD publication,
and witnesses the sound32 write during the exact native collection call.
A consumed sound queue need not remain set at return. Six API-only mock cases
pass, including rejection of wrong art and missing sound; these mocks are not
ROM or hardware evidence.

## Frozen source bindings

| File under tools | SHA-256 |
| --- | --- |
| reference/wwf_native_powerup_policy_1110.s | 7c1771f1c5815ca08a9a50dc06d3d253300a172af4bbaf34165fcfae1ab9baf7 |
| audit/check_wwf_native_powerups_1110.py | 9f770edf533af63fae1aeee9fc463aca027f3fd79ae20696a2e41d17581d2313 |
| audit/check_wwf_earned_powerup_1110.py | 242d664684338544cd03538ee63c151f40247dcc527cb95b1044b0545ec9c4e5 |
| audit/check_wwf_powerup_lifecycle_1110.py | e53f1e02de2ae2fea4078c8927b0344bd23d414606d141ce3a31131d0eb2e703 |
| playthroughs/wwf_earned_powerup_stdout_1110.lua | c98caae3c61adea500b15403d2eb6642ba29d758ece5f9f3492722d114817c79 |
| audit/check_wwf_stdout_controller_source_1110.py | e8f8e05138de84e1e608add48ab97d6368db7609117282d50c7a4e0ec61cff8a |

Checks ran with Python `-B` under the bounded runner, `--max-files 1`, and wrote
zero files. No helper actor or placement changes are part of this proposal.
Natural remaining items, full 1-1, original endurance/gear, audible output, and
whole-roster completion remain open.
