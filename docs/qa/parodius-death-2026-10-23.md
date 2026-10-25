# Private Parodius death rendering / NR

This continues the full verification plan; it is not a release or a final roster
pass. The published33-identity MMC3/MMC5 ROMs remain unchanged. The private MMC5
candidate is `build/verification/parodius-death-nr/candidate-v2.nes`, SHA256
`2931163dd7d3c31f9a81776b16c45631a0abd2120abff4454833084825475590`.

## Source and repair

The authenticated original is `Parodius Da! (Japan).nes`, SHA256
`ef1dd05ad5b6095d1d8e9a9f81fcb549b5cf0248779d4e76eb7bd9b139de4c9a`.
Its player-death entry at original$8001 selects animation through$932E,Y,
uses skin10, and gives TwinBee palette override1. It is not a common explosion:

| Pilot | Animation | Sprite records | Colors |
|---|---:|---|---|
| Octopus |89|122–126|Original white/pink/brown |
| TwinBee |91|68–70|Original white/yellow/dark red |
| Pentarou |90|236–240|Four colors exact; source yellow28 uses shared yellow27 |

Ordinary-controller captures of all three original deaths confirm the actual
sprite records, palette override and physical CHR. The original remaps its CHR
to blank page51 in vertical blanking. Earlier endFrame pattern dumps therefore
returned blank data; those attempts are retained and excluded. The admitted
startFrame captures resolve logical addresses to physical ROM bytes and match
the original committed OAM. Their folders are the NQ `original-death-pixels-v9`
capture for Octopus and NR `original-variant-2/3` for TwinBee/Pentarou.

The native animation routine and its unmodified tables now drive each pilot's
own sequence. Generated records retain original visible geometry and flips;
their pixels are repacked into unused family pages892/956/1020. Pentarou's five
colors require the private player palette plus shared white/yellow. The single
declared yellow quantization preserves NPC palette ownership. No SRAM is added.
The player's live tiles are retained until matching death OAM is constructed.
After respawn the normal private palette, native skin and actual movement return.

SMB keeps its existing120-update death/respawn lifecycle. This does not reproduce
the original game's overall death hold/respawn duration or its final-cursor wait
state. The differential checks cover each actual call of the original animation
routine up to that SMB transition, not the original game's entire death handler.
Dedicated original death audio remains part of the open audio work.

## Evidence boundary

The current strict death fixture is `tests/parodius-native-death.lua` and the
admitted run is NR `death-v7`. Three seeded solid-terrain arenas enter through
ordinary character selection, produce one real terrain kill each, and verify
movable respawns and restored live palettes. They do not inject death flags.
The source oracle checks354 completed DMA frames,363 native animation calls and
67,666 source-pixel observations across all13 distinct records. It compares the
original animation instructions with the runtime state trace, actual uploaded
CHR/palettes and all intended committed body sprites. Screenshots of the13
records were reviewed in `native-burst-review.png`; screenshot sampling waits
for a stable pose to avoid labeling the previous framebuffer as a new pose.

The first implementation mistakenly assigned Octopus's animation to all three
pilots. Candidatev1 and its passing narrow checks are retained as incomplete
evidence, not admitted source-fidelity proof. The later source-table and original
TwinBee/Pentarou captures exposed the mistake. Early respawn assertions also
sampled the first engine8 transition before native movement resumed; the current
fixture waits60 frames, requires actual movement updates and keeps its live-state
and palette assertions. Old failures and their embedded scripts are retained.

The final NR proof separately binds six fresh controller discoveries from
retained NQ prefixes and six independent fixed replays, Easy/Hard for each pilot.
Each must clear1-1 with zero deaths and prove movable1-2, matching committed CHR,
actual HUD glyphs and rendered body records. A direct older Octopus stream ended
before the changed candidate met movable1-2; it is retained as a failed replay.
Fresh complete streams, rather than a relaxed completion assertion, are used.
Cold selection/movement/interrupt checks cover37 identities. Component/Bell/
physical pickup suites and Roll's Easy ability regression are separate arenas.
None of these narrow suites is the final every-powerup campaign matrix.

## Remaining work

Octopus still has severe partial sprite dropout. The full fleets/Big forms,
global lag, dedicated Roll/Parodius audio, other source-fidelity gaps, production
oversized MMC3 integration and the final every-identity/every-powerup checks
remain open under `final-verification-plan-2026-10-23.md`. NR makes no60Hz claim.
The guide remains explicitly pinned to NQ for its four development previews.

Completed older source-rebuild staging and the superseded candidatev1 controller
routes were moved to the existing external archive with every file SHA verified.
Checkpoint ROM/source ZIPs stay local. No lossless evidence was discarded.
