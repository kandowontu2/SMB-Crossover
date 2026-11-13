.setcpu "6502"
.segment "STEVE_ARMOR_COLD"

; The common copy already installed the exact CHR220 punch suffix. For
; CHR306 copy and verify only D800 through DA7F, leaving DA80–DBFF alone.
; All other late rows keep their original full 1024-byte transfer.
SteveLateCold:
    jsr $a7c0
    bcc SteveLateFailed
    lda #$33
    ldx #$ce
    jsr SteveLateRow
    bcc SteveLateFailed
    lda #$32
    ldx #$d8
    jsr SteveLateRow
    bcc SteveLateFailed
    jsr $da4d
    bcc SteveLateDone
.ifdef STEVE_COLD_SCATTER
    ldx #$d0
    jmp SteveArmorFinishCold
    .byte $ea,$ea,$ea,$ea,$ea,$ea,$ea,$ea,$ea,$ea,$ea
.else
    lda #$50
    ldx #$d0
    jsr SteveLateRow
    bcc SteveLateFailed
    lda #$52
    ldx #$d4
    jmp SteveLateRow
.endif

SteveLateRow:
    sta $05
    stx $06
    ldy #0
    sty $03
    clc
SteveLatePass:
    php
    lda $06
    sta $04
    jsr SteveLateMapRow
    ldx #4
    plp
SteveLateByte:
    lda $2007
    bcs SteveLateCompare
    sta ($03),y
    bcc SteveLateNext
SteveLateCompare:
    cmp ($03),y
    bne SteveLateFailed
SteveLateNext:
    iny
    bne SteveLatePartial
    inc $04
    dex
    bne SteveLateByte
    beq SteveLatePassDone
SteveLatePartial:
    ; Stop the CHR306 transfer at DA80. EOR preserves the pass bit in carry.
    tya
    eor #$80
    bne SteveLateByte
    lda $04
    eor #$da
    bne SteveLateByte
    ldy #0
SteveLatePassDone:
    bcs SteveLateDone
    sec
    bcs SteveLatePass
SteveLateDone:
    rts

SteveLateFailed:
    clc
    rts

SteveLateMapRow:
    lda #1
    sta $5130
    lda $05
    sta $5123
    sty $5130
    bit $2002
    lda #$0c
    sta $2006
    sty $2006
    lda $2007
    rts

.ifdef STEVE_COLD_SCATTER
.segment "STEVE_ARMOR_SCATTER"

; Move off CD00 before replacing the spent loader. The PPU row read starts
; at offset $280 of CHR306. Y=0 and PPU increment=1 are already qualified
; by the ordinary final late row. Keep R5/R6 ($08/$09) for cookie commit.
SteveArmorFinishCold:
    ldy #31
ArmorScatterInstallMap:
    lda $d1e0,y
    sta $c8c0,y
    dey
    bpl ArmorScatterInstallMap
    lda #$50
    jsr SteveLateRow
    bcc ArmorScatterReturn
    lda #$52
    ldx #$d4
    jsr SteveLateRow
    bcc ArmorScatterReturn
SteveArmorScatterTransfer:
    jsr SteveArmorMap
ArmorScatterCopy:
    lda $2007
    sta $cd00,y
    iny
    cpy #$88
    bne ArmorScatterCopy
    jsr SteveArmorMap
ArmorScatterRead:
    lda $2007
    cmp $cd00,y
    bne ArmorScatterFailed
    iny
    cpy #$88
    bne ArmorScatterRead
ArmorScatterReturn:
    rts
ArmorScatterFailed:
    clc
    rts

.segment "STEVE_ARMOR_SCATTER_MAP"
; C8C0 is the uncalled mirror of the cold bootstrap at B7C0. It is
; writable player-pose scratch after cold transfer and readback finish.
; The complete source row at D000 was already PPU-readback verified.
SteveArmorMap:
    lda #1
    sta $5130
    lda #$32
    sta $5123
    ldy #0
    sty $5130
    bit $2002
    lda #$0e
    sta $2006
    lda #$80
    sta $2006
    lda $2007
    rts

.endif
