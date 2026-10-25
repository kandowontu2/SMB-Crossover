# TMNT equipment: private NY checkpoint

NY adds the missing TMNT1 secondary weapons for Leonardo, Raphael,
Michelangelo and Donatello. It preserves NX's Mike graphics/HUD repair.
This is a verified private MMC5 checkpoint, not completion of the full roster.

Candidate SHA-256:
`45a2cad0cdb60e2d5ea79b108c8b4dff226e05f037839b9a1d97deeebd0ed2ba`.
Parent NX: `17b8ae45a1973e252c1f9e8683137c6829dfa5bab8dcb44bce1c25080e4df095`.
Original TMNT USA: `15e112c3790add361157dfa42854c3159c956f72e6acd8fabc518615f1ce8525`.

## Controls and rewards

B uses the selected weapon. Select switches between the turtle's primary
weapon and his one equipped secondary. Replacement equipment auto-selects;
collecting a duplicate preserves selection. Each turtle has separate gear/ammo.

| Equipment | Native supply and behavior |
| --- | --- |
| Single shuriken | Straight projectile; up to three concurrent source actors |
| Triple shuriken | Three directions; uses the free portion of that same pool; one ammo per volley |
| Boomerang | Source fractional deceleration, reversal and pre-integration catch; returning weapons refund ammo |
| Kiai scroll | Piercing crescent; authored physical flower reward at full 128 HP |

Replacement gives 20 ammo. A duplicate adds 20 and caps the pickup refill at 99.
The original catch increments without that cap: refilling while three
boomerangs return can yield 100–102. The HUD supports three digits.
Empty ammo returns to the primary; a returning boomerang can re-equip it.
Full actor capacity spends no ammo. Partial triple capacity spends one only
when at least one projectile actually spawns.

Every 25 eligible ordinary defeats resets the source counter and runs the
original random gate. Half the accepted drops are single shuriken; a quarter
each are triple shuriken and boomerang. Kiai is excluded from this lottery.
Drops are physical, expire after 128 native updates, and require contact.
Bowser defeats clear the counter and do not produce ordinary weapon drops.

The flower adaptation freezes the reward at reveal. At full HP it produces a
physical Kiai scroll, which cannot be collected inside the block or while
rising. Later damage does not turn that revealed scroll back into food.
Mushrooms heal 32 HP; hurt-state flowers heal 64. Original SMB lifecycle and
terrain remain the host adaptation.

Original animations retain their native phase/timer/reset behavior. Source
damage uses current weapon selection/equipment, even for an in-flight actor;
Select, replacement and last-ammo fallback can change that actor's damage.
Single/triple actors disappear on lethal accepted hits, but survive nonlethal
hits. Boomerang and Kiai persist through both. These source quirks are tested.

Area changes retain per-turtle gear/ammo and the drop counter, while clearing
transient actors. Life loss clears only the selected turtle's gear/ammo and
restores his health under the retained SMB respawn adapter. Ordinary Easy
stomps and Hard contact policy are unchanged.

## Evidence on the exact merged candidate

Evidence root:
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-review-ny/merged-v2`.
The immutable agent handoff is in the sibling `2026-10-24-tmnt-nx/handoff`.
It is based on NW; NY independently composes its 7,096 changed ROM bytes onto
NX with no conflicting bytes, and rebuilds the merged source.

All eight cold-menu discoveries and independent saved-input replays clear
1-1 with zero deaths, then reach movable underground 1-2:

| Turtle | Easy frames | Hard frames |
| --- | ---: | ---: |
| Leonardo | 4,756 | 4,725 |
| Raphael | 5,217 | 5,308 |
| Michelangelo | 4,607 | 4,888 |
| Donatello | 4,621 | 4,902 |

Complete input and telemetry bytes match on every independent replay.
37,424 lossless route PNGs are retained. Body CHR checks cover 26,393 native
frames with zero mismatches. The 102,560 recorded visible gameplay scroll
writes all occur in the resident native split at scanline 31. Camera/world
step bounds pass. Root inspected all eight 24-frame overview sheets and five
final equipment/HUD screenshots; this is sampled visual inspection.

32 native component runs cover all four turtles in both modes: physical
equipment collection/use, primary/food/death/respawn, five actual boss defeats
per run, and actual ammo HUD values 20/99/100/101/102/inactive. Targets, health,
RNG and drop counters are explicitly arranged in these components. Equipment
in the collection suite is obtained only by actual physical collision.
These are not untouched natural 25-defeat campaign proofs.

13,708 linked/source CPU cases pass, including 2,048 animation updates,
320 in-flight damage contexts, 128 lethal/nonlethal hit cases, last-ammo input,
the source overlap grid, boomerang trajectories/catches, pause, queue bounds,
life/area state and expiry. All 456 non-TMNT shared-hook differential cases
pass against NX. All eight primary/food/death/respawn native CSVs remain
byte-identical to the original NW components. All 37 cold character entries
pass on NY. Both ordinary mapper builds remain byte-identical to their
existing 14-character outputs.

The source-counter investigation executes 12 original generic-clear cases
and 24 original life-loss branch leaves. A declared counter marker of 23
survives controller-driven first-sewer entry at frame 731 and exit at 813,
through frame 1500. No generic clear executes during either transition.
That is a first-sewer observation, not a complete original campaign audit.

## Graphics, retained limits and release boundary

Source equipment extraction rebuilds the prepared CHR bytes and metasprite
records exactly. All old 24,576 body/primary CHR bytes remain unchanged;
22 source tile pairs use the reserved physical page 628. Actual DMA checks
cover 30,154 parts across 8,921 draws, both facings, source pixel masks,
coordinates, flips, page ownership and declared shared-palette adaptation.
Original equipment blue/light blue are adapted to shared dark ink/white;
the native red remains shared red. Enemy palettes are not rewritten.

Crowded world rows still reach 13–15 sprites, beyond the NES eight-sprite
scanline limit. Rotation admits every observed part eventually, but temporary
pickup/weapon dropout remains. HUD parts receive full admission in these
components. The route measurements still show approximately 13.5–16.7% lag
NMIs during the measured gameplay portions; this checkpoint does not fix all
lag. Native TMNT motion intentionally advances every two source frames,
separately from those measured lag frames.

Music/SFX still use the existing shared host adapters. Full source audio,
every natural reward path, broad campaign/terrain/performance work, the final
every-character/every-item matrix and the full 37-identity MMC3 port remain
open. Public ROMs are preserved. NY's source-only ZIP rebuild must reproduce
the candidate exactly, and the workspace remains below 30,000,000,000 bytes.
