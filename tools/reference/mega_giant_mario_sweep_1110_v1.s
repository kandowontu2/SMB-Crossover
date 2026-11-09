.setcpu "6502"
.export GiantBGIngress, GiantSweepFront

.segment "GIANT_SWEEP"

; At the actual native PlayerBGCollision entry, restore the exact displaced
; LDA $0719 after doing the private source-side effects. The resident
; allocation and stable source scheduler are separate from this fixture.
.proc GiantBGIngress
    php
    pha
    txa
    pha
    tya
    pha
    lda SelectedCharacter
    bne Done
    lda MarioVariant
    cmp #9
    bne Done
    lda OperMode
    cmp #1
    bne Done
    lda GameEngineSubroutine
    cmp #8
    bne Done
    lda DisableCollisionDet
    bne Done
    lda PlayerFacingDir
    cmp #1
    bne Done
    jsr GiantSweepFront
Done:
    pla
    tay
    pla
    tax
    pla
    plp
    lda DisableCollisionDet
    rts
.endproc

; Original group 33..43 includes the first 1-1 standing crush contacts.
; Stop before the $ff sentinel. Native coin/flag/pipe handlers retain
; ownership. Crouching, backwards groups and landing remain separate.
.proc GiantSweepFront
    ldy #33
Probe:
    lda GiantProbeY,y
    clc
    php
    adc Player_Y_Position
    tax
    lda Player_Y_HighPos
    adc #0
    plp
    bpl ComparePage
    sbc #0
ComparePage:
    cmp #1
    bne Next
    cpx #$20
    bcc Next
    cpx #$f0
    bcs Next
    jsr GiantSide
    beq Next
    cmp #$23
    beq Next
    cmp #$c2
    beq Next
    cmp #$c3
    beq Next
    cmp #$c5
    beq Next
    cmp #$5f
    beq Next
    cmp #$60
    beq Next
    cmp #$6c
    beq Next
    cmp #$1f
    beq Next
    and #$c0
    asl
    rol
    rol
    tax
    lda R3
    cmp SolidLimits,x
    bcs Next

    tya
    pha
    lda GiantProbeX,y
    clc
    php
    adc Player_X_Position
    lda Player_PageLoc
    adc #0
    plp
    bpl WorldPageReady
    sbc #0
WorldPageReady:
    tax
    ldy R5
    lda R3
    jsr GiantCrushCell
    pla
    tay
Next:
    iny
    cpy #44
    bcc Probe
    rts
SolidLimits:
    .byte $24,$6d,$8a,$c6       ; exact original $df96..$df99
.endproc
