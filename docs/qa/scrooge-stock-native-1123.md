# Scrooge's hidden 1-UP in Easy 1-1

Mesen started the Downloads `3af597a7` build from the title, selected
Scrooge McDuck in row two, and verified regular Easy 1-1 with both
lives. Scrooge collected the first Mushroom, hit the hidden block at
X1024 and caught the 1-UP as it moved to X1047/Y129. The native cue
played and the life counter advanced to three. He landed at
X1048/Y176 with the Mushroom and three lives after 25 more movement
updates. The replay took 1,662 video frames and saved no captures.

Mesen receipt `1e4db907834d116fe1bb15d556da12ec49b006f00ab20117073b728c81ff5889`.
Controller SHA-256 `72aa8e678c63346b1740763011016ee02f83c2c569505a8636cfd98c73783c63`.

## Freeze on the Star route

Two normal-input Star attempts stopped before the Star block. Scrooge
was airborne at X1024/Y128, holding Right, Down and B near the hidden
1-UP block. The game loop stopped returning at update 921 with both
lives. The second replay repeatedly observed CPU PC `$01F9`, stack
pointer `$7A`, and the same native frame counter while video frames
continued. The exact trigger and the cause of the stalled game loop
are under investigation. The 1-UP replay used an ordinary jump and
completed on the same ROM.

Mesen receipts `265c06be532cb5f711b292d60b530397576448162161ab7b4603bab5798aa966`
and `cc96e555dd46ebc3fae989dc6a9592f4a859e8a2ed345fea9488789f0c74b3a7`.

A bounded Mesen trace stopped at the descending stack before it reached
the far-call trampoline in RAM. It recorded the pogo's block probe,
the native head collision and a long chain of pickup preparation calls,
ending at stack pointer `$85`. The linked trace independently reached the
same chain after creating a real 1-UP at X1024. The X1024/Y128 reading is
the temporary block position used by the pogo's native block effect.
The short Mesen trace receipt is
`e5a841fb923e8e1124d8d35612355a301dd280188555376b6c72a7ac91efb0af`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_simon_ryu_stock_1123.py --form scrooge --route life --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_simon_ryu_stock_1123.py --form scrooge --route star --run
```

## Pogo freeze fix and Star verification

Scrooge's pogo used the same extra-life pickup preparation as a normal
head hit, but reached it through a deeper chain of calls. The fix prepares
Scrooge's ordinary 1-UP directly. It uses the existing three pickup
dispatch routines, changes 130 bytes and retains the original destinations
for other characters and items. Source tests verified the original
pickup state, including Darkwing's paths, and tested the pogo preparation
through 34 placements each of the scanline interrupt, audio interrupt and
nested interrupt. The updated dispatch adds up to 28 cycles to the sampled
item-name reads.

Mesen tested the private `82e8da0e` ROM in two separate Easy 1-1 runs.
Scrooge earned the Mushroom, pogoed into the hidden block at X1024 and
collected the released 1-UP. The life counter advanced to three with its
cue. He landed at X1045/Y176 with the Mushroom after 25 more movement
updates. The separate Star route continued past the former freeze,
released the Star at X1616 and caught it at X1683/Y152. It started
invincibility and queued the Star music, awarded 1,000 points and remained
active after 25 more movement updates. Scrooge kept both lives and his
Mushroom and finished on the ground at X1675/Y176. No captures were saved.

| Replay | Video frames | Mesen receipt SHA-256 |
| --- | ---: | --- |
| Pogo 1-UP | 1,508 | `cb19b664f8ee78f38993aece44cf18937d4d20e7fd2fcd51dea56b1d0b2b87a5` |
| Star | 2,478 | `9f115dd24e8dc32097c0fb86fce2d51299490f3c12ef6db791dce4955d7092b8` |

The Downloads nightly was replaced directly with `82e8da0e`. Launching
that file reproduced both Mesen receipts exactly. The patch guard found
no IPS, BPS or UPS sidecar before or after replacement. The installed ROM,
the tested candidate and the shared test ROM match byte for byte.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/scrooge-pogo-prepare-native-1123 --max-files 2 --timeout 280 -- python -B tools/audit/run_scrooge_prepare_native_1123.py --route life --installed
python -B tools/audit/run_bounded_build_v1.py --output build/scrooge-pogo-prepare-native-1123 --max-files 2 --timeout 280 -- python -B tools/audit/run_scrooge_prepare_native_1123.py --route star --installed
```
