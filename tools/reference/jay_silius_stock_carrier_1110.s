.setcpu "6502"

.segment "COPY"
; The compact worker already read back the third CHR row at C2:D800.
; Its live art prefix ends at DA80. Copy only the binding and verify A3
; before resuming the decoder's saved-register return and cookie commit.
CopyBindings:
 ldx #0
FirstPage:
 lda $da80,x
 sta $b000,x
 cmp $b000,x
 bne Failed
 inx
 bne FirstPage
Tail:
 lda $db80,x
 sta $b100,x
 cmp $b100,x
 bne Failed
 inx
 cpx #TailBytes
 bne Tail
 sec
 jmp DecodeReturn
Failed:
 clc
 jmp DecodeReturn
