# Sypha pickups in Easy 1-1

Mesen launched Downloads `ffd70810`. The replays highlighted Simon,
pressed Select twice for Sypha and started Easy 1-1. They used normal
controller input and saved no captures.

- **Mushroom.** The first block at X336 released the Mushroom. Sypha
  collected it at player X402/Y176, gained the first power tier and
  received 1,000 points. Her health stayed at its 64 HP cap and she
  kept both lives for 25 more movement updates.
- **Fire Flower.** Sypha earned the Mushroom, then collected the reward
  from X1248 at player X1263/Y139. It equipped Flame and raised hearts
  from 11 to 16. Up+B cost one heart. Mesen observed the flame advance
  horizontally at Y120, and Sypha kept Flame and both lives.

| Replay | Video frames | Controller SHA-256 | Mesen receipt SHA-256 |
| --- | ---: | --- | --- |
| Mushroom | 766 | `467b10ba27eca9eeba2b85020b4d061fe00f437d9138a2c0974f992b4fcd5e57` | `b2e818b51f8551149f0a1da0d63c45a57d2ec3551374802f832ba0195877ae6a` |
| Fire Flower and Flame cast | 1,619 | `8976459aca2b52a67a4615c0d98243de154a79be1019b08768ed7f1167b2c265` | `595e10a81be9c20291571ec23b4430afe1fec31c4e716d3dfddf5e801d0db5c8` |

## Hidden 1-UP and Star

These tests each started 1-1 with Sypha's starting equipment.

- **Hidden 1-UP.** Sypha jumped into the hidden block at X1024 and collected
  its 1-UP at player X1039/Y135. The life count rose to three with the life
  sound. She finished on the ground with full HP after 25 more movement
  updates.
- **Star.** She hit the brick at X1616 and caught the Star at player
  X1665/Y176. The game started invincibility, queued the Star music and
  awarded 1,000 points. She kept full HP, both lives and the active Star
  for 25 more movement updates.

| Replay | Video frames | Controller SHA-256 | Mesen receipt SHA-256 |
| --- | ---: | --- | --- |
| Hidden 1-UP | 1,314 | `3c9156f9d505270b7e305e6f1dfe203450a2040404e984363fe17fdf264e65ca` | `4a88ca0f350b9b4d6fbdf86f6f3c7546a442571f61d82389a6c90e6caf1b2d8d` |
| Star | 1,831 | `839a1a2b248dd4d9a7510354f9bb24ab4668673f745f8667e714f5ef4d5db488` | `d3b83053f491801b8abb0f63d256d438e1f0d2a73900381267286fd6675f2969` |

The route arguments are `mushroom`, `flower`, `life` and `star`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/sypha-stock-native-1123 --timeout 230 --max-files 2 -- python -B tools/audit/run_sypha_stock_1123.py --item flower --run --native-root build/sypha-stock-native-1123
```
