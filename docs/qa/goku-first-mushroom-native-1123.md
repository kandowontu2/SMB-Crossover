# Goku's pickups in Easy 1-1

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

## Star

On nightly `bcc26bb5`, Goku revealed the Star from the brick at X1616.
He collected it as it emerged. Invincibility and the Star music started,
and he received 1,000 points. He retained two lives, the Power Pole and
an active Star through 25 more Goku movement updates. The replay began
at the normal menu, took 2,441 video frames and wrote no captures.
Mesen receipt `41d2d1d42352d4a93b47c0c16b95d5ad182d80bf378f90af44cd9fca6ffd2a54`.

## Hidden 1-UP

On `bcc26bb5`, Goku's upward head probe reached the hidden block at X1024
on five jumps. The terrain query recognized tile `$60` and treated it as
empty, so the block never appeared.
Diagnostic receipt `64fec330dcecef238b4040be2444069eb2540428ec06d60cc8facf769a90c062`.

The revised terrain query lets Goku hit invisible blocks from below
during a normal jump. Walking sideways into the space, falling through it
and attacking it still leave the block hidden. Goku uses the existing
block bump and item collection code. The repair changes only the two
existing Goku routines in PRG bank 86.

The linked-code checks compared 1,536 ordinary tile queries, covering all
256 tile values, both foundation cases and three camera positions. They
verified the same output and scratch state outside hidden head contact,
including page changes. The revised query took 7–79 fewer CPU cycles in
those ordinary cases. Another 22 cases checked hidden-block contact,
including the side probe that shares its return address's low byte with
the head command.

## Replays on `93f140ba`

All three Mesen replays began at the normal menu in Easy mode. They used
ordinary controller input and wrote no captures.

| Route | Result | Receipt |
| --- | --- | --- |
| Mushroom and hidden 1-UP | The X1024 block released its 1-UP. Goku collected it at X1039/Y132, got the extra-life sound and kept three lives and the Power Pole for another 25 movement updates. | `f3f4215f585a22593c447bfed673ea48f46547d9b4ccb10d6124c8a972579476` |
| Fire Flower | Goku earned three waves, fired one and kept two charges after at least 25 more movement updates. | `a575c92f7af7d54794f4a61641e9bfc015022cf4552e0a3165ee410292d42729` |
| Star and full 1-1 | The Star from X1616 started invincibility and music and awarded 1,000 points. Goku reached the flagpole without the shortcut pipe and completed 43 more movement updates in 1-2 with both lives. | `2e6595f9157eb10a753ee4909e99357cbf97aa49035b29564215c45cda7aa50b` |

The nightly was replaced directly in Downloads. Launching that path
in Mesen repeated the exact hidden 1-UP receipt. The installed ROM matched
`93f140baee70d97dd061dae60d549c2ac1ed1920a80b2288fa2b52b9e4be1712`,
and the patch guard found no same-name patch before or after replacement.

Run the current replays through the bounded runner. The earlier commands
below bind their own historical builds.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/goku-hidden-head-1123 --max-files 8 --timeout 600 -- python -B tools/audit/repair_goku_hidden_head_1123.py --run life --run flower --run stage
```

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_goku_first_food_1123.py --run
python -B tools/audit/run_bounded_build_v1.py --output build/goku-flower-source-1123 --max-files 8 --timeout 300 -- python -B tools/audit/run_goku_flower_1123.py --run
python -B tools/audit/run_bounded_build_v1.py --output build/goku-stock-source-1123 --max-files 8 --timeout 300 -- python -B tools/audit/run_goku_stock_1123.py --route star --run
```
