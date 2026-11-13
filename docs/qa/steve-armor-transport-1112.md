# Steve armor entry transport

This records historical component and funding experiments. The mounted full
armor packet, current grants and qualified CPU candidates are documented in
`steve-armor-live-1113.md`.

The private entry component was first checked on
`f228e61399432c1a205b8f5ac6dad13d990515f9c2e2f5024bcd5ce443c76653`, producing
`4e765c16214cd2976e335096fb55e01a09604629a62e8aa1abc62af42fdcc632` in memory.
The complete matrix was repeated on
`8fc57b8b4268a47f8a906af8b5813834bbf76ca7376d1d12767d510708da9582`, producing
`78bbc0c091aa05c67fe32f337cacad1ea1e5bffa38d4976ecc06b31d08063c4b`.
Both resident headers use `a810200a14c48e5309fa9e59139fb26a`.

The live Steve companion update reaches the original matching-token grant but
never calls the stored transform routine. The new worker stays within the
existing 239-byte CHR371 transfer and state boundary. It keeps token preview at
`$C100`, routes the real grant call at `$AB7C` through the armor entry, and calls
the verified punch reset at `$DB4B` on transform underflow. Both punch suffix
copies read the same authoritative timer at `$C1F2`. The transform checks each
preimage and exactly reverses its edits, including both cookie copies.

The original cartridge executes player state before the token tick and holds
player decisions while the token countdown is `$2F` through `$01`. In the
paired host fixture, the grant commits at update 80 with windup `$7F`. Update 81
steps to `$7B`. The next 47 updates leave the windup untouched. The 32nd windup
call occurs at update 159, clears the three punch fields, returns to state 0 and
sets the armor timer to `$7F`. The original cartridge trace started from a
matching actor and countdown `$31` and showed the corresponding sequence over
79 post-grant updates. These fixtures seed a matching pattern and robot.

The bounded CPU run passed 512 token previews, 4,096 grant cases covering all
robot bytes and both facings, 9,216 token boundaries, and 256 windup comparisons
against the original cartridge instructions and original punch reset. The
windup comparison isolates the source support and effect callbacks. Eight
Alpha and Laserbot fixture episodes ran 2,864 actual `$CA00` companion updates,
including paused intervals. The real cartridge cold farcall read back the 239
worker bytes and relocated punch operand with 32,800 PPU reads, accepted both
new cookies, and performed zero PPU reads on a warm call. Fourteen forced-blank
lag-NMI cuts passed. A readback fault on the final worker byte rejected both
cookies. Current-parent repeat receipt
`6911a36922eeb3bbd1359cefd6fc9f177b52b1ab1ca28ac92f87fb4fc23a3556`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-armor-transport-1112 --max-files 1 --timeout 120 -- python -B tools/audit/check_steve_armor_transport_1112.py --matrix --underflow --runtime --cold
```

All results are in memory. Release qualification still needs original companion
position and projectile cleanup during entry, active armor clock and damage
absorption, complete expiry and robot restoration, body and effect assets,
scene reset, and an earned gameplay replay. The previous funding audit details
the 86 unique ordinary body cells and occupied Steve carrier regions.

## Original lifecycle leaves

`steve_armor_lifecycle_1112.s` occupies 188 bytes before host adapters. Its
paired checker passes 1,064 clock cases, 12 exit starts, 1,344 state-16 exit
decisions, 5,120 entry/exit orbit angle and radius decisions, and 510 accepted
damage timer calculations for the original 8 and 16 costs. The source calls
the modeled robot constructor 168 times across the exit matrix. Animation and
constructor callbacks are isolated in this decision comparison. The leaf
SHA-256 is `7364aa42cf580e6abc43fce2fc0954463bd226eb89f046424b3769cb36bcf2e0`.

The `--bank1` fixture places the 188-byte body at raw WRAM bank 1 `$A000`,
enters through native `FarCallCommon`, and returns to raw3 with raw2
continuously mapped at `$C000`. It passes 100 clock calls and 20 IRQ plus 20
lag-NMI instruction cuts on current
`15a683321cde608cfe15447e90ef58d5295a16a1a6b607434f98df37162ac533`.
The fixture writes the body directly to RAM. Its source carrier and cold
loader still need mounting.

## Storage and runtime recovery

`check_steve_armor_cold_space_1112.py --scatter` replaces the late CHR306
transfer with a 640-byte prefix transfer and readback. The original common
copy already loaded CHR220's identical 384-byte punch suffix at `$DA80–DBFF`.
Those live punch bytes stay exact. CHR306 offsets `$280–$3FF` then supply 384
bytes of source storage.

After all late rows verify, a 60-byte callback copied from CHR371's existing
staging tail runs at `$C3BF–C3FA`. Its mapper is temporarily copied from
CHR307 offsets `$3E0–$3FF` to `$C8C0–C8DF`, the existing writable pose scratch.
It transfers and rereads 136 source bytes over the spent loader at
`$CD00–CD87`. The fixture executes a canary there through the actual CPU.
The fifth-row copier now includes the declared 60-byte tail. The cold source
and final runtime are included in the recomputed cookie.

On current `15a683321cde608cfe15447e90ef58d5295a16a1a6b607434f98df37162ac533`,
the canary composition is
`9ab5f2223d80a2e17f210fe5aee9074f4cac73412ec0fdba936a243c82427302` with
cookie `a810200a775fcd638b437aa8e754a703`. Both Jay and Steve retain exact
resident bytes outside the declared loader, scatter and headers. Their cold
read count is 32,306 instead of 32,800. Warm calls add zero PPU reads.
The checker passes 177 forced-blank lag-NMI cuts and faults at `$D800`,
`$DA7F`, `$CD00`, and `$CD87`. The real Prince loader overwrites these regions
and commits its headers after 31,310 PPU reads. Steve's real loader restores
the canary and scatter after 32,306 reads, with both markers invalidated before
commit. Exact reverse reconstruction passes without a ROM backup.

The callable interface is `proposal(raw, cookie, payload, scatter=True,
extra_edits=())`, returning image bytes, the new cookie and assembled program.
The 384-byte payload supplies its first 136 bytes to CD00.
`reverse(image, parent_cookie, scatter=True, extra_edits=())` reconstructs and
authenticates the parent by recomposition. Compose the entry first, pass its
cookie into the storage component, and reverse them in opposite order.

## Body atlas candidates

`steve_armor_art_1112.py` packs 19 ordinary armored pose records and their
mirrored facings. There are 86 distinct source cells and 216 tile/geometry
comparisons. Three atlas groups use 31, 24 and 32 cells, leaving 288 storage
bytes across the first two rows.

Candidate physical pages 8 and 10 are identical to page 2. All four native
CHR map mirrors reference those pages through logical `$70` and `$78`.
Redirecting the references to page 2 passes 44 actual native publisher cases,
528 hardware windows, and 247 paired opening updates for each of Mike, Jay and
Steve. Page 709 is identical to page 13. Its retained finite-ledger claim is
the conservative four-page Mike family range. The compiled body selector
passes 168 calls across four family values, seven pose selectors, both facings
and three native states. Its requested body pages are 216, 220 and 708. The
two compiled auxiliary publications are 710 and 711. The full 709 ownership
review remains explicit before an atlas write. Atlas bytes remain in memory.

## Natural acquisition and stage persistence

The persisted `--natural-footprint` route on current
`15a683321cde608cfe15447e90ef58d5295a16a1a6b607434f98df37162ac533` collects
the authored blocks at world X336, X1248 and X1744, switches the third token,
earns Laserbot, and reaches active 1-2 at X40 with six health and two lives.
The robot remains actor 3 with pattern 0 across the transition. The route
executes 4,658 CPU updates. Receipt
`8ff0d82832a1653e75ef798fe0d716063383937618504026559660fc71fafb96`.

This trace observes zero authenticated raw3 `$A000–$AAFF` executions for
Steve. Static inspection found actual Jay code there, so the range has no
retirement grant. The three type-0 powerup blocks in 1-1 supply the first
robot. A second matching set for natural armor needs later authored pickups.
Robot persistence provides a path to continue that acquisition in 1-2.

All tests use bounded zero-output root `build/steve-armor-transport-1112`.
There are no helper-generated ROMs, captures, backups or patch assets. Root
owns emulator and public integration. The current funding request permits a
larger native PRG or conditional WRAM helper. The 136-byte runtime recovery
remains a tested option while the 188-byte leaf plus live dispatch, damage,
robot reinitialization and renderer need a larger placement.
