# SMB3 Mario / Luigi: private playable integration packet

The private expanded MMC5 build implements raw character17, portrait slot16, with Select choosing SMB3 Luigi. Both identities share the original NES SMB3 movement and graphics; the original palette changes distinguish them. Main source was not edited.

Candidate: `build/verification/smb3-mario-candidate-agent/smb3-private.nes`.

SHA-256: `186c2537ddbab65e5abe1a3bb2d4c0e6810f37a98faae74171b1774e4c58d3b9`.

## Authority and scope

The [Southbird SMB3 disassembly](https://github.com/captainsouthbird/smb3), commit `09b1bd81a788de8ceec664a34094e84ddb463117`, rebuilt PRG and CHR byte-for-byte against the local USA Rev1 ROM. Only its iNES header differs. Original ROM hash: `1ddc4b429490e298c05fa70389034107c0cb50f671c7c1baaa3f228224afc2e9`. Credit: https://sonicepoch.com/sm3mix/ . The [Nintendo manual](https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NAACE.pdf) supplies the player-facing controls. Authentication and relocation receipts are retained beside the candidate.

The controller, acceleration, fractional integration, jumping, swimming, animation selection, seven-bit power meter, tail wag, flight and statue routines retain the authenticated source instructions and order. Their external room/terrain/PPU services are explicit SMB adapters. This is not a claim that every original object, slope, audio track or collision response has been ported.

## Playable behavior

| Form | Controls and behavior |
|---|---|
| Small / Super | D-pad movement; B runs; A jumps. Original SMB3 speed, acceleration, traction and variable jump rules. |
| Fire | B edge launches a fireball. Original two-slot launch, velocity and bounce timing; enemies use SMB equivalents. |
| Raccoon | B tail attack; repeated A slows descent. Reach full P and jump to fly; repeated A flaps. Text P0–P7 exposes the actual seven charge bits. |
| Frog | Original land hopping and underwater D-pad/A controls. |
| Tanooki | Raccoon controls plus Down+B statue; release Down to return. Native statue timer/pose/palette and landing contact protection. |
| Hammer | B edge throws a hammer. Original two-slot timing, fractional horizontal motion, directional player-speed inheritance and gravity. |

Small characters receive a mushroom from an eligible block. Powered characters receive a random Fire, Leaf, Frog, Tanooki or Hammer reward, implementing the user's requested random forms at flower positions. Each uses an authentic distinct original item icon. A repeat is possible; this random block policy is an adaptation, not original SMB3's fixed item placement or a Crossover2.02 rule.

Rewards occupy real native powerup actors. They rise for48 updates, retain background priority while emerging, and cannot collect inside the block. Mushrooms begin native SMB walking after emergence; suits remain stationary. Ownership changes only on physical collection. Full enemies do not get overwritten to create rewards.

Small-to-big growth and big-to-small shrinking use the original47-tick GrowFrames sequence, including its alternating original CHR pages and reverse shrinking order. Higher suit loss uses the original23-tick poof. The source two-sprite poof replaces the body. Damage uses USA progression: higher suit→Super→small→death, with113 updates of protection and the source two-tick blink. Native death/life and room transitions reset the active overlay; the persistent suit survives ordinary room changes and resets on death/fresh game. The menu variant survives Start initialization.

## Graphics and collision

Body tiles are authentic original CHR. Native frame OAM is converted losslessly into this engine's record format; the four unavailable Kuribo-shoe frames are not exposed. Somersault records include the source horizontal adjustment and both vertical orientations. The portrait and live colored preview use actual source art.

Source flat terrain probes use big head6, small/ducking head16, upper sides14/20, lower sides27 and feet32. The initially proposed10/20 values were low-clearance probes; the implementation was corrected after checking the actual terrain tables. Upper source contacts separate vertically before native side probes, and bypass only the native head-admission heuristic. They do not temporarily change the player's X or invent a block origin.

Source enemy-contact boxes are small/ducking left4,width8,top17,height13; big left3,width10,top5,height25. SMB enemy definitions, armor classes, scoring, brick effects, pipes and terrain remain host adapters. Tail collision uses source phases12/9, a10×15 rectangle at Y+16 and source X offsets17/−10. Its exact-cell block transaction excludes terrain-backed bricks and preserves an adjacent question block. Fireballs do not activate question blocks or break bricks; hammers ignore terrain, as in the source.

Body and item palettes queue only when their state changes. Initial colors and portraits force initialization. There are no per-pose palette writes that could permanently block `BlockObjMT_Updater`. No opaque black is written to mirrored universal color3F10. Item icons use the original inventory highlight colors; original effect pixel indices are remapped losslessly to share that palette. Simultaneous mixed items/effects share its current highlight, an explicit NES palette compromise.

## Verification

- Original/relocated controller:16,800 updates,168 scenarios,76 watched fields,100,800 linked calls; all seven forms, two directions, dry/water and12 input policies. Empty head-query, render/palette and periodic grounding are declared adapters in this component proof.
- Original/relocated projectile kernels:9,780 comparisons across60 scenarios, including slot exhaustion, hammer speed inheritance, fractional motion and gravity. Host contact/page carry are tested separately.
- Linked actual metasprite engine and MMC5 publisher:1,190 OAM/physical-CHR cases. All ordinary form/frame/facing records plus source somersault orientations. No empty-render pass is accepted.
- Linked core:1,849 checks /3,249 calls covering source body boxes, head/side page boundaries, no query X displacement, side-counter preservation, change-only palettes and queue-full rejection, physical collection/death and old192-byte ammo/inactive-overlay sentinels.
- Native Mesen:1,000-frame ordinary controller selection/Select Luigi/entry/walk/jump check. Separate3,400-frame authored interaction arenas cover all six actual head-hit block rewards, final used-cell and neighbor contents, emergence coordinates, collection, fireball kill, hammer, Frog hop, statue/release, tail enemy/exact brick, full-P seeded controller flight, damage/death/new life and old ammo. The latter produced3,392 NMIs and3,308 IRQs with full A/C bank restoration assertions.
- Both flag-off standard builds remain exact KB hashes. Composition verifies every old resident/SMC/SRAM public address; only cold menu/profile implementation labels relocate.

The interaction arenas modify block-buffer geometry and seed PRNG choices/full P deliberately. They are not natural campaign playthroughs. Their green fixture block is a consequence of retaining the old nametable attribute at an injected empty-area cell; it is not evidence about natural block colors. No campaign/video claim is made.

## Integration contract

Use only the new own files and compose the contextual hooks against the current roster. The private baseline is immutable `chip-roster-mj`; current main has later profiles. Do not replace current shared files wholesale.

- PRG90/A logic;91/C records;92/A native controller/projectile kernels. CHR524..543 body,544 item/effects;545..603 remain unused.
- Variant5FE4; persistent16 bytes5F40..4F; active-only transient5C00..FF. No old SRAM address changes or generic twelve-family inventory row for rawID17.
- Chain `M3BoundingBoxGate` before the current `VvBoundingBoxGate`. Exclude the private MJ-only18-byte PLAYER trampoline. That trampoline sits at the actual end of the MJ PLAYER segment and preserves all preexisting public addresses.
- `CrossoverSourceSideProbe` uses the approved same-size28-byte substitution:18-byte farcall plus10 padding; cold inactive behavior reproduces Sophia/native.
- Compose the existing draw and visibility chains; allocate no new bank4 guard or PLAYER tail. The NMI C-bank selector stays fully resident; current root C91 reservation already covers17. Retain physical CHR upper bits2.
- Regenerate the joint current menu using `original-art/smb3-mario-portrait.png` and slot16/character17. Do not overwrite newer menu binary/CHR data with this older private roster. The private name indices20/21 must be reassigned after current root names.

## Remaining limitations

Music still uses the inherited Pit-family fallback. Action cues use provisional SMB effects; original SMB3 APU music/SFX are not ported. Fire pickup lacks the original dedicated palette-flash transition. Host collisions, enemy class reactions, mushroom walking, invulnerability/star duration, item delivery and death/room timing are SMB adaptations; no universal original-game parity claim is made. Kuribo's Shoe, P-Wing inventory, slopes, held shells and other SMB3 map objects are outside this requested normal-form implementation. No long-route/swimming-campaign or performance sweep has been performed.
