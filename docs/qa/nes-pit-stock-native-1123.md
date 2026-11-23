# NES Pit pickups in Easy 1-1

Mesen started the Downloads `82e8da0e` nightly and selected Pit without
pressing Select for the Game Boy alternate. The replays used controller
input in Easy 1-1. The powerups came from the original blocks and the game
continued for at least 25 movement updates after each award.

## Mushroom and Fire Flower

Pit hit the first block at X336 and collected its Mushroom at player
X406/Y176. He finished the 60-update growth animation and gained the first
power tier. A real B press then launched an arrow. The replay observed its
motion and the native projectile collision path before the arrow retired.

In the second run, Pit reached the Fire Flower at X1248 and collected it
at player X1261/Y97. The second growth animation enabled wing flutter.
From the ground at X1304, Pit jumped, released A and pressed it again in
the air. He rose from Y147 to Y135 while using eight units of fuel. He
landed at Y176 with 52 fuel, then the ground update restored it to 60.
He remained at full fuel and second power tier with both lives after 25
more movement updates.

| Replay | Video frames | Controller SHA-256 | Mesen receipt SHA-256 |
| --- | ---: | --- | --- |
| Mushroom and arrow | 1,030 | `002349583230248e44017dfd2f30da07306693808e1426a50ff761d208b0d447` | `3191ff233aa645403c0d7927dbb18edd4e2e9b8247ab3bdfc97b5197a4c37d0d` |
| Fire Flower and wing flutter | 2,395 | `bc17717c4af88a9d2b3c54bc3dedf13c2c4107ed196d2947f8639217586ed859` | `a3fb411a89e018e720a87fce70b086bd23e250e79b5af90cd9d41f452c49f932` |

## Hidden 1-UP and Star

Pit hit the hidden block at X1024 and collected its 1-UP at player
X1039/Y122. The life cue played and he gained a third life. He landed at
X1039/Y176 with his first power tier and full fuel.

The separate Star replay hit the brick at X1616, then jumped to catch the
moving Star at player X1646/Y92. It started invincibility, queued the Star
music and awarded 1,000 points. Pit landed at X1646/Y176 with both lives,
his first power tier and the Star still active.

| Replay | Video frames | Controller SHA-256 | Mesen receipt SHA-256 |
| --- | ---: | --- | --- |
| Hidden 1-UP | 1,843 | `d2301f8a2799369c08ae8e766f41b2f8e1b4af364bbfa996e6bd415d1e14eeb3` | `14ed9535bf0d963241e22ae2b21165557542ce82d04a8ddfae1ee58e2a23c34e` |
| Star | 2,806 | `4b86a2da9fea98b1a45bf64eacdd953d7f122e48f36492ca864b8648ca398309` | `9403c75647c5d27b999d4896d1cf0018eb46df73d4a26c117d9f24ec4d8e1415` |

No captures were saved. The four route arguments are `mushroom`,
`upgrades`, `life` and `star`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_nes_pit_stock_1123.py --route upgrades --run
```
