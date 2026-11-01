; X native enemy; KbSavedSlot copied shell. The renderer draws a16x16
; shell centered at KbShotX/Y. Native box offsets use the enemy origin.
; Only admitted visible-page enemies and the12 native enemy box shapes
; are accepted. World X and Y differences retain their borrow/high byte.
; Uses existing Kirby contact temporaries only; X remains the actor slot.
.pushseg
.segment "KIRBY_ABILITIES"
.proc KbShellEnemyContact
  lda Enemy_Y_HighPos,x
  cmp #1
  beq Visible
  clc
  rts
Visible:
  lda Enemy_BoundBoxCtrl,x
  cmp #12
  bcc NativeBox
  clc
  rts
NativeBox:
  asl
  asl
  tay
  sty KbTempY
  lda BoundBoxCtrlData+2,y
  sec
  sbc BoundBoxCtrlData,y
  clc
  adc #16
  sta KbTemp
  lda BoundBoxCtrlData+2,y
  clc
  adc #8
  sta KbTemp2
  ldy KbSavedSlot
  lda Enemy_X_Position,x
  sec
  sbc KbShotX,y
  sta KbTempX
  lda Enemy_PageLoc,x
  sbc KbShotPage,y
  sta KbTempPage
  ; Inline the first axis so the actual source contact chain has no
  ; additional nested helper return frame.
  lda KbTempX
  clc
  adc KbTemp2
  sta KbTempX
  lda KbTempPage
  adc #0
  bne No
  lda KbTempX
  cmp KbTemp
  bcs No
  ldy KbTempY
  lda BoundBoxCtrlData+3,y
  sec
  sbc BoundBoxCtrlData+1,y
  clc
  adc #16
  sta KbTemp
  lda BoundBoxCtrlData+3,y
  clc
  adc #8
  sta KbTemp2
  ldy KbSavedSlot
  lda Enemy_Y_Position,x
  sec
  sbc KbShotY,y
  sta KbTempX
  lda #0
  sbc #0
  sta KbTempPage
Axis:
  lda KbTempX
  clc
  adc KbTemp2
  sta KbTempX
  lda KbTempPage
  adc #0
  bne No
  lda KbTempX
  cmp KbTemp
  bcs No
  sec
  rts
No:
  clc
  rts
.endproc
.popseg
