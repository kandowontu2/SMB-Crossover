.setcpu "6502"

.segment "STEVE_PUNCH"
.export StevePunchControl, StevePunchAnimation, StevePunchOffsets, StevePunchLives
.export StevePunchShapes, StevePunchSound

; A is the Shatterhand posture (0 standing, 1 air, 3 crouched).
; StevePressed uses the NES B bit $40. The caller maps posture and pauses.
; On return C is set only on hit birth, X indexes its geometry and lifetime.
StevePunchControl:
    tay
    lda SteveCombo
    clc
    adc #4
    bcc StoreComboAge
    lda #$fc
StoreComboAge:
    sta SteveCombo
    lda #0
    sta StevePunchSound
    lda StevePunchSelector
    bne ActivePunch
    bit StevePressed
    bvc Idle
    cpy #1
    beq BeginAirPunch
    ldx SteveCombo
    lda SteveCombo
    and #3
    cmp #2
    bcs BeginCombo
    cpx #$50
    bcc KeepComboCount
    lda #$ff
KeepComboCount:
    sta SteveCombo
    inc SteveCombo
    lda #1
    cpy #3
    bne BeginPunch
    lda #9
    bne BeginPunch
BeginCombo:
    lda #$4a
    sta SteveCombo
    lda #$0f
    cpy #3
    bne BeginPunch
    lda #$16
    bne BeginPunch
BeginAirPunch:
    lda #8
BeginPunch:
    ldx #$0c
    stx StevePunchSound
    bne StevePunchAnimation
ActivePunch:
    cpy #1
    bne StevePunchAnimation
    lda #8
    bne StevePunchAnimation
Idle:
    clc
    rts

; Bank 13 $B79A..$B849, with only the five ordinary attack selectors admitted.
; Input A is the requested selector. The emitted pose number is a donor asset ID.
StevePunchAnimation:
    ldx #4
FindSelector:
    cmp SteveSelectors,x
    beq SelectorFound
    dex
    bpl FindSelector
    clc
    rts
SelectorFound:
    cmp StevePunchSelector
    beq CountDelay
    sta StevePunchSelector
    lda #0
    sta StevePunchPhase
    sta StevePunchDelay
CountDelay:
    lda StevePunchDelay
    beq NextPhase
    dec StevePunchDelay
    bne Idle
NextPhase:
    lda SteveArmor
    beq NormalPose
    lda SteveArmorRows,x
    bne ReadPhase
NormalPose:
    lda SteveNormalRows,x
ReadPhase:
    clc
    adc StevePunchPhase
    adc StevePunchPhase
    tay
    lda StevePunchFrames,y
    beq LoopPhase
    sta StevePunchDelay
    iny
    lda StevePunchFrames,y
    sta StevePunchPose
    inc StevePunchPhase
    lda StevePunchDelay
    cmp #$ff
    beq FinishPunch
    lda StevePunchPhase
    cmp #2
    bne Idle
    lda SteveHitIndices,x
    tax
    sec
    rts
LoopPhase:
    sta StevePunchPhase
    beq NextPhase
FinishPunch:
    lda #0
    sta StevePunchSelector
    sta StevePunchPhase
    sta StevePunchDelay
    clc
    rts

SteveSelectors:
    .byte $01,$08,$09,$0f,$16
SteveHitIndices:
    .byte 0,0,1,2,3
SteveNormalRows:
    .byte 0,6,12,18,28
SteveArmorRows:
    .byte 38,46,52,60,60
; Duration and pose ID from $BCEE/$BD00/$BCF7/$BD09/$BD18, then the
; corresponding $BBC9 armored table. All ten rows use pose bank zero.
StevePunchFrames:
    .byte $02,$7a,$06,$7c,$ff,$7c
    .byte $02,$76,$06,$78,$ff,$78
    .byte $02,$86,$06,$88,$ff,$88
    .byte $07,$7e,$04,$80,$07,$82,$06,$84,$ff,$84
    .byte $07,$8a,$04,$8c,$07,$8e,$06,$90,$ff,$90
    .byte $0a,$c4,$08,$c6,$08,$c8,$ff,$c8
    .byte $04,$d0,$06,$d2,$ff,$d2
    .byte $0a,$ca,$08,$cc,$08,$ce,$ff,$ce
    .byte $40,$da,$00,$00
StevePunchLives:
    .byte 10,10,20,20
StevePunchShapes:
    .byte $0a,$0a,$0b,$0b
; Donor $B903..$B922. Each row has right and left signed Q4 x/y pairs.
StevePunchOffsets:
    .word $00f0,$ffc0,$ff10,$ffc0
    .word $00f0,$0008,$ff10,$0008
    .word $0120,$ffc8,$fee0,$ffc8
    .word $0120,$0008,$fee0,$0008
