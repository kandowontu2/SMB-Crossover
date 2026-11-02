# Helper platform inventory — functional pass in progress

The functional roster pass is not complete. This inventory separates source
placements from actual route verification; it is not the final all-character list.

Installed MMC5 SHA256: `128915e97e78891a585aa8f9fd904c166ca64dcd6dd1ee395fc68fd505c1e72c`.
`tools/audit/inventory_named_helpers_1101_v2.py` verified identical installed and
candidate bytes, read all 34 compiled shared records and executed `HpConfigure`
in 80 cases: raw owners 0–36 in both modes, plus Grant/Sypha/Alucard. These are
admission tests, not native assisted-crossing or complete-route tests.

| Characters / scope | Stage | Placement | Native behavior | Verification remaining |
|---|---|---|---|---|
| Mega Man, Proto Man; Samus, Rogue Dawn; Bill, Lance; Link, Zelda II Link; Simon, Grant, Sypha, Alucard; Pit, GB Pit; Rygar; Ryu; Scrooge, Darkwing Duck; Kirby, Meta Knight; Chip, Dale; Little Mac, Doc Louis, Mike Tyson; Mike Jones; Popo, Nana; Alex, Ryan | 1-1 | Center X=3104, **native left edge=3096**, initial Y=64, width=16 pixels, near end staircase/flagpole | Native horizontal actor `$28` | Both modes admit the same helper; current alternate-by-alternate assisted crossings pending |
| Goku and Karnov | 1-1 | Centers X=704 and 888; left edges 688 and 872; initial Y=208 | Existing native vertical platform, actor `$25`; one owned lift at a time | Full current-build route |
| Thomas | 1-1 | Left edges X=400,560,688,864; initial Y=192 | Existing native vertical platform, actor `$25` | Full current-build route |

Coordinates are world pixels. Initial/authored Y is not a fixed platform height:
the platform moves. Center coordinates and left-edge coordinates are explicitly
distinguished to avoid a 16-pixel ambiguity. Thomas's placements assist pipes
at X=448,608,736,912. Goku/Karnov's two placements assist the latter two pipes.

Machine-readable current output: `build/helper-named-inventory-1101-v2/inventory.json`.
Metal Storm now has a controller-only full non-shortcut1-1 clear on this ROM,
including the transition to active1-2, without added or shared helper platforms.
See `docs/qa/metal-storm-route-1101.md`. Its powerup/mode checks remain unfinished.

The shared width field counts 8-pixel tiles. `HpProjectPosition` subtracts
`Width * 4` from the center: shared width 2 therefore means a 16-pixel platform,
with its native left edge 8 pixels left of center. Do not use the separate
32-pixel Goku/Karnov lift's 16-pixel subtraction for shared records.

All named 1-1 placements above apply in **both Easy and Hard**. Only
`Cv3Variant` changes the shared alternate mask; other same-owner alternates
inherit it without an individual ability check. High raw IDs are excluded from
shared admission, so Shinobi/Metal Storm do not inherit Ryu/Sophia helpers.
Karnov and Thomas use separate native managers. Karnov's controller-only run
crossed both tall pipes and the first pit, not all 1-1; see
`docs/qa/checkpoints/2026-11-01/karnov-pit-route-progress.md`.
No additional impossible crossing was proven by this read-only audit, and no
platforms were added. Shinobi's opening-pipe failure is still being diagnosed;
it is not evidence yet that a helper is needed.

## Later-stage shared placements

**H** means every named character/alternate in the first table row above.
**V** means Mega Man/Proto Man; Bill/Lance; Link/Zelda II Link;
Grant/Sypha/Alucard; Sophia; Scrooge/Darkwing Duck; Kirby/Meta Knight;
Chip/Dale; Little Mac/Doc Louis/Mike Tyson; Mike Jones; Alex/Ryan.
**O** means raw owners 0–5, including their same-owner alternates: Mario and
raw-0 variants, Mega Man/Proto Man, Samus/Rogue Dawn, Bill/Lance,
Link/Zelda II Link, Simon/Grant/Sypha/Alucard. Luigi is raw 8 and is excluded.
This condition does not separately inspect raw-0 Mario variants (Supermaaa,
Sonic, Celeste Mario, Kamikaze Mario, Mario the Tank); menu readiness remains
a separate concern. A dash means absent in that mode.

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
