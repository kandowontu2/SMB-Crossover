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

## Interrupt correction and funded explosion cells

The first interrupt sweep exposed a real geometry hazard: NMI overwrites
zero-page 00 while the point conversion was using it. The live linker now
uses point 03–06, low 07–0A, high 0B–0E, delta 90–91, and extent 92.
The scan saves/restores 90–92 in addition to its previous scratch range.
Interrupt comparisons deliberately exclude 00–02, which are not live geometry
inputs or outputs in this version.

Bounded session 31031 exited 0 with 24 contacts, ten rejection cases, and
346 NMI plus 346 IRQ injection points. Twelve mapper publication windows
were checked by executing the pending STA 5115 on both the interrupted and
uninterrupted branches and comparing their resulting state. Native kills,
bank returns, and all live contact scratch survived. Candidate SHA256:
`ba910ef27bdafbe5547d82f183b30805c7880383aa508f7b72a3163e1ec436f0`.

The subsequent duplicate-cell audit resolves the CHR shortage without
overwriting other images. CHR711 cells +1E0/+200 equal CHR710 +280/+2A0.
Only the shared item-9/item-13 record at PRG97:C210 references those old
tiles. Remapping record C211 from 5F to 29 and C215 from 61 to 2B preserves
pixels for Mike/Jay/Steve, whose shared JnDraw publishes both pages.
`steve_robot_death_art_funding_1112.py` qualifies exact publication opcodes,
item pointers, all 71 native packed records, and identical item pixels before
replacing the freed 64 bytes with original donor cells 51/53. Root bounded
test passed with zero output files. These art edits are not mounted yet.

Helper audit also identified the later routing seams: intercept the grant
call before LaserLifecycle/FirstBotActive for actor FF; retain projectile
updates through timer expiry; branch LaserTick before its normal pose call.
The renderer can branch at SteveLiftDraw, then reuse its existing BuildPose
and draw/projectile suffix. Preserve a death-frame marker on terminal actor
zero to avoid drawing stale Laser body art. Gameplay hooks, rendering,
audio, and emulator validation remain pending.

## Explosion art mounted and renderer checked

The combat-storage proposal now applies the two item-reference aliases and
installs original donor cells 51/53 in the freed CHR711 cells. Bounded cold
session 19142 exited 0: 78 interrupt cuts, 11 faults, exact punch-tail retention,
and full Prince overwrite/restore passed. Candidate SHA256:
`9d2262e7c0ef1efbe173fbfac1b9820502eb259c8b9efb9ce17fe4be67ea5ce6`.
The current code row uses 888 bytes before the new renderer.

`steve_robot_death_draw_1112.s` supplies a 77-byte renderer multiplexer.
It uses a death-frame bit to remain handled through terminal actor zero,
draws retained-body hurt colors, selects original explosion records, and
reuses the existing pose builder and projectile suffix. Records occupy 44
bytes plus four pointer bytes. A zero-byte label `SteveDeathBuildPose` exposes
the existing builder entry without changing its machine code.

Bounded session 18684 exited 0: 16 visible explosion cases, 16 hidden cases,
and four retained-body facing/polarity comparisons passed with balanced stack.
The renderer comparison is an isolated CPU fixture using the actual pose
builder; native projection/draw calls are stubbed. The 125-byte draw/record
addition is NOT mounted or called by gameplay yet. It would leave only eleven
bytes in the current row; update dispatch requires further packing or another
qualified allocation. No files/captures were generated by either test.
