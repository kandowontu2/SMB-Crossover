.setcpu "6502"
.segment "ARMOR_LIFECYCLE"

; Donor bank 12 $9191. The caller supplies the committed frame counter.
SteveArmorClock:
    and #$0f
    bne ClockDone
    lda SteveArmorTimer
    beq ClockDone
    cmp #2
    bcc ClockWarning
    bne ClockDecay
    jsr StevePunchReset
    lda #$0f
    sta SteveUpgradeState
    lda #$24
    sta SteveUpgradeSound
ClockDecay:
    lda SteveUpgradeState
    cmp #$11
    bcs ClockDone
    dec SteveArmorTimer
ClockDone:
    rts
ClockWarning:
    lda #$57
    sta SteveArmorWarning
    rts


; Donor $9829. The caller owns the native support probe and hurt timer.
SteveArmorExitBegin:
    jsr StevePunchReset
    sta SteveArmorTimer
    sta SteveArmorEffectActor
    lda #$10
    sta SteveArmorExitCount
    inc SteveUpgradeState
    rts

; Donor $983B. Caller supplies N from the support probe and maps animation
; and companion reset to their host-owned fields. A stale animation callback
; may clobber A/X/Y. This code does not keep arguments in those registers.
SteveArmorExitStep:
    bmi ExitStanding
    lda #6
    bne ExitAnimate
ExitStanding:
    lda #0
ExitAnimate:
    jsr SteveArmorExitAnimation
    lda SteveArmorWindup
    and #$7f
    cmp #$7c
    bcs ExitCheckAngle
    adc #4
    sta SteveArmorWindup
ExitCheckAngle:
    lda SteveRobotActor
    beq ExitCount
    clc
    lda SteveRobotAngle
    adc #$e8
    and #$3f
    cmp #$10
    bcs ExitDone
ExitCount:
    dec SteveArmorExitCount
    bne ExitDone
    lda #0
    sta SteveUpgradeState
    jmp SteveArmorResetRobot
ExitDone:
    rts


; Donor $A5E6/$A603. Use the existing companion vector table and place the
; actor against the player's anchor in the host projection caller.
SteveArmorEntryOrbit:
    lda SteveRobotAngle
    sec
    sbc #4
    sta SteveRobotAngle
    lda SteveArmorWindup
    and #$f0
    rts

SteveArmorExitOrbit:
    lda SteveArmorWindup
    and #$70
    pha
    eor #$70
    lsr a
    lsr a
    lsr a
    lsr a
    sta SteveArmorAngleStep
    lda SteveRobotAngle
    clc
    sbc SteveArmorAngleStep
    sta SteveRobotAngle
    pla
    rts

; Donor bank 12 $9FBE and bank 8 $8360. The accepted caller has already
; validated the armor timer and the original hurt gate. X is preserved.
SteveArmorDamage8:
    lda SteveArmorTimer
    sec
    sbc #8
    jmp ArmorDamageResult
SteveArmorDamage16:
    lda SteveArmorTimer
    sec
    sbc #$10
ArmorDamageResult:
    bcs ArmorDamageRound
    lda #2
    bcc ArmorDamageStore
ArmorDamageRound:
    ora #7
ArmorDamageStore:
    sta SteveArmorTimer
    rts
