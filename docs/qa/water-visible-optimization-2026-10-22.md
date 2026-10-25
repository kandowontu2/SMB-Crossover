# Water Shield collision work

The current Mega Man/Bass shield uses a direct Water50 enemy consumer. It keeps the original inclusive/wrapping collision core and native DamageEnemy routine. Every ball reads live enemy state, visibility, position and health; earlier balls can change the later balls' targets. No geometry snapshot or replacement physics is introduced. The broad candidate scan omits offscreen enemies that the original consumer already rejects.

The additive merge preserves the installed terrain publication, score anchors, Cheats, cannon cooldown, firebar allocation and Claude Sophia head-origin changes. The helper occupies208 bytes at bank24 A:B600-B6CF, adds no RAM, and leaves the shared Ryu and score reservations intact. Existing SPECIAL_MM grows10 bytes and its external callers are bound to the same symbolic routines. Header, CHR and rebuilt baselines are unchanged.

## Current evidence

Both mapper builds pass42 scoped native tests:18 Water behavior/drawing/armor checks,4 Cheats checks and20 audio/weapon/retained-fix regressions. The unchanged geometry oracle executes42760 cases per mapper over flags, all enemy IDs, state boundaries, offscreen classes, inclusive/wrapped edges, armor, health and multiple contacts. The private Bridge/both-consumer oracle checks1040 Bridge cases and2080 consumer calls per mapper.

An independent current-ROM replay executes213 captured full weapon calls with all42 attained interrupt boundaries, exact registers, every10240 RAM bytes, hardware-read order, mapper restoration and ordered writes. A separate matched-input no-interrupt comparison continues the actual parent suffix to GameLoop's publication. It proves every differing input RAM cell is replaced before any read there and changedY is overwritten before use. Actual moved return pushes and standard farcall operands are individually decoded and symbolically bound; no stack/SMC range is discarded. This is bounded attained coverage, not a universal interrupt-phase claim.

Earlier CN/CP/CQ comparisons and their failures remain. CN inherited a privateJ output-equality assumption that does not apply to CI's older unfiltered candidate scan. CI's rejected offscreen consumers leave different deadY/proxy scratch. CP then required literal suffix write equality despite relocated draw pushes; CQ exposed an additional relocated Bass target. The final CR/CU checks preserve complete native equality and explicitly prove subsequent use of changed inputs, while binding each changed suffix write to its actual producer.

## Measured cost

In the populated1-1 diagnostic, actual inputs summon eight balls, approach native enemies and expand the shield. Equipment and Hard mode are authored and journaled; player positions, enemies and terrain are ordinary native world state. These runs are not natural-acquisition or playthrough evidence. Exclusive timings subtract attained IRQ/NMI time; nested scopes are not additive.

| Expansion near visible enemies | Previous ability cycles, mean | Current | Reduction |
| --- | ---: | ---: | ---: |
| Mega Man MMC3 |11750|10636|9.5%|
| Bass MMC3 |11735|10600|9.7%|
| Mega Man MMC5 |11587|10463|9.7%|
| Bass MMC5 |11601|10466|9.8%|

Full GameLoop means also fall in these four bins, but the MMC3 Mega Man maximum rises33420 to36363 cycles. Native interrupt phase, route pacing and sample populations differ across builds. The raw maximum is retained and prevents a universal frame-time claim.

In a separately authored six-enemy/eight-ball stress arena, complete GameLoop mean falls45050 to44496 cycles on MMC3 and42454 to41771 on MMC5. Worst cases also fall in that arena. The total lag increments remain46 on MMC3 and45 on MMC5. This is a CPU saving; visible Water Shield lag still needs further work.

Checkpoint: `build/checkpoints/water-visible-cw/manifest.json`. Aggregate receipt: `build/verification/water-visible-final-cw/summary.json`. All source captures, raw profiles, controller journals and negative checks are retained. The original full-roster through2-2, every ability/upgrade, remaining footage defects and final recordings goal is still active under the user-authorized100GB retention cap.
