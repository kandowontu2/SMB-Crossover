.segment "THROW_POSE_LOOKUP"
SteveThrowFindPlayerPose:
    ldx #<ThrowRecoveryAE
    cmp #$ae
    beq ThrowRecoveryPointer
    ldx #<ThrowRecoveryB2
    cmp #$b2
    bne ThrowStockPlayerPose
ThrowRecoveryPointer:
    stx $00
    lda #>ThrowRecoveryAE
    sta $01
    ; The matching CMP already set carry.
    rts
ThrowStockPlayerPose:
    jmp FindPose

.segment "THROW_POSE_CHR"
SteveThrowPoseChr:
    lda #$53
    ldx $01
    cpx #>ThrowRecoveryAE
    bne ThrowPoseChrReady
    lda #$33
ThrowPoseChrReady:
    rts
