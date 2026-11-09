; A mixed record starts with its unaligned source parts, followed by a grid.
; The existing byte reader, pose scratch, grid and OAM ordering are retained.
.setcpu "6502"
.segment "MIXED_POSE"
.export ResetMixedPose, ReadMixedX, MixedPoseEnd

ResetMixedPose:
    jsr ResetPair
    bit GridFlag
    bmi ProjectionDone
    jsr Byte
    sta RawRemaining
    jsr Byte
    sta GridBaseX
    jsr Byte
    sta GridBaseY
    lda #0
    sta GridFlag
ProjectionDone:
    rts

ReadMixedX:
    bit GridFlag
    bpl RawX
    jmp ExistingGridX
RawX:
    jsr Byte
    pha
    dec RawRemaining
    lda RawRemaining
    and #$7f
    bne ReturnX
    lda RawRemaining
    lsr a
    ora #$80
    sta GridFlag
ReturnX:
    pla
    rts

RawRemaining:
    .byte 0
MixedPoseEnd:
