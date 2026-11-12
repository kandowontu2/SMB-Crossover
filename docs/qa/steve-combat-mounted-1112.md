# Steve combat payload mounting — November 12

`check_steve_throw_controls_live_1111.py --combat-storage` now packs the
combined combat leaves into the authenticated AB00–AEFF row, alongside active
flight. The payload occupies 656 of 1,024 bytes. This mounts the routines;
it does not yet connect enemy-contact dispatch or destruction rendering.

Private candidate SHA256:
`760b71c5d2d2a27efbd6a5e1ae1ac7b7fd6492cc47de501323f83f6fadac500d`.

Bounded cold test session 96556 exited 0. It checked 78 NMI cuts, 11 fault
locations, 701 declared resident edit bytes, the 224-byte scatter payload,
and all 1,024 extension bytes after the actual Prince overwrite/return.
The original 384-byte punch tail remained intact. Loaded direction and
launch routines executed successfully. No output files or captures were
created. Downloads and the release remain unchanged.

Native enemy contact, death visuals/audio, and emulator validation remain
required before delivery.

Bounded gameplay session 93471 also exited 0 with the same candidate hash.
All six controller launch cases (states 5/6/7, both facings) passed recovery,
outbound flight, hidden phase, homing, and exactly one reattachment update.
The check verified 102 player recovery DMA updates. These are CPU/PPU model
tests, not a Mesen playthrough or evidence of working combat dispatch.
