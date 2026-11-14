# Independent SMB2 post-BG caller/IRQ qualification — November13

This source-only check qualifies the six-operand mirror successor
`12397b1c2557834f6a2b7e23c9915d5dc40c6cabff7a6ee844c1adebf6564c52`
over exact parent
`3684f3d2a418a484befd80fca351d0dc5f9b472f6f067a0a7894994ea343679d`.
The composer/core finite tests and native adapter belong to the separate Prince
task. This checker owns only real-caller, family continuation and interrupt
qualification. No ROM, gameplay, audio, ability, actor or timer state is granted.
No Mesen, ROM file, capture, patch, new output tree or release asset is produced.

Reservation: `docs/qa/allocations/smb2-postbg-mirrors-1113.json`. Only the six
literal operand bytes in physical119/120 may change; all opcodes/PCs, samples,
managers and unrelated debt remain exact. The source-bound composer is
`compose_smb2_postbg_mirror_1113.py`, SHA256
`415ca42d6efe1023a56c147a2d1dc0c8e32c75c98fef31b9f1a54e0fb71b7647`.
Its strict proposal/inverse and exact canonical125/127/source bindings are reused.
The confirmed wrong historical CF:BB87 target is never used as an intended
foreground parity oracle.

## Canonical oracle and exact comparison

Both actual canonical125/127 copies supply the unchanged44B post-BG instruction
worker atE5CC, including intended target rawC2:B438. The test oracle changes only
the **source of these ROM instruction reads** in an otherwise original-parent
model; it retains the actual119/120 fixed map and sample ownership. This permits
comparison with the intended canonical implementation without remapping the
active sample bank. It is not a live-state mask or repair. No RAM, overlay, SMC,
stack, register, clock, sample-status or audio value is replaced after a cut.

Snapshots read backing RAM directly, avoiding side effects from reading PPU
ports. Comparisons include all32768 low backing bytes, every WRAM overlay,
all four maps, VRAM/CHR/protection/PPU state, fullAXYP/SP/PC, live stack, all query
scratch, complete resident SMC bytes and ordered CPU/overlay writes. ISR return
also preserves the individual pre-cut registers, scratch, SMC and live stack.
There are no audio/clock masks, stack repairs or hidden state grants.

## Source qualification results

- `caller`:64 native-bank1 A173→A176 complete call pairs across all eight real
  SMB2/Doki menu constructors, aliases119/120, canonical templates125/127 and two
  incoming flag cases. Every call reaches C2:B438 once, restores actual A-bank
  and CurrentBank129, and returns at the original PC/SP. There are128 observed
  resident returns, zero stale-target entries; minimumSP222. These use explicitly
  declared caller register/map/SP contexts on initialized families, rather than
  pretending to be a natural whole-stage replay.
- `--family`:all eight actual menu/cold constructions plus256 actual Main/NMI
  ordinary-controller continuations match the canonical oracle exactly,
  including5,651,895 paired Main-loop processor cycles. NMI also executes and its
  complete state is compared; its separate call's cycles are not added to this
  Main-loop count. No health, position, actor, ability
  or audio fields are seeded. This opening continuation matrix is not a full
  stage, and does not claim every modified bridge PC was reached by normal
  opening movement; the directed actual-caller and interrupt matrices cover them.
- `--vectors`:156 reached foreground instruction/SP points. For each119/120
  alias,78 actual IRQ and78 genuine busy-lag-NMI injections compare the original
  ISR/canonical foreground against the repaired ISR/foreground:312 injections
  total, minimumSP182. All six changed-operand instruction PCs are reached:
  E5E9/E5EE/E5F3 under both raw247/248 maps. Surrounding bridge and resident
  farcall transport instructions are covered as well.
- All156 busy-NMI comparisons advance actual source music identically. Sixteen
  pending A-map completions are recognized at the real split
  `STA CurrentBank; STA $5115` boundary: both original ISRs legitimately finish
  the pending mapping, then execute the same complete native caller. Nothing
  is repaired by the test. Entire ISR and caller states/writes agree.

The all-eight family identities are Mario, Luigi, Toad, Peach, Imajin, Lina,
Papa and Mama. Actual family source ownership/Ready is established through the
existing real menu/parser/constructor, not by writing variant or actor state.

## Genuine sample prefixes

Sample states are obtained before any caller-map fixture is installed. No4015,
NmiDisable, source clock, audio-manager or sample-bank values are synthesized.
Capture requires original active ownership, busy status, genuine NmiDisableFF,
clock phase and synchronized native bank shadows.

| Owner | Ordinary earning prefix | Retained state |
|---|---|---|
|120|Walk into the actual first Goomba; sourceMain185|HP15/reserve0,4015=31,fixed248,clock96,F840/LEN16/rate15 (257B)|
|119|Actual first healthy Flower, reserve pull and original lift request08|HP31/reserve2,4015=31,fixed247,clock224,FA80/LEN56/rate15 (897B)|

The119 prefix uses the **unchanged** qualified Imajin Flower/throw factory
`b4e4aa2ef067df6a961a3d7ec34bea51366c4a870edfcae8f8bd4bef0cad9dd0`.
Its complete natural prefix finishes620 logical Main/NMI iterations. Both sample
snapshots are taken in real Main atPC82B2/SP253. The later caller/interrupt
fixtures alter only the explicitly tested CPU call context, not the retained
genuine sample/audio/health state. Existing Flower APIs and observers are untouched.

The CPU peripheral model does not prove analog waveform playback, sample DMA
timing or a hardware deadline. Physical active-sample/return correlation and
full-stage survival remain root's native queue and delivery gate. No native or
installation claim is inferred from this source note.

## Reproduction and ownership

The only owned paths are this QA file and
`tools/audit/check_smb2_postbg_irq_1113.py`. The existing unfinished output root
retains zero files. Run each mode through the bounded wrapper:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/karnov-equipment-1113 --resume --max-files 1 --timeout 180 -- python -B tools/audit/check_smb2_postbg_irq_1113.py --vectors
```

Omit `--vectors` for the caller matrix, or use `--family`. All receipts go to
stdout only. CLI input accepts only exact3684, or exact12397 through its strict
inverse to3684; candidate and recipe pins are unchanged. Unknown inputs are
rejected. `--adapter` independently passed that exact known inverse path and
rejected an unknown mutated image, entirely in memory. GitHub releases stay
empty; no installation is performed here.

## Delivered-input CLI follow-up

After root reported direct12397 delivery, the actual Downloads bytes read back
as exact12397. A CLI-only extension in
`tools/audit/check_smb2_flag_handoff_1113.py::load_input` now authenticates the
unchanged post-BG composer SHA415ca42d… and strictly reverses known12397 to3684.
The existing Current inverse then produces exactf88, followed by the existing
Bub inverse to exact7ef. Digest is recomputed after each stage. No proposal,
recipe, controller pin, frozen Flower API/observer or grant is changed.

One bounded zero-output known-path check passed the actual Downloads read and
each of the four exact in-memory inputs independently:
`12397 → 3684 → f88 → 7ef`. Three unknown mutated12397 images were rejected,
changing header byte0, the granted-operand position976378 and final ROM byte
2097167 respectively. This is a loader/source check only; no Mesen was launched,
ROM installed or native receipt inferred. The only follow-up edits are the
existing loader and this appended QA section. Output remains zero files.
