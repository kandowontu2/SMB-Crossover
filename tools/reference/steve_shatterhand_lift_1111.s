.setcpu "6502"
.segment "LIFT"

; The caller admits the donor crouch-to-assist transition and owns terrain.
SteveLiftBegin:
    lda #4
    sta SteveLiftState
    lda #$80
    sta SteveLiftRadius
    lda #16
    sta SteveLiftWait
    lda #0
    sta SteveLiftDelta
    sta SteveLiftThrow
    ldx #4
ResetLiftBot:
    sta SteveLiftBotAnim,x
    dex
    bpl ResetLiftBot
    rts

; Player bank 12 $98DC, $9945, $99B5 and $9A08. The actor owns its
; angle and the host reports support and the upward terrain boundary.
SteveLiftDecision:
    lda #0
    sta SteveLiftDelta
    sta SteveLiftThrow
    ldx SteveLiftState
    cpx #7
    beq LiftRise
    lda SteveLiftSupported
    beq LiftFall
    cpx #4
    bne CheckLatch
    jmp LiftApproach
CheckLatch:
    cpx #5
    bne LiftGrip
    jmp LiftLatch

LiftGrip:
    jsr LiftMotorSound
    lda SteveLiftBot
    beq LiftCrouch
    cmp #$ff
    beq LiftCrouch
    lda #6
    jsr PlayLiftBot
    jsr LiftThrowPressed
    bcs LiftFall
    lda SteveLiftPad
    bpl LiftCrouch
    lda #2
    jsr PlayLiftPlayer
    lda SteveLiftPlayerDelay
    cmp #$ff
    bne LiftDone
    inc SteveLiftState
LiftDone:
    rts

LiftRise:
    jsr LiftMotorSound
    lda SteveLiftBot
    beq LiftFall
    cmp #$ff
    beq LiftFall
    lda #6
    jsr PlayLiftBot
    jsr LiftThrowPressed
    bcs LiftFall
    lda SteveLiftPad
    bpl LiftFall
    lda SteveLiftCanRise
    beq RisePose
    lda #$f0
    bit SteveLiftPolarity
    bpl RiseStep
    lda #$10
RiseStep:
    sta SteveLiftDelta
RisePose:
    lda #3
    jmp PlayLiftPlayer

LiftFall:
    lda #1
    sta SteveLiftState
    rts
LiftCrouch:
    lda #3
    sta SteveLiftState
    rts

LiftApproach:
    lda SteveLiftBot
    beq LiftCrouch
    cmp #$ff
    beq LiftCrouch
    lda #4
    jsr PlayLiftBot
    lda SteveLiftPad
    bpl LiftCrouch
    lda #$30
    bit SteveLiftPolarity
    bpl LiftTarget
    lda #$10
LiftTarget:
    sta SteveLiftTemp
    lda SteveLiftAngle
    and #$3f
    cmp SteveLiftTemp
    bne ApproachPose
    dec SteveLiftWait
    bne ApproachPose
    inc SteveLiftWait
    lda SteveLiftRadius
    cmp #$30
    bcc BeginLatch
    sbc #$10
    sta SteveLiftRadius
    lda #1
    jmp PlayLiftPlayer
BeginLatch:
    lda #$31
    sta SteveLiftSound
    inc SteveLiftState
    rts
ApproachPose:
    lda #0
    jmp PlayLiftPlayer

LiftLatch:
    lda SteveLiftBot
    beq LiftCrouch
    cmp #$ff
    beq LiftCrouch
    jsr LiftThrowPressed
    bcc LatchPose
    lda #$10
    sta SteveLiftRadius
    jmp LiftCrouch
LatchPose:
    lda #5
    jsr PlayLiftBot
    lda SteveLiftBotDelay
    cmp #$ff
    bne LatchPad
    lda SteveLiftClock
    and #2
    clc
    adc #$62
    sta SteveLiftBotPose
LatchPad:
    lda SteveLiftPad
    bmi LatchHeld
    jmp LiftCrouch
LatchHeld:
    and #4
    bne KeepLatch
    lda SteveLiftBotDelay
    cmp #$ff
    bne KeepLatch
    lda #$60
    sta SteveLiftRadius
    inc SteveLiftState
    rts
KeepLatch:
    lda #1
    jmp PlayLiftPlayer

LiftMotorSound:
    lda SteveLiftClock
    and #7
    bne NoMotorCue
    lda #$0b
    sta SteveLiftSound
NoMotorCue:
    rts

; The live actor owns the throw trajectory and hit response.
LiftThrowPressed:
    lda SteveLiftPressed
    asl a
    asl a
    bcc NoThrow
    lda #$0c
    sta SteveLiftSound
    lda #$60
    sta SteveLiftRadius
    lda SteveLiftState
    sta SteveLiftThrow
NoThrow:
    rts

; Source animation records are delay, pose low, pose high. Zero loops
; and FF holds the last record. The bot fields follow the five player
; fields so both clocks use the same worker.
PlayLiftPlayer:
    ldx #0
    beq PlayLift
PlayLiftBot:
    ldx #5
PlayLift:
    cmp SteveLiftPlayerAnim,x
    beq LiftAnimReady
    sta SteveLiftPlayerAnim,x
    lda #0
    sta SteveLiftPlayerStep,x
    sta SteveLiftPlayerDelay,x
LiftAnimReady:
    lda SteveLiftPlayerDelay,x
    beq LiftAnimRead
    cmp #$ff
    beq LiftAnimDone
    dec SteveLiftPlayerDelay,x
    bne LiftAnimDone
LiftAnimRead:
    ldy SteveLiftPlayerAnim,x
    lda SteveLiftPlayerStep,x
    asl a
    clc
    adc SteveLiftPlayerStep,x
    adc LiftSequenceOffsets,y
    tay
    lda LiftSequences,y
    bne LiftAnimStore
    sta SteveLiftPlayerStep,x
    beq LiftAnimRead
LiftAnimStore:
    sta SteveLiftPlayerDelay,x
    lda LiftSequences+1,y
    sta SteveLiftPlayerPose,x
    lda LiftSequences+2,y
    sta SteveLiftPlayerPose+1,x
    inc SteveLiftPlayerStep,x
LiftAnimDone:
    rts
