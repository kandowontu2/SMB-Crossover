# SMB2 DMC sample-alias timing diagnostic

This is a timing investigation, not an alias repair or a gameplay failure
verdict. The first native observer completes the route but exhausts its
record budget; a separately pinned scene-only successor is pending.
Current Downloads is exactly
`3684f3d2a418a484befd80fca351d0dc5f9b472f6f067a0a7894994ea343679d`.
The ordinary Luigi full-stage control binding is
`a8e2c9a408daf9fb228c822ab85ccabb98eda00769922dfbec2be0337af47cc5`.
The separate terrain factory remains frozen at source SHA256
`6ad3dade9260e8cc44ed9816f3b621f2b7deb92c538d19b1b69ac8230e20bcb0`.

`tools/audit/replay_smb2_dmc_alias_native_1113.py.controller(raw)` strictly
authenticates current3684, its typed foreground inverse to f88, Bub inverse
to7ef, and the flag/foot/priority/foreground source chain. It reconstructs
the exact Luigi profile above and adds only passive callbacks and receipt
fields. Removing those insertions yields the original text byte for byte,
including all controller decisions and the original25 living grounded1-2
endpoint. No old factory or game byte changes. Its CLI prints metadata only;
root alone writes a controller in its existing output and starts Mesen.

Frozen observer Lua SHA256 is
`b80d9992f21e4b9632de3a9b8abd4352270368f8394285deb226be0968d10e46`;
its factory source SHA256 is
`c39e3abea1bd7ada4397e28635038ceb281fcc3f36d2e18816051f6aa1b9e95e`.
The bounded source metadata/strict lineage/current instruction windows,
Lua compilation, read-only runner guard and exact base-text inversion pass.
There are9 authenticated byte windows and11 callback sites. A separate
explicit observer-only mocked callback fixture sends150 changing writes:
64 records retained/86 dropped. Two hundred native-tail mock calls retain
16 records/drop184. These are cap tests, not native/gameplay evidence.

The new observer has one64-record event cap, with at most16 native
tail/farcall records within that cap. Repeated identical status contexts are
deduplicated. Excess observations increment counters without changing the
route. It records frame, cycle, Main, engine, level, source audio owner/state,
debugger-read4015, actual resident mapping/tail/target, and available selected
APU state fields. It uses `nesDebug` reads, never CPU-side-effect APU reads.
There are no emulator state writes, cancellations, grants, files or images.

The actual source writers are authenticated at physical PRG74:

| CPU writer | Instruction | Observations |
| --- | --- | --- |
|BB93|`STA $5117`|sample alias selection; after-write execBB96|
|BB9C|`STA $4015`|source sample start; after-write execBB9F|
|BB78|`STA $4015`|source stop; after-write execBB7B|

Mesen write callbacks report the next PC. The observer authorizes each
writer using the exact preceding three-byte instruction and physical
mapping. Before/current write status and the separate post-instruction
debug status are distinguished. Shared mixer4015 writes are excluded.
Resident snapshots are restricted to ordinary level1 after gameplay starts.
The observation does not assert a predetermined audio outcome.

## Source-model evidence and contrary timing result

The full Luigi source CPU run on frozen dadb reaches level1, engine7,
X40/Y176/HP31/lives2, then the unchanged strict bus rejects a write to9139.
Fault instruction PC is A176, with maps254/207/208/248, SPED, A C9 and Y6D.
Physical PRG79 A175 is `DD99CC`, `CMP $CC99,X`, inside Chip/Dale graphics.
A176 is its operand; the subsequent decoded `STA $90CC,Y` is not an
authorized program entry or writer. No bus assertion is relaxed.

The narrow mapper/SMC trace identifies the preceding actual path:
sample mirror120:E5CC, the resident `RyuSourceBodyAfterBGBridge`, selects
raw207:BB87 through FarCallCommon. In current PRG79, BB87 is the BPL inside
`HuGmStatusName::Copy` atBB80, followed by PLA/TAY/RTS, not a valid public
entry. Canonical127 and125 instead select raw194:B438, current
`ThPostNativeHot`. The current compiled labels and Thomas source preparer's
explicit HuAfterTerrainGate-to-ThPostNativeHot rebinding agree. This is real
stale resident-alias debt, independent of the CPU model's APU limitations.

Exact44-byte E5CC-window hashes on current3684 are:

| Physical PRG | SHA256 | Encoded fallback |
| --- | --- | --- |
|119,120|`dd2799b5dfe5c241a1a1b4392cf0f0221f4050fea6b75db4245d292a6309b77c`|raw207:BB87|
|125,127|`8c872431079201f1f39b26893f1157f04736ce5377a6fd94d15f384decfe89ab`|raw194:B438|

The established ControllerBus has no DMC reader/completion clock:4015 is
ordinary stored data, so a written busy bit can persist. That initially
suggested an expired-sample model artifact. A second **unmodified** full
source run with passive APU-write/cycle observation contradicts that
stronger explanation:

- The only real sample start occurs during level1/engine0 at executed cycle
  99,266,515, source BB9C, rate0E, length321 bytes, addressF580, alias120.
- The resident E5CC call occurs at99,301,569, only35,054 executed cycles
  later, with4015=1F and engine7. The strict fault follows196 cycles later.
- Current PRG74 sample tables and writer bytes equal the retained original
  linked source. All eight requests use non-loop rates0E/0F. This sample's
  conservative completion bound is186,764 cycles, including an extra output
  byte and4 DMA cycles per byte; the maximum over all eight is622,924.

The DMC status bit follows the remaining-byte counter, rather than retaining
the enable write. NTSC rates0E/0F are72/54 CPU cycles per bit, and sample
length is16 times4013 plus1. These peripheral facts are documented in
[NESdev APU status](https://www.nesdev.org/wiki/NES_APU) and
[NESdev DMC](https://www.nesdev.org/wiki/DMC).
The executed-cycle counter omits idle wall time and hardware DMA timing.
In particular, `Frames.frame(..., whole_pass=True)` injects NMI directly,
starts a fresh CPU at IdleLoop and stops upon returning to IdleLoop with
SP253. Native GameLoop has cleared NmiDisable at that point. Real hardware
would spin in IdleLoop's LDA/BEQ until the next NMI; the source driver stops
before that wait and directly injects NMI in the next epoch. Its input/end
frame callbacks advance no video/APU clock, and long Main calls receive no
hardware-timed busy NMIs. Thus35,054 is a lower bound on elapsed cycles,
not an elapsed physical-frame/APU duration. Comparing35k with186k proves
neither that the sample remains active nor that it has completed on actual
hardware. The stronger model-only classification is withdrawn, and a real
active-sample trigger is still unproven. Successful physical full routes
also do not exclude a timing-dependent stale-alias hazard.

Both diagnostic producers used the existing bounded zero-output root
`build/prince-pickup-reach-1112 --max-files 1`, with300-second limits. No
ROM, actor, position, health, source audio state or APU status was seeded or
changed by those observations. No mirror repair is proposed from this
evidence alone.

## First native observer and scene-only successor

Root ran the frozen b80d observer on actual Downloads3684: full route PASS,
4744 physical frames/3820 Main, HP31/lives2, receipt
`ebf1deb136b938432d1ae6158cd85b5f890425c9d0e94cbd08aaae8f99b69a8d`.
Its64 records were all filled by frame1073 with early level0 status stops;
495 later observations were dropped. Counters show402 resident entries,
three deduplicated native chains and two named stale-target entries, but
no retained level1 timing. Those target-name counts are **not** causal
evidence: v1's pending target can survive a special branch or live alias
change, then count a later legitimate name-copy fall-through. No active
sample hazard is concluded from that receipt.

The new checked path
`tools/audit/replay_smb2_dmc_scene_native_1113.py` keeps c39e/b80d unchanged.
It accepts exact3684 only, authenticates the frozen old source/Lua, and
returns standalone Lua with SHA256
`5bd36d95616f88bc30946c7b6d0a2a6aa7d7948964848236ecef02b7e76e016f`.
The new factory SHA256 is
`62d5bf8cd39ac07b45115f0031063d3914c9c670a56f30e1990130657d09b9d8`.
Removing its observer changes reproduces exact b80d, so the original
a8e2c9a4 inputs and25-grounded endpoint remain unchanged.

All recording/writer observation is filtered to world0/level1 before the
64-record budget. Status dedup uses only DMC bit4, available actual
bytesRemaining, resident bank and engine; raw4015 remains in each retained
record. Pulse/noise bit changes cannot fill the budget. The native subset
remains capped at16 snapshots, with at most three detailed interest
contexts, five records each for a complete normal chain.

A named old/canonical target now requires a fresh same-Main token from
E5CC through E5F5, FarCallCommon015A and actual SMC JSR016B. Each step checks
live target, physical bank and expected SP. Target entry additionally
requires the correct three-byte-deeper SP and real stack return016E.
The token is bounded to120,000 cycles/four physical frames and expires at
the next Main return. The observer then witnesses FRC return016E, the
original caller's mapped return/SP and the next Main outcome. A live alias
change before E5F5 uses that actual tail, rather than retaining E5CC's old
pointer as an assumption.

Bounded source checks pass strict lineage/current bytes, Lua compilation
and exact input/endpoint inversion. Explicit mocked observer fixtures
accept a correct old chain and a correct alias-to-canonical flip, reject
three uncorrelated named entries, witness both FRC/resident returns and
next Main, exclude100 level0 writes, deduplicate100 low-status changes to
one record and retain the64-record cap. These are observer fixtures, not
native timing or gameplay evidence. Root's scene-only physical trace is
pending; no mirror, physics, state or input patch is proposed.
