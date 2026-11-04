# Mini Mario lag profile

The published MMC5 nightly starts 1-1 at one Mini update per two video frames, even during the stationary opening. The controller replay observed 270 full owner checks across 20 idle updates. Four calls per update come from the native side probe. The two complete WRAM header comparisons run on every call before the private Mini code is invoked.

The private candidate validates both headers on the first Mini service call of each update. Repeated calls in that update verify that both headers are still marked live for Mini. The direct cold-load and retirement checks still compare every byte. The movement code, collision probes, and ROM graphics are byte-identical.

| Same replay phase | Mini updates | Nightly video frames | Candidate video frames |
| --- | ---: | ---: | ---: |
| Idle | 20 | 40 | 31 |
| Walk right | 33 | 66 | 64 |
| Walk left | 24 | 48 | 46 |
| Jump | 20 | 40 | 40 |
| Land | 22 | 44 | 37 |
| Full non-shortcut 1-1 to active 1-2, including menu and transitions | 2705 | 7875 | 7720 |

The CPU check measured 653 cycles for the old hot authentication call and 412 for a cached call. The new cold Mini call took 921 cycles. Across 594 CPU cases covering six owner cookies, three incoming bank mappings, and each individual header byte, full authentication matched the nightly. The candidate also passed the real question-block mushroom release, one pickup, all 60 power-transition updates, and powered sprite checks in Mesen.

The shared banked helper added 199–269 CPU cycles to uncached non-Mini calls, so the candidate is private. The next production change needs a Mini-only entry into the cache while retaining the resident path for all other owners. The candidate's Cheats-menu code span also overlaps the separate private Prince proposal and must be reconciled before combining them. The Mini-only fixed-point conversion experiment left video-frame cadence unchanged and was dropped.

- Published parent SHA-256: `9d291cb7562aad3a21e575386d0d6461dc39eab5cbd34c85856ae8a1f1d2b622`
- Private candidate SHA-256: `5beff1900c118824d3f22436da5faac651075e6c59d653489986bf12637e34ca`
- Candidate: `build/mini-frame-auth-1103/mini-frame-auth.nes`
- Profile receipts: `build/mini-auth-final-before-1103/capture/timing.json` and `build/mini-auth-final-after-1103/capture/timing.json`
- Regression receipts: `build/mini-auth-full11-1103/capture/result.json` and `build/mini-auth-mushroom-1103/capture/result.json`

From the repository root, rebuild the private candidate with the existing pinned Mini-power inputs:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/mini-frame-auth-1103 -- python -B tools/audit/build_mini_frame_auth_1103.py --output build/mini-frame-auth-1103
```
