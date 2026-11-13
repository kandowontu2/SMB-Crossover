.setcpu "6502"
.segment "ALIAS"
DkDuplicateTileAlias:
    cmp #46
    beq TileEight
    cmp #54
    beq TileEight
    cmp #48
    bne PairTile
    lda #40
    bne PairTile
TileEight:
    lda #8
PairTile:
    clc
    ora #1
    rts
DkDuplicateTileAliasEnd:

.segment "SERVICE_HEAD"
DkPrivateRetireOrBBox:
    lda $6002
    cmp #40
    bne OriginalBBox
    lda $0764
    ora $0761
    bne OriginalBBox
    lda $d6
    cmp #$ce
    bne OriginalBBox
    lda $10,x
    cmp #1
    bne OriginalBBox
    lda $17,x
    cmp #$25
    bne OriginalBBox
    lda $1f,x
    bne OriginalBBox
    lda $0646,x
    cmp #5
    bne OriginalBBox
    lda $0566,x
    bpl OriginalBBox
    jmp DkRetireGeometry
OriginalBBox:
    jmp $b7ca
DkPrivateRetireHeadEnd:

.segment "SERVICE_TAIL"
DkRetireGeometry:
    sec
    lda $071f
    sbc $76,x
    sta $03
    lda $071d
    sbc $5d,x
    bcc OriginalBBox
    bne Retire
    lda $03
    cmp #49
    bcc OriginalBBox
Retire:
    jmp $8d2f
DkPrivateRetireTailEnd:
