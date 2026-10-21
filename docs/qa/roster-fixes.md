# Roster corrections in progress

This follows [the source audit](roster-source-audit.md). The audit describes the old checkpoint; it is deliberately retained as historical evidence. This document tracks its corrections and remaining work. The ROM is not yet source-identical.

The later [walking/brick/flight/music update](walk-flight-update.md) has newer ROM hashes and verification. The 283-case results, 78-rule observations and twelve videos below belong to this document's earlier hashes; those videos were not relabeled as recordings of the later build.

The later2.02 Link movement audit in [the through2-2 ledger](roster-through-2-2-link-simon-ryu.md) supersedes the hosted1.0 horizontal movement rules below:2.02 uses immediate175 speed, stops on neutral/both directions, and stops during a grounded sword attack. Historical coasting observations and the old78-rule results remain attached to their original source version and ROMs.

## Implemented

- Empty metasprites safely return without reading parts or modifying OAM. Small Luigi ignores crouch input. Luigi's large atlas, missing hurt/death poses, Mega Man's hurt pose and Sophia's missile art use the pinned source labels.
- All 78 independent numeric source rules match on both mappers in [the current observations](../../build/roster-fixes/vram-observations/comparison-table.md) (24 fixture captures, 50,400 updates). The expected contract was not changed. These are actor fixtures, not controller-only level clears.
- Source acceleration, friction, jump-release, terminal speeds, attack movement locks and projectile limits/speeds were corrected for Pit, Luigi, Ryu and Sophia. Luigi also has source reversal/skid friction and its atlas pose. Link's airborne momentum, coasting attack and beam speed were corrected. Bill can fire downward in air and jump from crouch. Simon can jump during attacks/crouch and no longer has an invented dry fall cap.
- Bill's automatic fire retains the 110ms timer remainder and burst delay. Link's boomerang has directional throws, distance braking and spring return, and his beam produces four moving impact fragments. Ryu has the source's directional wall-jump variants, 45ms sword/throw phases for ground/crouch/air/wall stances, delayed throw launch and source windmill reversal/spring/vertical tracking. Windmill hit suppression lasts through continuous contact, allowing a new hit after leaving and returning. The unused source friction constant is not applied. Sophia has initial gravity-free rise, underwater steering/damping/drift and timed hover consumption/regeneration.
- The 2.02 characters use their source enemy HP/damage values, including Luigi's five-fireball Bowser and the later guests' 1100-HP World 8 Bowser. Ryu and Sophia retain their normal source palettes through pickups. Guest spring velocities have separate source profiles.
- Samus has her periodic native walking sound. Bass, Ryu and Sophia route their source area/event playlists; 42 selections each matched 400 captured APU-register updates on both mappers in the final suite. This validates frame-quantized non-DPCM commands; most looping songs currently restart after 90 seconds. Bass now also uses the imported MM3 native short-effect engine for buster, hit, damage, extra-life, landing and death sounds, with a separately initialized persistent SFX register image and source channel priorities. Mega Man now has his missing native landing cue.
- Bill/Simon's moving corpses land before their death delays begin. Link has flash, wait, spin, gray and cross phases. Luigi freezes then launches; Ryu moves and lands before his delay; Bass has the source particle burst; Sophia has its source explosion, wheel/cannon/hover/wall artwork. Normal-death tests pass on both mappers. They caught and corrected Ryu's counter freezing after 255 updates, Bass's particle lookup using the wrong graphics bank, and one frame of a living guest sprite reappearing at the life-loss transition.
- Pit, Luigi and Sophia accept rapid fresh attack presses up to their source projectile limits. Their source pose timers do not impose a fire delay. Three controller-input fixtures reproduced and removed the port's invented eight-update cooldown; held B still does not auto-fire for these characters.
- Guest lag NMIs retain the physical CHR mapping with the previous hardware OAM. Applying a new pose bank before its OAM is ready caused real scrambled Bass frames. The hardware-register stress check failed before the fix and now passes on both mappers. [Native before/after frames](../../build/roster-fixes/bass-chr-before-after.png) show the same controller inputs and timestamps. Desired-pose telemetry can still advance during a lag frame; adjacent native images distinguish that from a physical mapping error.
- The screen loader waits for NMI to consume a pending full VRAM column set. Previously, a lagged loading frame could append another set, wrap the offset, and display command bytes as terrain after the shortcut pipe. The pending-buffer fixture reproduced the problem and passes on both mappers after the fix. [Native pipe-exit before/after](../../build/roster-fixes/bass-pipe-before-after.png). MMC3's inline far-bank macros also publish `CurrentBank` before switching hardware, making interrupted bank restoration safe.

## Verification

The complete [283-case Mesen regression suite](../../build/verification/summary.json) passes on both mappers, including all playlist selections, normal-death checks, rapid fresh-press cases, physical bank retention and pending-VRAM loading. Mario's 19 sampled state fields match the native baseline over 521 frames. The independent source audit also matches all 78 measured rules on these exact ROMs. These are emulator tests, not physical hardware tests or proof of full source parity.

MMC3 SHA-256: `7b9987c6083340cce0832efb419a96eefe9e2ed716ad863f8086ad1be31e58f6`.

MMC5 SHA-256: `4c1933e3ed926b4f1476b06928b52abb843af40ec993bc21e576bf38e76a7d3c`.

Some existing fixture expectations were corrected from primary source: Link's air friction, Sophia's initial-rise gravity and neutral water damping, Bass's 17-damage hit against 75 HP, and a Luigi enemy fixture that previously spawned eight pixels inside the floor. The Link beam fixture now waits for its arena initialization before examining impact state; power-on WRAM cannot falsely mark a pre-game impact.

All six additions now have fresh fixed-input MMC3 replays on both routes, through actual control in 1-2. Surface runs defeat all 17 enemies and collect all five powerups; shortcut runs defeat six enemies and collect the first powerup. No enemy fall/despawn was counted as a defeat in these twelve final runs. The [combined evidence](../../build/roster-fixes/controller-review.json) binds each manifest, review, controller stream and ROM hash.

Every recorded frame was decoded: 59,762 native video frames, 35,896 HUD split observations, 11,728 queued sound cues and 36 powerup emergence sequences. Automated checks found no vertical-stage shifts, split timing errors, missing common/native cues after source-priority accounting, palette errors, selected animation-pose errors, position jumps, emergence motion errors or HUD glyphs in terrain. This is automated per-frame review with targeted manual contact-sheet inspection, not a claim that every frame or waveform was manually reviewed. Native audio is included in every video.

| Character | Surface video | Shortcut video | Lag frames, surface / shortcut |
| --- | --- | --- | ---: |
| Pit | [17 enemies, 5 powerups](../../build/playthroughs/roster-fixes-current-6-surface/playthrough.mp4) | [6 enemies, 1 powerup](../../build/playthroughs/roster-fixes-current-6-pipe/playthrough.mp4) | 31 / 20 |
| Rygar | [17 enemies, 5 powerups](../../build/playthroughs/roster-fixes-current-7-surface/playthrough.mp4) | [6 enemies, 1 powerup](../../build/playthroughs/roster-fixes-current-7-pipe/playthrough.mp4) | 28 / 16 |
| Luigi | [17 enemies, 5 powerups](../../build/playthroughs/roster-fixes-current-8-surface/playthrough.mp4) | [6 enemies, 1 powerup](../../build/playthroughs/roster-fixes-current-8-pipe/playthrough.mp4) | 6 / 12 |
| Bass | [17 enemies, 5 powerups](../../build/playthroughs/roster-fixes-current-9-surface/playthrough.mp4) | [6 enemies, 1 powerup](../../build/playthroughs/roster-fixes-current-9-pipe/playthrough.mp4) | 681 / 221 |
| Ryu | [17 enemies, 5 powerups](../../build/playthroughs/roster-fixes-current-10-surface/playthrough.mp4) | [6 enemies, 1 powerup](../../build/playthroughs/roster-fixes-current-10-pipe/playthrough.mp4) | 23 / 17 |
| Sophia | [17 enemies, 5 powerups](../../build/playthroughs/roster-fixes-current-11-surface/playthrough.mp4) | [6 enemies, 1 powerup](../../build/playthroughs/roster-fixes-current-11-pipe/playthrough.mp4) | 156 / 41 |

Raw desired-pose/CHR observations remain in the reports: one Pit sample per route, 75 Bass surface samples and 21 Bass shortcut samples. Their adjacent native frames were inspected after the physical bank fix; the prior scrambled tiles are corrected. Crowded rows still visibly lose alternating sprite parts. Bass's buster also intentionally yields to the native enemy-hit effect: its imported priority is 7 versus 9 for enemy hit, even though the voices differ. The reports preserve those suppressed cues separately from missing effects.

A Bass replay exposed different lag timing with randomized cold-boot RAM. Final route captures explicitly select Mesen's all-zero power-on RAM and disable random CPU/PPU alignment and mapper startup. This is an emulator startup configuration, not an injected gameplay state. The 283-case fixture suite retains the existing runner settings. Historical captures retain their own settings/hashes and are not relabelled as new proofs. The enemy audit records Y-high as well as Y-low so genuine falls across the low-byte boundary are distinguished from horizontal escapes.

## Still open

- Enemy white hit silhouettes; Simon's overloaded composite whip poses; remaining native fractional collision/muzzle approximations.
- Sophia's accelerating/triplet/homing missiles; complete 2.02 independent inventory/ammo and Bass/Ryu special-weapon collections.
- Remaining source animation timing, including Luigi's full grow/shrink and fireball-impact sequences, composite Bill aiming poses, Sophia attachment transitions and character-specific short-effect/landing/hover audio.
- Further CPU performance work. Bass still has substantial lag under sustained combat/audio load, as the recorded counts above show; the bank fixes prevent corruption, not all lag.
- Music loops beyond the captured segment and DPCM. Pit/Rygar event themes and several sound effects remain adaptations.
- Rygar's larger SMB traversal jump and Pit's requested crouch attack/hammer remain intentional adaptations. Mario retains the requested native SMB foundation.

Do not interpret the fixed numeric checks or previous controller clears as proof that these open items have been completed.

## Audit interpretations rechecked against code

- The hosted 1.2 Mega Man source does **not** contain a level-entry teleport animation. Its inherited `Character.teleport` shifts X and overrides the camera; `Character.initiate` initializes the actor normally. The earlier missing-entry-teleport claim was unsupported and is withdrawn. A later-version arrival sequence must not be invented as a requirement of this pinned reference.
- Link's 150ms initial stopped `attackStart` pose carries the active sword rectangle in `Link.checkState`. The timer then changes to `attack-2`, with two short retraction phases. The overall 13-update duration was reasonable, but the old 9–10 hit window was late. It is now active at ages 0–8, including the initial press. A focused fixture checks an immediate hit and a new target entering during retraction.
- Ryu's `STAR_BIG_FRICTION_X` is assigned but is not used by his projectile's active update path. Applying it merely because the constant exists would introduce a new discrepancy. His 2300 spring acceleration and 800 speed cap are verified against the source equations in both directions.
