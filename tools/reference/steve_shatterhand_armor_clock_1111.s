.setcpu "6502"
.segment "ARMOR_CLOCK"

; Shatterhand bank 12 $9191–$91C0. A is the committed frame counter.
SteveArmorClock:
    and #$0f
    bne ClockDone
    lda SteveArmorTimer
    beq ClockDone
    cmp #2
    bcc Warn
    bne Decay
    jsr ResetPunchAnimation
    lda #$0f
    sta SteveUpgradeState
    lda #$24
    sta SteveUpgradeSound
Decay:
    lda SteveUpgradeState
    cmp #$11
    bcs ClockDone
    dec SteveArmorTimer
ClockDone:
    rts
Warn:
    lda #$57
    sta SteveArmorWarning
    rts

; Shatterhand bank 12 $9829–$983A, after the original support/visual calls.
SteveArmorEnd:
    jsr ResetPunchAnimation
    sta SteveArmorTimer
    sta SteveArmorEffectActor
    lda #$10
    sta SteveArmorExitCount
    inc SteveUpgradeState
    rts

ResetPunchAnimation:
    lda #0
    sta StevePunchSelector
    sta StevePunchDelay
    sta StevePunchPhase
    rts
