; Old Link's ahRect is exported on frames5/19/21 (tiers share geometry).
; HRect.getHitPoints writes parentx/y through AVM2 setters, truncating to
; Twips, then getBounds rounds transformed vertices. Native targets are
; integer boxes, so store ceil(min)/floor(max), preserving inclusive overlap.
; Six rows: normalR/L,DownR/L,UpR/L. Valid normal worldX/Y are nonnegative.
.pushseg
.segment "GUEST"
.proc EasyLinkRectPrepare
  phx
  phy
  lda RgThrust
  asl
  tax
  lda PlayerFacingDir
  cmp #1
  beq :+
    inx
  :
  lda MinX,x
  sta RgTemp
  lda MmXFraction+1
  cmp MinXHi,x
  bcc MinReady
  bne MinInc
  lda MmXFraction
  cmp MinXLo,x
  bcc MinReady
MinInc:
  inc RgTemp
MinReady:
  lda RgTemp
  ldy #0
  jsr StoreX
  lda MaxX,x
  sta RgTemp
  lda MmXFraction+1
  cmp MaxXHi,x
  bcc MaxReady
  bne MaxInc
  lda MmXFraction
  cmp MaxXLo,x
  bcc MaxReady
MaxInc:
  inc RgTemp
MaxReady:
  lda RgTemp
  ldy #1
  jsr StoreX
  lda Top,x
  sta MmBillEdgeY
  lda MmYFraction+1
  cmp TopHi,x
  bcc Bottom
  bne TopInc
  lda MmYFraction
  cmp TopLo,x
  bcc Bottom
TopInc:
  inc MmBillEdgeY
Bottom:
  lda Bot,x
  sta MmBillEdgeY+1
  cpx #2
  bcs Translate                  ; Up/Down have integer bottom, no carry.
  lda MmYFraction+1
  cmp #$80                       ; floor(.5+trunc40*f/40) steps atf=.5.
  bcc Translate
  inc MmBillEdgeY+1
Translate:
  lda MmBillEdgeY
  clc
  adc Player_Y_Position
  sta MmBillEdgeY
  lda MmBillEdgeY+1
  clc
  adc Player_Y_Position
  sta MmBillEdgeY+1
::EasyLinkRectPrepareFinish:
  ply
  plx
  rts
StoreX:
  sta RgTemp3
  clc
  adc Player_X_Position
  sta MmBillEdgeX,y
  lda #0
  bit RgTemp3
  bpl :+
    lda #$ff
  :
  adc Player_PageLoc
  sta MmBillEdgePage,y
  rts
MinX: .byte 15,<(-11),7,6,5,8
MaxX: .byte 27,1,10,9,8,11
MinXLo: .byte $00,$cd,$67,$67,$67,$67
MinXHi: .byte $40,$4c,$86,$86,$86,$86
MaxXLo: .byte $9a,$67,$00,$00,$00,$00
MaxXHi: .byte $b9,$c6,$80,$80,$80,$80
Top: .byte 23,23,32,32,5,5
Bot: .byte 28,28,42,42,15,15
TopLo: .byte $67,$67,$67,$67,$67,$67
TopHi: .byte $86,$86,$06,$06,$06,$06
.endproc
.popseg
