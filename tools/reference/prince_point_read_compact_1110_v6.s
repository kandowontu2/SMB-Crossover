; Lossless source-owned PointRead factoring. Query/Raw fields remain at their
; original addresses, and every original X/Y and A/C result is preserved.
.setcpu "6502"
.segment "POINT"
PpHostReadPoint:
 txa
 pha
 tya
 pha
 lda $b36c
 bne Empty
 lda $b36b
 sec
 sbc #32
 cmp #208
 bcs Empty
 and #$f0
 tay
 lda $b36a
 and #1
 tax
 lda $b369
 lsr a
 lsr a
 lsr a
 lsr a
 clc
 adc BlockBufferAddr,x
 sta ReadLow
Read:
 lda Block_Buffer_1,y
 tax
 lda MTileAttribute,x
 lsr a
 txa
 bcs Finish
Empty:
 lda #0
 clc
Finish:
 sta $b36d
 pla
 tay
 pla
 tax
 lda $b36d
 rts
