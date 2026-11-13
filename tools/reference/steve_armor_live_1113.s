.setcpu "6502"
.segment "STEVE_ARMOR_RUNTIME"

SteveArmorDispatch:
    cmp #1
    beq ArmorPose
    cmp #2
    beq ArmorDamage
    cmp #5
    beq ArmorSceneBind
ArmorMain:
    lda FrameCounter
    jsr SteveArmorClock
    lda #$7c
    ldy #$ab
    jsr ArmorCallRaw3
    lda SteveTokenCountdown
    cmp #$30
    bne ArmorGrantCleanupDone
    lda SteveTokenPattern
    bne ArmorGrantCleanupDone
    lda #$70
    ldy #$ad
    jsr ArmorCallRaw3
ArmorGrantCleanupDone:
    lda SteveUpgradeState
    cmp #$0f
    bne ArmorAfterExitBegin
    lda #$20
    sta ArmorHurtAge
    jsr SteveArmorExitBegin
    jmp ArmorHandled
ArmorAfterExitBegin:
    cmp #$10
    bne ArmorAfterExitStep
    lda #$20
    sta ArmorHurtAge
    lda #$80
    ldx Player_State
    beq ArmorExitSupported
    lda #0
ArmorExitSupported:
    ora #0
    jsr SteveArmorExitStep
    lda SteveUpgradeState
    beq ArmorHandled
    jsr ArmorFixedAnchor
    jsr SteveArmorExitOrbit
    jsr $c5a9
    jmp ArmorHandled
ArmorAfterExitStep:
    cmp #$0d
    bne ArmorActiveCheck
    lda #$20
    sta ArmorHurtAge
    lda SteveTokenCountdown
    beq ArmorTransformOrbit
    cmp #$21
    bcc ArmorHandled
    lda SteveUpgradeFacing
    bpl ArmorArrivalRight
    lda SteveRobotAngle
    clc
    adc #4
    bne ArmorArrivalAngle
ArmorArrivalRight:
    lda SteveRobotAngle
    sec
    sbc #4
ArmorArrivalAngle:
    sta SteveRobotAngle
    jsr ArmorFixedAnchor
    ldx #3
ArmorArrivalAnchor:
    lda $c90c,x
    sta $c908,x
    dex
    bpl ArmorArrivalAnchor
    jsr $c5f1
    lda #$80
    jsr $c5a9
    jmp ArmorHandled
ArmorTransformOrbit:
    jsr ArmorFixedAnchor
    jsr SteveArmorEntryOrbit
    jsr $c5a9
    jmp ArmorHandled
ArmorActiveCheck:
    lda SteveArmorTimer
    beq ArmorUnclaimed
    lda #0
    sta $c941
    lda ArmorHurtAge
    cmp #$ff
    beq ArmorHandled
    inc ArmorHurtAge
ArmorHandled:
    ldx #0
    lda SteveUpgradeState
    cmp #$0d
    beq ArmorTransitionVisible
    cmp #$10
    bne ArmorStoreLaserVisibility
ArmorTransitionVisible:
    lda SteveRobotActor
    and #$3f
    cmp #3
    bne ArmorStoreLaserVisibility
    inx
ArmorStoreLaserVisibility:
    stx $c941
    lda SteveArmorTimer
    bne ArmorMirrorHandled
    lda #1
ArmorMirrorHandled:
    sta $5c85
    lda #1
    sec
    rts
ArmorUnclaimed:
    lda ArmorHurtAge
    cmp #$ff
    beq ArmorOrdinaryProtection
    inc ArmorHurtAge
ArmorOrdinaryProtection:
    lda ArmorHurtAge
    cmp #$70
    lda #0
    bcs ArmorMirrorOrdinary
    lda #1
ArmorMirrorOrdinary:
    sta $5c85
    lda #0
    clc
    rts

ArmorSceneBind:
    lda #0
    sta $c033
    sec
    rts

ArmorFixedAnchor:
    ; Match the existing world Q4 anchor without the ordinary orbit bob.
    lda Player_X_Position
    clc
    adc #8
    sta $c90c
    lda Player_PageLoc
    adc #0
    sta $c90d
    lda Player_Y_Position
    clc
    adc #16
    sta $c90e
    lda Player_Y_HighPos
    adc #0
    sec
    sbc #1
    sta $c90f
    ldx #4
ArmorPackAnchor:
    asl $c90c
    rol $c90d
    asl $c90e
    rol $c90f
    dex
    bne ArmorPackAnchor
    lda $5c8e
    ora $c90c
    sta $c90c
    lda $5c8f
    ora $c90e
    sta $c90e
    rts

ArmorResetRobot:
    lda #$10
    sta SteveRobotArrival
    lda #$ff
    sta SteveRobotLife
    lda SteveRobotIndex
    and #$7f
    sta SteveRobotIndex
    lda #0
    ldx #8
ArmorClearAnimation:
    sta $c917,x
    dex
    bpl ArmorClearAnimation
    sta $c941
    lda #$6c
    ldy #$ac
    jsr ArmorCallRaw3
    lda #$70
    ldy #$ad
    jmp ArmorCallRaw3
ArmorCallRaw3:
    sta $016c
    sty $016d
    lda #3
    jmp $015a

ArmorDamage:
    lda SteveArmorTimer
    beq ArmorNoDamageClaim
    lda ArmorHurtAge
    cmp #$20
    bcc ArmorDamageProtected
    jsr SteveArmorDamage8
    lda SteveArmorTimer
    sta $5c85
    lda #0
    sta ArmorHurtAge
    lda #$33
    sta SteveUpgradeSound
ArmorDamageProtected:
    lda #1
    sec
    rts
ArmorNoDamageClaim:
    lda $5c85
    bne ArmorDamageProtected
    lda JnHurt
    sec
    rts

ArmorPose:
    lda $730b
    and #$60
    cmp #$40
    bne ArmorPoseUnclaimed
    lda SteveUpgradeState
    cmp #$0d
    beq ArmorTransformPose
    cmp #$10
    beq ArmorExitPose
    lda SteveArmorTimer
    beq ArmorPoseUnclaimed
    lda $5c80
    beq ArmorOrdinaryPose
    lda $5c83
    jmp ArmorFindPose
ArmorOrdinaryPose:
    lda #3
    ldx Player_State
    bne ArmorAnimatePose
    lda #6
    ldx $5c92
    cpx #3
    beq ArmorAnimatePose
    lda #0
    ldx $5c93
    beq ArmorAnimatePose
    lda #2
ArmorAnimatePose:
    jsr ArmorAnimate
ArmorExitPose:
    lda ArmorBodyPose
    jmp ArmorFindPose
ArmorTransformPose:
    lda #$dc
ArmorFindPose:
    ldx #18
ArmorFindLoop:
    cmp ArmorPoseIds,x
    beq ArmorFoundPose
    dex
    bpl ArmorFindLoop
ArmorPoseUnclaimed:
    clc
    rts
ArmorFoundPose:
    lda ArmorPageLow,x
    pha
    lda ArmorPageHigh,x
    pha
    lda ArmorRecordLow,x
    sta $03
    lda ArmorRecordHigh,x
    sta $04
    lda #8
    sta $c943
    lda #16
    sta $c944
    lda #0
    ldx PlayerFacingDir
    cpx #2
    bne ArmorMirrorReady
    lda #$40
ArmorMirrorReady:
    sta $c942
    lda #$c0
    sta $05
    sta SmPosePtr
    lda #$c8
    sta $06
    sta SmPosePtr+1
    jsr $cf6a
    lda #$e9
    sta ObjectMetasprite
    pla
    tax
    pla
    sec
    rts

ArmorAnimate:
    ldx #4
ArmorAnimationLookup:
    cmp ArmorSelectors,x
    beq ArmorAnimationFound
    dex
    bpl ArmorAnimationLookup
    rts
ArmorAnimationFound:
    cmp SteveUpgradeAnim
    beq ArmorDelay
    sta SteveUpgradeAnim
    lda #0
    sta StevePunchDelay
    sta StevePunchPhase
ArmorDelay:
    lda StevePunchDelay
    beq ArmorNextFrame
    dec StevePunchDelay
    bne ArmorAnimationDone
ArmorNextFrame:
    lda ArmorAnimationOffsets,x
    clc
    adc StevePunchPhase
    adc StevePunchPhase
    tay
    lda ArmorFrames,y
    bne ArmorFrameReady
    sta StevePunchPhase
    beq ArmorNextFrame
ArmorFrameReady:
    sta StevePunchDelay
    iny
    lda ArmorFrames,y
    sta ArmorBodyPose
    inc StevePunchPhase
ArmorAnimationDone:
    rts

ArmorSelectors: .byte 0,2,3,6,16
ArmorAnimationOffsets: .byte 0,3,16,19,24
ArmorFrames:
    .byte $40,$da,0
    .byte 7,$de,7,$e0,7,$e2,7,$e6,7,$e8,7,$e4,0
    .byte 8,$ea,0
    .byte 8,$ec,8,$ee,0
    .byte 8,$dc,0

.segment "STEVE_ARMOR_BRIDGE"
ArmorPoseEntry:
    pha
    lda GameEngineSubroutine
    cmp #8
    bne ArmorOriginalStockPose
.ifdef STEVE_ARMOR_IDLE_FAST
    lda SteveUpgradeState
    ora SteveArmorTimer
    beq ArmorOriginalPose
.endif
    lda #1
    jsr ArmorInvoke
    bcs ArmorPublishedPose
ArmorOriginalPose:
    lda $c977
    bne ArmorOriginalSpecialPose
    jmp $cedc
ArmorOriginalSpecialPose:
    jmp $cee7
ArmorOriginalStockPose:
    jmp $cf41
ArmorPublishedPose:
    jmp $cf24

ArmorMainGateway:
    lda #0
    jsr ArmorInvoke
    bcc ArmorGatewayDone
    ; CA00 tail-jumped through DEB1. Discard DEB4 and return to C236.
    pla
    pla
ArmorGatewayDone:
    rts
ArmorDamageGateway:
    lda #2
    jsr ArmorInvoke
    bcs ArmorDamageReady
    lda JnHurt
ArmorDamageReady:
    sec
    rts

.segment "STEVE_ARMOR_GATE"
ArmorInvoke:
    sta $016a
    lda #<ArmorVerifyRaw1
    sta $016c
    lda #>ArmorVerifyRaw1
    sta $016d
    lda #3
    jsr $015a
    bcc ArmorGateDeclined
    lda #1
    jmp $015a
ArmorVerifyRaw1:
    pha
    ldx #15
ArmorCheckRaw1:
    lda $bfe0,x
    cmp $dfe0,x
    bne ArmorRaw1Rejected
    dex
    bpl ArmorCheckRaw1
    lda CurrentBank
    cmp #1
    beq ArmorExecuteRaw1
    pla
    sec
    rts
ArmorExecuteRaw1:
    pla
    jmp $a000
ArmorRaw1Rejected:
    pla
ArmorGateDeclined:
    txa                         ; failed header index0..15 is an invalid marker
    sta $dfe0
    clc
    rts

.segment "STEVE_ARMOR_BRIDGE"
ArmorFirstBotActive:
    lda SteveUpgradeState
    cmp #$0d
    beq ArmorFirstBotActor
    cmp #$10
    beq ArmorFirstBotActor
    ora SteveArmorTimer
    bne ArmorFirstBotDone
ArmorFirstBotActor:
    lda SteveRobotActor
    cmp #1
ArmorFirstBotDone:
    rts

.segment "STEVE_ARMOR_RECOVERY"
ArmorRecoveryPage:
    lda #$53
    ldx #1
    ldy $04
    cpy #$cd
    bne ArmorRecoveryReady
    lda #10
    ldx #0
ArmorRecoveryReady:
    rts
