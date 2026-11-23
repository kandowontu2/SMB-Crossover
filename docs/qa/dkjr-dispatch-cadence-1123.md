# Donkey Kong Jr. opening performance

The installed `59e1a591` nightly runs 13 full code header checks in each
ordinary Donkey Kong Jr. update. A linked CPU trace of 16 standing and
16 walking updates found 7,449 cycles per update in those checks. Both
tests began through the normal character menu and used an empty opening
in 1-1. [Trace script](../../tools/audit/profile_dkjr_shared_dispatch_1123.py)

The `b7562774` test ROM repeats the full check at the first call of each
update and checks the live bank prefixes for the later calls in the same
update. In paired linked CPU runs, it saved 5,080 cycles per standing
and walking update. The observed native game state, bank mappings, and
PPU state stayed matched through 32 standing, 48 walking, 16 jumping,
and 26 landing updates. The saved cycles during the jump averaged
4,649 because some calls fell back to full validation. Source receipt
`1c277d93c992d52e80abaa1582dea1723f689828ba3c6ade4340eb099c892f03`.

Mesen completed the same 48 standing and 16 walking updates in 13 fewer
video frames. No enemies were active in either run. Both runs finished
at world X50/Y176 with two lives. The standing phase improved, while
walking still took about two video frames per game update.

| ROM | Video frames across both phases | Frames with no game update | Skipped NMIs | Mesen receipt SHA-256 |
| --- | ---: | ---: | ---: | --- |
| Downloads `59e1a591` | 128 | 64 | 96 | `6a4cf967e575c0b7c397666f176de4b569aa812a63d289eacc7fd95614c3b41b` |
| Private `b7562774` | 115 | 51 | 83 | `0e2678cb33ea64052c6b9ffa74b48f00df78bf6df5eef3f17690006e6258badc` |

The Downloads nightly still contains `59e1a591`. The candidate needs the
full stage, shared-code, and interrupt checks before delivery. Both native
measurements used the shared test slot and wrote zero captures.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_dkjr_dispatch_native_1123.py --run
```
