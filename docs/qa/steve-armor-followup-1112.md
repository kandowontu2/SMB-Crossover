# Steve armor integration audit — November 12

Audited installed Downloads image
`cebb0ae64b4e6cc92e473a239cb8fd4011d54cfd5e6814013a3afbd2de2bf7d7`.
Original US Shatterhand input:
`fbdfaab40aedda270d7473be37566b59e68811d932740c105d84fa6b1a7f19e1`.
No ROM, delivery recipe, shared source, or emulator process was changed.
No new assembly/checker is proposed as a live patch: the required code and
armor atlas funding has not been qualified. Root retains the single Mesen queue.

## Exact earned event and present failure

The existing 239-byte upgrade worker is already live, byte for byte, in
CHR371 +000–0EE, resident raw2 C100–C1EE. Its live-layout SHA-256 is
`a939f70171c8258614fd3532741686a1f606252a34ccb395282a719498b54e28`.
The source is `tools/reference/steve_shatterhand_upgrades_1111.s`.

Three physical tokens complete the packed pattern after their HUD flight.
The ordinary token countdown starts at 80 hex and commits its grant when
31 hex decrements to 30 hex: 80 token decisions after countdown start.
The pattern table is 15, 2A, 25, 29, 1A, 16, 19, 26 hex for robot IDs 1–8.
Original bank12 92F0 clears the pattern and original projectile slots;
9300 masks the current actor with 3F. A matching nonzero robot sets robot
arrival/HP to 10 hex, cue 1D, player upgrade state 0D, and windup 7F.
Another or absent robot instead receives the new actor ID and cue 1E.

The current host worker enters that matching-robot branch, but its resident
`SteveArmorTransformTick` at C1BE has no ordinary companion caller. Once
state 0D is entered, `FirstBotActive` rejects Alpha, and LaserLifecycle clears
LaserActive before the companion caller returns on the nonzero state.
The player never receives active armor through this path.

Bounded direct loaded-code tests reproduced both supported cases:

| Robot / earned pattern | Actual CA00 companion updates | Final state / windup / armor timer | Transform calls |
| --- | ---: | --- | ---: |
| Alpha 1 / 15 hex | 144 | 0D / 7F / 00 | 0 |
| Laserbot 3 / 25 hex | 144 | 0D / 7F / 00 | 0 |

The grant occurs on update80 and remains stalled for64 more calls. These are
direct CPU fixtures that seed the matching robot and completed token pattern;
they do not establish controller-earned armor, rendered armor, or a Mesen run.
The fixtures execute the actual installed CA00 update, combat early dispatcher,
throw prelude, token grant, and Laser/Alpha state gates. The throw bridge is
loaded using its real scatter destinations rather than a contiguous copy.

Resident reconstruction used exact slices from the installed image:

| CHR source | CPU destination | Bytes |
| --- | --- | ---: |
| 371 +000 | C100 | 239 |
| 375 +000 | CA00 | 1,024 |
| 379 +000 | C500 | 1,024 |
| 336 +000 | D000 | 1,024 |
| 338 +000 | D400 | 1,024 |
| 167 +000 | DC00 | 1,024 |
| 304 +000 | AB00 | 1,024 |
| 306 +000 | D800 | 640 |
| 307 +300 | C980, C9CA, C4A0 | 74, 54, 96 |

All are plain in-memory arrays; native farcalls, rendering, NMI and IRQ are
not part of these fixtures. An initial incorrect pause-byte assertion and an
initial omitted Laser bridge were corrected before the passing loaded test.
Those fixture failures are not gameplay findings.

## State ownership that a live patch must connect

| Meaning | Existing resident address |
| --- | --- |
| Committed token pattern | C1F1 |
| Upgrade armor timer | C1F2 |
| Token countdown | C1F3 |
| Upgrade/transform state | C1F4 |
| Robot actor | C1F6 |
| Robot arrival / HP | C1F7 |
| Upgrade cue | C1F8 |
| Armor windup | C1F9 |
| Robot angle / index / age | C1FB / C1FC / C1FD |
| Upgrade animation / combo | C1FE / C1FF |
| Existing punch armor input | 5C85 |
| Existing punch selector / delay / phase | 5C80 / 5C81 / 5C82 |

The current punch worker reads a different armor input (5C85) from the token
worker's C1F2 timer. Calling the detached transform alone would leave ordinary
punches unarmored. Use one authoritative timer or a deliberate bridge, including
death, new-life, character-change, and room/stage reset handling.

The detached transform leaf also omits original 97F7's JSR B7B8 punch reset.
At windup underflow, original 97E7–980A clears selector 05A5, delay 05A4 and
phase 05B4 before publishing state0 and timer7F. The old paired test compares
upgrade fields only. Four bounded underflow comparisons, starting windup0–3,
confirm that the original clears seeded punch values9/7/2 while the detached
leaf retains them. Its upgrade fields still match. A composed live worker
must include the original reset and qualify the actual punch-owned addresses.

The matching grant also clears original projectile slots0700–070A before the
robot-match decision. The detached token leaf deliberately excludes that
native actor cleanup. A live armor entry must reconcile Alpha and Laser shot
slots, rather than leaving a newly hidden companion's projectiles frozen.

## Clock, warning, and complete exit

`check_steve_shatterhand_armor_clock_1111.py` passed again under the bounded
runner:1,064 clock cases and12 exit cases, including24 warnings,24 exit starts,
and84 decrements. The detached clock/exit/reset worker remains73 bytes,
SHA-256 `b900d4d982973e612a992c3043c35f368562987c5e5b89d4ead133b037a2d40b`.

Original 9191 runs from the committed frame counter, every16 frames. Timer2
resets the punch, starts state0F, queues24 and decrements to1. Timer1 retains
armor while requesting CHR warning57. States11 and higher freeze higher
timers. The separate state0F entry at9823 performs native support checking
and publishes the transform/hurt support timer20 before9829 clears armor and
effect actor060F, starts064C at10, and advances to state10.

The 73-byte leaf is not the entire exit. State10 at983B–9876 restores the
player animation (selector0 or6 from support), expands windup by4 up to7C,
waits until the robot has reached its angle band or is absent, counts064C
down, then calls8842 to clear player state and935C to reinitialize the robot.
The robot initializer restores HP10 and ageFF and clears its shot, animation,
pose and auxiliary fields. The current generic orbit always replaces its
radius from age and cannot simply stand in for this exit choreography.

Warning57 is an original CHR publication, not an implemented host warning
effect or an audible cue. The upgrade cues1D/24 currently have no mapped
audible consumer. Neither is qualified by the clock RAM comparison.

Armor also absorbs native player damage through its timer. Original bank12
9FB2 reduces the active timer by8 after the20-update hurt gate; original bank8
8354 reduces it by10 hex. Both clamp underflow to2 and otherwise OR with7,
without decrementing ordinary player health on those branches. The current
Mike-family damage path needs a source-verified adapter for the relevant host
contacts. A timer and palette alone would not implement armor's protection.

## Art and allocation budget

The original armor animation table is bank13 BBC9. Ordinary armored idle uses
pose00DA; walk uses00DE/E0/E2/E6/E8/E4; crouch uses00EA; vertical states use
00EC/EE. Ordinary armor attack poses are00C4/C6/C8,00CA/CC/CE and00D0/D2.
Pose00DC is another armored body record. Donor records and facings can be
read directly with `check_steve_shatterhand_lift_geometry_1111.parts`.

Those19 right-facing pose records require87 source8x16 cells across original
CHR76/77/78/79/82/83,86 unique cell payloads (2,752 bytes). The whole installed
CHR search finds only source83 tile1E, at physical278 tile18; that byte match
does not qualify its ownership, mapping, or reuse. There is no existing armor
atlas to expose by changing a pose flag.

A feasible packing target is three separately published1KiB body atlases:
source76+77 use31 cells,78+79 use24,82+83 use32 before payload deduplication.
Every listed pose stays within one such atlas. This is an art budget and layout
proposal, not an allocation grant. Transform effects, terminal/warning assets,
armor special attacks and any extra records can add requirements.

The current combat extension uses1,020 of1,024 bytes. The upgrade row's worker
uses239 of the240 bytes before its16 state bytes. The old detached transform
already occupies33 of those239 bytes. The current CHR710/711 item/robot art
and the funded death-cell aliases must remain intact. Four combat bytes and
one upgrade byte cannot hold the missing orchestration, complete exit, player
damage adapter and atlas selector. Do not overwrite occupied cells or treat
an all-zero row as proof of freedom.

## Concrete next integration

1. Qualify new carrier ownership for at least the armor code/records and the
   three body atlas rows, using the current finite selector census. Recover
   only exact ledger/source inputs in memory. Repack existing workers only
   after proving the executed instruction and asset equivalence.
2. Intercept the existing grant path before LaserLifecycle. Run state0D's
   original windup, punch reset and transform art; activate the authoritative
   timer at the original underflow. Keep all incoming native support and
   player-state calls balanced. Suspend/hide the companion in the source order
   and settle projectile cleanup on entry.
3. Call the clock once per committed ordinary update, map its warning to
   qualified host art, and implement both state0F and state10 through original
   robot reinitialization. Drive the player body selector and punch table from
   the same timer; qualify absorbed player damage and its timer cost.
4. Build composable preimage edits against the current installed bytes,
   recompute both authentication cookies, and prove cold-loader readback,
   NMI/IRQ cuts and actual foreign-owner overwrite/restore. Preserve the Prince
   packet and other characters. Merely reconstructing an old464c8 parent does
   not qualify a patch against later delivered changes.
5. Root should earn six matching symbols in gameplay, verify transform/active
   art, attacks, damage absorption, warning and companion restoration on
   expiry, then check pause/death/scene transitions and1-1. Physical emulator
   qualification and Downloads launch-context delivery remain root-owned.

Remaining robot actors2,4,5,6,7,8 are accepted by the source grant table but do
not have their original active attack/actor paths integrated. This audit adds
no alternate character or helper platform. Steve's existing1-1 helper
inventory is unchanged.

All source tests used
`python -B tools/audit/run_bounded_build_v1.py --output build/steve-armor-followup-1112 --max-files 1 --timeout 180 -- python -B ...`.
The existing clock checker was run directly through that wrapper; the two
additional audits used in-memory `-c` fixtures. Every completed invocation
reported zero output files. No historical tree was extracted, and no capture,
ROM candidate, backup, or patch file was created.
