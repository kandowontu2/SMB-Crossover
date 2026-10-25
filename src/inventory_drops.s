; 2.02 enemy collectibles. Four private slots never consume enemy/shot slots.
.pushseg
.segment "FIXED"
.proc InventoryStompDropHook
  lda Enemy_ID,x
  cmp #Goomba
  bne :+
    jmp InventoryDropHook
  :
  rts
.endproc
.proc InventoryDropHook
  php
  pha
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne Allowed
  lda SophiaDropBlocked
  beq Allowed
  pla
  plp
  rts
Allowed:
  pla
  plp
.if ::ENABLE_MMC5_EXPANDED
  farcall RlDropDispatch
.else
  farcall InventoryEnemyDrop
.endif
  rts
.endproc
.segment "INVENTORY"
; Same probability/ownership/cap checks, with an explicit world origin. The
; sentinel avoids temporarily mutating an enemy slot for a delayed effect.
.proc InventoryDropPoint
  php
  pha
  phx
  phy
  lda #$80
  sta InvDropEnemy
  jmp InventoryDropCheckCharacter
.endproc
.proc InventoryEnemyDrop
  php
  pha
  phx
  phy
  stx InvDropEnemy
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne CheckCharacter
  lda Enemy_ID,x
  cmp #Bowser                 ; source Bowser forceDefaultDeath/dropsItems=false.
  jeq Done
CheckCharacter:
::InventoryDropCheckCharacter:
  jsr InventoryLegacyClassic
  jcs Done                      ; Original guests have no2.02 ammo/energy drops.
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  beq Chance
  cmp #CHARACTER_BASS
  beq Chance
.if ::ENABLE_MMC5_EXPANDED
  farcall DwCanDrop
.else
  farcall RemainingCanDrop
.endif
  jcc Done
Chance:
  ldx InvDropEnemy
  bmi PointChance
  lda Enemy_State,x
  and #$20
  jne Done
PointChance:
  lda PseudoRandomBitReg+1
  and #3                         ; DROP_RATE=.25.
  jne Done
  ldx #3
Find:
  lda InvDropKind,x
  beq Spawn
  dex
  bpl Find
  jmp Done
Spawn:
  lda #1
  ldy PseudoRandomBitReg+2
  cpy #192                       ; 75% small, 25% big.
  bcc :+
    lda #2
  :
  sta InvDropKind,x
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  beq :+
  cmp #CHARACTER_BASS
  beq :+
.if ::ENABLE_MMC5_EXPANDED
    farcall DwDropMade
.else
    farcall RemainingDropMade
.endif
  :
  ldy InvDropEnemy
  bmi PointPosition
  clc
  lda Enemy_X_Position,y
  adc #8
  sta InvDropX,x
  lda Enemy_PageLoc,y
  adc #0
  sta InvDropPage,x
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne NativeY
  lda Enemy_ID,y
  cmp #PiranhaPlant
  bne SophiaY
  ; Source PiranhaGreen.topY is the fully raised bottom pivot. Native art
  ; extends24px below UpY; appearFromObject subtracts the pickup half-height8.
  lda PiranhaPlantUpYPos,y
  clc
  adc #16
  jmp StoreY
SophiaY:
  ; The actual shared enemy hurtbox is [EnemyY+8, EnemyY+24]: center+16.
  ; Source pickups have a bottom pivot, so center plus half-height8 =>+24.
  lda Enemy_Y_Position,y
  clc
  adc #24
  jmp StoreY
NativeY:
  lda Enemy_Y_Position,y
  clc
  adc #8
StoreY:
  sta InvDropY,x
  jmp Physics
PointPosition:
  lda RgTempX
  sta InvDropX,x
  lda RgTempPage
  sta InvDropPage,x
  lda RgTempY
  sta InvDropY,x
Physics:
  lda #0
  sta InvDropFraction,x
  sta InvDropFractionHi,x
  sta InvDropAge,x
  sta InvDropAgeHi,x
  lda #$55                       ; INITIAL_VY=-200/120, Q8.16.
  sta InvDropVY,x
  sta InvDropVYMid,x
  lda #$fe
  sta InvDropVYHi,x
Done:
  ply
  plx
  pla
  plp
  rts
.endproc

.proc InventoryUpdateDrops
  lda TimerControl
  jne Done
  lda GameEngineSubroutine
  cmp #8
  jne Done
  ldx #3
Loop:
  stx InvDropSlot
  lda InvDropKind,x
  jeq Next
  inc InvDropAge,x
  bne :+
    inc InvDropAgeHi,x
  :
  lda InvDropAgeHi,x
  cmp #1
  bne Physics
  lda InvDropAge,x
  cmp #164                       ; 4000ms opaque + 3000ms fading.
  jcs Kill
Physics:
  clc
  lda InvDropVY,x
  adc #$c7                       ; Source pickup gravity 1400/7200.
  sta InvDropVY,x
  lda InvDropVYMid,x
  adc #$31
  sta InvDropVYMid,x
  lda InvDropVYHi,x
  adc #0
  sta InvDropVYHi,x
  clc
  lda InvDropFraction,x
  adc InvDropVY,x
  sta InvDropFraction,x
  lda InvDropFractionHi,x
  adc InvDropVYMid,x
  sta InvDropFractionHi,x
  lda InvDropY,x
  adc InvDropVYHi,x
  sta InvDropY,x
  cmp #240
  jcs Kill
  lda InvDropVYHi,x
  bmi Collect
  lda InvDropX,x
  sta RgTempX
  lda InvDropPage,x
  sta RgTempPage
  lda InvDropY,x
  sta RgTempY
  farcall ExpandedMapCell
  ldx InvDropSlot
  bcc Collect
  lda RgTempY
  and #$f0
  sta InvDropY,x
  lda #0
  sta InvDropVY,x
  sta InvDropVYMid,x
  sta InvDropVYHi,x
  sta InvDropFraction,x
  sta InvDropFractionHi,x
Collect:
  lda Player_Y_HighPos
  cmp #1
  jne Next
  lda Player_X_Position
  clc
  adc #8
  sta InvTmp
  lda Player_PageLoc
  adc #0
  sta InvTmpHi
  lda InvTmp
  sec
  sbc InvDropX,x
  sta InvTmp
  lda InvTmpHi
  sbc InvDropPage,x
  sta InvTmpHi
  clc
  lda InvTmp
  adc #11
  sta InvTmp
  lda InvTmpHi
  adc #0
  jne Next
  lda InvTmp
  cmp #23
  bcs Next
  lda Player_Y_Position
  clc
  adc #16
  sec
  sbc InvDropY,x
  clc
  adc #18
  cmp #37
  bcs Next
  lda #8
  ldy InvDropKind,x
  cpy #2
  bne :+
    lda #40
  :
  pha
  lda AvDropItem,x
  sta AvRefillItem
  pla
.if ::ENABLE_MMC5_EXPANDED
  farcall RlRefillDispatch
.else
  jsr InventoryRefillAmount
.endif
  ldx InvDropSlot
Kill:
  lda #0
  sta InvDropKind,x
Next:
  ldx InvDropSlot
  dex
  jpl Loop
Done:
  rts
.endproc

.proc InventoryPrivatePickup
  phx
  jsr InventorySupported
  plx
  bcc Done
  lda InvPickupOwner,x
  cmp SelectedCharacter
  bne Native
  lda InvPickup,x
  beq Native
  cmp #$fc
  bcc Private
  cmp #$fe
  beq Private
Native:
  clc
Done:
  rts
Private:
  sec
  rts
.endproc
.proc InventoryPickupCollision
  jsr InventoryPrivatePickup
  bcc Allowed
  lda Enemy_State,x
  bmi Allowed
  cmp #2
  bcc Hidden                    ; Still entirely inside its solid parent block.
  txa
  asl
  asl
  tay
  lda Enemy_Y_Position,x
  clc
  adc #8
  sta EnemyBoundingBoxCoord+1,y
  ; During the rise, Y + state + 7 is the original block top. Only
  ; expose the pickup above it, even if Bass's head probe penetrates a
  ; few pixels into the tile on the collision update.
  lda Enemy_Y_Position,x
  clc
  adc Enemy_State,x
  adc #6
  sta EnemyBoundingBoxCoord+3,y
Allowed:
  sec
  rts
Hidden:
  clc
  rts
.endproc
.proc InventoryRisePickup
  jsr InventoryPrivatePickup
  bcc Native
  lda TimerControl
  bne Handled
  inc InvRisePhase,x
  lda InvRisePhase,x
  cmp #3                        ; Pickup.riseSpeed=40: 1 NES pixel / 3 updates.
  bcc Handled
  lda #0
  sta InvRisePhase,x
  dec Enemy_Y_Position,x
  inc Enemy_State,x
  lda Enemy_State,x
  cmp #17                       ; Sixteen pixels, exactly 48 updates.
  bcc Handled
  lda #$80
  sta Enemy_State,x
  lda #0
  sta Enemy_SprAttrib,x
  sta Enemy_X_Speed,x
Handled:
  sec
Native:
  rts
.endproc
.proc InventoryDrawPickups
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  beq Draw
  cmp #CHARACTER_BASS
  jne Done
Draw:
  ldx #5
World:
  stx InvDrawSlot
  lda Enemy_Flag,x
  jeq NextWorld
  lda Enemy_ID,x
  cmp #PowerUpObject
  jne NextWorld
  jsr InventoryPrivatePickup
  jcc NextWorld
  lda InvPickup,x
  cmp #$fe
  bne Upgrade
  lda FrameCounter
  and #4
  beq :+
    lda #1
  :
  clc
  adc #SS_ART_PICKUP14
  bne Art
Upgrade:
  tay
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  bne :+
    cpy #8
    bne :+
      ldy #9
  :
  lda UpgradeArt,y
  cpy #9
  bne :+
    pha
    lda FrameCounter
    and #4
    beq Still
    pla
    clc
    adc #1
    bne Art
Still:
    pla
  :
Art:
  farcall SpecialPickupArt
  jcc NextWorld
  ldx InvDrawSlot
  sec
  lda Enemy_X_Position,x
  sbc ScreenLeft_X_Pos
  sta R4
  lda Enemy_PageLoc,x
  sbc ScreenLeft_PageLoc
  sta R5
  clc
  lda R4
  adc #8
  sta R4
  lda R5
  adc #0
  sta R5
  lda Enemy_Y_Position,x
  clc
  adc #24                       ; Native origin is 8 above the art; source pivot is its bottom.
  sta R6
  lda Enemy_Y_HighPos,x
  sta R7
  lda Enemy_SprAttrib,x
  and #$20
  sta R3
  farcall MetaspriteRenderLoop
NextWorld:
  ldx InvDrawSlot
  dex
  jpl World
  ldx #3
Drops:
  stx InvDrawSlot
  lda InvDropKind,x
  jeq NextDrop
  lda InvDropAgeHi,x
  bne Fade
  lda InvDropAge,x
  cmp #240
  bcc Visible
Fade:
  lda FrameCounter
  and #1
  bne NextDrop
Visible:
  lda InvDropKind,x
  cmp #1
  beq Small
  lda #SS_ART_PICKUP14
  bne EnergyArt
Small:
  lda #SS_ART_PICKUP16
EnergyArt:
  sta InvDrawArt
  lda FrameCounter
  and #4
  beq :+
    inc InvDrawArt
  :
  lda InvDrawArt
  farcall SpecialPickupArt
  bcc NextDrop
  ldx InvDrawSlot
  sec
  lda InvDropX,x
  sbc ScreenLeft_X_Pos
  sta R4
  lda InvDropPage,x
  sbc ScreenLeft_PageLoc
  sta R5
  lda InvDropY,x
  sta R6
  lda #1
  sta R7
  lda #0
  sta R3
  farcall MetaspriteRenderLoop
NextDrop:
  ldx InvDrawSlot
  dex
  jpl Drops
Done:
  rts
UpgradeArt:
  .byte 0,SS_ART_PICKUP3,SS_ART_PICKUP4,SS_ART_PICKUP5,SS_ART_PICKUP6
  .byte SS_ART_PICKUP7,SS_ART_PICKUP8,SS_ART_PICKUP13,SS_ART_PICKUP10,SS_ART_PICKUP1,0
.endproc
.popseg
