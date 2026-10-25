# OC: original TMNT audio integration, held for performance work

**This is staged work, not an accepted replacement or a completed goal.** Live
game source remains private OA, ROM
`06908a38ac7c658c40f6c064b82e71f84ecc0b5f4617ed8b9a17fba6ad677701`.
Public ROMs remain preserved. The current staged candidate is v7,
`dde53bc1bdb02489230dcd561b96496d1551cdc2b0b684c98cede6d3ca5c3fff`.

Evidence and staged source are retained outside the workspace at
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-native-audio-oc`.
The original source and the independent original-NSF observations are pinned
in [the OB preparation record](tmnt-native-audio-preparation-2026-10-24.md).

## Implemented in the stage

The original TMNT music engine and data use PRG banks7B/7C. Bank7C maps atC000;
fixed bridges restore the C7D adapter before returning, then restore the
expanded-audio caller. The source's 129-byte, rate15 drum occupies fixed
E8C0..E940. Its completed output holds DAC44, matching the source, rather than
taking ordinary effect cleanup. Existing world effects retain the shared
MMC5 pulse/noise mixer. Source area songs are2,5,3,10,8,1,11; events are
15,13,12,12,13,12,6. This adapts the soundtrack to SMB's area/event categories.

Pause and silence stop advancement and active drums. Resuming restores a
completed drum's held level. Leaving for Mario, another guest or the title
cuts DMA and clears its final buffered output on the following audio update.
Mario then owns its original DAC counter; Samus and the title hold zero.
A new live sample owner takes precedence over delayed cleanup.

The delayed drain byte aliases the previously unused seventh byte of the
existing16-byte `BassAudioSavedApu` reserve. `AudioInit` explicitly clears it;
it is outside the history another guest can reuse. No SRAM allocation grows.
The relocated Samus adapter and source drum preparation remain as described
in OB; no part of another character's drum is truncated.

Version5 maps all180 original zero-page operands into the already reserved
fourteen-byte decoder slab, DE..EB. `InitializeMemory` already protects that
slab during interrupted level/life resets. The compressed decoder is inactive
for native character19, and a character change reinitializes it. Immediate
constants and raw data are untouched; per-instruction assertions preserve
all original widths, branches and ROM pointer locations. This removes392
save/restore cycles per ordinary adapter call without borrowing foreground
zero page. Measured inclusive adapter work falls20,024,546→15,793,227cycles
over the same10,827calls, approximately21.1percent. This percentage covers the
adapter fixture, not total game performance.

Version7 adds exact-ID admissions for TMNT graphics, special drawing and
weapon/HUD drawing before unrelated character dispatchers. Other identities
retain their original handlers. The two18-byte call spans and one3-byte call
retain their size; all prior runtime labels stay fixed. The compile-time
`_FARCALL_COUNT` increases by3. These helpers also remain inside the reclaimed
fixed padding. Changed PRG banks are1,4,38,123,124,125,127; all CHR is unchanged.

## Completed evidence and its boundaries

- Version5's actual linked engine passes all16songs for192,016calls,
  549,602ordered source APU requests and549,602writer ABI returns. Allowed
  RAM/mapper writes, images, DMC parameters and exact drum bytes are checked.
  Version7's independent repeat is retained under its own candidate directory.
- Version5's native fixture passes14area/event cases and three explicitly
  arranged active-drum transitions. It compares173,232source registers,
  150,505hardware registers and10,827interrupted-state snapshots, including
  every zero-page byte outside the owned decoder slab. It observes1,172active
  DMC frames,8,973held-DAC44 frames and259nested IRQs. Version7 repeats this
  fixture from an AllOnes power-on configuration.
- Version7 passes3,024real linked foreground-gate differentials: all21internal
  IDs, four turtle variants, three OAM offsets and four flag states. Final
  A/X/Y/meaningful flags/SP, application RAM outside discarded stack/SMC and
  safecall scratch, ordered OAM/non-banking hardware writes and final banks
  match. The direct-entry native savings are113,185and207cycles; the two
  enclosing bank trips are also avoided in gameplay.
- Version7's compatibility check passes8,820DMC cases,1,152non-TMNT audio
  dispatch cases,48initialization cases,2,856ordinary global-gate cases and
  812transition cases. It also pins changed bytes to their owned call/padding
  ranges and preserves53,682prior qualified symbols, except the explicitly
  relocated Samus-private labels and the compile-time counter above.
- Version3 passes the existing Samus beam, Mega Man charge, Bass Water Shield
  DMA/cleanup and Bill/Link/Simon isolation fixtures. All4,096cold Samus
  source-state/hardware CSV rows are byte-identical to OB's original baseline.
  The Gradius native fixture passes12cases and133,120source-register checks.
  Version3 also passes16,008Samus CPU cases,13,708equipment CPU cases and
  456non-TMNT gameplay-hook cases. These results bind to v3, not later hashes.
- Version3 passes all eight cold-menu Easy/Hard1-1discoveries and independent
  byte-identical input/trace replays, with zero deaths and movable1-2. Frame
  counts are Leo4775/4892, Raph4643/4881, Mike5224/4771 and Don4827/4852.
  Every replay PNG is retained. Automated CHR/scroll checks pass. Root viewed
  all eight24-frame overview sheets: no new obvious misplaced blocks, green
  tiles or missing body parts were found in those samples. This is sampled
  human inspection, not exhaustive frame review or v7 campaign certification.
- Version3's ordinary14-character MMC3/MMC5 outputs match the published
  ordinary hashes. Version7's full37identity entry/interrupt matrix and final
  source-only roundtrip are recorded separately when complete.

## Acceptance failure: combat lag

The native music is functionally correct in the tested components, but its
larger per-frame CPU peaks expose additional dropped draws in ordinary combat.
The optimization candidates are compared with the exact accepted OA profile,
using the unchanged600-update native fixture and observer. Each phase has120
updates. Both versions retain120samples with live native enemies. All recorded
gameplay-state fields match; controller-sampling differences are retained in
the reports rather than called byte-identical controls. Cycle spans exclude
NMI/IRQ bodies and include actual DMC DMA stalls; nested spans are not summed.

| Lag NMIs per120updates | OA Leo/Don | v3 Leo/Don | v5 Leo/Don | v7 Leo/Don |
| --- | --- | --- | --- | --- |
| Idle | 0/0 | 0/0 | 0/0 | 0/0 |
| Walk | 0/0 | 0/0 | 0/0 | 0/0 |
| Two live Goombas | 0/0 | 4/4 | 3/3 | 3/2 |
| Primary attacks | 0/0 | 13/10 | 12/6 | 7/5 |
| Triple shots | 51/50 | 59/60 | 55/56 | 49/47 |

Triple-shot stress improves beyond OA after the dispatch changes. The two
ordinary combat phases still regress, so every native-music performance
report explicitly fails its acceptance gate. Total video-frame counts alone
must not hide those dropped draws. **Do not promote v7 or describe all lag as
fixed.** Further rendering/host CPU work is required before final route/item
certification and adoption. Original native weapon/effect command bindings,
the full MMC3 port and the complete37identity/every-item matrix also remain
open.

## Retained negative evidence

Earlier fixtures incorrectly required DAC44 during deliberate silence and
DAC0 during Mario's own original DAC modulation. Corrected assertions retain
the native hold check in audible phases and observe Mario's actual original
`StrWave` store. The failed runs are kept. Version4's obsolete export and
version6's incorrect expected physical bank prevented preparation receipts;
their logs/stages remain. Version7's first symbol guard treated the assembler's
farcall counter as an immutable runtime address; the corrected guard requires
its exact+3delta while continuing to pin actual code and runtime labels.
The three performance failures above are genuine measured regressions and
remain unresolved, rather than being explained away as fixture errors.
