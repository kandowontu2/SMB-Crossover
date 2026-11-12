; Shatterhand player throw actions $14/$15. The host uses the existing lift
; animation clock with the two original player records appended as indices 7/8.
.setcpu "6502"

ThrowAirAction = 7
ThrowGroundAction = 8

.segment "THROW_PLAYER_BEGIN"
; A is the accepted lift state (5, 6, or 7). The current DX was projected
; before $9A89 and survives; the ordinary motion finish owns drag and steering.
SteveThrowPlayerBegin:
    tax
    lda SteveMoveFacing
    sta SteveBotFacing
    txa
    jsr SteveThrowBegin
    lda SteveThrowSpeed
    eor #$80
    sta SteveMoveVX
    ldy #ThrowGroundAction
    lda #3
    cpx #5
    beq ThrowSaveState
    dey
    lda #SteveThrowAirVY
    sta SteveMoveVY
    lda #$80
    sta SteveMoveJumpHold
    lda #1
ThrowSaveState:
    sta SteveMoveState
    sty SteveThrowPlayerAction
    lda #0
    sta SteveLiftState
    sta SteveMoveDY
    ; The admitted lift is playing index 0–3. The shared clock resets its
    ; delay and step when it switches to either distinct throw action.
    tya
    jmp PlayLiftPlayer

.segment "THROW_PLAYER_TICK"
; C is set when this leaf projected motion. A zero action falls through to
; normal projection. A negative action retains the final pose for one draw.
SteveThrowPlayerStep:
    lda SteveThrowPlayerAction
    beq ThrowPlayerIdle
    bmi SteveThrowPlayerCancel
    ldx SteveMoveState
    cmp #ThrowGroundAction
    bne ThrowAirProject
    cpx #3
    bne SteveThrowPlayerCancel
    lda SteveMoveVX
    sta SteveMoveDX
    lda #0
    sta SteveMoveDY
    beq ThrowAnimate
ThrowAirProject:
    cpx #1
    bne SteveThrowPlayerCancel
    jsr SteveMotionProject
ThrowAnimate:
    lda SteveThrowPlayerAction
    jsr PlayLiftPlayer
    lda SteveLiftPlayerDelay
    cmp #$ff
    bne ThrowPlayerClaimed
    lda #$80
    bcs ThrowClearClock
ThrowPlayerClaimed:
    sec
    rts

SteveThrowPlayerCancel:
    lda #0
    clc
ThrowClearClock:
    sta SteveThrowPlayerAction
    lda #0
    sta SteveLiftPlayerDelay
    sta SteveLiftPlayerStep
    rts
ThrowPlayerIdle:
    clc
    rts
