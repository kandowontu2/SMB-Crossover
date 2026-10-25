# Private Parodius integration

Octopus, TwinBee and Pentarou are selectable with Select on Vic Viper's card in
the private expanded MMC5 candidate. Their original Famicom movement, equipment,
projectile and animation instructions are retargeted into the SMB engine. A fires
and B purchases the highlighted cell, matching the existing ship controls.

The source cartridge is SHA256
`ef1dd05ad5b6095d1d8e9a9f81fcb549b5cf0248779d4e76eb7bd9b139de4c9a`.
Its 92 isolated core differential cases per proposed mapper layout are separately
documented under `parodius-native-ni`. The subsequent Bell work adds 272 cases
per layout and expands the original renderer oracle to 1,796 group0/group1 cases.
Current Bell/pickup evidence is described in `parodius-bells-2026-10-23.md`.

## Current integration

- Seven source equipment cells, source speed and Option caps, separate missiles,
  Tailgun/Double, Ripple/3-Way/Spread and original shield animation/HP machinery.
- Original body, speed-change, Big, Option and weapon shapes. Adaptive CHR pools
  preserve source offsets/flips; 664 packed native pose cases now pass. Shared world
  palettes are retained, with explicitly declared color quantization.
- SMB enemy rectangles meet the original projectile half extents. Single-cell
  native block transactions preserve protected ground and activate question
  blocks through SMB's ordinary reward animation.
- Physical capsule adapters and SMB mushroom/flower replacements advance the
  bar. Original character-specific Parodius capsules, colored Bells and five
  score sprites replace the temporary art. Gold streaks, roulette, White1UP,
  Super Bomb, three Red crest shots and the full Big timer are integrated.
  The source-to-SMB enemy drop policy still needs final review.
- Drawing reserves the complete player plus eight world sprites. Oversized
  effects draw rotating subsets. Native horizontal carry flags are translated;
  weapon parts above the status bar or outside the vertical viewport are omitted.
- The final draw step restores the actual body-record bank, even with no active
  projectiles. Without this, Pentarou's Big pose was read from the ordinary Vic
  bank and produced an invalid length. Pipe reset no longer clears overlapping
  Gradius-only actor/history fields in a Parodius state overlay.

The private graphics occupy physical CHR pages 832–1023. This leaves room for
the expanded MMC3 menu atlas below them. The native integration uses inactive
character/audio storage; no extra cartridge WRAM was allocated.

## Evidence and diagnostic boundaries

`build/verification/parodius-integration-nl` preserves component failures,
corrections, controller routes and replays. Component arenas explicitly seed
world/equipment state, staged together at a real native update boundary rather
than interrupting a partially processed actor at a video callback. They check
source equipment limits, both gun choices,
real Goomba defeat, question-block activation, protected ground, Big, a physical
SMB pickup, capsule cleanup, interrupt-bank restoration, body/world sprite
reservation and viewport clipping. They do not prove all pickup acquisition or
exact audio/bell parity.

The first surface routes flew into a used block, then an incoming Goomba at the
far screen edge, and later the tall stairs. Traces confirmed real contacts;
these were controller-route failures, not grounds for weakening terrain/enemies
or changing the source physics. The revised controller leaves reaction space
ahead of the ship and climbs before the final stairs.

An early rendering assertion also fired in an unrelated PRG bank at the same
CPU address. Hooks now qualify the physical bank before asserting. The genuine
Pentarou Big-bank failure remained with valid hooks and was repaired.

All three identities have a controller-only Easy surface clear and independent
replay through restored movement in 1-2. Final private snapshot receipts bind the
component/entry/replay checks and a byte-identical source-bundle rebuild to one
ROM. Published MMC3 menu checkpoint `mmc3-menu-nk` remains separate.

## Still required

Hero-change acquisition, the final Bell disappearance animation, precise left-edge
Bell lifetime/streak behavior, source SFX/music, dynamic palette overrides, exact shield contact geometry,
MMC3 state/CHR/menu integration, Hard/shortcut coverage and full visual/performance
review remain unfinished. The final full-roster and every-powerup gate is in
`final-verification-plan-2026-10-23.md`. This private build is not a final release.
