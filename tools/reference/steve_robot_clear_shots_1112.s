.setcpu "6502"
.segment "DEATH_SHOTS"
; Original destruction clears projectile types at timer 1 -> 0. Preserve
; $92/$93: DeathTick has already prepared its signed movement delta there.
SteveDeathClearShots:
    lda #0
    sta SteveBotShotType
    sta SteveBotShotTimer
    sta SteveBotShotPower
    ldx #10
DeathClearLaserTypes:
    sta SteveLaserShotType,x
    dex
    bpl DeathClearLaserTypes
    ldx #7
DeathClearLaserDrawTags:
    sta SteveLaserDrawTags,x
    dex
    bpl DeathClearLaserDrawTags
    rts
