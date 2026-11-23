# Darkwing Duck pickups in Easy 1-1

## First powerup block and Arrow adaptor

Mesen launched the Downloads nightly `06336f15`. The replay selected
Darkwing Duck by highlighting Scrooge and pressing Select once. In normal
Easy 1-1, Darkwing jumped from the ground at X330 and hit the first powerup
block at X336. The Arrow adaptor rose and became collectible at X336/Y120.

Darkwing jumped onto the first pipe and stopped at X442/Y144. He returned
left onto the block row at X394/Y112. This kept the left edge of the screen
at X330, so he could walk back to the item. He collected it at X352/Y112
with four HP and both lives. The actor disappeared, the pickup sound was
queued, he earned 1,000 points and his gas rose from zero to ten.

The replay verified 25 more movement updates and 25 Darkwing movement
returns after the reward registered. It finished in 908 video frames
with the Arrow adaptor, ten gas, four HP and two lives. The replay used
controller input and saved no captures.

- ROM SHA-256 `06336f15fae4d24afa8025e972764091def63b6c01d41f206828a5105939661f`
- Controller SHA-256 `3edcba9a21c8d4b221e554b5263e03246109cee15f3eb4f04d1ff4356621a3be`
- Mesen receipt SHA-256 `ec0da1dcdf195e962ff8bfe560d6f34fe9ec8bcf530b83003250890426fa8acf`

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_darkwing_stock_1123.py --route mushroom --run
```
