# Alucard pickups in Easy 1-1

Mesen started `82e8da0e` from Downloads and selected Alucard by highlighting
Simon and pressing Select three times. Alucard kept 64 HP and ten hearts
through the 1-UP and Star runs. He stayed in human form and used normal controller
input with no helpers or captures.

- **Hidden 1-UP.** He hit the block at X1024 and caught the moving 1-UP
  at player X1039/Y126. The life counter rose from two to three with its
  sound cue. He finished on the ground at X1027/Y176 after 29 more
  movement updates.
- **Star.** He hit the Star brick at X1616 and caught the
  Star while on the ground at X1665/Y176. It started invincibility,
  queued the Star music and awarded 1,000 points. He kept both lives and
  the active Star through 25 more movement updates.

| Replay | Video frames | Controller SHA-256 | Mesen receipt SHA-256 |
| --- | ---: | --- | --- |
| Hidden 1-UP | 1,285 | `7f69e8146e51a72c60ca774a2a4a312329d02de0eff598b8411173d8a944d0cb` | `52e7c8b68d7580eb8e04466b77de338ec488fa5246c812745e801f33336cc846` |
| Star | 1,856 | `9cf0c7cbf11a7ae8f6fa2eadf19f657720c13f28f228b2f7716e9c56befbe9bd` | `747e11a67898d5bd8afa94ad7bb4b716bd22010c7f011fbd7c986f99fa1f2c0a` |

## Fire Flower and upward fireball

Alucard picked up the Mushroom from X336, then hit the Fire Flower block
at X1248. He jumped in from the right and collected the Flower at player
X1263/Y126. It enabled fireball level one, queued the pickup sound and
awarded 1,000 points. On the block row at X1219/Y112, he pressed B and
fired a horizontal shot and a new upward-diagonal shot. The replay observed
both projectiles advance on consecutive weapon updates and retained both
lives, full health and the upgrade through the end of the run.

The 1,680-frame replay completed the four standard pickup checks. Its
controller SHA-256 is
`c30e385df7a1c7e07d0b616d1f8755036279d1da140f077ee18aa7bcd3ceed7c`.
Mesen receipt `7c76ed45f7b8ebbd5e606523ab52a22814ced44654f18703c099dc1cfcaaa247`.

Replace `flower` with `life` or `star` to repeat the other tests.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/alucard-stock-native-1123 --timeout 230 --max-files 2 -- python -B tools/audit/run_alucard_stock_1123.py --item flower --run --native-root build/alucard-stock-native-1123
```
