.setcpu "6502"
.segment "DEATH_DRAW"
; Frame bit6 owns the body even on the terminal actor-zero update.
SteveDeathDrawMux:
    bit SteveThrowFrame
    bvs DeathBody
    jmp SteveDeathOrdinaryDraw
DeathBody:
    lda SteveDeathDraw
    beq DeathHidden
    lda SteveDeathPolarity
    and #$80
    sta PoseMirror
    lda SteveBotPose
    cmp #$dc
    bcc DeathRetainedBody
    sbc #$dc
    lsr a
    tax
    lda DeathRecordLow,x
    sta $03
    lda #>DeathRecords
    sta $04
    jmp DeathBuild
DeathRetainedBody:
    jsr FindPose
    bcc DeathHidden
    lda SteveBotFacing
    lsr a
    and #$40
    ora #3
    ora PoseMirror
    sta PoseMirror
DeathBuild:
    lda #0
    sta PoseAnchorX
    sta PoseAnchorY
    jmp SteveDeathBuildPose
DeathHidden:
    jmp LiftDrawProjectiles
