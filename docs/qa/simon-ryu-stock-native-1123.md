# Simon and Ryu pickups in Easy 1-1

The Mesen replays start from power-on on Downloads `94fa7a02`, select
the original fighter through the menu, and use normal controller inputs.
Each passing check observes the authored block, an emerged item, native
credit and 25 further movement updates. No captures were saved.

Ryu hit the first question block at X336. He collected the Mushroom
after it left the row, finished the power-up animation, and retained
power tier 1 and both lives through 25 further updates. The run used
1,138 video frames. Its receipt is
`8d97c57550ae95f454a38f046ab30e7a55b53f4f170b192b9639bd346bb730d1`.

Ryu released and collected the hidden 1-UP at X1024 and the Star at
X1616 in separate runs. The extra life advanced the counter to three
with the native cue. The Star started the timer and music, granted
1,000 points, and remained active through 25 movement updates.

| Ryu replay | Video frames | Mesen receipt SHA-256 |
| --- | ---: | --- |
| Hidden 1-UP | 2,425 | `5f1636d902a22e9945718dd92b01bab278b09f66a041368b083657de05eb473d` |
| Star | 3,037 | `5e4bb59d68544f5d47fe50d74f20a2a2644db2b4166bdb0f628ced001ae9e47a` |

Simon's first attempt spawned the Mushroom from the same X336 block.
The old controller kept attempting to jump onto the block row and timed
out without collecting the item. Its receipt is
`7b778b9b99bd90c109870666ab159771ec1a6eda36d922d4f30ee7a873ed0ae2`.
The revised route followed the item along the floor and caught it at
X411/Y158. Simon kept his first power tier and both lives for 25 further
updates. Receipt
`585999880acc2c3103e2039f5168f140a3391fae2210de1ddf3f3918d814c467`
also records his first Flower attempt reaching its intended block.

The second Flower attempt established that Simon's double jump reaches
Y82 above the row. The input requested Right late, after Simon committed
to a vertical jump. Easy Simon copies his horizontal direction on each
jump edge and keeps it in the air. The revised second jump uses Right+A
together. Diagnostic receipt
`e85a58c878e7d9cb38e1b0f2bce615b75d1c621774af6ac96186306f2dd26386`.

Ryu's first attempt released inventory item 4 from the Fire Flower block.
A collision removed his first tier before he could collect the reward.
That attempt remains a partial observation. Receipt
`887c2cea9c5910f08cdb092fa6243eda06a4e7d3e90ac16ae89c81cd9ff8cd4e`.

Both revised Flower replays released the correct reward on `3af597a7`
and kept the first power tier and both lives. Simon's double jump
reached Y82, but he dropped back to the floor at X1244 before collecting
the Flower. Ryu reached X1290 on the right and jumped to Y126, short of
the height needed to land on the row. The first two attempts ended
before collection.

| Flower replay | Video frames | Mesen receipt SHA-256 |
| --- | ---: | --- |
| Simon | 2,151 | `039484b1a7e678d0e383d9a57e0c8dbe70484fc5fe0e83f9c8eeb42fd03e14b2` |
| Ryu | 2,529 | `cef8a8fe626b946de0be35e405bc4635cbabbfa3034e2f7411e8b96081b581f2` |

## Passing Fire Flower replays

On Downloads `3af597a7`, Simon started at X1316 on the ground to the
right of the row. He held Left through both jump edges. That carried
him from X1294/Y126 to X1287/Y104 and then onto the row. He collected
the Fire Flower, finished growing to tier two and kept both lives
through 25 further movement updates. Simon still needs passing hidden
1-UP and Star tests.

Ryu faced the right edge from X1290 and moved Left during the rise.
The wall grab attached at X1278/Y130. Up and a fresh jump with room at
the lip carried him above the row. The Flower block's reward was Fire
Dragon Ball. The inventory changed from `01` to `11` hex, kept the
Mushroom and both lives, and passed 25 further movement updates. Ryu
now has passing replays for all four standard Easy 1-1 pickups.

| Character | Video frames | Mesen receipt SHA-256 |
| --- | ---: | --- |
| Simon | 2,093 | `5ba6657f057b4baee015dff06d526c073236dcb7e586e2035fae1b86fb852451` |
| Ryu | 2,340 | `af57ab7504e0c3b21654812fc72aa0efbca15f21f5394a67ebe995dfc1880ecf` |

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_simon_ryu_stock_1123.py --form ryu --route mushroom --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_simon_ryu_stock_1123.py --form simon --route upgrades --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_simon_ryu_stock_1123.py --form ryu --route upgrades --run
```
