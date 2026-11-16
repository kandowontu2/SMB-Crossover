# Celeste passive Flower and dash pictures

Compile/restoration qualification only, exact00bb. No screenshot, gameplay
model, Mesen, game byte, ROM, capture file or native result is produced here.

New API `replay_celeste_flower_images_00bb_1116.controller(raw,'flower')`,
`metadata(raw,'flower')`, `family()`.

| Pin | SHA256 |
| --- | --- |
| Picture factory | `227ab25914f8d261e38893667c9d0a48fb7c76dd4ed105ffb283381e31197c87` |
| LF picture Lua | `13cc0ec068b8c6979e67b2eaffa1f215c0817d6266a76d6d616d12cd4b77074d` |
| Frozen functional factory | `528c17f0896d79744058ea6941d41b13f2c600d832629b4141ec16b34a646179` |
| Frozen functional LF Lua | `05b6e7c41db900ab6bc8827ee4d83136bdd761483ba945b385af0a7a1a5ec976` |
| Compile/restore receipt | `f11e277e8cb512046dc05217f17dc96f4338e4bb9733a68427492e54c31332c5` |

Removing the declarations, image-count assertion, sole new `visual` receipt
field and appended passive observers reconstructs the exact frozen controller.
Existing controls, menu, readbacks and functional assertions remain unchanged.
`functional_receipt(receipt)` deep-copies and removes only `visual`, enabling
root to compare the native result with functional receipt
`083deff3a20a0d3a2fe10f6a2e5d8c8acf8729348c7ab12c84b2566ed52782a4`.
No parent controller or native fixture is edited.

The intended native observations are two actual `endFrame` RAM PNG strings:

1. Actual mature live Flower remains uncollected, with small Celeste visible.
2. The earned dash has actual returned motion, State6 and positive Timer,
   while small Celeste remains visible, before the functional18px endpoint.

Each PNG must have the real PNG signature and be at most65536 bytes; exactly
two are required on success and emitted as `SMB_NATIVE_IMAGE` base64 stdout.
No file or source-model screenshot substitute is used. The sole added receipt
field is `visual={pictures=[...],wall_jump_observed=...,wall_jump=...}`; the
last member is absent if no qualifying wall jump is naturally reached.

Each picture records actual physical OAM (at most32 visible records), a separate
Celeste owning-OAM subset near expected small rendered top PlayerY+16 and
current hero screen X, sprite height, palette, observed MMC5 mode/banks and
at most16 direct CHR ROM pattern pairs. The owning subset requires CHR740..743
and proximity, not a fabricated source sprite image. Those records scope the
eventual visual review; compile alone proves no appearance or palette quality.

An optional first naturally reached tier1 CmWallJump is read-only and not an
image-success gate. The mapped PRG98:B3EF ingress binds eight actual bytes
`A9018D245CAD5905`, with bank SHA256
`93ce5f75102e23962268afe86fb7db2fb0208160724b38b0cafe105f54763c38`.
One entry and dynamic PC/SP return record FootPhysics, WallKick, stamina high/
low, Up/LR and native state; absence cannot be promoted to wall-grip proof.

The checker initially failed before compilation because its native trap named
the historical helper's nonexistent `run` attribute. Correcting the trap to
the actual Runner.Native API then passed. This setup error executed no source
gameplay, screenshot or native call and says nothing about game behavior.

The successful bounded compile used absent
`build/celeste-flower-images-source-1116`, max1file/600s and zero generated
files. All source handles are terminal. Root retains the sole native queue and
must separately authorize/run the visual capture and inspect the actual PNGs.
