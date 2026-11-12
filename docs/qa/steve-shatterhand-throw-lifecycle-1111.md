# Shatterhand companion throw lifecycle

The traces use Shatterhand USA `fbdfaab40aedda270d7473be37566b59e68811d932740c105d84fa6b1a7f19e1`. The crossover baseline was installed `235de3ed2487cd3f93c695e1eb2ceec55c172cede3cb6d98c5309afbc7cfbe38`.

| Original location | Observed behavior |
| --- | --- |
| PRG12 `$9965`, `$99E6`, `$9A2C`, `$9A89` | Fresh B during state 5 throws and leaves crouch state 3. Fresh B during state 6 or 7 throws and enters airborne state 1 through `$A300`. Set bit 7 of robot selector `$065C`, cue `$0C`, and signed Q4 horizontal speed `$60` or `$A0` in `$063C`. |
| PRG13 `$A588`, `$A740`, `$A777` | The thrown selector dispatches animation `$14` and outbound motion. Each unobstructed outbound update moves the same robot by six pixels horizontally with constant Y. The outbound test uses the pre-step Q4 position and the half-open camera range `[X, X+256)`. |
| PRG8 `$83E2`, `$841D`, `$84CD`, `$849E` | The enemy contact path tests robot slot 12 after age `$06EC` reaches `$0C`. An eligible overlap writes the hit receipt to robot ID `$060C` bit 7 before checking enemy cooldown. Pose `$015E` or `$015F` yields two damage from `$8A19+2*pose`. The enemy HP gate starts at age eight. The same overlap can damage the robot. |
| PRG13 `$A761`, `$A75D`, `$A786` | A surviving contact receipt starts the return timer at `$FF` and requests cue `$0D`. It moves on the following update. A camera miss instead seeds `$80` and increments the timer only on odd `$0C` updates. The hidden branch pins X high to the appropriate camera edge, preserves X and Y low, clamps Y high only when above camera top, and clears the displayed pose and animation step/delay. |
| PRG13 `$A7C0`, `$A80F`, `$A830` | At `$FF`, steer return angle `$069C` by two units toward PRG12 `$8E54` via `$C051`, and apply donor polar radius row `$50` in Q4 without the ordinary orbit's fourfold scaling. The contact/miss transition seeds `$00` for a left throw and `$20` for a right throw. The fixed `$C051→C101` wrapper writes Y to `$90`, replacing the player X low byte for the direction calculation. Actor action `$14` leaves Y at 2 when its sole `$7F`-delay row loads, and at 1 otherwise. The AAB left trace diverges if the port skips that wrapper behavior. |
| PRG13 `$A806` → PRG12 `$9361` | Reattach if the X high bytes match and the Y high bytes match or differ by one, or if direction lookup returns `$FF`. Set life `$06EC` to `$FF`, clear selector bit 7, reset ten private motion/animation bytes, and set orbit angle `$30`. Keep actor ID and weapon selector. There is one zero-pose update before the normal companion draw resumes. |

If incoming damage is lethal, PRG8 `$848B` writes actor ID `$FF` and timer `$20`. The next general actor update uses PRG13 `$A4C9` destruction. It bypasses the surviving-contact return branch. The controller round trips below exercise surviving actors.

## Checked traces

The bounded stdin probe `build/steve-throw-natural-return-1111` used `trace_steve_shatterhand_donor_1111.boot`, set only the completed token pattern to `$15` or `$25`, let the cartridge spawn the companion, then used controller input. After the grant, it held Down for three updates, Down+A through update 55, then A through update 90. AAB was faced left with a one-frame Left input at grant-wait update 135. Throw age zero is the fresh B update.

| Route | Last outbound movement | Offscreen transition | First homing | Reattach | Ordinary pose |
| --- | --- | --- | --- | --- | --- | --- |
| AAA right | 21 | 22, X516/Y359 | 277, X494.125/Y360.25 | 300, X367/Y393 | 301 |
| AAB left | 17 | 18, X275.875/Y359 | 273, X281.75/Y360.25 | 295, X400.375/Y400.75 | 296 |

Both misses took 255 updates to first homing with the observed clock phase. The code gives 254 or 255 depending on the retirement clock parity. No new token or spawn countdown runs. The first ordinary Laserbot update may reuse `$062C` for weapon scratch after the thrown flag clears.

The directed stdin probe `build/steve-throw-contact-matrix-1111` called the original PRG8 `$83E2` with an overlapping robot at pose `$015E`, actor age 60, robot HP 16, and enemy HP 6 unless otherwise noted. It then entered original PRG13 `$A740` for surviving receipts. Ordinary overlap left enemy HP4 and robot HP15. Enemy cooldown age7 left enemy HP6 and robot HP15 and still triggered return. Enemy HP2 reached zero with native defeat state `$84`. Robot HP1 entered actor ID `$FF` and timer `$20`. Robot age11 and an out-of-bounds position produced no contact. Enemy flag `$21` blocked damage to the enemy and blocked return while the robot still lost one HP. The three surviving receipt cases left position fixed during `$A761`, set timer `$FF`, seeded angle `$20`, and requested `$0D`.

Both probes exited zero. Their commands used `python -B tools/audit/run_bounded_build_v1.py --output build/steve-throw-natural-return-1111 --max-files 1 --timeout 110 -- python -B -` and `python -B tools/audit/run_bounded_build_v1.py --output build/steve-throw-contact-matrix-1111 --max-files 1 --timeout 60 -- python -B -`. All ROMs, fixtures, and traces stayed in memory.

## Detached source proof

`tools/reference/steve_shatterhand_throw_1111.s` links at 654 bytes, including a 64-byte direction table derived from PRG12 `$8EEA` by exact octant symmetry. The worker SHA-256 is `f58fe49ea0b0343bb7e0a6e9af96ca14cef59c2d766f166a916623d719f9471b`. The source shares the existing expanded donor polar table and lift animation leaf. It leaves enemy detection, fatal robot destruction, player recoil, and native scene admission to the host bridge.

`tools/audit/check_steve_shatterhand_throw_1111.py` compared 529 direction inputs, eight directed contact transition and homing updates, and all 597 original actor updates across the two controller round trips. It checked actor state against the original `$A740` input and `$A523` return boundary. The two native traces run the fixed `$C051` wrapper. The directed fixture uses its displaced target-byte write and directly enters already-mapped PRG12. This is detached proof. The installed crossover build still needs live throw integration.

A separate bounded stdin invocation `build/steve-throw-launch-1111` ran the same checker's `begins()` against PRG12 `$9965`, `$99E6`, and `$9A2C`. It matched selector, timer, speed and cue for states 5, 6 and 7, both facings and both companion selectors in 12 cases. The 654-byte worker hash was unchanged. Player recoil belongs to the host bridge.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-throw-detached-1111 --max-files 1 --timeout 120 -- python -B tools/audit/check_steve_shatterhand_throw_1111.py
```
