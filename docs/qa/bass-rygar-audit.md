# Bass and Rygar audit — 2026-10-16

This checkpoint corrects Bass's default movement, buster and artwork, and Rygar's unpowered Diskarmor path and standing throw art. Both MMC3 and MMC5 ROMs are rebuilt. The scope is the currently implemented abilities; this is not a claim that the complete Crossover weapon inventory or every original-game effect has been ported.

## References

Bass was checked against the pinned **Crossover 2.02** `Bass.as`, `MegaManBase.as`, `MegaManProjectile.as`, `DamageValue.as`, `HealthValue.as`, and the default Bass bitmap sheet. The SWF SHA-256 is `6374c72426556bfc3cc16f7594ce4443a5867fe2d367514136c99cc8458b70af`.

Rygar was measured in the user's original **Rygar (USA)** ROM, SHA-256 `965330fed9f5b8492452f3b53084752e83b7f899a1f88f3c475ece2fde6f9231`. `tools/reference/capture_rygar_motion.lua` supplies ordinary controller input and reads screenshots/OAM/CHR/palette data. It does not write game memory or registers. The original file remains unchanged. The capture manifest and CSV are under `build/rygar-audit/native/`; persistent measurement metadata is in [rygar-motion.json](../reference/rygar-motion.json).

## Bass corrections

| Area | Corrected behavior |
| --- | --- |
| Movement | The source's movement override takes precedence over its unused acceleration constants: a two-NES-pixel initial step, 100 ms step hold, then instant 1.375 px/update walking and immediate stop on release. Underwater ground walking caps at 0.75. |
| Jump | Normal launch 565/120 px/update; gravity 1500/7200 px/update²; release applies the source's vertical friction. One second jump is allowed. Water uses 500/120 jump and 500/7200 gravity. |
| Falling | The fractional 700/120 terminal speed is compared across all velocity bytes; it no longer clamps prematurely when the integer part first reaches five. |
| Dash | Down+A uses a short collision profile, 2.5 px/update dry or 1.875 submerged. The distance test follows the source's strict endpoint comparison. Wall contact and opposite input cancel the dash when there is headroom; a roof keeps the short profile. |
| Dash jump | Launch uses 650/120 upward speed and retains the dash air-speed cap. It does not expire on the previous 24-frame timer. A second jump restores the normal air cap. Walking off an edge ends the ground-dash firing restriction. |
| Ground firing | B stops ground movement, including the remainder of the firing pose after release; aiming can still turn him. An ordinary Down press does not duck him. Select does not fire the default buster. |
| Rapid fire | 75 ms cadence retains its half-update remainder through alternating five/four-update cooldowns. Maximum active shots are three before the mushroom and four afterward. |
| Aim | Seven directions, including Down+B without horizontal input aiming diagonally down in the facing direction. Speed is 580/120 px/update, with diagonal axes multiplied by 0.75. Muzzle offsets distinguish ground and air poses. |
| Damage | Default buster damage is 17 in every power state. The invented flower piercing/stronger default-buster behavior is removed. |
| Graphics | Correct atlas cells for jumping, ground shooting, upward/diagonal aiming and their airborne versions. The projectile now uses the actual orange buster graphic, replacing an incorrectly cropped HUD fragment. The default buster suit retains its orange/black/gray palette through upgrades. |
| Sprite budget | Bass-only packing optimizes combined scanline occupancy across color layers. Every generated body pose fits eight hardware sprites per scanline when alone. The buster needs one sprite. Existing priority rotation still shares visibility in crowded scenes. |

[Representative ground/air aiming frames](../../build/bass-rygar-audit/bass-aim-contact.png)

## Rygar corrections

Original standing-right OAM frames 304–313 give these disk-center offsets from the body center, in NES pixels:

`24, 28, 32, 36, 40, 36, 32, 28, 24, 20`

Crouching-left frames 343–352 give:

`-22, -26, -30, -34, -38, -34, -30, -26, -22, -18`

The port now reproduces those ten visible gameplay-update positions: four-pixel extension/return, the original mirrored anchor offset, and catch before the center reaches the body. The old throw incorrectly started at zero, extended farther, then returned all the way to zero. Invisible windup frames no longer collide with enemies or blocks.

The original has **one short chain sprite**, whose center trails the disk center by twelve pixels. The former three-link tail has been replaced. Standing and crouching disk centers are respectively 24 and 17 pixels above the feet. The disk uses both original animation tiles and their correct horizontal/vertical reflection. Standing attacks now use an extended-arm capture rather than a frame holding the disk against the torso.

The mushroom/flower maxima of 64/88 pixels are this port's upgrades, not measurements of original Rygar adventure items. Regression checks also cover moving/airborne anchoring and wall-triggered return. Original injury blinking limits the airborne reference samples; no exact native airborne-animation or disk-spin phase claim is made. Rendered screenshots follow the games' different OAM/DMA staging, so the offset assertions use end-frame OAM/gameplay state rather than equating screenshot indices.

[Consecutive original/port frames](../../build/bass-rygar-audit/rygar-return-contact.png) · [Slowed diagnostic animation](../../build/bass-rygar-audit/rygar-return-slow.gif)

## Verification

`bass-reference.lua` exercises 60 aim cases: ten direction/facing inputs, ground/air and three power states. It checks muzzle coordinates, actual velocities, pose selection, physical OAM scanline counts and PPU colors. Further cases verify fire cadence/limits, initial step, stop/reversal, firing lock, short/held jumps, second-jump limit, dash/roof collision profile, dash jump, wall/reversal cancellation, off-edge shooting and the fractional fall cap.

`rygar-native-return.lua` asserts the measured sequence in both directions, standing/crouching, moving and airborne, with actual single-chain OAM allocation. `pit-rygar-attacks.lua` checks all upgrades and block/enemy interaction. The existing water, pipes, pickups, lives, sound mixing, NMI preservation, terrain protection and death/respawn cases run on both mappers. The block fixture now places Rygar's target at his corrected standing weapon height.

The full-suite result and ROM hashes are recorded in [summary.json](../../build/verification/summary.json); the task's focused evidence and replay manifests are in [the audit summary](../../build/bass-rygar-audit/summary.json). These emulator fixtures use explicit state setup and are not physical-cartridge tests.

**Final result: all 241 emulator cases pass across MMC3 and MMC5.** Mario's 19 state fields remain identical to the baseline through the 521-frame replay. The expanded Bass roof case also passes on both mappers.

Two additional fixed-controller **shortcut-route** recordings start from power-on without RAM/register writes. Both defeat all six encountered enemies, collect the mushroom, survive and verify control in 1-2. Every captured frame was decoded; manual review covered aiming/attack contexts, item emergence and the original/port disk sequence.

| Character | Video | Decoded frames | Lag frames | Overloaded sprite frames | Queued common SFX checked |
| --- | --- | ---: | ---: | ---: | ---: |
| Bass | [shortcut replay](../../build/playthroughs/bass-final-proof-9-pipe/playthrough.mp4) | 4,156 | 21 | 901 | 1,006 |
| Rygar | [shortcut replay](../../build/playthroughs/rygar-final-proof-7-pipe/playthrough.mp4) | 3,736 | 16 | 18 | 291 |

The automatic video/state review found no stage-row vertical shifts, bad HUD split timing, CHR-bank mismatches, mushroom palette errors, abnormal emergence motion or missing queued common sounds. Native PCM audio is present in both recordings. This checks mixer delivery, not source waveform identity. These are new shortcut runs; the older surface-route recordings remain evidence for their historical checkpoint. An exploratory new Rygar surface run died and is not accepted as a clear.

## Remaining reference differences

- Bass's complete special-weapon collection, ammo/selection system and source-specific upgrade inventory remain outside the port's three-state pickup system.
- Shared enemy health still follows the existing port table rather than Crossover 2.02's table; for example, the port Goomba has 100 HP versus 75 in that source. The corrected 17-damage Bass buster therefore takes six hits there rather than five. Enemy white hit-flash rendering also remains incomplete.
- Bass's death uses the simplified guest sequence, not the source's full particle burst. Its old unrelated atlas glyph is replaced with a hurt pose.
- Character-specific short sound waveforms, landing effects and full area/death/victory music parity remain unfinished. Bass currently uses the captured Strike Man stage stream and common NES sound-effect mixer.
- Eight sprites per scanline remains a hardware limit. Bass's body alone now fits, but bullets/enemies can still overload the same row. The recorded 901 overload frames are not a claim of zero flicker or zero lag.

## Checkpoint

- MMC3 SHA-256: `df0e850b2bd3903990bb061eb02b1dcac00537ae54aa403b2c86cee7eed4391a`
- MMC5 SHA-256: `281499572c1f764610a645a67ef0b8e4d90b376202c86a98a4a9ecaae179d14f`

```powershell
python tools/verify.py --mmc5 --jobs 4
python tools/run_mesen.py tests/bass-reference.lua build/smb-crossover-mmc3.nes
python tools/run_mesen.py tests/rygar-native-return.lua build/smb-crossover-mmc3.nes
```
