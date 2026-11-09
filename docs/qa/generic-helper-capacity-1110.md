# Generic helper entry and slot capacity

The exact `f003b378` source audit covers all 35 native generic placements. The
proposed birth guard uses the original centers, projected left edges, initial
heights, widths, constructors, motion and retention intervals. The birth window
ends at camera-relative left X256. Its inclusive size for widths 16, 32 and 48
is 32, 24 and 16 pixels in Easy, and 25, 17 and 9 in Hard. The same post-scroll
scan can allocate during native engine `$0A`. It leaves an existing actor's
retention and phase untouched while the master timer is active.
[Helper source](../../tools/reference/generic_helper_camera_1110.s) ·
[Exact CPU and IRQ proof](../../build/generic-helper-camera-admission-1110/proof.json)

For WWF record 34 in 1-1, the initial left edge is X1376, center X1400, top
Y208 and width 48. The camera-left windows are X1105–1120 in Easy and
X1112–1120 in Hard. The exact enemy stream has two locally authored enemies
at X1280 and X1312. The preceding group is authored at X864 and can be
constructed no farther right than X888, before the X912 pipe. That is an
origin bound. The earlier WWF route receipts record carry and crossing.
Native pickups also need
counting. The area can supply a hidden 1-up at X1024 and a second power-up
block at X1248. Earlier survivors and missed or collected pickups depend on
actual play. The private replay observer records six native slots before
birth, real constructor geometry, first visible edge, and subsequent carry.
[WWF crossing scope](helper-platform-inventory-1101.md) ·
[Exact stream source](../../src/level_tiles.s) ·
[Native observer](../../tools/audit/wwf_generic_helper_entry_1110.lua)

On private candidate
`dad683110311fa7925dcc4c2ce0aff3bb645d5c51b1a68b2d5c0731052850e73`, Hogan
passed the controller-only Easy replay into active 1-2, with both lives.
The physical native constructor ran once, on frame 4409 in slot 5. At birth,
the left edge was X1376, Y208, and the camera covered X1105–1360. One of
the six slots was occupied before birth. At first visible entry on frame
4536, the same actor's moving left edge was X1406, equal to camera-right.
The controller recorded 72 native carry calls and crossed the X1376–1424
pit. This witnesses one Easy Hogan admission and crossing.
[ROM and run binding](../../build/generic-helper-wwf-native-1110/wwf/capture/binding.json) ·
[Constructor, six slots, and visible entry](../../build/generic-helper-wwf-native-1110/wwf/capture/helper-entry.json) ·
[Full route result](../../build/generic-helper-wwf-native-1110/wwf/capture/result.json)

On the same private image, Easy Scrooge reached active 3-4 with both lives
intact. Record 11 constructed once at world left X2344, center X2352, top
Y64 and width 16. On frame 3190 the camera covered X2057–2312 and five of
six slots were occupied before the constructor used slot 0. The platform
first appeared on frame 3276 with its moving left edge and the camera's
right edge both at X2373. A second route repeated that exact entry, then
used the stock pulley and pogo to board record 11. The native actor recorded
21 carries, six while moving. Scrooge departed and reached active 3-4 with
both lives. Stage select was used and all other cheats were off.
[Controller-only 3-3 evidence](../../build/generic-helper-3-3-native-1110-v7/capture/result.json)

Natural capacity is still open across the complete roster and stage set.
The stream-origin recensus uses camera-left minus 73 at first Easy eligibility
through the last offscreen camera-right plus 48, rounded down to a 16-pixel
column. For 3-2 it includes two three-member groups at nominal X2912 and
X3056 before the helper at left X3272. For 3-3 it includes two Koopas and
three platforms at X1984, X2016, X2112, X2176 and X2240 before the helper at
left X2344. Four drop platforms fall in the window for the 6-3 helper at
left X2600. These counts describe authored origins and group multiplicity.
Native group construction caps its own admissions at slots 0–4, and pickups,
frenzy objects and some guest attacks can occupy slot 5. In particular,
Darkwing's native arrow allocator uses the same actor pool. Water and castle
records need their actual special actor and room timing considered as well.
[Shared placements](helper-platform-inventory-1101.md) ·
[Native parser](../../src/level_tiles.s) ·
[Native arrow allocator](../../src/darkwing_weapons.s)

The six-slot CPU control fills every slot through WWF's complete Easy window,
then frees one at camera-left X1121. The previous code spawns a visible lift.
The guarded code declines allocation. Natural occurrence of that capacity
tradeoff remains unverified. A natural witness
must cover all six flags and positions from first eligibility through entry.
If an existing actor naturally clears a slot while the lift is still offscreen,
an end-of-enemy-loop retry could use that slot without evicting an actor. If
all six remain live until entry, guaranteed construction would require more
capacity or an earlier reservation with its effect on authored admissions
qualified. Later-stage crossings require their own native qualification.

## Next controller witnesses

Both 3-2 and 3-3 use the H mask in Easy and Hard. The affected families and
alternates are Mega Man and Proto Man, Samus and Rogue Dawn, Bill and Lance,
Link and Zelda II Link, Simon, Grant, Sypha and Alucard, Pit and GB Pit,
Rygar, Ryu, Scrooge and Darkwing Duck, Kirby and Meta Knight, Chip and Dale,
Little Mac, Doc Louis and Mike Tyson, Mike Jones, Popo and Nana, and Alex and
Ryan. WWF's separate H-independent record applies to Hulk Hogan, Ted DiBiase,
Bam Bam Bigelow, Honky Tonk Man, Randy Savage, and André the Giant.
[Exact family masks and record gates](../../build/wwf-helper-stable-1102-v2/source.s) ·
[Named inventory](helper-platform-inventory-1101.md)

| Stage | Actual loaded area | Camera-left birth window, Easy / Hard |
| --- | --- | --- |
| 3-2 | `$35` | X2985–3016 / X2992–3016 |
| 3-3 | `$20` | X2057–2088 / X2064–2088 |

Use the game's **Options → Cheats → Start Level** row to launch these
stages. The real menu sets `$7FFC` to `$29` for 3-2 or `$2A` for 3-3, and
character confirmation applies the corresponding world, stage, and area.
From the default selector value, press Right nine or ten times on that row.
Leave the other five cheat toggles off (`$7FFB=0`). Check the selected
character, alternate, mode and loaded area before recording active play.
The existing Sound/Cheats controller demonstrates the menu entry and genuine
controller pulses. Its audio and extra cheat tests are outside this route.
[Controller menu fixture](../../tools/audit/sound_cheats_menu_native_v1.lua) ·
[Native start-level apply](../../src/cheats.s#L160) ·
[World 3 area table](../../src/common.s#L648)

For a regular stage-select control, use Scrooge and reuse the terrain and
jump probes from the campaign navigation policy. For additional slot pressure,
use Darkwing Duck with genuine Arrow attachments. The Arrow observer already
validates ID `$26` against the shot's native slot and owner tag. The existing
Darkwing route scripts switch to an untuned fallback outside 1-1. Reuse their
Arrow input phases and observer fields with stage-specific wall and landing
probes. Prove an earned adaptor and gas on the normal-play branch. A separate
Full Power run can exercise allocator pressure through the real menu, with
the cheat scope recorded explicitly. The compact 1-1 harness asserts a
default start and all cheats off, so its menu and terminal policy need a
stage-select variant before either case can run.
[Campaign terrain probes](../../tools/playthroughs/mario_luigi_scrooge_nav.lua) ·
[Arrow controls](../../tools/playthroughs/current_roster_darkwing_arrow_v5.lua) ·
[Native Arrow observer](../../tools/audit/current_darkwing_resource_observer_v2.lua) ·
[Compact harness](../../tools/audit/current_roster_compact_11_v1.lua)
