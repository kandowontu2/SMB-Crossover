.setcpu "6502"
.export RelativePlayerPosition, RelativeFireballPosition, RelWOfs
.export RelativeEnemyPosition, RelativeBlockPosition, VariableObjOfsRelPos
.export GetXOffscreenBits, XOffscreenBitsData

R0 = $03
R4 = $07
R5 = $08
R6 = $09
R7 = $0a
ObjectOffset = $0d
ObjectX = $75
ObjectY = $bd
ObjectXPage = $5c
RelX = $0571
RelY = $057c
ScreenEdgeX = $071f
ScreenEdgePage = $071d
GetProperObjOffset = $8adf

.segment "RELATIVE"
RelativePlayerPosition:
  ldx #0
  ldy #0
  jmp RelativeCoordinates
RelativeFireballPosition:
  ldy #0
  jsr GetProperObjOffset
  ldy #2
RelWOfs:
  jmp RelativeCoordinates
  .res 3,$ea
RelativeEnemyPosition:
  stx R0
  inx
  ldy #1
  bne RelativeCoordinates
RelativeBlockPosition:
  lda #9
  ldy #4
  jsr VariableObjOfsRelPos
  inx
  inx
  lda #9
  iny
VariableObjOfsRelPos:
  stx R0
  clc
  adc R0
  tax
RelativeCoordinates:
  lda ObjectY,x
  sta RelY,y
  lda ObjectX,x
  sec
  sbc ScreenEdgeX
  sta RelX,y
  ldx ObjectOffset
  rts
  .res 4,$ea

.segment "OFFSCREEN"
GetXOffscreenBits:
  stx R4
  ldy #1
Edge:
  lda ScreenEdgeX,y
  sec
  sbc ObjectX,x
  sta R7
  lda ScreenEdgePage,y
  sbc ObjectXPage,x
  bmi Negative
  bne Far
  lda #56
  sta R6
  lda #8
  sta R5
  lda R7
  cmp #56
  bcs Far
  lsr a
  lsr a
  lsr a
  cpy #1
  bcs NearIndex
  adc #8
NearIndex:
  tax
  lda XOffscreenBitsData,x
  ldx R4
  cmp #0
  rts
Far:
  cpy #1
  bcc Outside
  dey
  bpl Edge
Negative:
  cpy #1
  bcs Outside
  lda #0
  sec
  dey
  rts
Outside:
  lda #$ff
  sec
  rts
XOffscreenBitsData:
  .byte $7f,$3f,$1f,$0f,$07,$03,$01,$00
  .byte $80,$c0,$e0,$f0,$f8,$fc,$fe,$ff
