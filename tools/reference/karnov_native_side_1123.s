.setcpu "6502"

FarNext = $0162
FarA = $016a
FarLo = $016c
FarHi = $016d
FarCall = $015a
FrameCounter = $0e
MapC = $80c2
CurrentBankC = $7da1
ValidatedFrame = $dfdf
Header = $dfe0
QueryY = $c81e
QueryAxis = $c81f
QueryIndex = $c820
PlayerY = $bd
CrouchingFlag = $0717
NativeProbeY = $e194
NativeSide = $958b

.segment "ADMIT"
Admit:
    php
    pha
    txa
    pha
    ; The public route leaves these operands for the outer fixed-bank caller.
    lda #$2a
    sta FarLo
    lda #$b4
    sta FarHi
    lda #$9d
    sta FarNext
    cpy #33
    bcc Reject
    cpy #37
    bcs Reject
    lda $01f9
    cmp #$52
    bne Reject
    lda $01fa
    cmp #$83
    bne Reject
    lda CurrentBankC
    pha
    lda #2
    jsr MapC
    lda ValidatedFrame
    beq RejectMapped
    cmp FrameCounter
    bne RejectMapped
    jsr CheckPrefix
    bcc RejectMapped
    lda #3
    jsr MapC
    jsr CheckPrefix
    bcc RejectMapped
    lda #2
    jsr MapC
    jmp Probe

RejectMapped:
    pla
    jsr MapC
Reject:
    pla
    tax
    pla
    sta FarA
    lda #$9d
    plp
    jmp FarCall

.segment "PREFIX"
CheckPrefix:
    ldx #3
CheckByte:
    lda Header,x
    cmp Expected,x
    bne InvalidPrefix
    dex
    bpl CheckByte
    sec
    rts
InvalidPrefix:
    clc
    rts
Expected:
    .byte $a7,$07,$01,$14

.segment "PROBE"
Probe:
    tya
    ldx CrouchingFlag
    beq HaveIndex
    clc
    adc #14                 ; native slide side offsets match Karnov's crouch
HaveIndex:
    tax
    lda PlayerY
    clc
    adc NativeProbeY,x
    sec
    sbc #32
    cmp #208
    bcc InBounds
    jmp RejectMapped
InBounds:
    sty QueryY
    tya
    sec
    sbc #30
    sta QueryIndex
    lda #1
    sta QueryAxis
    pla
    jsr MapC
    txa
    tay
    pla                     ; native probe replaces X and A
    pla
    plp
    jsr NativeSide
    php
    pha
    cpy #47
    bcc OriginalIndex
    tya
    sec
    sbc #14
    tay
OriginalIndex:
    pla
    plp
    rts
