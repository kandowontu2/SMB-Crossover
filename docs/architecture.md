# Architecture and provenance

## Foundation and reference

[SMB1Base](https://github.com/smbstudio/smb1base) was imported at `46ff88f7d9e854db80bf8d50e5bf74340fcc64ce`. Its README and credits remain in `docs/SMB1BASE.md`. The upstream LICENSE is empty; this port does not assign a new license to original material.

The requested hosted SWF is `https://www.smbgames.be/roms/super-mario-crossover.swf`, SHA-256 `46bdcf0b60721bbe0f006cdb083f503e0312feacede6f65f2942f7a5a406b1eb`. It runs at 60 Hz with a 512x480 stage. Coordinates are halved for NES pixels. The creator's published v3 source is a different version.

Pinned constants, sprite identities, audio provenance, and known limitations are in `docs/reference/`. Downloaded references and upstream checkouts stay ignored under `reference/crossover/` and `.upstream/`.

## Cartridge and state

Both NTSC NES 2.0 targets have 512 KiB PRG, 256 KiB CHR, and 8 KiB volatile WRAM. MMC3 is mapper 4; MMC5 is mapper 5. Guest music and weapon sounds use the normal NES APU. MMC5's two expansion pulse voices play shared world tones.

| Physical 8 KiB PRG bank | Contents |
| --- | --- |
| $00-$04 | Objects, player/guest physics, levels, screen rendering, metasprites |
| $05-$07 | Base audio allocation and extra objects |
| $08 | Shared guest weapon, health, block and collision helpers |
| $09 / $0b | MM2 / MM3 audio |
| $0a | Samus and shared pickup animation |
| $0c / $0d | Mega Man / Samus metasprite data |
| $0e-$12 | Native Metroid audio banks |
| $13-$15 | Bill, Link and Simon metasprite data |
| $16 | Bill, Link and Simon gameplay |
| $17-$18 | Contra audio and wrapper |
| $19-$1a | Zelda audio and wrapper |
| $1b-$1c | Castlevania audio and wrapper |
| $1d | Shared guest world effects, audio mixer, water and character select |
| $1e | Added roster movement and pose dispatch |
| $1f-$24 | Pit, Rygar, Luigi, Bass, Ryu and Sophia metasprite data |
| $25 | Added roster weapons and collision bridges |
| $26 | Added roster register-music decoder at $c000 |
| $27-$3a | Native APU music register streams |
| $3b-$3d | Spare PRG banks |
| $3e / $3f | Fixed $8000 / $e000 engine code |

The $a000 window holds game logic; $c000 normally holds character metadata. During native roster audio both windows hold the selected sound driver and its wrapper; NMI restores the main code bank and character metadata afterward. Every MMC3 banking macro shadows its selector before writing $8000. Both NMI paths save and restore that selector, including when a main-thread select/data pair is interrupted. Dynamic MMC5 ROM-bank writes include bit 7.

WRAM contains character selection, Q8.16 movement, independent weapon pools, enemy health/stun, parallel block health/coin/terrain maps, animation state, and private audio state. SMB supplies levels, enemies, collision, camera, items, score, and progression. Returning to Mario restores his own small/big flag from his power state.

## Gameplay and rendering

`characters.s` handles dispatch; `character_select.s` opens a separate portrait screen after Start. The static title runs no player or demo logic. Background CHR banks $3c-$3f hold the menu, and a private sprite preview renders the highlighted character above its name. Mega Man's physics, weapons, palettes, environment and death have separate modules. `samus.s` and `samus_weapons.s` implement Morph Ball, beams and bombs. `roster.s` and `roster_weapons.s` implement Bill, Link and Simon. `expanded.s` and `expanded_weapons.s` add Pit, Rygar, Luigi, Bass, Ryu and Sophia, using separate movement and weapon state with the common integrator, collision and camera. `guest_powerups.s` holds the current pose and freezes gameplay for 60 frames during an upgrade.

`BillVariant` persists outside the transient roster state: Select on Bill toggles Lance without changing the twelve-slot roster or Contra gameplay dispatch. Lance has 48 source poses in `lance_metasprites.inc`, nine private 1 KiB CHR pools at logical $74-$77/$7a-$7e, and matching menu, HUD, lives and pickup colors. Every pool reserves Bill's bullet pairs. His pants share the existing world palette's red, so mushroom colors remain intact. These banks replace redundant Mega Man charge-background copies; Bass's private special poses retain their separate allocation.

Every guest feeds SMB's camera with its relative X position. Q8.16 integration supplies the actual integer displacement to scrolling. Wall contact clears fractional drift. Terrain provenance distinguishes underground ground from breakable bricks sharing tile $52. Native block activation receives the contacted cell, preserving bounce/reward alignment. Wide melee attacks probe interior columns as well as their outer corners.

Player graphics use private pointer tables so hundreds of poses do not exhaust the global 8-bit metasprite IDs. Repeated body frames share 1 KiB CHR pools. The added roster occupies CHR $d1-$e3, after the original Samus allocation, with thirty poses per power state including crouch/air attacks. Its menu deduplicates 104 portrait tiles in one 4 KiB background. Each pool begins with identical common weapon tiles, keeping shots stable across pose changes. Mega Man occupies $40-$90, compacted Samus occupies $91-$d0, and the later roster uses the available lower banks starting at $1d. Large Mega Man charges have a separate allocation.

OAM allocation rejects complete metasprites before overflow. Mario and Samus retain their established reservations and death-particle cleanup. Mega Man and every character from Bill onward allocate projectiles first, reserve their body budget, then allocate other objects. A rotation maps these logical offsets onto hardware OAM; body parts, weapons, enemies and effects all share scanline priority. Its step is coprime to the allocated sprite count so no parts are starved, and shrinking lists reset an out-of-range cursor. Their previous OAM is cleared before allocation, and flipped sprites wrap within the OAM page. Mega Man reserves 24 parts during his death burst. Bill's upgraded bullet fits one sprite; palette-compatible body colors are merged to remove overlays. The flame whip still spans a row wider than eight sprites can display fully.

Brick-fragment physics runs in the native block slots. The final metasprite pass renders the four fragments from those positions, after clearing and allocating sprites. The old direct OAM writes from block physics are disabled in Crossover builds: they were erased by the final pass and could overwrite characters whenever that pass was skipped. Fragment page coordinates and the original block column remain independent of temporary weapon-contact coordinates.

`world_firebars.s` similarly caches up to twelve native collision-part positions per actor, then renders them in the final OAM pass. Firebar art uses unused pairs $00/$02 in the shared misc CHR bank, copied from native small Mario $3c/$3e, instead of relying on the replaceable player bank. The misc mushroom pairs $3c/$3e stay intact. The C data bank is saved/restored around the draw.

`GetLevelExitSlot` searches all six actors and, if full, reclaims a noncritical actor while protecting both pole and castle flags. Both native exit producers use it. `MegaManSpringVelocity` preserves the caller's actor index; the pit check accepts signed Y pages above the viewport. Sophia applies strong release damping only after an actual A-release event, allowing an unassisted spring rebound.

Wide attacks claim one of SMB's two animation slots before activating a block. An active bounce or pending nonblank replacement cannot be overwritten. A new brick shatter may replace old debris only after committing its blank logical map cell, so neighboring question blocks keep their bounce, reward and used-block tile. Sprite palette 2 always retains the world's red/white/tan colors. Simon's black outlines share palette 3; axe blade tones use white/tan instead of taking over the mushroom palette. The separate outline can require additional sprites.

The MMC3 HUD split delays its final $2005/$2006 writes into hblank. Both normal and lag NMIs allow the mapper IRQ to interrupt native audio; otherwise long audio updates postpone the split and vertically displace the background for one frame. Scrolling tests keep native enemies active and require both final writes on scanline 31 between dots 257 and 320 on both mappers, including lag frames.

Simon retains his launch velocity while wall contact clamps his position. It resumes when his double jump clears a pipe, matching the hosted lastVX behavior. Stomping replenishes the second jump. Head collisions use the hosted brick rule: powered Mega Man and Samus's first two suits can break bricks; Bill, Link and Simon use their weapons. Samus's wave suit and Morph Ball cannot head-break bricks.

`water.s` classifies submerged/above-water state using the hosted pose's hit-rectangle height and full fractional Y position. Mario's water-only movement uses source acceleration, coasting/skid friction, paddle impulse, release friction, gravity and current forces; his dry engine remains SMB's. Mario's swim animation advances on alternating four/five-frame intervals for the source's 75ms timer. Guests retain their original ground/air input rules in water. Water gravity is selected after pose/input updates; the common 250 Flash px/s fall limit is applied before gravity. Hosted `PitVacuum` explicitly targets Mario, so guests bypass the native whirlpool routine. The water reference lists exact constants and verification boundaries.

## Graphics regeneration

JPEXS 26.3 exports the pinned SWF. Export preparation removes runtime-hidden debug rectangles and reconstructs independently animated body parts. Pillow converts reference frames into 2bpp 8x16 NES tile pairs.

```sh
python tools/reference/prepare_crossover.py
python tools/reference/build_megaman_assets.py
python tools/reference/prepare_samus.py
python tools/reference/build_samus_assets.py
python tools/reference/prepare_roster.py
python tools/reference/build_roster_assets.py
python tools/reference/build_lance_assets.py
python tools/reference/build_expanded_assets.py
python tools/reference/build_menu_assets.py
python tools/reference/build_inventory.py
python tools/reference/build_special_art.py
python tools/reference/build_bass_special_poses.py
python tools/reference/build_special_math.py
```

These optional commands require the pinned local reference/tool checkouts. Generated CHR and metasprite includes are shipped with the source.

The regular build runs `pack_chr.py` using shipped binary assets. It deduplicates
logical 1 KiB CHR banks while keeping required aligned MMC3 2 KiB pairs. Logical
body/area IDs remain stable; a fixed lookup selects physical banks. Special
weapon art preserves the native background and actor tiles in each composite
bank. The selected weapon's background icon/font bank is independent of the
weapon sprite bank, so changing the icon cannot corrupt projectile tiles.
Special-art packing shares best-fit composite families across weapons and omits
unobtainable Magma Beam/Rush pickup variants; obtainable pickup records and all
eight source HUD icons remain available. This leaves room for Lance in 256 KiB.

`inventory.s` lives in PRG $3b and `special_weapons.s` in $3c; $3d is reserved
for the other inventory migrations. Persistent owned/viewed/stored upgrades,
selection and per-item ammo live outside the transient area-clear range.
The Crossover 2.02 inventory is enabled for Mega Man/Bass while the other
characters retain their previous gameplay until their runtime weapons are ready.
The inventory HUD only appends to an empty native VRAM buffer and keeps enough
space for the native producers that run later in the update.

`BankPRGC` publishes `CurrentBankC` before writing the mapper. Every NMI saves
that value and restores it after audio, including lag NMIs. Weapon sprite data
can be in Samus's data bank while the body data is in Bass's bank; restoring
only the character's body bank would return to the wrong metasprite bytes.
The renderer rejects headers whose byte count is not divisible by four.

## Audio

Native Capcom drivers are imported from [lsmmega/mm2](https://github.com/lsmmega/mm2) at `8e378590488ce589c526f0d24ad4dee60afd14a3` and [lsmmega/mm3](https://github.com/lsmmega/mm3) at `8ecd0a9247ed17709e8cd9cc692c38288daa2bc5`; charge effects come from the pinned MM4 source identified in the generated file.

Metroid audio comes from the user's local ROM, with operand locations verified against [nmikstas/metroid-disassembly](https://github.com/nmikstas/metroid-disassembly) at `4270d57f9468daebdeea485686e31e26218a780c`. Contra and Zelda sources are pinned in `roster-audio.json`. Audio data is included inline, so normal builds need none of those checkouts.

Castlevania audio is relocated from the local ROM identified in `castlevania-audio.json`. `import_cv_audio.py` records executed instruction and indirect-pointer provenance. `emit_cv_audio.py` also follows both sides of reachable branches, covering effects layered over music; it moves channel state to private WRAM and leaves indirect pointers in shadowed zero page. This prevents the sound driver from modifying SMB state. `validate_cv_wram.py` compares original/ported APU events for 84 sound IDs over 4000 frames each.

```sh
python tools/reference/import_megaman_audio.py
python tools/reference/import_samus_audio.py
python tools/reference/import_cv_audio.py
python tools/reference/emit_cv_audio.py
python tools/build.py
python tools/reference/validate_cv_wram.py
```

The three newer guests share private driver RAM, reset on character changes. Sparse ZP shadows save 17 bytes for Contra/Zelda and 24 for Castlevania. Pause freezes driver updates and silences the APU. Contra and Zelda DPCM playback is disabled because their original fixed sample addresses belong to this port's engine.

`prepare_guest_audio.py` redirects documented native APU stores into a private register image without changing instruction widths. Timer and sweep writes retain dirty flags, preserving same-value note retriggers. The shared SMB effect engine produces a second image for block bumps, coins, item/vine reveals, fireworks, timer ticks, flagpole slides and brick shatter. It leaves the native music's frame sequencer alone. On MMC3 an active shared effect borrows its corresponding voice, then restores the native register image. Pause invalidates the output cache so held notes reload their length counters on resume.

Metroid's indirect `STA ($e0),Y` / `INY` register-loader pair also routes through the shadow image via a same-width JSR. Its helper preserves A, X, carry and the displaced INY result. Short, long and wave beams can therefore update their envelope, sweep and pitch without the mixer restoring stale music registers over the sound effect.

On MMC5, pulse effects instead use `$5000-$5003` and `$5004-$5007`, with independent enables in `$5015`. Both native pulse voices continue playing music. MMC5 has no sweep unit, so the bump and flagpole pitch sweeps use a software divider with two half-frame updates per video frame; their timing within each frame is quantized. Native noise is still shared for brick shatter. The expansion channels are muted on pause, title, reset, and return to Mario. This path has emulator coverage; no physical cartridge audio test has been performed. See the [MMC5 audio register reference](https://www.nesdev.org/wiki/MMC5_audio).

`compare_crossover_music.py`, `compare_samus_music.py`, and `compare_roster_music.py` compare hosted audio chroma with native APU renders. Their score files are build evidence, not proof of sample-perfect identity. Remaining unidentified edits/tunes are recorded in the parity audit.

The additional roster uses a compact register-stream decoder in PRG $26 with data in $27-$3a. It records native stage music, retains timer retriggers, and sends it through the same APU mixer. Luigi keeps the original SMB audio path. Optional regeneration uses `capture_expanded_music.py` and `build_expanded_audio.py`; [expanded.md](reference/expanded.md) records reference hashes, the Rygar audio-extraction fixture, three-state upgrade adaptations, and area/event-music limitations.

## Verification

`python tools/verify.py --mmc5` builds each target and runs the controller/fixture suite. Mario's 19-field, 521-frame replay must equal the baseline. Guest tests include actual pickups, lives portraits for every power state, combat, protected terrain, scrolling and split timing, native music, death/respawn, OAM overflow, and projectile allocation. Regression fixtures also cover repeated Bill stomps, complete OAM priority rotation, Link's question blocks across page boundaries, rendered brick debris, Simon clearing all four 1-1 pipes, Samus's three head-collision rules, and MMC3 register selection across regular/lag NMIs.

Simon's adjacent-block fixture tests all three whip strengths in both directions. It checks the used question block's logical cell and all four rendered background tiles, neighboring brick removal, reward emergence and the shared mushroom palette. Real-pickup fixtures also check that Bill and Simon preserve that palette through both upgrade animations.

Six water fixtures initialize the actual 2-2 room and check source trajectories, paddle/jump eligibility, release friction, surface equality and fractional crossings, fall caps, weapons, poses, water music and whirlpool eligibility on both mappers. These fixtures explicitly set state; they are distinct from controller-only route replays.

`build/verification/summary.json` records the passing cases and exact hashes. Startup diagnostics from the base engine remain in full logs. No complete all-world replay, PAL verification, or physical hardware test has been performed.
