# Added roster

Pit, Rygar, Luigi, Bass, Ryu Hayabusa and Sophia III are playable, giving twelve characters. They have dedicated graphics, menu and lives portraits, movement, attacks, power-up transitions, collision, scrolling and respawn. The menu shows all twelve portraits in two rows and names only the highlighted character beneath its color preview.

## Reference versions

Luigi, Bass, Ryu and Sophia use the default NES bitmap sheets and character constants from the pinned **Crossover 2.02** SWF. Its SHA-256 is `6374c72426556bfc3cc16f7594ce4443a5867fe2d367514136c99cc8458b70af`. The extracted scripts and downloaded reference files are optional local regeneration inputs, excluded from source control.

Pit uses the creator's unfinished published v3 character code for the 180 Flash px/s walk, 500 px/s jump, 700/400 px/s² gravity, two-arrow limit, upward firing and arrow upgrades. His pixel art comes from controller captures of the user's original Kid Icarus ROM. Rygar uses controller-captured original NES graphics with an adaptation of the returning Diskarmor, crouch, jump and increasing weapon reach. These two are separate playable additions; they were not part of the 2.02 roster.

Exact reference hashes are in [expanded.json](expanded.json). Art packing and its sprite/CHR budgets are in [expanded-assets.json](expanded-assets.json); optional regeneration is implemented in `tools/reference/build_expanded_assets.py`.

## Movement and weapons

| Character | Implemented abilities |
| --- | --- |
| Pit | Ground jump, crouch/air arrows, two-arrow limit, upward arrows, long/fire arrow forms, Select hammer with ground/crouch/air poses; flower-level winged flight with a one-second budget recharged on landing |
| Rygar | Ground jump, crouch/air attacks, four-pixel Diskarmor extension/retraction attached to the hand, wall-triggered return, increasing reach, once-per-enemy hit masks |
| Luigi | Mario's native walk/run, jump-release, climbing, spring, collision and death routines; modestly higher dry jump and slightly lower braking traction; source small/large atlas; bouncing fireballs that preserve blocks; Mario's underwater paddle and whirlpool behavior |
| Bass | Initial step and instant walk/stop, dash/dash jump, one second jump, jump release, held rapid fire at 75 ms intervals, seven firing directions with ground/air poses, three/four-shot limit, non-piercing 17-damage default buster, no charge mechanic |
| Ryu | Source sword/throw phases for standing/crouch/air/wall, shuriken, source windmill reversal and spring tracking, wall cling, up/down wall movement and directional wall jumps |
| Sophia | Fresh-press three-shot cannon, upward cannon, initial gravity-free jump rise, underwater steering/damping/drift, timed hover consumption and regeneration, missile/homing missile adaptation, wall climbing and ceiling attachment/release |

Most additions retain the port's **three-state mushroom/flower system**. Bass now has separately acquired weapons, per-weapon energy, selection and inventory recovery; Mega Man shares the core while its own special art and Rush need more work. The other inventory migrations, selectable skins, Ryu's full ninjitsu set and Rygar's adventure items are incomplete. Quantized source movement rules have independent checks; native collision, Sophia attachment geometry/homing and Rygar's larger traversal jump remain adaptations. Pit and Rygar have adapted underwater movement so they remain playable in SMB's water stages. See [Bass's inventory update](../qa/bass-inventory.md) and [roster corrections](../qa/roster-fixes.md).

Luigi now uses Mario's actual movement engine, as requested. His dry initial upward velocity gains 51/256 pixel per update and ground braking is reduced by one eighth; acceleration, maximum speeds, gravity and jump release remain Mario's. Measured standing/running jump heights are 73/90 pixels, compared with Mario's 66/83. Swimming, whirlpools, springs and climbing use Mario's behavior without these dry modifiers.

The other added guests feed the existing Q8.16 integration and native SMB collision/camera code. Ryu and Sophia receive explicit wall-contact state from the guest wall clamp. Ceiling attachment requires a solid map cell above Sophia and drops when that support ends or the player releases with A/Down. Luigi preserves his small/big collision height. All six traverse the four native 1-1 pipes in the enemy-suppressed fixture.

Pit, Luigi and Sophia fire on every fresh B press while their projectile pool has room; their shooting-pose timers do not add a firing delay. Held B does not auto-fire for these three. Bass retains his separate 75ms automatic cadence.

Bass's walk now uses the normal walk cells on row 2 of his NES skin, with a separate initial-step pose, then a 1/2/3/2 cycle at six updates per pose. Rygar uses fresh native frames 302/309/316 in a three-pose cycle at seven updates per pose. His artwork retains the native logical origin from `$0512` and one-update OAM staging, so extending an arm does not re-center the body. Both restart their animation on a fresh walk or reversal and stop on idle.

Pit activates flight by releasing and pressing A again in the air at flower power, then holding A. It supplies 1.5 NES pixels/update of lift for up to 60 active updates. Releasing A pauses consumption; another press can use the remaining budget. Landing, including a jump on the next update, restores the budget. It cannot be activated submerged or while climbing; power loss cancels it. The two wing phases include horizontal/upward shooting poses. A predictive head check preserves solid ceilings during continuous lift. This is the user's requested new ability, not a source-parity claim.

The [special-button audit](special-attacks.md) records the original S actions and current missing inventories. Bass's mushroom raises the buster cap from three to four; further blocks reveal his seven special weapons and Energy Balancer individually. Select cycles owned weapons, while paused Left/Right cycles in both directions and paused Select returns to the buster. The HUD shows the source weapon icon and remaining energy.

Projectiles allocate before enemies and participate in the full OAM priority rotation. Rygar uses the original single chain sprite, twelve pixels behind the disk center. His unpowered throw follows the measured original offsets and catches before reaching the body; mushroom/flower reach remains an adaptation. Frame tables have stable weapon tiles across body-bank changes. Palette 2 retains the world's red/white/tan colors in every character. Bass's repacked body poses fit eight sprites per scanline when alone, and his orange buster uses one sprite. Ryu's source blade/wave parts use the available weapon palette; his current full pose set peaks at seven sprites per scanline. Crowded scenes still encounter the NES eight-sprites-per-scanline limit. Empty metasprites now return safely without modifying OAM.

`capture_pit_rygar_attacks.lua` records the original games' ground, crouch and airborne graphics with controller input and read-only OAM/CHR inspection. Pit has separate airborne bow/hammer poses; his crouching bow shot is an adaptation combining native crouch and bow-arm pixels, since original Kid Icarus does not shoot while ducking. Select activates the hammer so Down+B remains available for crouching arrows. `capture_rygar_motion.lua` adds a fresh original-game motion capture, including the extended-arm standing throw, correct disk tiles and stance heights. Weapon regression fixtures cover both directions and all three upgrades, continuous four-pixel return steps, actual chain OAM/scanline usage and airborne attacks. See [the Bass/Rygar audit](../qa/bass-rygar-audit.md) and [Rygar measurements](rygar-motion.json).

## Audio

The new register-stream player uses native APU music captured in Mesen. It stores changed register values and timer retriggers, then feeds the existing music/SFX mixer. It does not play PCM samples or run another game's gameplay code in the port.

| Character | Current stage theme |
| --- | --- |
| Pit | Kid Icarus first stage |
| Rygar | Seven native songs assigned to outdoor, water, underground, castle, bonus, intro and star/hurry selections |
| Luigi | Existing SMB music and SFX driver |
| Bass | Mega Man 10, Strike Man (embedded NSF track 13) |
| Ryu | Ninja Gaiden, Unbreakable Determination (embedded NSF track 15) |
| Sophia | Blaster Master, Area 1 (embedded NSF track 3) |

Pit was captured with ordinary controller startup. Rygar's original gameplay runs inside NMI and eventually loses the life while standing still. Its reference extraction therefore replaces the emulated NMI vector after startup with a stub that calls only the original audio driver and bank selector; the original file is unchanged. This is an audio-extraction fixture, not a controller replay of the port. The final reference screenshot remains in the opening stage rather than returning to the title.

Bass, Ryu and Sophia select their pinned 2.02 area/event playlists. Rygar now uses seven distinct songs from the pinned original ROM, extracted by invoking its native `$e000` driver and `$0740` song queue in the frozen-world extraction fixture. His area assignments are port adaptations, recorded by native driver ID rather than guessed soundtrack titles. All seven have verified full loop periods; the longest encoded period is 4,608 updates. Rygar retains SMB death/victory event cues. Pit retains one native stage theme and SMB event cues; Luigi retains the native SMB driver.

Fifty-six area/event selections are checked against 400 captured native register updates each, including source silence and fallback selections. Rygar's castle song also has a 4,500-update check across its 4,032-update loop. The streams use verified command compression; other unverified looping songs still restart after 5,400 updates. Writes are quantized to video frames and DPCM is omitted. [Playlist sources](expanded-playlist.json) and [encoding limits](expanded-playlist-encoding.json) distinguish these paths.

Bass's weapon, hit, damage, life, landing and death effects use the imported MM3 native effect engine over his MM10 playlist. Its persistent effect image is separate from held music notes, and released channels restore music timer/length state. Other added characters still have character-specific effect gaps. Common block, coin and world effects use the shared mixer; MMC5 moves those pulse effects to its two expansion voices. `build_expanded_audio.py` now forwards to `build_playlist_audio.py` so the legacy regeneration command cannot overwrite the current encoding format.

## Verification

Each new character has checks for menu startup, movement, jump, real pickups, three lives portraits, upgrade animations, actual 2-2 water initialization and trajectories, native enemy defeat, block behavior, protected terrain, NMI preservation and respawn. Separate tests exercise source normal-death sequences, Bass's dash/second jump and aiming/cadence, Ryu's wall jump and windmill equations in both directions, and Sophia's hover/ceiling release. The windmill suppresses damage during continuous contact and can hit again on re-entry.

World-SFX tests check physical APU/MMC5 output, channel restoration, simultaneous effects and pause/resume. Luigi uses the native SMB driver. Fixtures use explicit state setup and are not controller-only clears or hardware tests. The [added-character 1-1 audit](../qa/world-1-1-expanded.md) retains its historical videos. Luigi jump snapping, Ryu ground poses in air, and Sophia's missing hover artwork have since been corrected; the hover sound and full attachment transitions remain open. New route attempts retain their own ROM hashes and are accepted only after an independent fixed-input replay.
