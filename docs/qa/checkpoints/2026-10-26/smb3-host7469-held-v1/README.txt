Private authentic SMB3 host music7469 — HELD, NOT INSTALLED

Production remains3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287.
Private candidate7469d9f62af3161c896b844546ead66002bb425ba8b5143692b1c2ae1d9f1219.
No ROM/NSF/DMC/sample/settings/raw capture payload is included here.

Source adapter checks pass (see source-report), and one genuine cold-menu
SMB3Mario Easy opening ran1200PPU with no state/selection/mode writes.
Original native runner verdict remains FALSE. Call2 real6502 RMW bus writes
included old then new values; semantic CPU oracle omitted the old-value writes.
The separately versioned offline model adds ORIGINAL bus writes, never drops
native events.768calls/4704ordered logicalAPU/RAM/state/AXYP/SP now match,
including7945real RMW dummy writes. Both original FALSE and firstdifference
are included. No native retry was used to obtain this corrected comparison.

Actual source26DMC starts/11717reads/24completefetches; residentE70 exercised,
E97 not exercised.1013complete256-byte DMA epochs/679scoped enables pass all
original hardware checks. SharedSFX capture/mixer remains present; source
logical-store fidelity is separate from physical common-mixer order/waveform.
Full actualPPU was retained externally. The sheet contains6full frames with
contrasting panel gaps; no obvious scenery corruption in these6 samples,
not a claim every frame or all graphic behavior is clean.

A separately approved baseline3b replay used the exact1199poll input stream.
Baseline hardware/CHR/motion pass and settings/environment stayed exact.
Candidate599draws vs697baseline;1125completedMain vs1163baseline.
Candidate179lagNMI entries vs81baseline:98extra lag NMIs exactly match the
98lost draws.688cumulative prefixes show draw deficits. First deficitPPU513;
first Main-commit deficitPPU516.768same opening audio calls cost2,988,252 vs
1,996,853 CPU elapsed cycles: +991,399. Actual per-call audio mean3890.953
vs2600.069; peaks9841vs8261. Sourceoriginal mean645.761; translated native
source elapsed1736.874 includes real DMC/IRQ costs. This split is not yet a
pure translation profile. No renderer compensation or weakened cadence gate.

This integration is HELD for performance. No production/source default was
changed. Durable mirror production hook remains unintegrated/private.
Next source-only work profiles original-core vs reader/bank/image/adapter
costs before choosing a faithful optimization. No sample/voice/tick cuts.

Review map: source/implementation.patch is the actual9-file source delta
(external binary payload is referenced, not embedded). source/changed-source-
files.json names exact old/new hashes. native/original-runner-FALSE.json and
original-first-difference.json preserve first failure. corrected-offline-
original-bus-proof.json is distinct. paired-cost-and-deficit.json and
per-PPU-candidate-minus-baseline.csv retain timing rejection. review/ has
one sheet only. owned-tools.json lists source tools ROOT should review/stage.
external-evidence-bindings.json pins large/private originals and source trees.

Reproduction limit: this Git checkpoint does not contain copyrighted raw
NSF/DMC/ROM assets, complete original generated source trees, emulator,
settings or lossless PPU captures. Full native/original verification requires
those exact external files. It is not a standalone public binary build kit.
