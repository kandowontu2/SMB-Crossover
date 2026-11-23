# Rash and Zitz's second Mushroom in Easy 1-1

Both characters receive a second healing Mushroom from the question block
at world X1248. Their health system keeps Mario's size at zero, so the
original block selector serves a Mushroom. A literal Fire Flower does
not appear on these routes.

Normal Mesen play on the Downloads MMC5 nightly `ffd70810` proved the
reward for both characters. Each collected the first Mushroom, waited for
enemy-contact protection to expire, and took a real Goomba hit from 47 to
43 HP. The X1248 block created another Mushroom. Each character collected
it at player X1305/Y176, restored 47 HP, triggered the pickup cue, earned 1,000
points and completed 25 more updates with both lives. The runs saved no
captures and used no cheats or game-state writes.

| Character | Video frames | Controller SHA-256 | Mesen receipt SHA-256 |
| --- | ---: | --- | --- |
| Rash | 1,605 | `f404e1d4bebaaed617c753074822196c9a9777e24436b9f5396c5b9582d7a3ec` | `a00083415df2228f4a3df405d242bc7a77c96526d99f60fc57af61cd8428b0e3` |
| Zitz | 1,623 | `f993e0b3c487cf8dd3c019eb39155ee1e9b2a268fbb88660dbb3f41b4d092de9` | `90374978d935404cab3e2ad94352798b1eab236e50184d39ec1ce8b503a73afb` |

The linked selector trace independently observed its size read and
Mushroom write in both runs at the authored block. Rash's selector receipt
is `a7a69c24c9545643748b56e99466f2e4ef264b682240d45d245c63412cb2e529`.
Zitz's selector receipt is
`43851db7a15484cca1fb3b3ccc910796671cb8c32d87d5b95ad93189d143300b`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_battletoads_flower_1123.py --form rash --scope second-food --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_battletoads_flower_1123.py --form zitz --scope second-food --run
```
