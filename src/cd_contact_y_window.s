; Full visible-page center minus crateY; never admit an8-bit wrap.
.pushseg
.segment "CD_LOGIC"
.proc CdContactYWindow
 lda Enemy_Y_HighPos,x
 cmp #1
 bne No
 lda Enemy_Y_Position,x
 clc
 adc #8
 bcs No
 sec
 sbc CdRectY
 bcs Positive
 cmp #$f0
 bcc No
 sec
 rts
Positive:
 cmp #16
 bcs No
 sec
 rts
No:
 clc
 rts
.endproc
.popseg
