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

## Loaded native defeat verification

`check_steve_throw_contact_loaded_1112.py` now executes the mounted contact
routine against a runtime state reached by earning Alpha through the level.
Bounded session 89038 exited 0: 24 combinations of Alpha/Laser actor IDs,
robot HP 1/16, enemy HP 1/2/6, and cooldown 0/7 passed. Lethal enemy hits
execute the real native bank-switched defeat routine and set the defeated
state; robot damage still runs afterward, including fatal robot hits. The
test checks return bank mappings, robot age/HP/timer, and enemy cooldown/HP.

The initial cold-only fixture lacked initialized runtime services. The warm
fixture additionally requires `CurrentBank=3` when explicitly mapping raw
bank 3 at A000, alongside `CurrentBankC=2`. Omitting the logical bank shadow
made the native call return through the wrong bank; the fixture now keeps
both hardware mapping and logical shadow consistent.

Candidate remains `d0f7594c…`. These are direct loaded-routine calls after
normal setup, not controller-triggered robot contacts. Score placement,
audio, interrupt scratch ownership, contact admission, age advancement,
and fatal rendering remain pending. No output files were generated.

## Contact scan admission

The mounted payload now includes `steve_throw_scan_1112.s` (110 bytes).
It admits Alpha/Laser actors, age >=12, no armor or transformation, an active
throw, visible throw phase, and a nonzero pose. It composes world-coordinate
conversion, enemy selection, and damage. Scratch bytes 00–0E and 90 plus the
caller's ObjectOffset are saved/restored around contact. Normal enemy contact
uses flag 01. Surviving age increments with saturation; fatal age stays zero.

Bounded session 88035 exited 0: 24 loaded contact cases, including actual
native enemy kills, plus ten rejection/saturation cases. Tests verify scratch
and ObjectOffset restoration. Candidate:
`c927815d46e960571a3d2e646af7b770cdd6d8d27b9d7ed63fb1b6e6e51aec45`.
Combined row is 876 bytes, leaving 148. The scan entry is loaded but not yet
called by the gameplay update. Interrupt safety remains unverified.

The read-only art helper found no free pair of 32-byte cells in CHR710/711:
native item records occupy CHR711 tiles 41–6D, Alpha uses 6F–79, and Laser
uses 7B–7F. CHR710 has native shots, tokens, and Laser cells. The remaining
32-byte tails in CHR339 and CHR307 cannot simultaneously supply both missing
explosion cells in the current mapping. Hardware sprite slot 1 also contains
native misc graphics; replacing it would corrupt unrelated actors. Do not
overwrite these cells. A properly funded/remapped atlas remains necessary.
