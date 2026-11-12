; Find a native hostile actor at ThrowPoint. No damage or cooldown filtering:
; the caller must issue the return receipt before testing JnEnemyHurt.
.setcpu "6502"
.segment "THROW_TARGET"
SteveThrowFindTarget:
    ldx #5
ThrowTargetNext:
    lda Enemy_Flag,x
    beq ThrowTargetSkip
    bmi ThrowTargetSkip
    lda Enemy_ID,x
    cmp #$0c
    beq ThrowTargetSkip
    cmp #$15
    bcs ThrowTargetSkip
    lda Enemy_State,x
    and #$20
    bne ThrowTargetSkip
    lda Enemy_Y_HighPos,x
    cmp #1
    bne ThrowTargetSkip
    lda Enemy_BoundBoxCtrl,x
    cmp #3
    bcc ThrowTargetSkip
    cmp #12
    bcs ThrowTargetSkip
    jsr SteveThrowEnemyOverlap
    bcs ThrowTargetFound
ThrowTargetSkip:
    dex
    bpl ThrowTargetNext
    clc
ThrowTargetFound:
    rts
