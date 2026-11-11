; Shatterhand's unarmored ground, crouch, landing and jump movement.
; Pad/edge have donor layout A=$80, B=$40, Down=$04, L=$02, R=$01.
; X/Y displacements and velocities are signed Q4. The caller owns terrain
; and applies the projected step before calling SteveMotionFinish with the
; carry set on downward landing. It clips the projected Y delta itself.
.setcpu "6502"
.segment "MOTION"

SteveMotionProject:
    lda #0
    sta SteveMoveDY
    lda SteveMoveVX
    sta SteveMoveDX
    ldx SteveMoveState
    beq Ground
    dex
    beq Air
    dex
    beq Landed

    ; $9C8A. Releasing Down returns to standing but cannot launch this tick.
    lda SteveMovePad
    and #4
    bne ProjectDone
    sta SteveMoveState
    rts

Ground:
    ; $9F09 and $A2C2. Down takes precedence over the jump edge.
    lda SteveMovePad
    and #4
    beq GroundJump
    lda #3
    sta SteveMoveState
    lda #0
    sta SteveMoveDX
    rts
GroundJump:
    lda SteveMovePressed
    bpl ProjectDone
    lda #1
    sta SteveMoveState
    lda #0
    sta SteveMoveJumpHold
    lda #$b2
    sta SteveMoveVY
    rts

Air:
    ; $A012/$A0C8. The first six sustained updates reinstate $FFB2
    ; before +4 gravity; release permanently exhausts the hold window.
    lda SteveMoveVY
    bpl Gravity
    lda SteveMovePad
    bpl EndHold
    lda SteveMovePressed
    bmi EndHold
    lda SteveMoveJumpHold
    cmp #6
    bcs Gravity
    inc SteveMoveJumpHold
    lda #$b6
    bne StoreY
EndHold:
    lda #$ff
    sta SteveMoveJumpHold
Gravity:
    lda SteveMoveVY
    clc
    adc #4
    bmi StoreY
    cmp #$61
    bcc StoreY
    lda #$60
StoreY:
    sta SteveMoveVY
    sta SteveMoveDY
ProjectDone:
    rts

Landed:
    ; $9EAE. Any current input ends the recovery, or it expires on the
    ; ninth following update. The fresh jump edge still belongs to recovery.
    lda SteveMovePad
    bne EndRecovery
    dec SteveMoveRecovery
    bne ProjectDone
EndRecovery:
    lda #0
    sta SteveMoveState
    rts

SteveMotionFinish:
    bcc Steer
    lda #0
    sta SteveMoveJumpHold
    sta SteveMoveVY
    lda SteveMovePad
    and #3
    beq Recover
    lda #0
    beq SetLanded
Recover:
    lda #9
    sta SteveMoveRecovery
    lda #2
SetLanded:
    sta SteveMoveState
Steer:
    ; $9B59/$9C6D. State 0/1 accepts steering. Left is the donor's
    ; selected direction when both D-pad contacts are closed.
    ldx SteveMoveState
    cpx #2
    bcs Brake
    lda SteveMovePad
    and #3
    beq Brake
    lsr a
    beq SteerRight
    lda #$80
SteerRight:
    tay
    eor SteveMoveFacing
    bpl Accelerate
    cpx #1
    beq Accelerate
    lda SteveMoveVX
    cmp #$80
    ror a
    sta SteveMoveVX
Accelerate:
    sty SteveMoveFacing
    tya
    bmi Left
    lda SteveMoveVX
    clc
    adc #2
    bmi StoreX
    cmp #22
    bcc StoreX
    lda #22
    bne StoreX
Left:
    lda SteveMoveVX
    sec
    sbc #2
    bpl StoreX
    cmp #$ea
    bcs StoreX
    lda #$ea
    bne StoreX

Brake:
    ; $9B97. The old velocity was already published before neutral drag.
    ldy #4
    cpx #1
    bne Sign
    ldy #1
Sign:
    sty SteveMoveDrag
    lda SteveMoveVX
    bmi BrakeLeft
    sec
    sbc SteveMoveDrag
    bcs StoreX
    bcc Stop
BrakeLeft:
    clc
    adc SteveMoveDrag
    bcc StoreX
Stop:
    lda #0
StoreX:
    sta SteveMoveVX
    rts
