# Mini Mario lag profile

## Delivered Mini-only fast path

The full empty-floor CPU trace found roughly 21,000 cycles per update in header checks, owner dispatch, and bank trampolines. The released successor keeps the original complete header check for other owners. Mini uses its validated movement epoch for repeated gameplay services, and the common side query, visibility, and two geometry constants can use Mini's exact native results directly.

| Opening 1-1 idle replay | Previous nightly | Updated nightly |
| --- | ---: | ---: |
| Simulation updates | 120 | 120 |
| Video frames | 240 | 180 |
| Frames with neither controller port read | 180 | 120 |
| Lag NMIs | 180 | 120 |

The no-read count was observed from the actual Mesen execution at both controller ports. The Lua state did not expose a numeric built-in lag counter. The exact Downloads build reproduced the updated row. It also passed the existing full non-shortcut 1-1 route to active 1-2 and the earned mushroom replay. The same full route went from 7,875 to 6,420 video frames for 2,705 source updates.

The side path matched all 2,048 live-source CPU cases and saved about 1,520 cycles per call. Each immutable visibility or geometry path saved about 1,400 cycles per call. The shared route guards matched the original continuation state in 3,690 foreign CPU cases. Those entry checks still cost 17 cycles for the rare gate and 28 for the side gate. The original large foreign header-check penalty from the first experiment is absent.

- Released ROM SHA-256: `4ff069b3474077a1f3f8924b530780dee7a81c2a32d759f8fbe2defcf91e3f4c`
- Current IPS SHA-256: `ea7efd5359ea444aa27276f1a40e2aee281b2d7aa765635b8c482b23f7da7fab`
- Build: `build/mini-idle-constants-1103`
- Verification: `build/mini-idle-delivery-1103/verified-delivery.json`
- The private Prince test needs a new rebase over this nightly. This Mini solution leaves its proposed Cheats-menu code span untouched.

## First experiment

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
