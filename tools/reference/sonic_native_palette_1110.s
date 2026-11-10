; Raw43 needs its own ordinary palette before the private runtime is loaded.
; Other owners use the original GetPlayerColors farcall with original A/P.
.setcpu "6502"
.segment "ENTRY"
 php
 pha
 lda $6002
 cmp #43
 beq SonicPalette
 pla
 plp
 jmp NativeColors
.segment "BODY"
NativeColors:
 sta $016a
 lda #$da
 sta $016c
 lda #$b0
 sta $016d
 lda #$c1
 jmp $015a
SonicPalette:
 pla
 plp
 ldx $04ae
 cpx #78                       ; Six bytes plus the terminator must fit.
 bcs Done
 ldy #0
NextColor:
 lda Colors,y
 sta $04af,x
 inx
 iny
 cpy #7
 bne NextColor
 dex
 stx $04ae
Done:
 rts
Colors:
 .byte $3f,$11,3,$16,$12,$30,0
