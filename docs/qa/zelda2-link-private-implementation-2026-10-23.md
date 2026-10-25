# Zelda II Link private integration packet — 2026-10-23

Playable private alternate, ready for contextual integration after Darkwing. Main source has not been changed by this agent. This is an original Zelda II profile adapted to SMB scenes; it is not a Crossover 2.02 character or a claim of complete original-game equivalence.

Candidate: `build/verification/zelda2-link-candidate-agent/zelda2-private.nes`

SHA256: `0d076ad7c082508d6659a109cc750f3ce8fd736e38a37ec2c7854c69848f16dc`

The exact common baseline is frozen `build/checkpoints/expanded-profiles-lr/source.zip`, expanded ROM SHA256 `3b90274e09eac19d8d12bd973c15b4a9ceedce0f742a21665d7f88683b32b0f3`. The earlier KY renderer/core evidence remains historical. Production MMC5 expansion code, Proto modules, and the shared ExRAM initializer are copied exactly from LR; Z2 requires no diagnostic probes or altered mapper behavior.

## Implemented controls and progression

Highlight Link and press Select to switch Link / Zelda II Link; family ID remains 4. The private front end shows the actual native alternate sprite and name, including the lives screen. Root should compose these menu cases with the shared registry and Darkwing rather than replacing `character_select.s`.

* D-pad walks/crouches; A jumps; B uses the original timed sword sequence. Learned Downthrust / Upthrust use Down / Up in the air. Full health permits the original sword beam. Fire changes sword attacks to fire projectiles, with the original Attack-level projectile-slot threshold.
* Start pauses. Up/Down chooses a spell; Left/Right switches the spell and stat panels. On the stat panel Up/Down chooses Attack/Magic/Life/Cancel and A purchases the chosen affordable level. Select casts the selected learned spell during play and pays its native MP cost.
* The two HUD rows show HP/MP, selected spell and EXP, or the paused levels/costs. Original Link's items and ammo are rejected in Z2 mode; its owner-4 inventory is preserved.
* Attack/Magic/Life each run from original level 1 through 8. Native threshold tables, damage/cost tables, inclusive HP/MP caps, the one-unit-short casting exception, level-8 extra lives, EXP tick arithmetic, six-kill weak/strong counters, jar distributions, and meter refill cadence are installed. The actual EXP register retains native 16-bit wrap; only SMB's queued delivery accumulator saturates.
* Shield halves damage and changes tunic color; Jump uses the original jump modifier; Life queues native recovery; Fairy uses original native sprite phases and eight-direction speeds; Fire enables the native projectile form; Reflect turns contacting Bowser flames into outgoing shots through the translated original shield rectangle; Spell transforms eligible SMB enemies to Goombas; Thunder applies the original 50 damage to eligible active enemies. Enemy correspondence and immunities are SMB adaptations.
* Deterministic physical upgrade rewards follow the separately frozen `progression-policy.json`: Jump, Downthrust, Upthrust, Fairy, Shield, Life, Fire, Reflect, Spell, Thunder, Glove, then HP/MP containers up to eight each, then restoration. Owned or pending unique rewards are skipped. A mushroom additionally supplies practical Life recovery. Nothing is granted by spawning or rising: collection uses the native actor collision path after visible emergence.
* Drops are six independent visible pickup slots. Native jar/bag reward amounts and counter rules are retained; their world placement, gravity and SMB collision are an explicit adaptation.

## Source and art provenance

[Nintendo's original English manual](https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NAASE.pdf) and the user's original USA cartridge dump are the primary rule/art sources. The retained [reverse disassembly](https://github.com/FiendsOfTheElements/z2disassembly/tree/c4c3a4c7d4156b41f54f726dc40644d45812ad29) is pinned to commit `c4c3a4c7d4156b41f54f726dc40644d45812ad29` and was independently assembled and compared with that dump. It has six substantive unrelated byte differences plus padding/reset-tail differences; it is not globally byte-identical. All selected numeric/control/renderer ranges used here were authenticated against the original binary; exact range evidence is retained under `original-source-authentication/`.

Original ROM SHA256: `9fca03064a5113e6a92f550d9f42bac9ac1ae248a84df1f653d7cd7f76a1803d`.

Art is extracted by executing the original ROM renderer at EBF0, then repacking the exact original tile pairs, palette attributes, flip bits and relative positions. The only positional conversion is source X+8 to the port's player origin. No new painted sprite or extra outline layer was used. 27 body/fairy pages and one native item page occupy CHR 308..335; 336..339 remain unused.

The sword rectangle test executes both original EBF0 and E9A2, then compares the linked port rectangles. It caught and fixed the initial horizontal and left-facing upward-reach errors. Native source positions, rather than an assumed common sword box, determine reach.

## Evidence and scope

All current numerical receipts name the candidate hash above.

| Check | Result | Scope |
|---|---:|---|
| RPG rules | 87,251 linked CPU calls | Packed levels, costs, HP-zero/underflow, EXP overflow, all jar queue byte-wrap boundaries, containers, refill and lifecycle |
| Original motion comparison | 14,342 cases | Original ROM and retargeted walking/input/jump/sword/integration produce identical tested gameplay writes; CPU cycle counts differ |
| Original sword rectangles | 48 cases | Standing/crouching/up/down, both facings, multiple positions, unclipped source rectangles |
| Full DrawAll rendering | 324 cases + physical pickup negative | Native records/physical CHR match; exactly two extra pickup sprites, no old-Link upgrade garbage |
| Family/variant ownership | 3,584 cases | Only selected family 4, variant exactly 1 activates Z2 |
| Integrated components | 625 linked calls | All 11 unique rewards, full 48-update rise without auto-grant, no pending duplicate, all eight remaining containers, UI rows/navigation/casting/purchase, old-item rejection, two-hit Goomba and single EXP, beam/fire, actual reset/death bridges |
| Native Mesen | 1,700 frames; 1,692 NMIs, 1,608 IRQs | Real controller menu selection, entry, movement/jump/sword; explicitly authored pickup/casting/fatal contact/new-life arenas; full NMI A/C bank/shadow checks |

Native screenshots and log are in `native-interactions-v2/`. Review of v1 found old `SpecialDrawShots → RemainingDraw` treating private reward tags as old weapon-table indices. The v2 packet adds an equal-size cold dispatch hook to suppress that old draw path only for Z2; the corrected native screenshot and complete DrawAll pickup sprite count are retained. The failed v1 visual evidence remains available.

These are bounded functional/component checks. They do not prove a full campaign, water/maze/flagpole coverage, natural acquisition of the first four rewards by 2-2, or every spell in a natural controller route.

## Resources and integration instructions

`incremental-merge-manifest.json`, `incremental-merge.patch`, and `merge-staging/` form the adoption packet. There are 23 new files and 18 contextual shared-file changes. Copy only new owned files directly. Merge shared hook hunks into the current DD/registry tree; do not copy old complete game files over it.

* PRG 69/A owns logic, 70/C owns body/item records, and 71/A owns original motion. Bank 69 uses about 6.2KB; 70 uses 814 bytes; 71 uses 1,502 bytes.
* Fixed SRAM `$73F8..$73FF` is eight aliases only. The initialized 16-byte RPG record occupies owner-0 InvAmmo; the owner-0 sentinel audit proves generic Mario paths do not consume this row. Owner-4 Link ammo remains separate. Existing SRAM allocations are not shifted.
* Transients use exactly ExRAM `$5E00..$5E7F`; no obsolete shot-fraction aliases remain. Shared LR `$5104=2` and `X5InventoryInit` own fresh-game ExRAM clearing. Private `Z2GlobalInit` chains the LR Proto initializer.
* Bank-4 body/own-shot guard is `$BFA9..$BFCB`, 35 bytes. Its inactive `JMP RosterDrawShots` must become the agreed `JMP DwDrawGuard` in the combined tree. The existing `farcall SpecialDrawShots` is retargeted at equal size to `Z2SpecialDrawGate`; inactive mode tails to the original. No additional resident bytes are consumed.
* Native existing inventory leaves are outlined with exact byte spans. Root must compose any Darkwing consumer rules before installing the three narrow InventoryLegacyClassic/Supported/Hurt wrappers. Old public entry addresses outside intentional cold-menu changes remain fixed. `ModernRules` is an outlined private internal label; flat debug-label movement is documented in the renderer receipt.
* Standard builds were not rebuilt by this private freeze; all gameplay hooks are conditional on `ENABLE_MMC5_EXPANDED`. Root should rerun the standard byte-identity controls during composition.

## Remaining polish / explicit adaptations

Inherited Zelda I music/SFX remain; original Zelda II audio is not installed. Some beam/hurt SFX still rely on the existing sound driver. Fairy/item palette-1 colors require a real original-scene palette comparison; native body colors are authenticated. Non-pit death displays the authentic hurt frame with the inherited Link death duration, while pit deaths hide the player; the original Zelda II death scene/CHR context is not recreated.

SMB enemy HP/EXP/classification, restoration pickup motion, spell effects on SMB enemy classes, pause/HUD layout, NPC-taught moves delivered by upgrade blocks, and area-scoped spell clearing are documented adaptation policies. Reflect currently handles Bowser flames, not every possible enemy projectile class. Default shield defense against ordinary original-Zelda projectiles is not meaningful for all SMB hazards. The stat Cancel selection currently defers automatic level-up prompts until a later manual purchase, rather than recreating original next-threshold prompt selection. Original walking/jumping routines are authenticated in isolation; their SMB terrain, swimming, camera, and death-scene adapters are not claims of universal original-game parity.

No level/helper/Bass changes or main-source mutations are part of this packet.
