# SMB2/Doki normal foreground lifetime — November 13

The private `dadb` pipe-priority fix permits native side-pipe entry, but preserves
priority `$20` into ordinary underground engine8 play. Root observed this on the
actual Mario route after21 grounded next-area updates. The separately pinned
`2448` successor clears the source's normal attribute when its existing normal
World caller sees sourceYPage0/nativeY>=64. It preserves above-HUD and offscreen
behavior, and all native pipe/end handoffs bypass this routine.

This is a source/native integration fix for all eight raw25 variants: SMB2 Mario,
Luigi, Toad, Peach, Imajin, Lina, Papa and Mama. It changes no movement constants,
items, helpers, state allocation, CHR, palette data or renderer code. All existing
`dadb` APIs and negative lifetime receipts remain frozen. No installation or
release publication is performed by this recipe.

## Exact source and resource

- Strict parent SHA256:
  `dadb9d80702148fe40b1a64d1cfff7ff2df65248b9c72e7c167d32e3589670be`.
- Strict successor SHA256:
  `2448c558298d9f1b6d178dcdc00e90db90ae7d85b95e37c0101130701aab261a`.
- Reservation: `docs/qa/allocations/smb2-normal-foreground-1113.json`.
- Only physicalPRG118/CPU`B9AE..BA7C`, file973246,207B may change. Its exact
  parent SHA256 is
  `11a67f3e1bee7cc85fd136a0f9ff89398e4d2fe4a4b25c1fe3aebcf846a00297`.
- New owning source `tools/reference/smb2_pipe_foreground_1113.s` SHA256
  `9805940a149bd04dbb10057b677ba9231f85136ad5d6ed449e51a16eb8f719d3`.
  Its complete207B body replaces205B+2EA. Exactly150 ROM bytes differ. Following
  MainPickup`BA7D`, all `dadb` graphics/palette/helper/body bytes and every byte
  outside this footprint remain exact.

Funding removes two3B HeadPage stores after the live head query, plus2EA. The
actual89B MainPlayer source reproduces byte-for-byte. Its sole same-bank World
call at973033 immediately executes `PLA; STA $5C7E` before MainBox. The removed
coin stores are never read during that interval. The early head query remains
live, and the later body-contact reader consumes the restored pre-motor Y.

The source's known-zero page load supplies attribute0. Temporary X samples Y;
the original arithmetic restores A/flags, and coin/flag paths preserve the real
caller ABI. Moved private helper/coin labels have no external own-bank pointer
or farcall readers. Other raw B9AE transfers at214760/524036 belong to physical
banks26/63 and remain unchanged.

Current native policy is independently bound to the actual28B fragment at8582:
`a5bdc9409016a50fc905f010c907f00cc9049008ad870529df8d8705`.
It skips Y<64, engine5/7 and engine<4 before clearing bit20. Source MainPlayer
bypasses that native routine. This change implements the needed normal-engine8
visible subset, retaining the source's palette/normal-attribute0 contract. It is
not a claim of replacing the entire native policy in every engine state.

SourceYPage1/FF retain their prior priority; actual source export maps them to
nativeHigh2/0 respectively. On returning to sourcePage0/Y>=64, the next eligible
source World update clears the latch. This source motor can update at30Hz; it is
not a promise of clearing on a skipped source update. Above-HUD Y<64 retains the
existing latch. No new persistent flag is used.

## Bounded source qualification

All fixtures below are directed CPU fixtures in memory. They do not stand in for
natural physical routes or native item collection.

- `--finite`:1369 actual World transactions:66 Y/HUD/source-page boundary cases,
  9 native coin points,12 head transactions,2 native down-pipe entries and1280
  all-eight flag boundary cases, including192 true admissions. Returned AXYP
  and all scratch/SMC/RAM agree except intended attribute and the explicitly dead
  direct-callee cache.1133 leaf cases differ in that dead cache output; there is
  no claim that a standalone World caller may consume it.
- `--caller`:320 all-eight actual MainPlayer/motor/World/MainBox continuations;
  HeadPage equals the actual saved pre-motor Y. Full returned AXYP/SP and all
  nondead RAM agree except the intended attribute.32 explicitly synthetic
  admitted body-contact callbacks then consume that restored cache and produce
  matching original standing position. Cache, query scratch, SMC and audio are
  not masked. Only stack bytes below the returned SP are excluded.
- `--cache`:40 complete actual MainPlayer intervals monitored every CPU read
  of HeadPage after consumption and before the real caller reset: zero reads.
- `--references`: whole89B owning caller reproduced, all three direct cache
  readers classified, moved internal references closed, protected bytes exact.
- `--render`:704 World-to-actual-native-OAM pose/color/CHR pairs, all eight real
  constructors, sizes/faces/holding states and all11 animations. Native class map
  is the actual `0,3,2,1,0,1,2,3`; post-Ensure inputs are retained.32 HUD/offscreen
  cases retain priority. Normal OAM equals the original source foreground0
  contract. The offscreen cases use the real source export.
- `--handoffs`:510 all-non25 actual boundary pairs with whole RAM and no masks;
  eight actual menu-preview OAM/VRAM/CHR pairs; ten native non8/non11 handoffs
  preserve attribute32. The source handoff's real target is native129/A021;
  the distinct outer owner boundary targets A14D. Uninitialized foreign native
  physics is not executed.
- `--vectors`:134 reached World instruction/SP points;134 actual IRQ and134
  busy-lag-NMI paired cuts, minimumSP170. Both original and successor ISRs advance
  real music identically on134 cuts. Every actual ISR cache read was monitored:
  none. No audio, clock, cache, SMC, scratch or live-stack masking. Genuine busy
  input prefix reaches Main185/X301/Y176/HP15/audioBank120.
- `--faults`:213 corrupt parent and213 corrupt successor images rejected,
  covering every207B envelope byte plus protected boundaries/other bytes. The
  exact99B Ready85 source export is reproduced, with actual sourcePage0/1/FF
  becoming nativeHigh1/2/0 and attributes0/32/32.

The first IRQ observer left its `inISR` marker set after RTI and counted its own
subsequent RAM snapshots; its final assertion failed. The corrected observer
clears on actual RTI return, then the complete134+134 run above passed. Earlier
handoff observer attempts incorrectly reused the outer boundary's target and
omitted the source handoff's initial A-save; the exact28B source literal corrected
those test bindings. None of these observer corrections changed ROM/Lua bytes.

## Controller and native scope

`compose_smb2_pipe_foreground_1113.proposal(exact_dadb)` returns `(image,metadata)`;
`inverse(exact_2448)` returns exact `dadb`, independently of Downloads. Existing
flag→mirror→priority APIs reconstruct that private parent from exact7ef. CLI
input normalization explicitly accepts known publicf88 through Bub's exact
inverse; strict proposal/inverse pins are not broadened.
The CLI adapter also explicitly accepts exact merged3684 through root's frozen
`compose_smb2_foreground_current_1113.inverse` to f88, then Bub inverse to7ef.
Its exact module SHA is authenticated. `--normalization` tests this complete
known path in memory and rejects an unknown mutated image. It does not broaden
any strict source recipe, controller, proposal or inverse API.

`replay_smb2_pipe_foreground_1113.controller(image,variant)` preserves the ordinary
full1-1 inputs and25-grounded-underground1-2 assertion. Imajin4 Lua SHA256:
`2a5af0d1eceaf6dac4f57025fe35c981f9eac85073703cac130c5895d0538b82`.
The optional `visual_controller` retains root's two passive in-memory image tags
and adds normal-grounded attribute0, SHA256:
`d1086dbd0ac0d110cc6bd9869e331bb4498e32ee3a163892999d291cc8bc894b`.
All are controller/read-only observers; no runtime writes or helpers.

Root independently ran actual private2448 Mario full1-1 plus25 living grounded
1-2 updates:4484 physical/3597 Main, HP15/lives2. Root's stronger visual observer
also asserts side-pipe priority20, Lua
`0792b198c4327d33f80474412b68fd338cd19a7d288c3acfe09b455ac20c4968`, receipt
`8704b71f04b3df4d420516396b8167c013eead88ffb82d66ca4225cc2bab3132`.
Reviewed memory images: pipe2645B/SHA prefix`ff20a4d4` at3987/attribute32;
underground2010B/SHA
`d2cea1da19b66b74420e21a2f96b6a3ac24d31881dcfd4471f334b3d8158ce29`
at4481/next21/attribute0. No image files were produced.

Root subsequently reported all-eight ordinary physical full-stage passes on
the explicitly merged-f88 successor
`3684f3d2a418a484befd80fca351d0dc5f9b472f6f067a0a7894994ea343679d`.
Mario/Luigi/Toad/Peach/Imajin/Lina/Papa/Mama physical/Main counts respectively:
4484/3597,4744/3820,4629/3723,4680/3723,4558/3555,4945/3912,4926/3849,
4969/3925. Each reached25 living grounded1-2 updates at40/176 with both lives;
idle48/48,zero skips/capture files. Those are root-owned native proofs, separate
from this checker's directed source fixtures. Root's delivery report remains the
authority for any later installation/Downloads verification.

Healthy first Flower remains documented adaptation; all-eight
natural injured Mushroom proof is separate. Remaining earned flower attacks,
Star/1UP and full per-variant completion are not inferred from this fix.

## Reproduction and storage

For each checker mode, use the same unfinished zero-output task root:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/karnov-equipment-1113 --resume --max-files 1 --timeout 180 -- python -B tools/audit/check_smb2_pipe_foreground_1113.py --finite
```

Replace `--finite` with `--caller`, `--cache`, `--references`, `--render`,
`--handoffs`, `--vectors`, `--faults` or `--normalization`. Composer and pure replay CLI use the same
wrapper. No ROM copies, fixtures, captures or receipts are written. Active
output remains zero files; root retains the sole Mesen queue. GitHub releases
remain empty and no IPS assets are created.
