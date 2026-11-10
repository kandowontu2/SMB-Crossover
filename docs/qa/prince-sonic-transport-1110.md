Prince's frozen logical support packet loads on the current public Sonic
transport. The controller reaches full fourth-pipe support and clears the
first two gaps in the native CPU scene. The same scene begins from the prior
translated third-pipe approach and executes the authored parser, enemy loops,
collision, ordinary NMI, and original Prince actions from there.

| Exact transport parent | Combined SHA-256 |
|---|---|
| `e7a30825f992d9a28c813ee7eb2571e6836b8f75c6579234f7f7a66106a6d896` | `53b9ea335b92fc05870ad2d3c3838b2f653fc369b0b893cd976e7e4d97c3b924` |
| `ccd2de04d1a2c00989a240943f7bbaf5ac1863bae34dce65e6c313558c7ba9ed` | `f8f91daf9851e76fafaaa55a069b0da5d4eead097d48b3c5fd55435773f6397b` |
| `d2542ff3c9f78ac26eb7e19d64a7708711bc766515f634b05952bab1be9103f0` | `47a7a6aeabe2cc7db593f431591e52331b834485b3d7638e3f10f95cbf43db4b` |

Each composition takes the same frozen v8 packet from
`a9c08e84041ed0d86e806d84261febd63008a7686cdf9f1a17915f6f340ad0d8`.
It changes 14,244 bytes within the 45 Prince carrier pages and the existing
16-byte cookie `a726021676a00802119275ac7f48cce7` at physical PRG65:AB9F
(file offset 535471). The checker binds the full copied preimages to the
seventh-owner image, where the cookie moved from AB9D to AB9F. It verifies
disjointness from the subsequent eighth-owner transport, Sonic portrait,
palette, and scripted scene writes. The required Zelda II alias is present.
Both 101 Select states and 100 distinct named entries match the parent.

The static-portrait and scene combinations passed these source checks.

- All seven cold and warm owners, 224 header byte poisons, and 49 ordered
  owner transitions, including Prince and Sonic in both directions.
- Actual Prince cold construction with both committed headers, 8,007,136 CPU
  cycles, 31,248 PPU reads, and full consumption of 6,395/5,930/1,233 staged
  bytes. Metadata and state keep minimum unread margins of 407/131 bytes.
- Five injected faults at the footer copy, independent reread, and state
  decoder. The last reread crosses the 256-byte boundary. All five fail closed
  with both headers invalid.
- 2,591 forced-blank NMI cuts, 145 IRQ cuts, 212 append contexts, and 164
  resumed forced-blank seams. Hot checks cover the actual logical cap, the
  legacy physical cap, and pose 123 projection with 107, 94, and 30 cuts for
  each of IRQ and lag NMI.
- The existing Easy landing flattens the live Goomba and preserves HP5 at
  X891. All 19 landing contact cases and seven lifecycle cases pass, including
  pause, duplicate epoch, scripted engine, foreign owner, and fresh life.

| Authored route witness | Update | Position | Original action and outcome |
|---|---:|---|---|
| Full fourth-pipe support | 660 | X928, Y112 | Careful step 42, both native feet supported |
| First gap far bank | 868 | X1175, Y176 | Running jump 4, native ground |
| Second gap request | 979 | X1349, Y176 | Running 1 with native near bank and three empty columns |
| Second gap admission | 982 | X1351, Y176 | Running jump 4 |
| Second gap far bank | 1016 | X1461, Y176 | Native ground, HP4, two lives |
| Leftward return to the near lip | 1160 | X1372, Y176 | Original action 4, actual native left-foot support |
| Both walkers fell and retired | 1360 | X1372, Y176 | Original standing pose 15, HP4, two lives |

The second gap spans X1376 through X1423. The parser naturally creates the
next Goomba pair before the far-bank landing. At update 1016 those actors are
at X1548 and X1572. Standing A and standing Right+A start original action 3,
then encounter a fatal contact at X1504 before the source jump lifts off.
The direct running jump reaches X1525 and encounters the live walker while
near ground. Up from the supported X1488 stance starts original reach action
8 and reaches X1496 before the fatal contact at update 1099. Pressing Left
on the far-bank running-jump pose enters original action 6 and continues
right to X1515. The fatal contact at update 1061 precedes the turn and reverse
jump. These inputs preserve the authentic source reactions. The affected identity is Prince of
Persia, Excitebike Select1/raw38. Helper placements are unchanged.

The controller that first lets Prince settle can reverse successfully. It
reaches original left run frame 6 at X1456 and requests Left+A at update
1124. Action 4 is admitted at 1126. The near-bank witness uses the real tile
at X1374 because the native camera clamps player X at 1372. An earlier X≤1363
observer missed this supported landing. The two native walkers fall at X1408
with Y206 and Y205 on updates 1296 and 1343, then retire. The initial return
trial started action 3 with Prince still facing left at 1362 and eventually
fell at X1405. From this same narrow lip, original turn action 5 reaches X1378
as it changes facing. At the settled pose 15 at X1381 both native feet are
over the gap, so the controller declines a standing takeoff there.

An earlier grounded running request at X1339 on update 975 starts action 4
at X1349. The earlier jump lands at X1459, two pixels left of the standard
route. This branch also sees both walkers fall, but the camera edge of X1370
still leaves the final right-facing stance unsupported at X1379.

Root separately ran the physical menu and first pipe on exact 47a7. The
controller entered the original jump at X206, used original Up and climb,
then reached supported far-side floor at X563/Y176 with HP5 and two lives at
commit 509. The reported receipt SHA-256 is
`c2b0c955979942b90d8e968d34e13b495af98ac6032052697f08a2ab75da2390`.

Use `check_prince_sonic_transport_1110.proposal(sonic_scene=True)` to recover
the 47a7 image and the matching current common loader program. The standalone
`compose(parent, frozen, transport_parent=...)` function also checks a
downstream image against the exact e7 base before applying the same packet.
The direct e7 reconstruction uses `proposal(static_portrait=False)`.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python tools/audit/run_bounded_build_v1.py --output build/prince-sonic-current-transport-1110 --max-files 1 --timeout 600 -- python -B tools/audit/check_prince_sonic_transport_1110.py --sonic-scene --cold --readback --owners --cold-vectors --route --hot-vectors
python tools/audit/run_bounded_build_v1.py --output build/prince-post-pair-climb-1110 --max-files 1 --timeout 600 -- python -B tools/audit/check_prince_late_route_1110.py --sonic-scene --approach climb-A
python tools/audit/run_bounded_build_v1.py --output build/prince-post-pair-bank-1110 --max-files 1 --timeout 600 -- python -B tools/audit/check_prince_late_route_1110.py --sonic-scene --approach retreat-unturned
```

The recipes retain zero files under `build/`. Physical verification beyond
the first pipe, full stage completion, and Prince's natural powerup
progression remain pending.
