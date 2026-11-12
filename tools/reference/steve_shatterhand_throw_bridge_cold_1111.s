.setcpu "6502"
.segment "THROW_BRIDGE_COLD"
; CHR307's verified spare tail is still staged at D100-D1FF here.
; The subsequent Laserbot row restores D000-D3FF after these copies.
SteveThrowBridgeCold:
    ldx #127
CopyBridgeHigh:
    lda $d100,x
    sta $c980,x
    cmp $c980,x
    bne BridgeFailed
    dex
    bpl CopyBridgeHigh
    ldx #95
CopyBridgeLow:
    lda $d180,x
    sta $c4a0,x
    cmp $c4a0,x
    bne BridgeFailed
    dex
    bpl CopyBridgeLow
    sec
    rts
BridgeFailed:
    clc
    rts
