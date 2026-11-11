# Donkey Kong Jr. completes World 1-1

From Donkey Kong on the character select screen, press Select once to choose
Donkey Kong Jr. The MMC5 nightly reuses the game's stock 32-pixel vertical
platform for the last two pipes and the descent to the flagpole. The stage
timer and the character's donor movement stay at their existing values.

| World 1-1 location | Initial left X | Center X | Initial top Y |
|---|---:|---:|---:|
| Fifth pipe, ascent | 2576 | 2592 | 192 |
| Fifth pipe, descent | 2640 | 2656 | 192 |
| Sixth pipe, ascent | 2832 | 2848 | 192 |
| Final staircase, descent toward flagpole | 3040 | 3056 | 192 |

Mesen ran the route continuously from the title screen. Each added platform
spawned offscreen at relative X287, entered view at relative X255, and carried
Donkey Kong Jr. The second-gap jump started at X1366/Y176 while the horizontal
platform's left edge was at X1402 and moving left. This saved 211 gameplay
updates over the earlier wait. Donkey Kong Jr. reached the flagpole at update
9605 before native timeout, then entered active underground 1-2 with both
lives. The replay traversed all three gaps and six pipes without using the
shortcut pipe.

The [second-gap CPU replay](../../tools/audit/check_dkjr_second_gap_early_1111.py)
also verified the same single A press at all four frame-counter phases on the
released ROM. Each route reached X1424/Y176 with both lives.

- ROM SHA-256 `b1d449ebd7bbcc6f9c75be00891afc627a8354acb56a18bb9cd7a4ef40129576`
- IPS SHA-256 `c4d7f170903bf6c7d416f358897e197a7bc9d0cd86f94b4a7440aa14a02a8c89`
- Candidate Mesen receipt `51064f55fb39b1dfa59e7c9e20aa67fcb57180c6d2365f78ecbb6d37fdf0069f`
- Candidate controller `662a49401c12ab22200394cea34b919985a4663f4bc38b99db94341961718221`
- Downloads Mesen receipt `0d8861c3102a5a1fb721b3ce6fe3dfde8feec385c2b0a6807e4d5c57c07d88fc`
- Downloads controller `96b6aa7760e0d9567aed999405d5aa359357f9cf86aa2f9e99f45f427e6daced`
- Late-stage driver `b2eae50bb480049446303bdc6e56c1c771faef1a5160b62f3c5606adb91e69ee`
