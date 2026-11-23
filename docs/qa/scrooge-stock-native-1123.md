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

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_simon_ryu_stock_1123.py --form scrooge --route life --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_simon_ryu_stock_1123.py --form scrooge --route star --run
```
