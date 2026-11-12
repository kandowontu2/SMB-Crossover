; The donor runs $B174 before $A98F. Segments use the previous orbit
; delta, then the bot moves and its emitter can allocate a new segment.

SteveLaserLifecycle:
    lda SteveUpgradeState
    bne LaserInactive
    lda SteveBotActor
    cmp #3
    bne LaserInactive
    lda SteveLaserActive
    bne LaserLifecycleDone
    lda #0
    sta SteveBotShotType
    sta SteveBotShotTimer
    sta SteveBotAnim
    sta SteveLaserCooldown
    sta SteveLaserCharge
    sta SteveLaserGroup
    sta SteveLaserDeltaX
    sta SteveLaserDeltaX+1
    sta SteveLaserDeltaY
    sta SteveLaserDeltaY+1
    ldx #10
LaserResetSlots:
    sta SteveLaserShotType,x
    dex
    bpl LaserResetSlots
    lda #8
    sta SteveLaserMeta
    lda #$f8
    sta SteveLaserMeta+3
    sta SteveLaserMeta+4
    sta SteveLaserMeta+7
    lda #0
    sta SteveLaserMeta+8
    inc SteveLaserActive
LaserLifecycleDone:
    rts
LaserInactive:
    lda #0
    sta SteveLaserActive
    rts

SteveLaserTick:
    lda ScreenLeft_X_Pos
    sta SteveLaserCameraX
    lda ScreenLeft_PageLoc
    sta SteveLaserCameraX+1
    ldx #4
LaserPackCamera:
    asl SteveLaserCameraX
    rol SteveLaserCameraX+1
    dex
    bne LaserPackCamera
    ldx #7
LaserUpdateSegments:
    lda #0
    sta SteveLaserDrawTags,x
    lda SteveLaserShotType,x
    beq LaserNextSegment
    jsr SteveLaserSegmentTick
    bcc LaserNextSegment
    lda SteveLaserDrawTile1
    and #$3f
    sta SteveLaserDrawTags,x
    lda SteveLaserDrawAttr1
    and #$c0
    ora SteveLaserDrawTags,x
    sta SteveLaserDrawTags,x
    lda SteveLaserShotType,x
    bpl LaserNextSegment
    jsr SteveLaserContact
LaserNextSegment:
    dex
    bpl LaserUpdateSegments

    jsr SteveLaserBotPose
    ldx #1
LaserSaveOrbit:
    lda SteveBotX,x
    sta SteveLaserDeltaX,x
    lda SteveBotY,x
    sta SteveLaserDeltaY,x
    dex
    bpl LaserSaveOrbit
.ifdef STEVE_LIFT_LIVE
    jsr SteveLiftOrbit
.else
    jsr SteveCompanionOrbit
.endif
    sec
    lda SteveBotX
    sbc SteveLaserDeltaX
    sta SteveLaserDeltaX
    lda SteveBotX+1
    sbc SteveLaserDeltaX+1
    sta SteveLaserDeltaX+1
    sec
    lda SteveBotY
    sbc SteveLaserDeltaY
    sta SteveLaserDeltaY
    lda SteveBotY+1
    sbc SteveLaserDeltaY+1
    sta SteveLaserDeltaY+1
    lda #0
    sta SteveBotShotSound
.ifdef STEVE_LIFT_LIVE
    lda SteveLiftState
    cmp #4
    bcs LaserCueDone
.endif
    jsr SteveLaserBotWeapon
    lda SteveBotShotSound
    beq LaserCueDone
    lda Square1SoundQueue
    ora #$20                    ; Crossover fire cue on the donor's $1a events.
    sta Square1SoundQueue
LaserCueDone:
    rts

SteveLaserContact:
    lda SteveLaserRelX
    sta $07
    lda SteveLaserRelX+1
    sta $08
    lda SteveLaserRelY
    sta $09
    lda SteveLaserRelY+1
    sta $0a
    ldy #4
LaserUnpackContact:
    lsr $08
    ror $07
    lsr $0a
    ror $09
    dey
    bne LaserUnpackContact
    inc $0a
    txa
    pha
    jsr FindCompanionTarget
    bcc LaserContactMissed
    ; The donor charges each target's low-nibble resistance against the
    ; segment. Crossover enemies use their native HP as resistance.
    lda JnEnemyHP,x
    and #$0f
    bne LaserContactCost
    lda #1
LaserContactCost:
    sta SteveLaserBirthKind
    jsr ApplyCompanionDamage
    pla
    tax
    lda SteveLaserShotPower,x
    sec
    sbc SteveLaserBirthKind
    beq LaserExhausted
    bcs LaserSavePower
LaserExhausted:
    lda SteveLaserShotType,x
    and #$7f
    sta SteveLaserShotType,x
    lda #0
    sta SteveLaserShotPacked,x
LaserSavePower:
    sta SteveLaserShotPower,x
    rts
LaserContactMissed:
    pla
    tax
    rts

SteveLaserDraw:
    ldx #0
    lda SteveBotPose
    cmp #$3e
    bne LaserBodyFacing
    ldx #2
LaserBodyFacing:
    bit SteveBotFacing
    bpl LaserBodyPointer
    inx
LaserBodyPointer:
    lda LaserBodyLo,x
    ldy LaserBodyHi,x
    jsr SetCompanionMeta
    lda SteveBotX
    sta $07
    lda SteveBotX+1
    sta $08
    lda SteveBotY
    sta $09
    lda SteveBotY+1
    sta $0a
    jsr ProjectToScreen
    jsr DrawCompanionMeta
    lda #7
    sta SteveLaserDrawSlot
LaserDrawSegments:
    ldx SteveLaserDrawSlot
    lda SteveLaserDrawTags,x
    beq LaserDrawNext
    pha
    and #$3f
    sec
    sbc #$17
    lsr a
    tay
    lda LaserCell1,y
    sta SteveLaserMeta+1
    lda LaserCell2,y
    sta SteveLaserMeta+5
    pla
    and #$c0
    ora #1
    pha
    eor LaserFlip1,y
    sta SteveLaserMeta+2
    pla
    eor LaserFlip2,y
    sta SteveLaserMeta+6
    lda SteveLaserShotXLo,x
    sta $07
    lda SteveLaserShotXHi,x
    sta $08
    lda SteveLaserShotYLo,x
    sta $09
    lda SteveLaserShotYHi,x
    sta $0a
    lda #<SteveLaserMeta
    ldy #>SteveLaserMeta
    jsr SetCompanionMeta
    jsr ProjectToScreen
    jsr DrawCompanionMeta
LaserDrawNext:
    dec SteveLaserDrawSlot
    bpl LaserDrawSegments
    rts

LaserBodyLo: .byte <LaserStandRight,<LaserStandLeft,<LaserCrouchRight,<LaserCrouchLeft
LaserBodyHi: .byte >LaserStandRight,>LaserStandLeft,>LaserCrouchRight,>LaserCrouchLeft
; Attribute bits 2 and 3 are unused by the PPU and reserved by SMB.
LaserStandRight:  .byte 8,$39,$01,$f8,$f8,$3b,$01,$f8,0
LaserStandLeft:   .byte 8,$39,$41,$f8,0,$3b,$41,$f8,$f8
LaserCrouchRight: .byte 8,$3d,$01,$f8,$f8,$3f,$01,$f8,0
LaserCrouchLeft:  .byte 8,$3d,$41,$f8,0,$3f,$41,$f8,$f8
LaserCell1: .byte $41,$7b,$7d,$7f,$7f
LaserCell2: .byte $41,$7d,$7b,$7f,$7f
LaserFlip1: .byte 0,0,0,0,$c0
LaserFlip2: .byte $c0,0,0,$c0,0
