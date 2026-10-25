# Authored level changes: isolated candidate

The candidate at `build/verification/level-variants-candidate-agent/source` implements the definite authored differences from the immutable [revision2 audit](level-layout-audit-2026-10-22.md). It has **not been adopted into the main game**. Dynamic source helper platforms are owned by the parent task and are not implemented here. All changes reuse native level tiles, block effects, actor slots, platform graphics, collision and carry.

Easy selects the pinned hosted six-character1.x constructor behavior; the exact1.x patch remains unverified. Hard selects the authenticated2.02 behavior. This is the game's behavior-version option, not Flash's separate five-position difficulty menu.

## Implemented cells and actors

The complete native/source cell bindings, gates, old/new metatiles and reasons are in `build/verification/level-variants-candidate-agent/implemented-cell-contract.json`. Native coordinates are retained; source column deletions and expanded castle lengths are not blindly copied.

| Change | Easy | Hard | Native coordinates / qualification |
|---|---|---|---|
| Sixteen `UnbreakableBrick` constructor cells | Solid brick art; no payload | Single-coin brick, then the native empty block |1-2:165,10;4-2:186,10;5-2:147–149,9;6-2:113,9;115,5;119–127,5 |
|2-3 four coins | Down one tile | Down one tile |72:5→6;73:4→5;74:4→5;75:5→6.7-3 remains unchanged |
|4-2 ceiling brick | Removed | Removed |128,2 |
|4-4 maze cell | Preserved | Removed |96,10, explicitly aligned to source161,10. Source225,10 is an expanded copy; native maze equivalence is not certified |
|3-3 mushroom landing | Absent | H characters |34–35,14 |
|4-3 mushroom landing and decorative stem | V characters | V characters | Tops30–32,7; stem31,8–14. Stem metatiles stay noncollidable |
|1-1 later grouped Goomba | Preserved | Second group member omitted | `E_GroundArea6` offset23; the group itself and its first member remain |
|2-2/7-2 Blooper | Omitted | Omitted | `E_WaterArea2` offset23; native column71,row8 |
|6-2 upper Goomba | Omitted | Omitted | `E_GroundArea4` offset14; native column68,row3 |
|6-2 later grouped Goomba | Second group member omitted | Same | `E_GroundArea4` offset32; nominal group-camera anchor170.5 |
| Native firebar fast variants | Ordinary source speed | Same | Original direction, length and hard-only admission retained; fast spin increment56 becomes40 |
|2-4 small lift pair | Left falls; right rises; each starts at96/192 | Same | Existing two native lift slots. First duplicate `type=` constructor property wins |
|5-4 small lift pair | Left rises at96/224; right falls at64/192 | Same | Existing two native lift slots |

H characters: Mega Man, Samus, Bill/Lance, Link, Simon, Ryu; approved custom additions Pit, Rygar and Scrooge. V characters: Mega Man, Bill/Lance, Link, Sophia; approved custom addition Scrooge. Mario, Luigi and Bass receive neither family. These custom assignments are accommodations approved by the parent task, not claims of official2.02 membership.

The new solid-brick IDs `$6E/$6F` use the original native brick graphics and ordinary solid/bump attributes. Hard reuses native coin-brick IDs `$58/$5D`; a location-scoped completion rule forces just these sixteen cells to empty after the first coin. Other native Mario and guest multi-coin rules remain in their original paths.

## Native lift reuse

The two original small-platform actors remain in the original six-slot enemy pool. No actor is erased to make room, and no extra actor or RAM allocation is introduced. Within small IDs `$2B/$2C`, otherwise unused `Enemy_State` stores the second platform's Y, `Enemy_X_Speed` its fractional Y, and `Enemy_Y_MoveForce` the cadence counter. `XMoveSecondaryCounter` aliases `Enemy_X_Speed` and is deliberately **not** used as an independent counter.

Each of the two drawn platforms updates and wraps independently. The cadence is235,235,234 Q8 units per three logic updates, exactly55 NES pixels per60 updates. Castle reset positions are64 and240. A wrapping platform releases only its own currently supported passenger before the native carry function, avoiding a top-to-bottom teleport. The source rectangle is24×8, and the native drawing, second-platform bounding box and native carry all consume the same second-Y state.

The native draw body is moved into cold code. Its original130-byte span holds the draw entry and three small native-bank bridges; its original public entry, subsequent code and diagnostic-label address aliases remain fixed. The first failed native wrap witness and the first failed counter-alias component are retained under `initial-lift-failures` and the early `native-lift-*` folders, with the pre-fix ROMs and bindings. The final native fixture checks both girder rows in physical OAM, top contact and carry for both independently moving platforms, and passenger release at the rising reset.

This remains native NES quantization: the ordinary firebar increment40 is about105.47 degrees per60-update second, compared with the source106 degrees/s. The constructor change removes the source-incompatible fast variant; it does not claim continuous-time, subpixel-identical Flash rotation. Source lift rates are represented in Q8 with the stated rational cadence.

## Layout and integration contract

Authored cold code/data uses physical bank`$1A`, CPU`$A000..A587` (1,416 bytes), with an assembler assertion that it ends before`$A800`. Parent helper space`$A800..$BBFF` remains all`$FF`. The original Zelda wrapper's physical bytes and`$DC00` public addresses remain unchanged.

The column hook replaces the original three-byte `AreaParserCore→ProcessAreaData` call. Its15-byte A-register-dead bridge fits the existing LEVEL tail at`$BFEF`. It invokes the real native parser before applying the declared cells, so rendering and block collision publish the same result. Enemy filters replace existing farcall targets and consume only the specific admitted records/members listed above. Every pre-existing public symbol and RAM address is unchanged on both mappers, and both disabled-Crossover baseline ROMs remain byte-identical.

After `level_lift_bridges.inc`, the old draw span has47 unused bytes beginning at CPU`$BE8E` in physical bank0 on both current mappers. The guide agent's helper bbox gate may be inserted there in the parent's combined build, before the130-byte padding assertion. It is not included in this standalone candidate because its real parent-owned cold target does not exist here. The gate must qualify large helper IDs`$25/$28` before interpreting `Enemy_State` marker bits; small-lift second-Y values can contain those same bits.

Apply only the reviewed source hunks from the candidate; do not replace whole current files from this snapshot when combining later parent edits. Main source and ROMs are still unchanged.

## Validation and remaining work

`native-verification.json` contains18 passing native tests: the source coin and lift arenas plus character selection, score positions, terrain publication, firebar fairness, cannon cooldown, Bill flagpole completion and Mega Man projectile overload, on MMC3 and MMC5. Seeded arenas are component witnesses; they are not ordinary controller playthroughs.

The final compiled verification passes4,212 affected/negative cell cases across13 character IDs and both versions;34,816 full-parser column comparisons (first256 columns in each of34 original areas, covering every implemented cell);11,152 authored enemy/group cases with primary/secondary hard gating and world/version negatives;1,664 single-coin constructor and page/buffer/version negatives; and5,760 independent lift updates plus freeze checks. The result is recorded in `component-verification.json`. A passing result does not certify untested ordinary campaign traversal or graphical review of final playthrough videos. Rejected early arena setups and fixed candidate failures are classified separately in `rejected-and-fixed-witnesses.json`; passing fixtures are not substituted silently for failed evidence.

Still outside this candidate:

- The31 hosted /34 later moving helper placements, character gating and source motion, being implemented by the parent through native platform reuse. `helper-swept-bound-proof.json` retains every record and every same-area pair; minimum source swept horizontal edge gap is322px, so no pair shares a256px viewport.8-1a has three records. Spawn-ahead margins and native landmark remapping still need separate verification.
- Literal source column deletions/insertions, expanded4-4/7-4/8-4 maze lengths, checkpoints and leftward camera behavior. Clearing the one aligned4-4 cell is not a claim that the two full castle representations are equivalent.
- The five underwater exit-bottom cells whose source class is pipe while the native class is generic solid. Their existing collisions/transports are preserved; they are not automatically new pipe entrances.
- The source's explicit water-fish placements versus native random frenzy, Lakitu/Bullet Bill/Cheep/Bowser-flame zones versus native controls, and source clones versus runtime native loop admissions. The audit retains all records; no unmatched count is silently converted into missing simultaneous enemies.
- Other enemy/platform anchor deltas whose sprite origin, movement phase, camera admission or clone alignment is ambiguous. The complete revision2 comparison remains the evidence inventory; only the definite removals and lift/firebar constructor changes above are implemented here.
- A fresh combined-mapper gameplay route and media review after the parent merges static changes with its dynamic native helpers. This candidate alone does not complete the larger game task.
