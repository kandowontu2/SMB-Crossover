# SMB2/Doki flag handoff: private native findings

Downloads remains `7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc`.
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
