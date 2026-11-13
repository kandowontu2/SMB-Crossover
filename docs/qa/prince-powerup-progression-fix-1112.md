# Prince mushroom progression candidate

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

Not delivered: natural block acquisition, interrupt cuts and full-stage candidate
regression remain to verify. Downloads and Current release remain parent6d0346.
Next: validate helper interrupt behavior and natural item acquisition, then
candidate playthrough and normal guarded nightly/IPS delivery.
