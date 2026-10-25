; Samus beams and Morph Ball bombs from the pinned hosted ActionScript.
.pushseg
.segment "SAMUS"
.proc SamusWeapons
  lda #0
  sta Fireball_State
  sta Fireball_State+1
  sta ObjectMetasprite+7
  sta ObjectMetasprite+8
  lda TimerControl
  jne Done
  lda GameEngineSubroutine
  cmp #8
  beq Active
  lda #0
  ldx #2
Clear:
  sta SmShotType,x
  sta SmBombAge,x
  dex
  bpl Clear
  rts
Active:
  ; Empty primary/bomb pools and no B input cannot query an enemy this batch.
  ; Active effects and a possible new beam retain the original fresh cache.
  lda SmShotType
  ora SmShotType+1
  ora SmShotType+2
  ora SmBombAge
  ora SmBombAge+1
  ora SmBombAge+2
  bne PrepareEnemies
  lda A_B_Buttons
  and #B_Button
.if ::MAPPER_MMC5
  bne PrepareEnemies
  jmp EmptyUpdate
.else
  beq EnemiesReady
.endif
PrepareEnemies:
  farcall GuestPrepareEnemies
EnemiesReady:
  lda SmShootPose
  beq :+
    dec SmShootPose
  :
  lda Player_State
  cmp #3
  beq Update
  lda A_B_Buttons
  eor PreviousA_B_Buttons
  and A_B_Buttons
  and #B_Button
  beq Update
  lda SmBall
  beq Fire
  jsr DropBomb
  jmp Update
Fire:
  farcall AvSamusPrimary
  bcs Update
  jsr Spawn
Update:
  ldx #2
Shots:
  stx SmSlot
  lda SmShotType,x
  jeq Next
  lda SmShotImpact,x
  beq Flying
  dec SmShotImpact,x
  bne Next
  jmp Kill
Flying:
  inc SmShotAge,x
  lda SmShotType,x
  cmp #1
  bne :+
    lda SmShotAge,x
    cmp #12
    bcs Kill
  :
  jsr Move
  lda SmShotType,x
  beq Next
  jsr BridgeShot
.if ::ENABLE_MMC5_EXPANDED
  ; BridgeShot hands the shared projectile over in slot0 and returns X=0.
  ; The bridged type, rather than a now-unrelated Samus pool index, owns
  ; whether this live projectile can collide with terrain.
  lda MmBulletType
  cmp #9
.else
  lda SmShotType,x
  cmp #3
.endif
  beq :+
    farcall MegaManWeapons::Blocks
  :
  ldx #0
  lda MmBulletType
  beq Impact
  lda GuestEnemyMask
  beq Next
  ldx #0
  farcall MegaManWeapons::Enemies
  lda MmBulletType
  bne Next
Impact:
  ldx SmSlot
  lda #3
  sta SmShotImpact,x
  jmp Next
Kill:
  ldx SmSlot
  lda #0
  sta SmShotType,x
Next:
  ldx SmSlot
  dex
  jpl Shots
  ldx #2
Bombs:
  stx SmSlot
  lda SmBombAge,x
  beq NextBomb
  inc SmBombAge,x
  lda SmBombAge,x
  cmp #82
  bcc :+
    lda #0
    sta SmBombAge,x
    beq NextBomb
  :
  cmp #58
  bcc NextBomb
  bne :+
    lda SmSfx
    ora #8
    sta SmSfx
  :
  jsr BombBoost
  jsr BombBlocks
  ldx SmSlot
  lda SmBombX,x
  sta MmBulletX
  lda SmBombPage,x
  sta MmBulletPage
  lda SmBombY,x
  sta MmBulletY
  jsr BombBridge
  lda GuestEnemyMask
  beq NextBomb
  farcall MegaManWeapons::Enemies
NextBomb:
  ldx SmSlot
  dex
  bpl Bombs
  ; The shared collision bridge does not own a visible Mega Man projectile.
  lda #0
  sta MmBulletType
Done:
  rts

.if ::MAPPER_MMC5
EmptyUpdate:
  ; Entry: active engine, both three-slot pools empty, current B released.
  ; Keep the firing-pose timer and original empty-loop completion ABI.
  lda SmShootPose
  beq :+
    dec SmShootPose
  :
  lda Player_State
  cmp #3                       ; Original path leaves this carry unchanged.
  ldx #0
  stx SmSlot
  dex
  lda #0
  sta MmBulletType
  rts
.endif

Spawn:
  ldx #2
Find:
  lda SmShotType,x
  beq Slot
  dex
  bpl Find
  rts
Slot:
  stx SmSlot
  farcall SamusBeamType
BeamType:
  ldx SmSlot
  sta SmShotType,x
  lda #0
  sta SmShotAge,x
  sta SmShotFraction,x
  sta SmShotImpact,x
  lda SmWavePolarity
  eor #1
  sta SmWavePolarity
  sta SmShotPolarity,x
  lda PlayerFacingDir
  sta SmShotDir,x
  jsr SamusMuzzle
  ldx SmSlot
  lda SmTempX
  sta SmShotX,x
  lda SmTempPage
  sta SmShotPage,x
  lda SmTempY
  sta SmShotY,x
  lda SavedJoypadBits
  and #Up_Dir
  beq PoseTimer
  lda #3
  sta SmShotDir,x
PoseTimer:
  lda #3
  ldy Player_X_Speed
  beq :+
    lda #9
  :
  sta SmShootPose
  lda SmShotY,x
  ldy SmShotDir,x
  cpy #3
  bne :+
    lda SmShotX,x
  :
  sta SmShotCenter,x
  lda #Sfx_Fireball
  sta Square1SoundQueue
  rts

Move:
  lda SmShotType,x
  cmp #3
  beq WaveSpeed
  lda #43                        ; round(1/6 * 256)
  ldy #4
  jmp AddStep
WaveSpeed:
  lda #85                       ; wave: 400 / 120 = 3 1/3
  ldy #3
AddStep:
  clc
  adc SmShotFraction,x
  sta SmShotFraction,x
  tya
  adc #0
  sta SmTemp
  lda SmShotDir,x
  cmp #3
  beq MoveUp
  cmp #1
  bne MoveLeft
  clc
  lda SmShotX,x
  adc SmTemp
  sta SmShotX,x
  lda SmShotPage,x
  adc #0
  jmp Page
MoveLeft:
  sec
  lda SmShotX,x
  sbc SmTemp
  sta SmShotX,x
  lda SmShotPage,x
  sbc #0
Page:
  sta SmShotPage,x
  jmp Wave
MoveUp:
  sec
  lda SmShotY,x
  sbc SmTemp
  sta SmShotY,x
  cmp #$20
  bcc MoveKill
Wave:
  lda SmShotType,x
  cmp #3
  bne Onscreen
  ldy SmShotAge,x
  dey                           ; The source forms the first wave at angle zero.
  lda WaveTable,y
  ldy SmShotPolarity,x
  bne :+
    eor #$ff
    clc
    adc #1
  :
  clc
  adc SmShotCenter,x
  ldy SmShotDir,x
  cpy #3
  beq WaveUp
  sta SmShotY,x
  jmp Onscreen
WaveUp:
.if ::ENABLE_MMC5_EXPANDED
  jsr SamusWaveWorldX
.else
  sta SmShotX,x
.endif
Onscreen:
  lda SmShotX,x
  sec
  sbc ScreenLeft_X_Pos
  lda SmShotPage,x
  sbc ScreenLeft_PageLoc
  bne MoveKill
  rts
MoveKill:
  lda #0
  sta SmShotType,x
  rts

BridgeShot:
  ldx SmSlot
  lda SmShotX,x
  sta MmBulletX
  lda SmShotPage,x
  sta MmBulletPage
  lda SmShotY,x
  sta MmBulletY
  lda SmShotDir,x
  sta MmBulletDir
  lda SmShotType,x
  clc
  adc #6
  sta MmBulletType
  lda #0
  sta MmSlot
  tax
  rts

DropBomb:
  ldx #2
BombSlot:
  lda SmBombAge,x
  beq BombFound
  dex
  bpl BombSlot
  rts
BombFound:
  lda #1
  sta SmBombAge,x
  lda #0
  sta SmBombHits,x
  sta SmBombBoosted,x
  sta SmBombBlocksDone,x
  clc
  lda Player_X_Position
  adc #8
  sta SmBombX,x
  lda Player_PageLoc
  adc #0
  sta SmBombPage,x
  clc
  lda Player_Y_Position
  adc #26
  sta SmBombY,x
  lda SmSfx
  ora #4
  sta SmSfx
  rts
BombBridge:
  lda #10
  sta MmBulletType
  lda #1
  sta MmBulletDir
  lda #0
  sta MmSlot
  tax
  rts
BombBoost:
  lda SmBombBoosted,x
  bne NoBoost
  lda MmVY+2
  bmi NoBoost
  lda Player_X_Position
  clc
  adc #8
  sec
  sbc SmBombX,x
  clc
  adc #16
  cmp #33
  bcs NoBoost
  lda Player_Y_Position
  clc
  adc #25
  sec
  sbc SmBombY,x
  clc
  adc #20
  cmp #41
  bcs NoBoost
  inc SmBombBoosted,x
  lda #$55
  sta MmVY
  lda #$15
  sta MmVY+1
  lda #$fe
  sta MmVY+2
  sta Player_Y_Speed
  lda #1
  sta Player_State
  lda CrossoverBehaviorVersion
  beq LegacyStep
  lda #1
  sta SmSourceJumped
  rts
LegacyStep:
  ; Old hitProj retains jumped history and immediately updates both axes.
  phx
  phy
  farcall SamusLegacyBombStep
  ply
  plx
NoBoost:
  rts
BombBlocks:
  lda SmBombBlocksDone,x
  bne BlocksDone
  inc SmBombBlocksDone,x
  lda #8
  sta SmBombCell
Cell:
  ldx SmSlot
  ldy SmBombCell
  lda CellX,y
  sta SmTemp
  clc
  adc SmBombX,x
  sta MmBulletX
  lda #0
  bit SmTemp
  bpl :+
    lda #$ff
  :
  adc SmBombPage,x
  sta MmBulletPage
  lda CellY,y
  clc
  adc SmBombY,x
  sta MmBulletY
  jsr BombBridge
  farcall MegaManWeapons::Blocks
  dec SmBombCell
  bpl Cell
BlocksDone:
  rts
CellX: .byte -16,0,16,-16,0,16,-16,0,16
CellY: .byte -16,-16,-16,0,0,0,16,16,16
WaveTable:
  .include "samus_wave.inc"
.endproc

; Shared by normal, Ice and missile shots. The 2.02 crouch muzzle is
; 27 Flash pixels above the feet (13.5 NES pixels); round to a whole pixel.
.proc SamusMuzzle
  ldy #21
  lda PlayerFacingDir
  cmp #1
  beq :+
    ldy #$fb
  :
  lda SavedJoypadBits
  and #Up_Dir
  beq HorizontalSpawn
  ldy #10
  lda PlayerFacingDir
  cmp #1
  beq :+
    ldy #6
  :
HorizontalSpawn:
  tya
  sta SmTemp
  clc
  adc Player_X_Position
  sta SmTempX
  lda #0
  bit SmTemp
  bpl :+
    lda #$ff
  :
  adc Player_PageLoc
  sta SmTempPage
  ldy #10
  lda Player_State
  beq :+
    ldy #17
  :
  lda SmCrouch
  beq :+
    ldy #19
  :
  lda SavedJoypadBits
  and #Up_Dir
  beq :+
    ldy #$fc
  :
  tya
  ldy #0
  cmp #$80
  bcc :+
    dey
  :
  sty SmClearance
  clc
  adc Player_Y_Position
  sta SmTempY
  lda Player_Y_HighPos
  adc SmClearance
  sta SmClearance
  rts
.endproc

.segment "SAMUS"
.proc SamusDrawShots
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  beq :+
    rts
  :
  lda #0
  sta SsChrActive
  lda #$ff
  sta SsDrawFamily
  lda FrameCounter
  and #1
  bne :+
    farcall RemainingDraw
  :
  lda MmDeathFlag
  beq :+
    jsr SamusPublishChr
    jmp SamusDrawDeath
  :
  inc SsDrawFirst
  lda SsDrawFirst
  cmp #6
  bcc :+
    lda #0
    sta SsDrawFirst
  :
  sta SsSlot
  lda #6
  sta SsDrawRemaining
  lda SmShotType
  ora SmShotType+1
  ora SmShotType+2
  ora SmBombAge
  ora SmBombAge+1
  ora SmBombAge+2
  bne Slot
  ; Keep the rotating cursor and exhausted scratch exactly as the six empty
  ; slots do, without visiting each one. Active shots/bombs keep the full loop.
  lda SsSlot
  sec
  sbc #1
  bpl EmptyLast
  lda #5
EmptyLast:
  sta SsSlot
  cmp #3
  bcc EmptyIndex
  sbc #3
EmptyIndex:
  tax
  stx SmSlot
  lda #0
  sta SsDrawRemaining
  jmp Done
Slot:
  lda SsSlot
  cmp #3
  bcs BombSlot
  tax
Shots:
  stx SmSlot
  lda SmShotType,x
  beq Next
  sec
  sbc #1
  asl
  asl
  clc
  adc #METASPRITE_SAMUS_BEAM_1
  ldy SmShotImpact,x
  beq :+
    clc
    adc #2
  :
  ldy SmShotDir,x
  cpy #3
  bne :+
    clc
    adc #1
  :
  tay
  lda SmShotX,x
  sec
  sbc ScreenLeft_X_Pos
  sta R4
  lda SmShotPage,x
  sbc ScreenLeft_PageLoc
  sta R5
  lda SmShotY,x
  sta R6
  jsr Draw
Next:
  jmp NextSlot
BombSlot:
  sec
  sbc #3
  tax
Bombs:
  stx SmSlot
  lda SmBombAge,x
  beq NextBomb
  cmp #58
  bcs Explosion
  lsr
  and #1
  jmp BombPose
Explosion:
  sec
  sbc #58
  ldy #2
Divide:
  cmp #6
  bcc ExplodePose
  sbc #6
  iny
  cpy #5
  bcc Divide
  lda SmBombAge,x
  and #2
  beq NextBomb
  ldy #4
ExplodePose:
  tya
BombPose:
  clc
  adc #METASPRITE_SAMUS_BOMB_1
  tay
  lda SmBombX,x
  sec
  sbc ScreenLeft_X_Pos
  sta R4
  lda SmBombPage,x
  sbc ScreenLeft_PageLoc
  sta R5
  lda SmBombY,x
  sta R6
  jsr Draw
NextBomb:
NextSlot:
  dec SsDrawRemaining
  beq Done
  inc SsSlot
  lda SsSlot
  cmp #6
  jcc Slot
  lda #0
  sta SsSlot
  jmp Slot
Done:
  lda FrameCounter
  and #1
  beq :+
    farcall RemainingDraw
  :
  jsr SamusPublishChr
  rts
Draw:
  phy
  jsr SamusWeaponArt
  ply
  bcs :+
    rts
  :
  ldx SmSlot
  lda SmShotDir,x
  tya
  sec
  sbc #METASPRITE_SAMUS_BEAM_1
  tay
  lda SmShotDir,x
  cmp #2
  bne Right
  lda WeaponLeftLo,y
  sta R0
  lda WeaponLeftHi,y
  jmp Pointer
Right:
  lda WeaponRightLo,y
  sta R0
  lda WeaponRightHi,y
Pointer:
  sta R1
  lda #1
  sta R7
  lda #0
  sta R3
  farcall MetaspriteRenderLoop
  rts
; The global metasprite pointer tables live in the renderer's A000 bank.
; SamusDrawShots executes in SAMUS, so use private tables in this same bank.
.macro SamusWeaponPointers Side, Operator
 .repeat 6,I
  .byte Operator .ident(.sprintf("SmSAMUS_BEAM_%d%s",I+1,Side))
  .byte Operator .ident(.sprintf("SmSAMUS_BEAM_%d_UP%s",I+1,Side))
 .endrepeat
 .repeat 6,I
  .byte Operator .ident(.sprintf("SmSAMUS_BOMB_%d%s",I+1,Side))
 .endrepeat
.endmacro
WeaponLeftLo: SamusWeaponPointers "Left", <
WeaponLeftHi: SamusWeaponPointers "Left", >
WeaponRightLo: SamusWeaponPointers "Right", <
WeaponRightHi: SamusWeaponPointers "Right", >
.assert METASPRITE_SAMUS_BOMB_6-METASPRITE_SAMUS_BEAM_1=17,error,"Samus private weapon table order"
.endproc

.proc SamusPublishChr
  GuestPublishChrLocal
  rts
.endproc

.segment "SAMUS"
.proc SamusWeaponArt
  tya
  sec
  sbc #METASPRITE_SAMUS_BEAM_1
  tay
  lda SamusWeaponFamilies,y
  tax
  lda SmWeaponPhysicalBanks,x
.if ::MAPPER_MMC5
  ora #1
.endif
  ldx SsChrActive
  beq Choose
  cmp SsChrPhysical
  bne No
Choose:
  sta SsChrPhysical
  lda #1
  sta SsChrActive
  sec
  rts
No:
  clc
  rts
.endproc
.segment "SAMUS"

.proc SamusDrawDeath
  lda MmDeathPit
  jne Done
  lda MmDeathAge
  cmp #41
  jcs Done
  lsr
  and #3
  sta SmDeathGfx
  clc
  adc #SAMUS_CHR_DEATH
  cmp PlayerChrBank
  beq :+
    sta PlayerChrBank
    inc ReloadCHRBank
  :
  lda CurrentOAMOffset
  pha
  lda #0
  sta CurrentOAMOffset
  lda #5
  sta SmDeathPart
Loop:
  lda SmDeathGfx
  asl
  clc
  adc SmDeathGfx
  asl
  clc
  adc SmDeathPart
  tax
  lda SamusGutsLo,x
  sta R0
  lda SamusGutsHi,x
  sta R1
  ldy MmDeathAge
  lda DeathDistance,y
  sta SmTemp
  lda SmDeathPart
  and #1
  beq Left
  clc
  lda MmDeathX
  adc SmTemp
  sta R4
  lda MmDeathPage
  adc #0
  jmp XReady
Left:
  sec
  lda MmDeathX
  sbc SmTemp
  sta R4
  lda MmDeathPage
  sbc #0
XReady:
  sta R5
  sec
  lda R4
  sbc ScreenLeft_X_Pos
  sta R4
  lda R5
  sbc ScreenLeft_PageLoc
  sta R5
  lda SmDeathPart
  lsr
  tax
  lda DeathTableLo,x
  sta R6
  lda DeathTableHi,x
  sta R7
  lda (R6),y
  clc
  adc Player_Y_Position
  sta R6
  lda #1
  sta R7
  lda #0
  sta R3
  farcall MetaspriteRenderLoop
  dec SmDeathPart
  jpl Loop
  pla
  sta CurrentOAMOffset
Done:
  rts
DeathTableLo: .byte <DeathTop,<DeathMid,<DeathBottom
DeathTableHi: .byte >DeathTop,>DeathMid,>DeathBottom
  .include "samus_death_tables.inc"
.endproc
.popseg
