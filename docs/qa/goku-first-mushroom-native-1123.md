# Goku's Mushroom and Fire Flower in Easy 1-1

Mesen launched the Downloads nightly `27e01af3`. Goku hit the block at
X336 and collected the Mushroom at X400/Y176. His health rose from 94 to
114, he earned the Power Pole and reached tier one. The pickup played its
cue and awarded 1,000 points. He completed 25 further movement updates on
the ground with two lives and the Power Pole still equipped.

The replay took 750 video frames with no captures. Mesen receipt
`f8dee82fa537069088c78b40282b5905b51abada6e610c87baa692b33e9113a9`.

On Downloads `bcc26bb5`, a second replay earned the Mushroom and then
revealed the Fire Flower at X1248. Goku collected it at X1261/Y138. It
granted three waves, tier two and 1,000 points. He charged with B and
pressed A to launch a wave. One charge was spent and the projectile
traveled 119 pixels. He kept two lives through 25 further movement updates.
The run took 2,180 video frames with no captures. Mesen receipt
`59c60b575be0b20efdc75eae0ff0cc4760927bb4204ecbc38edaa025718db118`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_goku_first_food_1123.py --run
python -B tools/audit/run_bounded_build_v1.py --output build/goku-flower-source-1123 --max-files 8 --timeout 300 -- python -B tools/audit/run_goku_flower_1123.py --run
```
