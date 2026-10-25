; Source 2.02 weapons sharing the roster's ten projectile slots. Types 1..8
; belong to the older primary-weapon dispatch; types >=9 are updated here.
.include "special_art_ids.inc"
.include "special_art.inc"
.include "bass_special_poses.inc"
.include "bass_special_pose_ids.inc"
.include "megaman_special_poses.inc"
.include "megaman_special_pose_ids.inc"
SS_ARM = 9
SS_METAL = 10
SS_KNUCKLE = 11
SS_PHARAOH = 12
SS_PHARAOH_MED = 13
SS_PHARAOH_BIG = 14
SS_FLAME_BULLET = 15
SS_FLAME = 16
SS_WATER = 17
SS_BALLOON = 18
SS_KICK = 19
SS_RUSH = 20
SS_ARM_DEBRIS = 21
.pushseg
.segment "SRAM"
CurrentBankC: .res 1
SpecialRamStart:
SsMode: .res 10
SsAngleLo: .res 10
SsAngleHi: .res 10
SsHidden: .res 10
SsArt: .res 10
SsHitTimer: .res 10
SsBodyStop: .res 1
SsFreeze: .res 1
SsHeld: .res 1
SsKick: .res 1                    ; 0=no slide, 1=paid attack, 2=ordinary/cancelled slide.
SsSelected: .res 1
SsCount: .res 1
SsType: .res 1
SsSlot: .res 1
SsTmp: .res 1
SsTmp2: .res 1
SsSaveInput: .res 1
SsWaterRadius: .res 1
SsWaterFraction: .res 1
SsWaterExpand: .res 1
SsWaterX: .res 1
SsWaterPage: .res 1
SsWaterY: .res 1
SsWaterEmpty: .res 1             ; Per-update conservative orbit terrain reject.
SsWaterScaleLo: .res 8           ; Four products and their exact signed opposites.
SsWaterScaleHi: .res 8
SsWaterScaleKey: .res 1          ; Low five angle bits guard nonuniform fixtures.
SsWaterScaleBuild: .res 1
SsDrawFirst: .res 1
SsDrawRemaining: .res 1
SsDrawFamily: .res 1
SsChrActive: .res 1
SsChrPhysical: .res 1
SsLastChrActive: .res 1
SsLastChrPhysical: .res 1
SsMul: .res 2
SsProduct: .res 2
SsNegative: .res 1
SsOffset: .res 2
SsSavedMm: .res 5
SsEnemies: .res 1
SsProbe: .res 1
SsRadius: .res 1
SsCollideSolid: .res 1
SsLastPalette: .res 1
SsContactX: .res 1
SsContactPage: .res 1
SsContactY: .res 1
SsAudioRequest: .res 1           ; Native MM3 track + 1; zero means no request.
SpecialRamEnd:

.segment "SPECIAL_MM"
.proc SpecialClear
  lda MmDeathFlag
  bne :+
    lda #1
    sta BassSourceKill
  :
  lda #0
  ldx #SpecialRamEnd-SpecialRamStart-1
Loop:
  sta SpecialRamStart,x
  dex
  jpl Loop
  rts
.endproc

.if ::MAPPER_MMC5
.proc SpecialPoolAny
  ; Slots are allocated from9 downward. Return at the first live slot so
  ; active shields and other weapons do not pay a ten-slot idle check.
 .repeat 9, I
  lda RgShotType+9-I
  bne Present
 .endrepeat
  lda RgShotType
Present:
  rts
.endproc
.endif

.proc SpecialMovement
  lda SsFreeze
  jeq Normal
  lda #0
  sta Player_X_Speed
  rts
Normal:
  lda SavedJoypadBits
  sta SsSaveInput
  lda SsBodyStop
  jeq Move
  lda Player_State
  jne Move
  lda SavedJoypadBits
  and #$fc
  sta SavedJoypadBits
  lda #0
  sta MmVX
  sta MmVX+1
  sta MmVX+2
  sta Player_X_Speed
Move:
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  jne MegaMan
  farcall ExpandedMovement
  jmp Restore
MegaMan:
  farcall MegaManMovement
Restore:
  lda SsSaveInput
  sta SavedJoypadBits
  rts
.endproc

.proc SpecialWeapons
  ; Types9..21 and their persistent effects belong exclusively to MM/Bass.
  ; RosterClearState/SpecialClear clears them at character/area boundaries;
  ; other inventories keep their own weapon batches and world clocks.
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  beq Supported
  cmp #CHARACTER_BASS
  beq Supported
  rts
Supported:
  lda TimerControl
  jne Done
  lda GameEngineSubroutine
  cmp #8
  jne Done
  lda MmDeathFlag
  jne Done
  lda MmBulletType
  sta SsSavedMm
  lda MmBulletX
  sta SsSavedMm+1
  lda MmBulletPage
  sta SsSavedMm+2
  lda MmBulletY
  sta SsSavedMm+3
  lda MmBulletDir
  sta SsSavedMm+4
  lda #0
  sta SsEnemies
  ldx #5
EnemyCandidates:
  lda Enemy_Flag,x
  beq EnemyNext
  bmi EnemyNext                  ; Bowser duplicate is not another target.
  lda Enemy_State,x
  and #$20
  bne EnemyNext
  lda Enemy_ID,x
  cmp #$15
  bcc EnemyFound
  cmp #Bowser
  beq EnemyFound
  cmp #BulletBill_CannonVar
  bne EnemyNext
EnemyFound:
  ; Same field the native consumer rejects, read live again for each ball.
  lda EnemyOffscrBitsMasked,x
  bne EnemyNext
  inc SsEnemies
EnemyNext:
  dex
  bpl EnemyCandidates
  jmp EnemyCandidatesDone
WaterEnemyTargetLo: .byte <MegaManWeapons::Enemies,<WaterShieldEnemies
WaterEnemyTargetHi: .byte >MegaManWeapons::Enemies,>WaterShieldEnemies
.if ::MAPPER_MMC5
WaterEnemyTargetBank: .byte .bank(MegaManWeapons::Enemies)|MMC5_PRG_ROM,.bank(WaterShieldEnemies)|MMC5_PRG_ROM
.else
WaterEnemyTargetBank: .byte .bank(MegaManWeapons::Enemies),.bank(WaterShieldEnemies)
.endif
  .res 50-(*-EnemyCandidates),$ea
EnemyCandidatesDone:
  lda SsBodyStop
  beq :+
    dec SsBodyStop
  :
  lda SsFreeze
  beq :+
    dec SsFreeze
  :
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  jeq MegaWeapons
  cmp #CHARACTER_MEGAMAN
  jne Update
MegaWeapons:
  ldx SelectedCharacter
  lda InvSelected,x
  sta SsSelected
  ; Source attackSlide belongs to this paid slide, rather than the selected
  ; weapon or its remaining energy. Switching away or leaving slide ends it.
  lda XgDash
  ora MmSliding
  beq ClearKickReceipt
  lda SsSelected
  cmp #5
  beq KickReceiptReady
  lda #2                        ; An ordinary/cancelled active slide cannot reactivate.
  bne StoreKickReceipt
ClearKickReceipt:
  lda #0
StoreKickReceipt:
  sta SsKick
KickReceiptReady:
  lda SsSelected
  jeq Update
  farcall InventoryHas
  jcc Update
  lda Player_State
  cmp #3
  jeq Update
  lda XgDash
  ora MmSliding
  jeq Input
  lda SsSelected
  cmp #5
  jne Update
  lda SsKick
  jne Update
  lda #2                        ; Failure to fund this start remains an ordinary slide.
  sta SsKick
  lda #5
  ldy #4
  farcall InventorySpend
  jcc Update
  lda #1
  sta SsKick
  lda #65
  sta SsAudioRequest
  jsr FindSlot
  jcc Update
  lda #SS_KICK
  jsr Spawn
  jmp Update
Input:
  lda #0
  sta SsKick
  lda SsSelected
  cmp #1
  jne Fresh
  lda SsHeld
  jne Fresh
  lda SavedJoypadBits
  and #B_Button
  jeq Update
  jsr GrabBrick
  jmp Update
Fresh:
  lda InvFresh
  and #B_Button
  jeq Update
  jsr MegaAttack
Update:
  lda #0
  sta SsWaterEmpty
  lda SsWaterExpand
  beq WaterFollowCenter
    lda #$ff
    sta SsWaterScaleKey
    lda SsWaterFraction
    eor #1
    sta SsWaterFraction
    clc
    adc SsWaterRadius
    adc #2
    sta SsWaterRadius
    jmp UpdateShots
WaterFollowCenter:
  ; All eight balls follow this identical center in a non-expanding orbit.
  ; Recompute once after player motion, before any per-ball collision.
  lda Player_X_Position
  clc
  adc #8
  sta SsWaterX
  lda Player_PageLoc
  adc #0
  sta SsWaterPage
  lda Player_Y_Position
  clc
  adc #20
  sta SsWaterY
  lda SsSelected
  cmp #7
  bne UpdateShots
  jsr WaterAreaEmpty
UpdateShots:
.if ::MAPPER_MMC5
  ; An empty shared pool cannot run motion, terrain or enemy contacts. Keep
  ; every clock/input/palette step above and reproduce the exhausted loop's
  ; scratch state below; any nonzero type conservatively takes the full loop.
  jsr SpecialPoolAny
  bne ActiveShots
  lda #0
  sta RgSlot
  ldx #$ff
  clc
  jmp SpecialWeaponsFinish
ActiveShots:
.endif
  ldx #9
Loop:
  stx RgSlot
  lda RgShotType,x
  cmp #SS_WATER
  jeq FastWater
  cmp #32
  jcs Next
  cmp #9
  jcc Next
  inc RgShotAge,x
  lda SsHitTimer,x
  beq :+
    dec SsHitTimer,x
    bne :+
    lda #0
    sta RgShotHits,x
  :
  jsr Motion
  ldx RgSlot
  lda RgShotType,x
  jeq Next
  lda SsHidden,x
  jne Next
  jsr Art
  ldx RgSlot
  lda RgShotImpact,x
  jmi Next                       ; Deflected shots are visible, but stopHit.
  lda RgShotType,x
  cmp #SS_RUSH
  jeq Next
  cmp #SS_ARM
  bne :+
    lda SsMode,x
    jne Next
  :
  lda RgShotType,x
  cmp #SS_KNUCKLE
  bne :+
    lda RgShotAge,x
    cmp #10
    jcc Next
  :
  lda RgShotType,x
  cmp #SS_BALLOON
  jeq Enemies
  cmp #SS_KICK
  jeq Next                       ; The graphic does not attack; actual body contact does.
  cmp #SS_ARM_DEBRIS
  jeq Enemies
  cmp #SS_WATER
  bne GeneralTerrain
  jsr WaterCollisionCandidate
  jmp TerrainReady
FastWater:
  ; Water has no gravity, acceleration, flame cooldown, held-brick state,
  ; startup lock or changing artwork. Its orbit and every collision still run.
  inc RgShotAge,x
  jsr Orbit
  ldx RgSlot
  lda RgShotType,x
  jeq Next
  lda SsHidden,x
  jne Next
  lda #SS_ART_WATER40
  sta SsArt,x
  lda SsWaterEmpty
  jne Enemies
  jsr WaterCollisionCandidate
  jmp TerrainReady
GeneralTerrain:
  jsr CollisionCandidate
TerrainReady:
  jcc Enemies
  jsr Bridge
  farcall MegaManWeapons::Blocks
  lda MmBulletType
  jne Enemies
  ldx RgSlot
  lda RgShotType,x
  cmp #SS_FLAME_BULLET
  jeq Ignite
  cmp #SS_FLAME
  jeq Enemies
  cmp #SS_ARM
  jeq Shatter
  jmp Kill
Ignite:
  jsr FlameContact
  lda #1
  sta RgShotDir,x
  lda #SS_FLAME
  sta RgShotType,x
  lda #0
  sta RgShotAge,x
  sta RgShotVXLo,x
  sta RgShotVXHi,x
  sta RgShotVYLo,x
  sta RgShotVYHi,x
  jmp Next
Shatter:
  jsr ArmShatter
  jmp Next
Enemies:
  lda SsEnemies
  jeq Next
  jsr Bridge
  ; Only the Water50 proxy selects the direct, live native enemy consumer.
  SMC_StoreValue SafecallA, a
  lda WaterEnemyTargetLo,y
  SMC_StoreLowByte FarcallJmpTarget, a
  lda WaterEnemyTargetHi,y
  SMC_StoreHighByte FarcallJmpTarget, a
  lda WaterEnemyTargetBank,y
  jsr FarCallCommon
.if ::MAPPER_MMC5
::_FARCALL_COUNT .set ::_FARCALL_COUNT + 1
.endif
  lda MmBulletType
  jne Next
  ldx RgSlot
  lda RgShotType,x
  cmp #SS_ARM
  jeq Shatter
Kill:
  ldx RgSlot
  lda #0
  sta RgShotType,x
Next:
  ldx RgSlot
  dex
  jpl Loop
::SpecialWeaponsFinish:
  lda SsSavedMm
  sta MmBulletType
  lda SsSavedMm+1
  sta MmBulletX
  lda SsSavedMm+2
  sta MmBulletPage
  lda SsSavedMm+3
  sta MmBulletY
  lda SsSavedMm+4
  sta MmBulletDir
  jsr SpecialPalette
Done:
  rts

MegaAttack:
  lda SsSelected
  cmp #7
  jeq Water
  cmp #5
  jeq Return
  jsr Count
  lda SsSelected
  cmp #8
  jeq Rush
  lda SsSelected
  cmp #1
  jne Ordinary
  lda SsHeld
  jeq Return
ArmThrowSpan:
  ;2.02 pays at the actual throw, after the free lift/hold epoch.
  farcall MegaManSuperArmThrow
  jcc Return
  jmp ShootPose
  .res 39-(*-ArmThrowSpan),$ea
Ordinary:
  ldy SsSelected
  lda SsCount
  cmp Limits-1,y
  jcc FireOrdinary
  cpy #4
  jne Return
  lda #0                        ; The balloon has a separate slot allowance.
  sta SsCount
  jmp MakeBalloon
FireOrdinary:
  jsr FindSlot
  jcc Return
  ldy SsSelected
  lda Costs-1,y
  tay
  lda SsSelected
  farcall InventorySpend
  jcc Return
  ldx RgSlot
  ldy SsSelected
  lda Types-1,y
  jsr Spawn
  ldx RgSlot
  lda #$c0
  sta RgShotVXLo,x
  lda #3
  sta RgShotVXHi,x
  jsr SignX
  lda SsSelected
  cmp #3
  jeq Knuckle
  cmp #2
  jeq Metal
  cmp #4
  jeq Pharaoh
  cmp #8
  jeq Rush
  jmp ShootPose
Knuckle:
  lda #0
  sta RgShotVXLo,x
  sta RgShotVXHi,x
  lda Player_State
  jeq ShootPose
  lda #10
  sta SsFreeze
  jne ShootPose
Metal:
  jsr Aim
  jmp ShootPose
Pharaoh:
  jsr Aim
  lda #1
  sta SsCount
MakeBalloon:
  jsr FindSlot
  jcc PharaohDone
  lda #4
  ldy #4
  ; Creating the balloon needs remaining energy but does not spend it.
  farcall InventoryIndex
  lda StarInvincibleTimer
  bne BalloonEnergy
  lda InvAmmo,x
  cmp #4
  jcc PharaohDone
BalloonEnergy:
  ldx RgSlot
  lda #SS_BALLOON
  jsr Spawn
  lda Player_X_Position
  clc
  adc #8
  sta RgShotX,x
  lda Player_PageLoc
  adc #0
  sta RgShotPage,x
  lda Player_Y_Position
  sec
  sbc #9
  sta RgShotY,x
  lda Player_Y_HighPos
  sbc #0
  sta RgShotYHigh,x
  lda #1
  sta SsHidden,x
PharaohDone:
  lda SsCount
  jne ShootPose
  rts
Rush:
RushDispatchSpan:
  farcall MegaManRushAttack
  rts
  .res 62-(*-RushDispatchSpan),$ea

ShootPose:
  lda #12
  sta RgShootPose
  sta MegaManShotPose
  lda SsSelected
  cmp #6
  jeq Sound
  sta SsBodyStop
  lda #12
  sta SsBodyStop
Sound:
  lda SsSelected
  cmp #1                        ; Source Super Arm lifting/throwing is silent.
  jeq Return
  lda #Sfx_Fireball
  sta Square1SoundQueue
  ldy SsSelected
  lda ShotSounds-1,y
  sta SsAudioRequest
Return:
  rts
Types: .byte SS_ARM,SS_METAL,SS_KNUCKLE,SS_PHARAOH,SS_KICK,SS_FLAME_BULLET,SS_WATER,SS_RUSH
Costs: .byte 8,4,8,4,4,4,16,0
Limits: .byte 1,3,1,1,1,3,8,1
ShotSounds: .byte 0,64,22,61,22,22,67,22

Water:
  lda #0
  sta SsCount
  ldx #9
WaterCheck:
  lda RgShotType,x
  cmp #SS_WATER
  jne WaterNext
  inc SsCount
  lda SsHidden,x
  jne Return
WaterNext:
  dex
  jpl WaterCheck
  lda SsCount
  jeq NewWater
  lda SsWaterExpand
  jne Return
  lda #1
  sta SsWaterExpand
  lda Player_X_Position
  clc
  adc #8
  sta SsWaterX
  lda Player_PageLoc
  adc #0
  sta SsWaterPage
  lda Player_Y_Position
  clc
  adc #20
  sta SsWaterY
  jsr Sound
  lda #66
  sta SsAudioRequest
  rts
NewWater:
  lda #7
  ldy #16
  farcall InventorySpend
  jcc Return
  lda #22
  sta SsWaterRadius
  lda #0
  sta SsWaterExpand
  sta SsWaterFraction
  sta SsCount
CreateWater:
  jsr FindSlot
  jcc Return
  lda #SS_WATER
  jsr Spawn
  lda SsCount
  asl
  asl
  asl
  asl
  asl
  ldy RgShotDir,x
  cpy #2
  bne :+
    eor #$80                    ; Source left-facing starting angle subtracts pi.
  :
  sta SsAngleHi,x
  lda SsCount
  beq :+
    lda #1
  :
  sta SsHidden,x
  inc SsCount
  lda SsCount
  cmp #8
  jcc CreateWater
  jmp ShootPose

Count:
  lda #0
  sta SsCount
  ldx #9
CountLoop:
  lda RgShotType,x
  beq :+
    inc SsCount
  :
  dex
  jpl CountLoop
  rts
FindSlot:
  ldx #9
Find:
  lda RgShotType,x
  jeq Found
  dex
  jpl Find
  clc
  rts
Found:
  stx RgSlot
  sec
  rts
Spawn:
  ldx RgSlot
  sta RgShotType,x
  lda #0
  sta RgShotAge,x
  sta RgShotFracX,x
  sta RgShotFracY,x
  sta RgShotVXLo,x
  sta RgShotVXHi,x
  sta RgShotVYLo,x
  sta RgShotVYHi,x
  sta RgShotHits,x
  sta RgShotImpact,x
  sta SsMode,x
  sta SsHidden,x
  sta SsAngleLo,x
  sta SsAngleHi,x
  sta SsArt,x
  sta SsHitTimer,x
  lda PlayerFacingDir
  sta RgShotDir,x
  lda #27
  cmp RgShotDir,x
  lda RgShotDir,x
  cmp #1
  jeq Right
  lda #$f5
  ldy #$ff
  jne XOffset
Right:
  lda #27
  ldy #0
XOffset:
  clc
  adc Player_X_Position
  sta RgShotX,x
  tya
  adc Player_PageLoc
  sta RgShotPage,x
  lda #19
  ldy Player_State
  beq :+
    lda #15
  :
  clc
  adc Player_Y_Position
  sta RgShotY,x
  lda Player_Y_HighPos
  adc #0
  sta RgShotYHigh,x
  rts
SignX:
  lda RgShotDir,x
  cmp #2
  jne SignDone
NegateX:
  sec
  lda #0
  sbc RgShotVXLo,x
  sta RgShotVXLo,x
  lda #0
  sbc RgShotVXHi,x
  sta RgShotVXHi,x
SignDone:
  rts
NegateY:
  sec
  lda #0
  sbc RgShotVYLo,x
  sta RgShotVYLo,x
  lda #0
  sbc RgShotVYHi,x
  sta RgShotVYHi,x
  rts
Aim:
  lda SavedJoypadBits
  and #Up_Dir | Down_Dir
  jeq AimDone
  sta SsTmp
  lda #$c0
  sta RgShotVYLo,x
  lda #3
  sta RgShotVYHi,x
  lda SsTmp
  and #Up_Dir
  beq :+
    jsr NegateY
  :
  lda SavedJoypadBits
  and #3
  jne Diagonal
  lda SsSelected
  cmp #2
  jne Diagonal
  lda #0
  sta RgShotVXLo,x
  sta RgShotVXHi,x
  rts
Diagonal:
  ; 450/120 * .75 = 2.8125 px/update, in both axes.
  lda #$d0
  sta RgShotVXLo,x
  lda #2
  sta RgShotVXHi,x
  jsr SignX
  lda #$d0
  sta RgShotVYLo,x
  lda #2
  sta RgShotVYHi,x
  lda SsTmp
  and #Up_Dir
  jeq AimDone
  jsr NegateY
AimDone:
  rts

Motion:
  lda RgShotImpact,x
  jmi Integrate
  lda RgShotType,x
  cmp #SS_ARM
  jeq Arm
  cmp #SS_ARM_DEBRIS
  jeq Debris
  cmp #SS_BALLOON
  jeq Balloon
  cmp #SS_WATER
  jeq Orbit
  cmp #SS_KICK
  jeq Kick
  cmp #SS_RUSH
  jeq RushMotion
  cmp #SS_FLAME
  jeq Flame
  cmp #SS_FLAME_BULLET
  jeq FlameGravity
  cmp #SS_KNUCKLE
  jeq KnuckleMotion
  jmp Integrate
Flame:
  lda RgShotAge,x
  cmp #45
  jcs MotionKill
  rts
FlameGravity:
  lda RgShotX,x
  sta SsAngleLo,x
  lda RgShotPage,x
  sta SsAngleHi,x
  lda RgShotY,x
  sta SsHitTimer,x
  clc
  lda RgShotVYLo,x
  adc #46
  sta RgShotVYLo,x
  lda RgShotVYHi,x
  adc #0
  sta RgShotVYHi,x
  jmp Integrate
Arm:
  lda SsMode,x
  jeq ArmGravity
  lda Player_X_Position
  clc
  adc #8
  sta RgShotX,x
  lda Player_PageLoc
  adc #0
  sta RgShotPage,x
  lda Player_Y_Position
  sec
  sbc #8
  sta RgShotY,x
  rts
Debris:
  lda RgShotAge,x
  cmp #32
  jcs MotionKill
ArmGravity:
  clc
  lda RgShotVYLo,x
  adc #57
  sta RgShotVYLo,x
  lda RgShotVYHi,x
  adc #0
  sta RgShotVYHi,x
  jmp Integrate
KnuckleMotion:
  lda RgShotAge,x
  cmp #10
  jcc NoMove
  lda RgShotDir,x
  cmp #2
  jne KnuckleRight
  jsr NegateX
  jsr Accelerate
  jsr NegateX
  jmp Steer
KnuckleRight:
  jsr Accelerate
Steer:
  lda #0
  sta RgShotVYLo,x
  sta RgShotVYHi,x
  lda SavedJoypadBits
  and #Up_Dir | Down_Dir
  jeq Integrate
  pha
  lda #$6b
  sta RgShotVYLo,x
  pla
  and #Up_Dir
  jeq Integrate
  jsr NegateY
  jmp Integrate
Accelerate:
  clc
  lda RgShotVXLo,x
  adc #16
  sta RgShotVXLo,x
  lda RgShotVXHi,x
  adc #0
  sta RgShotVXHi,x
  cmp #2
  jcc NoMove
  jne CapKnuckle
  lda RgShotVXLo,x
  cmp #$eb
  jcc NoMove
CapKnuckle:
  lda #2
  sta RgShotVXHi,x
  lda #$eb
  sta RgShotVXLo,x
NoMove:
  rts
Integrate:
  clc
  lda RgShotFracX,x
  adc RgShotVXLo,x
  sta RgShotFracX,x
  lda RgShotX,x
  adc RgShotVXHi,x
  sta RgShotX,x
  lda #0
  ldy RgShotVXHi,x
  bpl :+
    lda #$ff
  :
  adc RgShotPage,x
  sta RgShotPage,x
  clc
  lda RgShotFracY,x
  adc RgShotVYLo,x
  sta RgShotFracY,x
  lda RgShotY,x
  adc RgShotVYHi,x
  sta RgShotY,x
  lda #0
  ldy RgShotVYHi,x
  bpl :+
    lda #$ff
  :
  adc RgShotYHigh,x
  sta RgShotYHigh,x
  cmp #1
  jne MotionKill
  lda RgShotX,x
  sec
  sbc ScreenLeft_X_Pos
  lda RgShotPage,x
  sbc ScreenLeft_PageLoc
  jeq NoMove
  cmp #$ff
  jne MotionKill
  lda RgShotX,x
  sec
  sbc ScreenLeft_X_Pos
  cmp #$d8
  jcs NoMove
  jmp MotionKill

Balloon:
  lda SavedJoypadBits
  and #B_Button
  jeq ReleaseBalloon
  lda RgShotAge,x
  cmp #15
  jcc NoMove
  lda #0
  sta SsHidden,x
  jsr BalloonFollow
  lda Player_Y_Position
  sec
  sbc #9
  sta RgShotY,x
  lda Player_Y_HighPos
  sbc #0
  sta RgShotYHigh,x
  lda RgShotAge,x
  cmp #63
  jcc NoMove
  lda #63
  sta RgShotAge,x
  rts
BalloonFollow:
  ; Source motion integrates the old drift before constraining the balloon
  ; to +/-20 Flash pixels and choosing the next 75px/s counter-drift.
  clc
  lda RgShotFracX,x
  adc RgShotVXLo,x
  sta RgShotFracX,x
  lda RgShotX,x
  adc RgShotVXHi,x
  sta RgShotX,x
  lda #0
  ldy RgShotVXHi,x
  bpl :+
    lda #$ff
  :
  adc RgShotPage,x
  sta RgShotPage,x
  lda Player_X_Position
  clc
  adc #8
  sta SsTmp
  lda Player_PageLoc
  adc #0
  sta SsTmp2
  lda RgShotX,x
  sec
  sbc SsTmp
  sta SsOffset
  lda RgShotPage,x
  sbc SsTmp2
  sta SsOffset+1
  bmi BalloonLeft
  bne ClampRight
  lda SsOffset
  cmp #10
  bcc BalloonVelocity
  bne ClampRight
  lda RgShotFracX,x
  beq BalloonVelocity
ClampRight:
  lda #10
  ldy #0
  jmp ClampBalloon
BalloonLeft:
  cmp #$ff
  bne ClampLeft
  lda SsOffset
  cmp #246
  bcs BalloonVelocity
ClampLeft:
  lda #246
  ldy #$ff
ClampBalloon:
  clc
  adc SsTmp
  sta RgShotX,x
  tya
  adc SsTmp2
  sta RgShotPage,x
  lda #0
  sta RgShotFracX,x
BalloonVelocity:
  lda #0
  sta RgShotVXLo,x
  sta RgShotVXHi,x
  lda MmVX
  ora MmVX+1
  ora MmVX+2
  beq StationaryBalloon
  lda MmVX+2
  bmi CounterRight
  lda #$60                       ; -75/120.
  sta RgShotVXLo,x
  lda #$ff
  sta RgShotVXHi,x
  rts
CounterRight:
  lda #$a0
  sta RgShotVXLo,x
  rts
StationaryBalloon:
  lda PlayerFacingDir
  cmp #1
  bne CatchLeft
  lda SsOffset+1
  bpl BalloonDone
  lda #$40                       ; Stationary right-facing catch-up: 150/120.
  sta RgShotVXLo,x
  lda #1
  sta RgShotVXHi,x
  rts
CatchLeft:
  lda SsOffset+1
  bmi BalloonDone
  lda SsOffset
  ora RgShotFracX,x
  beq BalloonDone
  lda #$c0
  sta RgShotVXLo,x
  lda #$fe
  sta RgShotVXHi,x
BalloonDone:
  rts
ReleaseBalloon:
  lda RgShotAge,x
  cmp #45
  jcc MotionKill
  pha
  jsr Count
  pla
  lda SsCount
  cmp #2
  jcs MotionKill
  lda #4
  farcall InventoryIndex
  lda StarInvincibleTimer
  bne ChargedReady
  sec
  lda InvAmmo,x
  sbc #8                        ; Source release spends/clamps, without gating.
  bcs :+
    lda #0
  :
  sta InvAmmo,x
  inc InvDirty
ChargedReady:
  ldx RgSlot
  lda RgShotAge,x
  cmp #63
  lda #SS_PHARAOH_MED
  bcc :+
    lda #SS_PHARAOH_BIG
  :
  jsr Spawn
  lda #$c0
  sta RgShotVXLo,x
  lda #3
  sta RgShotVXHi,x
  jsr SignX
  jsr Aim
  jsr ShootPose
  ldx RgSlot
  lda RgShotType,x
  cmp #SS_PHARAOH_BIG
  bne :+
    lda #62                    ; MM4's full Pharaoh release, native noise.
    sta SsAudioRequest
  :
  rts

Kick:
  lda SsKick
  cmp #1
  jne MotionKill
  lda SsSelected
  cmp #5
  jne MotionKill
  lda XgDash
  ora MmSliding
  jeq MotionKill
  lda Player_X_Position
  clc
  adc #8
  sta RgShotX,x
  lda Player_PageLoc
  adc #0
  sta RgShotPage,x
  lda Player_Y_Position
  clc
  adc #26
  sta RgShotY,x
  rts
RushMotion:
  lda SsMode,x
  jeq RushFall
  cmp #2
  jeq RushSpring
  cmp #3
  jeq RushExitAnimation
  cmp #4
  jeq RushFly
  lda RgShotAge,x
  cmp #252                       ; 12 landing + two 2000 ms wait intervals.
  jcs RushBeginExit
  lda Player_State
  jeq NoMove
  lda Player_Y_Speed
  jmi NoMove
  lda Player_X_Position
  clc
  adc #8
  sec
  sbc RgShotX,x
  clc
  adc #12
  cmp #25
  jcs NoMove
  lda Player_Y_Position
  clc
  adc #32
  sec
  sbc RgShotY,x
  clc
  adc #12
  cmp #9
  jcs NoMove
RushBounceSpan:
  farcall MegaManRushBounce
  .res 27-(*-RushBounceSpan),$ea
  lda #$55
  sta MmVY+1
  lda #0
  sta MmVY
  sta MmYFraction
  sta MmYFraction+1
  lda #$f9                       ; -800 Flash px/s / 120.
  sta MmVY+2
  sta Player_Y_Speed
  lda #1
  sta Player_State
  ldx RgSlot
  lda #2
  sta SsMode,x
  lda #0
  sta RgShotAge,x
  lda #Sfx_BigJump
  sta Square1SoundQueue
  rts
RushSpring:
  lda RgShotAge,x
  cmp #24
  jcc NoMove
RushBeginExit:
  ldx RgSlot
  lda #3
  sta SsMode,x
  lda #0
  sta RgShotAge,x
  rts
RushExitAnimation:
  lda RgShotAge,x
  cmp #12
  jcc NoMove
  lda #4
  sta SsMode,x
RushFly:
  sec
  lda RgShotVYLo,x
  sbc #82                        ; 2300 / 7200, Q8.8.
  sta RgShotVYLo,x
  lda RgShotVYHi,x
  sbc #0
  sta RgShotVYHi,x
  jmp Integrate
RushFall:
  clc
  lda RgShotVYLo,x
  adc #82
  sta RgShotVYLo,x
  lda RgShotVYHi,x
  adc #0
  sta RgShotVYHi,x
  cmp #8
  jcc RushFalling
  lda #8
  sta RgShotVYHi,x
  lda #$55
  sta RgShotVYLo,x
RushFalling:
  jsr Integrate
  ldx RgSlot
  lda RgShotType,x
  jeq NoMove
  lda RgShotY,x
  cmp #32
  jcc NoMove
  lda RgShotX,x
  sta RgTempX
  lda RgShotPage,x
  sta RgTempPage
  lda RgShotY,x
  sta RgTempY
  farcall ExpandedMapCell
  jcc NoMove
  ldx RgSlot
  lda RgTempY
  and #$f0
  sta RgShotY,x
  lda #1
  sta SsMode,x
  lda #0
  sta RgShotAge,x
  sta RgShotVYLo,x
  sta RgShotVYHi,x
  rts

Orbit:
  lda SsWaterExpand
  jeq OrbitFixedRadius
  jmp WaterPosition
OrbitFixedRadius:
  ; The exact existing signed radius-22 lookup needs no general multiply or
  ; per-ball center copies. Keep 16-bit carry at the world/page boundaries.
  lda SsAngleHi,x
  clc
  adc #64
  tay
  lda SsCircle,y
  sta SsOffset
  clc
  adc SsWaterX
  sta RgShotX,x
  lda #0
  bit SsOffset
  bpl :+
    lda #$ff
  :
  adc SsWaterPage
  sta RgShotPage,x
  ldy SsAngleHi,x
  lda SsCircle,y
  sta SsOffset
  clc
  adc SsWaterY
  sta RgShotY,x
  lda #1
  bit SsOffset
  bpl :+
    lda #0
  :
  adc #0
  sta RgShotYHigh,x
  jmp OrbitAdvance
WaterPosition:
  ; Keep arbitrary-angle fallback; a matching vector cache needs no subroutine.
  lda SsAngleHi,x
  and #31
  cmp SsWaterScaleKey
  beq WaterScaleReady
  jsr EnsureWaterScale
WaterScaleReady:
  ldx RgSlot
  lda SsAngleHi,x
  lsr
  lsr
  lsr
  lsr
  lsr
  sta SsTmp
  clc
  adc #2
  and #7
  tay
  clc
  lda SsWaterScaleLo,y
  adc SsWaterX
  sta RgShotX,x
  lda SsWaterScaleHi,y
  adc SsWaterPage
  sta RgShotPage,x
  ldy SsTmp
  clc
  lda SsWaterScaleLo,y
  adc SsWaterY
  sta RgShotY,x
  lda SsWaterScaleHi,y
  adc #1
  sta RgShotYHigh,x
OrbitAdvance:
  lda RgShotDir,x
  cmp #2
  beq OrbitReverse
  clc
  lda SsAngleLo,x
  adc #$b7
  sta SsAngleLo,x
  lda SsAngleHi,x
  adc #2
  sta SsAngleHi,x
  bcc :+
    lda #0
    sta SsHidden,x
  :
  jmp OrbitExpansionEnd
OrbitReverse:
  ; Bias the signed angle by pi: borrowing across that boundary is the
  ; source left-facing reveal threshold (angle <= -pi), not zero wrap.
  lda SsAngleHi,x
  eor #$80
  sta SsTmp
  sec
  lda SsAngleLo,x
  sbc #$b7
  sta SsAngleLo,x
  lda SsAngleHi,x
  sbc #2
  sta SsAngleHi,x
  eor #$80
  cmp SsTmp
  bcc OrbitExpansionEnd
  lda #0
  sta SsHidden,x
OrbitExpansionEnd:
  lda SsWaterExpand
  jeq OrbitDone
  lda SsWaterRadius
  cmp #180
  jcs MotionKill
OrbitDone:
  rts
EnsureWaterScale:
  ; Source balls share their fractional phase and differ by exactly 32 angle
  ; units. Four products cover the positive half-circle; their two's-complement
  ; opposites cover the other half. Cosine is two vector slots after sine.
  ; A nonuniform angle fixture rebuilds instead of reusing an unrelated phase.
  sta SsWaterScaleKey
  lda #3
  sta SsWaterScaleBuild
BuildScale:
  lda SsWaterScaleBuild
  asl
  asl
  asl
  asl
  asl
  clc
  adc SsWaterScaleKey
  tay
  lda SsSine,y
  jsr MultiplyRadius
  ldx SsWaterScaleBuild
  lda SsOffset
  sta SsWaterScaleLo,x
  lda #0
  sta SsWaterScaleHi,x
  sec
  sbc SsOffset
  sta SsWaterScaleLo+4,x
  lda #0
  sbc #0
  sta SsWaterScaleHi+4,x
  dec SsWaterScaleBuild
  bpl BuildScale
ScaleReady:
  rts
MultiplyRadius:
  ; EnsureWaterScale only multiplies nonnegative first-half sine samples.
  sta SsTmp
  clc
  adc SsWaterRadius
  tax
  jcc SmallSum
  lda SsQuarterLo+256,x
  sta SsProduct
  lda SsQuarterHi+256,x
  jmp Difference
SmallSum:
  lda SsQuarterLo,x
  sta SsProduct
  lda SsQuarterHi,x
Difference:
  sta SsProduct+1
  sec
  lda SsTmp
  sbc SsWaterRadius
  bcs :+
    eor #$ff
    clc
    adc #1
  :
  tay
  sec
  lda SsProduct
  sbc SsQuarterLo,y
  sta SsProduct
  lda SsProduct+1
  sbc SsQuarterHi,y
  sta SsProduct+1
  lda SsProduct
  asl
  lda SsProduct+1
  rol
  sta SsOffset
  lda #0
  rol
  sta SsOffset+1
  rts

MotionKill:
  ldx RgSlot
  lda #0
  sta RgShotType,x
  rts

GrabBrick:
  jsr FindSlot
  jcc Return
  lda Player_X_Position
  clc
  adc #8
  sta RgTempX
  lda Player_PageLoc
  adc #0
  sta RgTempPage
  lda #10
  ldy PlayerFacingDir
  cpy #1
  beq :+
    lda #$f6
  :
  sta SsTmp
  clc
  adc RgTempX
  sta RgTempX
  lda #0
  bit SsTmp
  bpl :+
    lda #$ff
  :
  adc RgTempPage
  sta RgTempPage
  lda Player_Y_Position
  clc
  adc #20
  sta RgTempY
  farcall ExpandedMapCell
  cmp #$51
  jeq Grab
  cmp #$52
  jne Return
  lda R0
  sec
  sbc #<Block_Buffer_1
  sta M0
  lda R1
  sbc #>Block_Buffer_1
  clc
  adc #>MmSolidTerrain
  sta M1
  lda M0
  clc
  adc #<MmSolidTerrain
  sta M0
  bcc :+
    inc M1
  :
  ldy #0
  lda (M0),y
  jne Return
Grab:
  lda VRAM_Buffer1_Offset
  cmp #80
  jcs Return
  lda R0
  sta M0
  lda R1
  sta M1
ArmLiftCheckSpan:
  ; Eligibility is checked before removing the cell. Holding is free.
  lda StarInvincibleTimer
  sec
  bne ArmLiftReady
  lda SelectedCharacter
  asl
  asl
  asl
  asl
  tax
  lda InvAmmo+1,x
  cmp #8
  jcc Return
ArmLiftReady:
  .res 27-(*-ArmLiftCheckSpan),$ea
  ldy #0
  lda #0
  sta (M0),y
  ; Native metatile writer takes a column base plus the row offset.
  lda RgTempY
  and #$f0
  sec
  sbc #32
  sta R2
  lda M0
  sec
  sbc R2
  sta R6
  lda M1
  sbc #0
  sta R7
  ldx #0
  farcall DestroyBlockMetatile
  lda #SS_ARM
  jsr Spawn
  ldx RgSlot
  lda #1
  sta SsMode,x
  txa
  clc
  adc #1
  sta SsHeld
  rts

ArmShatter:
  ; Four independent falling fragments preserve the thrown brick's contact
  ; point without borrowing the native question-block bounce slots.
  lda RgShotX,x
  sta SsWaterX
  lda RgShotPage,x
  sta SsWaterPage
  lda RgShotY,x
  sta SsWaterY
  lda #0
  sta RgShotType,x
  sta SsCount
Fragment:
  jsr FindSlot
  jcc Return
  lda #SS_ARM_DEBRIS
  jsr Spawn
  ldx RgSlot
  lda SsWaterX
  sta RgShotX,x
  lda SsWaterPage
  sta RgShotPage,x
  lda SsWaterY
  sta RgShotY,x
  lda #2
  sta RgShotVXHi,x
  lda SsCount
  and #1
  beq :+
    jsr NegateX
  :
  lda #$fc
  ldy SsCount
  cpy #2
  bcc :+
    lda #$fe
  :
  sta RgShotVYHi,x
  inc SsCount
  lda SsCount
  cmp #4
  jcc Fragment
  lda #Sfx_BrickShatter
  sta NoiseSoundQueue
  rts

Bridge:
  ldx RgSlot
  lda RgShotX,x
  sta MmBulletX
  lda RgShotPage,x
  sta MmBulletPage
  lda RgShotY,x
  sta MmBulletY
  lda RgShotDir,x
  sta MmBulletDir
  lda RgShotType,x
  sec
  sbc #9
  tay
  lda DamageTypes,y
  cmp #51
  bne :+
    lda RgShotAge,x
    cmp #45
    lda #51
    bcc :+
    ldy RgShotAge,x
    cpy #63
    bcs :+
    lda #46                     ; Source medium balloon damage for 45..62.
  :
  cmp #49
  bne :+
    ldy SsMode,x
    beq :+
    tya
    clc
    adc #54                    ; Rotated flame bounds: right/down/left.
  :
  sta MmBulletType
  ldy #0
  cmp #50
  bne :+
    iny
  :
  lda #0
  sta MmSlot
  tax
  rts
DamageTypes: .byte 42,43,44,45,46,47,48,49,50,51,52,53,54

WaterAreaEmpty:
  ; A radius-22 ball has radius-4 collision corners. Scan a conservative
  ; 52-pixel envelope once; if it contains no hittable tile, all eight exact
  ; corner probes would reject. Near vertical wrap or on expansion use the
  ; ordinary per-ball path. Five columns cover every alignment of that span.
  lda SsWaterY
  cmp #58
  jcc WaterAreaDone
  cmp #214
  jcs WaterAreaDone
  clc
  adc #26
  and #$f0
  sec
  sbc #32
  sta R5                         ; Last row in the exact vertical envelope.
  lda SsWaterY
  sec
  sbc #26
  and #$f0
  sec
  sbc #32
  sta R4
  lda SsWaterX
  sec
  sbc #26
  lsr
  lsr
  lsr
  lsr
  sta R0
  lda SsWaterX
  cmp #26
  lda SsWaterPage
  sbc #0
  and #1
  asl
  asl
  asl
  asl
  ora R0
  sta R0                         ; First ring-buffer column, in 0..31.
WaterAreaRow:
  lda R0
  sta R1
  lda #5
  sta R3
WaterAreaColumn:
  lda R1
  and #15
  clc
  adc R4
  tay
  lda R1
  cmp #16
  bcs WaterAreaPage1
  lda Block_Buffer_1,y
  jmp WaterAreaTile
WaterAreaPage1:
  lda Block_Buffer_1+208,y
WaterAreaTile:
  jsr WaterTile
  bcs WaterAreaDone
  inc R1
  lda R1
  and #31
  sta R1
  dec R3
  bne WaterAreaColumn
  lda R4
  cmp R5
  beq WaterAreaClear
  clc
  adc #16
  sta R4
  bne WaterAreaRow
WaterAreaClear:
  inc SsWaterEmpty
WaterAreaDone:
  rts

WaterCollisionCandidate:
  ; Water only damages masonry/question tiles. Use the same four corners
  ; as CollisionCandidate, but read each distinct map cell directly. Most
  ; small balls occupy one cell; rebuilding a pointer four times dominated
  ; the eight-ball shield's update even in an empty stretch of level.
  ldx RgSlot
  sec
  lda RgShotX,x
  sbc #4
  lsr
  lsr
  lsr
  lsr
  sta R0                         ; Left column; recover page carry separately.
  lda RgShotX,x
  cmp #4
  lda RgShotPage,x
  sbc #0
  and #1
  sta R2
  clc
  lda RgShotX,x
  adc #4
  sta R1
  lda RgShotPage,x
  adc #0
  and #1
  sta R3
  lda R1
  lsr
  lsr
  lsr
  lsr
  sta R1                         ; Right column/page, including page seams.
  lda #$ff
  sta R4                         ; Previously inspected row.
  sec
  lda RgShotY,x
  sbc #4
  jsr WaterRow
  bcs WaterReturn
  ldx RgSlot
  clc
  lda RgShotY,x
  adc #4
WaterRow:
  cmp #32
  bcc WaterNo
  cmp #240
  bcs WaterNo
  and #$f0
  cmp R4
  beq WaterNo
  sta R4
  sec
  sbc #32
  sta R5
  clc
  adc R0
  tay
  lda R2
  bne WaterLeftPage1
  lda Block_Buffer_1,y
  jmp WaterLeftTile
WaterLeftPage1:
  lda Block_Buffer_1+208,y
WaterLeftTile:
  jsr WaterTile
  bcs WaterReturn
  lda R0
  cmp R1
  bne WaterRight
  lda R2
  cmp R3
  beq WaterNo
WaterRight:
  clc
  lda R5
  adc R1
  tay
  lda R3
  bne WaterRightPage1
  lda Block_Buffer_1,y
  jmp WaterTile
WaterRightPage1:
  lda Block_Buffer_1+208,y
WaterTile:
  cmp #$51
  bcc WaterNo
  cmp #$61
  bcs WaterQuestion
  cmp #$54
  beq WaterNo
  sec
  rts
WaterQuestion:
  cmp #$c0
  beq WaterYes
  cmp #$c1
  bne WaterNo
WaterYes:
  sec
WaterReturn:
  rts
WaterNo:
  clc
  rts

CollisionCandidate:
  ; Four source collision corners, with a cheap metatile rejection before
  ; entering the native block/bounce bridge. Ordinary terrain is absent
  ; from these weapons' hit-test dictionary except Arm and Flame's seed.
  ldx RgSlot
  lda RgShotType,x
  sec
  sbc #9
  tay
  lda ProbeRadius,y
  sta SsRadius
  lda #0
  sta SsCollideSolid
  sta SsProbe
  lda RgShotType,x
  cmp #SS_ARM
  jeq SolidCandidate
  cmp #SS_FLAME_BULLET
  jne ProbeCorner
SolidCandidate:
  inc SsCollideSolid
ProbeCorner:
  ldx RgSlot
  lda RgShotX,x
  sta RgTempX
  lda RgShotPage,x
  sta RgTempPage
  lda SsProbe
  and #1
  jeq ProbeLeft
  clc
  lda RgTempX
  adc SsRadius
  sta RgTempX
  jcc ProbeY
  inc RgTempPage
  jmp ProbeY
ProbeLeft:
  sec
  lda RgTempX
  sbc SsRadius
  sta RgTempX
  jcs ProbeY
  dec RgTempPage
ProbeY:
  lda RgShotY,x
  sta RgTempY
  lda SsProbe
  and #2
  jeq ProbeAbove
  clc
  lda RgTempY
  adc SsRadius
  jmp ReadProbe
ProbeAbove:
  sec
  lda RgTempY
  sbc SsRadius
ReadProbe:
  cmp #32
  jcc ProbeNext
  cmp #240
  jcs ProbeNext
  sta SsContactY
  and #$f0
  sec
  sbc #32
  sta R0
  lda RgTempX
  lsr
  lsr
  lsr
  lsr
  clc
  adc R0
  sta R0
  lda #0
  sta R1
  lda RgTempPage
  and #1
  jeq ProbePage
  clc
  lda R0
  adc #208
  sta R0
  rol R1
ProbePage:
  clc
  lda R0
  adc #<Block_Buffer_1
  sta R0
  lda R1
  adc #>Block_Buffer_1
  sta R1
  ldy #0
  lda (R0),y
  jeq ProbeNext
  cmp #$23
  jeq ProbeNext
  cmp #$26
  jeq ProbeNext
  cmp #$c2
  jeq ProbeNext
  cmp #$c3
  jeq ProbeNext
  ldy SsCollideSolid
  jne Candidate
  cmp #$54                      ; Native overworld foundation, not masonry.
  jeq ProbeNext
  cmp #$51
  jcc ProbeQuestion
  cmp #$61
  jcc Candidate
ProbeQuestion:
  cmp #$c0
  jeq Candidate
  cmp #$c1
  jeq Candidate
ProbeNext:
  inc SsProbe
  lda SsProbe
  cmp #4
  jcc ProbeCorner
  clc
  rts
Candidate:
  lda RgTempX
  and #$f0
  sta SsContactX
  lda RgTempPage
  sta SsContactPage
  lda SsContactY
  and #$f0
  sta SsContactY
  sec
  rts
ProbeRadius: .byte 8,5,7,4,7,10,3,8,4,10,12,12,3

FlameContact:
  ; Resolve from the seed's previous box, then snap the source pivot to
  ; the contacted surface. SsMode is clockwise quarter turns.
  lda SsHitTimer,x
  clc
  adc #3
  cmp SsContactY
  bcc Floor
  beq Floor
  lda SsContactY
  clc
  adc #16
  sta SsTmp
  lda SsHitTimer,x
  sec
  sbc #3
  cmp SsTmp
  bcs Ceiling
  lda RgShotVXHi,x
  bmi LeftWall
  lda SsContactX
  sta RgShotX,x
  lda SsContactPage
  sta RgShotPage,x
  lda #3
  bne SetRotation
LeftWall:
  clc
  lda SsContactX
  adc #16
  sta RgShotX,x
  lda SsContactPage
  adc #0
  sta RgShotPage,x
  lda #1
  bne SetRotation
Ceiling:
  lda SsTmp
  sta RgShotY,x
  lda #2
  bne SetRotation
Floor:
  lda SsContactY
  sta RgShotY,x
  lda #0
SetRotation:
  sta SsMode,x
  lda #0
  sta RgShotHits,x
  sta SsHitTimer,x
  rts

Art:
  lda RgShotType,x
  cmp #SS_ARM
  jeq NativeArt
  cmp #SS_ARM_DEBRIS
  jeq NativeArt
  cmp #SS_KICK
  jeq KickArt
  cmp #SS_RUSH
  jeq RushArt
  cmp #SS_WATER
  jeq WaterArt
  cmp #SS_FLAME_BULLET
  jeq FlameBulletArt
  cmp #SS_FLAME
  jeq FlameArt
  cmp #SS_BALLOON
  jeq BalloonArt
  cmp #SS_PHARAOH_BIG
  jeq BigArt
  cmp #SS_PHARAOH_MED
  jeq MedArt
  cmp #SS_PHARAOH
  jeq SmallArt
  cmp #SS_METAL
  jeq MetalArt
  lda RgShotAge,x
  cmp #10
  jcs KnuckleArt
  lsr
  clc
  adc #SS_ART_KNUCKLE17
  jne SaveArt
KnuckleArt:
  lsr
  and #1
  clc
  adc #SS_ART_KNUCKLE22
  jne SaveArt
MetalArt:
  lda RgShotAge,x
  lsr
  lsr
  and #1
  clc
  adc #SS_ART_METAL15
  jne SaveArt
SmallArt:
  lda #SS_ART_PHARAOH50
  jne SaveArt
MedArt:
  lda #SS_ART_PHARAOH51
  jne SaveArt
BigArt:
  lda RgShotAge,x
  lsr
  lsr
  lsr
  and #1
  clc
  adc #SS_ART_PHARAOH52
  jne SaveArt
BalloonArt:
  lda RgShotAge,x
  cmp #63
  jcs BigArt
  sec
  sbc #15
  ldy #0
Six:
  cmp #6
  jcc BalloonFrame
  sbc #6
  iny
  jne Six
BalloonFrame:
  tya
  clc
  adc #SS_ART_PHARAOH42
  jne SaveArt
FlameBulletArt:
  lda #SS_ART_FLAME24
  jne SaveArt
FlameArt:
  lda RgShotAge,x
  ldy #0
Three:
  cmp #3
  jcc FlameFrame
  sbc #3
  iny
  jne Three
FlameFrame:
  tya
  ldy SsMode,x
  beq :+
    clc
    adc FlameArtOffsets-1,y
  :
  clc
  adc #SS_ART_FLAME25
  jne SaveArt
FlameArtOffsets:
  .byte SS_ART_FLAME9025-SS_ART_FLAME25,SS_ART_FLAME18025-SS_ART_FLAME25,SS_ART_FLAME27025-SS_ART_FLAME25
WaterArt:
  lda #SS_ART_WATER40
  jne SaveArt
KickArt:
  lda RgShotAge,x
  lsr
  and #1
  clc
  adc #SS_ART_KICK11
  jne SaveArt
RushArt:
  lda SsMode,x
  jeq RushFlyingArt
  cmp #4
  jeq RushFlyingArt
  cmp #2
  jeq RushSpringArt
  cmp #3
  jeq RushExitArt
  lda RgShotAge,x
  cmp #12
  jcc RushLandArt
  cmp #132
  jcc RushStandArt
  and #2
  jne NativeArt                  ; Hardware alpha adaptation during exit warning.
RushStandArt:
  lda RgShotAge,x
  lsr
  lsr
  lsr
  lsr
  and #1
  clc
  adc #SS_ART_RUSH1
  jne SaveArt
RushLandArt:
  lsr
  lsr
  clc
  adc #SS_ART_RUSH5
  jne SaveArt
RushExitArt:
  lda RgShotAge,x
  lsr
  lsr
  clc
  adc #SS_ART_RUSH9
  jne SaveArt
RushSpringArt:
  lda #SS_ART_RUSH4
  jne SaveArt
RushFlyingArt:
  lda #SS_ART_RUSH13
  jne SaveArt
NativeArt:
  lda #0
SaveArt:
  sta SsArt,x
  rts
.endproc

.proc SpecialBassPose
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  jne Native
  lda SsHeld
  jeq Attack
  ldx #SS_BASS_ARM_CARRY
  lda Player_State
  jeq GroundCarry
  ldx #SS_BASS_ARM_CARRY_JUMP
  jmp Variant
GroundCarry:
  lda RgPose
  cmp #XG_POSE_WALKSTEP
  bne :+
    ldx #SS_BASS_ARM_CARRY_STEP
  :
  cmp #XG_POSE_WALK1
  jcc Variant
  cmp #XG_POSE_WALK3+1
  jcs Variant
  sec
  sbc #XG_POSE_WALK1
  asl
  clc
  adc #SS_BASS_ARM_CARRY_WALK1
  tax
  jmp Variant
Attack:
  lda RgShootPose
  jeq Pharaoh
  lda InvSelected+CHARACTER_BASS
  jeq Native
  cmp #7
  jeq Native
  cmp #6
  jeq Native
  ldx #SS_BASS_ARM_THROW
  lda Player_State
  beq :+
    ldx #SS_BASS_ARM_AIR_THROW
  :
  lda InvSelected+CHARACTER_BASS
  cmp #3
  jne Variant
  ldx #SS_BASS_ARM_FIST
  lda Player_State
  jeq Variant
  ldx #SS_BASS_ARM_AIR_FIST
Variant:
  lda InvSelected+CHARACTER_BASS
  cmp #4
  jne Pointer
  inx                            ; Each special-arm pose has a Pharaoh pair.
  jmp Pointer
Pharaoh:
  lda InvSelected+CHARACTER_BASS
  cmp #4
  jne Native
  ldx RgPose
Pointer:
  lda SsBassBanks,x
  sta SmChrBank
  lda PlayerFacingDir
  cmp #2
  jeq Left
  lda SsBassRightLo,x
  sta SmPosePtr
  lda SsBassRightHi,x
  sec
  rts
Left:
  lda SsBassLeftLo,x
  sta SmPosePtr
  lda SsBassLeftHi,x
  sec
  rts
Native:
  clc
  rts
.endproc

.proc SpecialPalette
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  jeq Check
  cmp #CHARACTER_MEGAMAN
  jne Done
Check:
  lda GuestPowerupActive
  ora StarInvincibleTimer
  beq :+
    lda #0
    sta SsLastPalette
    rts
  :
  ldx SelectedCharacter
  lda InvSelected,x
  clc
  adc #1
  cmp SsLastPalette
  jeq Done
  sta SsLastPalette
  lda InvSelected,x
  jne Palette
  lda #0
  sta MmLastPalette
  farcall GetPlayerColors
  rts
Palette:
  sec
  sbc #1
  sta SsTmp
  asl
  clc
  adc SsTmp
  tay
  ldx VRAM_Buffer1_Offset
  cpx #77
  jcs Retry
  lda #$3f
  sta VRAM_Buffer1,x
  lda #$11
  sta VRAM_Buffer1+1,x
  lda #3
  sta VRAM_Buffer1+2,x
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  bne :+
    tya
    clc
    adc #24
    tay
  :
  lda Colors,y
  sta VRAM_Buffer1+3,x
  lda Colors+1,y
  sta VRAM_Buffer1+4,x
  lda Colors+2,y
  sta VRAM_Buffer1+5,x
  txa
  clc
  adc #6
  tax
  stx VRAM_Buffer1_Offset
  lda #0
  sta VRAM_Buffer1,x
Done:
  rts
Retry:
  lda #0
  sta SsLastPalette
  rts
Colors:
  ; Bass palette-sheet row 1, columns 3..8 and 10. Pharaoh's black,
  ; white and orange body is layered on palettes 2/3 to retain purple shots.
  .byte $0f,$30,$17, $0f,$37,$18, $0f,$10,$01, $0f,$14,$34
  .byte $0f,$30,$26, $0f,$27,$16, $0f,$31,$11, $0f,$16,$30
  ; Mega Man sheet: black, dark suit and light suit.
  .byte $0f,$18,$37, $0f,$16,$30, $0f,$01,$10, $0f,$17,$37
  .byte $0f,$26,$30, $0f,$16,$27, $0f,$11,$31, $0f,$16,$30
.endproc

.proc SpecialEnemyHit
  ; Preserve the incoming native enemy slot. Persistent contact attacks
  ; use per-projectile masks; flames can deal a new hit every 100 ms.
  lda GuestBodyAttack
  jne Native                     ; The shared body-contact cadence owns this receipt.
  lda SpecialWeapons::DamageTypes
  lda MmBulletType
  cmp #42
  jcc Native
  lda Bits,x
  sta SsTmp
  ldy RgSlot
  lda RgShotHits,y
  and SsTmp
  jne Skip
  lda RgShotHits,y
  ora SsTmp
  sta RgShotHits,y
  lda #12
  sta RgEnemyStun,x
  lda RgShotType,y
  cmp #SS_FLAME
  jne Hit
  lda #6
  sta SsHitTimer,y
Hit:
  clc
  rts
Skip:
  sec
  rts
Native:
  clc
  rts
Bits: .byte 1,2,4,8,16,32
.endproc

; X is the canonical enemy body slot. The shared contact wrapper has already
; accepted a newly entered contact and owns its previous/current target bits.
; Keep the player's ordinary projectile pools entirely independent of this
; temporary bridge into their established health, defeat and sound rules.
.proc MegaKickBodyDamage
  lda Enemy_ID,x
  cmp #BuzzyBeetle
  beq Done
  cmp #BulletBill_FrenzyVar
  beq Done
  cmp #BulletBill_CannonVar
  beq Done
  cmp #Podoboo                    ; Source LavaFireBall is a hostile Projectile.
  beq Done
  phx
  phy
  lda ObjectOffset
  pha
  lda RgSlot
  pha
  lda MmSlot
  pha
  lda GuestBodyAttack
  pha
  lda MmEnemySlot
  pha
  ldy #3
SaveTypes:
  lda MmBulletType,y
  pha
  dey
  bpl SaveTypes
  lda #1
  sta GuestBodyAttack
  stx ObjectOffset
  stx MmEnemySlot
  lda #52                       ; Source Charge Kick deals75 with ordinary pierce0.
  sta MmBulletType
  lda #0
  sta MmSlot
  farcall MegaManWeapons::DamageEnemy
  ldy #0
RestoreTypes:
  pla
  sta MmBulletType,y
  iny
  cpy #4
  bne RestoreTypes
  pla
  sta MmEnemySlot
  pla
  sta GuestBodyAttack
  pla
  sta MmSlot
  pla
  sta RgSlot
  pla
  sta ObjectOffset
  ply
  plx
Done:
  rts
.endproc

.proc BassDeflectProjectile
  lda #26                       ; 2.02's MM6 deflection effect.
  sta SsAudioRequest
  ldx RgSlot
  lda RgShotType,x
  cmp #SS_FLAME_BULLET
  beq ReverseSeed
  cmp #4                        ; Bass's default buster in the primary pool.
  beq Bounce
  cmp #SS_METAL
  beq Bounce
  cmp #SS_BALLOON
  beq Bounce
  cmp #SS_PHARAOH
  bcc Destroy
  cmp #SS_PHARAOH_BIG+1
  bcs Destroy
Bounce:
  lda RgShotVXLo,x
  ora RgShotVXHi,x
  bne Reverse
  lda #$c0
  sta RgShotVXLo,x
  lda #3
  sta RgShotVXHi,x
  lda RgShotDir,x
  cmp #2
  beq Lift
Reverse:
  jsr SpecialWeapons::NegateX
Lift:
  lda #$15                      ; -350/120 NES pixels/update, Q8.8.
  sta RgShotVYLo,x
  lda #$fd
  sta RgShotVYHi,x
  lda #$80
  sta RgShotImpact,x
  sec
  rts
ReverseSeed:
  jsr SpecialWeapons::NegateX
  sec
  rts
Destroy:
  clc
  rts
.endproc

.proc SpecialDrawShots
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bcc NativeDraw
  cmp #CHARACTER_PIT
  bcc AdvancedDraw
  cmp #CHARACTER_RYU
  beq AdvancedDraw
  cmp #CHARACTER_SOPHIA
  bne NativeDraw
AdvancedDraw:
  farcall RemainingDraw
  rts
NativeDraw:
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  bne :+
    rts                         ; Samus publishes this shared window herself.
  :
  lda #0
  sta SsChrActive
  lda MmDeathFlag
  jne Publish
  lda #$ff
  sta SsDrawFamily
  BankPRGC #.bank(SsArt0Right)
  lda FrameCounter
  and #1
  bne :+
    farcall InventoryDrawPickups
  :
  inc SsDrawFirst
  lda SsDrawFirst
  cmp #10
  bcc :+
    lda #0
    sta SsDrawFirst
  :
  tax
  lda #10
  sta SsDrawRemaining
  BankPRGC #.bank(SsArt0Right)
.if ::MAPPER_MMC5
  jsr SpecialPoolAny
  bne Loop
  ; The empty loop ends one slot before its rotating start. Preserve that
  ; receipt and publication/CHR work even when no shot needs drawing.
  ldx SsDrawFirst
  dex
  bpl :+
    ldx #9
  :
  stx RgSlot
  lda #0
  sta SsDrawRemaining
  clc
  jmp Publish
.endif
Loop:
  stx RgSlot
  lda RgShotType,x
  cmp #32
  jcs Next
  cmp #9
  jcc Next
  lda SsHidden,x
  jne Next
  lda RgShotType,x
  cmp #SS_WATER
  bne GeneralDraw
  jsr SpecialDrawWaterShot
  jmp Next
GeneralDraw:
  BankPRGC #.bank(SsArt0Right)
  ldy SsArt,x
  jeq NativeBlock
  lda SsArtFamilies,y
  ldx SsDrawFamily
  cpx #$ff
  jne CheckFamily
  sta SsDrawFamily
  tax
  lda SsPhysicalBanks,x
.if ::MAPPER_MMC5
  ora #1
.endif
  sta SsChrPhysical
  lda #1
  sta SsChrActive
  jmp ArtPointer
CheckFamily:
  cmp SsDrawFamily
  jne Next
ArtPointer:
  ldx RgSlot
  lda RgShotDir,x
  cmp #2
  jeq Left
  lda SsArtRightLo,y
  sta R0
  lda SsArtRightHi,y
  jmp BankedPointer
Left:
  lda SsArtLeftLo,y
  sta R0
  lda SsArtLeftHi,y
BankedPointer:
  sta R1
  lda SsArtBanks,y
.if ::MAPPER_MMC5
  ora #MMC5_PRG_ROM              ; Table entries are ROM bank numbers, not RAM selectors.
.endif
  BankPRGC a
  jmp Coordinates
NativeBlock:
  lda #<SsNativeBrick
  sta R0
  lda #>SsNativeBrick
  ldy RgShotType,x
  cpy #SS_ARM_DEBRIS
  jne Pointer
  lda #<SsNativeChunk
  sta R0
  lda #>SsNativeChunk
Pointer:
  sta R1
Coordinates:
  ldx RgSlot
  lda RgShotX,x
  sec
  sbc ScreenLeft_X_Pos
  sta R4
  lda RgShotPage,x
  sbc ScreenLeft_PageLoc
  sta R5
  lda RgShotY,x
  sta R6
  lda RgShotYHigh,x
  sta R7
  lda #0
  sta R3
  farcall MetaspriteRenderLoop
Next:
  dec SsDrawRemaining
  jeq Publish
  ldx RgSlot
  inx
  cpx #10
  bcc :+
    ldx #0
  :
  jmp Loop
Publish:
  lda MmDeathFlag
  bne :+
    lda FrameCounter
    and #1
    beq :+
      farcall InventoryDrawPickups
  :
  farcall MegaManHurtDraw
::SpecialDrawFinish:
  lda SsChrActive
  cmp SsLastChrActive
  jne Changed
  lda SsChrPhysical
  cmp SsLastChrPhysical
  jeq Done
Changed:
  lda SsChrActive
  sta SsLastChrActive
  lda SsChrPhysical
  sta SsLastChrPhysical
  inc ReloadCHRBank
Done:
  jsr CrossoverGraphicsBank
  rts
.endproc
.proc SpecialPickupArt
  pha
  BankPRGC #.bank(SsArt0Right)
  pla
  tay
  lda SsArtFamilies,y
  ldx SsDrawFamily
  cpx #$ff
  bne Check
  sta SsDrawFamily
  tax
  lda SsPhysicalBanks,x
.if ::MAPPER_MMC5
  ora #1
.endif
  sta SsChrPhysical
  lda #1
  sta SsChrActive
  jmp Pointer
Check:
  cmp SsDrawFamily
  bne No
Pointer:
  lda SsArtRightLo,y
  sta R0
  lda SsArtRightHi,y
  sta R1
  sec
  rts
No:
  clc
  rts
.endproc
.proc SpecialPublishChr
  lda SsChrActive
  cmp SsLastChrActive
  bne Changed
  lda SsChrPhysical
  cmp SsLastChrPhysical
  beq Done
Changed:
  lda SsChrActive
  sta SsLastChrActive
  lda SsChrPhysical
  sta SsLastChrPhysical
  inc ReloadCHRBank
Done:
  rts
.endproc
.include "special_sine.inc"
.popseg
.include "water_draw_proposal.inc"
