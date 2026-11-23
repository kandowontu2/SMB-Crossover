.setcpu "6502"

TileRead = $a87b
TileWrite = $ad7e
SceneDestination = $c004

; The generic entries still resolve the pointer for other callers. These
; two emitters can reuse it because their loops never change SceneDestination.
.segment "COLUMNS"
ColumnEmit:
    jsr ColumnStart
    ldx $c008
    ldy #1
ColumnCell:
    jsr TileWrite
    clc
    adc #1
    iny
    pha
    jsr TileRead
    and #$3f
    jsr TileWrite
    pla
    iny
    iny
    iny
    dex
    bne ColumnCell
    rts

.segment "ROWS"
RowEmit:
    jsr SetTileOperands
    ldy #0
RowStart:
    ldx $c006
    lda $c001
    sta $c009
RowCell:
    lda $c009
    jsr TileWrite
    clc
    adc #8
    sta $c009
    iny
    iny
    iny
    lda $c000
    jsr TileWrite
    iny
    dex
    bne RowCell
    clc
    adc #8
    sta $c000
    dec $c007
    bne RowStart
    rts

ColumnStart:
    jsr SetTileOperands
    lda $c002
    rts

SetTileOperands:
    lda SceneDestination
    sta TileRead+1
    sta TileWrite+1
    lda SceneDestination+1
    cmp #8
    bcs SetHighByte
    ora #$c0
SetHighByte:
    sta TileRead+2
    sta TileWrite+2
    rts

; The seven consecutive source tiles have a fixed display mapping.
; One tile ID lies outside that run.
.segment "DRAW_DISPATCH"
    cmp #$5e
    beq IsolatedTile
    sbc #$f1
    cmp #7
    bcs SkipTile
    tay
    lda DrawTiles,y
    bne ClearTileCarry
IsolatedTile:
    lda #$74
ClearTileCarry:
    clc

.segment "DRAW_TILES"
DrawTiles:
    .byte $70,$72,$76,$78,$7a,$7c,$7e
