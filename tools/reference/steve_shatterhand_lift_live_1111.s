; The movement hook receives inputs after the native family update.
.setcpu "6502"
.segment "LIFT"

SteveLiftForget:
    lda #0
    sta SteveHostReady
    sta SteveLiftState
    clc
    rts

SteveLiftMovement:
    lda SteveUpgradeState
    ora JnHurt
    bne CancelLift
    lda SteveBotActor
    cmp #1
    beq WithLiftBot
    cmp #3
    bne CancelLift
WithLiftBot:
    lda SteveLiftState
    cmp #4
    bcs UpdateLift
    lda SteveMoveState
    cmp #3
    bne NormalMotion
    lda SteveMovePad
    bpl NormalMotion
    lda #$ff
    sta SteveLiftPlayerAnim
    jsr SteveLiftBegin
    jmp LiftProject

UpdateLift:
    lda #0
    ldx Player_State
    bne SaveSupport
    lda #1
SaveSupport:
    sta SteveLiftSupported
    lda #0
    sta SteveLiftCanRise
    lda SteveLiftState
    cmp #7
    bne DecideLift
    jsr LiftClearAbove
    rol SteveLiftCanRise
DecideLift:
    jsr SteveLiftDecision
    lda SteveLiftState
    cmp #4
    bcs LiftProject
    cmp #1
    bne CancelLift
    lda #1
    sta SteveMoveState
    bne ResetLiftVelocity
CancelLift:
    lda SteveLiftState
    cmp #4
    bcc ClearLift
ResetLiftVelocity:
    lda #0
    sta SteveMoveVY
ClearLift:
    lda #0
    sta SteveLiftState
NormalMotion:
    jmp SteveMotionProject

LiftProject:
    lda #$ff
    sta SteveMoveJumpHold
    lda SteveMovePad
    and #$fc
    sta SteveMovePad
    lda #0
    sta SteveMoveDX
    sta SteveMoveVX
    lda #3
    ldx SteveLiftState
    cpx #7
    bne LiftSaveMotion
    lda #1
LiftSaveMotion:
    sta SteveMoveState
    lda SteveLiftDelta
    sta SteveMoveDY
    sta SteveMoveVY
    rts

; The donor tests the robot against the top of the camera. Check the native
; head point at its next position as well, before touching the level buffer.
LiftClearAbove:
    lda SteveBotY+1
    beq LiftBlocked
    bmi LiftBlocked
    lda Player_Y_HighPos
    cmp #1
    bne LiftBlocked
    lda Player_Y_Position
    clc
    adc #3
    cmp #32
    bcc LiftClear
    and #$f0
    sec
    sbc #32
    sta $02
    lda Player_X_Position
    clc
    adc #8
    sta $00
    lda Player_PageLoc
    adc #0
    and #1
    tax
    lda $00
    lsr a
    lsr a
    lsr a
    lsr a
    clc
    adc LiftBufferLow,x
    sta $06
    lda #>Block_Buffer_1
    sta $07
    ldy $02
LiftReadCell:
    lda ($06),y
    tay
    lda MTileAttribute,y
    and #3                       ; Solid and climbable flags.
    cmp #1
    beq LiftBlocked
LiftClear:
    sec
    rts
LiftBlocked:
    clc
    rts
LiftBufferLow:
    .byte <Block_Buffer_1,<Block_Buffer_2

LiftAttachBob:
    lda SteveLiftBotDelay
    cmp #$ff
    bne LiftBobDone
    lda SteveLiftClock
    and #3
    asl a
    asl a
    asl a
    sta SteveLiftTemp
    lda SteveBotY
    sec
    sbc SteveLiftTemp
    sta SteveBotY
    bcs LiftBobDone
    dec SteveBotY+1
LiftBobDone:
    rts

.segment "COMPANION_HOST"

; Bank 13 $A62A takes one shortest-path angle step per update and anchors
; to the player's newly resolved center. The normal orbit keeps its bob.
SteveLiftOrbit:
    lda SteveLiftState
    cmp #4
    bcs LiftAngle
    jmp SteveCompanionOrbit
LiftAngle:
    lda SteveBotAngle
    sec
    sbc #$30
    and #$3f
    beq LiftAnchor
    cmp #$20
    bcs LiftAngleInc
    dec SteveBotAngle
    jmp LiftAnchor
LiftAngleInc:
    inc SteveBotAngle
LiftAnchor:
    ldx #1
LiftCopyCenter:
    lda SteveBotPlayerX,x
    sta SteveBotX,x
    lda SteveBotPlayerY,x
    sta SteveBotY,x
    dex
    bpl LiftCopyCenter
    lda SteveBotPlayerFacing
    sta SteveBotFacing
    lda SteveLiftState
    cmp #6
    beq TryLiftAttach
    lda SteveLiftRadius
    cmp #$50
    bcs LiftOrbitVector
TryLiftAttach:
    lda SteveLiftPlayerPoseHigh
    bne LiftOrbitVector
    lda SteveLiftPlayerPose
    sec
    sbc #$ac
    bcc LiftOrbitVector
    lsr a
    tay
    clc
    lda SteveBotY
    adc LiftAttachOffsets,y
    sta SteveBotY
    lda SteveBotY+1
    adc LiftAttachOffsets+1,y
    sta SteveBotY+1
    jmp LiftAttachBob
LiftOrbitVector:
    lda SteveLiftRadius
    jmp RadiusReady
LiftAttachOffsets:
    .byte $00,$ff,$80,$fe,$80,$fe,$30,$fe
