# Rash empty idle/walk CPU profile, November14

Exactf11a source candidate:
`f11a25b892779cb0d5192457f7feff548f35019818cd75dfef5bdf3f2419b865`.
The genuine compiledRash menu/Start constructs physicalRAM3 normally. Four
neutral Main warmups precede48 idle and32 Right updates. Only controller
inputs0/1 are provided; no health, actor, terrain, coordinate or ability seed.

The profiling tool is `tools/audit/profile_battletoads_current_idle_1114.py`.
All producers run through bounded `build/battletoads-idle-profile-1114`,
max-files1,timeout600, with file-write and Mesen traps. Generated files0,
output directory absent. All frozen camera composers/factories/checkers and
the allocation-pinned669b source/593f QA are unchanged.

Corrected session26047 terminal exit0 binds actualBtPhysicsStep to RAM3/A094
from currentBtCoreStep's tail-JMP operand. An initial62872 report listed its
synthetic linker segment asPRG0; it did not attribute the real call. The
corrected report has one physics call per Main, no unclosed function scopes,
and identical scheduler totals. Final session73944 terminal exit0 independently
records and asserts exactly1 GameLoop entry and1 return in every individual
scheduler iteration, not merely aggregate48/32 counts. All80 assertions pass;
the cycle vectors below remain identical. No source process remains active.

Frozen profiling source SHA256:
`468c330cd08241be76915040bbca334b635c0abb1f8874efa3dc26a82a6471e8`.

## Measured source cost

| Measurement | Idle48 | Right32 |
|---|---:|---:|
| Mean scheduler cycles/update |36604.0625|36864.5625|
| Range |36496..37351|36678..37599|
| Mean actualGameLoop inclusive cycles |36574.0625|36834.5625|
| Separate normal-NMI cycles/update |4324.70833|4305.6875|
| PlayerX |40→40|40→83|
| CameraX |0→0|0→1|
| HP/lives/power/Star |47/2/0/0|47/2/0/0|
| Active / onscreen native enemies, every sample |0/0|0/0|

Every actor sample is empty, so there are no active or onscreen enemy
positions to list. No B or A input occurs. NativeState0/engine8/Y176 remain
stable; minimum sourceSP184. Normal NMI is tracked separately from the
scheduler CPU object, rather than silently adding it to the Main figure.

| Inclusive function cycles/update | Idle | Right |
|---|---:|---:|
| BtCheck,12 calls each |3900|3900|
| CfOrBtCheck,12 calls each (includesBtCheck) |5052|5052|
| BtMovement |1308.5|1571.78125|
| BtCoreStep |718.5|987.59375|
| ActualBtPhysicsStep |711.5|980.59375|
| BtDraw (includesGraphics and renderer) |2742|2742|
| BtGraphics |1083|1083|
| MetaspriteRenderLoop |1324|1324|
| BtWeapons |215|215|
| BtImportNative |147|141.1875|
| BtExportNative |194|194|
| ScrollHandler |166|169.75|

Function costs include callees and overlap one another. The separate map
partition assigns8951.625 idle/8949.96875 walking cycles to lowRAM (chiefly
farcall transport),4288 toPRG93,2978.5/3241.78125 to physicalRAM3,
2801.29167/2801.3125 toPRG4,3646.27083/3641.75 toPRG126. The header loop's
PRG93 ADD9/ADDC instructions each cost768 cycles/update. LowRAM016B/017A
cost1062.75/1014.75 idle. These identify executed work, not removable work.

Current exact inlinedBtSave/BtRestore patterns each span30 bytes. Four pairs
execute per update:256 save +304 restore =560 cycles, with64/76 per pair
component asserted. Six static sites exist, but only the executed four pairs
are charged. FullCoCheckCode has zero calls here; allPRG65 instructions total
70 cycles/update. This differs from Contra Force's full-validator profile.

## Per-update scheduler cycle vectors

Idle48:

```text
36539 36505 36547 36502 36547 36794 36547 36497
36546 36505 36539 36505 36539 36807 36547 36497
36547 36497 36751 37351 36547 36802 36538 36511
36539 36505 36547 36496 36547 36794 36547 36497
36546 36511 36539 36505 36539 36806 36547 36702
36547 36497 36546 37339 36547 36802 36538 36505
```

Right32:

```text
36678 36775 36817 36766 36817 37070 36817 36767
36816 36775 36809 36775 37014 37071 36817 36769
36813 36763 36812 37599 36825 37080 36816 36783
36817 36789 36825 36774 36825 37072 36825 36895
```

## Scope and next source audit

This is source CPU attribution. It does not establish native FPS or an idle
cadence acceptance. Root's separate nativeRash53541 fullstage positive is
6464physical/4359Main/2799Btsteps/58next/25 grounded1-2/HP35/lives2, receipt
`f64ec257be8f7dec5c59b10bc7fb26f1519fbc328b6cf2f10b506e314197b48b`.
That mixed traversal count is not an idle clock. Root47036 later verifies both
full routes on actually installedf11. Separate root86156 terminal actual-native
idle observation:48 Main returns over72 physical frames,49 sourceBtstep hooks
across48 intervals,NmiSkipped+48,0 active actors,x40/Y176/HP47/lives2. Exact
Lua `f6cc1a294935e7e8a76ba301f8de423b9227880b34059731f9f7b375f89a336e`;
receipt `52d1f1f4d179ac568505e021ed03d40e38349d54f31c5b4206c27aa4d67f4ea0`.
This actual bounded idle observation confirms lag independently of the source
profile. It is not inferred from source cycles or the full-stage ratio. No
idle-lag improvement has been implemented or accepted by either observation.

The measured donor physics is a small part of the empty-opening cost. The
next read-only audit will enumerate current explicitly unsupported BT service
slots and their real caller/ABI/foreign behavior before proposing a way to
avoid unnecessary validated farcall roundtrips. No header cache, validation
bypass, new state, performance code or allocation is placed by this work.
