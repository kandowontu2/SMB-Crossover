# Mario and Luigi pickup checks

The archived Easy 1-1 playtests on `731c918b` prove normal Mushroom and
Fire Flower progression for both brothers. Each run selected the intended
character, hit the authored blocks, collected both items and watched the
actual 60-update transformation for each item. Both characters finished in
Fire form with two lives.

| Character | Collected Mushroom | Collected Fire Flower | Further gameplay |
| --- | ---: | ---: | --- |
| Mario | Frame 839, from block X336 | Frame 1457, from block X1248 | A fireball hit an active Goomba, then both shot slots cleared |
| Luigi | Frame 851, from block X336 | Frame 1653, from block X1248 | A fireball reached a live Green Koopa, then the shots cleared |

The level clear and Mushroom and Fire Flower results retain their respective
tested builds.

- [Mario's native playtest](checkpoints/2026-10-26/mario-physical-flower731-v1/reports/mario-flower731-east-native-2026-10-26.txt)
- [Luigi's native playtest](luigi-flower731-Rg-native-2026-10-26.txt)

## Hidden 1-UP and Star playtests

The current Easy 1-1 replays ran against the installed `32eaf178` nightly.
Mario and Luigi each hit the hidden block at X1024/Y128, collected the
item after it fell to the floor and gained a third life. Both stayed
grounded before the pit through 25 further movement updates.

Mario also hit the Star block at X1616/Y144 and collected the Star on its
bounce. It started the invincibility timer and Star music, awarded 1,000
points and remained active through his grounded finish.

| Playtest | Physical frames | Mesen receipt SHA-256 | Controller SHA-256 |
| --- | ---: | --- | --- |
| Mario 1-UP | 1,166 | `dc04b36842e89a05bfa705d3554f18ad388c686df52d69d696b84f433c9b014a` | `934d8a551e45b4ec37d35974f0ca651a4dac127738578d21ea7b3791eea2564b` |
| Mario Star | 1,564 | `8bea033f9826327aa9454eefd88b8d2ee852e29645eccad1a0a3e42504b344aa` | `a76fc30ff0bdd83a48325d668c102041d9a1bacf7b1e7bf33e99aa83747986e7` |
| Luigi 1-UP | 1,221 | `a6295b8a8f16ea3d262b1d17e2d9e059987181828b966c0315e07d178f74b613` | `d1d7cf79d722c6ea8af137bf2acd95dc26d252d432c6d2998a4b27cd878e8ae7` |

In the first Luigi Star replay, Luigi died at X1224/Y112 on the way to
the Star block when he came down beside a Goomba on the Fire Flower row.
That attempt stopped at physical frame 1,030.
Receipt `07a654ce3eb4cb61d7a328d8c7c1ced6f8bfd8391babf8d129af2a99d28d1abe`.
Luigi's Star needs a passing replay. These tests created no captures.
