.setcpu "6502"
.export GiantMarioRoute, GiantSweep, GiantSweepProbe, GiantSweepEffect

.segment "GIANT_ROUTE"

; Physical PRG93:$AFE7 is reached only for SelectedCharacter=0 and
; already holds the adapter's saved A/P. Keep the native variant-2 test
; and fall through to its original branch for all other callers.
GiantMarioRoute:
    lda MarioVariant
    cmp #9
    bne Legacy
    lda OperMode
    cmp #1
    bne Native
    lda GameEngineSubroutine
    cmp #8
    bne Native
    lda DisableCollisionDet
    bne Native
    lda SwimmingFlag
    bne Native
    pla
    plp
    jsr GiantBodyBox
    jsr GiantSweep
    jmp PlayerBGCollision
Legacy:
    cmp #2
    jmp $afec
Native:
    jmp $afee

; Donor DD24..DD97 chooses an initial source Y and then skips one
; sentinel between the two probe groups. Standing/crouching locomotion
; is projected from the host; the source's prior-frame climbing state
; and presentation-specific transitions have separate ownership. Only Giant's destructive
; foreground effects belong here. The ordinary BG owner below still
; handles current-host floors, head response, pickups and transitions.
GiantSweep:
    lda CrouchingFlag
    bne Crouch
    ldy #31
    lda Player_X_Speed
    bpl Check
    ldy #25
    bne Check
Crouch:
    ldy #46
Check:
    lda GiantProbeY,y
    cmp #$ff
    bne ProbeHeight
    iny
    lda GiantProbeY,y
    cmp #$ff
    beq SweepDone
ProbeHeight:
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
GiantSweepProbe:
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
GiantSweepEffect:
    jsr GiantCrushCell
    pla
    tay
Next:
    iny
    bne Check
SweepDone:
    ldx #0
    rts
SolidLimits:
    .byte $24,$6d,$8a,$c6
