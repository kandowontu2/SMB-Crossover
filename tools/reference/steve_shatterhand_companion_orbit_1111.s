.setcpu "6502"
.segment "COMPANION"

; Shatterhand bank 13 $AD51. Coordinates are unsigned 12.4 positions.
; Input direction bits use the original (and SMB) Right/Left values 1/2.
SteveCompanionOrbit:
    jsr CompanionAnchor
    lda SteveBotPlayerFacing
    eor SteveBotRoomPolarity
    rol a
    rol a
    and #1
    tay
    lda SteveBotPad
    and #3
    beq RestAngle
    ror a
    ror a
    ror a
    sta SteveBotPlayerFacing
    lda SteveBotRoomPolarity
    bpl HeldNormal
    lda #$10
    bne HeldOffset
HeldNormal:
    lda #$30
HeldOffset:
    adc SteveBotAngle
    and #$3f
    cpy #0
    bne HeldLeft
    cmp #$1b
    beq OrbitOffset
    bcc RestAngle
    lda SteveBotActor
    bpl HeldDec
    asl a
    eor SteveBotFacing
    bmi OrbitOffset
HeldDec:
    dec SteveBotAngle
    jmp OrbitOffset
HeldLeft:
    cmp #$25
    beq OrbitOffset
    bcs RestAngle
    lda SteveBotActor
    bpl HeldInc
    asl a
    eor SteveBotFacing
    bpl OrbitOffset
HeldInc:
    inc SteveBotAngle
    jmp OrbitOffset

RestAngle:
    lda SteveBotClock
    lsr a
    bcc OrbitOffset
    lda SteveBotRoomPolarity
    bpl RestNormal
    lda #$10
    bne RestOffset
RestNormal:
    lda #$30
RestOffset:
    clc
    adc SteveBotAngle
    and #$3f
    cmp CompanionRestAngles,y
    bcc RestShort
    beq OrbitOffset
    tya
    bne RestShort
RestDec:
    lda SteveBotActor
    bpl StepRestDec
    asl a
    eor SteveBotFacing
    bpl OrbitOffset
StepRestDec:
    dec SteveBotAngle
    jmp OrbitOffset
RestShort:
    tya
    bne RestDec
    lda SteveBotActor
    bpl StepRestInc
    asl a
    eor SteveBotFacing
    bmi OrbitOffset
StepRestInc:
    inc SteveBotAngle

OrbitOffset:
    lda SteveBotAge
    cmp #6
    lda #16
    bcs RadiusReady
    lda #0
RadiusReady:
    sta SteveBotRadius
    lda SteveBotAngle
    jsr CompanionVector
    asl SteveBotVectorX
    rol SteveBotVectorX+1
    asl SteveBotVectorX
    rol SteveBotVectorX+1
    asl SteveBotVectorY
    rol SteveBotVectorY+1
    asl SteveBotVectorY
    rol SteveBotVectorY+1
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

; Bank 13 $AE31. Capture the old facing and anchor to the player's bob.
CompanionAnchor:
    lda SteveBotClock
    lsr a
    pha
    and #$0f
    tay
    pla
    and #$10
    beq AnchorBelow
    sec
    lda SteveBotPlayerY
    sbc CompanionBob,y
    sta SteveBotY
    lda SteveBotPlayerY+1
    sbc #0
    jmp AnchorHigh
AnchorBelow:
    clc
    lda SteveBotPlayerY
    adc CompanionBob,y
    sta SteveBotY
    lda SteveBotPlayerY+1
    adc #0
AnchorHigh:
    sta SteveBotY+1
    lda SteveBotPlayerFacing
    sta SteveBotFacing
    lda SteveBotPlayerX
    sta SteveBotX
    lda SteveBotPlayerX+1
    sta SteveBotX+1
    rts

; Bank 12 $900E, with only the two radii the ordinary companion uses.
; The original magnitude table is linked from the pinned cartridge.
CompanionVector:
    pha
    and #$0f
    clc
    adc SteveBotRadius
    tax
    pla
    pha
    and #$10
    bne SwapAxes
    lda CompanionPolar,x
    sta SteveBotVectorX
    jsr ComplementaryMagnitude
    sta SteveBotVectorY
    jmp SignVector
SwapAxes:
    lda CompanionPolar,x
    sta SteveBotVectorY
    jsr ComplementaryMagnitude
    sta SteveBotVectorX
SignVector:
    lda #0
    sta SteveBotVectorX+1
    sta SteveBotVectorY+1
    pla
    and #$30
    beq VectorDone
    cmp #$10
    beq NegateX
    cmp #$30
    beq NegateY
    jsr NegateX
NegateY:
    sec
    lda #0
    sbc SteveBotVectorY
    beq VectorDone
    sta SteveBotVectorY
    dec SteveBotVectorY+1
VectorDone:
    rts
NegateX:
    sec
    lda #0
    sbc SteveBotVectorX
    sta SteveBotVectorX
    lda #0
    sbc SteveBotVectorX+1
    sta SteveBotVectorX+1
    rts
ComplementaryMagnitude:
    txa
    and #$0f
    beq VectorDone
    dex
    txa
    eor #$0f
    tax
    lda CompanionPolar,x
    rts

CompanionRestAngles:
    .byte $25,$1b
