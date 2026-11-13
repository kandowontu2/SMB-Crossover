; Shatterhand USA PRG8 $844E-$8494 and PRG13 $A4C9-$A50D.
; The host admits an overlapping, vulnerable robot before calling Damage.
; DeathTick runs once per admitted actor update while Actor is $FF.
.setcpu "6502"
.segment "ROBOT_DEATH"

; A is the donor collision flag. HP retains its old byte on fatal damage.
SteveRobotDamage:
    cmp #0
    beq RobotNoDamage
    bmi RobotContactDone
    pha
    lda #0
    sta SteveBotAge
    lda SteveThrowSound
    bne RobotHitCueReady
    lda #$33
    sta SteveThrowSound
RobotHitCueReady:
    pla
    and #$0f
    cmp #8
    bcc RobotDamageReady
    lda #1
RobotDamageReady:
    sta $90
    sec
    lda SteveBotHP
    sbc $90
    beq RobotFatal
    bcs RobotSaveHP
RobotFatal:
    lda #0
    sta SteveBotAngle
    lda #$20
    sta SteveThrowTimer
    lda #$ff
    sta SteveBotActor
RobotContactDone:
    lda #$ff
    rts
RobotSaveHP:
    sta SteveBotHP
    rts
RobotNoDamage:
    lda #0
    rts

; Draw is an update receipt. A hidden blink keeps the underlying pose.
SteveRobotDeathTick:
    lda #0
    sta SteveDeathDraw
    lda #$f0
    ldx #$ff
    bit SteveDeathPolarity
    bpl RobotDeathDirectionReady
    lda #$10
    ldx #0
RobotDeathDirectionReady:
    sta $92
    stx $93
    lda SteveThrowTimer
    beq RobotDeathExplosion
    dec SteveThrowTimer
    bne RobotDeathDrift
    jsr SteveDeathClearShots
    lda #$0a
    sta SteveThrowSound
RobotDeathDrift:
    jsr RobotDeathAddY
    lda SteveBotClock
    and #2
    bne RobotDeathDone
RobotDeathDraw:
    inc SteveDeathDraw
RobotDeathDone:
    rts
RobotDeathExplosion:
    asl $92
    jsr RobotDeathAddY
    jsr SteveRobotDeathAnimate
    lda SteveLiftBotDelay
    bpl RobotDeathDraw
    jsr SteveRobotDeathReset
    sta SteveBotActor
    rts

RobotDeathAddY:
    clc
    lda SteveBotY
    adc $92
    sta SteveBotY
    lda SteveBotY+1
    adc $93
    sta SteveBotY+1
    rts

SteveRobotDeathAnimate:
    lda #$20
    cmp SteveLiftBotAnim
    beq RobotDeathAnimReady
    sta SteveLiftBotAnim
    lda #0
    sta SteveLiftBotDelay
    sta SteveLiftBotStep
RobotDeathAnimReady:
    lda SteveLiftBotDelay
    beq RobotDeathAnimRead
    ; Delay is 0..3 or the terminal $FF marker.
    bmi RobotDeathAnimDone
    dec SteveLiftBotDelay
    bne RobotDeathAnimDone
RobotDeathAnimRead:
    ; Original five rows: three updates each for DC/DE/E0/E2, then FF/E2.
    ; Valid animation steps are 0..4; reset retires the terminal step.
    ldx SteveLiftBotStep
    lda #3
    cpx #4
    bcc RobotDeathRowReady
    lda #$ff
    ldx #3
RobotDeathRowReady:
    sta SteveLiftBotDelay
    txa
    asl a
    ; X is 0..3, so ASL already clears carry.
    adc #$dc
    sta SteveBotPose
    lda #1
    sta SteveBotPose+1
    inc SteveLiftBotStep
RobotDeathAnimDone:
    rts

; Original PRG12 $936E. Actor, selector, age, angle and HP are outside it.
SteveRobotDeathReset:
    lda #0
    sta SteveThrowTimer
    sta SteveThrowSpeed
    sta SteveThrowAux
    sta SteveThrowAim
    sta SteveThrowAnimAux
    sta SteveLiftBotDelay
    sta SteveLiftBotStep
    sta SteveLiftBotAnim
    sta SteveBotPose
    sta SteveBotPose+1
    rts

