# Rogue Dawn eight-gear inventory — read-only cb95, 2026-11-16

This is an inventory of existing acquisition, controls and source boundaries. No gear was awarded or gameplay CPU run for this review. It adds no item, opcode, helper, RAM, controller, ROM file or native qualification. Root owns the native queue and any delivery. The frozen M/MF/ML/MS, missile and full-route packets remain unchanged.

Both reads captured exact public `98261effbc214d24a00b2f8bd2950eca8ea3bf3675b331956a2ad42a7ab819e6` once and used the qualified strict composer **in memory** to obtain owning `cb95eb8dff9929c8162e019d5e3f33e45b570946f5281c07584a9f11cacdba07`. This is not a claim that cb95 was public at inspection time. The reference image is `13272464e34237f09c7fce87ac276b20da299f8028640cc51155759d6c642a4d`; the two-byte missile operand is the only Rogue change from that reference through the Sonic/Mini join. All Mini20/Sonic94 bytes remain preserved.

Actual donor: `C:/NES/the stash/Metroid - Rogue Dawn 1.21 (header fixed).nes`, 786448 bytes, SHA256 `9271411a20cc26c09f4d4bffe74c0d69a1bf91b815f7716fcf4610c4cee61077`. Donor addresses below use **decimal physical 8 KiB PRG bank**, followed by CPU address; area numbers are not physical bank numbers.

## Read-only receipts and bindings

The two inline producers ran through `python -B tools/audit/run_bounded_build_v1.py --output build/rogue-gear-inventory-source-1116 --timeout 600 --max-files 1 -- python -B -c ...`. They used only existing source/symbol metadata and the immutable captured images. The output root remained absent: zero generated files, no archive restoration. No `cold()`, controller, natural route or proposed/current game instruction was executed. Py65 MPU objects were instantiated solely to format disassembly, never stepped.

- Initial inventory receipt: `ab35300d950f34340d341e8a0a901e2dd5b0bc841a8026751c5aeff2836dd7ad`.
- Corrected donor/table receipt: `f48601f1de230e6fb54693d9eec61d8d8a08ccc00a34cf5095c187fa7e8f6c4d`.
- Two initial *inspection* mistakes are excluded from conclusions: reading physical bank2:BFE7 instead of bank3:BFE7, and linearly disassembling an unaligned F472 lead. The correction authenticates bank3:BFE7 at donor file32759 and aligned bank63:F483 onward. These were neither game failures nor candidate changes.

Strict frozen APIs: `current_rogue_missile_cb95_1116.reference(raw)` is metadata only; `compose_rogue_missile_9826_1116.proposal(raw9826)` owns the actual cb95 image. This review used `W.Symbols.bundle()` directly rather than the old metadata UI/cold path. The named source bindings include:

| Existing routine | Actual cb95 bank:PC | File offset |
| --- | --- | ---: |
| RdHsRewardForRaw / RdHsGrantType | 95:AC78 / 95:AD18 | 781448 / 781608 |
| RdHsDropContact / RdHzGrant | 95:AD7D / 95:BE14 | 781709 / 785956 |
| RdHzTerminal / RdHzUpdateDrops | 121:B707 / 121:B809 | 997143 / 997401 |
| RdHsDamage / RdHsEnvironment | 95:AE82 / 95:AA41 | 781970 / 780881 |
| RdStartJump / RdSpringAdmitted | 124:B000 / 124:B147 | 1019920 / 1020247 |
| RdControlSpring / RdControlScrew | 124:AF2B / 124:BB6A | 1019707 / 1022842 |
| RdBombAllocate / RdBombStepBegin | 124:B278 / 124:B31E | 1020552 / 1020718 |
| RdInitWaveHorizontal / RdInitIce | 124:B566 / 124:B5B3 | 1021302 / 1021379 |
| RdWaveKinematics / RdIceUpdateAdmission | 124:B5DA / 124:B700 | 1021418 / 1021712 |
| RdWxUpdateSlot / RdWxActorContact | 121:AF60 / 121:B287 | 995184 / 995991 |
| RdWxBombTerrain / RdWxBombNative | 121:B3ED / 95:BC1D | 996349 / 785453 |
| RdAddMissileTank | 124:B234 | 1020484 |

These are current byte/metadata bindings and a source inspection, not a fresh whole-source reassembly or dynamic all-gear ABI proof. Some retained source comments still say PRIVATE/unintegrated; they do not override the owning image or the later qualified routes.

## Natural selection, resources and duplicates

`RdHsRewardForRaw` is a selector, not a grant. Actual raw0 selects source item8, typed **D8 energy tank**. Raw1 selects source item9, typed **D9 missile tank**, while max missiles is zero. Thereafter each new raw1 construction selects the lowest *missing* gear bit in order:

`D0 Bomb → D1 High Jump → D2 Wall Jump → D3 Screw → D4 Spring → D5 Environment → D6 Wave → D7 Ice`.

When all eight bits are owned, later raw1 selects D9 again. The selector neither consumes RNG nor changes inventory. `RdHsPrepareActor` applies it to the genuine constructed native slot/ID2E; owner2 and typedD0..D9 remain explicit. The transaction retains the raw type and uses the stationary native Flower emergence carrier with distinct Rogue item art. A fully emerged actor and actual physical native contact must precede `RdHsCollectActor`/`RdHsGrantType`; the consumer erases once, issues popup6/cue32 and requests the original source reward sound. There is no imported 60-update growth-freeze policy.

Gear grants OR their bit into `RdGear` (source6878), exactly preserving the donor's nonexclusive commit at 61:A667. Wave and Ice therefore coexist. New constructors avoid an already owned gear bit; an already constructed duplicate can still contain that earlier typed reward. Its OR is idempotent, with the ordinary collection/score/sound transaction still present. This stale-duplicate case is a control-flow conclusion, not a newly observed duplicate pickup.

Energy tanks increment `RdTanks` up to6 and always refill the original raw BCD image to Lo99/Hi`(Tanks<<4)|09`, including at cap. Missile tanks add5 independently to current/max missiles, saturating each atFF, and **do not refill health**. Donor authority is 61:A684/A68D and 62:DD97..DDAF; the current add leaf is 124:B234. Health bytes are a source BCD image, not an integer copied from their hex value.

The native status mirror is nonzero when tanks, max missiles or gear are nonzero. Thus ordinary later raw1 rewards can advance the sequence after the first tank. This is an SMB stock adaptation, not a claim that the donor placed those upgrades in SMB1's authored blocks, or that all eight can be collected in a single 1-1 visit. A genuine acquisition plan needs enough freshly authored raw1 rewards during legal stage/area progression; no block, actor or outcome may be seeded.

Raw2 Star and raw3 hidden1UP take the actual native fallback once rather than becoming gear. Existing M/F/S/L receipts remain separately versioned: they prove tank, missile tank, native Star and life, **not** any of the eight gear bits. New cb95 source MF/missile/full gates are recorded in `rogue-missile-cb95-source-1116.md`; that source work is not a new native all-gear pass.

## Eight existing abilities and their actual controls

All eight selector entries, grant bits and the following implemented branches are present. “Implemented” here identifies code, not a genuine earned/native ability qualification.

| Typed reward / gear | Donor authority | Existing current behavior and controls | Remaining qualification |
| --- | --- | --- | --- |
| D0 / 01 Bomb | 62:D150; D65E/D670/D691 | In morph action3, fresh/retrigger **B** allocates one of shared D0/E0/F0 records if gear01 and no elevator. Airborne placement is allowed. Source8→9→10 fuse/explosion/animation remains; cost0. Host explosion phases query the genuine native bomb-point block transaction and mapped enemy contacts. | Earn Bomb naturally, place it with real input, prove fuse, legal block/question transaction, enemy contact and cleanup. No bomb-jump claim is established by this inventory. |
| D1 / 02 High Jump | 62:CFC3 and DC4B | Ordinary and upward-aim fresh-A jumps keep source VYFC; dry jump gravity becomes12 instead of18. Environment-aware helpers still determine reduced-environment behavior. | Genuine gear-before/after jump arc and native collision/landing, with normal controls. |
| D2 / 04 Wall Jump | 62:DA46..DA6B | Airborne freshA while holding toward a blocked side runs the actual side probe and source jump continuation. Ordinary dry max-speed selection remains12h. This is not a free midair second jump. | Earn bit04 and observe both actual wall probes/facings, admission, movement and safe landing. |
| D3 / 08 Screw | 62:CD9C..CDBE | Source action1, spin animation0C/0E, pose phase and upward-motion tests admit Screw; the same source admission drives mapped enemy damage/contact protection. Morph touching an enemy is not a substitute. | Genuine spin contact/protection/defeat, invalid-pose rejection and ordinary hurt behavior. |
| D4 / 10 Spring | 61:A2AD..A2FE; 62:DA0A..DA40 | In ball, freshA requires real tile/frozen support, then source VYFC and gravity18/12. Releasing A clamps the qualifying spring rise toFE. FreshDown can morph in the original airborne action/cooldown context. Ordinary morph is already available without gear. | Earn bit10, actual supported spring/release and repeated fresh-edge behavior; no flight inference. |
| D5 / 20 Environment | 62:CEAC; 63:E294 | Suit halves source BCD contact damage. Current explicit Firebar/Podoboo heat adapter retains original cadence/suit admission and half-damage arithmetic. Suit does not confer Screw/Star immunity. | Genuine suited contact/heat and unsuited comparison with actual resources, plus native palette/art scope if needed. |
| D6 / 40 Wave | 62:D359/D52C; actual D58F/D5A8 tables | Normal B/up+B with missile mode off installs action2 and original packed Wave direction/phase, sine decoder, animation7D and sound request. | Natural gear, both launch directions/up, actual source movement/cell/terrain response, enemy damage and expiry. Do not infer wall penetration from the beam's name or the source comment. |
| D7 / 80 Ice | 62:D38E; D5C1→DA85 | Mode-off shots become action3; first mapped contact freezes without HP debit, then damaging contacts/thaw use the declared host mapping. Gear40 selects the actual Wave kinematics even for Ice. | Natural bit80, real freeze/thaw/support/second contact and Wave+Ice coexistence. All source/native target classes remain explicit. |

Common existing controls: Left/Right move and face; freshA jumps; B fires at admitted source fire events; Up aims/fires upward; Down morphs, and Up unmorphs only through actual clearance. **Select** toggles missile mode only with ammo. Missile B/up+B spends1; last ammo clears mode and emits the original palette request. Long beam and Morph are already intrinsic donor abilities, not two more gear rewards. Original Metroid gear names for bits04/10 are incorrect for this Rogue cartridge.

The actual donor projectile table is 62:D4D3..D4EA: normal1, Wave2, Ice3, impact4, bomb8/9/10 and missile11 are distinct. Current cb95 changes only the action11 jump operand at native121:AF76 to the existing normal projectile leaf AFE2. The qualified motion is horizontal ±4 or upward−4, with actual cell/animation/viewport cleanup. Its authorized ordinary native enemy damage1 adaptation is unchanged. No damage increase or new weapon mode is proposed.

## How ordinary small drops differ from upgrades

The current source-paid terminal path uses native `PseudoRandomBitReg+1`: values below10h produce no drop; otherwise the low3 bits index `80 81 89 80 81 89 81 89`. Correct donor binding is **physical bank3:BFE7**, file32759; current identical bytes are at file997289. This is an explicit SMB enemy adaptation of that one donor-area table, not a universal RNG-rate claim.

- 80: missile+5, clamped to current max; not spawned while max missiles is0.
- 81: energy+5 through original BCD/cap arithmetic.
- 89: energy+20; the authored Goomba/sourceHP2 mapping suppresses this large drop. Declared HP4/8 classes can permit it.

Four existing `InvDrop` records hold stationary full-world-page drops. Birth cannot collect in the same update; lifetime96 decrements on `RdClock&3==0`. Actual source radius overlap precedes grant/erase. These kills never grant gear. The source-paid weapon/Screw terminal path is the producer; a native Star, shell or stomp alone does not silently become an extra Rogue drop producer.

Aligned donor 63:F483..F4D3 also shows the scripted extra-quantity context (`6B02`): ordinary missile5 versus scripted30, and ordinary energy5/20 versus its separate scripted branch. The current adaptation deliberately exposes only ordinary80/81/89 amounts, not donor scripted actor/room state. No large/scripted value was silently imported.

## Lifecycle and explicit boundaries

Current NewSession clears gear, current/max missiles, tanks and health, then initializes raw99/09. Actual NewLife refills at earned tank capacity and clears active scene state while preserving earned gear/ammo under the approved SMB adaptation. Area entry preserves resources; real death chooses the NewLife path. No extra life/reset is manufactured by a gear grant.

The source reduced-environment flag comes from host water versus dry scene, not the suit bit. Donor 62:DBE6..DC72 consults source room/environment fields; the current adapter does not synthesize7808..780D Metroid rooms. `RdSlow` is read by current per-pixel movement but this inspected source set has no ordinary writer besides active-state clearing; its original external room-context behavior is **not newly closed**. It is not evidence that suit should remove water drag.

Explicit unfinished or unmapped boundaries remain: `RdHsNoDoor` rejects unadmitted source door/elevator actions; native SMB pipe/area transitions retain their own owner. `RdHsLowHealth` is an explicit CLC stub for the original06C4 counter/audio owner, and `RdHsHealth` does not construct room-specific6996=E4. Source room healing/environment scripts, alternate source costume, scripted drop quantities and full audio waveform fidelity are not made complete by the eight grant bits. Native morph ground-bounce is implemented in `RdGroundCollisionResponse`; it must not be confused with an unproved self-bomb boost.

Full genuine acquisition/control coverage for the eight bits remains open. The smallest next useful source scope is **one first missing raw1 reward after the already genuine MF prefix**, expected D0 Bomb, with actual construction, maturity, physical collector, OR01/source sound, erase/popup, real score writer and ≥25 new original/public returns; then one normal morph+B placement/fuse/terrain or enemy interaction. It needs root review before another route. No idle/walk cadence or performance conclusion is drawn from this static inventory.

## Exact retained source pins

| Source | SHA256 |
| --- | --- |
| rogue_dawn_state.inc | f91a3dae3adabbf8231a9c446e09e07d1ce232e352a663b48f15ed0792336134 |
| rogue_dawn_core.s | 3324311bf4cde2845871aa5f3970e0222b5b76f77f64854f44b2d32ecb5cda4a |
| rogue_dawn_control.s | 6b5374774a730941c12b02ad44792318b237d2996b6febbb9d9c65239f2fa199 |
| rogue_dawn_weapons.s | bcc48630d66cef7084ca994e0f6a9730f929ee8bcdf82a636c6b89f877949aa4 |
| rogue_dawn_host_services.s | e43f538e3dd25b4fa0e791b549731e51d22a2ccf8e2b698fd06702599f699fa8 |
| rogue_dawn_host_services_bcd.inc | 4f1fe975b3ccb1b765bd5a1bc728671e455ab6257808bc7311db7fc5b2f49ddf |
| rogue_dawn_host_floor_v4.s | d0eb0d2cb586f7c540346f751ec28467b40ca2b2c1e2ffd7b8fdf601559f7777 |
| rogue_dawn_host_hazards_gate_v1.s | 7f9ed6f1602f02398dc527d8a4036bd336b3edf3b9c9f8667113f5d3b07a0d30 |
| rogue_dawn_host_hazards_drops_v1.s | 783d0147967b1d018297468b6d525564261b3f5327bde23aa431c42282032c02 |

Historical `rogue-dawn-source-2026-10-28.txt` and `rogue-dawn-weapons-source-2026-10-28.txt` retain the donor map and finite component receipts. Their old “not integrated” state and component-only passes are not relabelled as this current inventory's gameplay/native evidence.
