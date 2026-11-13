# Prince mushroom progression delivery

Parent installed ROM: `6d0346164b7099f8e75cdbe22a9e9f1fd5f4f673116fd1dcb48a3cee620734c2`.
In-memory candidate: `cebb0ae64b4e6cc92e473a239cb8fd4011d54cfd5e6814013a3afbd2de2bf7d7`.

The accepted mushroom previously healed Prince without advancing PlayerStatus;
the next native block therefore revealed another mushroom instead of a flower.
The new helper sets PlayerStatus to 1 only on accepted mushroom paths, including
full health. It does not grant the sword. Flower pickup retains the existing
sword grant and action. Dead or immature pickups retain their original behavior.

Funding: NativeCall DA1B uses relocated Landing tables at D4C8/D4CD/D4D2;
its retired C7F3 table bytes hold the eight-byte helper. The authenticated cold
state stream contains the exact checked preimage. No allocation expands.

Validation: bounded `check_prince_powerup_progression_1112.py --candidate`
passed actual cold loading, native actor collision/collection and subsequent
PwrUpJmp reveal (HP4→5, item consumed, status1, next type1, sword still absent).
72 direct pickup cases cover HP0..5, status0..2, mushroom/flower, immature/mature.
No output files or captures were produced.

Actual IRQ and FF lag-NMI checks passed at64 instruction boundaries each across
healing mushrooms, full-health mushrooms and flowers. Minimum SP197. Cold state,
registers, maps, native scratch, OAM and CHR latches agree with uninterrupted runs.

Physical Mesen controller-only full1-1 passed into active1-2, HP5/lives2,
frame16355. Installed Downloads repeated the exact receipt. No capture files.
Receipt: `a08e3b269c53fe9f29e4284de6ba4d9896cb4780016b5b52bd719a2a09cf102a`.
Controller: `2192f9cabc250bd55db10d902bd36a202137c978c7b8b6a33daac0c5399ff3f2`.
IPS: `9b7e72e7a772c0b1bbbd8054f86f3c08e64b7450c48f9ed0237bec80f9b7e3ad`.
Direct replacement installed exact cebb0ae6, with automatic patch guards before
and after, no backups. Reverse transform reconstructs parent6d0346 exactly.
Current release publication pending.

Natural block acquisition remains unfinished. The full-stage route does not
earn these items; the pickup proof is an explicitly controlled native scene.
