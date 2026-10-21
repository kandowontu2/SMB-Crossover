# Contra spread-shot performance

Both MMC3 and MMC5 now avoid repeated map-cell work for Bill’s bullets. The five-pellet fan and ten-bullet cap are preserved. Fixed workload measurements show **38–44% less CPU work** in the weapon update. Lag remains when the rest of the frame exceeds the NES CPU budget.

The change calculates bullet edges once, shares each block-map column pointer between rows, and reads only distinct cells. Empty air returns early; potential block hits still use the existing health, brick, reward and sound dispatcher. Firing counts the pool once per burst. Enemy checks skip ineligible actors and reject vertical misses before preparing the general collision boxes.

## Fixed workloads

Median weapon-update CPU cycles, with IRQ/NMI time subtracted. Each row uses 32 identical fixtures before and after. These six scene results are identical on both mappers. Enemies are active ground Goombas; bullets pass above them, exercising rejection work.

| Bullets | Enemies | Before | After | Reduction |
| ---: | ---: | ---: | ---: | ---: |
| 5 | 0 | 6,845.0 | 3,944.0 | 42.4% |
| 10 | 0 | 13,285.0 | 7,433.0 | 44.0% |
| 5 | 1 | 8,840.5 | 5,504.0 | 37.7% |
| 10 | 1 | 17,142.0 | 10,523.0 | 38.6% |
| 5 | 6 | 12,480.5 | 7,069.0 | 43.4% |
| 10 | 6 | 24,654.0 | 13,713.0 | 44.4% |

## Native-enemy stress scene

A separate scripted 650-frame scene keeps native enemies active while moving, jumping and firing. It injects the flower and invincibility to stress spread shots; it is not a controller-only completion replay. Its busy-NMI lag count changed as follows:

| Mapper | Before | After |
| --- | ---: | ---: |
| MMC3 | 165 | 153 |
| MMC5 | 166 | 153 |

That whole-scene improvement is smaller than the collision-time reduction. Rendering, audio and native engine work still consume CPU time. Input is pinned to video frames, so enemy/room progression can differ as update speed improves; the fixed fixtures above isolate equal workloads. These figures are one scene, not a universal lag percentage or a hardware-cartridge measurement.

## Behavior and regression checks

The existing **233 emulator checks pass** on the shipped ROM hashes, including the 521-frame, 19-field Mario baseline comparison. An additional **2,400 cases per mapper** produce byte-identical outcomes to the pre-optimization ROM: tile/subpixel boundaries, facing directions, vertical/page seams, protected terrain, brick damage, question-block rewards, enemy damage and rejection, all three gun forms, and partially occupied shot pools. Timing is recorded separately from the behavior fingerprint.

The pinned fingerprint is in [bill-collision-reference.json](../../tests/bill-collision-reference.json). The runner rejects changed outcomes. The fixture is included in future runs of `tools/verify.py`; the 233-case suite run and the two targeted fixture runs are recorded separately for this checkpoint.

[Measurements and hashes](../../build/contra-profile/comparison.json) · [MMC3 ROM](../../build/smb-crossover-mmc3.nes) · [MMC5 ROM](../../build/smb-crossover-mmc5.nes)

The [twelve added-character videos](world-1-1-expanded.md) validate the preceding checkpoint. Their known animation/SFX findings remain unresolved by this Contra-only optimization.

## Reproduce

```powershell
python tools/verify.py --mmc5
python tools/run_mesen.py tests/bill-spread-performance.lua build/smb-crossover-mmc3.nes
python tools/run_mesen.py tests/bill-collision-equivalence.lua build/smb-crossover-mmc3.nes --timeout 60
python tools/profile_bill.py --publish build/contra-profile/before build/contra-profile/after
```

The preserved `before` directory contains the reference ROMs/symbols and measurements; `after` contains the shipped checkpoint and its measurements. Both stress fixtures explicitly set emulator RAM. The level-clear video audit remains controller-only.

## Shipped ROM hashes

- MMC3: `06cc2a4c30331532b92a28891102b2f412edb7620c1c95a1dafc3d515e904044`
- MMC5: `6d431914a3bd84c78d79371a02c2deaaa6df661617ee936cbed9db84d9412db2`
