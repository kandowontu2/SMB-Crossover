.setcpu "6502"

.segment "TRANSFER"
; The common scatter worker has verified the carrier rows under forced blank.
; The movement decoder is about to overwrite A400. Copy the selected pages
; to B400 first, leaving the cookie pointer at $08/$09 intact.
CopyAlternate:
 lda #0
 sta $03
 sta $05
 lda #$a4
 sta $04
 lda #$b4
 sta $06
 ldy #0
 ldx #CopyPages
CopyByte:
 lda ($03),y
 sta ($05),y
 cmp ($05),y
 bne CopyFailed
 iny
 bne CopyByte
 inc $04
 inc $06
 dex
 bne CopyByte
.ifdef CopyTailBytes
CopyTail:
 lda ($03),y
 sta ($05),y
 cmp ($05),y
 bne CopyFailed
 iny
 cpy #CopyTailBytes
 bne CopyTail
.endif
 jmp $d000
CopyFailed:
 clc
 rts
