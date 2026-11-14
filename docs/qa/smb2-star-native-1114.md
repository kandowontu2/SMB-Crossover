# Native Star pickups for all eight SMB2/Doki characters

All eight natural Star routes passed on exact ROM
`421379021e775e6e03357c0aa11d4cab04008452f94bc9e8938f0662cc0c979f`.
Mario's root55653 run used the private candidate; the other seven root40276
runs launched the actual Downloads nightly. Its bytes matched that tested
candidate before and after every run, with clean same-name patch guards.

The source module is frozen at
`532c95177838497c4e7bf354e11629d0a0d750f7a8e63b397a23e2a0bf6f992c`.
The matching eight Lua hashes, source routes and retained diagnostic negatives
are in `smb2-natural-star-source-1114.md`. No Star game code was changed for
these tests.

Each character uses real menu selection/Start and ordinary controls to hit
the authored 1-1 Star block at world **left1616/top144**, spawn runtime kind2,
collect the actual native actor and resume play for 30 completed Main updates.
The collector erases the item, publishes popup6 and sound queue32, grants
native Star timer35 and music queue64, then the original character movement
imports the Star effect. Both timers remain active during the observed scope.
All observed item collectors are state128; this is an observed value, not an
extra admission fence. Sound/music queue writes are not a listening review.

| Character | Physical frames / Main returns | Head / collect / import Main | Endpoint X/Y | HP retained |
|---|---|---|---|---:|
| SMB2 Mario | 1894 / 1335 | 1218 / 1304 / 1306 | 1666/176 | 15 |
| SMB2 Luigi | 2146 / 1536 | 1417 / 1505 / 1507 | 1678/135 | 31 |
| SMB2 Toad | 2035 / 1467 | 1350 / 1436 / 1438 | 1667/176 | 15 |
| SMB2 Peach | 2023 / 1419 | 1301 / 1388 / 1390 | 1664/176 | 15 |
| Imajin | 1948 / 1301 | 1185 / 1270 / 1272 | 1669/176 | 15 |
| Lina | 2196 / 1593 | 1475 / 1562 / 1564 | 1646/176 | 15 |
| Papa | 2231 / 1580 | 1463 / 1549 / 1551 | 1667/176 | 31 |
| Mama | 2226 / 1545 | 1425 / 1514 / 1516 | 1679/137 | 15 |

All finish alive with two lives, max-health0 and vegetable reserve0. The six
HP15 variants took damage before collection and retain that health through
pickup and resumed play. Lina's native route takes earlier damage where its
source route retained31; neither is presented as damage-free. Luigi and Mama
finish airborne. These are item lifecycle scopes, not full-stage clears or
grounded stage endpoints. No health, actor, item, position, ability or terrain
seeds were used.

Native receipt SHA256 by variant:

```text
0 0db25417dcb342f1ce59143f6f6af2a7981d3781899782581f9761cb48f3113e
1 39d39efbfdaf8ef360ff0afa5d66a266db1494fdd7a15b765efbb5cd5a1b493e
2 770f8afe39f0ad073610829ad4697d2f856e97f82ea14b3edcb5dd1ea2a2c6b8
3 1821a90dbce933d2de44be714c781ce57b72429341631eb835088710ff1f1414
4 822de20e4cdd2f3eaa1ae3f9637445f0ecac7efe7102625dc1036f338e9e362d
5 bbc71d70ef82905386bf1b556ea04238d2322468bf0a881a72358c4c70666103
6 c277a736af3aeb859c8f1766535b081a1c9d624108429127f070121dbdea9056
7 6855fd5679c940ff3fc6510dfe9ab1ea70b9b8637c67ec998c86c0a6a367d677
```

Root reused only the two existing files in `build/smb2-flag-native-1113`.
The remaining-seven batch ran through the bounded runner with max-files2,
timeout600 and a 120-second capture-watchdog limit per Mesen run. Screenshots,
videos, image sequences, logs, per-frame dumps, backups and new build files:
zero. Root's sole Mesen queue is now free; other-project processes remain
untouched. No helper platform was added or moved, and no release or patch
asset was published.
