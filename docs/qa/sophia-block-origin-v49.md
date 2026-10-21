Sophia block-origin correction, 21 October 2026

The supplied video shows a head-struck coin brick moving sideways during its bounce. The old native fixture reproduces a contact at world X112 with bounce X96. Sophia's wider source head can reach a neighboring cell while the old block constructor derives its X from Mario's center.

The correction uses the accepted source head query's actual column and page for the bouncing block, coin, or emerging power-up. Projectile-authored origins and fallback contacts retain the existing constructor. The same-cell replacement remains unchanged.

Both updated playable ROMs are installed in build/smb-crossover-mmc3.nes and build/smb-crossover-mmc5.nes. Frozen checkpoint: build/checkpoints/roster-audit-v49-sophia-block-origin-hu/manifest.json.

Validation:64 native controller-jump cases across Easy/Hard and both mappers, including left/right edges, page crossings, question blocks, mushrooms, multi-coin bricks, ordinary brick bumps, actual OAM halves and bump queue requests.12 unchanged boot and other-character/projectile checks pass.2688 compiled helper controls preserve old registers, mapper state and complete RAM except the three intended origin bytes and two individually asserted popped stack cells. Both baseline ROMs are literal H; each playable ROM differs by42 bytes.

This is a targeted provisional fix. Existing H playthroughs retain their original ROM identity; full integrated roster/arsenal/performance and final recordings remain open. The initial failing H collision and HQ test-oracle omission are retained separately.
