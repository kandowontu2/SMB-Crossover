# Audited levels and native helper platforms — private MR integration

This packet combines the previously frozen static candidate and JP native-platform implementation over `build/checkpoints/cv3-roster-mr/source.zip` (SHA-256 `d23bd0470815cd50c4b0bde0c2772419208eb2fc519ba77889945c7df3e1e960`). It does not replace whole current game files. The incremental patch uses exact MR contexts; later SMB3 and CV3 weapon work must be composed around those contexts by the parent task.

The original [revision-2 audit](level-layout-audit-2026-10-22.md), static candidate and JP/JR/JW proofs remain unchanged. Easy means the pinned hosted six-character **1.x** behavior, whose exact patch version is unverified. Hard means the authenticated **2.02** reference. These are separate from Flash's five difficulty positions.

## Implemented authored differences

All coordinates below are native metatile columns/rows. The complete 38-cell bindings and 16 single-coin transactions are retained in the packet's `implemented-cell-contract.json`.

| Difference | Implemented behavior |
|---|---|
| Sixteen constructor cells | Easy solid/unbreakable; Hard single coin then native empty block. 1-2 `(165,10)`; 4-2 `(186,10)`; 5-2 `(147..149,9)`; 6-2 `(113,9)`, `(115,5)`, `(119..127,5)`. |
| 2-3 coins | Move four coins down one tile: `(72,5→6)`, `(73,4→5)`, `(74,4→5)`, `(75,5→6)`. Shared 7-3 stream remains unchanged. |
| 4-2 ceiling | Remove brick `(128,2)` in both modes. |
| 4-4 aligned maze cell | Remove `(96,10)` in Hard only, aligned to source `(161,10)`. This does not expand the native maze or certify its repeated-section equivalence. |
| 3-3 landing | Hard H-mask characters receive native mushroom tops `(34..35,14)`. |
| 4-3 landing/stem | V-mask characters receive native tops `(30..32,7)` and noncollidable decorative stem `(31,8..14)` in both modes. |
| 1-1 grouped Goomba | Hard omits only the final member of `E_GroundArea6`, offset 23. Easy retains the native group. |
| 2-2 / 7-2 Blooper | Omit the admitted actor at `E_WaterArea2`, offset 23, column 71/row 8. |
| 6-2 upper Goomba | Omit `E_GroundArea4`, offset 14, column 68/row 3. |
| 6-2 later grouped Goomba | Omit only the final member at offset 32; preserve the group record/first member. |
| 2-4 small lifts | Left falls/right rises, independently at Y 96/192. |
| 5-4 small lifts | Left rises at Y 96/224; right falls at Y 64/192. |
| Small-lift motion | Native paired actors/render/collision/carry; separate Y/fractions; 55 px/s rational Q8 cadence; individual wrap over 64..240; release passenger on that row's wrap. Native collider becomes 24×8. |
| Firebar constructor | Fast/ordinary source variants share native increment 40. Approximately 105.47°/60 updates rather than claiming continuous Flash 106°/s identity. |

Native enemy hard-only admissions, slot limits and ordinary generator algorithms are preserved except for the explicit authored omissions above. The old exact actor stream comparison is retained; runtime slot exhaustion and frenzy generation are not inferred from static XML counts.

## Genuine native helpers

`src/crossover_helper_data.json` contains **34** source-aligned records: **31** active in hosted 1.x, **34** in 2.02 before character gating. Source/native coordinates, source strings, exact area keys, widths and gates are retained per record. The earlier swept-bound proof includes all 34 records, including all three in 8-1a; its minimum swept horizontal edge separation is 322 px, so a pair cannot share a 256 px viewport.

The helpers occupy existing native enemy actor IDs `$25`/`$28`. Their initialization, collision, carrying, rendering, native girder tiles and OAM allocation are reused. They are not a separate visible platform or collision engine. Widths 16/32/48 use native girders and tagged native bounding boxes with height 8. The 16 px descriptor is the first two native girder records, not new art. Native ordinary platform IDs and poses remain unchanged.

The retained JP engine samples source sine before phase increment and quantizes to native integer positions. Its Q24 phase steps, horizontal/vertical tables, visibility gates, actor ownership and detach/reentry rules are unchanged. Easy visibility is strict `(-56,+296)` around camera left; Hard is inclusive `[-48,+288]`. Detached helpers preserve phase. Native master timer/pause behavior is retained.

Admission never clears an occupied native enemy or firebar to make room. All six occupied slots leave an eligible helper pending. A released/stale helper owner cannot erase an actor that legitimately reused its slot. This deliberately preserves native capacity; it does not guarantee a helper appears immediately when every slot is occupied.

## Character accommodation policy

H/V are source helper-mask families, not movement axes. The original installed masks remain:

| Family ID | Character | Mask |
|---|---|---|
| 0 | Mario / Luigi alternate | None |
| 1 | Mega Man / Proto Man | H+V |
| 2 | Samus | H |
| 3 | Bill / Lance | H+V |
| 4 | Link / Zelda II Link | H+V |
| 5 | Simon | H |
| 6 | Pit | H, declared custom policy |
| 7 | Rygar | H, declared custom policy |
| 8,9 | Legacy Luigi / Bass | None |
| 10 | Ryu | H |
| 11 | Sophia | V |
| 12 | Scrooge / Darkwing | H+V, declared custom policy |
| 13,14,15,16 | Kirby, Chip/Dale, Mac, Mike | H+V, newly approved custom policy |
| 17,18,19 | SMB3 Mario/Luigi, Vic Viper, TMNT | None |

Expanded CV3 variants 1/2/3 (Grant/Sypha/Alucard) receive H+V as approved custom accommodations; Simon variant 0 retains audited H. The variant is part of the helper cache key. Other Select alternates inherit their family. The hosted unfiltered-original-six tag remains limited to the first six families. New custom masks do not claim reference-game parity. IDs not yet enabled in frozen MR receive data rules only; this packet does not expose portraits or character stubs.

## Layout and hooks

Static cold code is bank `$1A:$A000..$A579` (1,402 bytes); helpers are `$1A:$A800..$B11F` in the final expanded build. Both have assembler/linker bounds. Original Zelda wrapper physical bytes `$1A:1C00..1FFF` and CPU `$DC00` addresses remain exact.

The helper SRAM ABI is exactly 91 bytes: MMC5 `$7382..$73DC`, ending immediately before Proto `$73DD`; MMC3 `$736A..$73C4`. The existing aligned audio history and every previous SRAM/public code/SMC address remain fixed. No ExRAM allocation is added.

The parser uses its original three-byte call and existing 15-byte LEVEL-tail bridge. Existing enemy farcall targets, three small-lift calls and fast-firebar table entries receive narrow replacements. The 130-byte old small-platform draw span supplies the lift bridges and 38-byte native helper bbox gate at `$BE8E`; no new PLAYER or bank-4 tail space is consumed. The existing 68-byte resident pause span supplies equal-size wrappers; the native platform jump-table span and Samus pointer override remain exact-size replacements. The NMI graphics-bank selector is untouched and stays fully resident.

## Verification and scope

See the frozen integration manifest for exact final ROM hashes and proof-file hashes. Native fixtures separately exercise real 16/32/48 px OAM and carrying, detach ownership, Kirby/Chip/Grant/Sypha carrying, both independently moving lift rows and wrap release, actual solid/single-coin head contact and physical used-block completion, and actual parser callbacks for version/character/world negatives. The expanded profile arena checks complete A/C-bank restoration across NMI/IRQ. These are seeded component fixtures, not campaign routes or video reviews.

The complete pre-final MR rebase checks every original area's first 256 parser columns (covering every implemented static cell), authored actor/group records with both hard flags and world/version negatives, all affected cell/profile/version/negative keys, single-coin aliases and lift updates. A final admission correction prevents invalid raw IDs from aliasing the packed CV3 cache. Its earlier binary/proofs and invalid-ID witness remain retained; final exact-ROM configuration, cell/public-ABI and native checks are separate rather than silently relabeling old evidence.

Two native-column fixture revisions are retained as rejected harness setups: one lacked an actual-PRG-bank guard around a banked execution callback, and one incorrectly expected Bill to lack V support. Corrected fixtures qualify physical bank 26 and use Samus for the H-only counterexample. Neither failure justified a game-source change.

Still explicitly unresolved: literal expanded castle/maze lengths and checkpoints; source-only column insertion/deletion/camera differences; the five underwater pipe-bottom class representations whose native collisions/transports are preserved; water-fish/frenzy and other generator equivalence; ambiguous sprite-origin/phase/clone anchor differences in the audit. This packet implements the definite static list and the complete retained helper placement list, not those unproved structural equivalences.
