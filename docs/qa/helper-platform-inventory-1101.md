# Helper platform inventory — in progress

The functional roster pass is not complete. This inventory separates source
placements from actual route verification; it is not the final all-character list.

Current candidate: `6deeb43ae28c8c3725633979413a64cfb8cbdf937b2c89b23bc1084e20c8913f`.
`tools/audit/inventory_current_helpers_1101_v1.py` reads all 34 compiled shared
records and executes the real `HpConfigure` for 36 default families in both modes.
All 72 admission calls completed. Alternate selectors were zero, so this does
not certify every Select alternate. No gameplay bytes were changed by the audit.

| Characters / scope | Stage | Placement | Native behavior | Verification remaining |
|---|---|---|---|---|
| Shared eligibility: raw families 1,2,3,4,5,6,7,10,12,13,14,15,16,20,21 with default alternates | 1-1 | Center X=3104, authored Y=64, width=2 tiles, near end staircase/flagpole | Horizontal platform | Expand alternate names and verify actual crossings on current build |
| Goku and Karnov | 1-1 | Centers X=704 and 888; left edges 688 and 872; initial Y=208 | Existing native vertical platform, actor `$25`; one owned lift at a time | Full current-build route |
| Thomas | 1-1 | Left edges X=400,560,688,864; initial Y=192 | Existing native vertical platform, actor `$25` | Full current-build route |

Coordinates are world pixels. Initial/authored Y is not a fixed platform height:
the platform moves. Center coordinates and left-edge coordinates are explicitly
distinguished to avoid a 16-pixel ambiguity. Thomas's placements assist pipes
at X=448,608,736,912. Goku/Karnov's two placements assist the latter two pipes.

Machine-readable current output: `build/helper-inventory-1101-v1/inventory.json`.
Metal Storm now has a controller-only full non-shortcut1-1 clear on this ROM,
including the transition to active1-2, without added or shared helper platforms.
See `docs/qa/metal-storm-route-1101.md`. Its powerup/mode checks remain unfinished.

The final delivery must include named alternates, Easy/Hard differences, any new
accommodations, and current route evidence.
