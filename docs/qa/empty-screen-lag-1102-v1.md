# Empty-opening performance — November 2

Exact installed MMC5 SHA256: `cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8`.

Controller-only measurements in 1-1, with zero active or visible enemy slots. Each cold launch settles, measures 180 physical idle frames, then holds Right for 40 physical frames. The percentage is Main updates per physical frame. This does not test a whole level.

| Character | Idle updates | Walking updates | Walking displacement |
| --- | ---: | ---: | ---: |
| MARIO | 100.0% | 100.0% | 36 px |
| DONATELLO | 100.0% | 100.0% | 42 px |
| HULK HOGAN | 63.9% | 52.5% | 0 px |
| RASH | 66.7% | 67.5% | 31 px |
| BURNS | 50.0% | 50.0% | 23 px |
| PAPA | 100.0% | 100.0% | 51 px |
| EXCITEBIKE | 66.7% | 65.0% | 7 px |
| ARTHUR | 66.7% | 65.0% | 39 px |
| METAL STORM | 66.7% | 67.5% | 37 px |

The longer Hogan replay confirms movement: X40 → X92 over 180 physical frames (92 Main updates, 51.1%), with correct held Right reaching the original frame handler. The initial 40-frame check alone was too short to establish whether movement worked. His delayed start and slowdown remain under review.

The single Metal Storm screenshot also reveals a visual issue: the HUD says MARIO and the visible sprite is at the left edge while native world X is 77. The timing measurement does not validate his graphics. This needs a separate actual OAM/CHR/graphics ingress check.

Every measured run retains lives 2 → 2. Mario, Donatello and Papa reach one update per frame in this opening. The slower source integrations remain performance work; no thresholds were relaxed to call them fixed. Full roster routes and every earned powerup remain required.

Compact evidence: `docs/qa/checkpoints/2026-11-02/empty-screen-lag-v1/receipt.json`. Captures stay in the bounded task roots; one PNG per run, no videos.
