# MMC5 lag-frame HUD font repair — private NW

The tested candidate is
`f650bbb4980ad11911eef1a214405191abd17b4f31f1960af3f2d1d7cdc1a402`.
It adds a font-only repair to the private NV Gradius music checkpoint. Published
ROMs and the ordinary mapper targets remain unchanged.

## Cause and change

The scanline IRQ switches background window 0 from the HUD font to the level
font. Guest lag NMIs deliberately preserve the previous sprite CHR banks,
because their OAM can still be the previous completed image. That also skipped
re-establishing the custom background font. Vic's power bar then interpreted
its label tile numbers through the level font, producing unrelated shapes.

The early common guest-audio entry runs on both regular and lag NMIs. It now
re-establishes only background window `$5128` when a custom HUD is active and
rendering is enabled. The font's two upper CHR bits are captured with that
write, then the shared `$5130` latch returns to zero for the later world-font
IRQ. Sprite registers, queued body publication, CHR assets, palettes, OAM and
physics are untouched. No additional RAM is allocated.

The native condensed Gradius label masks and layout are unchanged. This fixes
their raster ownership; it is not a new font or a claim that every other
character's HUD has received a visual redesign.

## Evidence

- Retained NV negative: 54 of 270 sampled native HUD frames differ from the
  committed font/nametable masks, totaling 38,502 incorrect pixels.
- Final Easy discovery and independent cold replay: 4,782 frames, zero deaths,
  then 25 frames of actual control in underground 1-2. Full input and trace
  bytes match. All 3,253 observed active player/CHR frames pass ownership checks.
- Final Hard discovery and independent replay: 4,897 frames, zero deaths,
  then 25 frames of underground control. Full inputs and traces match. All
  3,281 observed active player/CHR frames pass.
- Actual native HUD pixels match on all 3,253 Easy and 3,281 Hard frames:
  10,036,224 compared pixels, zero mismatches. Background publications stay
  within the expected HUD394/world0 pair, with no late font publication in the
  displayed HUD region. The comparison covers x32..223/y8..15, not every pixel
  of the complete frame or palette hue.
- All 37 identities pass actual cold selection, alternate persistence, lives
  display, ordinary entry/movement and interrupt ownership checks.
- Native Gradius audio still passes 12 area/event cases, 133,120 source-register
  comparisons, 115,967 hardware comparisons and 8,320 borrowed-state checks.
- The established 24 source-effect tests pass 3,948 exact register checks plus
  full durations, voice ownership and music restoration. Only their obsolete
  controller startup was adapted to the current menu; effects remain explicit
  request fixtures, not natural collection evidence.
- Flag-off ordinary MMC3/MMC5 rebuilds retain their exact published hashes.
  The final checkpoint records a standalone source-ZIP rebuild as well.

The pixel reference uses one fixed alignment: live PPU snapshots taken at
endFrame correspond to the next completed screenshot, consistent with the
existing DMA observer's physical-frame convention. The first unshifted checker
falsely reported the two entrance frames. Its output is retained and superseded;
no frames are selectively excluded to obtain the final result.

## Retained unsuccessful experiments

Candidate v1 did not link and was never installed. Candidate v2 restored the
font but left the shared upper CHR latch at one; the later IRQ consequently
selected world bank256. Its failed background publications and images remain
retained. Candidate v3 resets that shared latch and passes both pixel and bank
checks. Frozen NV remains available separately.

All native replay frames, telemetry, masks, candidates and failures are under
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-vic-hud-nw`.
Local evidence is indexed by `build/verification/vic-hud-nw/proof.json`.

## Remaining scope

This is a narrow HUD and music regression pass. It does not complete the
every-character/every-powerup matrix, source music/SFX for other unfinished
families, full Gradius weapon audio, broad lag/dropout repair, other castle
hazards or the 37-identity MMC3 port. The source-song boundary flaw found during
NV also requires re-auditing other recorded NSF inputs. The final goal remains
active.
