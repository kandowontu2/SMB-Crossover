; Private Prince native terrain primitive; no identity/router admission.
; Input: owned QueryX16, QueryY16 in screen-Y convention(32..239 valid).
; Output: C=solid and A=actual native metatile, else C=0/A=0. X/Y preserved.
; All scratch/SMC belongs to conditional code RAM3; host ZP is untouched.
.setcpu "6502"
.segment "HOST"
.export PpHostReadPoint,PpQueryX,PpQueryY,PpHostPointEnd
PpHostReadPoint:
 txa
 pha
 tya
 pha
 lda PpQueryY+1
 bne Empty
 lda PpQueryY
 cmp #32
 bcc Empty
 cmp #240
 bcs Empty
 lda PpQueryX
 lsr
 lsr
 lsr
 lsr
 sta Read+1
 lda PpQueryX+1
 and #1
 tay
 lda BlockBufferAddr,y
 clc
 adc Read+1
 sta Read+1
 lda #>Block_Buffer_1
 sta Read+2
 lda PpQueryY
 and #$f0
 sec
 sbc #32
 tay
Read:lda $ffff,y
 tax
 lda MTileAttribute,x
 and #1
 beq Empty
 txa
 sec
 bcs Finish
Empty:
 lda #0
 clc
Finish:
 sta Raw
 pla
 tay
 pla
 tax
 lda Raw
 rts
PpQueryX:.word 0
PpQueryY:.word 0
Raw:.byte 0
PpHostPointEnd:
