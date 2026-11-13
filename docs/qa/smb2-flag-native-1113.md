# SMB2/Doki flag handoff: private native findings

Current Downloads is `f88cfe5aee15bb3921c691b7f06d905246be9ff88b9b43eea71c2405722724a7`.
The older7ef base and native receipts below are retained historical evidence.
The private flag proposal is
`0e9e9254927236bcc651e79da36a77924eea5481421858a05f869b15298412e1`.
It is not installed or released. The source qualification is recorded separately
in `smb2-flag-handoff-1113.md`; those CPU/component passes are not a native
full-stage pass.

## Actual Mesen result

The frozen ordinary-controls Imajin route, Lua
`09c0f838b1c8f592d7a470f51892cafe03227dbd898e5c1b61d317fc1873c453`,
now reaches the actual native flag, castle and next-level entrance states.
It crosses all 1-1 terrain without helpers. Empty opening remains 48 Main in
48 physical frames, with no skipped NMI, no actors and both lives. The original
later rising Goomba contact at 1257/91 versus 1263/87 reduces health 31 to 15;
no life is lost.

The full native receipt
`48815812b48be3b7960f9814863ce68c439de37e59d2927fad90c15196accd2c`
is **negative**, at the 22,001-physical-frame bound: only 3,065 Main returned.
World 1-2, area type 1, engine 7, X40/Y176, health15/lives2 remains stuck.
The original formatter did not distinguish scene setup from active entrance,
so that initial observation alone did not identify the failing phase.

## Passive phase and mapping diagnostics

`replay_smb2_next_area_diagnostic_1113.py` appends observations to the same
frozen controls. It never writes ROM, game RAM or emulator state. It stops
intentionally false after 600 physical frames without a returned Main in
world 1-2. It retains at most 64 phase changes and eight sparse samples,
plus one PNG in memory. No capture file, video, state dump or image sequence
is created. `run_smb2_flag_native_1113.py --next-area-diagnostic` uses the
same bounded two-file output as the private candidate.

| Observer | Lua SHA256 | Native receipt SHA256 |
| --- | --- | --- |
| Phase fields and one memory PNG | `f4f29a9965cf3d3d5bb595b266bc4c3cc99f529a76538ee95f9d3a3291ccd312` | `fbac49f9b748ce207bd4b9051e89751164992474cd41206c38ac50004935d030` |
| Same observations plus actual mapped PC, stack and CPU registers | `d9c63c0720beabfc6c419a1515899418cfe056bcb8995f94a5c050054d447f4d` | `0e131a578a09dd40b80d5f625eea5856cf1e40cc4efd81bc46adc9416bbcd75a` |

Both stop at physical 4,485/Main 3,065 with identical gameplay state.
The next-stage screen tasks progress normally through task12. At physical
3,885 the operation mode/task is 1/3, engine7, X40/Y176, native state0.
On the following physical frame Main enters but does not return. The final
600-frame observation has:

- OperMode1, OperMode_Task3, ScreenRoutineTask12, DisableScreenFlag0,
  GamePauseStatus0, NmiDisable255, FrameCounter164.
- Engine7, PlayerEntranceCtrl7, AltEntranceControl0, ScrollLock1, area1,
  native Player_State2, YHigh1, source Ready178/variant4/health15, lives2.
- PC `$B144`, SP222, A9/X32/Y176/P0. `emu.convertAddress($B144)` is PRG
  offset397636, actual bank48. A000 maps393216, 8000 maps1032192,
  C000 maps655360, E000 maps983040. Shadow banks are176/208.
- The mapped byte at `$B144` is illegal halt opcode `$02`, surrounded by
  data: B13C..B153 is
  `46fd468da909052102a7056d08a60700a502a9210250aa43`.
- SP+1..FF contains
  `c2306d01940c9c6d01dd6d018149a16d01f66d01bf6d0180a3834f83bd826f3be3`.

This is an actual CPU halt while entering the outdoor walk-to-pipe scene,
not a long lives-screen delay. The automatic entrance farcall/bank path is
under source investigation; no cause or fix is claimed from the PC alone.

The reviewed 256x240 PNG shows the outdoor castle at left, pipe at right,
Imajin at the ground and the status line at the bottom. Its 2,807 bytes have
SHA256 `8ec0e9cb3e23f9b02bed8777a6e146f11bb9bab2eba5866d81bc2fec57cb3c41`.
It stayed in memory, with zero PNGs on disk.

The subsequent bounded bank-write/SMC observation preserves the same controls:
Lua `bd3920452bdc9ef1dc78d393a8003a269d455bd8cb4813e3d72da7aadbb72ce1`,
receipt `9052a1e7f269d1051fbea4732722171a23867fa3ba103880756a98452254ca4c`.
It retains the last16 bank writes and resident jumps in memory. The final
5115 write selects176 at resident PC0169, SP226, with stale targetB101 and
argument25. The return chain identifies fixed126 `DoFootCheck` at9C0A
callingE46A. The source agent's unbroken genuine-route CPU replay reproduces
that bad mapping before the hardware halt.

The authenticated source lead is a stale fixed-bank mirror: the Sonic shared
feet change moved the foot entry fromE46D toE46A and retargeted callers, but
only updated bank127's63-byte head/feet region. The live E-window bank120
retains the old layout, whereE46A is a `JMP FarCallCommon` head-call tail.
PlayerY176 is consequently consumed as the bank argument, with stale S2Head
targetB101. This explains the actual bank48 mapping. Exact mirror preimages,
source reproduction and a narrowly scoped synchronization are being reviewed;
there is no new accepted candidate yet. `S2MainGame` dispatch itself was not
shown to be faulty, and no source physics or bare-feet substitute is proposed.

## Powerup scope correction

The retained October29 design explicitly gives the initially large/two-heart
SMB2/Doki form a Flower. A Mushroom is selected after a real small-form
injury. The source agent reproduced ordinary healthy Flower birth and
injured Imajin's actual Mushroom collector (health15 to47, max-health0 to1,
native erase, sound and popup). These are CPU-model results pending their
separate frozen native test. Do not change PlayerStatus/MaxHealth to force
a healthy first Mushroom or call that documented behavior a new bug.

The private flag proposal remains frozen while the newly reachable entrance
halt is repaired. No local nightly replacement is claimed. GitHub releases
must remain empty; no Current release or patch asset may be recreated.

## Three mirrors remove the halt; sprite priority blocks the pipe

Root independently rebuilt the existing canonical127 source body and verified
the exact three old63-byte mirrors, both full inverses and all unowned bytes.
The separately pinned all-mirror plus flag candidate is
`2c62e1a0de1b732cfa57af59e71c0775396e067bf04aa101e78f644c3e4c9c4b`;
all-mirror-only over7ef is
`690482ef99abb5cc9c4e1cc1bcfecc81fce391722a60ff4bdb3c0f7aa1b87ac3`.
Their proposal is not installed. The three source-owned mirrors are119/120
(SMB2 sample banks) and125 (Castlevania sample bank); only their exact
E45B..E49A regions change,180 actual bytes total. Other mirror debt and all
sample/manager bytes remain unchanged under the narrow allocation.

The frozen full controller changes only its ROM label to the new candidate:
Lua `a6e3fefaadbec7398f11b60fc10475414db57fbf534047e26d5670444fea9276`.
Actual native receipt
`6006649b766039b0060ec4c1c16c844407cce06e83f10d8cd96433a19dce860d`
proves the CPU halt is removed: Main continues returning to the7,000-update
bound,7,819 physical frames. It remains in outdoor1-2/engine7 at239/176,
health15/lives2; flag/castle/entrance are true, underground settled updates0.
The complete exit assertion is unchanged and remains negative.

An initial attribute observer096c0b1d/a65f5a58 reached its64-phase-change
assertion before the pipe because live NmiDisable transitions now continue.
That is a diagnostic cap failure, not another gameplay failure. Replacing
the cap assertion with a ring of the64 latest changes retains bounded memory
and leaves controls unchanged.

Corrected diagnostic Lua:
`5be4870a2f0d4eefff58ecbaa86d327f177a5dfae9795c961f3f5266e68efa85`.
Actual native receipt:
`12e9ce45243f78a14d52fff84420bff700aa1ff460c468e9949a7a2132918476`.
It stops intentionally false after400 returning entrance Main at physical4286 /
Main3466. There are72 real Player_SprAttrib transitions. At Main3217/frame4037,
X147/Y176, native fixed126 PC9CFD/PRG1039613 sets0 to32. The same Main's
source graphics writer B6A5/PRG972453 clears32 to0. That pair repeats through
Main3252/X173; terminal ChangeAreaTimer160 never decrements and the player
continues to239/176. This authenticates the graphics routine erasing the real
native pipe-entry priority/latch bit. Source-owned priority preservation and
the OAM consumer need repair; no such candidate is accepted yet.

The reviewed in-memory PNG is2,766 bytes, SHA256
`e4823eed71b80ebadbc12215d05ac2be6f74fdf5eea19367503f34f24a715987`.
It shows Imajin beyond the pipe at the right edge, with the HUD correctly at
the top. It is not a PNG file on disk.

A proposed19-byte funding design from the older checked-in render source
was rejected before allocation: the actual current Doki palette function is
B7EF..B82D and has no old NativePaletteOffset table. Its actual source and
preimages must be recovered before a priority proposal. The tentative design
did not change any ROM, allocation or current palette behavior.

## Actual Ready85 priority proposal: two natural full-stage passes

The separately pinned private successor is
`dadb9d80702148fe40b1a64d1cfff7ff2df65248b9c72e7c167d32e3589670be`.
It uses the actual Ready85 code, with8 source-owned bytes reclaimed inside
the current palette function and exact scoped graphics/body/caller changes.
Its inverse returns2c62. It is not installed, and its normal-play foreground
priority lifetime remains under review below.

Imajin's original controls and full exit assertions now pass actual Mesen:
Lua `f4b9ebfaee4cd75245ecd3cb0e38b5d4ab6c00127fc2a9f125270448a5ddf5cc`,
receipt `ce9b9c55e30dc1e0118151f3f77381936c49f6af985d96223ff3abc9ae4d44c0`.
The run takes4566 physical/3555 returned Main, with actual flag/castle/pipe
transition and25 consecutive living grounded underground1-2 updates at40/176,
health15/lives2. Empty opening remains48 Main/48 physical/skips0. All1-1
terrain is crossed without helpers.

SMB2 Mario also passes, with the two read-only visual observers appended:
Lua `6f1c494c855d5a946735f660ecd9d43152833eac2d26438b36b5302059037c53`,
receipt `a8092c7c38c1537185c96be94e8e54ef618e54c89c8cff91a18e351efed98395`.
He reaches the same25-update grounded endpoint, health15/lives2, in4484
physical/3597 Main. `replay_smb2_priority_visual_1113.py` leaves ordinary
controls and the full exit assertion unchanged and captures two bounded PNGs
in memory, with no disk images:

- Side pipe:2645 bytes, SHA256
  `ff20a4d447f220d226028752ff71c7360f6b977e93f1da03badd172e4edc13d3`,
  frame3987/Main3273,155/176,engine7,attr32. The reviewed image shows Mario
  correctly passing behind the pipe.
- Underground:2002 bytes, SHA256
  `8c2d0635c1cb45d1d7744041dc6b754acb0d07ce397f442b073c300aebb2ecab`,
  frame4481/Main3593,40/176,engine8,next-area count21,attr32. The HUD, Mario
  and upcoming Goombas are visible.

The second view also proves the priority latch remains32 during normal
active play. The new helper preserves that bit indefinitely, while the old
graphics cleared it. Actual native PlayerCtrlRoutine's normal foreground
clear is a source lead because S2MainPlayer replaces that routine. A player
remaining behind decorative background would be a rendering regression.
Normal-play foreground clearing and the native pipe latch must both work
before delivery; two logical stage passes alone do not settle that issue.

The first2112-pose directed claim used wrong Doki5..7 native-class fixtures
that could reset in S2Ensure. That coverage claim is withdrawn. The corrected
actual-constructor table is0,3,2,1,0,1,2,3, with explicit postcall assertions
that variant/class/size/facing/holding/animation are not reset. Its corrected
2112 Graphics/2112 real OAM pairs pass, with1216 active priority cases;
the old1408 count must not be reused. Source domain/constructor and actual
PublishBody Y0/R3 lifetime gates are separate. Remaining caller/interrupt and
foreground-lifetime work is still open; no complete eight-character or
finished-visual-review claim is made.

## Papa: intended charge controls pass actual Mesen

The separate variant-profile factory retains the complete flag/castle/pipe
and25 grounded1-2 assertions. It uses original Down60 charged jumps where
required, with no new helpers or game bytes. All eight profile scripts were
compiled and bound to exactdadb before the physical run.

Papa's profile Lua
`09092856114a8a74822324682efa4d1675e1e62d560cfbb734708255cc2f2227`
passes actual Mesen with receipt
`2d423f943acd6c47837068709abd2142583385e21adadaf90e11d511c580aa36`:
5015 physical frames,3912 returned Main, HP31/lives2, no injuries, all1-1
terrain and25 living grounded1-2 updates at40/176. Empty opening remains
48 Main in48 physical frames with no skipped NMI. This qualifies the
ordinary controls for the lowest-jump Doki variant; it does not resolve
dadb's separate normal-foreground lifetime defect or install the candidate.
