# Parodius rendering repair — private checkpoint NQ

Candidate: `build/verification/parodius-render-nq/candidate-v3.nes`, SHA256
`c5f15fcd1bca72ca6a0787782f010342dbea99df8391c57a305be1addca8bf2e`.
Parent: immutable checkpoint `chr-publication-np`. This remains a private MMC5
development build. No published ROM was replaced and the full goal is unfinished.

## Changes and limits

The original layer splitting made Pentarou's normal pose164 use8 overlapping
sprites before firing. Its native dark blue had also been quantized to a
separate black plane. TwinBee's white layer similarly spent extra sprites.
Both now use the native white/blue/dark-blue primary palette. Small red/yellow
details use existing world colors16/27 instead of source06/28. This remaining
quantization is explicit; no enemy palette is changed.

All131 body poses are regridded from their actual opaque palette planes after
composing source sprite priority. No visible geometry is invented or dropped.
Octopus retains its previous colors, including blue weapon/Bell details. Its
repacking improves visibility but does not solve its dense overlap problem.
The662 source-record comparisons cover the new pooled body/weapon/pickup data,
including duplicates across pools; they are not662 unique animations or a full
runtime visibility certificate. The original field/weapon/motion programs and
world adapter source are unchanged.

The unsupported `!?` text is replaced with `RST` in the reset cell. The native
reset-before-defense order and all equipment rules remain. This is a readable
text HUD repair, not certification of complete original power-bar art/layout.

The existing shared Gradius death-burst path was publishing live Parodius
tiles. The draw dispatch now follows its graphics dispatch during death. The
same physical terrain-death test fails49 rendered frames before this fix and
passes all49 afterward for each of the three alternates, through respawn.
This repairs tile ownership only. Original Parodius death animation, palette
and rendered-pixel fidelity remain to finish; the common Gradius burst is not
being presented as a source-authentic Parodius death.

## Current candidate evidence

`build/verification/parodius-render-nq/proof.json` binds the receipts to the
exact candidate, input streams and passive trace files.

- All three alternates have fresh Easy and Hard cold-controller1-1 discoveries
  and independent fixed-input replays:6 clears,29,878 video frames, zero deaths,
  native transition and movement restored in1-2. Each replay's input file is
  byte-identical to its own discovery. Actual behavior bytes are checked.
- Actual committed pose records, DMA, hardware CHR and palette are examined.
  Every intended interior body part reaches DMA. First-eight-per-scanline
  modeling also counts projectile/native-actor competition and sprite pixel
  occlusion. It does not model background occlusion or certify real hardware.
- Pentarou Easy's pixel-weighted body coverage rises57.0% to98.3%; TwinBee's
  rises67.5% to98.3%, with zero fully hidden frames in both final checked runs.
  Octopus rises67.7% to74.4%. Hard coverage is73.6% /98.2% /98.4% respectively.
  These are separate before/after controller routes, not an identical-input
  CPU benchmark or an all-pose coverage claim.
- The six replays retain substantial lag: Easy1295/1203/1195 lag NMIs for
  Octopus/TwinBee/Pentarou; Hard1372/1289/1236. Each includes3055 or3056 native
  ship updates. Partial dropout remains even in the improved characters.
- There are336 actual nametable checks for the complete28-cell HUD label row.
  No unsupported question-mark tile is admitted in those samples.
- All37 identities pass cold selection/movement/interrupt-ownership entry
  checks. These are not37 final campaign clears.
- All three component, Bell and physical pickup suites pass. The pickup suite
  includes45 uploaded pixel/color comparisons. These are explicitly seeded
  arenas, not natural full-powerup campaign certificates. Roll's Easy component
  regression passes. Ordinary14-identity MMC3/5 builds retain exact prior hashes.

Screenshots around the body and death defects, all failed attempts and the
partial v1/v2 repairs are retained. Sampled images were visually inspected;
this is not a claim of manually viewing every video frame. The NPC palettes
and native Bowser/Podoboo sprite windows remain owned by the existing engine.

## Source death follow-up

Ordinary-controller exploration of the authenticated original cartridge is in
`original-death-exploration-v4/`. Earlier attempts stopped in original menus;
they are not gameplay/death evidence. The fourth enters Octopus gameplay and
observes death beginning at video frame2561. The original live trace selects
animation89, with sprite-frame values122–126. Its original animation table is
at53541 ($D125), with explicit4/10/160 delay entries and terminator255. The
source renderer's sprite group, skin pages and palette still need capture to
implement this faithfully. Its trace is discovery evidence, not proof of the
candidate's death animation.

## Remaining goal work

Octopus still has severe individual dropout frames; Big forms and the fullest
fleets need stronger runtime coverage. Global lag, dedicated Roll/Parodius audio,
source death fidelity, remaining character details, the production oversized
MMC3 integration and final every-identity/every-powerup matrix remain open under
`final-verification-plan-2026-10-23.md`.

To stay below30GB, completed source-rebuild staging from NP/NO/NN was moved to
the existing external archive with every file hash verified. Their checkpoint
ROMs and source ZIPs remain local. No lossless evidence was discarded.
