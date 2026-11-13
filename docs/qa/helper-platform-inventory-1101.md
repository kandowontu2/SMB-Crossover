# Helper platform inventory — functional pass in progress

The functional roster pass is not complete. This inventory separates source
placements from actual route verification; it is not the final all-character list.

## November 13 Thomas hidden 1UP access

Thomas now has eight native vertical lifts in World 1-1, all actor `$25`,
width32 and initial top Y192. Their initial left edges are X400, X560,
X688, X864, **X1008**, X1200, X2560 and X2816; corresponding centers are
X416, X576, X704, X880, **X1024**, X1216, X2576 and X2832. The new X1008
lift is below the authored hidden 1UP. No other character or alternate is
affected by this placement.

Actual Mesen on candidate `65ee94ca` observes its offscreen construction
at relative left287, boarding at player X1023/Y152, a fresh original jump,
the real hidden-block hit at X1026/Y139, native emergence/collection and
exactly one awarded life (2 to3). Receipt
`3035b17ea05fa4600ea64238fbbd59dc03a83fd680404c210e597392b5565cf3`.
A separate full-stage run earns mushroom, flower and Star, uses the six
pipe assists plus the flower lift, and enters active1-2 with both lives at
frame8914. Receipt
`0ce772a418109ffd070ea0c1d5b29d6ba290ea1f21757246c3a7ff9f3737f3de`.
See `thomas-oneup-lift-1113.md`. The older notes below retain the earlier
seven-record and six-record verification scopes.

## November 13 Thomas flower access

Thomas receives a seventh native vertical platform in World 1-1 at the
authored flower approach. Its **initial left edge is X1200, center X1216,
initial top Y192, width32**, actor `$25`. The existing manager constructs it
offscreen using the 256..287-pixel camera window and available native slots.
Mesen observed birth in slot4 at camera left X913, relative left287, followed
by boarding at player X1214/Y158, departure at X1216/Y96 and natural flower
collection at X1261/Y112. Both powerup transactions and resumed movement pass.
The first four original pipe crossings also pass on this candidate. The
current full-stage replay's first-pit failure is under investigation.
See `thomas-flower-lift-1112.md` for exact ROM and replay hashes.

A later ordinary-controller run on installed `318a0877` crosses that first
pit and then collects the authored Star after the mushroom and flower.
Both lives remain at frame4746. The successful input-poll timing is in
`replay_thomas_star_1113.py`. Receipt
`a69f4b97d08a557a0120452b1c3a092fb4d5b61038fe4cc2a1f2362311d93f47`
qualifies this route segment. The complete current stage and natural1UP
checks continue separately.

The complete run on the same installed `318a0877` subsequently passes at
frame8823, entering active1-2 at X40/Y48 with status2 and both lives. It
collects the mushroom, flower and Star and boards all six original pipe
lifts plus the flower lift. The two late lifts at left X2560 and X2816,
centers X2576 and X2832, initial top Y192, each construct at relative287
before the viewport. Their native contacts and departures are recorded.
Receipt `081b1c56d079d2976086e4d841c54f3d177438d39cc35f581ad4d919778bb06c`
uses script `22a1ba43bb5b517c15b30843d4527cc3ba2f310c73fd8434daa8dfeda09b49c8`.
Natural1UP access remains a separate private eighth-platform candidate.

## November 12 current WWF route recheck

On installed ROM `8fc57b8b4268a47f8a906af8b5813834bbf76ca7376d1d12767d510708da9582`,
Hulk Hogan, Ted DiBiase, Bam Bam Bigelow, Honky Tonk Man, Randy Savage and
Andre the Giant each cleared non-shortcut 1-1 into active 1-2 with both lives.
Each used the existing native horizontal platform at **1-1, initial left
X1376, center X1400, initial top Y208, width48**. Native carry counts were
70, 64, 62, 63, 64 and 65 respectively. No platform was added or relocated.
Receipts and controller qualifications are in `roster-stage-regressions-1112.md`.
This confirms the assisted crossing for all six on the current build; both
difficulty modes and every powerup remain separate unfinished checks.

Earlier shared-record inventory fixture SHA256:
`128915e97e78891a585aa8f9fd904c166ca64dcd6dd1ee395fc68fd505c1e72c`.
Earlier Jay route ROM SHA256:
`4df817587ea5b0aff3f278a4201976745bad4d9dd1b2a99d6cb5fd3b9c74dadc`.

The `2d7fb6e6` nightly retains the helper placements below. Its Mesen replay
gets Prince of Persia (Excitebike, Select once) through all six pipes, three
gaps, the final staircase and the native flagpole, then into active 1-2 with
both lives. Prince uses no helpers. [Prince full replay](prince-native-flag-delivery-1111.md)

Jay McCray (Mike Jones, Select once) uses two stock 32-pixel-wide vertical
platforms in 1-1. Mesen verified offscreen admission, visible entry at
relative X255, both rides, and a clear into active 1-2 with both lives.
[Jay delivery](jay-silius-scrolling-delivery-1111.md)

| World 1-1 location | World left X | Center X | Initial top Y |
|---|---:|---:|---:|
| Third pipe, ascent | 688 | 704 | 192 |
| Fourth pipe, ascent | 880 | 896 | 192 |

Donkey Kong Jr. (Donkey Kong, Select once) has twelve stock 32-pixel-wide
vertical girders and one stock 48-pixel-wide horizontal platform in World 1-1.
Mesen verified a continuous clear through all six pipes, all three gaps,
the flagpole and active 1-2 with both lives. The first and third gaps required
no platform. [Full delivery](dkjr-full-nightly-delivery-1111.md)

| Pipe | World left X | Center X | Initial top Y |
|---|---:|---:|---:|
| First, ascent | 416 | 432 | 192 |
| First, descent | 480 | 496 | 192 |
| Second, ascent | 560 | 576 | 192 |
| Second, descent | 624 | 640 | 192 |
| Third, ascent | 688 | 704 | 192 |
| Third, descent | 752 | 768 | 192 |
| Fourth, ascent | 880 | 896 | 192 |
| Fourth, descent | 944 | 960 | 192 |
| Fifth, ascent | 2576 | 2592 | 192 |
| Fifth, descent | 2640 | 2656 | 192 |
| Sixth, ascent | 2832 | 2848 | 192 |
| Flagpole approach, staircase descent | 3040 | 3056 | 192 |

| Gap | World left X | Center X | Initial top Y | Width | Actor |
|---|---:|---:|---:|---:|---|
| Second, pit X1376–1423 | 1408 | 1432 | 208 | 48 | Stock horizontal `$28` |

The horizontal platform spawns at camera-left X1121. Its left edge first
enters screen bounds at X1397 with camera-left X1143. Donkey Kong Jr. lands
on it at X1393 and reaches the far side at X1425/Y176.

The [SMB2 preview update](smb2-menu-tier-isolation-1110.md) changes menu
power state and uses no new helper platforms.
Prince of Persia (Excitebike Select 1) clears four authored pipes and the first
two gaps in 1-1 with his original jump and climb. This route uses zero helper
platforms. [Prince delivery](prince-native-pipe-gap-delivery-1110.md)
Sonic now uses his original Master System movement and clears 1-1 in Mesen
with two lives and zero helper platforms. His menu location is row 4, column 2,
Mr. Gimmick Select 3. [Sonic delivery](sonic-original-delivery-1110.md)
The [earned mushroom and injury update](sonic-earned-injury-delivery-1110.md)
uses zero helpers and repeats the Prince four-pipe/two-gap route.
The WWF pickup and secondary-palette repair changes none of the six wrestlers'
existing helpers or summon controls. All-six actual mushroom/recovery checks
are documented in the [current delivery report](wwf-pickup-palette-delivery-1110.md);
these are not new full-stage assisted-crossing proofs.
The Thomas mushroom admission/progression repair changes none of his existing
six helpers. Its actual earned-pickup result is in the
[Thomas delivery report](thomas-physical-delivery-1110.md).
The November10 Excitebike progression repair changes no helper actor,
admission, location or movement. Its actual earned-pickup run is documented
in [the delivery report](excitebike-physical-delivery-1110.md).

**Current delivered Level 2 controls:** Mini Mario, Karnov, all six WWF
wrestlers and all four Final Fantasy classes have Up + Select vertical and
Down + Select horizontal summons. Horizontal begins to the right, travels
112 world pixels, then goes back and forth. The axes have separate ownership;
a fresh chord replaces only its own platform type. See the November 10 tables
at the end for all names, initial world left edges, centers and heights.
Native carrying/oscillation tests pass; every character's assisted pit/full
stage route remains a separate qualification.

The entries below retain their recorded build hashes and chronology. A
historical paragraph's use of “current” describes that paragraph's build,
not a newer test result. The final November 10 section records this delivery.

The Giant nightly repeats Mini's actual Downloads 1-1 clear, boarding all three
existing lifts with unchanged positions and timing. It adds no Giant helper.
[Delivery receipt](../../build/mega-giant-delivery-1110/verified-delivery.json)

Delivered user-requested assistance: Mini Mario and Karnov, Up + Select to spawn
or replace one small vertical platform directly below the player. This is a
dynamic player-position placement, not a fixed stage coordinate. Both controls
were replayed from the actual Downloads launch in build `9906787a`; the
vertical controls remain available in the current nightly alongside the
subsequent horizontal and roster extensions.

Implementation `00cf5481231239967994bd3ad69ea65fe9f02c7dc74560a997d3722ad6a4566c`
passed actual native input, carrying and replacement checks for both owners.
The current nightly includes that implementation plus the title credit, with
identical manual-platform implementation. The latest Giant impact repair also
passed Mini's normal 1-1 regression with 3,494 updates / 3,494 gameplay frames,
zero lag NMIs, and no new helper placements.
[Verified delivery](../../build/manual-title-delivery-v2-1110/verified-delivery.json)
The control is available in ordinary gameplay, not restricted to stage 1-2.
It uses native actor `$25`, width 32 pixels, and replaces only its own manual
platform. A full actor pool queues the request until a slot is available.

| Character | Initial left edge | Initial center | Initial top | Native 1-1 observed births (left, center, top) |
|---|---|---|---|---|
| Mini Mario | Player world X − 12, clamped at zero | Left + 16 | Native player Y + 32 | (28, 44, 208), then (37, 53, 119) |
| Karnov | Player world X − 8, clamped at zero | Left + 16 | Native player Y + 32 | (32, 48, 208), then (59, 75, 110) |

These are initial placements at the button press, not later moving-platform
positions. Existing fixed helpers are retained. Evidence is in
`build/manual-platform-native-1110/{mini,karnov}/capture/result.json`.

The shared side-collision update repeats the actual Downloads Mini 1-1 route,
including offscreen construction and boarding all three lifts, with the same
coordinates and timing. [Delivery receipt](../../build/shared-side-tank-delivery-1110/verified-delivery.json)

The shared draw successor repeats Mini's full Downloads 1-1 replay and all
three offscreen constructions and assisted crossings. Their placements are
unchanged. [Delivery receipt](../../build/shared-sparse-draw-delivery-1110/verified-delivery.json)

The current Mini successor admits its native lifts at camera-relative left
X256–263, before they are visible, and also checks admission after scrolling
during native injury. The actual earned-mushroom damage replay constructed the
third lift at relative X263 and reached its visible edge in the same injury,
retaining both lives. The full Downloads 1-1 replay boards and crosses all three.
Their authored left edges remain X560, X688, and X864; centers remain X576,
X704, and X880, initial top Y192 and width32. The natural 1-1 slot bound and
injury timing audit are in [the capacity note](mini-helper-slot-capacity-1110.md).
This is not a guarantee for artificially saturated actor RAM.

Camera-entry fixes are delivered. Full native routes on parent `f2050c19` verify
Mini's three lifts, Thomas's six lifts, and both Goku/Karnov lifts spawning at
relative X286–287, followed by actual support and assisted crossings into 1-2.
The earlier `d998e71b` successor preserved the camera admission and placement bytes.
It shortens Mini's already-seen helper path and source-qualifies native actor
bounds across all seven platform types; actual construction remains unchanged. Its actual Downloads launch
repeats Mini's route and matches audio and helper evidence. Goku/Karnov retain
separate native slots for their two lifts.
The shared generic manager, including WWF, already uses a camera margin.
No placement coordinates changed. This is not new native coverage of every
shared roster alternate or every later stage. The separate
[scope audit](helper-camera-scope-1110.md) records the native-slot capacity
constraint; no natural full-slot entry-window failure has been witnessed.
On the actual `f33c7b19` Downloads ROM, Easy Scrooge's 3-2 native `$28` lift
was constructed 30 pixels beyond the right edge with three of six actor slots
occupied. Its initial left edge was X3272, center X3280 and top Y64. The
moving left edge first entered at X3284, exactly at camera-right. Scrooge
reached active 3-3 with both lives on a route that passed below the lift.
[Downloads replay](../../build/current-helper-3-2-entry-1110/capture/result.json)
The private generic guard has an Easy Scrooge scroll-in witness for 3-3.
The native horizontal lift began at left X2344, center X2352 and top Y64.
It first appeared at the right edge of the camera. Scrooge rode the lift
with 21 native carry calls, then cleared to 3-4 with both lives.
The exact released `c8bd2e2c` cartridge independently passed the same Easy
Scrooge controller route using the released generic manager. With five of six
slots occupied, the native 16-pixel `$28` lift began at left X2344, center
X2352 and top Y64, 32 pixels past camera-right X2312. Its moving left edge
first entered at X2373, matching camera-right. Scrooge rode it for 21 native
carry calls, six while moving, and reached active 3-4 with both lives.
[Released-cartridge result](../../build/current-helper-3-3-1110/capture/result.json)
Easy Kirby also verified scroll-in for the 6-3 native horizontal lift at
initial left X2600, center X2608 and top Y64. Its moving left edge was one
pixel inside the screen at first visibility. That route reached entry with
both lives and did not test a full actor pool.
[Entry and capacity evidence](generic-helper-capacity-1110.md)
Bub/Bob added no helper platforms. Earlier route proofs below retain their stated hashes.
Thomas's two late placements were added on d0b445a7; other placements are unchanged. The original admission fixture belongs to its stated earlier hash.
`tools/audit/inventory_named_helpers_1101_v2.py` verified identical installed and
candidate bytes, read all 34 compiled shared records and executed `HpConfigure`
in 80 cases: raw owners 0–36 in both modes, plus Grant/Sypha/Alucard. These are
admission tests, not native assisted-crossing or complete-route tests.

| Characters / scope | Stage | Placement | Native behavior | Verification remaining |
|---|---|---|---|---|
| Mega Man, Proto Man; Samus, Rogue Dawn; Bill, Lance; Link, Zelda II Link; Simon, Grant, Sypha, Alucard; Pit, GB Pit; Rygar; Ryu; Scrooge, Darkwing Duck; Kirby, Meta Knight; Chip, Dale; Little Mac, Doc Louis, Mike Tyson; Mike Jones; Popo, Nana; Alex, Ryan | 1-1 | Center X=3104, **native left edge=3096**, initial Y=64, width=16 pixels, near end staircase/flagpole | Native horizontal actor `$28` | Both modes admit the same helper; current alternate-by-alternate assisted crossings pending |
| Goku and Karnov | 1-1 | Centers X=704 and 888; left edges 688 and 872; initial Y=208; width=32 | Existing native vertical platforms, actor `$25`, separate owned slots | Both full routes and both offscreen constructions/contact/crossings pass on `f2050c19`, no life lost; native both-mode coverage remains open |
| Thomas | 1-1 | Left edges X=400,560,688,864,2560,2816; centers X=416,576,704,880,2576,2832; initial Y=192; width=32 | Existing native vertical platform, actor `$25` | All six offscreen constructions and assisted crossings, full non-shortcut1-1 into1-2 pass on `f2050c19`, no life loss. Both modes/all powerups remain open. |

Coordinates are world pixels. Initial/authored Y is not a fixed platform height:
the platform moves. Center coordinates and left-edge coordinates are explicitly
distinguished to avoid a 16-pixel ambiguity. Thomas's placements assist pipes
at X=448,608,736,912,2608,2864. Goku/Karnov's two placements assist pipes736/912.

Machine-readable current output: `build/helper-named-inventory-1101-v2/inventory.json`.
Metal Storm now has a controller-only full non-shortcut1-1 clear on this ROM,
including the transition to active1-2, without added or shared helper platforms.
The November2 successor repeats the full route in5587frames, lives2→2, with repaired sprite reservation. See `docs/qa/metal-reservation-1102-v42.md`. Powerup/mode checks remain unfinished.

The shared width field counts 8-pixel tiles. `HpProjectPosition` subtracts
`Width * 4` from the center: shared width 2 therefore means a 16-pixel platform,
with its native left edge 8 pixels left of center. Do not use the separate
32-pixel Goku/Karnov lift's 16-pixel subtraction for shared records.

All named 1-1 placements above apply in **both Easy and Hard**. Only
`Cv3Variant` changes the shared alternate mask; other same-owner alternates
inherit it without an individual ability check. High raw IDs are excluded from
shared admission, so Shinobi/Metal Storm do not inherit Ryu/Sophia helpers.
Karnov and Thomas use separate native managers. Karnov's current controller-only
run clears all 1-1; see
`docs/qa/checkpoints/2026-11-02/karnov-full11-v6/receipt.json`.
No additional impossible crossing was proven by this read-only audit, and no
platforms were added. Shinobi's opening-pipe failure is still being diagnosed;
it is not evidence yet that a helper is needed.

Excitebike (raw37, slot29 base alternate) has no added or inherited helper in
the `current4.nes` candidate (`cf1412eb`). Its source motor/lean jump reaches
61px in CPU and native controls. A genuine controller run crosses all four
pipes and three gaps, reaching active 1-2 with no life loss. Both 64px pipes
record native top support; the third has static left X736, width32, top Y144
and rider top Y112. No helper stage, height or world position has been assigned.
The slot29 Prince alternate remains locked and has no helper.

On November3, the private Bub/Bob upgrade candidate
`b7e2a161ea2781a8346b126b9c759f7c60f2583e2a18e58f8ca888d041c0bd53`
clears the full non-shortcut1-1 for **both Bub and Bob without any helper**.
Each naturally earns six original bubble rides, clears all four pipes and three
gaps, and reaches active1-2 with two lives unchanged. Bub takes13,540 physical
frames; Bob takes13,510. These are original character abilities, not native
helper-platform placements. See
`docs/qa/checkpoints/2026-11-03/bub-upgrade-full11-v80/receipt.json`.
The candidate remains private while its head-block/powerup bridge is repaired.

The November3 successor `cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd`
also clears the complete route for both identities without helpers: Bub13,460
frames and Bob13,513, each with17 natural pops, six original bubble rides and
two lives unchanged. Separate controller runs collect a naturally released
mushroom and complete its animation/source speed upgrade for each identity.
See `docs/qa/checkpoints/2026-11-03/bub-earned-native-v90/receipt.json`.
Flower and final interrupt/Downloads qualification remain open; these results
do not change the installed nightly or any platform placement.

Hogan crosses all four 1-1 pipes and the first pit without helpers under
the later-edge controller. The next opening pit still fails: the x+8
launch starts at world X1368, rises from Y176 to Y110, and falls at X1412.
Waiting until x+4 loses ground support before a second jump can begin.
Original directional attacks and helper placement remain under review.
The historical verified build (`f5c30cea`)
adds one existing native horizontal actor `$28` for all six WWF identities in
1-1 / area `$25`: **initial center X=1400, initial left edge X=1376,
initial Y=208, width=48 pixels**. Hogan crossed the authored X1376–1424 pit
with 72 actual native platform-carry calls and reached the castle without
losing a life. A longer terminal wait verifies the full transition to active
1-2 in 12,277 physical frames, lives2→2, with 15 native enemy defeats.
Ted DiBiase, Bam Bam Bigelow, Honky Tonk Man, and Randy Savage also reach
active 1-2 without losing a life (11,938 / 12,372 / 12,337 / 12,307 physical
frames). Their native platform-carry counts are 72 / 72 / 72 / 75.
Andre now also reaches active 1-2 without losing a life in 11,172 physical
frames, defeating 13 enemies and recording 64 native platform-carry calls.
His original walking action must retire before a fresh punch press; two
neutral source updates fixed the test controller, with no ROM change.
All six wrestlers have full-route evidence on this exact nightly. Both modes
admit the platform; these route checks do not establish both-mode qualification.
The actual Downloads launch repeats Hogan's full clear in 12,277 frames.
Karnov's separate lifts still cross both tall pipes and the first gap,
grounded at X1156 with no life loss; this is not a full Karnov clear.
Evidence: `build/wwf-helper-stable-1102-v2/native-hogan3/capture/`.
Native death recovery is verified for all six wrestlers. The earlier unfinished
gap diagnostic in `docs/qa/checkpoints/2026-11-02/hogan-gaps-v5/receipt.json`
is superseded by the complete routes described above.

## Later-stage shared placements

**H** means every named character/alternate in the first table row above.
**V** means Mega Man/Proto Man; Bill/Lance; Link/Zelda II Link;
Grant/Sypha/Alucard; Sophia; Scrooge/Darkwing Duck; Kirby/Meta Knight;
Chip/Dale; Little Mac/Doc Louis/Mike Tyson; Mike Jones; Alex/Ryan.
**O** means raw owners 0–5, including their same-owner alternates: Mario and
raw-0 variants, Mega Man/Proto Man, Samus/Rogue Dawn, Bill/Lance,
Link/Zelda II Link, Simon/Grant/Sypha/Alucard. Luigi is raw 8 and is excluded.
The actual compiled menu cycle resolves Mario(variant0), Supermaaa(2),
Kamikaze Mario(3), Celeste Mario(4), Toad(5), Peach(6), and Mario the Tank(7)
to raw0; Luigi(1) resolves to raw8. Sonic is not in this Mario cycle and is
not assigned raw0 by this inventory. Menu readiness remains a separate concern.
A dash means absent in that mode.

All coordinates and widths below are pixels. Area IDs distinguish a reused
outdoor exit from the main underground/water area. Gate group is independent
of motion axis: records 4 and 22 move vertically but admit H.

| Record | Stage / area | Center X / native left X | Initial Y | Width | Motion | Easy / Hard |
|---|---|---|---|---|---|---|
| 0 | 1-1 / $25 | 3104 / 3096 | 64 | 16 | H | H / H |
| 1 | 1-2 / $25 | 3104 / 3096 | 64 | 16 | H | H / H |
| 2 | 1-3 / $26 | 2368 / 2360 | 64 | 16 | H | H / H |
| 3 | 2-1 / $28 | 3136 / 3128 | 64 | 16 | H | H / H |
| 4 | 2-2 / $01 | 2568 / 2544 | 160 | 48 | V | H / H |
| 5 | 2-2 / $01 | 2168 / 2144 | 208 | 48 | H | H / H |
| 6 | 2-2 / $25 | 3104 / 3096 | 64 | 16 | H | H / H |
| 7 | 2-3 / $27 | 3536 / 3528 | 64 | 16 | H | H / H |
| 8 | 2-3 / $27 | 1744 / 1736 | 208 | 16 | H | — / H |
| 9 | 3-1 / $24 | 3136 / 3128 | 64 | 16 | H | H / H |
| 10 | 3-2 / $35 | 3280 / 3272 | 64 | 16 | H | H / H |
| 11 | 3-3 / $20 | 2352 / 2344 | 64 | 16 | H | H / H |
| 12 | 4-1 / $22 | 3536 / 3528 | 64 | 16 | H | H / H |
| 13 | 4-2 / $25 | 3104 / 3096 | 64 | 16 | H | H / H |
| 14 | 4-3 / $2c | 2288 / 2280 | 64 | 16 | H | H / H |
| 15 | 5-1 / $2a | 3120 / 3112 | 64 | 16 | H | H / H |
| 16 | 5-2 / $31 | 3136 / 3128 | 64 | 16 | H | H / H |
| 17 | 5-3 / $26 | 2368 / 2360 | 64 | 16 | H | H / H |
| 18 | 6-1 / $2e | 2912 / 2904 | 64 | 16 | H | H / H |
| 19 | 6-2 / $23 | 3392 / 3384 | 64 | 16 | H | H / H |
| 20 | 6-3 / $2d | 2608 / 2600 | 64 | 16 | H | H / H |
| 21 | 7-1 / $33 | 2800 / 2792 | 64 | 16 | H | H / H |
| 22 | 7-2 / $01 | 2568 / 2552 | 160 | 32 | V | H / H |
| 23 | 7-2 / $01 | 2168 / 2152 | 208 | 32 | H | H / H |
| 24 | 7-2 / $25 | 3104 / 3096 | 64 | 16 | H | H / H |
| 25 | 7-3 / $27 | 3536 / 3528 | 64 | 16 | H | H / H |
| 26 | 7-3 / $27 | 1744 / 1736 | 208 | 16 | H | — / H |
| 27 | 8-1 / $30 | 5952 / 5944 | 64 | 16 | H | H / H |
| 28 | 8-1 / $30 | 3584 / 3576 | 208 | 16 | H | O / H |
| 29 | 8-1 / $30 | 5064 / 5056 | 208 | 16 | H | — / H |
| 30 | 8-2 / $32 | 3392 / 3384 | 64 | 16 | H | H / H |
| 31 | 8-2 / $32 | 2416 / 2408 | 192 | 16 | H | O / H |
| 32 | 8-3 / $21 | 3360 / 3352 | 64 | 16 | H | H / H |
| 33 | 8-4 / $65 | 4472 / 4464 | 208 | 16 | H | O / V |

Sources: `src/crossover_helpers.s`, `src/crossover_helper_data.inc`,
`src/crossover_helper_data.json`,
`tools/audit/prepare_karnov_native_platform_1101_v1.py`,
`tools/prepare_dragon_power_two_platforms_v1.py`, and
`tools/reference/thomas_pipe_lifts_v1.s`.

Remaining: native assisted-crossing checks for every named alternate and mode,
later-stage activation, and full-route evidence. This inventory does not claim
that characters without current helpers will never need one. Refresh it after
any helper or raw-owner change.

November 2 Karnov: the current `f5c30cea` ROM reaches active 1-2 in 9,908
gameplay-observer frames with no life change or death. The controller uses
original crouch shots, waits for overhead Goombas, and lands on the final
stair before jumping the third pit. Existing native pipe lifts are retained;
no new platform, physics or ROM change was needed. This is a non-shortcut
route, not every powerup or both modes. Evidence:
`docs/qa/checkpoints/2026-11-02/karnov-full11-v6/receipt.json`.

Native 1-1 addendum: Shinobi now clears the entire stage into active 1-2 on installed 933c0650, in 8462 physical frames, lives 2 to 2, without helpers. Tall-pipe takeoffs at 692/868 and later gap input were sufficient with original motion. Metal Storm also clears on this hash in 5498 frames, lives 2 to 2, without helpers. These are stage-specific results; exact Shinobi body-policy review remains open.

Arthur on cumulative c3dd0303 also clears 1-1 into active 1-2 in 6107 physical frames, lives 2 to 2, without helpers. His intended second jump press is required. This covers Arthur only, not his Goku alternate.

With original pose-based contact bounds installed in 6f319d20, Shinobi again clears 1-1 into active 1-2 without helpers (8924 physical frames, lives 2 to 2). Arthur also passes on this exact ROM in 6107 frames without helpers.

November2: current nightly379590 adds playable Excitebike. No helper platforms were added; its full1-1/tall-pipe qualification is still open. The source placements listed above are unchanged.

Arthur now clears full non-shortcut1-1 into active1-2 on d8a87050 in5950 physical frames, lives2to2, with no source injury or helpers. The source weapon-tail callback repair lets his real lances damage native enemies; his original side probes and jumps remain unchanged.

Excitebike now clears full non-shortcut 1-1 into active 1-2 on cf1412eb in 6996 physical frames, lives 2 → 2, all four pipes and three gaps, with no added or inherited helpers. Third and fourth 64px pipe support contacts are recorded in the native receipt.

Goku now clears full non-shortcut Hard 1-1 into active 1-2 on `22d09909`
in 5,837 physical frames / 4,033 gameplay updates, lives 2 → 2. The controller
uses the existing two vertical pipe lifts listed above, and takes off later
at the X1376–1424 gap. No platform or physics change was required. This proves
that route, not every powerup or Easy mode. Evidence:
`build/goku-gap-1102-v4/native/capture/result.json` and
`docs/qa/goku-current-full11-1102.md`.

November 3: Mini Mario (Mario Select alternate8/raw41) on nightly `ca90e8be`
uses no helper platforms. A controller-only non-shortcut 1-1 run crosses the
four pipes at X448–480, X608–640, X736–768 and X912–944, and the gaps at
X1104–1136, X1376–1424 and X2448–2480, with lives2to2. Three wall-cling/jump
restarts use his explicit traversal adaptation. These coordinates describe
the native obstacles, not new platform placements; there are no helper left
edges, centers or initial heights to report for Mini. The run completes the
flagpole/castle sequence and reaches active 1-2 in 7,875 physical frames.
Evidence: `docs/qa/checkpoints/2026-11-03/mini-end-v50/receipt.json`.

The November 3 mushroom repair `9d291cb7` repeats the complete Mini route into
active 1-2, lives 2 to 2, with the same obstacle crossings and no helpers.
The separate earned mushroom run also passes from Downloads. Prince remains
private. The November 3 first-pipe runs stop at the first Goomba. See `roster-resume-v62/receipt.json`
under the November 3 checkpoints for the positive and negative scope.

November 8: Prince private `b6df037e` clears the first Goomba with all five HP
using the original running jump. The climb animation starts at the first pipe,
but the host alignment lands left of the pipe at X448. No Prince helper has
been placed and no assisted crossing has been verified. The source alignment
trace is in `build/prince-climb-trace-1108/capture/prince-diagnostic.json`.

Goku's Hard replay on the installed `244734bb` nightly reaches active 1-2 in
5,999 physical frames and 4,096 gameplay updates with lives 2 → 2. The controller
waits for grounded takeoff at X2434 or later before the final gap. It uses the
existing native `$25` lifts in 1-1 at initial Y208, centers X704 and X888,
left edges X688 and X872. No placement or ROM byte changed. Evidence is in
`build/goku-current-last-gap-1108/capture/result.json`.

November 8 Mini Mario (Mario Select alternate 8, raw 41) nightly `fc7d4554`
replaces the wall grab with three existing native `$25` vertical
girder actors. The controller-only run boarded and jumped from each, cleared
the four pipes and three gaps, and reached active 1-2 with lives 2 → 2 and zero
wall-jump restarts. Each girder is 32 pixels wide.

| Stage | Native left edge X | Center X | Initial top Y | Assisted pipe left edge X |
|---|---:|---:|---:|---:|
| 1-1 | 560 | 576 | 192 | 608 |
| 1-1 | 688 | 704 | 192 | 736 |
| 1-1 | 864 | 880 | 192 | 912 |

The earlier `84d372ef` Downloads route repeats all three crossings and clears
1-1 with both lives. Evidence is in `build/mini-contact-render-delivery-1109/verified-delivery.json`.
The first pipe at X448 and the three gaps use Mini's ordinary jump.

Earlier camera-spawn nightly `56c4135e` retains those same placements.
The three native constructors run with left edges 287, 286 and 287 pixels
from the camera's left edge, before entering the visible screen. Each gets
its own native actor slot (5, 4 and 3); an earlier visible platform is no
longer retargeted to the next placement. Mini's floor sweep recognizes all
three. The controller-only route boarded and departed each and reached
active 1-2 with both lives. Evidence:
`build/mini-combined-camera-native-1110/route-v2/capture/result.json`.
The installed Downloads ROM repeats the full route successfully; see
`build/mini-camera-delivery-1110/verified-delivery.json`.
The shared non-Mini helper manager already uses camera-relative margins;
this change repairs Mini's separate player-proximity admission.

### Manually summoned support: Mini Mario and Karnov

Up + Select summons a native vertical girder beneath the player. The new
Down + Select horizontal girder is delivered on `74fde1db`, with actual
Downloads controller tests for both characters. Mini's normal 1-1 regression
retains zero lag NMIs and missed updates. These are dynamic summons in the current stage/area,
including 1-1, rather than fixed stage records. Each is 32 pixels wide.

Here X and Y mean the native player world X and native player Y at the actual
constructor event. Left edges clamp to zero when necessary; center is always
the final left edge + 16. Initial top is Y + 32.

| Character / alternate | Control | Initial native left edge | Initial center | Initial top |
|---|---|---:|---:|---:|
| Mini Mario, Mario alternate 8 / raw 41 | Up + Select | max(0, X − 12) | left + 16 | Y + 32 |
| Mini Mario, Mario alternate 8 / raw 41 | Down + Select | X + 20 | X + 36 | Y + 32 |
| Karnov, Rygar alternate / raw 34 | Up + Select | max(0, X − 8) | left + 16 | Y + 32 |
| Karnov, Rygar alternate / raw 34 | Down + Select | X + 24 | X + 40 | Y + 32 |

Horizontal placement always uses the right side, including when facing left.
It begins moving right at one pixel per gameplay update, reaches initial
left edge + 112, then returns to its initial left edge and repeats. Its top
remains at its initial Y. One manual girder of each axis can coexist; a new
matching chord replaces only that axis. Holding the chord does not repeatedly
construct actors. A full native pool queues the request.

The delivered 1-1 opening tests verify both directions of native carrying,
right–left–right motion, actual controller edges, independent replacement,
and right-side placement while facing left. The camera retains SMB's native
one-way scroll: a returning platform can leave the rider at the viewport's
left boundary, and an older vertical girder can be culled offscreen. These
tests do not yet establish a manual horizontal-assisted pit crossing. Mini's
full non-shortcut 1-1 route still uses the three fixed girders listed above.

### Donkey Kong Jr. opening prototype

Nightly `d1333adf` makes DK Jr. startable through Select on Donkey Kong. His
source prototype retains two native vertical girders in 1-1, both 32 pixels
wide and initially at top Y192:

| Character | Stage | Native left edge X | Center X | Initial top Y |
|---|---|---:|---:|---:|
| Donkey Kong Jr. | 1-1 | 416 | 432 | 192 |
| Donkey Kong Jr. | 1-1 | 480 | 496 | 192 |

Their earlier native offscreen births were observed on private `88e62d81`.
The first assisted pipe crossing still failed at jump/detach; the new nightly
qualifies only selection and the early walk/jump opening before these lifts.
Do not treat their presence as a verified crossing. Prince of Persia adds no
helper platforms in this opening prototype.

### November 10: full WWF and Final Fantasy Level 2 support

Delivered nightly `c10b7d87` extends both manual native `$25` girder controls
to **Hulk Hogan, Ted DiBiase, Bam Bam Bigelow, Honky Tonk Man, Randy Savage,
Andre the Giant, Fighter, White Mage, Black Mage and Thief**. Mini Mario and
Karnov retain their existing controls and placements above. Sonic, Jay McCray
and Steve Hermann add no helper records.

These are dynamic summons in **any active gameplay stage/area**, verified in
1-1, rather than fixed world coordinates. Each is 32 pixels wide. X means
player world X and Y means native player Y at the constructor event. For each
of the ten newly supported characters:

| Control | Initial native left edge X | Initial center X | Initial top Y |
|---|---:|---:|---:|
| Up + Select, vertical | max(0, X − 8) | left + 16 | Y + 32 |
| Down + Select, horizontal | X + 24 | X + 40 | Y + 32 |

The horizontal platform starts right, reaches initial left edge + 112, returns
left 112 and repeats. Facing left does not reverse its birth side. Each axis
has its own single actor; a fresh chord replaces only that axis, held chords
do not repeat, and an occupied pool queues the request.

The following **observed initial world positions in 1-1** are from the first
vertical and horizontal births in each final-ROM controller replay. Initial
height differs because the vertical platform has already lifted the player
two pixels when the horizontal one is summoned.

| Character / alternate | Vertical left / center / top | Horizontal left / center / top |
|---|---|---|
| Hulk Hogan | 32 / 48 / 208 | 64 / 80 / 206 |
| Ted DiBiase | 32 / 48 / 208 | 64 / 80 / 206 |
| Bam Bam Bigelow | 33 / 49 / 208 | 66 / 82 / 206 |
| Honky Tonk Man | 32 / 48 / 208 | 64 / 80 / 206 |
| Randy Savage | 32 / 48 / 208 | 64 / 80 / 206 |
| Andre the Giant | 33 / 49 / 208 | 66 / 82 / 206 |
| Fighter | 32 / 48 / 208 | 64 / 80 / 206 |
| White Mage | 32 / 48 / 208 | 64 / 80 / 206 |
| Black Mage | 32 / 48 / 208 | 64 / 80 / 206 |
| Thief | 32 / 48 / 208 | 64 / 80 / 206 |

All ten final-hash replays pass six birth/replacement events, both axes alive,
native carrying and right–left–right 112-pixel endpoints with both lives.
Fighter repeats from the actual Downloads filename. Final Fantasy uses a
temporary one-pixel platform-only foot allowance; ordinary body collision
boxes are restored exactly. Mini's separate full non-shortcut 1-1 route still
passes at 3,494 updates / 3,494 gameplay frames with zero lag NMIs/missed updates.
The manual helper opening tests do not establish every character's assisted
pit crossing or full 1-1 clear. Evidence and prototype limits:
`docs/qa/complete-roster-starts-1110.md`.

### November 10 follow-up: DK Jr. first-pipe crossing verified

The unchanged installed `c10b7d87` ROM now has a passing controller-only
two-girder crossing. Both fixed **1-1** platforms retain their original
placements: left/center/top **416/432/192** and **480/496/192**, width32.
Both spawn 287 pixels beyond camera-left, get different native actor slots,
and have45 authenticated native carries each. The replay reaches ordinary
far-ground **X517 / native Y176**, source state1, native grounded state0,
engine8 and lives2, with1,749 scroll publications and zero mismatches.
Body checks include906 matching DMA/hardware observations.

The former jump attempt failed because the rising lift recaptured the original
slow jump. The passing route walks toward the supported right edge and steps
across without a second A press. The first revised observer then stalled on
the second lift because it sampled transient native Player_State2 between
source/terrain/platform updates. Its successor accepts intermediate support
only with source state1, exact source/native feet and a current/prior actual
carry from the same lift. Strict ordinary far-ground, both lives, both births
and both carries remain required. No ROM bytes, physics or platform coordinates
changed. This qualifies the first pipe, **not a full DK Jr. 1-1 clear**.

Live positive packet: `build/dkjr-supported-departure-1110/`.
Result SHA256: `9ddf1e6ea00af9b182f0663e35fcfa9ed1c8f355825098f6d6387170e9f07a92`.
Its bindings are valid. The two earlier failed packets remain diagnostic
evidence; see `docs/qa/cleanup-current-owned-1110.md` for exact disposable files
whose deletion was rejected before execution.

### November 13: Karnov natural flower via manual vertical helper

On exact Downloads `65ee94ca`, Karnov uses the existing **Up + Select** control
to summon a native ID25 vertical girder in **1-1**. Its observed creation is
**left1201, center1217, initial top208, width32**, slot0, frame3246. The actual
Mesen route records141 native carries and then naturally collects the first
flower at frame3491, reaching original triple shot with health0 and both lives.
This is a controller-created helper, not a new authored ROM placement. The
fixed Karnov pipe helpers remain left688/center704/top208 and
left872/center888/top208, width32, in1-1.

Root's native two-pickup receipt is
`55c1f5d3b097377b190f836cb213ed7f31a0736dbdc9ec5d3054638dd6f45a23`;
controller `88ccc41014cea57d2e95e48833f27291f7bf566356481362c4cbbe08b6f0eba4`.
Later natural Boots/Bomb acquisition remains in progress. See
`docs/qa/karnov-natural-bomb-1113.md`; no ROM bytes or helper controls changed.
