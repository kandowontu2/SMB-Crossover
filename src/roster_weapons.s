.pushseg
.segment "GUEST"
.proc RosterWeapons
  lda #0
  sta Fireball_State
  sta Fireball_State+1
  sta ObjectMetasprite+7
  sta ObjectMetasprite+8
  lda TimerControl
  jne Done
  lda GameEngineSubroutine
  cmp #8
  jne Clear
  lda #0
  ldx #5
  ldy SelectedCharacter
  cpy #CHARACTER_BILL
  beq EnemiesReady
CheckEnemies:
  ora Enemy_Flag,x
  dex
  bpl CheckEnemies
  sta RgEnemiesPresent
EnemiesReady:
::RosterBillCandidatesReady:
  lda RgCooldown
  beq :+
    dec RgCooldown
  :
  lda RgShootPose
  beq :+
    dec RgShootPose
  :
  lda SavedJoypadBits
  eor RgPreviousButtons
  and SavedJoypadBits
  sta RgWeaponButtons
  lda SavedJoypadBits
  sta RgPreviousButtons
  lda GuestHurtTicks
  beq InputReady
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  beq LockedInput
  cmp #CHARACTER_SIMON
  bne InputReady
LockedInput:
  lda #0                        ; Keep physical history: recovery is no press.
  sta RgWeaponButtons
  jmp Projectiles               ; Existing projectiles/effects stay live.
InputReady:
  lda Player_State
  cmp #3
  jeq Projectiles
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bne Melee
  jsr BillInput
  jmp Projectiles
Melee:
  lda RgAttack
  beq NewAttack
  dec RgAttack
  inc RgAttackAge
  lda RgAttackKind
  beq MeleeHit
  lda SelectedCharacter
  cmp #CHARACTER_SIMON
  jne Projectiles
  lda RgAttackAge
  cmp #14
  jne Projectiles
  farcall AvSimonRelease
  jmp Projectiles
MeleeHit:
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne Whip
  lda RgAttackAge
  cmp #9
  bne :+
    farcall RemainingPower
    cmp #2
    bne :+
      jsr SpawnBeam
  :
  lda RgAttackAge
  cmp #9
  jcs Projectiles
  jsr MeleeBridge
  jmp Projectiles
Whip:
  lda RgAttackAge
  cmp #14
  jcc Projectiles
  jsr MeleeBridge
  jmp Projectiles
NewAttack:
  lda RgWeaponButtons
  and #Select_Button
  bne Special
  lda A_B_Buttons
  eor PreviousA_B_Buttons
  and A_B_Buttons
  and #B_Button
  jeq Thrust
  lda SavedJoypadBits
  and #Up_Dir
  beq SwordWhip
  lda SelectedCharacter
  cmp #CHARACTER_SIMON
  beq Special
SwordWhip:
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne SwordWhipStart
    ; Link2.02 attackStart rejects an ordinary aerial sword while Up/Down
    ; selects a thrust; checkState continues the held thrust instead.
    lda Player_State
    beq SwordWhipStart
    lda SavedJoypadBits
    and #Up_Dir|Down_Dir
    beq SwordWhipStart
    lda CrossoverBehaviorVersion
    jeq Thrust
    farcall RemainingPower
    cmp #2
    jne Thrust
      jsr SpawnBeam              ;2.02 pressAtkBtn can beam during a thrust.
    jmp Thrust
SwordWhipStart:
  lda #0
  sta RgAttackKind
  jsr StartAttack
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne :+
    jsr MeleeBridge            ; attackStart has the active sword rectangle.
  :
  jmp Projectiles
Special:
  farcall AvRosterSpecial
  jmp Projectiles
Thrust:
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne Projectiles
  lda CrossoverBehaviorVersion
  bne NativeThrust
  lda RgBillBurst               ; Old checkState precedes native ground contact.
  cmp #19
  beq EasyDown
  cmp #21
  bne ResetThrust
  lda #2
  bne EasyActive
EasyDown:
  lda #1
  bne EasyActive
EasyActive:
  sta RgThrustReset
  jmp ActiveThrust
NativeThrust:
  lda Player_State
  beq ResetThrust
  lda SavedJoypadBits
  and #Up_Dir
  beq DownThrust
  lda #2
  bne ThrustPhase
DownThrust:
  lda SavedJoypadBits
  and #Down_Dir
  beq ResetThrust
  lda #1
ThrustPhase:
  cmp RgThrustReset
  beq ActiveThrust
  sta RgThrustReset             ; START pose lasts one completed logic update.
  farcall LinkClearThrustBlocks
  jmp Projectiles
ActiveThrust:
  sta RgThrust
  jsr MeleeBridge
  jmp Projectiles
ResetThrust:
  lda #0
  sta RgThrustReset
  sta LinkThrustPrev
  sta LinkThrustNow
Projectiles:
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne NativeProjectileBatch
  lda CrossoverBehaviorVersion
  bne NativeProjectileBatch
  farcall EasyLinkAnimate
NativeProjectileBatch:
  ; Inspect the actual pool after input/spawning. A late NMI controller
  ; receipt can feed the raw-input Laser/Flare handlers after parsed B.
  ; Each nonempty Bill batch prepares fresh candidates before consumption.
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bne ShotPoolReady
  ldx #9
BillCheckPool:
  lda RgShotType,x
  bne BillActiveEnemies
  dex
  bpl BillCheckPool
  bmi ShotPoolReady
BillActiveEnemies:
  jsr GuestPrepareEnemies
ShotPoolReady:
  ldx #9
ShotLoop:
  stx RgSlot
  lda RgShotType,x
  jeq Next
  cmp #9
  jcs Next
  lda RgShotImpact,x
  beq Fly
  inc RgShotAge,x
  dec RgShotImpact,x
  jne Next
  jmp Kill
Fly:
  lda RgShotType,x
  cmp #3
  bne AdvanceAge
  lda RgShotAge,x
  cmp #35
  bcs MoveAgeReady
AdvanceAge:
  inc RgShotAge,x
MoveAgeReady:
  jsr Move
  lda RgShotType,x
  beq Next
  jsr ShotBridge
  jsr MegaManWeapons::Blocks
  lda MmBulletType
  bne EnemyCollision
  ldx RgSlot
  lda RgShotType,x
  cmp #5
  bne :+
    farcall LinkBoomerangReturn
    jsr ShotBridge
    jmp EnemyCollision
  :
  cmp #6
  bne Impact
  jsr ShotBridge
EnemyCollision:
  lda RgEnemiesPresent
  jeq Next
  ldx #0
  jsr MegaManWeapons::Enemies
  lda MmBulletType
  bne Next
Impact:
  ldx RgSlot
  lda #3
  ldy RgShotType,x
  cpy #4
  bne :+
    lda #0
    sta RgShotAge,x
    lda #21                    ; 40 Flash pixels /115px/s, at 60Hz.
  :
  sta RgShotImpact,x
  jmp Next
Kill:
  ldx RgSlot
  lda #0
  sta RgShotType,x
Next:
  ldx RgSlot
  dex
  jpl ShotLoop
  lda #0
  sta MmBulletType
Done:
::RosterWeaponsFinish:
  rts
Clear:
  lda #0
  ldx #9
ClearLoop:
  sta RgShotType,x
  dex
  bpl ClearLoop
  rts

BillInput:
  farcall AvBillInput
  jcs InputDone
  lda RgBillBurstDelay
  beq :+
    dec RgBillBurstDelay
    bne :+
    lda #0
    sta RgBillBurst
  :
  farcall RemainingPower
  cmp #1
  bne Fresh
  lda A_B_Buttons
  and #B_Button
  beq MachineRelease
  lda RgWeaponButtons
  and #B_Button
  bne MachineStart
  lda RgCooldown
  jne InputDone
  jsr MachineCadence
  jsr CountShots
  lda RgCount
  cmp #6
  bcs MachineFull
  lda RgBillBurst
  cmp #6
  bcc MachineAuto
  lda RgBillBurstDelay
  jne InputDone
  lda #3
  sta RgBillBurstDelay
  rts
MachineAuto:
  inc RgBillBurst
  jmp BillFire
MachineFull:
  lda #0
  sta RgBillBurst
  rts
MachineStart:
  lda #0
  sta RgBillCadence
  sta RgBillBurst
  sta RgBillBurstDelay
  jsr MachineCadence
  jmp BillFire
MachineRelease:
  lda #0
  sta RgBillCadence
  sta RgBillBurst
  sta RgBillBurstDelay
  rts
Fresh:
  lda A_B_Buttons
  eor PreviousA_B_Buttons
  and A_B_Buttons
  and #B_Button
  beq InputDone
BillFire:
  jsr CountShots
  pha
  farcall RemainingPower
  tax
  pla
  lda BillLimits,x
  cmp RgCount
  beq InputDone
  bcc InputDone
  lda #1
  sta RgSfx
  lda #15
  sta RgShootPose
  lda #7
  pha
  farcall RemainingPower
  tax
  pla
  cpx #1
  beq :+
    sta RgCooldown
  :
  lda #0
  sta RgSpread
  farcall RemainingPower
  cmp #2
  beq Fan
  jsr SpawnBill
  rts
Fan:
  ; Both source versions truncate the ordered fan0,+1,-1,-2,+2.
  ; Tail transfer retains the original BillInput caller and label footprint.
  jmp BillSpreadFanOrdered
  nop
  nop
FanLoop:
  .res 13,$ea                    ; Retain all later original CPU addresses.
InputDone:
  rts
BillLimits: .byte 4,6,10
MachineCadence:
  ; Preserve the fractional 110ms boundary: 7,7,6,7,6 updates.
  lda RgBillCadence
  clc
  adc #2
  ldx #7
  cmp #5
  bcc :+
    sbc #5
    dex
  :
  sta RgBillCadence
  stx RgCooldown
  rts
CountShots:
  lda #0
  sta RgCount
  ldx #9
Count:
  lda RgShotType,x
  beq SkipCount
  cmp #43                        ; Each Hard Flare owns an invisible center.
  bne CountOne
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bne CountOne
  lda CrossoverBehaviorVersion
  beq CountOne
  inc RgCount
CountOne:
  inc RgCount
SkipCount:
  dex
  bpl Count
  rts
FindType:
  sta RgTemp
  ldx #9
Find:
  lda RgShotType,x
  cmp RgTemp
  beq Found
  dex
  bpl Find
  clc
  rts
Found:
  sec
  rts
FindSlot:
  ldx #9
Slot:
  lda RgShotType,x
  beq Available
  dex
  bpl Slot
  clc
  rts
Available:
  sec
  rts
InitShot:
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
  lda #1
  sta RgShotYHigh,x
  lda PlayerFacingDir
  sta RgShotDir,x
  rts
SpawnBill:
  ; BillFire counted the pool once. Keep that count current as the fan fills
  ; instead of rescanning all ten slots for every pellet.
  pha
  farcall RemainingPower
  tax
  pla
  lda BillLimits,x
  cmp RgCount
  jeq SpawnDone
  jcc SpawnDone
  jsr FindSlot
  jcc SpawnDone
  inc RgCount
  jsr InitShot
  farcall RemainingPower
  clc
  adc #1
  sta RgShotType,x
  farcall BillSourceProjection
  lda #Sfx_Fireball
  sta Square1SoundQueue
SpawnDone:
  rts
BillSpeedLo: .byte 102,160,198,164,227,13,225,38,84,213,43,85
BillSpeedHi: .byte 2,2,2,2,2,3,2,3,3,2,3,3
BillDiagonalLo: .byte 178,219,246,222,11,40,9,58,90,32,96,128
BillDiagonalHi: .byte 1,1,1,1,2,2,2,2,2,2,2,2
MuzzleX: .byte 26,12,22,23,8
MuzzleY: .byte 10,-15,-3,19,32
SpawnX:
  clc
  lda Player_X_Position
  adc RgTemp
  sta RgShotX,x
  lda #0
  bit RgTemp
  bpl :+
    lda #$ff
  :
  adc Player_PageLoc
  sta RgShotPage,x
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
StartAttack:
  lda #0
  sta RgThrustReset
  sta RgThrust
  lda #1
  sta RgSfx
  lda #0
  sta RgAttackAge
  sta RgMeleeHits
  lda #<RgMeleeBlocks
  sta R0
  lda #>RgMeleeBlocks
  sta R1
  lda #0
  ldy #0
ClearBlocks:
  sta (R0),y
  iny
  bne ClearBlocks
  inc R1
  ldy #0
ClearLast:
  sta (R0),y
  iny
  cpy #160
  bcc ClearLast
  lda #21
  ldx SelectedCharacter
  cpx #CHARACTER_LINK
  bne :+
    lda #13
  :
  sta RgAttack
  rts
SpawnBeam:
  lda #4
  jsr FindType
  jcs SpawnDone
  jsr FindSlot
  jcc SpawnDone
  jsr InitShot
  lda #4
  sta RgShotType,x
  lda #4
  sta RgShotVXHi,x
  lda #$2b
  sta RgShotVXLo,x
  lda #18
  sta RgTemp
  lda PlayerFacingDir
  cmp #1
  beq :+
    jsr NegateX
    lda #$fd
    sta RgTemp
  :
  jsr SpawnX
  lda Player_Y_Position
  clc
  adc #25
  sta RgShotY,x
  lda #$80
  sta RgShotFracX,x
  sta RgShotFracY,x
  rts
SpawnBoomerang:
  jsr FindSlot
  jcc SpawnDone
  jsr InitShot
  lda #5
  sta RgShotType,x
  lda #$80
  sta RgShotVXLo,x
  lda #2
  sta RgShotVXHi,x
  lda #16
  sta RgTemp
  lda PlayerFacingDir
  cmp #1
  beq :+
    jsr NegateX
    lda #0
    sta RgTemp
  :
  jsr SpawnX
  lda Player_Y_Position
  clc
  adc #21
  sta RgShotY,x
  stx RgSlot
  farcall LinkBoomerangSpawn
  rts
SpawnAxe:
  jsr FindSlot
  jcc SpawnDone
  jsr InitShot
  lda #6
  sta RgShotType,x
  lda #$15
  sta RgShotVXLo,x
  lda #2
  sta RgShotVXHi,x
  lda #$55
  sta RgShotVYLo,x
  lda #$fb
  sta RgShotVYHi,x
  lda #19
  sta RgTemp
  lda PlayerFacingDir
  cmp #1
  beq :+
    jsr NegateX
    lda #$fd
    sta RgTemp
  :
  jsr SpawnX
  lda #0
  sta RgShotFracY,x
  lda CrossoverBehaviorVersion
  bne HardAxeHeight
  lda #2
  ldy RgCrouch
  beq AxeHeight
  lda #$80
  sta RgShotFracY,x
  lda #9
  bne AxeHeight
HardAxeHeight:
  lda #7
  ldy RgCrouch
  beq AxeHeight
  lda #17
AxeHeight:
  clc
  adc Player_Y_Position
  sta RgShotY,x
  rts
Move:
  lda RgShotType,x
  cmp #5
  bne Axe
  farcall LinkBoomerangMotion
  ldx RgSlot
  jmp Integrate
Axe:
  cmp #6
  bne Integrate
  clc
  lda RgShotVYLo,x
  adc #53
  sta RgShotVYLo,x
  lda RgShotVYHi,x
  adc #0
  sta RgShotVYHi,x
  bmi Integrate
  cmp #7
  bcc Integrate
  bne ClampAxe
  lda RgShotVYLo,x
  cmp #$80
  bcc Integrate
ClampAxe:
  lda #7
  sta RgShotVYHi,x
  lda #$80
  sta RgShotVYLo,x
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
  cmp #5
  beq MoveDone
  lda RgShotX,x
  sec
  sbc ScreenLeft_X_Pos
  lda RgShotPage,x
  sbc ScreenLeft_PageLoc
  bne MoveKill
  lda RgShotYHigh,x
  cmp #2
  bcs MoveKill
  cmp #1
  bne Above
  lda RgShotY,x
  cmp #240
  bcs MoveKill
  cmp #32
  bcs MoveDone
Above:
  lda RgShotType,x
  cmp #6
  beq MoveDone
MoveKill:
  lda #0
  sta RgShotType,x
MoveDone:
  rts
Home:
  lda Player_X_Position
  clc
  adc #8
  sta RgTemp
  lda Player_PageLoc
  adc #0
  sta RgTemp2
  lda RgTemp
  sec
  sbc RgShotX,x
  sta RgTemp
  lda RgTemp2
  sbc RgShotPage,x
  sta RgTemp2
  beq CatchRight
  cmp #$ff
  bne FarHome
  lda RgTemp
  cmp #$f8
  bcc FarHome
  bcs CatchY
CatchRight:
  lda RgTemp
  cmp #9
  bcs FarHome
CatchY:
  lda Player_Y_Position
  clc
  adc #21
  sec
  sbc RgShotY,x
  clc
  adc #8
  cmp #17
  bcs FarHome
  lda #0
  sta RgShotType,x
  rts
FarHome:
  lda #$55
  sta RgShotVXLo,x
  lda #3
  sta RgShotVXHi,x
  lda RgTemp2
  bpl :+
    jsr NegateX
  :
  lda #$55
  sta RgShotVYLo,x
  lda #3
  sta RgShotVYHi,x
  lda Player_Y_Position
  clc
  adc #21
  cmp RgShotY,x
  bcs :+
    jsr NegateY
  :
  rts
ShotBridge:
  ldx RgSlot
  lda RgShotX,x
  sta MmBulletX
  lda RgShotPage,x
  sta MmBulletPage
  lda RgShotY,x
  sta MmBulletY
  lda RgShotDir,x
  sta MmBulletDir
  ldy RgShotType,x
  lda DamageTypes-1,y
  sta MmBulletType
  lda #0
  sta MmSlot
  tax
  rts
DamageTypes: .byte 11,12,13,17,18,22
MeleeBridge:
  lda Player_X_Position
  clc
  adc #8
  sta MmBulletX
  lda Player_PageLoc
  adc #0
  sta MmBulletPage
  lda PlayerFacingDir
  sta MmBulletDir
  lda #18
  ldx RgCrouch
  beq :+
    lda #27
  :
  clc
  adc Player_Y_Position
  sta MmBulletY
  lda SelectedCharacter
  cmp #CHARACTER_SIMON
  bne :+
    lda #13
    ldx RgCrouch
    beq SimonY
      lda #23
SimonY:
    clc
    adc Player_Y_Position
    sta MmBulletY
  :
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  beq Sword
  lda #19
  bne Power
Sword:
  lda #14
Power:
  pha
  farcall RemainingPower
  tax
  pla
  stx RgTemp2
  clc
  adc RgTemp2
  sta MmBulletType
  lda RgThrust
  beq Forward
  lda MmBulletType
  clc
  adc #9
  sta MmBulletType
  lda RgThrust
  cmp #1
  bne ThrustUp
  lda Player_Y_Position
  clc
  adc #36
  sta MmBulletY
  jmp HitMelee
ThrustUp:
  lda Player_Y_Position
  clc
  adc #10
  sta MmBulletY
  jmp HitMelee
Forward:
  lda #16
  ldx SelectedCharacter
  cpx #CHARACTER_SIMON
  bne :+
    farcall RemainingPower
    ; Leather and morning-star whips have the same source rectangle.
    ; The flame whip adds fifteen NES pixels of reach, half on each side.
    cmp #2
    lda #22
    bcc :+
      lda #30
  :
  ldx PlayerFacingDir
  cpx #1
  beq AddMeleeX
  eor #$ff
  clc
  adc #1
AddMeleeX:
  sta RgTemp
  clc
  adc MmBulletX
  sta MmBulletX
  lda #0
  bit RgTemp
  bpl :+
    lda #$ff
  :
  adc MmBulletPage
  sta MmBulletPage
HitMelee:
  farcall EasyWhipPrepare
  lda #0
  sta MmSlot
  tax
  lda LinkThrustReceipt
  bmi RestoreMeleeType           ; Deferred pass owns only the enemy rectangle.
  jsr MegaManWeapons::Blocks
  ; A solid background contact ends the probe, not the player's melee swing.
RestoreMeleeType:
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  beq :+
    lda #19
    bne MeleeType
  :
  lda #14
MeleeType:
  pha
  farcall RemainingPower
  tax
  pla
  stx RgTemp2
  clc
  adc RgTemp2
  ldx RgThrust
  beq :+
    clc
    adc #9
  :
  sta MmBulletType
  lda RgThrust
  beq MeleeEnemies
  lda CrossoverBehaviorVersion
  beq MeleeEnemies               ; Original HitTester attacks before body.
  lda LinkThrustReceipt
  bpl MeleeDone                  ; Native body contacts must precede this sword.
MeleeEnemies:
  lda RgEnemiesPresent
  beq MeleeDone
  ldx #0
  jsr MegaManWeapons::Enemies
MeleeDone:
  lda #0
  sta MmBulletType
  rts
.endproc

.segment "GUEST"
LinkEnemyBits: .byte 1,2,4,8,16,32



; HitTester.checkLastHitPoints: previous vertical separation wins both upper
; corners; lower corners use current penetration, vertical winning ties.
; A side entry receives bottom only when airborne with <=15 Flash pixels of
; foot penetration. Native edges are integers, so half-scale15 means <=7.
; Input X=enemy, output A=0 neutral/1 bottom/2 top; X preserved.
.proc LinkContactSide
  lda LinkEnemyBits,x
  and LinkLastValid
  jeq Neutral
  lda LinkLastIds,x
  cmp Enemy_ID,x
  jne Neutral
  txa
  asl
  asl
  clc
  adc #4
  tay
  lda LinkLastBoxes+3          ; Previous player bottom <= previous enemy top.
  cmp LinkLastBoxes+1,y
  bcc Bottom
  beq Bottom
  lda LinkLastBoxes+1
  cmp LinkLastBoxes+3,y
  bcc Side
  lda LinkLastBoxes+2
  cmp LinkLastBoxes,y
  bcc LowerLeft
  beq LowerLeft
  lda LinkLastBoxes
  cmp LinkLastBoxes+2,y
  bcs LowerRight
  lda #2
  rts
LowerLeft:
  lda BoundingBox_LR_Corner
  sec
  sbc BoundingBox_UL_Corner,y
  jmp LowerCorner
LowerRight:
  lda BoundingBox_LR_Corner,y
  sec
  sbc BoundingBox_UL_Corner
LowerCorner:
  sta RgTemp
  lda BoundingBox_LR_Corner+1,y
  sec
  sbc BoundingBox_UL_Corner+1
  cmp RgTemp
  bcc Top
  beq Top
  bcs Neutral
Side:
  lda LinkLastBoxes+2
  cmp LinkLastBoxes,y
  bcc SidePadding
  beq SidePadding
  lda LinkLastBoxes
  cmp LinkLastBoxes+2,y
  bcc Neutral
SidePadding:
  lda Player_State
  beq Neutral
  lda BoundingBox_LR_Corner+1
  sec
  sbc BoundingBox_UL_Corner+1,y
  bcc Neutral
  cmp #8
  bcs Neutral
Bottom:
  lda #1
  rts
Top:
  lda #2
  rts
Neutral:
  lda #0
  rts
.endproc

; Input X=actual overlapped native enemy slot. Preserve X/Y; carry protects
; only the active thrust's source-matching body side, including an immune
; target. Shared collision still handles star, inert shells and ordinary hurt.
.proc LinkBodyContact
  phx
  phy
  lda Enemy_ID,x
  cmp #Podoboo
  jeq Ordinary
  cmp #$15
  bcc EnemyBody
  cmp #BulletBill_CannonVar
  beq EnemyBody
  cmp #Bowser
  jne Ordinary
EnemyBody:
  cmp #Goomba
  bne Shell
  lda Enemy_State,x
  cmp #2
  jcs Ordinary
Shell:
  lda Enemy_ID,x
  cmp #3
  bcs ActiveBody
  lda Enemy_State,x
  bmi MovingShell
  and #7
  cmp #2
  jcs Ordinary                  ; Inert Koopa/Buzzy shells retain native kicks.
  bcc ActiveBody
MovingShell:
  lda Enemy_CollisionBits,x
  and #1
  jne Ordinary                  ; Existing native kick's no-hit contact receipt.
ActiveBody:
  lda RgThrust
  jeq Ordinary
  farcall EasyLinkStunnedSide
  jsr LinkContactSide
  jeq Ordinary
  cmp RgThrust
  jne Ordinary
  ; Rear geometry is distinct, but both native Bowser bodies own one source
  ; enemy and therefore one HP/contact receipt.
  lda Enemy_Flag,x
  bpl Canonical
  and #$7f
  cmp #6
  jcs Ordinary
  tax
  lda Enemy_ID,x
  cmp #Bowser
  jne Ordinary
  lda Enemy_Flag,x
  jeq Ordinary
  jmi Ordinary
Canonical:
  lda LinkEnemyBits,x
  and LinkThrustReceipt
  bne Protected
  lda LinkEnemyBits,x
  ora LinkThrustReceipt
  sta LinkThrustReceipt
  lda CrossoverBehaviorVersion
  beq Protected                  ; Easy sword already ran; retain special priority.
  ; One Flash enemy has one body contact even when native Bowser has two
  ; halves. Source hitEnemy clears both dictionaries before its body attack;
  ; C_HIT does not suppress the separate deferred sword rectangle.
  lda #0
  sta LinkThrustPrev
  sta LinkThrustNow
  stx MmEnemySlot
  farcall RemainingPower
  clc
  adc #23
  sta MmBulletType
  lda #0
  sta MmSlot
  ldx MmEnemySlot
  jsr MegaManWeapons::DamageEnemy
  lda #0
  sta MmBulletType
Protected:
  ply
  plx
  sec
::LinkBodyContactProtected:
  rts
Ordinary:
  ply
  plx
  clc
::LinkBodyContactOrdinary:
  rts
.endproc

; game.s invokes this after every native enemy/body update. Flash HitTester
; resolves Link.hitEnemy first, then the independent attack rectangle. In
; particular, C_HIT records this update but only L_HIT rejects another call.


; A real sword contact bounces down-thrust or cancels upward movement.
; Does not create a cooldown: C_HIT/L_HIT controls repeat contacts instead.
.proc LinkThrustResponse
  lda RgThrust
  cmp #1
  beq Down
  lda MmVY+2
  bpl Done
  lda #0
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  sta Player_Y_Speed
  rts
Down:
  lda CrossoverBehaviorVersion
  bne HardBounce
  farcall EasyLinkBounce
  rts
HardBounce:
  lda #$ab                      ; Link2.02 bounce power325/120.
  sta MmVY
  lda #$4a
  sta MmVY+1
  lda #$fd
  sta MmVY+2
  sta Player_Y_Speed
  lda #1
  sta Player_State
  lda #8
  sta LsrHurtFlags                ; Source down-thrust bounce sets jumped=true.
Done:
  rts
.endproc
.proc LinkClampThrustFeet
  ; A=source contact top; canonical feet are PlayerY+32. Preserve X/Y.
  sec
  sbc #32
  sta RgTempY
  lda Player_Y_Position
  cmp RgTempY
  bcc Done
  beq Done
  sec
  sbc RgTempY
  sta RgTemp
  lda RgTempY
  sta Player_Y_Position
  sta Player_Rel_YPos
  lda BoundingBox_UL_Corner+1
  sec
  sbc RgTemp
  sta BoundingBox_UL_Corner+1
  lda BoundingBox_LR_Corner+1
  sec
  sbc RgTemp
  sta BoundingBox_LR_Corner+1
  lda #0
  sta MmYFraction
  sta MmYFraction+1
Done:
  rts
.endproc

; Thrusts use four previous/current exact block-address keys. This reuses
; sixteen bytes of Link's mutually exclusive ordinary-swing map and avoids
; clearing/scanning416 bytes each update. Nonattackable terrain never bounces.
.proc LinkThrustBlockSeen
  lda CrossoverBehaviorVersion
  bne Hard
  farcall EasyLinkThrustBlock
  rts
Hard:
  lda R3
  jsr BlockBumpedChk
  bcs Attackable
  lda R3
  cmp #$51
  beq Attackable
  cmp #$52
  bne New
  clc
  lda R6
  adc #<(MmSolidTerrain-Block_Buffer_1)
  sta M0
  lda R7
  adc #>(MmSolidTerrain-Block_Buffer_1)
  sta M1
  ldy R2
  lda (M0),y
  bne New
Attackable:
  lda R6
  clc
  adc R2
  sta RgTempX
  lda R7
  adc #0
  sta RgTempPage
  ldx #6
CheckNow:
  lda RgMeleeBlocks+8,x
  cmp RgTempX
  bne NextNow
  lda RgMeleeBlocks+9,x
  cmp RgTempPage
  beq Seen
NextNow:
  dex
  dex
  bpl CheckNow
  ldx #6
FindFree:
  lda RgMeleeBlocks+9,x
  cmp #$ff
  beq Mark
  dex
  dex
  bpl FindFree
  bmi Seen                       ; Four generic corners cover at most4 cells.
Mark:
  lda RgTempX
  sta RgMeleeBlocks+8,x
  lda RgTempPage
  sta RgMeleeBlocks+9,x
  ldx #6
CheckLast:
  lda RgMeleeBlocks,x
  cmp RgTempX
  bne NextLast
  lda RgMeleeBlocks+1,x
  cmp RgTempPage
  beq Seen
NextLast:
  dex
  dex
  bpl CheckLast
  jsr LinkThrustResponse
  lda RgThrust
  cmp #1
  bne New
  lda MmProbeY
  and #$f0
  jsr LinkClampThrustFeet
New:
  ldx MmSlot
  clc
  rts
Seen:
  ldx MmSlot
  sec
  rts
.endproc

.proc RosterIsMelee
  cmp #32
  beq Yes
  cmp #33
  beq Yes
  cmp #38
  beq Yes
  cmp #23
  bcc :+
  cmp #26
  bcc Yes
  :
  cmp #14
  bcc No
  cmp #17
  bcc Yes
  cmp #19
  bcc No
  cmp #22
  bcc Yes
No: clc
  rts
Yes: sec
  rts
.endproc
.proc RosterKeepWeapon
  cmp #59
  bcc :+
    farcall RemainingKeepWeapon
    rts
  :
  cmp #55
  bcc :+
  cmp #58
  bcc Keep
  :
  cmp #44
  beq Keep
  cmp #49
  beq Keep
  cmp #51
  beq Keep
  cmp #52
  beq Keep
  cmp #39
  beq Keep
  cmp #41
  beq Keep
  cmp #29
  beq Keep
  cmp #32
  beq Keep
  cmp #33
  beq Keep
  cmp #38
  beq Keep
  cmp #14
  bcc No
  cmp #17
  beq No
  cmp #26
  bcs No
Keep:
  sec
  rts
No: clc
  rts
.endproc
.proc RosterEnemyHit
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  bne Existing
  farcall SamusHardEnemyAdmission
  jcs Skip
Existing:
  lda MmBulletType
  cmp #59
  bcc :+
    farcall RemainingEnemyHit
    rts
  :
  lda MmBulletType
  cmp #42
  bcc :+
    farcall SpecialEnemyHit
    rts
  :
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  bcc :+
.if ::ENABLE_MMC5_EXPANDED
    farcall DwExpandedEnemyHit
.else
    farcall ExpandedEnemyHit
.endif
    rts
  :
  cmp #CHARACTER_BILL
  jcc Hit
  lda MmBulletType
  jsr RosterKeepWeapon
  jcc Stun
  lda HitBits,x
  sta RgTemp3
  lda MmBulletType
  cmp #18
  jeq Projectile
  cmp #22
  jeq Projectile
  cmp #23
  bcc OrdinaryMelee
  cmp #26
  bcs OrdinaryMelee
  lda CrossoverBehaviorVersion
  bne HardThrustHit
  farcall EasyLinkThrustHit
  jcs Skip
  jmp Stun
HardThrustHit:
  ; Thrust contact receipts follow C_HIT/L_HIT, not sword-swing lifetime.
  lda LinkThrustNow
  ora RgTemp3
  sta LinkThrustNow
  lda LinkThrustPrev
  and RgTemp3
  jne Skip
  jsr LinkThrustResponse
  lda RgThrust
  cmp #1
  bne :+
    lda Enemy_Y_Position,x
    clc
    adc #8
    jsr LinkClampThrustFeet
  :
  jmp Stun
OrdinaryMelee:
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne MeleeLifetime
  lda CrossoverBehaviorVersion
  beq MeleeLifetime
  ; Link's ordinary ATK_DCT lifetime is additional to Character's C/L_HIT.
  ; Releasing a thrust into a forward swing does not erase last contact.
  lda LinkThrustNow
  ora RgTemp3
  sta LinkThrustNow
  lda LinkThrustPrev
  and RgTemp3
  jne Skip
MeleeLifetime:
  lda RgMeleeHits
  and RgTemp3
  bne Skip
  lda RgMeleeHits
  ora RgTemp3
  sta RgMeleeHits
  jmp Stun
Projectile:
  ldy RgSlot
  lda RgShotHits,y
  and RgTemp3
  bne Skip
  lda RgShotHits,y
  ora RgTemp3
  sta RgShotHits,y
Stun:
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  beq SourceEffects
  cmp #CHARACTER_SIMON
  beq Hit                       ; DamageEnemy applies properties after armor.
  lda #12
  sta RgEnemyStun,x
  bne Hit
SourceEffects:
  lda MmBulletType
  cmp #18
  bne Hit
  ; The zero-damage boomerang has independent pierce10/STOP3000(false).
  farcall LsrEffectsBoomerang
  farcall LinkBoomerangReturn
  ldx MmEnemySlot
  jmp Skip
Hit: clc
  rts
Skip: sec
  rts
HitBits: .byte 1,2,4,8,16,32
.endproc
.proc RosterBlockSeen
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bcc New
  lda MmBulletType
  jsr RosterIsMelee
  bcc New
  lda RgThrust
  beq :+
    jmp LinkThrustBlockSeen
  :
  jsr Map
  lda (M0),y
  beq New
  sec
  rts
New: clc
  rts
Map:
  clc
  lda R6
  adc #<(RgMeleeBlocks-Block_Buffer_1)
  sta M0
  lda R7
  adc #>(RgMeleeBlocks-Block_Buffer_1)
  sta M1
  ldy R2
  rts
.endproc
.proc RosterMarkBlock
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bcc Done
  lda MmBulletType
  jsr RosterIsMelee
  bcc Done
  lda RgThrust
  bne Done                      ; Dedicated rolling thrust keys already marked.
  jsr RosterBlockSeen::Map
  lda #1
  sta (M0),y
Done:
  rts
.endproc

.proc GuestClaimBlockSlot
  ; Wide weapons can contact more than two blocks before SMB finishes their
  ; animations. Never overwrite a bouncing item/question block. A new brick
  ; shatter may replace older debris after committing its already-blank tile.
  ldx SprDataOffset_Ctrl
  jsr Reusable
  bcs Claim
  txa
  eor #1
  tax
  jsr Reusable
  bcc Busy
Claim:
  stx SprDataOffset_Ctrl
  lda Block_State,x
  beq Available
  lda Block_BBuf_Low,x
  sta M0
  lda #>Block_Buffer_1
  sta M1
  ldy Block_Orig_YPos,x
  lda #0
  sta (M0),y
  sta Block_RepFlag,x
Available:
  sec
  rts
Reusable:
  lda Block_State,x
  beq PendingReplacement
  and #$0f
  cmp #2
  bne Busy
  lda Block_Metatile,x
  beq Available
Busy:
  clc
  rts
PendingReplacement:
  lda Block_RepFlag,x
  beq Available
  bne Busy
.endproc

.segment "METASPRITE"
.proc RosterDrawShots
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  bcc :+
    jmp ExpandedDrawShots
  :
  cmp #CHARACTER_BILL
  jcc Done
  lda MmDeathFlag
  jne Done
  inc RgDrawFirst
  lda RgDrawFirst
  cmp #10
  bcc :+
    lda #0
    sta RgDrawFirst
  :
  tax
  lda #10
  sta RgDrawRemaining
Loop:
  stx RgSlot
  lda RgShotType,x
  beq SkipForeign
  cmp #32
  bcc Legacy
SkipForeign:
  jmp Next                    ;RemainingDraw owns advanced weapons and CHR.
Legacy:
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  beq Link
  cmp #CHARACTER_SIMON
  beq Simon
  jsr BillSourceDrawFrame
  jmp Pointer
Link:
  lda RgShotAge,x
  lsr
  and #3
  tay
  lda RgShotType,x
  cmp #4
  bne LinkFrame
  tya
  clc
  adc #4
  tay
  lda RgShotImpact,x
  beq LinkFrame
  jsr LinkBeamFragments
  jmp Next
LinkFrame:
  lda RgShotDir,x
  cmp #2
  bne LinkRight
  lda RgLINKWeaponsLeftLo,y
  sta R0
  lda RgLINKWeaponsLeftHi,y
  jmp Pointer
LinkRight:
  lda RgLINKWeaponsRightLo,y
  sta R0
  lda RgLINKWeaponsRightHi,y
  jmp Pointer
Simon:
  lda RgShotAge,x
  lsr
  lsr
  and #3
  tay
  lda RgSIMONWeaponsRightLo,y
  sta R0
  lda RgSIMONWeaponsRightHi,y
Pointer:
  sta R1
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
  jsr MetaspriteRenderLoop
Next:
  dec RgDrawRemaining
  beq Done
  ldx RgSlot
  inx
  cpx #10
  bcc :+
    ldx #0
  :
  jmp Loop
Done:
  rts
.endproc
.popseg


; Common1.0/2.02 source fan. Only the per-pellet spread index changes.
; Existing SpawnBill remains the pool/cap/allocation/origin/damage owner.
.pushseg
.segment "GUEST"
.proc BillSpreadFanOrdered
  ldx #0
Next:
  txa
  pha                            ; SpawnBill owns/clobbers X and scratch bytes.
  lda Order,x
  sta RgSpread
  jsr RosterWeapons::SpawnBill
  pla
  tax
  inx
  cpx #5
  bne Next
  rts                            ; Actual original BillInput caller join.
Order:
  .byte 0,1,$ff,$fe,2
.endproc
.popseg
; Exact default Bill/Lance source projection in Q8.8. Both SWF versions use
; 0.75 diagonal components; velocity and muzzle fractions are independent.
.pushseg
.segment "SPECIAL_EXTRA"
.proc BillSourceProjection
  jsr AvBillSpeedIndex
  tay
  lda RgShotType,x
  cmp #42
  beq AdvancedKey
  cmp #43
  bne LegacyKey
AdvancedKey:
  lda AdvancedIndices,y
  ldy RgShotType,x
  cpy #43
  bne :+
    clc
    adc #3
  :
  tay
LegacyKey:
  sty RgTempPage
  lda #0
  sta RgAim
  lda SavedJoypadBits
  and #Up_Dir
  beq Down
  inc RgAim                       ;1=Up,2=Up diagonal.
  lda SavedJoypadBits
  and #3
  beq AimReady
  inc RgAim
  bne AimReady
Down:
  lda SavedJoypadBits
  and #Down_Dir
  beq AimReady
  lda #3
  sta RgAim
  lda SavedJoypadBits
  and #3
  bne AimReady
  lda #5
  sta RgAim                       ; Grounded Down-only is prone.
  lda Player_State
  beq AimReady
  lda #4
  sta RgAim
  lda RgDoubleJump
  bmi AimReady                    ; Genuine launched jump retains its bit.
  lda #0
  sta RgAim                       ; Walking off retains horizontal fire.
AimReady:
  lda RgAim
  cmp #2
  beq Diagonal
  cmp #3
  beq Diagonal
  lda SpeedLo,y
  sta RgTemp
  lda SpeedHi,y
  bne SpeedReady
Diagonal:
  jmp DiagonalSpread
SpeedReady:
  sta RgTemp2
  lda RgAim
  cmp #1
  beq Vertical
  cmp #4
  beq Vertical
  lda RgTemp
  sta RgShotVXLo,x
  lda RgTemp2
  sta RgShotVXHi,x
  lda RgAim
  cmp #2
  beq Vertical
  cmp #3
  bne Spread
Vertical:
  lda RgTemp
  sta RgShotVYLo,x
  lda RgTemp2
  sta RgShotVYHi,x
  lda RgAim
  cmp #1
  beq NegateUp
  cmp #2
  bne Spread
NegateUp:
  jsr NegateY
Spread:
  clc
  lda RgSpread
  adc #2
  tay
  lda RgAim
  cmp #2
  beq DiagonalSpread
  cmp #3
  beq DiagonalSpread
  lda FanLo,y
  sta RgTemp
  lda FanHi,y
  sta RgTemp2
  lda RgAim
  cmp #1
  beq SetFanX
  cmp #4
  beq SetFanX
  lda RgTemp
  sta RgShotVYLo,x
  lda RgTemp2
  sta RgShotVYHi,x
  jmp Facing
SetFanX:
  lda RgTemp
  sta RgShotVXLo,x
  lda RgTemp2
  sta RgShotVXHi,x
  jmp Muzzle                      ; Vertical fan X is independent of facing.
DiagonalSpread:
  ; Quantize the complete source vector once, avoiding double rounding.
  lda RgTempPage
  asl
  asl
  clc
  adc RgTempPage
  adc #2
  sta RgTemp3
  clc
  adc RgSpread
  tay
  lda DiagPlusLo,y
  sta RgShotVXLo,x
  sta RgShotVYLo,x
  lda DiagPlusHi,y
  sta RgShotVXHi,x
  sta RgShotVYHi,x
  sec
  lda RgTemp3
  sbc RgSpread
  tay
  lda RgAim
  cmp #3
  beq DownSpreadX
  lda DiagPlusLo,y
  sta RgShotVYLo,x
  lda DiagPlusHi,y
  sta RgShotVYHi,x
  jsr NegateY
  jmp Facing
DownSpreadX:
  lda DiagPlusLo,y
  sta RgShotVXLo,x
  lda DiagPlusHi,y
  sta RgShotVXHi,x
Facing:
  lda PlayerFacingDir
  cmp #2
  bne Muzzle
  jsr NegateX
Muzzle:
  lda #0
  ldy Player_State
  beq GroundRow
  lda #6
  bit RgDoubleJump
  bmi GroundRow
  lda #12
GroundRow:
  clc
  adc RgAim
  tay
  sty RgTempX
  lda XHalf,y
  sta RgTemp
  lda RgAim
  cmp #1
  beq XFacing
  cmp #4
  beq XFacing
  cmp #5
  bne XSpread
  lda CrossoverBehaviorVersion
  beq XSpread
  lda PlayerFacingDir
  cmp #2
  beq XFacing                     ;2.02 pcode getproperty spreadOffset/pop.
XSpread:
  clc
  lda RgSpread
  adc #2
  tay
  lda RgTemp
  sec
  sbc OffsetHalf,y
  sta RgTemp
XFacing:
  lda PlayerFacingDir
  cmp #2
  bne XCenter
  lda #0
  sec
  sbc RgTemp
  sta RgTemp
XCenter:
  clc
  lda RgTemp
  adc #16                         ; Source nx is native left+8 pixels.
  sta RgTemp
  jsr HalfParts
  clc
  lda MmXFraction+1
  adc RgTemp3
  sta RgShotFracX,x
  lda Player_X_Position
  adc RgTemp2
  sta RgShotX,x
  lda #0
  bit RgTemp2
  bpl :+
    lda #$ff
  :
  adc Player_PageLoc
  sta RgShotPage,x
  ldy RgTempX
  lda YHalf,y
  sta RgTemp
  lda RgAim
  beq YReady
  cmp #5
  beq YReady
  clc
  lda RgSpread
  adc #2
  tay
  lda RgAim
  cmp #3
  beq YSubtract
  cmp #4
  beq YSubtract
  clc
  lda RgTemp
  adc OffsetHalf,y
  jmp YSave
YSubtract:
  sec
  lda RgTemp
  sbc OffsetHalf,y
YSave:
  sta RgTemp
YReady:
  jsr HalfParts
  clc
  lda MmYFraction+1
  adc RgTemp3
  sta RgShotFracY,x
  lda Player_Y_Position
  adc RgTemp2
  sta RgShotY,x
  lda #0
  bit RgTemp2
  bpl :+
    lda #$ff
  :
  adc Player_Y_HighPos
  sta RgShotYHigh,x
  rts
HalfParts:
  lda RgTemp
  lsr
  lda #0
  ror
  sta RgTemp3
  lda RgTemp
  cmp #$80
  ror
  sta RgTemp2
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
AdvancedIndices: .byte 12,12,12,13,13,13,14,14,14
; Hard getRealSpeed returns int before Q8 quantization.
SpeedLo: .byte 102,160,198,162,226,13,224,38,83,213,43,85,198,13,83,194,239,28
SpeedHi: .byte 2,2,2,2,2,3,2,3,3,2,3,3,2,3,3,1,1,2
DiagPlusLo: .byte 247,98,205,55,162,35,141,248,99,205,63,170,21,127,234,36,143,250,100,207,84,191,42,148,255,116,223,74,180,31,83,189,40,147,253,135,242,93,199,50,169,20,126,233,84,75,181,32,139,245,139,245,96,203,53,171,21,128,235,85,63,170,21,127,234,116,223,74,180,31,169,20,126,233,84,124,231,82,188,39,158,9,115,222,73,191,42,149,255,106
DiagPlusHi: .byte 0,1,1,2,2,1,1,1,2,2,1,1,2,2,2,1,1,1,2,2,1,1,2,2,2,1,1,2,2,3,1,1,2,2,2,1,1,2,2,3,1,2,2,2,3,1,1,2,2,2,1,1,2,2,3,1,2,2,2,3,1,1,2,2,2,1,1,2,2,3,1,2,2,2,3,0,0,1,1,2,0,1,1,1,2,0,1,1,1,2
FanLo: .byte 0,128,0,128,0
FanHi: .byte $ff,$ff,0,0,1
OffsetHalf: .byte 12,6,0,6,12
; Columns horizontal/up/updiag/downdiag/down-vertical/prone.
; Values in half-NES pixels, preserving source half-pixel origins exactly.
XHalf: .byte 35,9,27,30,0,36,25,0,19,19,0,36,25,0,25,25,0,36
YHalf: .byte 19,-29,-5,38,64,49,39,19,25,58,64,49,19,-14,3,38,64,49
.endproc
.popseg
.pushseg
.segment "BILL_GFX"
; Source BillBullet updateStats (Easy) / updateObj (Hard): .018 per update,
; capped at1.6. RgShotAge saturates35: art uses n, Hard cached bounds n-1.
.proc BillSourceDrawFrame
  ldy #6                         ; blowUp resets scale and selects end art.
  lda RgShotImpact,x
  bne Frame
  ldy #0
  lda RgShotType,x
  cmp #1
  beq Frame
  iny
  cmp #2
  beq Frame
  lda RgShotAge,x
  cmp #35
  bcc :+
    lda #35
  :
  tay
  lda GrowthArtFrame,y
  tay
Frame:
  lda RgBILLWeaponsRightLo,y
  sta R0
  lda RgBILLWeaponsRightHi,y
  rts
.endproc

; Return C1 and source-projected integer edges for Bill types11..13 only.
; Q8 extents use one rounding from the independent Flash formula. Actual
; projectile fractions participate before floor-to-native-box projection.
.segment "BILL_GFX"
.proc BillSourceBounds
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  jne Other
  lda MmBulletType,x
  cmp #69
  beq Advanced
  cmp #70
  beq Advanced
  cmp #11
  jcc Other
  cmp #14
  jcs Other
  jmp LegacyType
Advanced:
  ldy CrossoverBehaviorVersion
  jeq Other
  cmp #69
  bne Base
  ldy RgSlot
  lda RgShotVXLo,y
  ora RgShotVXHi,y
  beq Base
  lda RgShotVYLo,y
  ora RgShotVYHi,y
  beq Base
  lda #$1f                       ; nearest Q8 3/sqrt(2)=2.12132034356.
  sta RgTemp
  lda #2
  sta RgTemp2
  jmp RadiusReady
LegacyType:
  cmp #13
  bne Base
  ldy RgSlot
  lda RgShotAge,y
  cmp #35
  bcc :+
    lda #35
  :
  ldy CrossoverBehaviorVersion
  beq Index
  cmp #0
  beq Index
  sec
  sbc #1                         ; Hard super.updateObj caches before growth.
  bcs Index
Base:
  lda #0
Index:
  tay
  lda GrowthRadiusLo,y
  sta RgTemp
  lda GrowthRadiusHi,y
  sta RgTemp2
RadiusReady:
  ldy RgSlot
  sec
  lda RgShotFracX,y
  sbc RgTemp
  lda RgShotX,y
  sbc RgTemp2
  sta MmBillEdgeX+1
  lda RgShotPage,y
  sbc #0
  sta MmBillEdgePage+1
  sec
  lda RgShotFracY,y
  sbc RgTemp
  lda RgShotY,y
  sbc RgTemp2
  sta MmBillEdgeY
  lda CrossoverBehaviorVersion
  beq Symmetric
  ; Hard HRect replaces projected width/height with local6Flash=3NES.
  clc
  lda MmBillEdgeX+1
  adc #3
  sta MmBillEdgeX
  lda MmBillEdgePage+1
  adc #0
  sta MmBillEdgePage
  clc
  lda MmBillEdgeY
  adc #3
  sta MmBillEdgeY+1
  sec
  rts
Symmetric:
  clc
  lda RgShotFracX,y
  adc RgTemp
  lda RgShotX,y
  adc RgTemp2
  sta MmBillEdgeX
  lda RgShotPage,y
  adc #0
  sta MmBillEdgePage
  clc
  lda RgShotFracY,y
  adc RgTemp
  lda RgShotY,y
  adc RgTemp2
  sta MmBillEdgeY+1
  sec
  rts
Other:
  clc
  rts
.endproc
; Generated scalar tables follow this owned helper in patch_runtime.py.
; Bill-only scalar reads share the existing mapped C000 art-table ABI.
.segment "BILL_GFX"
GrowthRadiusLo: .byte 128,135,142,149,156,163,169,176,183,190,197,204,211,218,225,232,239,246,252,3,10,17,24,31,38,45,52,59,66,72,79,86,93,100,102,102
GrowthRadiusHi: .byte 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2
.segment "BILL_GFX"
GrowthArtFrame: .byte 2,2,2,2,2,2,3,3,3,3,3,3,3,3,3,3,3,4,4,4,4,4,4,4,4,4,4,4,5,5,5,5,5,5,5,5
.popseg

; Type43 exclusive center aliases. Old RAM addresses and allocations remain.
; Source LevObj.updateObj starts from displayed x/y. BillBullet caches the
; moved visible HRect in super.updateObj, then uses flareCenter.x (old draw)
; for the orbit. Level draws center.nx only after collision checks.
.pushseg
.segment "LEGACY_COLD"
.pushseg
.segment "SPECIAL_ROSTER"
.proc BillAdvancedFlareStep
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
  lda #1
  sta AvPending
  rts
.endproc
.popseg
.pushseg
.segment "SPECIAL_EXTRA"
.proc BillAdvancedFlarePublish
  lda #0
  sta AvPending
  lda SsMode,x
  bne Extended
  lda RgShotAge,x
  cmp #241
  bcs Extended
  tay
  dey
  lda RgShotDir,x
  cmp #2
  beq Left
  lda BillFlareRightXLo,y
  sta R0
  lda BillFlareRightXHi,y
  sta R1
  lda BillFlareRightYLo,y
  sta R2
  lda BillFlareRightYHi,y
  sta R3
  jmp Orbit
Left:
  farcall BillFlareLoadLeft
  jmp Orbit
Extended:
  farcall BillFlareLoadExtended
Orbit:
  clc
  lda SsArt,x
  adc R0
  sta RgShotFracX,x
  lda SsAngleLo,x
  adc R1
  sta RgShotX,x
  lda #0
  bit R1
  bpl :+
    lda #$ff
  :
  adc SsAngleHi,x
  sta RgShotPage,x
  clc
  lda SsHitTimer,x
  adc R2
  sta RgShotFracY,x
  lda SsHidden,x
  adc R3
  sta RgShotY,x
  lda #0
  bit R3
  bpl :+
    lda #$ff
  :
  adc RgShotHitsNow,x
  sta RgShotYHigh,x
  ; Advance the separate invisible center for the next displayed update.
  clc
  lda SsArt,x
  adc RgShotVXLo,x
  sta SsArt,x
  lda SsAngleLo,x
  adc RgShotVXHi,x
  sta SsAngleLo,x
  lda #0
  ldy RgShotVXHi,x
  bpl :+
    lda #$ff
  :
  adc SsAngleHi,x
  sta SsAngleHi,x
  clc
  lda SsHitTimer,x
  adc RgShotVYLo,x
  sta SsHitTimer,x
  lda SsHidden,x
  adc RgShotVYHi,x
  sta SsHidden,x
  lda #0
  ldy RgShotVYHi,x
  bpl :+
    lda #$ff
  :
  adc RgShotHitsNow,x
  sta RgShotHitsNow,x
  rts
.endproc
.popseg
.popseg

.pushseg
.segment "BILL_GFX"
BillFlareRightXLo:
 .byte 165,230,111,236,74,194,204,17,83,87,197,24,136,6,63,161
 .byte 117,247,105,53,251,161,86,137,221,20,243,39,51,89,147,150
 .byte 218,171,67,228,240,0,239,226,65,169,216,149,146,88,51,40
 .byte 244,22,223,139,88,162,251,52,103,244,115,158,61,5,135,24
 .byte 198,89,86,19,206,196,75,236,111,228,163,60,103,234,129,192
 .byte 7,110,196,153,71,14,42,235,210,160,89,76,3,49,157,4
 .byte 3,0,30,54,224,124,75,137,130,175,199,197,239,199,252,84
 .byte 143,79,3,216,176,43,177,133,226,16,130,228,41,140,136,200
 .byte 16,33,165,17,155,49,124,232,189,53,150,74,247,131,34,70
 .byte 149,207,187,3,40,104,187,209,32,243,131,20,10,255,213,177
 .byte 0,96,146,90,107,74,64,77,45,92,40,205,138,191,254,29
 .byte 57,181,43,87,0,219,118,33,232,143,154,92,18,249,107,242
 .byte 91,185,102,245,31,172,84,171,12,140,248,219,144,83,97,14
 .byte 221,143,48,17,188,233,93,212,234,1,57,104,33,196,145,195
 .byte 168,189,186,160,182,130,180,19,93,51,1,240,223,107,249,204
BillFlareRightXHi:
 .byte 8,12,15,15,14,10,5,0,250,245,241,240,240,243,247,252
 .byte 2,7,12,15,15,14,11,6,0,251,245,242,240,240,242,246
 .byte 251,1,7,11,14,16,14,11,7,1,251,246,242,240,240,242
 .byte 245,251,0,6,11,14,15,15,12,7,2,252,247,243,240,240
 .byte 241,245,250,0,5,10,14,15,15,12,8,3,253,247,243,240
 .byte 240,241,244,249,255,5,10,13,15,15,13,9,4,254,248,244
 .byte 241,240,241,244,248,254,4,9,13,15,15,13,9,4,254,249
 .byte 244,241,240,240,243,248,253,3,8,13,15,15,14,10,5,255
 .byte 250,245,241,240,240,243,247,252,2,8,12,15,15,14,11,6
 .byte 0,250,245,242,240,240,242,246,252,1,7,12,15,15,14,11
 .byte 7,1,251,246,242,240,240,242,246,251,1,6,11,14,15,15
 .byte 12,7,2,252,247,242,240,240,241,245,250,0,6,10,14,15
 .byte 15,12,8,2,253,247,243,240,240,241,244,249,255,5,10,14
 .byte 15,15,13,9,3,253,248,243,240,240,241,244,249,254,4,9
 .byte 13,15,15,13,9,4,254,249,244,241,240,240,243,248,253,3
BillFlareRightYLo:
 .byte 137,136,201,153,51,216,234,0,246,238,81,187,233,163,156,92
 .byte 49,31,230,5,205,122,75,155,250,57,115,4,133,176,76,16
 .byte 140,22,190,75,69,1,190,183,67,234,115,239,178,78,121,250
 .byte 140,198,6,102,183,136,53,253,28,226,208,163,99,91,20,67
 .byte 173,16,9,0,23,42,207,105,58,122,120,171,202,206,253,216
 .byte 14,101,156,86,4,210,164,27,159,115,211,6,125,230,49,154
 .byte 153,219,33,47,173,18,150,39,108,214,171,38,139,69,248,139
 .byte 47,87,167,224,200,12,43,100,177,195,15,225,115,8,3,0
 .byte 219,190,16,114,163,105,117,77,60,68,31,74,22,188,126,184
 .byte 253,34,69,197,61,105,15,230,122,31,224,130,137,74,1,236
 .byte 99,241,96,196,117,7,49,187,95,176,11,132,235,203,126,66
 .byte 83,5,218,147,59,32,206,251,109,224,240,1,50,91,16,178
 .byte 127,180,159,185,189,169,196,147,198,35,105,58,2,233,211,91
 .byte 231,186,15,47,143,221,15,99,85,146,221,250,141,12,170,82
 .byte 170,29,242,100,183,90,243,108,251,20,94,156,145,233,33,117
BillFlareRightYHi:
 .byte 242,246,251,1,7,11,14,16,14,11,7,1,251,246,242,240
 .byte 240,242,245,251,0,6,11,14,15,15,12,8,2,252,247,243
 .byte 240,240,241,245,250,0,5,10,14,15,15,12,8,3,253,247
 .byte 243,240,240,241,244,249,255,4,10,13,15,15,13,9,4,254
 .byte 248,244,241,240,241,244,248,254,4,9,13,15,15,13,9,4
 .byte 255,249,244,241,240,240,243,248,253,3,8,13,15,15,14,10
 .byte 5,255,250,245,241,240,240,243,247,252,2,8,12,15,15,14
 .byte 11,6,0,250,245,242,240,240,242,246,252,1,7,12,15,16
 .byte 14,11,7,1,251,246,242,240,240,242,246,251,1,6,11,14
 .byte 15,15,12,7,2,252,247,242,240,240,241,245,250,0,6,10
 .byte 14,15,15,12,8,3,253,247,243,240,240,241,244,249,255,5
 .byte 10,14,15,15,13,9,3,253,248,243,240,240,241,244,249,254
 .byte 4,9,13,15,15,13,9,4,254,249,244,241,240,240,243,248
 .byte 253,3,9,13,15,15,14,10,5,255,249,244,241,240,240,243
 .byte 247,253,2,8,12,15,15,14,10,6,0,250,245,241,240,240
.popseg

.pushseg
.segment "LEGACY_COLD"
BillFlareLeftXLoTail:
 .byte 150,139,178,196,189,226,183,236,69,131,73,3,221,187,58,194
 .byte 150,240,26,134,226,33,127,121,183,0,21,157,15,160,60,138
 .byte 248,206,68,160,79,245,124,22,55,132,191,174,251,38,108,197
 .byte 223,49,4,146,31,15,255,206,166,241,80,130,77,98,71,67
 .byte 86,59,108,57,220,150,198,254,23,46,166,27,71,242,210,114
 .byte 35,240,156,170,109,33,5,114,244,86,174,87,228,15,157,73
 .byte 166,13,147,4,235,161,99,110,22,223,139,39,3,172,216,78
 .byte 201,229,2,64,115,48,213,161,208,177,192,183,151,169,113,163
 .byte 3,81,45,1,245,234,122,9,220,44,67,151,216,254,72,52
BillFlareLeftXHi:
 .byte 0,250,245,241,240,240,243,247,252,2,8,12,15,15,14,11
 .byte 6,0,251,245,242,240,240,242,246,251,1,7,11,14,16,14
 .byte 11,7,1,251,246,242,240,240,242,246,251,0,6,11,14,15
 .byte 15,12,7,2,252,247,242,240,240,241,245,250,0,5,10,14
 .byte 15,15,12,8,3,253,247,243,240,240,241,244,249,255,5,10
 .byte 13,15,15,13,9,3,254,248,243,240,240,241,244,248,254,4
 .byte 9,13,15,15,13,9,4,254,249,244,241,240,240,243,248,253
 .byte 3,8,13,15,15,14,10,5,255,250,245,241,240,240,243,247
 .byte 252,2,8,12,15,15,14,11,6,0,250,245,241,240,240,242
 .byte 246,252,2,7,12,15,15,14,11,6,1,251,246,242,240,240
 .byte 242,246,251,1,6,11,14,15,15,12,7,2,252,246,242,240
 .byte 240,241,245,250,0,6,11,14,15,15,12,8,2,253,247,243
 .byte 240,240,241,245,249,255,5,10,14,15,15,13,9,3,253,248
 .byte 243,240,240,241,244,249,254,4,9,13,15,15,13,9,4,254
 .byte 249,244,241,240,240,243,248,254,3,9,13,15,15,13,10,5
BillFlareLeftYLo:
 .byte 0,16,29,190,86,39,107,109,167,205,216,13,235,34,118,169
 .byte 94,5,204,152,10,140,97,194,250,120,232,58,168,172,238,51
 .byte 61,181,20,145,27,92,195,152,21,127,63,249,147,61,105,186
 .byte 243,215,22,46,96,166,179,252,206,98,251,253,0,227,203,34
 .byte 134,182,120,127,81,57,58,16,56,2,171,112,176,253,41,81
 .byte 214,80,124,31,241,127,28,215,115,118,54,239,222,91,239,101
 .byte 207,133,26,68,204,107,182,9,124,221,185,106,48,69,252,216
 .byte 152,70,48,225,14,126,237,247,1,43,78,255,158,109,165,148
 .byte 182,193,179,212,166,217,52,119,65,2,227,198,74,212,167,255
 .byte 36,138,223,24,114,103,165,239,8,149,14,165,71,153,10,223
 .byte 83,172,85,244,116,9,38,114,174,160,243,36,112,207,238,66
 .byte 22,162,43,21,255,199,153,224,61,112,62,89,67,70,96,73
 .byte 125,75,236,162,204,255,17,34,150,9,53,227,199,109,37,249
 .byte 170,187,127,50,19,122,245,81,163,72,210,253,142,62,161,15
 .byte 155,17,252,179,116,124,31,225,135,28,244,154,198,62,190,223
BillFlareLeftYHi:
 .byte 240,241,244,248,254,4,9,13,15,15,13,10,4,255,249,244
 .byte 241,240,240,243,248,253,3,8,12,15,15,14,10,5,255,250
 .byte 245,241,240,240,243,247,252,2,8,12,15,15,14,11,6,0
 .byte 250,245,242,240,240,242,246,251,1,7,11,14,16,14,11,7
 .byte 1,251,246,242,240,240,242,246,251,1,6,11,14,15,15,12
 .byte 7,2,252,247,242,240,240,241,245,250,0,5,10,14,15,15
 .byte 12,8,3,253,247,243,240,240,241,244,249,255,5,10,13,15
 .byte 15,13,9,3,254,248,243,240,240,241,244,248,254,4,9,13
 .byte 15,15,13,9,4,254,249,244,241,240,240,243,248,253,3,8
 .byte 13,15,15,14,10,5,255,249,245,241,240,240,243,247,253,2
 .byte 8,12,15,15,14,11,6,0,250,245,241,240,240,242,246,252
 .byte 2,7,12,15,15,14,11,6,1,251,246,242,240,240,242,246
 .byte 251,1,6,11,14,15,15,12,7,2,252,246,242,240,240,241
 .byte 245,250,0,6,11,14,15,15,12,8,2,252,247,243,240,240
 .byte 241,245,249,255,5,10,14,15,15,13,8,3,253,248,243,240
.popseg

.pushseg
.segment "LEGACY_COLD"
; Source createLaser: spacing13 straight /9 diagonal; reveal at the
; original muzzle minus3 along each nonzero axis. Constant source velocity
; makes ceil((spacing*segment-3)/abs(v)) exactly the position-threshold
; first update. The independent native oracle checks all six velocity rows.
.pushseg
.segment "SPECIAL_ROSTER"
.pushseg
.segment "BILL_COLD"
.proc BillLaserSpacingParameters
  lda RgTempPage
  sec
  sbc #12
  asl
  asl
  sta AvTmp
  lda RgAim
  cmp #2
  beq Diag
  cmp #3
  beq Diag
  lda #13
  sta RgTemp
  bne Timer
Diag:
  lda AvTmp
  clc
  adc #12
  sta AvTmp
  lda #9
  sta RgTemp
Timer:
  lda AvTmp
  ora AvTmp2
  tay
  lda Timers,y
  sta SsHidden,x
  lda RgTemp
  sta AvTmp
  rts
Timers: .byte 0,4,9,13, 0,4,8,12, 0,4,7,11
        .byte 0,3,8,12, 0,3,7,11, 0,3,7,10
.endproc
.popseg
.popseg
.popseg

.pushseg
.segment "BILL_GFX"
BillFlareLeftXLoPrefix:
 .byte 0,68,74,190,22,140,16,77,177,134,5,115,58,250,154,74
 .byte 121,204,4,229,31,48,92,156,164,234,188,82,239,246,0,233
 .byte 215,50,152,199,135,137,85,54,49,2,38,240,154,99,169,252
 .byte 46,92,230,98,142,46,251,131,26,206,101,101,36,222,208,83
 .byte 237,106,218,149,43,86,219,118,187,8,117,208,168,88,30,55
 .byte 243,213,156,80,62,242,32,142,249,253,0,36,66,239,140,91
.popseg
.pushseg
.segment "LEGACY_COLD"
.proc BillFlareLoadLeft
  cpy #96
  bcs Tail
  lda BillFlareLeftXLoPrefix,y
  jmp XReady
Tail:
  lda BillFlareLeftXLoTail-96,y
XReady:
  sta R0
  lda BillFlareLeftXHi,y
  sta R1
  lda BillFlareLeftYLo,y
  sta R2
  lda BillFlareLeftYHi,y
  sta R3
  rts
.endproc
.popseg

; Source Laser rotation and retained end rotation. No left-facing scaleX flip.
.pushseg
.segment "BILL_COLD"
.proc BillAdvancedDrawArt
  ldy #0
  lda RgShotType,x
  cmp #42
  bne Impact
  ldy SsArt,x
  iny
Impact:
  lda RgShotImpact,x
  beq Select
  lda #0
  ldy RgShotType,x
  cpy #42
  bne EndAngle
  lda SsArt,x
EndAngle:
  clc
  adc #5
  tay
Select:
  lda Arts,y
  sta AvDrawArt
  rts
Arts:
  .byte AV_ART_BILLBULLET4,AV_ART_BILLBULLET5,AV_ART_BILLLASER45,AV_ART_BILLLASER90,AV_ART_BILLLASER135
  .byte AV_ART_BILLEND0,AV_ART_BILLEND45,AV_ART_BILLEND90,AV_ART_BILLEND135
.endproc
.popseg

; Source Projectile.checkDosSides uses the final visual bounds, after collisions.
; Native positions are Q8; floor(irrational radius*256) preserves the exact
; strict comparison for every representable Q8 position (not a rounded box).
.pushseg
.segment "BILL_COLD"
.proc BillAdvancedExpiry
  lda RgShotImpact,x
  beq Radius
  cmp #3
  beq FreshEnd
  cmp #4                        ; Birth collision transient, before batch tick.
  jne Done                      ; stopUpdate retains contact-frame viewport.
FreshEnd:
  lda #0
  sta RgShotVXLo,x
  sta RgShotVXHi,x
  sta RgShotVYLo,x
  sta RgShotVYHi,x
Radius:
  ldy #0                        ; Flare active radius4NES.
  lda RgShotType,x
  cmp #42
  bne EndRadius
  lda SsArt,x
  and #1
  bne Diagonal
  ldy #1                        ; Laser0: X6,Y3.
  lda SsArt,x
  beq EndRadius
  ldy #2                        ; Laser90: X3,Y6.
  bne EndRadius
Diagonal:
  ldy #3                        ; Laser45/135: 9/sqrt(2).
EndRadius:
  lda RgShotImpact,x
  beq XRadius
  ldy #4                        ; End0/90 and FlareEnd: 3.5.
  lda RgShotType,x
  cmp #42
  bne XRadius
  lda SsArt,x
  and #1
  beq XRadius
  iny                           ; End45/135: 7/sqrt(2).
XRadius:
  lda RadiusXLo,y
  sta R3
  lda RadiusXHi,y
  sta R4
  sty AvTmp2
  ; Explicit port boundary: no original shipped source viewport extends past
  ;6400NES (400tiles). It never truncates an attainable source trajectory.
  ; Native terrain-command extent alone is not treated as a camera clamp.
  lda RgShotFracX,x
  sta R0
  lda RgShotX,x
  sta R1
  lda RgShotPage,x
  sta R2
  jsr Lower
  jcs Kill
  jsr MinusRadius
  bmi WorldReady
  cmp #25                       ;6400NES /256.
  bcc WorldReady
  jne Kill
  lda R1
  ora R0
  jne Kill                      ; Strictly beyond6400 plus visual radius.
WorldReady:
  lda RgShotFracX,x
  sta R0
  sec
  lda RgShotX,x
  sbc ScreenLeft_X_Pos
  sta R1
  lda RgShotPage,x
  sbc ScreenLeft_PageLoc
  sta R2
  ; LevObj.updateObj caches the viewport before Level.scrollScreen. Native
  ; PlayerCtrlRoutine already scrolled, so recover that frame's old viewport.
  clc
  lda R1
  adc ScrollAmount
  sta R1
  lda R2
  adc #0
  sta R2
  jsr Lower
  bcs Kill
  jsr MinusRadius
  bmi YRadius
  beq YRadius                   ; Below256.
  cmp #1
  bne Kill
  lda R1
  ora R0
  bne Kill                      ; Strictly greater than256.
YRadius:
  ldy AvTmp2
  lda RadiusYLo,y
  sta R3
  lda RadiusYHi,y
  sta R4
  lda RgShotFracY,x
  sta R0
  lda RgShotY,x
  sta R1
  sec
  lda RgShotYHigh,x
  sbc #1                        ; Native high1 is source viewport top0.
  sta R2
  jsr Lower
  bcs Kill
  jsr MinusRadius
  bmi Done
  bne Kill
  lda R1
  cmp #240
  bcc Done
  bne Kill
  lda R0
  beq Done                      ; Exactly240 survives.
Kill:
  lda #0
  sta RgShotType,x
Done:
  rts
Lower:
  clc
  lda R0
  adc R3
  lda R1
  adc R4
  lda R2
  adc #0
  asl                           ; C1 iff position+radius is negative.
  rts
MinusRadius:
  sec
  lda R0
  sbc R3
  sta R0
  lda R1
  sbc R4
  sta R1
  lda R2
  sbc #0
  rts
RadiusXLo: .byte 0,0,0,93,128,243
RadiusXHi: .byte 4,6,3,6,3,4
RadiusYLo: .byte 0,0,0,93,128,243
RadiusYHi: .byte 4,3,6,6,3,4
.endproc

; This first additive tail covers source indices240..383; age=index+1.
; SsMode extends age across255 without changing any of the original240 scalars.
.proc BillFlareLoadExtended
  lda SsMode,x
  cmp #1
  bcc ExistingTail
  bne Late
  lda RgShotAge,x
  cmp #129
  bcs Late
ExistingTail:
  lda RgShotAge,x
  sec
  sbc #241
  tay
  lda RgShotDir,x
  cmp #2
  beq Left
  lda BillFlareExtendedRightXLo,y
  sta R0
  lda BillFlareExtendedRightXHi,y
  sta R1
  lda BillFlareExtendedRightYLo,y
  sta R2
  lda BillFlareExtendedRightYHi,y
  sta R3
  rts
Left:
  lda BillFlareExtendedLeftXLo,y
  sta R0
  lda BillFlareExtendedLeftXHi,y
  sta R1
  lda BillFlareExtendedLeftYLo,y
  sta R2
  lda BillFlareExtendedLeftYHi,y
  sta R3
  rts
Late:
  jmp BillFlareLoadLate
.endproc
BillFlareExtendedRightXLo:
  .byte 30,57,147,219,7,85,68,128,205,237,133,11,176,93,185,47
  .byte 4,115,194,95,241,100,238,3,76,139,131,225,31,121,228,13
  .byte 103,59,195,67,34,253,185,127,190,24,76,33,69,61,77,115
  .byte 103,161,112,14,188,219,0,4,10,117,227,17,197,178,101,43
  .byte 11,199,222,164,85,46,138,248,70,140,40,173,216,110,40,151
  .byte 18,172,45,30,216,151,152,48,229,126,7,213,118,161,29,166
  .byte 211,4,85,154,98,12,214,252,205,201,172,121,124,60,108,209
  .byte 43,24,0,9,14,171,65,18,89,98,163,208,227,29,255,55
  .byte 138,185,103,6,197,138,248,118,75,176,237,115,234,68,184,192
BillFlareExtendedRightXHi:
  .byte 9,13,15,15,14,10,5,255,249,244,241,240,240,243,247,253
  .byte 3,8,12,15,15,14,10,6,0,250,245,241,240,240,242,247
  .byte 252,2,7,12,15,15,14,11,6,1,251,246,242,240,240,242
  .byte 246,251,1,7,11,14,16,15,12,7,1,252,246,242,240,240
  .byte 242,245,250,0,6,11,14,15,15,12,8,2,252,247,243,240
  .byte 240,241,245,250,255,5,10,14,15,15,13,8,3,253,248,243
  .byte 240,240,241,244,249,255,4,9,13,15,15,13,9,4,254,248
  .byte 244,241,240,241,244,248,254,4,9,13,15,15,13,10,4,255
  .byte 249,244,241,240,240,243,247,253,3,8,12,15,15,14,10,5
BillFlareExtendedRightYLo:
  .byte 218,254,85,41,179,55,28,254,192,140,207,42,94,47,79,64
  .byte 73,106,88,144,94,254,176,212,255,10,22,133,245,35,211,188
  .byte 105,40,2,185,205,146,68,33,130,246,75,151,55,191,234,126
  .byte 51,156,17,164,32,14,198,134,138,40,227,130,17,228,135,179
  .byte 45,177,216,3,78,141,82,250,197,237,196,198,176,131,139,77
  .byte 126,226,56,31,0,2,2,155,47,1,74,88,159,211,236,43
  .byte 17,74,155,198,110,7,192,127,232,100,58,161,227,110,236,76
  .byte 198,209,22,88,91,200,24,135,4,59,156,113,242,102,51,251
  .byte 163,89,141,226,25,246,42,52,88,145,147,214,166,63,225,238
BillFlareExtendedRightYHi:
  .byte 242,246,252,2,7,12,15,15,14,11,6,1,251,246,242,240
  .byte 240,242,246,251,1,6,11,14,15,15,12,7,1,252,246,242
  .byte 240,240,242,245,250,0,6,11,14,15,15,12,8,2,252,247
  .byte 243,240,240,241,245,250,255,5,10,14,15,15,13,8,3,253
  .byte 248,243,240,240,241,244,249,254,4,9,13,15,15,13,9,4
  .byte 254,248,244,241,240,241,244,248,254,4,9,13,15,15,13,10
  .byte 5,255,249,244,241,240,240,243,247,253,3,8,12,15,15,14
  .byte 10,5,0,250,245,241,240,240,243,247,252,2,7,12,15,15
  .byte 14,11,6,0,251,245,242,240,240,242,246,251,1,7,11,14
BillFlareExtendedLeftXLo:
  .byte 111,189,224,126,10,180,104,200,64,21,129,204,100,240,93,225
  .byte 244,59,123,119,217,29,125,238,27,119,76,210,78,39,253,178
  .byte 116,175,7,60,20,61,58,80,124,116,177,129,29,199,225,0
  .byte 254,254,102,211,1,183,169,97,45,19,212,238,181,100,58,145
  .byte 249,65,130,25,157,200,96,30,146,20,179,57,46,233,167,165
  .byte 56,231,122,253,198,101,145,15,155,205,5,92,166,114,29,230
  .byte 9,214,204,168,112,110,44,91,194,32,18,0,15,26,186,81
  .byte 34,103,107,167,205,219,16,239,39,123,173,96,5,202,149,6
  .byte 135,92,190,247,119,232,60,172,176,243,55,64,184,21,144,24
BillFlareExtendedLeftXHi:
  .byte 255,249,244,241,240,240,243,247,253,3,8,12,15,15,14,10
  .byte 5,0,250,245,241,240,240,242,247,252,2,7,12,15,15,14
  .byte 11,6,1,251,246,242,240,240,242,246,251,1,7,11,14,16
  .byte 14,11,7,1,252,246,242,240,240,242,245,250,0,6,11,14
  .byte 15,15,12,8,2,252,247,243,240,240,241,245,250,255,5,10
  .byte 14,15,15,12,8,3,253,248,243,240,240,241,244,249,255,4
  .byte 10,13,15,15,13,9,4,254,248,244,241,240,241,244,248,254
  .byte 4,9,13,15,15,13,10,4,255,249,244,241,240,240,243,248
  .byte 253,3,8,12,15,15,14,10,5,255,250,245,241,240,240,243
BillFlareExtendedLeftYLo:
  .byte 3,71,128,64,231,178,222,186,195,179,141,154,96,145,243,69
  .byte 38,0,251,246,138,27,238,58,77,155,214,246,58,35,93,172
  .byte 211,119,8,186,115,215,81,39,145,215,105,238,85,212,227,41
  .byte 106,105,208,27,130,248,42,137,94,226,89,45,252,171,103,159
  .byte 245,43,5,51,55,84,134,131,195,147,45,212,231,0,248,242
  .byte 86,193,239,168,159,93,48,28,226,255,199,117,70,152,250,59
  .byte 118,9,139,182,81,19,142,22,187,71,63,251,184,178,64,233
  .byte 117,242,183,84,127,255,144,200,6,100,179,130,47,248,23,223
  .byte 207,165,102,96,26,73,178,20,12,0,21,38,202,100,52,117
BillFlareExtendedLeftYHi:
  .byte 240,241,244,249,254,4,9,13,15,15,13,9,4,254,248,244
  .byte 241,240,240,243,248,254,3,9,13,15,15,13,10,5,255,249
  .byte 244,241,240,240,243,247,253,3,8,12,15,15,14,10,5,0
  .byte 250,245,241,240,240,242,247,252,2,7,12,15,15,14,11,6
  .byte 0,251,246,242,240,240,242,246,251,1,7,11,14,16,14,11
  .byte 7,1,251,246,242,240,240,242,245,250,0,6,11,14,15,15
  .byte 12,8,2,252,247,243,240,240,241,245,250,255,5,10,14,15
  .byte 15,12,8,3,253,247,243,240,240,241,244,249,255,4,10,13
  .byte 15,15,13,9,4,254,248,244,241,240,241,244,248,254,4,9
.popseg

; Tables cover source indices0..4095 (ages1..4096). The explicit source-global
; visual world envelope guarantees disappearance by3666 independent of carrier
; speed. Native command extent is measured separately, not a camera theorem.
; Keep all original240 scalars exact and use the new path only after384.
.pushseg
.segment "BILL_COLD"
.proc BillFlareLoadLate
  lda RgShotAge,x
  sec
  sbc #129                      ; (age-385) low.
  sta AvTmp
  lda SsMode,x
  sbc #1
  asl
  sta AvTmp2
  lda AvTmp
  asl
  lda AvTmp2
  adc #0                        ; (age-385)/128, chunks0..28.
  tay
  lda CurrentBankC
  pha
  lda Banks,y
.if ::MAPPER_MMC5
  ora #MMC5_PRG_ROM
.endif
  BankPRGC a
  lda PointerLo,y
  sta R4
  lda PointerHi,y
  sta R5
  lda RgShotDir,x
  cmp #2
  bne Right
  inc R5
  inc R5                        ; Left four arrays follow Right512B.
Right:
  lda AvTmp
  and #127
  tay
  lda (R4),y
  sta R0
  tya
  ora #128
  tay
  lda (R4),y
  sta R1
  inc R5
  tya
  and #127
  tay
  lda (R4),y
  sta R2
  tya
  ora #128
  tay
  lda (R4),y
  sta R3
  pla
  BankPRGC a                    ; Exact actual old C bank and shadow restored.
  rts
Banks: .byte .bank(BillFlareLate0),.bank(BillFlareLate1),.bank(BillFlareLate2),.bank(BillFlareLate3),.bank(BillFlareLate4),.bank(BillFlareLate5),.bank(BillFlareLate6),.bank(BillFlareLate7),.bank(BillFlareLate8),.bank(BillFlareLate9),.bank(BillFlareLate10),.bank(BillFlareLate11),.bank(BillFlareLate12),.bank(BillFlareLate13),.bank(BillFlareLate14),.bank(BillFlareLate15),.bank(BillFlareLate16),.bank(BillFlareLate17),.bank(BillFlareLate18),.bank(BillFlareLate19),.bank(BillFlareLate20),.bank(BillFlareLate21),.bank(BillFlareLate22),.bank(BillFlareLate23),.bank(BillFlareLate24),.bank(BillFlareLate25),.bank(BillFlareLate26),.bank(BillFlareLate27),.bank(BillFlareLate28)
PointerLo: .lobytes BillFlareLate0,BillFlareLate1,BillFlareLate2,BillFlareLate3,BillFlareLate4,BillFlareLate5,BillFlareLate6,BillFlareLate7,BillFlareLate8,BillFlareLate9,BillFlareLate10,BillFlareLate11,BillFlareLate12,BillFlareLate13,BillFlareLate14,BillFlareLate15,BillFlareLate16,BillFlareLate17,BillFlareLate18,BillFlareLate19,BillFlareLate20,BillFlareLate21,BillFlareLate22,BillFlareLate23,BillFlareLate24,BillFlareLate25,BillFlareLate26,BillFlareLate27,BillFlareLate28
PointerHi: .hibytes BillFlareLate0,BillFlareLate1,BillFlareLate2,BillFlareLate3,BillFlareLate4,BillFlareLate5,BillFlareLate6,BillFlareLate7,BillFlareLate8,BillFlareLate9,BillFlareLate10,BillFlareLate11,BillFlareLate12,BillFlareLate13,BillFlareLate14,BillFlareLate15,BillFlareLate16,BillFlareLate17,BillFlareLate18,BillFlareLate19,BillFlareLate20,BillFlareLate21,BillFlareLate22,BillFlareLate23,BillFlareLate24,BillFlareLate25,BillFlareLate26,BillFlareLate27,BillFlareLate28
.endproc
.popseg
.include "bill_flare_lifetime.inc"
