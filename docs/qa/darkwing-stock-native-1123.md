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

## Fire Flower block and Heavy adaptor

On the same nightly, Darkwing earned the Arrow adaptor and reached the
Fire Flower block at X1248 in the same run. The block gave a stationary
Heavy adaptor. Darkwing spent three gas to fire Left and made a temporary
grip with the Arrow adaptor. The arrow formed at world X1280, with its
center at X1292. He grabbed the arrow at X1299/Y149 and jumped from it
onto the block row to reach the Heavy adaptor.

The Heavy adaptor replaced Arrow on contact at X1264/Y101 and added ten
gas, from one to eleven. The pickup awarded 1,000 points and queued the
pickup sound. Darkwing kept Heavy, eleven gas, four HP and both lives
through 25 more movement and owner updates. He finished at X1262/Y112 in
2,222 video frames. The replay saved no captures.

- Controller SHA-256 `93fcee85ca766daebd3330cc4732a93832def45c170dd2d24636a0d20ddf2675`
- Mesen receipt SHA-256 `3b8a7e237feba6a7e1310f27cf78debc59336905cf72f88fa0e96e2a1d918f3d`

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_darkwing_stock_1123.py --route upgrades --run
```
