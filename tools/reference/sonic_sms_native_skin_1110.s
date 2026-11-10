; Startable prototype: original SMS pose pixels, existing native host motion.
; No SMS physics, rolling collision, rings or audio integration is claimed.
.setcpu "6502"
.export SonicNmiSlot0, SonicGraphics, SonicSkinSelect
.export SonicModeStore, SonicModeReady
.segment "SELECT"
.org $b6cb
SonicSkinSelect:
    lda $6002
    bne Done
    lda $730a
    cmp #10
    beq Sonic
    cmp #3
    bne Done
    lda $73e0
    cmp #$84
    beq SonicModeReady
Kamikaze:
    lda #$84
    bne Mode
Sonic:
    lda #$85
Mode:
    jmp SonicModeStore
.segment "COMPARE"
.org $b70e
SonicModeReady:
    lda #1
    sta $73ee
Done:
    rts
.segment "STORE"
.org $bb9c
SonicModeStore:
    sta $73e0
    inc $0146
    jmp SonicModeReady
.segment "NMI"
.org $a9c0
SonicNmiSlot0:
    php
    cmp #$84
    beq KamikazePage
    cmp #$85
    beq SonicPage
    and #3
    sta $5130
    lda $0147
    plp
    ora #0
    rts
KamikazePage:
    lda #2
    sta $5130
    lda $0147
    clc
    adc #$a8
    jmp Return
SonicPage:
    lda #0
    sta $5130
    lda $0147
    asl
    clc
    adc #$c0                 ; native16..19 -> physical224,226,228,230
Return:
    plp
    ora #0
    rts
SonicGraphics:
    jsr $b772                ; complete incumbent native/Bernie graphics
    php
    pha
    jsr SonicSkinSelect
    pla
    plp
    rts
