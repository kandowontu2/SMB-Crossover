# OD: verified host-side turtle performance changes

The candidate is private MMC5 ROM
`89d8b2002ad0f471e1d4a782d52b681e5f641cba7843ba5f2eb019841b8cdf72`,
based directly on accepted OA
`06908a38ac7c658c40f6c064b82e71f84ecc0b5f4617ed8b9a17fba6ad677701`.
Its acceptance receipt is `build/verification/tmnt-render-od/proof.json`;
adoption is established only when that receipt and the independently rebuilt
checkpoint exist. This is progress on the full goal, not final roster or
every-powerup certification. Published ROMs remain preserved.

All candidate sources, rejected experiments, emulator captures and complete
lossless replay frames remain outside the workspace at
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-render-od`.
The accepted candidate's evidence is in `host-only-v2`.

## What changes

The four-cell turtle health display gets a dedicated ordered-store renderer.
It validates the existing cache's length, coordinates, attributes and OAM
capacity, while reading the current tile numbers. Unexpected records and
edge/capacity cases retain the original renderer.

Primary weapon descriptors are compiled into ordered sprite stores using the
actual original ROM records. An exact pose/pointer, bank, coordinate and
capacity admission keeps clipping and unusual states on the original path.
The dispatch's synthetic return target is consumed immediately; its original
caller return remains intact underneath. Neither artwork nor sprite priority
changes.

Six profiles that own their own items bypass unrelated legacy-inventory
support dispatch. The UI shortcut still runs the bounce lifecycle and the
existing inventory tick, including fresh input, stale HUD cleanup and refill
handling. Little Mac and the vehicles retain their dedicated HUD paths.
The turtle movement shortcut preserves the enclosing pre-step camera sample
and avoids a redundant Little Mac gate. Other profiles retain their handlers.

Only PRG banks59,86,89 change. All CHR, SRAM allocations and pre-existing
runtime addresses stay unchanged. The build-only farcall counter grows by4.

## Performance acceptance

The original600-update arranged native fixture and observer are unchanged.
Each phase contains120updates. Both versions retain live enemies in every
enemy-phase sample. All recorded gameplay-state fields match; differences in
controller sampling from NMI timing are retained in the comparison report.

| Dropped-draw NMIs /120updates | OA Leo/Don | OD Leo/Don |
| --- | --- | --- |
| Idle | 0/0 | 0/0 |
| Walking | 0/0 | 0/0 |
| Two Goombas | 0/0 | 0/0 |
| Primary attacks | 0/0 | 0/0 |
| Triple shots | 51/50 | 32/31 |

Triple-shot lag falls by19NMIs in each measured case, approximately37–38percent,
and remains an open defect. These are two arranged components, not a constant
60Hz or whole-campaign performance claim. Ordinary walking and enemy-phase
game-loop CPU work falls by1281–1293cycles per update in these components.

The health call saves287–288cycles. The own-inventory support path saves
460–472cycles, while other paths add34–42cycles. The complete UI comparison
saves492–964cycles for admitted profiles and adds37–71cycles otherwise.
The movement comparison saves41cycles for turtles and adds56cycles to its
retained legacy entry. Primary admitted-record comparisons range from3extra
cycles for an empty record to229cycles saved. Nested savings are not summed.

## Verification and limits

- Actual linked CPU differentials pass7428health,13290primary,1752inventory,
  2560UI and2560complete movement/camera cases. They compare registers,
  meaningful flags, SP, application RAM outside discarded stack/SMC/safecall
  scratch, ordered sprite/hardware stores and final bank mappings.
- The actual linked MMC5 scroll IRQ interrupts every instruction boundary of
  all62weapon entries in two OAM configurations:10418cases, including460PHA/RTS
  boundaries. Registers, live stack bytes, partial synthetic returns and the
  completed drawing match. This CPU test is separate from timed native PPU/NMI
  coverage.
- Source equipment13708cases and456non-turtle shared-hook cases pass.
  Thirty-two native components cover equipment, primary attacks, bosses and
  ammunition across four turtles and both difficulty modes. Their inventory,
  RNG and target arrangements are explicit; natural delivery of every reward
  is not established by them.
- Eight fresh cold-menu1-1discoveries and independent exact-input/trace replays
  reach movable1-2with zero deaths. Easy/Hard frame counts: Leo4551/4703,
  Raph5172/5223, Mike4732/4851, Don4666/4838. All37136replay PNGs are retained.
  Automated body CHR and scanline31scroll checks pass. Root inspected all eight
  24-frame overview sheets and found no new obvious displaced blocks, green
  tiles or missing body parts in those samples. This is sampled human review.
- Actual equipment DMA, geometry and source colored-pixel comparisons pass;
  transient scanline overload still occurs. All37cold entries and the existing
  beam/charge/Water Shield/isolation/native-audio fixtures are required by the
  finalizer. These entry checks are not37complete1-1campaigns.
- Ordinary14-character MMC3/MMC5 outputs retain their published hashes. The
  independent full source-ZIP rebuild must reproduce the candidate before
  adoption. Workspace usage remains below30,000,000,000bytes; lossless evidence
  is retained externally.

## Experiments kept outside the accepted change

OC's original TMNT soundtrack remains functionally verified but unaccepted.
Duration shortcuts preserve53024shared-entry cases and all16songs'549602source
APU requests, but still add a dropped draw during primary attacks. A body
renderer passes13890CPU cases yet does not solve that performance regression.
Their native duration/body code, fixed-bank hooks and new audio state do not
enter this OA-based candidate. Native weapon sound bindings remain open.

Failed preparation/guard attempts, the rejected body routing and native-music
performance comparisons remain in their original external directories. They
are not erased or described as accepted. The broader roster/item matrix,
source/audio work, heavy projectile lag/flicker and full MMC3 port remain open
under `final-verification-plan-2026-10-23.md`.
