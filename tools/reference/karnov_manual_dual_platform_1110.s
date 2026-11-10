.setcpu "6502"
.export KrManualOptions,KrManualOptionsEnd,KrManualReset,KrManualResetEnd
KrHeld=$c01b
KrPressed=$c021
KrPending=$c866
KrTerrain=$c800
Facing=$053e
FarTarget=$016c
FarCall=$015a
ManualPlatform=$b378

.segment "OPTIONS"
KrManualOptions:
    php
    tya
    pha
    lda KrHeld
    and #$34
    cmp #$14
    beq Vertical
    cmp #$24
    beq Horizontal
Pending:
    ldy #0
    lda KrPending
    bmi Spawn
    iny
    asl a
    bmi Spawn
Done:
    pla
    tay
    plp
    rts
Vertical:
    ldy #0
    lda #$14
    bne Edge
Horizontal:
    ldy #1
    lda #$24
Edge:
    and KrPressed
    pha
    lda KrPressed
    and #$fb
    sta KrPressed
    pla
    beq Pending
Spawn:
    txa
    pha
    tya
    pha
    lda PendingBits,y
    ora KrPending
    sta KrPending
    tya
    beq VerticalSpawn
    ldx #$42
    ldy #24
    lda Facing
    cmp #2
    bne Call
    ldy #$d8
    bne Call
VerticalSpawn:
    ldx #$41
    ldy #$f8
Call:
    lda #<ManualPlatform
    sta FarTarget
    lda #>ManualPlatform
    sta FarTarget+1
    lda #$c0
    jsr FarCall
    pla
    tay
    txa
    bmi Restore
    lda ClearBits,y
    and KrPending
    sta KrPending
Restore:
    pla
    tax
    pla
    tay
    plp
    rts
PendingBits: .byte $80,$40
ClearBits: .byte $7f,$bf
KrManualOptionsEnd:

.segment "RESET"
KrManualReset:
    sta KrTerrain
    sta KrPending
    rts
KrManualResetEnd:
