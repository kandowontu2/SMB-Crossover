.setcpu "6502"
.segment "DEATH_EARLY"
; Surviving receipt bits are cleared at the end of every robot update.
SteveDeathEarly:
    jsr SteveThrowGrant
    bit SteveBotActor
    bpl DeathContinueNormal
    jmp SteveDeathHead
DeathContinueNormal:
    jmp SteveDeathContinueTick

.segment "DEATH_HEAD"
SteveDeathHead:
    lda #$c0
    sta SteveThrowFrame
    lda SteveLaserActive
    bne DeathContinueLaser
    jmp SteveDeathAlpha
DeathContinueLaser:
    jmp SteveLaserTick

.segment "DEATH_ALPHA"
SteveDeathAlpha:
    jsr SteveFirstBotShotUpdate
    jsr SteveCompanionHit
    jmp SteveRobotDeathTick

.segment "DEATH_LASER_GATE"
SteveDeathLaserGate:
    bit SteveBotActor
    bmi DeathLaserFatal
    jmp SteveDeathLaserNormal
DeathLaserFatal:
    jmp SteveRobotDeathTick

.segment "DEATH_LASER_NORMAL"
SteveDeathLaserNormal:
    jsr SteveLaserBotPose
    jmp SteveDeathContinueLaser
