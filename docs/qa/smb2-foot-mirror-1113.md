# Shared feet mirror synchronization — November 13

Private source work only. Public Downloads remains exact7ef. Root owns native
tests, installation and the single Mesen queue. No ROM, receipt, capture,
compiler or extracted-source output was written by this helper. GitHub releases
remain empty. This change adds no RAM, CHR, motor, helper or code allocation.

## Reproduced cause

Private flag0e9e fixes actual shaft contact and reaches native flag/castle/next
entrance, but the first normal engine7 update halts. Native receipt
`0e131a578a09dd40b80d5f625eea5856cf1e40cc4efd81bc46adc9416bbcd75a`
shows actual mapped native bank48/B144 KIL02. The boundary observer receipt
`9052a1e7f269d1051fbea4732722171a23867fa3ba103880756a98452254ca4c`
shows fixed126 DoFootCheck9C0A calling E46A with A=playerY176 and stale SMC
targetB101 (S2Head). Resident0169 therefore maps176/data48 before jumpingB101.
An unbroken actual-menu/controller/Main/NMI CPU replay independently reaches
the same map/target, stopping at the first BRK in dataB101. A synthetic initial
engine7 leaf call returned normally; that fixture did not reproduce the bug.

The source `check_sonic_shared_feet_1110.py` moved HEAD18→15B and feetE46D→E46A,
then globally retargeted the old foot operands. It changed canonical127 only.
The active SMB2 audio mirror120 still had the old18B head, whose E46A was the
tail JMP FarCallCommon. Thus the correct new caller entered an old head tail.
The source/CPU/native evidence agrees; no S2 motor or GameRoutines constant
change is needed.

## Exact existing ownership and APIs

Root's conditional grant is
`docs/qa/allocations/shared-feet-mirror-1113.json`. It permits exactly the same
63B E45B..E499 in mirrors119/120/125, with these hashes:

- Old complete body: c62b3fc0131afeebce146b5aac0983f87f3a6666bd0e86348fc2c6e1384d8c36.
- New canonical source body:2e785eb4539e8c3d9acba6c691d382d1eb864677be76c93082e9a1115013eaee.
- Existing source `sonic_shared_feet_1110.s`:106c68d674b24c52ce683339c0e95b9386b921eb774171970feeff13040d5dd3.

The in-memory assembler reproduces canonical127 byte-exact as HEAD15/FOOT45/
SIDE3. All128PRG banks are censused: old copies119/120/125, new copy127.
The existing SMB2 sample-bank table actually selects119/120. The retained
`build/thomas-natural-host-1031-v6/source/dmc-clones.s` (SHA7837a7c2ee96a54996cf08e9ed984ebc355e9a7438bb1314f9f740a6b13a2556)
copies final127's first4416B into both before sample overlays. This code is
offset1115..1177, wholly within that source-owned prefix. CV3's deterministic
`prepare_cv3_dmc_mirror.py` similarly clones127 into125 outside sample/manager
intervals starting4416 or later. No sample or manager byte changes.

There is other preexisting mirror debt:119/120 have109 different bytes in the
first4416B versus127, and125 has102. The granted63B span contains60deltas.
The other49/42bytes remain exact and are not claimed synchronized.

`compose_smb2_foot_mirror_1113.proposal/inverse` retain the explicit120-only
history. Public7ef→7164d5d3aa07d4090f474128b4193706eb80dd41cb140d59ac2263874f4ed6a2;
flag0e9e→5f27ee8dc002b08ecb09e2a20f6b214911da0e691921aec60afe706914b38651.

Separate `all_mirrors_proposal/inverse` synchronize all three with strict
parent hashes and exact forward/inverse closure:

| Parent | All-mirror candidate |
|---|---|
|7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc|690482ef99abb5cc9c4e1cc1bcfecc81fce391722a60ff4bdb3c0f7aa1b87ac3|
|0e9e9254927236bcc651e79da36a77924eea5481421858a05f869b15298412e1|2c62e1a0de1b732cfa57af59e71c0775396e067bf04aa101e78f644c3e4c9c4b|

Only spans975979/63,984171/63 and1025131/63 change (180actual byte deltas).
All adjacent bytes, canonical127, sample data and private owner payloads are
retained. OldfootE46D has no remaining word or literal farcall reference.
OldsideE496 has only unrelated words358452/693168, no transfers or literal
farcall producer. Newfoot has exactly native1269C0A/9C13 direct callers;
newsideE497 has native126 direct callers. HeadE45B remains at its old entry.

## Source qualification

Run `check_smb2_foot_mirror_1113.py` modes (default references, `--matrix`,
`--foreign`, `--vectors`) through the existing zero-output bounded root:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/karnov-equipment-1113 --resume --max-files 1 --timeout 180 -- python -B tools/audit/check_smb2_foot_mirror_1113.py --vectors
```

- Matrix:1500 canonical127/native-feet comparisons across every raw owner
  using the generic path,252 SMB2 head/feet/side comparisons and84 actual
  DoFootCheck continuation comparisons. All three E mappings are retained;
  AXYP/live stack/native RAM/overlay/SMC/A/C maps match canonical127. Synthetic
  getter cells/coordinates are explicitly directed fixtures. Minimum SP198.
- Actual current menu/cold LINK, SOPHIAIII, FFFIGHTER, MRGIMMICK, DONKEYKONG and
  SONIC:252 private feet comparisons against canonical127 plus18 actual
  parent/candidate Main/NMI opening-input comparisons. Minimum SP201.
- Vectors:81 reached changed-worker points,81 realIRQ+81 realbusy-lagNMI,
  minimum SP174. The source sample is genuinely started by the ordinary
  first-Goomba injury (Main178, player297/176, activebank120/status4015=31).
  Every actual original/candidate ISR advances and restores identically;
  63busyNMIs have real paired music progress. No audio/clock field is masked.
  Entire native RAM, overlays, SMC, AXYP/live stack/maps and the subsequent
  new getter continuation match. Explicit code-mirror mapping fixtures do
  not establish sample waveform, DMC fetch stealing or native deadlines.

## Native status and remaining entrance seam

`replay_smb2_foot_mirror_1113.controller(2c62,4)` changes only the expected ROM
label in frozen09c0. New Lua is
`a6e3fefaadbec7398f11b60fc10475414db57fbf534047e26d5670444fea9276`.
It retains all ordinary decisions and the complete exit assertions.

Root's actual private native repeat confirms the halt is fixed:7000Main return
through7819physical frames. It remains negative at engine7/X239/Y176 rather
than reaching the required underground endpoint. Receipt
`6006649b766039b0060ec4c1c16c844407cce06e83f10d8cd96433a19dce860d`.
The next independent native diagnostic proves S2Graphics clears the real
pipe-priority latch20→0 every draw. This is a separate source-owned rendering
fix;2c62/a6e3 remain frozen and are not installed. See root's native flag QA.

The old USA `src/smb2_roster_render.s` is not the current Doki compilation.
A tentative19B table-compaction funding idea from that stale source was
withdrawn before any patch/grant. Actual B7EF..B82D already has no such table;
the next request must reproduce the exact Ready85 member and current bytes.
No additional priority resource is granted by the mirror allocation.

## Later CLI input adapter

Root subsequently delivered tested Bub f88. `check_smb2_flag_handoff_1113.load_input`
accepts that one exact known hash and authenticates
`bub_native_noops_1113.py` SHA6770cb6c8c9a0fe73eebd8c2c9b4c112ee55dc81def05c9aaf280b5a14e718e6,
then its `combined_reverse` reconstructs exact7ef in memory. CLI entry points
use this typed adapter; all strict proposal/inverse/controller PINs and native
Lua remain unchanged. A zero-output current-input roundtrip again gives2c62,
Lua a6e3 and injured-Mushroom Lua36e5 exactly. No foreign ROM is silently rebased.
