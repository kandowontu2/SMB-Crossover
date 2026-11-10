# Sonic's earned mushroom and powered injury route

The same native CPU controller inputs reproduce the invalid injury tier on
the old build and verify the fix. The route selects Sonic through the fourth
Mr. Gimmick alternate. From confirmation onward it changes only controller
input and normal NMI scheduling. All actors, terrain, hits and progression
come from the game.

| Event | Actual CPU observation |
| --- | --- |
| Original opening | Sonic reaches X200/Y176 with the authenticated source motor. |
| Authored block | The original head contact reaches native `PlayerHeadCollision` with tile `$C1` and native pointer bytes R2/R6/R7 `70 D5 03` at player X334/Y160. |
| Item birth and maturity | Native mushroom slot 5 starts at X336/Y136 and reaches mature state 128 at X336/Y119. |
| Pickup | The player reaches the mature item at X391/Y113 versus item X403/Y133. The actor is erased, the score marker is 6, and the native sound queue receives `$20`. |
| Growth | All 60 native ages are observed in order. The player becomes tier 1 and returns to engine 8 with timer 0. |
| Deliberate injury | A live Goomba at X688/Y184 overlaps grounded Sonic at X678/Y176. The native injury path is entered once with tier 1. |
| Old result | The native store receives A43/C0. The player enters engine 10 with invalid tier 43. |
| Corrected result | The same store receives A0/C0. Native recovery takes 55 updates and retains two lives. A subsequent ordinary jump clears the pipe edge, with the original motor moving from recovered X722/Y176 to X738/Y103. |

The d254 predecessor SHA is
`d2542ff3c9f78ac26eb7e19d64a7708711bc766515f634b05952bab1be9103f0`.
The 19a5 successor SHA is
`19a5ea9001f22afd529c96c6c2401a237f487c0f851678363fb859f0ec7c1936`.
The CPU checker asserts every input change matches through the hit and
compares the block, item, pickup, transformation and injury witnesses.

The test initially kept expecting score marker 6 after the native marker
expired during growth. It now checks the marker on the collection update.
The first recovery controller held Right into the next pipe and stalled.
The final route uses the ordinary source-ready A cue to continue moving.
The injury patch and world data are identical across these test iterations.
No helper platform is used.

The Mesen script uses the same phase conditions with physical controller
polling. `SMB_TEST_VARIANT=0` and the runner-bound `SMB_STDOUT_ROM_SHA` select
the route. Its allowed predecessor pins are d254 and the installed Prince
combination `47a7a6aeabe2cc7db593f431591e52331b834485b3d7638e3f10f95cbf43db4b`.
The successor pins are 19a5 and the combined
`49295acff1d70349119b599882a2ec0b4e2f58d21f153c90b2228dc9aceee2a7`.
It verifies the associated full header cookie. Lua API mocks passed both
combined pins and 46 native constants. Root owns the physical runs.

| Source | SHA-256 |
| --- | --- |
| `tools/audit/check_sonic_earned_injury_1110.py` | `1fd65b7076c5a8931c9e2e29d6df7133af24010ad846d3e2d23c1348e2e83f9d` |
| `tools/playthroughs/sonic_earned_injury_stdout_1110.lua` | `612ff932018b09e734affe19041d4f6ee4e09023d510ac1d518789df611d94dd` |
| `tools/audit/check_sonic_earned_injury_stdout_source_1110.py` | `d10314c31111f05f9cbf2c02548529923480870e7652b058e1db8424bad527a3` |

The source jobs used the bounded runner and produced zero files. This route
qualifies native mushroom growth and injury. Sonic's original ring, shield
and combat implementation remains a separate task.
