.setcpu "6502"
.segment "COMPANION"

; Bank 13 $A954 after the orbit. This variant has one active shot slot.
SteveFirstBotWeapon:
    lda SteveBotAnim
    beq TryAttack
    jmp ContinueAttack
TryAttack:
    lda SteveBotPressed
    and #$40
    beq IdlePose
    lda SteveBotShotType
    bne IdlePose
    lda #$95
    sta SteveBotShotType
    lda #$33
    sta SteveBotShotTimer
    lda #2
    sta SteveBotShotFlags
    lda #1
    sta SteveBotShotPower
    sta SteveBotAnim
    sta SteveBotAnimStep
    lda #3
    sta SteveBotAnimDelay
    lda #$bc
    sta SteveBotPose
    lda #2
    sta SteveBotPose+1
    lda #$10
    ldx #4
    bit SteveBotFacing
    bpl SpinReady
    lda #$30
    ldx #$fc
SpinReady:
    sta SteveBotShotAngle
    stx SteveBotShotSpin
    ldx SteveBotPlayerState
    lda #$60
    ldy #$80
    cpx #3
    bne MuzzleY
    lda #$80
    ldy #$60
MuzzleY:
    sta SteveBotVectorX
    tya
    clc
    adc SteveBotY
    sta SteveBotShotY
    lda SteveBotY+1
    adc #0
    sta SteveBotShotY+1
    lda #0
    sta SteveBotVectorX+1
    bit SteveBotFacing
    bpl MuzzleX
    jsr NegateX
MuzzleX:
    jmp ProjectShotX

IdlePose:
    lda SteveBotAnimDelay
    beq InstallIdle
    dec SteveBotAnimDelay
    bne WeaponDone
InstallIdle:
    lda #$7f
    sta SteveBotAnimDelay
    lda #1
    sta SteveBotAnimStep
    lda #$bc
    sta SteveBotPose
    lda #2
    sta SteveBotPose+1
    rts

ContinueAttack:
    dec SteveBotAnimDelay
    bne WeaponDone
    lda SteveBotAnimStep
    cmp #18
    bcs EndAttack
    ; The donor's eighteen three-update records repeat BC, C0, BE.
    ldx SteveBotPose
    lda #$c0
    cpx #$bc
    beq PoseReady
    lda #$be
    cpx #$c0
    beq PoseReady
    lda #$bc
PoseReady:
    sta SteveBotPose
    inc SteveBotAnimStep
    lda #3
    sta SteveBotAnimDelay
WeaponDone:
    rts
EndAttack:
    lda #0
    sta SteveBotAnim
    sta SteveBotAnimStep
    rts

; Bank 13 $B6ED. Run the existing slot before admitting a new attack.
SteveFirstBotShotUpdate:
    lda SteveBotShotType
    beq WeaponDone
    bmi LiveShot
    ; Original positive $15 dispatches through $B222 after enemy contact.
    lda #0
    sta SteveBotShotType
    sta SteveBotAnim
    sta SteveBotAnimDelay
    sta SteveBotAnimStep
    rts
LiveShot:
    lda SteveBotClock
    and #7
    bne SpinShot
    lda #$34
    sta SteveBotShotSound
SpinShot:
    clc
    lda SteveBotShotAngle
    adc SteveBotShotSpin
    sta SteveBotShotAngle
    dec SteveBotShotTimer
    beq EndShot
.ifdef STEVE_LIFT_LIVE
    lda #$90
.else
    lda #32
.endif
    sta SteveBotRadius
    lda SteveBotShotAngle
    jsr CompanionVector
    asl SteveBotVectorX
    rol SteveBotVectorX+1
    ; The original projectile uses the horizontal polar component for
    ; both axes. It flips only the horizontal component on a turn.
    clc
    lda SteveBotY
    adc SteveBotVectorX
    sta SteveBotShotY
    lda SteveBotY+1
    adc SteveBotVectorX+1
    sta SteveBotShotY+1
    lda SteveBotPlayerFacing
    eor SteveBotRoomPolarity
    bpl ProjectShotX
    jsr NegateX
ProjectShotX:
    clc
    lda SteveBotX
    adc SteveBotVectorX
    sta SteveBotShotX
    lda SteveBotX+1
    adc SteveBotVectorX+1
    sta SteveBotShotX+1
    rts
EndShot:
    lda #0
    sta SteveBotShotFlags
    sta SteveBotShotType
    rts
