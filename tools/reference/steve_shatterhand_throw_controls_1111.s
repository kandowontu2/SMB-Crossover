.setcpu "6502"
.segment "THROW_ENTRY"
SteveThrowMovementGate:
    lda SteveThrowPlayerAction
    beq OriginalMovement
    lda SteveUpgradeState
    ora JnHurt
    beq RecoveryMovement
    jsr SteveThrowPlayerCancel
    jmp OriginalMovement
RecoveryMovement:
    jsr SteveThrowPlayerStep
    bcc OriginalMovement
    rts
OriginalMovement:
    lda SteveUpgradeState
    jmp SteveLiftMovement+3

.segment "THROW_CONTROL"
SteveThrowDecisionGate:
    jsr SteveLiftDecision
    lda SteveLiftThrow
    beq OriginalDecision
    jsr SteveThrowPlayerBegin
    lda JnPressed
    and #$bf
    sta JnPressed
    rts
OriginalDecision:
    lda SteveLiftState
    jmp DecideLift+6

SteveThrowForget:
    jsr SteveThrowPlayerCancel
    lda #0
    sta SteveHostReady
    sta SteveLiftState
    clc
    rts
