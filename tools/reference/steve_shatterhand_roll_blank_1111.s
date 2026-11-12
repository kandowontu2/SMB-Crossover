.setcpu "6502"
.segment "ROLL_PUBLISH"

RollPublish:
    lda #$f9
    sta $7da1
    lda #$f9
    sta $5116
    lda #0
    sta SsChrActive
    ldy RlPool
    lda RlPoolChrLo,y
    ldy #0
    jsr RollPublishPage
    ldy RlPool
    lda RlPoolChrLo,y
    clc
    adc #2
    ldy #6
    jsr RollPublishPage
    ldy RlPool
    lda RlPoolChrHi,y
    clc
    clv
    ldy #7
    jsr RollPublishPage
    ldx #1
    rts
RollPublishPage:
    php
    ldx #1
    cmp #$30
    beq RollPublishBlank
    cmp #$32
    bne RollPageReady
RollPublishBlank:
    ; CHR304 and CHR306 are byte-identical to the native blank CHR21.
    ldx #0
    lda #21
RollPageReady:
    plp
    sta $016a
    lda #<X5SetPhysicalChr
    sta $016c
    lda #>X5SetPhysicalChr
    sta $016d
    lda #$be
    jmp $015a
