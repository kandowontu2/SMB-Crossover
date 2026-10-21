; LinkBoomerang.as: directional launch, distance braking and spring return.
.pushseg
.segment "ROSTER"
.proc LinkBoomerangSpawn
  ldx RgSlot
  lda #0
  sta RgBoomReturning
  sta RgBoomFriction
  lda CrossoverBehaviorVersion
  bne OwnedBoom
  lda PlayerStatus
  cmp #2
  jmp BoomTier
OwnedBoom:
  lda #3
  farcall InventoryHas
BoomTier:
  lda #0
  bcc :+
    lda #2
  :
  sta RgBoomPower
  ldx RgSlot
  lda #$80
  ldy #2
  lda RgBoomPower
  cmp #2
  bcc :+
    lda #$55
    ldy #3
    bne Speed
  :
  lda #$80
Speed:
  sta RgShotVXLo,x
  tya
  sta RgShotVXHi,x
  lda SavedJoypadBits
  and #Up_Dir | Down_Dir
  beq Direction
  sta RgTemp3
  lda SavedJoypadBits
  and #3
  beq Straight
  lda #$e0                      ; Diagonal multiplier .75.
  ldy #1
  lda RgBoomPower
  cmp #2
  bcc :+
    lda #$80
    ldy #2
    bne Diagonal
  :
  lda #$e0
Diagonal:
  sta RgShotVXLo,x
  tya
  sta RgShotVXHi,x
Straight:
  lda RgShotVXLo,x
  sta RgShotVYLo,x
  lda RgShotVXHi,x
  sta RgShotVYHi,x
  lda RgTemp3
  cmp #Up_Dir
  bne :+
    jsr NegateY
  :
  lda SavedJoypadBits
  and #3
  bne Direction
  lda #0
  sta RgShotVXLo,x
  sta RgShotVXHi,x
  lda Player_X_Position
  clc
  adc #8
  sta RgShotX,x
  lda Player_PageLoc
  adc #0
  sta RgShotPage,x
Direction:
  lda PlayerFacingDir
  cmp #1
  beq :+
    jsr NegateX
  :
  lda SavedJoypadBits
  and #Up_Dir | Down_Dir
  beq Start
  ldy #16
  cmp #Up_Dir
  beq Height
  ldy #26
  lda SavedJoypadBits
  and #3
  bne Height
  ldy #32
Height:
  tya
  clc
  adc Player_Y_Position
  sta RgShotY,x
Start:
  farcall EasyLinkBoomOrigin
  ldx RgSlot
  lda RgShotX,x
  sta RgBoomStartX
  lda RgShotPage,x
  sta RgBoomStartPage
  lda RgShotY,x
  sta RgBoomStartY
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
.endproc
.proc LinkBoomerangReturn
  lda RgBoomReturning
  jne Done
  inc RgBoomReturning
  lda #0
  sta RgBoomFriction
  ldx RgSlot
  jsr LinkBoomerangSpawn::NegateX
  jsr LinkBoomerangSpawn::NegateY
Done:
  rts
.endproc
.proc LinkBoomerangMotion
  ldx RgSlot
  lda RgBoomReturning
  jne Home
  ; Stage-edge contacts turn either color around.
  lda RgShotY,x
  cmp #36
  jcc Turn
  cmp #236
  jcs Turn
  lda RgShotX,x
  sec
  sbc ScreenLeft_X_Pos
  sta RgTemp
  lda RgShotPage,x
  sbc ScreenLeft_PageLoc
  jne Turn
  lda RgTemp
  cmp #4
  jcc Turn
  cmp #252
  jcs Turn
  lda RgBoomPower
  cmp #2
  jcs Done                      ; Blue continues until a stage edge/hit.
  lda RgShotX,x
  sec
  sbc RgBoomStartX
  sta RgBoomDx
  lda RgShotPage,x
  sbc RgBoomStartPage
  sta RgBoomDx+1
  lda RgShotY,x
  sec
  sbc RgBoomStartY
  sta RgBoomDy
  lda #0
  sbc #0
  sta RgBoomDy+1
  jsr AbsoluteDistances
  ldy #75                       ; fDist=150 Flash pixels.
  jsr WithinRadius
  bcc Brake
  lda RgBoomFriction
  jeq Done
Brake:
  lda #1
  sta RgBoomFriction
  jsr FrictionBoth
  ldx RgSlot
  lda RgShotVXHi,x
  sta RgBoomVelocity+1
  lda RgShotVXLo,x
  sta RgBoomVelocity
  ora RgBoomVelocity+1
  bne :+
    lda RgShotVYLo,x
    sta RgBoomVelocity
    lda RgShotVYHi,x
    sta RgBoomVelocity+1
  :
  jsr Magnitude
  lda RgBoomVelocity+1
  jne Done
  lda RgBoomVelocity
  cmp #$d5                      ; changeDir below 100/120 on either axis.
  jcs Done
Turn:
  jsr LinkBoomerangReturn
Home:
  ldx RgSlot
  lda Player_X_Position
  clc
  adc #8
  sta RgTemp
  lda Player_PageLoc
  adc #0
  sta RgTemp2
  sec
  lda RgTemp
  sbc RgShotX,x
  sta RgBoomDx
  lda RgTemp2
  sbc RgShotPage,x
  sta RgBoomDx+1
  lda Player_Y_Position
  clc
  adc #24
  sec
  sbc RgShotY,x
  sta RgBoomDy
  lda #0
  sbc #0
  sta RgBoomDy+1
  jsr AbsoluteDistances
  ldy #8
  jsr WithinRadius
  bcc HomeFar
  lda #0
  sta RgShotType,x
  rts
HomeFar:
  ldy #40                       ; extra acceleration within 80 Flash px.
  jsr WithinRadius
  lda #0
  rol
  sta RgBoomNear
  lda #0
  sta RgBoomAxis
Axis:
  ldx RgSlot
  lda RgBoomAxis
  bne Vertical
  lda RgShotVXLo,x
  sta RgBoomVelocity
  lda RgShotVXHi,x
  sta RgBoomVelocity+1
  lda RgBoomDx+1
  sta RgBoomSign
  lda RgBoomDx
  jmp Delta
Vertical:
  lda RgShotVYLo,x
  sta RgBoomVelocity
  lda RgShotVYHi,x
  sta RgBoomVelocity+1
  lda RgBoomDy+1
  sta RgBoomSign
  lda RgBoomDy
Delta:
  tay
  lda RgBoomPower
  cmp #2
  bcs Blue
  lda YellowSpringLo,y
  sta RgBoomDelta
  lda YellowSpringHi,y
  jmp DeltaHigh
Blue:
  lda BlueSpringLo,y
  sta RgBoomDelta
  lda BlueSpringHi,y
DeltaHigh:
  sta RgBoomDelta+1
  lda RgBoomSign
  bpl Add
  sec
  lda RgBoomVelocity
  sbc RgBoomDelta
  sta RgBoomVelocity
  lda RgBoomVelocity+1
  sbc RgBoomDelta+1
  sta RgBoomVelocity+1
  jmp Damping
Add:
  clc
  lda RgBoomVelocity
  adc RgBoomDelta
  sta RgBoomVelocity
  lda RgBoomVelocity+1
  adc RgBoomDelta+1
  sta RgBoomVelocity+1
Damping:
  cpy #16
  bcs Extra
  jsr FrictionVelocity
Extra:
  lda RgBoomNear
  beq Clamp
  lda RgBoomSign
  bpl ExtraPositive
  sec
  lda RgBoomVelocity
  sbc #89                       ; 2500/7200 in Q8.8.
  sta RgBoomVelocity
  lda RgBoomVelocity+1
  sbc #0
  sta RgBoomVelocity+1
  jmp Clamp
ExtraPositive:
  clc
  lda RgBoomVelocity
  adc #89
  sta RgBoomVelocity
  lda RgBoomVelocity+1
  adc #0
  sta RgBoomVelocity+1
Clamp:
  lda RgBoomVelocity+1
  pha
  jsr Magnitude
  lda #$80
  ldy #2
  ldx RgBoomPower
  cpx #2
  bcc :+
    lda #$55
    ldy #3
  :
  cpy RgBoomVelocity+1
  bcc Cap
  bne Sign
  cmp RgBoomVelocity
  bcs Sign
Cap:
  sta RgBoomVelocity
  sty RgBoomVelocity+1
Sign:
  pla
  bpl Store
  jsr NegateVelocity
Store:
  ldx RgSlot
  lda RgBoomAxis
  bne StoreVertical
  lda RgBoomVelocity
  sta RgShotVXLo,x
  lda RgBoomVelocity+1
  sta RgShotVXHi,x
  inc RgBoomAxis
  jmp Axis
StoreVertical:
  lda RgBoomVelocity
  sta RgShotVYLo,x
  lda RgBoomVelocity+1
  sta RgShotVYHi,x
Done:
  rts
AbsoluteDistances:
  lda RgBoomDx+1
  bpl :+
    sec
    lda #0
    sbc RgBoomDx
    sta RgBoomDx
    lda #$ff
    sta RgBoomDx+1
  :
  lda RgBoomDy+1
  bpl :+
    sec
    lda #0
    sbc RgBoomDy
    sta RgBoomDy
    lda #$ff
    sta RgBoomDy+1
  :
  rts
WithinRadius:
  sty RgTemp3
  lda RgBoomDx
  cmp RgTemp3
  bcs Outside
  lda RgBoomDy
  cmp RgTemp3
  bcs Outside
  ldx RgBoomDx
  ldy RgBoomDy
  clc
  lda SquareLo,x
  adc SquareLo,y
  sta RgTemp
  lda SquareHi,x
  adc SquareHi,y
  sta RgTemp2
  ldy RgTemp3
  lda RgTemp2
  cmp SquareHi,y
  bcc Inside
  bne Outside
  lda RgTemp
  cmp SquareLo,y
  bcc Inside
Outside:
  ldx RgSlot
  clc
  rts
Inside:
  ldx RgSlot
  sec
  rts
FrictionBoth:
  ldx RgSlot
  lda RgShotVXLo,x
  sta RgBoomVelocity
  lda RgShotVXHi,x
  sta RgBoomVelocity+1
  jsr FrictionVelocity
  ldx RgSlot
  lda RgBoomVelocity
  sta RgShotVXLo,x
  lda RgBoomVelocity+1
  sta RgShotVXHi,x
  lda RgShotVYLo,x
  sta RgBoomVelocity
  lda RgShotVYHi,x
  sta RgBoomVelocity+1
  jsr FrictionVelocity
  ldx RgSlot
  lda RgBoomVelocity
  sta RgShotVYLo,x
  lda RgBoomVelocity+1
  sta RgShotVYHi,x
  rts
Magnitude:
  lda RgBoomVelocity+1
  bpl MagnitudeDone
NegateVelocity:
  sec
  lda #0
  sbc RgBoomVelocity
  sta RgBoomVelocity
  lda #0
  sbc RgBoomVelocity+1
  sta RgBoomVelocity+1
MagnitudeDone:
  rts
FrictionVelocity:
  lda RgBoomVelocity+1
  pha
  jsr Magnitude
  lda #0
  sta MmMul
  lda RgBoomVelocity
  sta MmMul+1
  lda RgBoomVelocity+1
  sta MmMul+2
  farcall MmFrictionY
  lda MmMul+1
  sta RgBoomVelocity
  lda MmMul+2
  sta RgBoomVelocity+1
  pla
  bpl MagnitudeDone
  jmp NegateVelocity
YellowSpringLo:
 .repeat 256,I
  .byte <((I*256+72)/144)
 .endrepeat
YellowSpringHi:
 .repeat 256,I
  .byte >((I*256+72)/144)
 .endrepeat
BlueSpringLo:
 .repeat 256,I
  .byte <((I*256+30)/60)
 .endrepeat
BlueSpringHi:
 .repeat 256,I
  .byte >((I*256+30)/60)
 .endrepeat
SquareLo:
 .repeat 76,I
  .byte <(I*I)
 .endrepeat
SquareHi:
 .repeat 76,I
  .byte >(I*I)
 .endrepeat
.endproc
.popseg


