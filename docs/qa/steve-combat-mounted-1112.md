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

## Robot coordinates for contact

`steve_throw_point_1112.s` adds a 91-byte conversion from wrapping Q4 robot
coordinates to the biased native world coordinates used by the overlap
worker. X is reconstructed relative to the full camera position, so passing
4,096 pixels does not put contact back at the start of the stage. Signed Y
is converted with arithmetic shifts and the native page-1 offset. The caller
must admit a visible robot within 2,048 pixels of the camera.

Bounded test 79132 exited 0: 2,268 conversion cases and 472 composed
conversion/admission/rectangle/overlap hit-or-miss cases passed, including
fractional coordinates, negative Y, page carries, and the Q4 world wrap.
No outputs were created. This new conversion is not mounted or dispatched
yet; scratch ownership and incoming robot damage still need integration.

## Updated mounted payload

The subsequent contact-order correction adds the conversion and a 19-byte
contact composition to the mounted row: 766 bytes used, 258 remaining.
Candidate SHA256 is now
`d0f7594ca698e8078086a74a3da5e23856d07d8a436049f713819cd45693db99`.
Bounded cold session 18805 exited 0 with the same 78 cuts, 11 fault locations,
and complete Prince overwrite/restore checks. Contact dispatch is still not
hooked into gameplay. See `steve-robot-destruction-1112.md` for the corrected
outgoing-before-incoming damage order and original-ROM comparison coverage.
No output files were generated; no nightly or release was replaced.
