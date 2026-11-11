; Existing shell-only route. Accept the red shell's old-to-new horizontal
; path against the actor's current native box. Green retains point contact.
.setcpu "6502"
.segment "KIRBY_SHELL"
KbShellEnemyContact:
 lda Enemy_Y_HighPos,x
 cmp #1
 bne Denied
 lda Enemy_BoundBoxCtrl,x
 cmp #12
 bcc NativeBox
Denied:
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
 adc #15
 sta KbTemp
 lda BoundBoxCtrlData+2,y
 adc #8
 sta KbTemp2
 ldy KbSavedSlot
 lda KbShotKind,y
 lsr
 bcc XStart
 ; Spawn and turn both publish exactly $03 or $fd with zero fraction.
 lda KbTemp
 adc #2
 sta KbTemp
 lda KbShotVXHi,y
 bmi XStart
 lda KbTemp2
 adc #3
 sta KbTemp2
XStart:
 lda Enemy_X_Position,x
 sec
 sbc KbShotX,y
 sta KbTempX
 lda Enemy_PageLoc,x
 sbc KbShotPage,y
 pha
 lda KbTempX
 clc
 adc KbTemp2
 sta KbTempX
 pla
 adc #0
 bne No
 lda KbTempX
 cmp KbTemp
 bcs No
CheckY:
 ldy KbTempY
 lda BoundBoxCtrlData+3,y
 sec
 sbc BoundBoxCtrlData+1,y
 adc #15
 sta KbTemp
 lda BoundBoxCtrlData+3,y
 adc #7
 sta KbTemp2
 ldy KbSavedSlot
 lda Enemy_Y_Position,x
 sec
 sbc KbShotY,y
 bcc YBelow
 adc KbTemp2
 bcs No
CheckYWidth:
 cmp KbTemp
 bcs No
 sec
 rts
YBelow:
 sec
 adc KbTemp2
 bcs CheckYWidth
No:
 clc
 rts
