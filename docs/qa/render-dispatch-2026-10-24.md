# Shallow render routing candidate OV

Private candidate SHA-256:
`4dcc0e87dd1c7dcbd6c11c92c5dc9d269616769e1cb7148b820cc5df2c463972`.
Parent OJ is `88906bd9b21a65c2a09128730599a4683ff6123a655386c1b55d3e0ec1ef3b8a`.
Adoption requires a separate exact source-only rebuild receipt; this document
alone does not adopt the candidate or certify the full roster/item goal.

## Change and rationale

Native direct captures confirm actual skipped-publication screen catch-up,
separate from the decoder screenshot timing defect described in
`direct-frame-capture-2026-10-24.md`. Repeated visits to unrelated character
banks add work before the existing graphics owner can run.

OV routes two existing calls directly to the first applicable existing owner.
Roll's alternate override retains its priority; Mac and turtle admissions
preserve their original input registers/flags; unsupported IDs use the unchanged
full chain. All body/drawing leaves remain intact. There are no new RAM, CHR,
audio, movement, collision, level or weapon changes.

The byte-confinement check finds 458 changed bytes: the two existing 18-byte call
spans in banks 1/4, plus a new 452-byte segment appended in bank 66. Every prior
named qualified address remains exact except the compile-time farcall count
(+18). Header and all CHR bytes match OJ.

## Component and native evidence

- 3,900 actual assembled call/router cases require identical first-owner
  A/X/Y/full-P admission and return registers/SP, no application writes, and
  identical final bank mappings. Render bodies are explicitly opaque in this
  component. The actual 18-byte call bytes execute in a declared synthetic RAM
  caller; full native loops and their real callers are checked separately.
- 7,842 actual linked IRQ injections cover every executed router/return
  instruction boundary in 96 profiles. Registers, meaningful flags, PC, live
  stack, ordered IRQ stores and completed admissions/returns match the old path.
- Matched native components run 600 updates each, with 120 updates per phase.
  Sophia/Chip retain every recorded input, position, state, pose, shot and enemy
  field. No scene adds lag. Turtle components retain byte-identical gameplay,
  including the input field, with no added lag.
- All 37 cold actual-menu entries pass ordinary movement/alternate/interrupt
  ownership checks. These are entry checks, not 37 campaign clears.
- Seven existing source-audio regressions pass, including all 4,096 cold Samus
  native audio rows and 12 nested IRQs. The existing 28 MM/Bass injury scenes
  also pass their unchanged movement and immunity assertions.

Missed-draw NMIs per 120 native updates, OJ → OV:

| Scene | Sophia | Chip |
| --- | ---: | ---: |
| Idle | 30 → 11 | 0 → 0 |
| Walking | 17 → 4 | 0 → 0 |
| Live enemies | 73 → 64 | 3 → 0 |
| Primary attack | 120 → 120 | 4 → 0 |
| Jumping | 102 → 91 | 7 → 1 |

Turtle ordinary loops save 162 CPU cycles per update in these components.
The first poll-indexed comparison had one different Donatello controller sample
at update500. The strong adoption gate rejected it before any live source copy.
Fresh paired PB components hold the same input through each completed update;
every recorded input/gameplay byte matches. Heavy secondary lag is27→26 for
Leonardo and25→23 for Donatello per120updates; it still drops draws.
More completed drawing can increase a
whole-loop average, as in Sophia idle; isolated routing savings do not imply
every complete loop is shorter. This is not constant 60 Hz or physical-console
compatibility evidence.

## Route and capture boundary

Fresh SMB3 Mario/Luigi Easy/Hard discovery and independent exact-input/trace
replays pass in 3,566/3,676/3,582/3,674 frames, with zero deaths and movable 1-2.
All four retain the original logical world/camera, actual visible scanline-31
scroll and body-CHR bounds. Their old decoder captures establish file retention;
direct physical-frame captures are a separate gate.

The controller correction jumps over the flagpole's ordinary solid base. It
does not alter the level or add a flagpole engine fix. Ryu Easy also has an exact
replay, but its raw strict review is rejected pending positive investigation of
a large trace step. Ryu Hard and both Sypha attempts remain failed. The original
mixed discovery/replay aggregates remain false and are retained.

Two fresh Sophia discoveries pass at 5,334/5,402 frames. Their native guarded
replays and direct captures pass, with exact independent inputs/trace, no invalid
execution/SMC writes and strict motion/CHR/scroll checks. Source-native empty-floor
B behavior explains the slow earlier CV3/Ryu controllers: repeatedly attacking
stops their walking. A corrected controller also gives Sypha Hard a 5,825-frame
strict independent direct replay; Ryu/Alucard Hard discoveries at6,146/5,617 still
need independent verification. Grant Hard still fails. These do not erase earlier
negative attempts. OV has seven strict pairs and four direct physical captures.
Do not add OJ's 53 independently verified pairs to OV's count:
they have different ROM hashes.

Selected review exposed a separate existing SMB3 shrink defect: glyph-like body
tiles at actual PPU955. A read-only exact-prefix replay of parent OJ independently
reproduces the same bad image. This is explicitly an open pre-existing repair,
not concealed by passing entry, logical CHR-bank or narrow router checks. The
authenticated source's shrink bank phase depends on the reversed growth index;
the port currently derives it from the unreversed timer.

Earlier render candidate versions are retained. Version 1's initial preparation
assertion assumed the wrong player-code bank; its first CPU fixture also stopped
at an intermediate gate for unrelated identities and is invalid. The corrected
fixture then exposed a real turtle admission mismatch in versions 1/2. Version
3 uses the original direct turtle owner, preserving incoming A/P, and passes.

## Open work

The final every-identity and every-powerup matrix, actual physical-frame review,
remaining graphics/behavior/music fidelity, heavy-attack and ordinary gameplay
lag, complete oversized MMC3 integration and final releases remain unfinished.
Published ROMs and the player guide are preserved. External evidence is under
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-render-dispatch-ov/`.
