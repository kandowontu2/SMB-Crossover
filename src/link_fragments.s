; LinkSwordProjectileExplosion.as: four mirrored pieces, +/-10 Flash px
; at spawn, each moving diagonally at 115 Flash px/s for 40 Flash px.
.pushseg
.segment "METASPRITE"
.proc LinkBeamFragments
  lda RgShotAge,x
  tay
  lda Distance,y
  sta RgTemp2
  lda #3
  sta RgTemp3
Piece:
  ldx RgSlot
  lda RgShotAge,x
  lsr
  and #3
  clc
  adc #8
  tay
  lda RgTemp3
  and #1
  beq :+
    tya
    clc
    adc #4
    tay
  :
  lda RgTemp3
  and #2
  bne Left
  lda RgLINKWeaponsRightLo,y
  sta R0
  lda RgLINKWeaponsRightHi,y
  jmp Pointer
Left:
  lda RgLINKWeaponsLeftLo,y
  sta R0
  lda RgLINKWeaponsLeftHi,y
Pointer:
  sta R1
  lda RgShotX,x
  sec
  sbc ScreenLeft_X_Pos
  sta R4
  lda RgShotPage,x
  sbc ScreenLeft_PageLoc
  sta R5
  lda RgTemp3
  and #2
  bne MinusX
  clc
  lda R4
  adc RgTemp2
  sta R4
  lda R5
  adc #0
  jmp StoreX
MinusX:
  sec
  lda R4
  sbc RgTemp2
  sta R4
  lda R5
  sbc #0
StoreX:
  sta R5
  lda RgTemp3
  and #1
  beq MinusY
  clc
  lda RgShotY,x
  adc RgTemp2
  sta R6
  lda RgShotYHigh,x
  adc #0
  jmp StoreY
MinusY:
  sec
  lda RgShotY,x
  sbc RgTemp2
  sta R6
  lda RgShotYHigh,x
  sbc #0
StoreY:
  sta R7
  lda #0
  sta R3
  jsr MetaspriteRenderLoop
  dec RgTemp3
  jpl Piece
  rts
Distance:
 .repeat 21,I
  .byte 5+(I*115)/120
 .endrepeat
.endproc
.popseg
