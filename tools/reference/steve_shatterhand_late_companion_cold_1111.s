; Jay/Steve's original cold decoder owns C2:D000-D7FF until it returns.
; The common owner still has forced blank, the bank maps, and the cookie.
.setcpu "6502"
.segment "STEVE_LATE_COLD"

SteveLateCold:
    jsr $a7c0
    bcc SteveLateFailed
.ifdef STEVE_POSE_CARRIER
    ; Load the pose worker before the two later rows. The lower half stays
    ; in CE00-CFFF; D000-D1FF is replaced by the original Laserbot row.
    lda #<STEVE_POSE_CARRIER
    ldx #$ce
    jsr SteveLateRow
    bcc SteveLateFailed
.endif
    lda #$50                       ; CHR336, retired Roll slot 0 mirror
    ldx #$d0
    jsr SteveLateRow
    bcc SteveLateFailed
    lda #$52                       ; CHR338, retired Roll slot 6 mirror
    ldx #$d4
    jmp SteveLateRow

SteveLateRow:
    sta $05
    stx $06
    stx $04
    ldy #0
    sty $03
    jsr SteveLateMapRow
    ldx #4
SteveLateCopy:
    lda $2007
    sta ($03),y
    iny
    bne SteveLateCopy
    inc $04
    dex
    bne SteveLateCopy
    lda $06
    sta $04
    jsr SteveLateMapRow
    ldx #4
SteveLateVerify:
    lda $2007
    cmp ($03),y
    bne SteveLateFailed
    iny
    bne SteveLateVerify
    inc $04
    dex
    bne SteveLateVerify
    sec
    rts

SteveLateFailed:
    clc
    rts

SteveLateMapRow:
    lda #1
    sta $5130
    lda $05
    sta $5123
    lda #0
    sta $5130
    bit $2002
    lda #$0c
    sta $2006
    lda #0
    sta $2006
    lda $2007
    rts
