# Mini Mario source reference

The expanded goal adds Mini Mario from
[Mico27's Super Mario Bros Mini](https://mico27.itch.io/super-mario-bros-mini)
as a Mario alternate, with an innate wall-grab if traversal requires it.
The [upstream project](https://github.com/Mico27/SuperMarioBrosMini) is a
Game Boy Studio remake with custom platformer state code.

The source packet pins Git tree
`56d5a30ff8f58096c074ca59656efc5f787d0edb` and independently verifies each
selected blob's Git object ID and SHA-256. Fifteen direct inputs total
143,096 bytes, compressed to 27,785 bytes. It contains the platformer/state
source, relevant engine settings, actor source, Mario/fire palettes and
the original small/super Mario sprite sheets. Each sprite sheet is 128×16.
No whole repository, scenes, compiled artifacts or dependency trees were
copied. The retained packet is
`docs/qa/checkpoints/2026-11-02/mini-mario-reference-v1/reference.zip`.

The project records walk/run velocity 3665/5602, jump velocity 12288,
gravity 2048 and coyote/jump-buffer values 2/2. These are original engine
values; their fixed-point units and caller order must be preserved or
explicitly adapted before using them in NES movement. Copying the numbers
alone would not establish matching behavior. The source state enum has
ground, fall, crouch, skid, jump, climb, blank and swim states; references
to `last_wall` alone do not establish a working wall-grab.

This is a verified reference packet, not a playable implementation. No
original compilation, NES physics/CHR port, wall-grab, menu admission or
stage clear is claimed. Keep source behavior separate from any traversal
adaptation. Credit Mico27, with Michirin credited for upstream music/sound.
