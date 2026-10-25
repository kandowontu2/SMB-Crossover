# Little Mac — functional MMC5 expanded profile

Frozen private MR-based ROM: `ca9785591b277b85c5587266daedbc7aef784e3be89c40bb3edb87ff03ce4b68`.
Use `manifest.json` and `shared-changes.diff` for integration into newer MV. Main was not edited.

## Controls and progression

* ID15, third-row slot14, name index30. No alternate selection.
* D-pad moves; A jumps; Down ducks; B punches; Up+B spends one star for an uppercut. Both standing and crouched attacks have their own source-pixel compositions.
* Native original Glass Joe starting values are used: 96 health and20 hearts (fighting spirit). A punch spends one heart; hitting an enemy refunds it, so a miss costs one. A hit costs3 hearts and one star. With no hearts, duck for30 updates to recover20. This recovery rule is a deliberate SMB adaptation; the original recovers through dodging/ducking in the boxing arena.
* A physical mushroom heals24 up to96 and sets the powered status. Each physical flower is displayed as the original Punch-Out white star and adds exactly one star, capped at3. The native emergence and collision path remains; head bumping does not grant the item immediately.
* Normal attack duration34 updates, super88, observed from actual native right-body-punch/super animation. Active attack windows, enemy damage and block interaction are SMB adaptations. Super has a taller attack volume and can defeat a Buzzy Beetle; normal fists cannot. Both use one contacted block cell per attack and preserve protected foundations.
* Health damage is adapted8 ordinary,16 Hammer Bro,32 Bowser. Fatal damage enters the existing native guest death/life-loss machinery. Life initialization returns health96/hearts20/stars0; area transitions retain persistent quantities and clear active attack state.
* Easy allows ordinary enemy stomps; Hard uses the existing guest no-stomp rule. Platform movement uses the port's actual MarioSourceMovement/MarioWaterMovement helpers under the real ID15. The high-ID integration receives Mario gravity and a5px fall cap. This is explicitly platformer movement, since Punch-Out has no platform jumping. A bounded native held-jump test rises73px.

## Authenticity and authored art

Original local ROM SHA256 `11b01730bc88173fd20a54bf327ff3a9db9a29e7a53c638359bbb30aac16a929`.
Pinned [primary disassembly](https://github.com/nmikstas/mike-tysons-punch-out-disassembly/tree/60b2fa0e61d57b10b5fadc04be96241d25755d25) and [official Nintendo manual](https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NAATE.pdf) are retained in the private reference directories. Controls and stars/heart meanings come from the manual; numeric animation timing and starting quantities were observed in the original emulator.

The two training run phases are exact original masks,44/45px tall, with native24/16 phase cadence over40 updates. They are not scaled/cropped in gameplay. Exact source palette0 is skin36/black0F/tracksuit25. Black ink remains with optional outlines disabled.

Idle, duck, punches and uppercuts are **authored SMB compositions of exact original pixels**, expressly approved by the parent/user. Idle pairs the original runner supporting leg; duck uses original duck torso; punches transplant genuine arm/glove pixels from original frames382/36 and map green garment pixels to pink tracksuit. These are not claimed to be original native boxing poses. The taller back-facing full boxing body is not substituted during attacks. Air uses an original running phase; damage uses the crouched composition.

An art-only14-byte original training-entry fixture reaches the genuine cutscene; it does not alter art/physics. Original boxing footage uses native controller inputs, with3 stars granted before the super solely to expose that source animation. Mac is a background object in the boxing engine, not an OAM sprite. Source models use actual physical MMC2 E-bank and nametable/palette state.2,951 opaque original screenshot pixels independently agree:879 training and2,072 boxing. Boxing's source scroll is RAM15 (source DEF A0AA/A0C5), not fixed176 during punches.

## Resource and call contract

* PRG93/A: LM_CORE `A000..AB38` approximately (use final map); PRG94/C: LM_GFX; PRG95/A: LM_COMBAT. `LmArtBegin` stays in C94. No new resident bank4 guard or NMI farcall. The existing resident ID15 table entry already publishes C94.
* Physical CHR668..707,40KB at `A7000..B0FFF`; poses use668..687, original star704. The rest is reserved zero space. The cfg allocation is physical, not a cursor-relative append.94 must be linked at C000.
* Persistent `$5F20..5F2F`; active overlay `$5C00..5C27` only while selected ID15. `$5FE2` reserved unused. No original SRAM moved or added. `X5InventoryInit` already clears the profile independently.
* `LmSetPose(X=pose)` publishes pointer/lowCHR and maps C94; `LmPublish` uses X5SetPhysicalChr with upper2 and X5SetSpecialChr704. Shared-call/NMI ownership is exercised in the native receipt.
* Full runner hurt hull: standing X0..15, Y−14..32 from native origin; crouched X−5..20,Y2..32. Arms are separate attack rectangles. Head and side adapters preserve native actor coordinates before block creation; collision buffer row remains authoritative. Crouch release waits for actual native headroom. Page-edge wall separation matches both hulls.
* `LmHeadGate` privately falls back to TnHeadDispatch, `LmBoundingBoxGate` to VvBoundingBoxGate, `LmSideLegacy` reproduces Sophia/native. **On current MV use M3HeadDispatch / M3BoundingBoxGate / M3SideDispatch for those inactive chains.**
* Same-size original SamusStopAtWall farcall is retargeted to `LmWallGate`; inactive tail remains CrossoverSourceWallDispatch. No resident growth.
* Private MR outer gameplay hooks lead Lm→previous Cv3/Vv chains. **Current MV has Jn/Mike outer wrappers: compose Lm admission into those live chains, retaining Jn as the inactive target where Mike currently owns the call.** Never replace current wrappers with old MR snapshots.
* Menu assets in this packet include only MR's completed portraits plusMac. Regenerate the current roster's18 portraits plus Mac19; copy the new4KB menu CHR slice only, and retain all later art. Name index30 is the intended current append; private28/29 are padding because MR predates SMB3.
* Constant body palette is cached and written only when invalidated/initializing. No world palette2 or3 rewrite. HUD is a small dirty text command `HP96 H20 S3`; it does not install a new font or IRQ timing path.

## Validation and honest limits

* Native Mesen:2,327 frames,2,319 NMIs,2,250 split IRQs, A/C ownership and33 shared-call operand bytes preserved. Real controller menu entry; movement/jump/duck/punch/super; headblock→physical emerging mushroom→controller collection; three physical flower stars→cap3; earned super consumption; Goomba punch; wall; own damage; fatal damage/native life-loss progression. The terrain/pickup/enemy scenes after ordinary entry are disclosed bounded RAM arenas, not full campaign clears.
*40 linked DrawAll pose/facing/outlines pixel cases;206 quantity/input/hull/page-edge/star/headroom checks against independent expectations. Source screenshot pixel check above. Standard flag-off M3/M5 exactly KB (`472097…` /`0ab6ac…`).
* No Punch-Out music engine or voice/sound sample port. Current generic new-profile music maps to Pit; attacks/pickups use existing native SMB SFX. No campaign/video, original boxing AI/dodge arena, knockdown recovery game, perfect Punch-Out physics, or new campaign layout claim. Shared spring/stomp adapter work is owned by level_changes_audit/root separately.

The private sources and tests are retained. Early failed/debug native/source captures remain as negatives; adoption-native is the final proof tied to the frozen ROM hash.
