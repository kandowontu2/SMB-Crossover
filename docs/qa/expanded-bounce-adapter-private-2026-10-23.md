# Expanded roster spring and stomp adapter

Private candidate: `build/verification/expanded-bounce-mu-candidate-agent`. Baseline is frozen MU plus the exact canonical MV Mike adoption. No main files or the separately frozen level/platform packet were changed.

The old spring routine indexes two ten-entry halves using `SelectedCharacter - 3`. Expanded IDs 13–19 therefore read the boosted half for normal springs or run beyond the table. The new expanded-only dispatch admits exact family IDs/variants, rejects unknown raw IDs, and leaves the original families' spring/bounce paths unchanged. Vic Viper remains a flying profile and does not index the platforming table.

New platforming profiles use the already installed Mario-source spring policy: 400/950 source units (about −3.333/−7.917 NES pixels per update), and the existing 300-unit stomp bounce (−2.5). This is an explicit SMB-scene adaptation, not an assertion that these characters' original games had identical springs. Each owner's format is respected:

- Kirby/Mac use `MmVY`; Kirby's hover/jump-rise override is released.
- Zelda II Link also receives native airborne state and its own velocity/gravity fraction.
- Chip/Dale receive upward-positive Q8.8 velocity. A local release predicate prevents the original short-jump clamp from canceling external impulses while A is physically released. Actual input memory, carry/throw state and cooldowns are unchanged.
- CV3 variants receive a temporary Q8 ballistic trajectory with ¼-pixel gravity and their existing 6/7-pixel fall cap. Their original jump-table index stays on a valid terminal row while the external trajectory owns vertical movement. Attacks and input state are retained.
- Mike uses its existing ballistic path after its authored jump-table mode is released. Native ceiling correction is imported. His own Y=16 clamp is respected: its stale negative exported speed must not be imported again, or a boosted spring can pin him at the HUD.
- SMB3 Mario/Luigi receive signed Q4 velocity directly. Native −12 cannot fit that format and would wrap to +4; the chosen bounded policy fits both spring strengths.
- TMNT receive native Q8 velocity/stage values directly. Turtle selection remains untouched.

Original Mario/Luigi, Mega Man/Proto Man, Samus, Bill/Lance, original Link, Simon, Pit, Rygar, Bass, Ryu, Sophia and Scrooge/Darkwing retain their previous paths. This patch does not revise their spring tuning or source-game movement.

## Integration contract

The new `X5_BOUNCE` code occupies physical bank 86, `$A000..$A3D0` (977 bytes). The Chip release trampoline occupies 19 bytes at bank 81 `CD_MOTION` tail `$A2EC..$A2FE`. Its old zero-page `LDA` + `AND` predicate is four bytes; the replacement is `JSR` + `NOP`, also four bytes. No existing PC moves.

Only existing resident farcall targets are retargeted: spring, stomp, the high-family movement entry and the UI entry. CV3's existing cold horizontal farcall target is retargeted at the same size. No PLAYER, fixed-bank or bank-4 tail growth occurs. All MV public code/SMC/SRAM addresses compare unchanged.

Six root-approved ExRAM bytes `$5FF0..$5FF5` hold owner, Q8 velocity, area, life and packed world/level identity. Cleanup runs on owner change, ground, ceiling, death, life, area/world/level or gameplay-engine departure. It never writes an inactive profile's transient overlay. Fresh-game/cold initialization already clears this ExRAM range.

**Root composition with Mac MW:** the private MV UI fallback is `VvUiDispatch`; change the new wrapper's tail fallback to `LmUiGate`. Its private movement fallback is `JnMovementDispatch`; change that tail to `LmMovementGate`. Retarget the existing high-family calls currently naming those Mac wrappers to the new wrappers. Keep the low 3–5 CV3 resident entry unchanged. These are contextual target substitutions, not whole-file replacements. Level/helper changes are disjoint.

## Evidence

Final private ROM SHA-256: `7d78bc07878719c91e3777634d494940f25a7107411561936189497965f3ea27`.

Linked checks pass 20 normal/boosted launches across ten identities, ten stomp launches, 104 original-wrapper register/RAM differentials, all 236 invalid raw IDs, 24 lifecycle counterexamples, 288 CV3 ballistic updates, and the Mike top-clamp regression. Public wrappers retain native enemy/spring X and meaningful processor flags.

The final real-Mesen fixture passes **27 arenas**: 18 actual normal/boost spring animation/contact launches and nine Easy Goomba stomps, all returning to the real seeded floor and clearing ownership. It covers Zelda II Link; Grant/Sypha/Alucard; Kirby; Chip; Mike; SMB3 Mario; and TMNT. Every boosted spring rises higher than that profile's normal spring. Both native spring and enemy slot X are checked. The run completes 2,454 frames with 2,446 NMIs and 2,392 IRQs, checking actual A/C-bank restoration. Setup is injected RAM; no campaign or video claim is made.

Mac ID15 has linked shared-Mario launch evidence in this MV-based candidate. Actual Mac is absent from this private baseline. The complete native fixture accepts `INCLUDE_MAC=true` for the parent's composed MW build; it adds normal spring, boosted spring and stomp arenas using the actual installed Mac profile.

Rejected fixture revisions remain retained: the first Goomba origin was incorrectly seeded at192 rather than the native184; the first stomp-height threshold demanded too much height from the 300-unit bounce. They did not justify game changes. The later Mike boosted-spring pin was a real adapter defect, fixed by the own-clamp guard. Its pre-fix native trace and component receipt are retained separately from final evidence.

Limits: these are normal movement-mode interactions, not exhaustive tests of every copy power, flight spell, transformation or weapon action. No original-game physics equivalence is claimed for the new cross-game spring trajectories. Standard MMC3 and ordinary MMC5 behavior is conditionally unchanged; the expanded dispatch is not compiled there.
