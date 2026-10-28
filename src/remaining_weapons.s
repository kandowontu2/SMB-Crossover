; Remaining Crossover 2.02 inventories. Primary attacks stay in their native
; character modules; this bank owns the additional projectile state machines.
.include "remaining_art_ids.inc"
.include "remaining_art.inc"
AV_ARROW=32
AV_BOMB=33
AV_EXPLOSION=34
AV_DAGGER=35
AV_HOLY=36
AV_FIRE=37
AV_CROSS=38
AV_WHEEL=39
AV_DRAGON=40
AV_MISSILE=41
AV_LASER=42
AV_FLARE=43
AV_SOPHIA=44
AV_HOMING=45
AV_ICE=46
.pushseg
.segment "SRAM"
AvRamStart:
AvStopwatch: .res 1
AvFrozen: .res 6
AvFrozenHi: .res 6
AvDropItem: .res 4
AvPickupAmmoItem: .res 6
AvRefillItem: .res 1
AvPending: .res 1
AvSlash: .res 1
AvFlip: .res 1
AvFlipClock: .res 1
AvSamusMode: .res 1
AvPower: .res 1
AvType: .res 1
AvItem: .res 1
AvSlot: .res 1
AvTmp: .res 1
AvTmp2: .res 1
AvSavedX: .res 1
AvSavedY: .res 1
AvCount: .res 1
AvLimit: .res 1
AvDrawFirst: .res 1
AvDrawIndex: .res 1
AvDrawLeft: .res 1
AvDrawArt: .res 1
AvDrawDirection: .res 1
AvDrawPhysical: .res 1
AvDrawFamily: .res 1
AvPalette: .res 1
AvFrictionKind: .res 1
AvFrictionNegative: .res 1
AvBombHurt: .res 1
AvScrewSound: .res 1
; Private source enemy explosions never consume a projectile/enemy slot.
SOPHIA_EFFECT_COUNT=6
SophiaDropBlocked: .res 1       ; scoped around native Bowser defeat only.
SophiaEffectAge: .res SOPHIA_EFFECT_COUNT
SophiaEffectX: .res SOPHIA_EFFECT_COUNT
SophiaEffectPage: .res SOPHIA_EFFECT_COUNT
SophiaEffectY: .res SOPHIA_EFFECT_COUNT
SophiaEffectYHigh: .res SOPHIA_EFFECT_COUNT
AvRamEnd:

.segment "SPECIAL_EXTRA"
.proc RemainingClear
  lda #0
  ldx #AvRamEnd-AvRamStart-1
Loop:
  sta AvRamStart,x
  dex
  jpl Loop
  rts
.endproc
.proc SpecialMegaPose
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  jne Native
  lda GuestPowerupActive
  jne Native
  lda GameEngineSubroutine
  cmp #8
  jne Native
  lda SsHeld
  jeq Attack
  ldx #SS_MEGA_CARRY
  lda Player_State
  bne AirCarry
  lda MmStepTimer
  beq :+
    ldx #SS_MEGA_CARRY_STEP
    jmp Pointer
  :
  lda Player_X_Speed
  beq Pointer
  lda MmWalkFrame
  cmp #3
  bcc :+
    lda #1
  :
  clc
  adc #SS_MEGA_CARRY_WALK1
  tax
  jmp Pointer
AirCarry:
  ldx #SS_MEGA_CARRY_JUMP
  jmp Pointer
Attack:
  lda MegaManShotPose
  jeq Native
  lda InvSelected+CHARACTER_MEGAMAN
  jeq Native
  cmp #5
  jcs Native
  ldx #SS_MEGA_THROW
  lda Player_State
  beq :+
    ldx #SS_MEGA_AIR_THROW
  :
  lda InvSelected+CHARACTER_MEGAMAN
  cmp #3
  jne Pointer
  ldx #SS_MEGA_FIST
  lda Player_State
  beq Pointer
  ldx #SS_MEGA_AIR_FIST
Pointer:
  BankPRGC #.bank(SsMegaTHROWRight)
  lda SsMegaBanks,x
  sta SmChrBank
  lda PlayerFacingDir
  cmp #2
  beq Left
  lda SsMegaRightLo,x
  sta SmPosePtr
  lda SsMegaRightHi,x
  jmp Ready
Left:
  lda SsMegaLeftLo,x
  sta SmPosePtr
  lda SsMegaLeftHi,x
Ready:
  sta SmPosePtr+1
  lda #METASPRITE_SAMUS_BODY
  sta ObjectMetasprite
  sec
  rts
Native:
  clc
  rts
.endproc
.proc RemainingAirPose
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  jne Native
  lda Player_State
  jeq Native
  cmp #3
  jeq Native
  lda AvSlash
  jne Slash
  lda AvFlip
  jeq Native
  lda AvFlipClock
  jsr Phase
  clc
  adc #XG_POSE_UP
  sec
  rts
Slash:
  lda AvFlipClock
  jsr Phase
  tax
  lda SlashPoses,x
  sec
  rts
Native:
  clc
  rts
Phase:
  ldx #0
Divide:
  cmp #3
  jcc Done
  sbc #3
  inx
  jne Divide
Done:
  txa
  and #3
  rts
SlashPoses: .byte XG_POSE_ATTACK1,XG_POSE_ATTACK2,XG_POSE_ATTACK3,XG_POSE_DASH
.endproc

.proc RemainingIcePlatform
  lda Player_Y_HighPos
  cmp #1
  jne Done
  lda Enemy_Y_Position,x
  clc
  adc #8
  sta AvTmp2
  lda Player_X_Position
  sec
  sbc Enemy_X_Position,x
  sta AvTmp
  lda Player_PageLoc
  sbc Enemy_PageLoc,x
  clc
  adc #1
  cmp #2
  jcs Done
  lda AvTmp
  clc
  adc #15
  cmp #31
  jcs Done
  lda Player_Y_Position
  clc
  adc #32
  sec
  sbc AvTmp2
  cmp #8
  jcs Side
  lda Player_Y_Speed
  jmi Done
  lda AvTmp2
  sec
  sbc #32
  sta Player_Y_Position
  lda #0
  sta Player_State
  sta Player_Y_Speed
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  sta MmYFraction
  sta MmYFraction+1
  rts
Side:
  cmp #40
  jcs Done
  lda Player_Y_Position
  clc
  adc #8
  cmp AvTmp2
  jcs Done
  lda AvTmp
  jmi Left
  clc
  lda Enemy_X_Position,x
  adc #16
  sta Player_X_Position
  lda Enemy_PageLoc,x
  adc #0
  jmp Stop
Left:
  sec
  lda Enemy_X_Position,x
  sbc #16
  sta Player_X_Position
  lda Enemy_PageLoc,x
  sbc #0
Stop:
  sta Player_PageLoc
  lda #0
  sta Player_X_Speed
  sta MmVX
  sta MmVX+1
  sta MmVX+2
  sta MmXFraction
  sta MmXFraction+1
Done:
  rts
.endproc

.proc RemainingSamusPool
  lda #0
  sta AvCount
  ldx #2
Beams:
  lda SmShotType,x
  beq :+
    inc AvCount
  :
  dex
  jpl Beams
  ldx #9
Missiles:
  lda RgShotType,x
  cmp #AV_MISSILE
  jeq Count
  cmp #AV_ICE
  jne Next
Count:
  inc AvCount
Next:
  dex
  jpl Missiles
  lda AvCount
  cmp #3
  rts
.endproc

.proc AvBillSpeedIndex
  phx
  phy
  jsr RemainingPower
  sta AvTmp
  lda CrossoverBehaviorVersion
  bne HardRapid
  lda AvTmp
  clc
  adc #9                         ; Easy340/380/400, no Rapid equipment.
  sta AvTmp
  jmp Index
HardRapid:
  lda #6
  farcall InventoryHas
  jcs RapidTwo
  lda #1
  farcall InventoryHas
  jcc Index
  lda AvTmp
  clc
  adc #3
  sta AvTmp
  jmp Index
RapidTwo:
  lda AvTmp
  clc
  adc #6
  sta AvTmp
Index:
  ply
  plx
  lda AvTmp
  rts
.endproc

; Source-derived visual/primary weapon tier, independent of the mushroom bit.
.proc RemainingPower
  lda CrossoverBehaviorVersion
  bne HardPower
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  beq EasyPower
  cmp #CHARACTER_SIMON
  bne HardPower
EasyPower:
  lda PlayerStatus
  rts
HardPower:
  phx
  phy
  lda PlayerStatus
  sta AvPower
  ldx SelectedCharacter
  cpx #CHARACTER_SCROOGE
  jcs Done
  lda CrossoverBehaviorVersion
  bne HardEquipment
  cpx #CHARACTER_SIMON+1
  jcc Done                       ; Easy classics use native three-tier status.
HardEquipment:
  lda InvOwnedLo,x
  ora InvOwnedHi,x
  jeq Done                       ; Imported old states retain their old form.
  lda #0
  sta AvPower
  lda PlayerStatus
  jeq Done
  lda #1
  sta AvPower
  cpx #CHARACTER_BILL
  jeq Bill
  cpx #CHARACTER_LINK
  jeq Link
  cpx #CHARACTER_SIMON
  jeq Simon
  cpx #CHARACTER_RYU
  jeq Ryu
  cpx #CHARACTER_SOPHIA
  jeq Sophia
  cpx #CHARACTER_SAMUS
  jne Done
  lda #5
  jne Two
Link:
  lda #4
  jne Two
Simon:
  lda #1
  jne Two
Ryu:
  lda #0
  sta AvPower
  lda #6
  farcall InventoryHas
  jcc Done
  inc AvPower
  jne Done
Sophia:
  lda #4
  farcall InventoryHas
  jcs LevelTwo
  lda #0
  sta AvPower
  lda #7
  farcall InventoryHas
  jcc Done
  inc AvPower
  jne Done
Bill:
  lda #0
  sta AvPower
  lda InvSelected+CHARACTER_BILL
  cmp #4
  jne Spread
  inc AvPower
  jne Done
Spread:
  cmp #5
  jne Done
  jeq LevelTwo
Two:
  farcall InventoryHas
  jcc Done
LevelTwo:
  lda #2
  sta AvPower
Done:
  ply
  plx
  lda AvPower
  rts
.endproc

.proc RemainingGrant
  lda #0
  sta AvPalette
  sta AvSamusMode
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  jne Done
  lda #7
  farcall InventoryHas
  jcc Done
  lda InvAmmo+160
  cmp #99
  jcc Done
  lda #99
  sta InvAmmo+160
Done:
  rts
.endproc

; Carry: enemy AI should be paused, leaving player control and weapon updates live.
.proc RemainingContactProtection
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  bne No
  lda SmFlip
  beq No
  lda Player_State
  beq No
  phx
  phy
  lda #6
  farcall InventoryHas
  ply
  plx
  rts
No:
  clc
  rts
.endproc
; Cold frozen-actor eligibility relocated to make room for Easy STOP gates.
; The resident no-freeze path in OBJECT avoids this bank call entirely.
.pushseg
.segment "SPECIAL_EXTRA"
.proc RemainingEnemyFrozen
  lda Enemy_State,x
  and #$20
  jne No
  lda Enemy_ID,x
  cmp #$24
  jcc Check
  cmp #Bowser
  jne No
Check:
  lda AvStopwatch
  ora AvFrozen,x
  ora AvFrozenHi,x
  jeq No
  sec
  rts
No:
  clc
  rts
.endproc
.popseg

.proc RemainingWeapons
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  bcc Unsupported
  cmp #CHARACTER_SIMON+1
  bcc Supported
  cmp #CHARACTER_RYU
  beq Supported
  cmp #CHARACTER_SOPHIA
  beq Supported
Unsupported:
  rts
Supported:
  lda TimerControl
  jne Done
  lda GameEngineSubroutine
  cmp #8
  jne Done
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  beq PrepareEnemies
  cmp #CHARACTER_BILL
.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
  beq BillEarlyCacheJump
.else
  beq PrepareEnemies
.endif
  cmp #CHARACTER_SOPHIA
  bne EnemiesReady
PrepareEnemies:
  ; Only Select can create a remaining-inventory shot in this batch. Keep
  ; preparation before that input and before every active pool, preserving
  ; eligibility refresh after an earlier weapon batch mutates native actors.
  lda InvFresh
  and #Select_Button
  bne PrepareActiveEnemies
  ldx #9
CheckActivePool:
  lda RgShotType,x
  bne PrepareActiveEnemies
  dex
  bpl CheckActivePool
.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  bne EnemiesReady
  jmp SamusEmpty
BillEarlyCacheJump:
  jmp ::BillEarlyCacheGate
.else
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  jeq SamusEmpty
  jmp EnemiesReady
.endif
PrepareActiveEnemies:
  farcall GuestPrepareEnemies
EnemiesReady:
  jsr AdvanceFreeze
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  jne Sophia
  jsr SamusInput
  jsr Screw
  jmp Shots
Sophia:
  cmp #CHARACTER_SOPHIA
  jne Ryu
  jsr SophiaInput
  jsr Shots                     ; only Sophia pays for its private effect pass.
  lda SophiaEffectAge
  ora SophiaEffectAge+1
  ora SophiaEffectAge+2
  ora SophiaEffectAge+3
  ora SophiaEffectAge+4
  ora SophiaEffectAge+5
  beq EffectsDone
  farcall SophiaUpdateEffects
EffectsDone:
  rts
Ryu:
  cmp #CHARACTER_RYU
  jne Shots
  lda Player_State
  bne :+
    lda #0
    sta AvSlash
    sta AvFlip
    sta AvFlipClock
    sta XgWall
    sta RyWallSide
    sta RyWallResolved
  :
  lda InvFresh
  and #A_Button
  jeq RyuFlipTick
  lda #1
  sta AvFlip
  lda #0
  sta AvFlipClock
RyuFlipTick:
  lda RgAttack
  ora XgWall
  beq :+
    lda #0
    sta AvFlip
    ; attachToWall cancels active Jump Slash; an airborne attack does not.
    ldx XgWall
    beq :+
    sta AvSlash
  :
  inc AvFlipClock
  ; Jump Slash damages actual body contacts in GuestBodyContact. Its
  ; visual flip remains live here, independent of enemy/projectile pools.
Shots:
  ldx #9
Loop:
  stx AvSlot
  stx RgSlot
  lda RgShotType,x
  cmp #32
  jcc Next
  cmp #47
  jcs Next
  lda RgShotImpact,x
  jeq Active
  dec RgShotImpact,x
  jne Next
  jmp Kill
Active:
  inc RgShotAge,x
  bne AgeReady
  lda RgShotType,x
  cmp #AV_FLARE
  bne AgeReady
  inc SsMode,x                  ; Type43-exclusive age high, initialized by Spawn.
AgeReady:
  lda RgShotType,x
  cmp #AV_FLARE
  beq MotionReady
  lda SsHitTimer,x
  beq :+
    dec SsHitTimer,x
    bne :+
    lda #0
    sta RgShotHits,x
  :
MotionReady:
  jsr Motion
  ldx AvSlot
  lda RgShotType,x
  jeq Next
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne MotionActive
  lda RgShotImpact,x
  jne Next
MotionActive:
  lda RgShotType,x
  cmp #AV_LASER
  bne :+
    lda SsHidden,x
    jne Next
  :
  lda RgShotType,x
  cmp #AV_BOMB
  jeq Next
  jsr Bridge
  ldy AvSlot                   ; Bridge leaves X=0 for the shared collision slot.
  lda RgShotType,y
  cmp #AV_ICE
  jeq Terrain
  cmp #AV_WHEEL
  jeq Terrain
  cmp #AV_DRAGON
  jeq Terrain
  cmp #AV_HOMING
  jeq Enemies
Terrain:
  farcall MegaManWeapons::Blocks
  lda MmBulletType
  jne Enemies
  ldx AvSlot
  lda RgShotType,x
  cmp #AV_HOLY
  jeq Ignite
  cmp #AV_EXPLOSION
  jeq Enemies
  cmp #AV_FIRE
  jeq Enemies
  cmp #AV_CROSS
  jeq Enemies
  jmp Hit
Enemies:
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  beq CachedPresence
  cmp #CHARACTER_BILL
  beq CachedPresence
  cmp #CHARACTER_SOPHIA
  bne HaveEnemies
CachedPresence:
  lda RgEnemiesPresent
  jeq Next
HaveEnemies:
  jsr Bridge
  farcall MegaManWeapons::Enemies
  lda MmBulletType
  jne Next
Hit:
  ldx AvSlot
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne OtherImpact
  farcall SophiaImpact
  jmp Next
OtherImpact:
  lda #3
  sta RgShotImpact,x
  jmp Next
Ignite:
  lda #AV_FIRE
  sta RgShotType,x
  lda #0
  sta RgShotAge,x
  sta RgShotVXHi,x
  sta RgShotVXLo,x
  sta RgShotVYHi,x
  sta RgShotVYLo,x
  sta RgShotHits,x
  lda #AV_SFX_SIMONHOLYWATEREXPLODE
  sta AvAudioRequest
  jmp Next
Kill:
  lda #0
  sta RgShotType,x
Next:
  ldx AvSlot
  lda RgShotType,x
  cmp #AV_FLARE
  bne OrbitReady
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bne OrbitReady
  lda AvPending
  beq OrbitReady
  jsr BillAdvancedFlarePublish
OrbitReady:
  ldx AvSlot
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bne ImpactReady
  lda RgShotType,x
  cmp #AV_LASER
  beq BillFinalPosition
  cmp #AV_FLARE
  bne ImpactReady
BillFinalPosition:
  farcall BillAdvancedExpiry
ImpactReady:
  dex
  jpl Loop
Done:
  lda #0
  sta MmBulletType
::RemainingWeaponsFinish:
  rts

SamusEmpty:
  ; With no Select edge and an entirely empty shared pool, SamusInput cannot
  ; spawn a shot. Freeze timers and Screw Attack still run every update.
  jsr AdvanceFreeze
  jsr Screw
.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
  clc                         ; Samus empty slots compare type0 to32.
BillNoAdvancedFinish:
.endif
  ldx #0
  stx AvSlot
  stx RgSlot
  dex
.if !(::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5)
  clc                         ; Original ordinary-target instruction order.
.endif
  jmp Done

AdvanceFreeze:
  lda AvStopwatch
  beq :+
    dec AvStopwatch
  :
  ldx #5
Freeze:
  lda AvFrozen,x
  ora AvFrozenHi,x
  beq :+
    lda AvFrozen,x
    jne DecFreeze
    dec AvFrozenHi,x
DecFreeze:
    jsr SamusFrozenDecrement
  :
  dex
  jpl Freeze
  rts

SamusInput:
  lda InvFresh
  and #Select_Button
  jeq Return
  lda SmBall
  jne Return
  lda #2
  farcall InventoryHas
  jcc Return
  ; Default nonclassic2.02 Special fires even while Down is held.
  ; Preserve the former classic-mode toggle span and every later PC.
  jmp Missile
.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
::BillEarlyCacheGate:
  lda InvFresh
  and #Select_Button
  beq BillEarlyNoSelect
  jmp RemainingWeapons::PrepareActiveEnemies
BillEarlyNoSelect:
  ldx #9
  jmp ::BillEarlyCachePool
  .assert *-::BillEarlyCacheGate=15,error,"Existing unreachable15B pad"
.else
  .res 15,$ea
.endif
Missile:
  jsr RemainingSamusPool
  jcs Return
  lda #AV_MISSILE
  sta AvType
  lda #2
  sta AvItem
  lda #3
  sta AvLimit
  jsr FireOwned
  rts
SophiaInput:
  lda InvFresh
  and #Select_Button
  jeq Return
  lda Player_State
  cmp #3
  jeq Return
  lda InvSelected+CHARACTER_SOPHIA
  cmp #2
  jeq Homing
  lda #1
  farcall InventoryHas
  jcc Return
  lda #AV_SOPHIA
  sta AvType
  lda #3
  sta AvLimit
  lda #1
  sta AvItem
 .if ::ENABLE_MMC5_EXPANDED
  jsr SophiaTripletAdmission
 .else
  jsr CountType
 .endif
  lda AvCount
  jne Return
  lda #1
  ldy #3
  farcall InventorySpend
  jcc Return
  lda #0
  sta AvCount
Triplet:
  jsr Spawn
  jcc Return
  ldx AvSlot
  farcall SophiaShotOrigin
  ldx AvSlot
  lda AvCount
  sta SsMode,x
  tay
  lda FanHi,y
  sta RgShotVYHi,x
  lda RgShotDir,x
  cmp #3
  jcc FanReady
  lda RgShotVYHi,x
  sta RgShotVXHi,x
  lda #0
  sta RgShotVYHi,x
FanReady:
  inc AvCount
  lda AvCount
  cmp #3
  jcc Triplet
  rts
FanHi: .byte 1,0,$ff
Homing:
  jsr FindHomingTarget
  jcc Return
  lda #AV_HOMING
  sta AvType
  lda #2
  sta AvItem
  lda #4
  sta AvLimit
  jsr FireOwned
  jcc Return
  ldx AvSlot
  farcall SophiaShotOrigin
  farcall SophiaFindTarget
  ldx AvSlot
  lda AvSavedX
  sta SsMode,x
  lda #4                      ; Remainder for round(n*16/9) source acceleration.
  sta SsAngleLo,x
Return:
  rts
FindHomingTarget:
  ldx #5
Target:
  lda Enemy_Flag,x
  jeq NextTarget
  jmi NextTarget              ; Bowser's duplicate is not a second target.
  lda Enemy_ID,x
  cmp #$15
  jcc TargetState
  cmp #BulletBill_CannonVar
  jeq TargetState
  cmp #Bowser
  jne NextTarget
TargetState:
  cmp #Goomba
  bne :+
    lda Enemy_State,x
    cmp #2
    jcs NextTarget            ; Flattened Goombas are no longer attackable.
  :
  lda Enemy_State,x
  and #$20
  jne NextTarget              ; The source excludes defeated/stopHit enemies.
  lda EnemyOffscrBitsMasked,x
  jeq HasTarget
NextTarget:
  dex
  jpl Target
  clc                         ; No on-screen target: preserve ammo and pool.
  rts
HasTarget:
  stx AvSavedX
  sec
  rts
Screw:
  lda SmFlip
  bne :+
    sta AvScrewSound
    rts
  :
  lda Player_State
  jeq Return
  lda #6
  farcall InventoryHas
  jcc Return
  lda AvScrewSound
  bne :+
    lda #AV_SFX_SAMUSSCREWATTACK
    sta AvAudioRequest
    inc AvScrewSound
  :
  rts                          ; Damage/protection uses the actual enemy body.
Slash:
  lda #74
PlayerHit:
  sta MmBulletType
  lda Player_X_Position
  clc
  adc #8
  sta MmBulletX
  lda Player_PageLoc
  adc #0
  sta MmBulletPage
  lda Player_Y_Position
  clc
  adc #16
  sta MmBulletY
  lda #0
  sta MmSlot
  lda PlayerFacingDir
  sta MmBulletDir
  ldx #0
  farcall MegaManWeapons::Enemies
  rts

CountType:
  lda #0
  sta AvCount
  ldx #9
CountLoop:
  lda RgShotType,x
  cmp AvType
  bne :+
    lda SelectedCharacter
    cmp #CHARACTER_SOPHIA
    bne CountActive
    lda RgShotImpact,x
    bne :+                    ; Source explosions do not occupy a missile limit.
CountActive:
    inc AvCount
  :
  dex
  jpl CountLoop
  rts
FireOwned:
  lda AvItem
  farcall InventoryHas
  jcc Return
  jsr CountType
  lda AvCount
  cmp AvLimit
  jcs Fail
  jsr FindSlot
  jcc Return
  lda AvItem
  farcall InventoryWeaponCost
  tay
  lda AvItem
  farcall InventorySpend
  jcc Return
  jsr Spawn
  rts
Fail:
  clc
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
  stx AvSlot
  stx RgSlot
  sec
  rts
Spawn:
  jsr FindSlot
  jcc Return
  lda AvType
  sta RgShotType,x
  lda #0
  sta RgShotAge,x
  sta RgShotFracX,x
  sta RgShotFracY,x
  sta RgShotImpact,x
  sta RgShotHits,x
  sta RgShotVXLo,x
  sta RgShotVXHi,x
  sta RgShotVYLo,x
  sta RgShotVYHi,x
  sta SsMode,x
  sta SsAngleLo,x
  sta SsAngleHi,x
  sta SsHidden,x
  sta SsHitTimer,x
  lda PlayerFacingDir
  sta RgShotDir,x
  lda Player_X_Position
  clc
  adc #8
  sta RgShotX,x
  lda Player_PageLoc
  adc #0
  sta RgShotPage,x
  lda Player_Y_Position
  clc
  adc #18
  sta RgShotY,x
  lda Player_Y_HighPos
  adc #0
  sta RgShotYHigh,x
  ldy RgCrouch
  beq :+
    lda RgShotY,x
    clc
    adc #9
    sta RgShotY,x
  :
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  bne :+
    ; Ice and missiles share Samus's standing/crouched/airborne muzzle.
    farcall SamusMuzzle
    ldx AvSlot
    lda SmTempX
    sta RgShotX,x
    lda SmTempPage
    sta RgShotPage,x
    lda SmTempY
    sta RgShotY,x
    lda SmClearance
    sta RgShotYHigh,x
    lda #12
    sta SmShootPose
  :
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  bne :+
    stx RgSlot
    farcall RyuProjectileOrigin
    ldx AvSlot
  :
  lda AvType
  sec
  sbc #32
  tay
  lda SpeedLo,y
  sta RgShotVXLo,x
  lda SpeedHi,y
  sta RgShotVXHi,x
  lda StartVYLo,y
  sta RgShotVYLo,x
  lda StartVYHi,y
  sta RgShotVYHi,x
  lda RgShotDir,x
  cmp #2
  bne :+
    jsr NegateX
  :
  lda AvType
  cmp #AV_MISSILE
  bne :+
    lda #12
    sta SmShootPose
  :
  cmp #AV_BOMB
  bne :+
    lda Player_Y_Position
    clc
    adc #32
    sta RgShotY,x
    lda #0
    sta AvBombHurt
  :
  cmp #AV_FLARE
  jne Aim
  lda RgShotX,x
  sta SsAngleLo,x
  lda RgShotPage,x
  sta SsAngleHi,x
  lda RgShotY,x
  sta SsHidden,x
Aim:
  lda AvType
  cmp #AV_MISSILE
  jeq Up
  cmp #AV_ICE
  jeq Up
  cmp #AV_SOPHIA
  jeq Up
  cmp #AV_HOMING
  jne Sound
Up:
  lda SavedJoypadBits
  and #Up_Dir
  jeq Sound
  lda RgShotVXLo,x
  sta RgShotVYLo,x
  lda RgShotVXHi,x
  sta RgShotVYHi,x
  lda #0
  sta RgShotVXLo,x
  sta RgShotVXHi,x
  lda #3
  sta RgShotDir,x
  lda RgShotVYHi,x
  jmi Sound
  jsr NegateY
Sound:
  lda AvType
  sec
  sbc #32
  tay
  lda SourceSounds,y
  beq NativeSound
  sta AvAudioRequest
  jmp SoundDone
NativeSound:
  lda #Sfx_Fireball
  sta Square1SoundQueue
SoundDone:
  lda #12
  sta RgShootPose
  sec
  rts
SourceSounds: .byte AV_SFX_LINKSHOOTARROW,AV_SFX_LINKSETBOMB,AV_SFX_LINKBOMBEXPLODE,AV_SFX_SIMONTHROWDAGGER,AV_SFX_SIMONTHROWDAGGER,AV_SFX_SIMONHOLYWATEREXPLODE,AV_SFX_SIMONCROSS,AV_SFX_RYUARTOFFIREWHEEL,AV_SFX_RYUFIREDRGONBALL,AV_SFX_SAMUSSHOOTMISSILE,AV_SFX_BILLLASER,AV_SFX_BILLFLARE,AV_SFX_SOPHIAMISSILE,AV_SFX_SOPHIAMISSILE,0
SpeedLo: .byte $2b,0,0,$2b,$15,0,$ab,$c0,$c0,$2b,$c6,$c3,0,0,$2b
SpeedHi: .byte 4,0,0,4,2,0,1,3,3,4,2,1,0,0,4
StartVYLo: .byte 0,0,0,0,$2b,0,0,$40,$c0,0,0,0,0,0,0
StartVYHi: .byte 0,0,0,0,$ff,0,0,$fc,3,0,0,0,0,0,0

Motion:
  lda RgShotType,x
  cmp #AV_EXPLOSION
  jeq Explosion
  cmp #AV_FIRE
  jeq Fire
  cmp #AV_BOMB
  jeq Bomb
  cmp #AV_HOLY
  jeq Holy
  cmp #AV_CROSS
  jeq Cross
  cmp #AV_SOPHIA
  jeq MissileMotion
  cmp #AV_HOMING
  jeq HomingMotion
  cmp #AV_FLARE
  jeq Flare
  cmp #AV_LASER
  jne Integrate
  lda SsHidden,x
  beq :+
    dec SsHidden,x
  :
  jmp Integrate
Explosion:
  lda RgShotAge,x
  cmp #48
  jcs MotionKill
  lda AvBombHurt
  jne Return
  lda #5
  farcall InventoryHas
  jcs Return
  ldx AvSlot
  lda Player_X_Position
  clc
  adc #8
  sec
  sbc RgShotX,x
  clc
  adc #19
  cmp #39
  jcs Return
  lda Player_Y_Position
  clc
  adc #18
  sec
  sbc RgShotY,x
  clc
  adc #24
  cmp #49
  jcs Return
  inc AvBombHurt
  jsr InjurePlayer
  rts
Fire:
  lda RgShotAge,x
  cmp #135
  jcs MotionKill
  rts
Bomb:
  lda RgShotAge,x
  cmp #60
  jcc BombFall
  lda #AV_EXPLOSION
  sta RgShotType,x
  lda #0
  sta RgShotAge,x
  sta RgShotHits,x
  lda #AV_SFX_LINKBOMBEXPLODE
  sta AvAudioRequest
  rts
BombFall:
  lda #36                        ; 1000 Flash pixels/s² / 7200, Q8.8.
  jne Gravity
Holy:
  lda #43                        ; 1200 / 7200.
Gravity:
  clc
  adc RgShotVYLo,x
  sta RgShotVYLo,x
  lda RgShotVYHi,x
  adc #0
  sta RgShotVYHi,x
  jsr Integrate
  ldx AvSlot
  lda RgShotVYHi,x
  jmi Return
  lda RgShotX,x
  sta RgTempX
  lda RgShotPage,x
  sta RgTempPage
  lda RgShotY,x
  clc
  adc #2
  sta RgTempY
  farcall ExpandedMapCell
  jcc Return
  ldx AvSlot
  lda RgTempY
  and #$f0
  sec
  sbc #2
  sta RgShotY,x
  lda #0
  sta RgShotVYLo,x
  sta RgShotVYHi,x
  lda RgShotType,x
  cmp #AV_HOLY
  jeq MotionIgnite
  rts
Cross:
  lda RgShotAge,x
  cmp #66                        ; 110 NES pixels at 200/120.
  jcc Integrate
  lda RgShotDir,x
  cmp #1
  jne CrossLeft
  sec
  lda RgShotVXLo,x
  sbc #25                        ; 700/7200 acceleration, Q8.8.
  sta RgShotVXLo,x
  lda RgShotVXHi,x
  sbc #0
  sta RgShotVXHi,x
  cmp #$fe
  jcs Integrate
  lda #$55
  sta RgShotVXLo,x
  lda #$fe
  sta RgShotVXHi,x
  jmp Integrate
CrossLeft:
  clc
  lda RgShotVXLo,x
  adc #25
  sta RgShotVXLo,x
  lda RgShotVXHi,x
  adc #0
  sta RgShotVXHi,x
  cmp #2
  jcc Integrate
  lda #$ab
  sta RgShotVXLo,x
  lda #1
  sta RgShotVXHi,x
  jmp Integrate
MissileMotion:
  lda #1
  sta AvFrictionKind
  lda RgShotDir,x
  cmp #3
  bcs DampenUpFan
  jsr DampY
  jmp FanDamped
DampenUpFan:
  jsr DampX
FanDamped:
  lda RgShotAge,x
  cmp #120
  jcs MotionKill
  lda RgShotDir,x
  cmp #4
  jeq MissileDown
  cmp #3
  jeq MissileUp
  cmp #2
  jne MissileRight
  jsr NegateX
  jsr Accelerate
  jsr NegateX
  jmp Integrate
MissileRight:
  jsr Accelerate
  jmp Integrate
MissileUp:
  sec
  lda RgShotVYLo,x
  sbc #25
  sta RgShotVYLo,x
  lda RgShotVYHi,x
  sbc #0
  sta RgShotVYHi,x
  jsr ClampXY
  jmp Integrate
MissileDown:
  clc
  lda RgShotVYLo,x
  adc #25
  sta RgShotVYLo,x
  lda RgShotVYHi,x
  adc #0
  sta RgShotVYHi,x
  jsr ClampXY
  jmp Integrate
Accelerate:
  clc
  lda RgShotVXLo,x
  adc #25
  sta RgShotVXLo,x
  lda RgShotVXHi,x
  adc #0
  sta RgShotVXHi,x
  jmp ClampX
ClampX:
  lda RgShotVXHi,x
  bmi ClampXNegative
  cmp #3
  bcc Accelerated
  bne ClampXPositive
  lda RgShotVXLo,x
  cmp #$8b
  bcc Accelerated
ClampXPositive:
  lda #$8b
  sta RgShotVXLo,x
  lda #3
  sta RgShotVXHi,x
  rts
ClampXNegative:
  cmp #$fc
  bcc ClampXMinus
  bne Accelerated
  lda RgShotVXLo,x
  cmp #$75
  bcs Accelerated
ClampXMinus:
  lda #$75
  sta RgShotVXLo,x
  lda #$fc
  sta RgShotVXHi,x
Accelerated:
  rts
ClampXY:
  jsr ClampX
  lda RgShotVXLo,x
  pha
  lda RgShotVXHi,x
  pha
  lda RgShotVYLo,x
  sta RgShotVXLo,x
  lda RgShotVYHi,x
  sta RgShotVXHi,x
  jsr ClampX
  lda RgShotVXLo,x
  sta RgShotVYLo,x
  lda RgShotVXHi,x
  sta RgShotVYHi,x
  pla
  sta RgShotVXHi,x
  pla
  sta RgShotVXLo,x
  rts
HomingMotion:
  ldy SsMode,x
  jmi HomeRetarget
  lda Enemy_Flag,y
  jeq HomeRetarget
  jmi HomeRetarget
  lda Enemy_State,y
  and #$20
  jne HomeRetarget
  lda Enemy_ID,y
  cmp #$15
  bcc HomeEnemyType
  cmp #Bowser
  beq HomeEnemyType
  cmp #BulletBill_CannonVar
  jne HomeRetarget
HomeEnemyType:
  cmp #Goomba
  bne :+
    lda Enemy_State,y
    cmp #2
    jcs HomeRetarget
  :
  lda EnemyOffscrBitsMasked,y
  jne HomeRetarget
HomeTracked:
  lda #0
  sta RgShotAge,x
  farcall SophiaHomingVector      ; cos/sin projection of the growing force.
  ldx AvSlot
  jsr HomeDamping
  jmp Integrate
HomeRetarget:
  farcall SophiaFindTarget
  ldx AvSlot
  bcc HomeInactive
  lda AvSavedX
  sta SsMode,x
  tay
  jmp HomeTracked
HomeInactive:
  lda #$ff
  sta SsMode,x
  lda RgShotAge,x
  cmp #120
  bcc :+
    farcall SophiaImpact
    rts
  :
  jmp Integrate
HomeDamping:
  lda #0
  sta AvFrictionKind
  jsr DampX
  jsr DampY
  jmp ClampXY
DampY:
  lda RgShotVXLo,x
  pha
  lda RgShotVXHi,x
  pha
  lda RgShotVYLo,x
  sta RgShotVXLo,x
  lda RgShotVYHi,x
  sta RgShotVXHi,x
  jsr DampX
  lda RgShotVXLo,x
  sta RgShotVYLo,x
  lda RgShotVXHi,x
  sta RgShotVYHi,x
  pla
  sta RgShotVXHi,x
  pla
  sta RgShotVXLo,x
  rts
DampX:
  lda RgShotVXHi,x
  and #$80
  sta AvFrictionNegative
  beq :+
    jsr NegateX
  :
  lda #0
  sta MmMul
  lda RgShotVXLo,x
  sta MmMul+1
  lda RgShotVXHi,x
  sta MmMul+2
  lda AvFrictionKind
  bne FanFriction
  jsr AvHomeFriction
  jmp Damped
FanFriction:
  jsr AvFanFriction
Damped:
  ldx AvSlot
  lda MmMul+1
  sta RgShotVXLo,x
  lda MmMul+2
  sta RgShotVXHi,x
  lda AvFrictionNegative
  beq :+
    jsr NegateX
  :
  rts
Flare:
  farcall BillAdvancedFlareStep
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
  lda RgShotType,x
  cmp #AV_LASER
  beq Alive                     ; Bill expires after allowed collision processing.
  cmp #AV_HOMING
  bne OffscreenExpiry
  lda SsMode,x
  bpl Alive                   ; Source active missiles update beyond the screen.
OffscreenExpiry:
  lda RgShotYHigh,x
  cmp #2
  jcs MotionKill
  lda RgShotAge,x
  cmp #240
  jcs MotionKill
  lda RgShotX,x
  sec
  sbc ScreenLeft_X_Pos
  lda RgShotPage,x
  sbc ScreenLeft_PageLoc
  jeq Alive
  cmp #$ff
  jeq Alive
  cmp #1
  jcs MotionKill
Alive:
  rts
NegateX:
  sec
  lda #0
  sbc RgShotVXLo,x
  sta RgShotVXLo,x
  lda #0
  sbc RgShotVXHi,x
  sta RgShotVXHi,x
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
MotionKill:
  lda #0
  sta RgShotType,x
  rts
MotionIgnite:
  lda #AV_FIRE
  sta RgShotType,x
  lda #0
  sta RgShotAge,x
  sta RgShotVXHi,x
  sta RgShotVXLo,x
  sta RgShotVYHi,x
  sta RgShotVYLo,x
  sta RgShotHits,x
  lda #AV_SFX_SIMONHOLYWATEREXPLODE
  sta AvAudioRequest
  rts
Bridge:
  ldx AvSlot
  lda RgShotX,x
  sta MmBulletX
  lda RgShotPage,x
  sta MmBulletPage
  lda RgShotY,x
  sta MmBulletY
  lda RgShotDir,x
  sta MmBulletDir
  lda RgShotType,x
  clc
  adc #27                        ; New collision profiles 59..73.
  sta MmBulletType
  lda #0
  sta MmSlot
  tax
  rts
Circle:
  .byte 0,2,3,5,6,8,9,10,11,12,13,14,15,15,16,16
  .byte 16,16,16,15,15,14,13,12,11,10,9,8,6,5,3,2
  .byte 0,-2,-3,-5,-6,-8,-9,-10,-11,-12,-13,-14,-15,-15,-16,-16
  .byte -16,-16,-16,-15,-15,-14,-13,-12,-11,-10,-9,-8,-6,-5,-3,-2
.endproc
; Private proposal C: zero-low-byte fast prefix, general domain retained.
; All original code/table PCs and stack calls are retained.
.proc AvHomeFriction
  lda MmMul
  beq KnownZero
  jmp SophiaHomeFrictionGeneralPrefix
KnownZero:
  lda #0
  sta MmProduct+1
  sta MmProduct+4
  ldx MmMul+1
  lda ProductMid,x
  sta MmProduct+2
  lda ProductHi,x
  sta MmProduct+3
  jmp HighByte
.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
::BillEarlyCachePool:
  lda RgShotType,x
BillEarlyRange:
  cmp #32
  bcc BillEarlyNext
  cmp #47
  bcc BillEarlyPrepare
BillEarlyNext:
  dex
  bpl ::BillEarlyCachePool
  ; No32..46 consumer: keep freeze clocks, omit the inert second scan.
  ; Final slot0 carry is0 below32,1 above46; AdvanceFreeze preserves it.
  jsr RemainingWeapons::AdvanceFreeze
  jmp RemainingWeapons::BillNoAdvancedFinish
BillEarlyPrepare:
  jmp RemainingWeapons::PrepareActiveEnemies
  .assert *-::BillEarlyCachePool=23,error,"Existing owned24B pool span"
  .res 1,$ea
  .assert *-::BillEarlyCachePool=24,error,"Existing owned24B pool span"
.else
  .res 24, $ea
.endif
HighByte:
  .assert HighByte-::AvHomeFriction=58, lderror, "Original high-byte offset"
  ldx MmMul+2
  clc
  lda MmProduct+2
  adc ProductLo,x
  sta MmMul
  lda MmProduct+3
  adc ProductMid,x
  sta MmMul+1
  lda MmProduct+4
  adc ProductHi,x
  sta MmMul+2
  rts
  .assert *-::AvHomeFriction=90, lderror, "Original table offset"
ProductLo:
  .repeat 256,I
    .byte .lobyte(I * 63068)
  .endrepeat
ProductMid:
  .repeat 256,I
    .byte .hibyte(I * 63068)
  .endrepeat
ProductHi:
  .repeat 256,I
    .byte .bankbyte(I * 63068)
  .endrepeat
.endproc
MmMultiplyRoutine AvFanFriction, 64980
; Append after every original SPECIAL_EXTRA byte; no old PC moves.
.proc SophiaHomeFrictionGeneralPrefix
  ldx MmMul
  lda AvHomeFriction::ProductMid,x
  sta MmProduct+1
  lda AvHomeFriction::ProductHi,x
  sta MmProduct+2
  lda #0
  sta MmProduct+3
  sta MmProduct+4
  ldx MmMul+1
  clc
  lda MmProduct+1
  adc AvHomeFriction::ProductLo,x
  lda MmProduct+2
  adc AvHomeFriction::ProductMid,x
  sta MmProduct+2
  lda MmProduct+3
  adc AvHomeFriction::ProductHi,x
  sta MmProduct+3
  lda #0
  adc #0
  sta MmProduct+4
  jmp AvHomeFriction::HighByte
.endproc
.popseg

.pushseg
.segment "SPECIAL_ROSTER"
.proc AvRosterSpecial
  lda CrossoverBehaviorVersion
  bne HardSpecial
  farcall EasyRosterSpecial, jmp
HardSpecial:
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  jne Simon
  lda InvSelected+CHARACTER_LINK
  cmp #1
  jeq Bomb
  cmp #2
  jeq Arrow
  lda #5
  farcall RosterWeapons::FindType
  jcs Done
  farcall RosterWeapons::SpawnBoomerang
  jmp Pose
Bomb:
  lda #AV_BOMB
  sta AvType
  lda #1
  sta AvItem
  lda #3
  jne Fire
Arrow:
  lda #AV_ARROW
  sta AvType
  lda #2
  sta AvItem
  lda #2
Fire:
  sta AvLimit
  farcall RemainingWeapons::FireOwned
  jcc Done
Pose:
  lda #1
  sta RgAttackKind
  farcall RosterWeapons::StartAttack
Done:
  rts
Simon:
  lda InvSelected+CHARACTER_SIMON
  jeq Done
  cmp #4
  jne Throw
  lda AvStopwatch
  jne Done
  lda #4
  ldy #5
  farcall InventorySpend
  jcc Done
  lda #180
  sta AvStopwatch
  lda #AV_SFX_SIMONSTOPWATCH
  sta AvAudioRequest
  lda #Sfx_TimerTick
  sta Square2SoundQueue
  rts
Throw:
  sta AvPending
  farcall InventoryHas
  jcc Done
  lda #1
  sta AvLimit
  lda #7
  farcall InventoryHas
  bcc :+
    inc AvLimit
  :
  lda #8
  farcall InventoryHas
  bcc :+
    inc AvLimit
  :
  lda #0
  sta AvCount
  ldx #9
Count:
  lda RgShotType,x
  beq :+
    inc AvCount
  :
  dex
  jpl Count
  lda AvCount
  cmp AvLimit
  jcs Done
  lda AvPending
  ldy #1
  farcall InventorySpend
  jcc Done
  jmp Pose
.endproc
.proc AvSimonRelease
  lda AvPending
  cmp #6
  jne Other
  farcall RosterWeapons::SpawnAxe
  rts
Other:
  tax
  lda Models,x
  jeq Done
  sta AvType
  farcall RemainingWeapons::Spawn
Done:
  rts
Models: .byte 0,0,AV_DAGGER,AV_HOLY,0,AV_CROSS,0
.endproc
.proc AvRyuSpecial
  lda InvSelected+CHARACTER_RYU
  jeq Done
  sta AvPending
  cmp #5
  jne Projectile
  ; Source Jump Slash requires ST_JUMP. Wall Special remains permitted for
  ; projectile subweapons, which already branched to Projectile above.
  lda XgWall
  beq AirJumpSlash
  rts
AirJumpSlash:
  lda Player_State
  jeq Done
  lda AvSlash
  jne Done
  lda #5
  ldy #5
  farcall InventorySpend
  jcc Done
  lda #1
  sta AvSlash
  sta AvFlip
  lda #AV_SFX_RYUJUMPSLASH
  sta AvAudioRequest
  lda #0
  sta AvFlipClock
  lda #Sfx_Fireball
  sta Square1SoundQueue
  rts
Projectile:
  ldx #9
Check:
  lda RgShotType,x
  jne Done
  dex
  jpl Check
  lda AvPending
  farcall InventoryHas
  jcc Done
  lda AvPending
  cmp #1
  jne FullCost
  ldy #3
  jmp Spend
FullCost:
  ldy #5
Spend:
  farcall InventorySpend
  jcc Done
  farcall ExpandedWeapons::BeginMelee
  lda #1
  sta RgAttackKind
Done:
  rts
.endproc
.proc AvRyuRelease
  lda AvPending
  cmp #1
  jeq Star
  cmp #3
  jeq Star
  cmp #2
  jne Dragon
  lda #AV_WHEEL
  jne Launch
Dragon:
  lda #AV_DRAGON
Launch:
  sta AvType
  farcall RemainingWeapons::Spawn
  rts
Star:
  lda InvSelected+CHARACTER_RYU
  cmp #3
  beq BigStarSound
  lda #AV_SFX_RYUTHROWSMALLSTAR
  bne StarSound
BigStarSound:
  lda #AV_SFX_RYUTHROWBIGSTAR
StarSound:
  sta AvAudioRequest
  farcall ExpandedWeapons::FireShot
  rts
.endproc
.pushseg
.segment "BILL_COLD"
.proc AvBillInput
  lda #0
  sta AvPending                  ; Bill-only delayed Flare orbit flag.
  lda CrossoverBehaviorVersion
  bne HardEquipment
  clc                            ; Local closure; AvSamusPrimary stays bank61.
  rts
HardEquipment:
  lda InvSelected+CHARACTER_BILL
  cmp #2
  jeq Laser
  cmp #3
  jeq Flare
  clc
  rts
Laser:
  lda #AV_LASER
  sta AvType
  lda RgWeaponButtons
  and #B_Button
  jeq Done
  ldx #9
ClearOldLaser:
  lda #0
  sta RgShotType,x
  dex
  jpl ClearOldLaser
  lda #4
  sta AvCount
LaserSegments:
  farcall RemainingWeapons::Spawn
  jcc Done
  jsr BillAim
  jsr LaserSpacing
  ldx AvSlot
  lda AvCount
  sta SsMode,x
  jsr BillAdvancedBirth
  dec AvCount
  jne LaserSegments
  jmp Done
Flare:
  lda #AV_FLARE
  sta AvType
  lda RgWeaponButtons
  and #B_Button
  jeq Done
  ; PLAYER_PROJ_DCT includes every projectile and each Flare's center.
  ; Gate before creation, so a Flare may legitimately take5 to7 entries.
  farcall RosterWeapons::CountShots
  lda RgCount
  cmp #6
  jcs Done
  farcall RemainingWeapons::Spawn
  jcc Done
  jsr BillAim
  jsr BillAdvancedBirth
Done:
  sec
  rts
LaserSpacing:
  lda #4
  sec
  sbc AvCount
  sta AvTmp2
  beq Spaced
  jsr BillLaserSpacingParameters
SpacingLoop:
  lda RgShotVXHi,x
  ora RgShotVXLo,x
  beq SpaceY
  lda RgShotVXHi,x
  bmi SpaceLeft
  sec
  lda RgShotX,x
  sbc AvTmp
  sta RgShotX,x
  lda RgShotPage,x
  sbc #0
  sta RgShotPage,x
  jmp SpaceY
SpaceLeft:
  clc
  lda RgShotX,x
  adc AvTmp
  sta RgShotX,x
  lda RgShotPage,x
  adc #0
  sta RgShotPage,x
SpaceY:
  lda RgShotVYHi,x
  ora RgShotVYLo,x
  beq SpaceNext
  lda AvTmp
  ldy RgShotVYHi,x
  bmi SpaceDown
  lda #0
  sec
  sbc AvTmp
SpaceDown:
  clc
  adc RgShotY,x
  sta RgShotY,x
SpaceNext:
  dec AvTmp2
  jne SpacingLoop
Spaced:
  rts
BillAim:
  ldx AvSlot
  lda #0
  sta RgSpread
  farcall BillSourceProjection
  ldx AvSlot
  lda RgShotType,x
  cmp #AV_FLARE
  bne LaserArt
  lda RgShotX,x
  sta SsAngleLo,x
  lda RgShotPage,x
  sta SsAngleHi,x
  lda RgShotY,x
  sta SsHidden,x
  lda RgShotYHigh,x
  sta RgShotHitsNow,x
  lda RgShotFracX,x
  sta SsArt,x
  lda RgShotFracY,x
  sta SsHitTimer,x
  jmp Sound
LaserArt:
  lda RgShotType,x
  cmp #42
  bne Sound
  ; Bill.setDir keeps this rotation even after blowUp zeroes velocity.
  ; SsArt is exclusive to Laser here; Flare owns it as centerX fraction.
  ldy #0
  lda RgShotVYLo,x
  ora RgShotVYHi,x
  beq ArtStore
  iny
  lda RgShotVXLo,x
  ora RgShotVXHi,x
  beq ArtVertical
  lda RgShotVXHi,x
  eor RgShotVYHi,x
  bpl ArtStore
  ldy #3
  bne ArtStore
ArtVertical:
  iny
ArtStore:
  tya
  sta SsArt,x
  jmp Sound
Sound:
  lda #15
  sta RgShootPose
  rts
.endproc
.popseg

.proc AvSamusPrimary
  lda CrossoverBehaviorVersion
  jeq Native
  farcall RemainingSamusPool
  jcs Handled
  ; Source default Attack always remains a beam. AvSamusMode is an old
  ; reserved alias; classic-mode B missiles are not enabled in this port.
  jmp Beam
  .res 40,$ea
Beam:
  lda #3
  farcall InventoryHas
  jcc Native
  lda #AV_ICE
  sta AvType
  farcall RemainingWeapons::CountType
  lda AvCount
  cmp #3
  jcs Handled
  farcall RemainingWeapons::Spawn
Handled:
  sec
  rts
Native:
::LegacyPrimaryNative:
  clc
  rts
.endproc

.proc RemainingRefill
  lda AvRefillItem
  sta AvItem
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  jeq Samus
  cmp #CHARACTER_LINK
  jeq Link
  cmp #CHARACTER_SIMON
  jeq Simon
  cmp #CHARACTER_RYU
  jeq Ryu
  cmp #CHARACTER_SOPHIA
  jeq Sophia
  rts
Samus:
  lda #2
  ldy #2
  jmp Owned
Link:
  lda AvItem
  cmp #1
  jeq LinkReady
  cmp #2
  jeq LinkReady
  lda #1
  farcall InventoryHas
  jcs LinkBomb
  lda #2
  jne LinkReady
LinkBomb:
  lda #1
LinkReady:
  ldy #2
  jmp Owned
Sophia:
  lda AvItem
  cmp #2
  jeq Homing
  lda #1
  ldy #6
  jmp Owned
Homing:
  lda #2
  ldy #2
  jmp Owned
Simon:
  lda #0
  ldy #1
  ldx InvDropAmount
  cpx #40
  jcc Add
  ldy #5
  jne Add
Ryu:
  lda #0
  ldy #5
  ldx InvDropAmount
  cpx #40
  jcc Add
  ldy #10
  jne Add
Owned:
  sty AvTmp
  pha
  farcall InventoryHas
  pla
  jcc Done
  ldy AvTmp
Add:
  sty AvTmp
  farcall InventoryIndex
  stx AvSavedX
  lda InvAmmo,x
  clc
  adc AvTmp
  sta AvTmp
  lda InvItem
  farcall InventoryMaximum
  ldx AvSavedX
  cmp AvTmp
  bcs :+
    sta AvTmp
  :
  lda AvTmp
  sta InvAmmo,x
  inc InvDirty
  lda #Sfx_CoinGrab
  sta Square2SoundQueue
Done:
  rts
.endproc

.proc RemainingChooseAmmo
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  jeq Samus
  cmp #CHARACTER_LINK
  jeq TwoKinds
  cmp #CHARACTER_SOPHIA
  jeq TwoKinds
  cmp #CHARACTER_RYU
  jeq Shared
  cmp #CHARACTER_SIMON
  jeq Shared
  clc
  rts
Samus:
  lda #2
  farcall InventoryHas
  lda #2
  rts
TwoKinds:
  lda #1
  farcall InventoryHas
  jcc Second
  lda #2
  farcall InventoryHas
  jcc First
  lda PseudoRandomBitReg+2
  and #1
  clc
  adc #1
  sec
  rts
First:
  lda #1
  sec
  rts
Second:
  lda #2
  farcall InventoryHas
  lda #2
  rts
Shared:
  lda #0
  sec
  rts
.endproc
.proc RemainingCanDrop
  phx
  phy
  jsr RemainingChooseAmmo
  ply
  plx
  rts
.endproc
.proc RemainingDropMade
  phx
  jsr RemainingChooseAmmo
  sta AvItem
  plx
  lda AvItem
  sta AvDropItem,x
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  jeq Size
  cmp #CHARACTER_SIMON
  jeq Size
  rts
Size:
  lda #1
  ldy PseudoRandomBitReg+2
  cpy #205                       ; Source small/big mix is 80/20.
  bcc :+
    lda #2
  :
  sta InvDropKind,x
  rts
.endproc
.proc RemainingPrepareAmmo
  phx
  lda InvPickup,x
  cmp #$fe
  jne Done
  jsr RemainingChooseAmmo
  sta AvItem
  plx
  lda AvItem
  sta AvPickupAmmoItem,x
  rts
Done:
  plx
  rts
.endproc

.proc RemainingEnemyHit
  lda GuestBodyAttack
  jne Hit                      ; A body contact owns its dictionary receipt.
  lda MmBulletType
  cmp #75
  jeq Hit
  cmp #76
  jeq Hit
  lda MmBulletType
  cmp #74
  jcs Melee
  ldy AvSlot
  lda Bits,x
  and RgShotHits,y
  jne Skip
  lda Bits,x
  ora RgShotHits,y
  sta RgShotHits,y
  lda MmBulletType
  cmp #64                        ; Flames may damage again after 120 ms.
  jne Ice
  lda #8
  sta SsHitTimer,y
Ice:

Hit:
  clc
  rts
Melee:
  ; Jump Slash uses its body-contact dictionary, not FLASH invulnerability.
  ; The actual-contact path above supplies the receipt even while flashing.
  clc
  rts
Skip:
  sec
  rts
Bits: .byte 1,2,4,8,16,32
.endproc
.proc RemainingKeepWeapon
  cmp #76
  bne :+
  clc
  rts
  :
  cmp #61                        ; Bomb explosion.
  beq Keep
  cmp #64                        ; Holy water flame.
  beq Keep
  cmp #65                        ; Cross passes through all contacts.
  beq Keep
  cmp #74                        ; Jump Slash and Screw Attack.
  bcs Keep
  clc
  rts
Keep:
  sec
  rts
.endproc

; Rotate the first producer across ten shots, six world items, four drops,
; the HUD and (Sophia only) six private enemy explosions. A draw only emits sprites whose physical CHR window is selected.
; This prevents mixed-bank corruption and gives every family a fair turn.
.proc RemainingDraw
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  jeq KeepWindow
  lda #0
  sta SsChrActive
KeepWindow:
  lda MmDeathFlag
  jne Publish
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  jeq SophiaNativeShots
  ldx #9
AnyShot:
  lda RgShotType,x
  cmp #32
  bcs Needed
  dex
  bpl AnyShot
CheckPickups:
  ldx #5
AnyPickup:
  lda Enemy_Flag,x
  beq NextPickup
  lda InvPickupOwner,x
  cmp SelectedCharacter
  bne NextPickup
  lda InvPickup,x
  beq NextPickup
  cmp #$fc
  bcc Needed
  cmp #$fe
  beq Needed
NextPickup:
  dex
  bpl AnyPickup
  ldx #3
AnyDrop:
  lda InvDropKind,x
  bne Needed
  dex
  bpl AnyDrop
  ldx SelectedCharacter
  lda InvSelected,x
  jeq Publish
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne Needed
  lda #20                    ; Only HUD remains; native missiles draw above.
  sta AvDrawIndex
  lda #1
  sta AvDrawLeft
  jmp Loop
Needed:
  inc AvDrawFirst
  lda AvDrawFirst
  cmp #21
  bcc FirstReady
  cmp #21+SOPHIA_EFFECT_COUNT
  bcs WrapFirst
  ldx SelectedCharacter
  cpx #CHARACTER_SOPHIA
  beq FirstReady
WrapFirst:
  lda #0
  sta AvDrawFirst
FirstReady:
  sta AvDrawIndex
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bne :+
    farcall BillEndDrawPriority
  :
  lda #21
  ldx SelectedCharacter
  cpx #CHARACTER_SOPHIA
  bne :+
    lda #21+SOPHIA_EFFECT_COUNT
  :
  sta AvDrawLeft
Loop:
  ldx AvDrawIndex
  cpx #10
  jcc Shot
  cpx #16
  jcc World
  cpx #20
  jcc Drop
  cpx #21
  jcs Effect
  jmp Hud
Shot:
  stx AvSlot
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  jeq Next                    ; Native prefix draws cannons and missiles together.
  lda RgShotType,x
  cmp #32
  jcc Next
  cmp #47
  jcs Next
  cmp #AV_LASER
  bne :+
    lda SsHidden,x
    jne Next
  :
  jsr ShotArt
  sta AvDrawArt
  ldx AvSlot
  lda RgShotDir,x
  sta AvDrawDirection
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  beq UnmirroredShot
  cmp #CHARACTER_RYU
  bne :+
UnmirroredShot:
    ; BillBullet/RyuProjectile.setDirection change motion, never scaleX. Its wheel and
    ; dragon flames keep the same chiral source poses on leftward launches.
    lda #1
    sta AvDrawDirection
  :
  lda RgShotX,x
  sta R4
  lda RgShotPage,x
  sta R5
  lda RgShotY,x
  sta R6
  lda RgShotYHigh,x
  sta R7
  jsr Camera
  jmp Draw
World:
  txa
  sec
  sbc #10
  tax
  stx AvSlot
  lda Enemy_Flag,x
  jeq Next
  lda Enemy_ID,x
  cmp #PowerUpObject
  jne Next
  lda InvPickupOwner,x
  cmp SelectedCharacter
  jne Next
  lda InvPickup,x
  jeq Next
  cmp #$fc
  jcc Upgrade
  cmp #$fe
  jne Next
  lda AvPickupAmmoItem,x
  sta AvRefillItem
  jsr RefillArt
  jmp WorldArt
Upgrade:
  jsr PickupArt
WorldArt:
  jeq Next
  sta AvDrawArt
  ldx AvSlot
  lda Enemy_X_Position,x
  clc
  adc #8
  sta R4
  lda Enemy_PageLoc,x
  adc #0
  sta R5
  lda Enemy_Y_Position,x
  clc
  adc #24
  sta R6
  lda Enemy_Y_HighPos,x
  sta R7
  lda #1
  sta AvDrawDirection
  jsr Camera
  jmp Draw
Drop:
  txa
  sec
  sbc #16
  tax
  stx AvSlot
  lda InvDropKind,x
  jeq Next
  lda AvDropItem,x
  sta AvRefillItem
  jsr RefillArt
  jeq Next
  sta AvDrawArt
  ldx AvSlot
  lda InvDropX,x
  sta R4
  lda InvDropPage,x
  sta R5
  lda InvDropY,x
  sta R6
  lda #1
  sta R7
  sta AvDrawDirection
  jsr Camera
  jmp Draw
Effect:
  txa
  sec
  sbc #21
  tax
  lda SophiaEffectAge,x
  jeq Next
  and #$7f
  beq :+
    sec
    sbc #1
  :
  lsr
  clc
  adc #AV_ART_SOPHIAEXPLOSION8
  sta AvDrawArt
  lda SophiaEffectX,x
  sta R4
  lda SophiaEffectPage,x
  sta R5
  lda SophiaEffectY,x
  sta R6
  lda SophiaEffectYHigh,x
  sta R7
  lda #1
  sta AvDrawDirection
  jsr Camera
  jmp Draw
Hud:
  lda OperMode
  cmp #1
  jne Next
  lda GameEngineSubroutine
  cmp #8
  jne Next
  ldx SelectedCharacter
  lda InvSelected,x
  jeq Next
  jsr PickupArt
  jeq Next
  sta AvDrawArt
  lda #192
  sta R4
  lda #0
  sta R5
  sta R3
  lda #24
  sta R6
  lda #1
  sta R7
.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
  jmp SamusFixedMissileHud
.else
  sta AvDrawDirection
.endif
Draw:
  lda AvDrawArt
  jsr ArtPointer
  jcc Next
FixedHudRender:
  lda #0
  sta R3
  farcall MetaspriteRenderLoop
Next:
  inc AvDrawIndex
  lda AvDrawIndex
  cmp #21
  bcc NextReady
  cmp #21+SOPHIA_EFFECT_COUNT
  bcs WrapNext
  ldx SelectedCharacter
  cpx #CHARACTER_SOPHIA
  beq NextReady
WrapNext:
  lda #0
  sta AvDrawIndex
NextReady:
  dec AvDrawLeft
  jne Loop
Publish:
  jsr PublishChr
  jsr CrossoverGraphicsBank
  rts
PublishChr:
  GuestPublishChrLocal
  rts
SophiaNativeShots:
  lda SophiaEffectAge
  ora SophiaEffectAge+1
  ora SophiaEffectAge+2
  ora SophiaEffectAge+3
  ora SophiaEffectAge+4
  ora SophiaEffectAge+5
  jne Needed
  jmp CheckPickups
Camera:
  sec
  lda R4
  sbc ScreenLeft_X_Pos
  sta R4
  lda R5
  sbc ScreenLeft_PageLoc
  sta R5
  rts
ArtPointer:
  tay
  lda AvArtFamilies,y
  tax
  lda AvPhysicalBanks,x
.if ::MAPPER_MMC5
  ora #1
.endif
  ldx SsChrActive
  jeq Choose
  cmp SsChrPhysical
  jne Reject
Choose:
  sta SsChrPhysical
  lda #1
  sta SsChrActive
  lda AvDrawDirection
  cmp #2
  jeq Left
  lda AvArtRightLo,y
  sta R0
  lda AvArtRightHi,y
  jmp Bank
Left:
  lda AvArtLeftLo,y
  sta R0
  lda AvArtLeftHi,y
Bank:
  sta R1
  lda AvArtBanks,y
.if ::MAPPER_MMC5
  ora #MMC5_PRG_ROM
.endif
  BankPRGC a
  sec
  rts
Reject:
  clc
  rts
ShotArt:
  lda RgShotType,x
  cmp #AV_LASER
  beq BillArt
  cmp #AV_FLARE
  beq BillArt
  sec
  sbc #32
  tay
  lda BaseArt,y
  sta AvDrawArt
  lda RgShotType,x
  cmp #AV_EXPLOSION
  jeq BombFrames
  cmp #AV_FIRE
  jeq FireFrames
  cmp #AV_CROSS
  jeq ThreeFrames
  cmp #AV_WHEEL
  jeq FourFrames
  cmp #AV_DRAGON
  jeq FourFrames
  cmp #AV_SOPHIA
  jeq ThreeFrames
  cmp #AV_HOMING
  jeq ThreeFrames
  lda AvDrawArt
  rts
BillArt:
  farcall BillAdvancedDrawArt, tail
BombFrames:
  lda RgShotAge,x
  ldy #0
DivideThree:
  cmp #3
  jcc Phase
  sbc #3
  iny
  cpy #15
  jcc DivideThree
Phase:
  tya
  clc
  adc AvDrawArt
  rts
FireFrames:
  lda RgShotAge,x
  ldy #0
DivideFifteen:
  cmp #15
  jcc Phase
  sbc #15
  iny
  cpy #8
  jcc DivideFifteen
  jcs Phase
ThreeFrames:
  lda RgShotAge,x
  lsr
  lsr
ModuloThree:
  cmp #3
  jcc AddPhase
  sbc #3
  jcs ModuloThree
FourFrames:
  lda RgShotAge,x
  lsr
  lsr
  and #3
AddPhase:
  clc
  adc AvDrawArt
  rts
BaseArt:
  .byte AV_ART_LINKPROJECTILE23,AV_ART_LINKPROJECTILE5,AV_ART_LINKPROJECTILE6
  .byte AV_ART_SIMONPROJECTILE18,AV_ART_SIMONPROJECTILE8,AV_ART_SIMONPROJECTILE9
  .byte AV_ART_SIMONPROJECTILE5,AV_ART_RYUPROJECTILE13,AV_ART_RYUPROJECTILE9
  .byte AV_ART_SAMUSSHOT7,AV_ART_BILLBULLET5,AV_ART_BILLBULLET4
  .byte AV_ART_SOPHIABULLET5,AV_ART_SOPHIABULLET5,AV_ART_SAMUSSHOT3

PickupArt:
  sta AvItem
  lda SelectedCharacter
  sec
  sbc #2
  asl
  asl
  asl
  clc
  adc AvItem
  tax
  lda PickupArts,x
  rts
RefillArt:
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  jne LinkRefill
  lda #AV_ART_SAMUSPICKUP11
  rts
LinkRefill:
  cmp #CHARACTER_LINK
  jne SimonRefill
  lda AvRefillItem
  cmp #2
  jne BombRefill
  lda #AV_ART_LINKPICKUP9
  rts
BombRefill:
  lda #AV_ART_LINKPICKUP10
  rts
SimonRefill:
  cmp #CHARACTER_SIMON
  jne RyuRefill
  lda #AV_ART_SIMONPICKUP11
  ldx AvSlot
  ldy InvDropKind,x
  cpy #2
  jne RefillDone
  lda #AV_ART_SIMONPICKUP10
  rts
RyuRefill:
  cmp #CHARACTER_RYU
  jne SophiaRefill
  lda #AV_ART_RYUPICKUP10
  ldx AvSlot
  ldy InvDropKind,x
  cpy #2
  jne RefillDone
  lda #AV_ART_RYUPICKUP9
  rts
SophiaRefill:
  cmp #CHARACTER_SOPHIA
  jne NoArt
  lda AvRefillItem
  cmp #2
  jne StandardAmmo
  lda #AV_ART_SOPHIAPICKUP9
  rts
StandardAmmo:
  lda #AV_ART_SOPHIAPICKUP10
RefillDone:
  rts
NoArt:
  lda #0
  rts
PickupArts:
  ; Eight entries per actual character, IDs 2..11. Zero is the mushroom.
  .byte 0,AV_ART_SAMUSPICKUP5,AV_ART_SAMUSPICKUP7,AV_ART_SAMUSPICKUP3,AV_ART_SAMUSPICKUP4,AV_ART_SAMUSPICKUP1,AV_ART_SAMUSPICKUP10,0
  .byte 0,AV_ART_BILLPICKUP4,AV_ART_BILLPICKUP8,AV_ART_BILLPICKUP10,AV_ART_BILLPICKUP2,AV_ART_BILLPICKUP6,AV_ART_BILLPICKUP4,0
  .byte 0,AV_ART_LINKPICKUP3,AV_ART_LINKPICKUP2,AV_ART_LINKPICKUP6,AV_ART_LINKPICKUP7,AV_ART_LINKPICKUP8,AV_ART_LINKPICKUP6,0
  .byte 0,AV_ART_SIMONPICKUP6,AV_ART_SIMONPICKUP3,AV_ART_SIMONPICKUP4,AV_ART_SIMONPICKUP5,AV_ART_SIMONPICKUP1,AV_ART_SIMONPICKUP2,AV_ART_SIMONPICKUP7
  .byte AV_ART_SIMONPICKUP8,0,0,0,0,0,0,0
  .res 24,0
  .byte 0,AV_ART_RYUPICKUP2,AV_ART_RYUPICKUP4,AV_ART_RYUPICKUP5,AV_ART_RYUPICKUP7,AV_ART_RYUPICKUP3,AV_ART_RYUPICKUP8,AV_ART_RYUPICKUP1
  .byte 0,AV_ART_SOPHIAPICKUP7,AV_ART_SOPHIAPICKUP6,AV_ART_SOPHIAPICKUP3,AV_ART_SOPHIAPICKUP2,AV_ART_SOPHIAPICKUP4,AV_ART_SOPHIAPICKUP5,0
.endproc
.popseg

; Cold effect management lives outside the almost-full EXPANDED weapon bank.
.pushseg
.segment "INVENTORY"
.proc SophiaDefeatBowser
  lda #1
  sta SophiaDropBlocked
  jsr HandleEnemyFBallCol
  lda #0
  sta SophiaDropBlocked
  rts
.endproc
.proc SophiaDefeatEnemy
  stx AvSavedX
  ldx #SOPHIA_EFFECT_COUNT-1
Find:
  lda SophiaEffectAge,x
  beq Free
  dex
  bpl Find
  ; All six native enemy slots can explode together. Only a genuine seventh
  ; concurrent explosion retires the oldest actor and completes its drop roll.
  ldy #0
  sty AvSavedY
  sty AvTmp
  ldx #SOPHIA_EFFECT_COUNT-1
Oldest:
  lda SophiaEffectAge,x
  and #$7f                    ; newborn $80 is youngest, not the oldest.
  cmp AvTmp
  bcc Next
  sta AvTmp
  stx AvSavedY
Next:
  dex
  bpl Oldest
  ldx AvSavedY
  jsr SophiaEffectDrop
Free:
  stx AvSavedY
  ldy AvSavedX
  lda Enemy_X_Position,y
  clc
  adc #8
  sta SophiaEffectX,x
  lda Enemy_PageLoc,y
  adc #0
  sta SophiaEffectPage,x
  lda Enemy_Y_Position,y
  clc
  adc #16                    ; center of the shared native enemy hit rectangle.
  sta SophiaEffectY,x
  lda Enemy_Y_HighPos,y
  adc #0
  sta SophiaEffectYHigh,x
  lda #$80                   ; noAnimThisCycle: update after all weapon kills.
  sta SophiaEffectAge,x
  ldx AvSavedX
  jsr ShellOrBlockDefeat      ; original immediate drop and native score award.
  ldx AvSavedX
  lda #0
  sta Enemy_Flag,x            ; source SophiaExplosion destroys the enemy now.
  sta EnemyMetasprite,x       ; renderer reads this even after Enemy_Flag clears.
  rts
.endproc
.proc SophiaUpdateEffects
  ldx #SOPHIA_EFFECT_COUNT-1
Loop:
  lda SophiaEffectAge,x
  beq Next
  bmi Newborn
  inc SophiaEffectAge,x
  lda SophiaEffectAge,x
  cmp #13                    ; six source frames, each two NES updates.
  bcc Next
  jsr SophiaEffectDrop       ; source enemyDieEnd -> destroy -> independent roll.
  lda #0
  sta SophiaEffectAge,x
  beq Next
Newborn:
  lda #1
  sta SophiaEffectAge,x
Next:
  dex
  bpl Loop
  rts
.endproc
.proc SophiaEffectDrop
  lda SophiaEffectX,x
  sta RgTempX
  lda SophiaEffectPage,x
  sta RgTempPage
  lda SophiaEffectY,x
  clc
  adc #8                     ; bottom-pivot pickup is centered on the effect.
  sta RgTempY
  jmp InventoryDropPoint
.endproc
.popseg

; Easy linked1.0 primary: status0/1/2 = Short/Long/Wave, no owned flags.
.pushseg
.segment "SPECIAL_EXTRA"
.proc SamusBeamType
  lda CrossoverBehaviorVersion
  bne Hard
  lda PlayerStatus
  clc
  adc #1
  rts
Hard:
  lda #4
  farcall InventoryHas
  lda #3
  bcs Done
  lda #7
  farcall InventoryHas
  lda #2
  bcs Done
  lda #1
Done:
  rts
.endproc

; Flash uses bottom-pivot displacement10px on exits and Easy entry.
; Nonclassic Hard grounded crouch entry is5Flashpx=2.5NES, in exactQ16.
.proc SamusMorphEnter
  lda CrossoverBehaviorVersion
  beq SamusMorphExit
  sec
  lda MmYFraction
  sbc #0
  sta MmYFraction
  lda MmYFraction+1
  sbc #$80
  sta MmYFraction+1
  lda Player_Y_Position
  sbc #2
  sta Player_Y_Position
  lda Player_Y_HighPos
  sbc #0
  sta Player_Y_HighPos
  jmp SamusMorphLifted
.endproc
.proc SamusMorphExit
  sec
  lda Player_Y_Position
  sbc #5
  sta Player_Y_Position
  lda Player_Y_HighPos
  sbc #0
  sta Player_Y_HighPos
Lifted:
::SamusMorphLifted:
  lda #1
  sta Player_State
  lda #0
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  sta Player_Y_Speed
  rts
.endproc
.popseg

.pushseg
.segment "BILL_COLD"
; Projectile.initiate immediately checks the initial cached HRect. Inactive
; delayed Laser segments skip it. No movement/orbit occurs before this check.
.proc BillAdvancedBirth
  ldx AvSlot
  lda RgShotType,x
  cmp #AV_LASER
  bne Check
  lda SsHidden,x
  bne Expiry
Check:
  stx RgSlot
  farcall GuestPrepareEnemies
  farcall RemainingWeapons::Bridge
  farcall MegaManWeapons::Blocks
  lda MmBulletType
  beq Hit
  farcall RemainingWeapons::Bridge
  farcall MegaManWeapons::Enemies
  lda MmBulletType
  bne Expiry
Hit:
  ldx AvSlot
  lda #4                         ; This same batch ticks once to3 before draw.
  sta RgShotImpact,x              ; Then three draws before50ms cleanup.
Expiry:
  ldx AvSlot
  jsr BillAdvancedExpiry         ; Same mapped cold closure, no new farcall.
Done:
  rts
.endproc
; Fair Bill-only physical-bank arbitration. Existing unused draw scratch bytes
; are exclusive aliases: persistent turn and live-other cursor, cleared by
; RemainingClear. No oldRAM address or allocation changes.
BillDrawTurn = AvDrawPhysical
BillDrawOtherCursor = AvDrawFamily
.proc BillEndDrawPriority
  ldx #9
FindShot:
  lda RgShotType,x
  cmp #AV_LASER
  beq HaveShot
  cmp #AV_FLARE
  beq HaveShot
  dex
  bpl FindShot
  rts
HaveShot:
  stx AvTmp2
  lda BillDrawTurn
  eor #1
  sta BillDrawTurn
  beq Shot
  lda BillDrawOtherCursor
  cmp #10
  bcc ResetCursor
  cmp #21
  bcc CursorReady
ResetCursor:
  lda #10
CursorReady:
  sta AvTmp
  lda #11
  sta AvCount
Candidate:
  lda AvTmp
  cmp #16
  bcc World
  cmp #20
  bcc Drop
  lda InvSelected+CHARACTER_BILL
  bne Other
  beq Advance
World:
  sec
  sbc #10
  tax
  lda Enemy_Flag,x
  beq Advance
  lda Enemy_ID,x
  cmp #PowerUpObject
  bne Advance
  lda InvPickupOwner,x
  cmp #CHARACTER_BILL
  bne Advance
  lda InvPickup,x
  beq Advance
  cmp #$fc
  bcc Other
  cmp #$fe
  beq Other
  bne Advance
Drop:
  sec
  sbc #16
  tax
  lda InvDropKind,x
  bne Other
Advance:
  inc AvTmp
  lda AvTmp
  cmp #21
  bcc :+
    lda #10
    sta AvTmp
  :
  dec AvCount
  bne Candidate
Shot:
  ldx AvTmp2
  stx AvDrawIndex
  lda #232                       ; Frozen AvPhysicalBanks[15], guarded by host.
.if ::MAPPER_MMC5
  ora #1
.endif
  sta SsChrPhysical
  lda #1
  sta SsChrActive
  rts
Other:
  lda AvTmp
  sta AvDrawIndex
  clc
  adc #1
  cmp #21
  bcc :+
    lda #10
  :
  sta BillDrawOtherCursor
  rts
.endproc
.popseg
