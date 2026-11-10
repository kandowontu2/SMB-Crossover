.setcpu "6502"

R0 = $03
R1 = $04
R2 = $05

.segment "DK_COLD"
DkColdEntry:
    lda #0
    sta R0
    sta R2
    lda #$a0
    sta R1
DkCopyRow:
    jsr DkMapRow
DkCopyByte:
    lda $2007
    sta (R0),y
    iny
    bne DkCopyByte
    inc R1
    dex
    bne DkCopyByte
    lda R1
    sec
    sbc #4
    sta R1
    jsr DkMapRow
DkVerifyByte:
    lda $2007
    cmp (R0),y
    bne DkColdNo
    iny
    bne DkVerifyByte
    inc R1
    dex
    bne DkVerifyByte
    inc R2
    lda R2
    cmp #8
    bne DkCopyRow
    rts
DkColdNo:
    clc
    rts
DkMapRow:
    ldx R2
    lda #3
    sta $5130
    lda DkCodePageLow,x
    sta $5123
    ldy #0
    sty $5130
    bit $2002
    lda #$0c
    sta $2006
    sty $2006
    lda $2007
    ldx #4
    rts
; The eight authenticated DK Jr. code carriers share CHR page high $03.
DkCodePageLow:
    .byte $31,$41,$4f,$58,$63,$71,$72,$73
DkColdEnd:
