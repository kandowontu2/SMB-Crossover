# Mini Mario source reference

November 3 delivery: Mini Mario is unlocked as Mario's ninth Select choice
in nightly `8daf59cc`. The original art and ground/jump/fall/crouch/skid
source port are integrated, with an explicit wall-cling/jump adaptation.
Actual Downloads selection, movement, jumping, landing, sprite rotation,
one-part reservation, palette and collision checks pass. All four 1-1 pipes
and three gaps are crossed without life loss or helpers; the flagpole/next
stage handoff is still unverified. Source actors, swimming/climbing,
projectiles, powerups, original audio and performance need further review.
Work is paused at the user's request. The compact source/native checkpoint
is [mini-nightly-v46](checkpoints/2026-11-03/mini-nightly-v46/receipt.json).

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

The November 3 horizontal port compiles literal acceleration blocks from
that packet as a host C reference and compares them with assembled 6502.
The initial 328-byte ground component passes 432,760 cases. A combined
483-byte ground/jump/fall component passes 963,824 cases, taking 98–271
CPU cycles per isolated call. The original jump and fall horizontal blocks
are also checked for token identity. Tests cover the complete supported
velocity range, simultaneous left/right/run inputs, signed platform
displacements, and animation/attack boundaries. They retain the original
airborne run reversal, which differs from ground turning, and air
deceleration of 208 versus ground deceleration of 256.

The small checkpoint is
`docs/qa/checkpoints/2026-11-03/mini-mario-motion-v4` (16,894-byte archive).
Fixtures remain in memory; no per-case files or emulator captures are made.
This is a source-C comparison, not a comparison with the original Game Boy
machine code or a full game update. The caller resets animation timing
before dispatching the state; isolated primitive preservation tests do not
replace that caller behavior.

The subsequent vertical component adds 359 bytes, bringing the combined
movement arithmetic to 842 bytes. Literal original jump/fall calculations
pass 315,036 cases, including horizontal-speed jump boost, enemy bounce,
fall-speed limits, drop-through and signed saturation. An initial fixture
slice omitted the original delta integration line; its failure is retained
and corrected without changing the 6502 implementation.

The project's GB Studio 4.2.0 source establishes held-jump gravity as 512.
The small reference packet includes its engine schema, plugin-schema
inventory, schema loader and bootstrap initializer; neither the Mini
project nor its plugins override that value. The unchanged component then
passes 482,241 cases with gravity 512, including 35 composed ballistic
episodes that execute vertical movement before horizontal acceleration.
Full-hold peaks are 37.5 pixels standing and 42.25 pixels at full run.
These are collision-free calculations, so they establish neither a native
landing nor an assisted crossing. The 48/64-pixel pipes need an explicit
traversal review; the requested innate wall-grab remains a possible
adaptation. No helper is assigned yet.

The vertical/default checkpoint is
`docs/qa/checkpoints/2026-11-03/mini-mario-vertical-v8` (49,546-byte archive).
It also preserves the original sprite definitions: the small body has a
6×7-pixel collision box, the powered body 6×15, and both use eight source
frames. The local Game Boy reference is
`C:/Users/kando/Downloads/SuperMarioBrosMini.gb`, SHA-256
`837d39a438f85c5b3ef32c4e41c6c4403147046a7e93bdeac039a09a4a202c81`.
Its header checksum passes; source-to-binary provenance and instruction
equivalence have not been established.

A bounded original-ROM observation subsequently found the exact 22-byte
parameter block uniquely at Game Boy CPU address `$DC1E`, at frames 300,
600 and 1000. This confirms the live constants, including held gravity
512. The single screenshot is black and has been retained as a limitation;
the observation does not certify successful visual boot or gameplay.
Its compact packet is
`docs/qa/checkpoints/2026-11-03/mini-mario-original-v10` (6,989 bytes).

Mini Mario is not playable yet. Full state dispatch, world collision,
lifecycle, graphics, audio and menu integration remain, along with an
innate wall-grab if traversal requires it. No native RAM or code allocation,
helper need, stage clear or nightly update is claimed.
Credit Mico27, with Michirin credited for upstream music/sound.
