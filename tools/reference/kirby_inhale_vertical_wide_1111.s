; Both existing users consume carry. Keep the visible enemy-page rule and
; compare full world Y against the same player+8 mouth center, +/-12 pixels.
.setcpu "6502"
.segment "TARGET"
KbInhaleTargetY:
 lda #8
 clc
 adc Player_Y_Position
 rts

.segment "VERTICAL"
KbInhaleVertical:
 lda Enemy_Y_HighPos,x
 cmp #1
 bne No
 lda Enemy_Y_Position,x
 sec
 sbc Player_Y_Position
 pha
 lda #1
 sbc Player_Y_HighPos
 beq Positive
 cmp #$ff
 pla
 bcc Done
 cmp #$fc
Done:
 rts
Positive:
 pla
 cmp #21
 bcs No
 sec
 rts
No:
 clc
 rts
