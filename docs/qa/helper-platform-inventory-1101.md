# Helper platform inventory — functional pass in progress

The functional roster pass is not complete. This inventory separates source
placements from actual route verification; it is not the final all-character list.

Inventory fixture SHA256: `128915e97e78891a585aa8f9fd904c166ca64dcd6dd1ee395fc68fd505c1e72c`.
Current nightly SHA256: `f33c7b19d27309ab4e4771125a74360f978dba08bd807d25bc6307026e568734`.

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
