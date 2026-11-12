; Shatterhand USA bank 13 $A740–A835. The caller admits a surviving
; thrown actor and supplies the native enemy-contact receipt in its bit 7.
.setcpu "6502"
.segment "THROW"

; A is the donor lift state that accepted fresh B. Recoil remains with the
; player worker. The same update may enter SteveThrowUpdate for the robot.
SteveThrowBegin:
    cmp #5
    beq ThrowGroundBegin
    lda #6
    bne ThrowBeginTimer
ThrowGroundBegin:
    lda #3
ThrowBeginTimer:
    sta SteveThrowTimer
    lda SteveThrowSelector
    ora #$80
    sta SteveThrowSelector
    lda #$60
    bit SteveBotFacing
    bpl ThrowSaveSpeed
    lda #$a0
ThrowSaveSpeed:
    sta SteveThrowSpeed
    lda #$0c
    sta SteveThrowSound
    rts

SteveThrowUpdate:
    lda #4
    jsr PlayLiftBot               ; Original actor animation $14.
    lda SteveThrowTimer
    bmi ThrowAway
    bit SteveBotActor
    bmi ThrowContact
    lda SteveBotX
    cmp SteveThrowCameraX
    lda SteveBotX+1
    sbc SteveThrowCameraX+1
    bcc ThrowOffscreen
    cmp #$10
    bcc ThrowOutbound
ThrowOffscreen:
    lda #$80
    bne ThrowLeave
ThrowContact:
    lda #$0d
    sta SteveThrowSound
    lda #$ff
ThrowLeave:
    sta SteveThrowTimer
    lda SteveThrowSpeed
    ror a
    ror a
    eor #$20
    and #$20
    sta SteveThrowAim
    rts

ThrowOutbound:
    clc
    lda SteveBotX
    adc SteveThrowSpeed
    sta SteveBotX
    lda #0
    bit SteveThrowSpeed
    bpl ThrowAddOutboundHigh
    lda #$ff
ThrowAddOutboundHigh:
    adc SteveBotX+1
    sta SteveBotX+1
    rts

ThrowAway:
    cmp #$ff
    beq ThrowHoming
    lda SteveBotClock
    lsr a
    bcc ThrowHiddenEdge
    inc SteveThrowTimer
ThrowHiddenEdge:
    lda SteveThrowSpeed
    asl a
    lda SteveThrowCameraX+1
    bcs ThrowSaveEdge
    adc #$10
ThrowSaveEdge:
    sta SteveBotX+1
    lda SteveBotY+1
    cmp SteveThrowCameraY+1
    bcs ThrowHidePose
    lda SteveThrowCameraY+1
    sta SteveBotY+1
ThrowHidePose:
    lda #0
    sta SteveBotPose
    sta SteveBotPose+1
    sta SteveLiftBotStep
    sta SteveLiftBotDelay
    rts

ThrowHoming:
    lda SteveBotX+1
    cmp SteveBotPlayerX+1
    bne ThrowPursue
    sec
    lda SteveBotY+1
    sbc SteveBotPlayerY+1
    beq ThrowReattach
    cmp #1
    beq ThrowReattach
    cmp #$ff
    beq ThrowReattach
ThrowPursue:
    ; Fixed $C051 stores animation Y in $90, replacing target X low.
    ; Action $14 leaves Y=2 when its one row loads and Y=1 otherwise.
    lda #1
    ldx SteveLiftBotDelay
    cpx #$7f
    bne ThrowWrappedDirection
    lda #2
ThrowWrappedDirection:
    jsr ThrowDirectionWithLow
    bmi ThrowReattach
    sec
    sbc SteveThrowAim
    and #$3f
    cmp #$20
    lda #2
    bcs ThrowAddAim
    lda #$fe
ThrowAddAim:
    clc
    adc SteveThrowAim
    sta SteveThrowAim
    ldx #$50
    stx SteveBotRadius
    jsr CompanionVector
    clc
    lda SteveBotX
    adc SteveBotVectorX
    sta SteveBotX
    lda SteveBotX+1
    adc SteveBotVectorX+1
    sta SteveBotX+1
    clc
    lda SteveBotY
    adc SteveBotVectorY
    sta SteveBotY
    lda SteveBotY+1
    adc SteveBotVectorY+1
    sta SteveBotY+1
    rts

ThrowReattach:
    lda #$ff
    sta SteveBotAge
    lda SteveThrowSelector
    and #$7f
    sta SteveThrowSelector
    lda #0
    sta SteveThrowTimer
    sta SteveThrowSpeed
    sta SteveThrowAux
    sta SteveThrowAim
    sta SteveLiftBotDelay
    sta SteveLiftBotStep
    sta SteveThrowAnimAux
    sta SteveLiftBotAnim
    sta SteveBotPose
    sta SteveBotPose+1
    lda #$30
    sta SteveBotAngle
    rts

; PRG12 $8E5C. Normalize the two absolute deltas to indices 0–15.
; At least one index is 8–15. The original table reflects around its
; diagonal, allowing eight columns of sixteen nibble-packed values.
SteveThrowDirection:
    lda SteveBotPlayerX
ThrowDirectionWithLow:
    sta SteveBotVectorX
    ldx #0
    sec
    lda SteveBotX
    sbc SteveBotVectorX
    sta SteveBotVectorX
    lda SteveBotX+1
    sbc SteveBotPlayerX+1
    sta SteveBotVectorX+1
    bcs ThrowDirectionY
    ldx #2
    lda SteveBotVectorX+1
    bpl ThrowDirectionY
    sec
    lda #0
    sbc SteveBotVectorX
    sta SteveBotVectorX
    lda #0
    sbc SteveBotVectorX+1
    sta SteveBotVectorX+1
ThrowDirectionY:
    sec
    lda SteveBotY
    sbc SteveBotPlayerY
    sta SteveBotVectorY
    lda SteveBotY+1
    sbc SteveBotPlayerY+1
    sta SteveBotVectorY+1
    bcs ThrowDirectionReady
    inx
    lda SteveBotVectorY+1
    bpl ThrowDirectionReady
    sec
    lda #0
    sbc SteveBotVectorY
    sta SteveBotVectorY
    lda #0
    sbc SteveBotVectorY+1
    sta SteveBotVectorY+1
ThrowDirectionReady:
    stx SteveThrowQuadrant
    lda SteveBotVectorX
    ora SteveBotVectorX+1
    ora SteveBotVectorY
    ora SteveBotVectorY+1
    beq ThrowNoDirection
ThrowNormalize:
    asl SteveBotVectorX
    rol SteveBotVectorX+1
    asl SteveBotVectorY
    rol SteveBotVectorY+1
    lda SteveBotVectorX+1
    ora SteveBotVectorY+1
    cmp #$10
    bcc ThrowNormalize
    lsr SteveBotVectorX+1
    lsr SteveBotVectorY+1
    lda SteveBotVectorX+1
    ora SteveBotVectorY+1
    cmp #$10
    bcs ThrowNoDirection
    lda SteveThrowQuadrants,x
    sta SteveThrowQuadrant
    and #$10
    beq ThrowFindOctant
    jsr ThrowSwapAxes
ThrowFindOctant:
    ldx #0
    lda SteveBotVectorX+1
    cmp SteveBotVectorY+1
    bcs ThrowHaveOctant
    ldx #$10
    jsr ThrowSwapAxes
ThrowHaveOctant:
    stx SteveBotVectorX
    lda SteveBotVectorX+1
    sec
    sbc #8
    asl a
    asl a
    asl a
    sta SteveBotVectorY
    lda SteveBotVectorY+1
    lsr a
    ora SteveBotVectorY
    tax
    lda SteveThrowAngles,x
    bcc ThrowTakeNibble
    lsr a
    lsr a
    lsr a
    lsr a
ThrowTakeNibble:
    and #$0f
    ldx SteveBotVectorX
    beq ThrowAddQuadrant
    eor #$ff
    clc
    adc #17
ThrowAddQuadrant:
    clc
    adc SteveThrowQuadrant
    rts

ThrowNoDirection:
    lda #$ff
    rts

ThrowSwapAxes:
    lda SteveBotVectorX+1
    ldy SteveBotVectorY+1
    sty SteveBotVectorX+1
    sta SteveBotVectorY+1
    rts

SteveThrowQuadrants:
    .byte $00,$30,$10,$20
