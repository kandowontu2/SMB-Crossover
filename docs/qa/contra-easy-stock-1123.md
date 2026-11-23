# Contra pickups in Easy 1-1

The November 22 Downloads nightly has SHA-256
`14b0b4c23baa1ff454d25720b0585dd45f7fa4179bbba6b7f38d68b6e0c141b5`.
Mesen starts each run from power-on, uses the normal menus, and plays with
controller inputs. The observer checks the authored block bump, full item
emergence, pickup sound, score and at least 25 further movement updates.
The test creates no captures or recordings.

| Character | Pickup | Result |
| --- | --- | --- |
| Bill Rizer | Mushroom | Hit the block at X336. After the pickup and transition, Bill kept the first power level and both lives. |
| Bill Rizer | Fire Flower | Hit the block at X1248. After the pickup and transition, Bill kept the second power level and both lives. |
| Bill Rizer | Hidden 1-UP | Hit the block at X1024. The item emerged, granted an extra life, played the life cue and Bill kept three lives through 25 movement updates. |
| Bill Rizer | Star | Hit the block at X1616. The Star started invincibility and its music, awarded 1,000 points and stayed active through 25 further updates. |
| Lance Bean | Mushroom | Hit the block at X336. After the pickup and transition, Lance kept the first power level and both lives. |
| Lance Bean | Fire Flower | Hit the block at X1248 and collected the mature Flower. Lance kept the second power level and both lives. |
| Lance Bean | Hidden 1-UP | Hit the block at X1024. The item emerged and credited a third life with the native life cue. |
| Lance Bean | Star | Hit the block at X1616. The Star started invincibility and music, awarded 1,000 points and remained active through 25 further updates. |

Bill's passing run took 2,656 video frames. Its receipt is
`bfdf57462b511579bbe6e6441118376baffe06916c9878c2ce6140aeb646c287`.
Lance's first run finished the Mushroom check and later hit a Goomba at
X853/Y176 on the way to the Flower. Its receipt is
`80bfeb8ec8da73b62f206333d53bdd60962bf1075602a50857ad1e248a8f55f3`.
The passing route landed at X794/Y176 after the fourth pipe and
defeated the Goomba at X856 with prone fire. Lance kept the Mushroom's
weapon through the fight and then collected the Fire Flower. The
same landing and combat worked on his 1-UP and Star routes.

The hidden 1-UP replay took 2,340 video frames and finished at X1039/Y176.
Its receipt is `9dae00a2a091fdd3c19ffcef9b311ab7a76cc3f9e4f76059e6cfa8a18344bb21`.
The Star replay took 3,079 video frames and finished at X1681/Y176 with
the Star active and both lives. Its receipt is
`ca0bc606d690e5e2b0a2e34c4610862f4cff8864dfa3706a5f519195fdd5e993`.

| Lance replay | Video frames | Mesen receipt SHA-256 |
| --- | ---: | --- |
| Mushroom and Fire Flower | 2,556 | `004d14853cf0b6eb3a042c19c817955ef346fb8695bf50726d517e3b3b21d421` |
| Hidden 1-UP | 2,217 | `61a10363cf712626377bb54fc0a869c26a479fe210691bb4f4f089f5a5276b60` |
| Star | 2,954 | `78f57c01cdb3cbce09c29d8614040a7f61076f59e5b54dbeec7c3375540c9fe8` |

The original Bill replay also shows the rifle, the Mushroom's Machine
Gun and the Flower's Spread Shot in use. The new run verifies their
pickup transitions. [October 22 gameplay verification](terrain-publication-repair-2026-10-22.md#new-ordinary-easy-progression-recording)

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 210 -- python -B tools/audit/run_megaman_proto_stock_1123.py --form bill --route upgrades --run
```
