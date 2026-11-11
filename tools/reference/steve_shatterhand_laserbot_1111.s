; Shatterhand USA Laserbot, AAB. Bank 13 $A98F updates the orbit before
; its emitter at $A9D8. The caller supplies that orbit and its Q4 delta.
.setcpu "6502"
.segment "LASERBOT"

SteveLaserBotPose:
    lda #$3c
    ldx SteveBotPlayerState
    cpx #3
    bne LaserPoseReady
    lda #$3e
LaserPoseReady:
    sta SteveBotPose
    lda #1
    sta SteveBotPose+1
    rts

SteveLaserBotWeapon:
    lda SteveLaserCooldown
    beq LaserReady
    dec SteveLaserCooldown
    rts
LaserReady:
    inc SteveLaserGroup
    bne CheckLaserCharge
    dec SteveLaserGroup
    ldx #7
LaserGroupOccupied:
    lda SteveLaserShotType,x
    bne LaserDone
    dex
    bpl LaserGroupOccupied
CheckLaserCharge:
    lda SteveLaserCharge
    bne LaserCharging
    lda SteveBotPad
    and #$40
    beq LaserMuzzleFlash
    lda #$10
    sta SteveLaserCharge
LaserDone:
    rts
LaserMuzzleFlash:
    lda SteveBotClock
    lsr a
    bcc LaserDone
    lda #3
    jmp LaserBirth

LaserCharging:
    dec SteveLaserCharge
    bne LaserCue
    lda #$40
    sta SteveLaserCooldown
LaserCue:
    lda SteveBotClock
    and #3
    bne LaserClockParity
    lda #$1a
    sta SteveBotShotSound
LaserClockParity:
    lda SteveBotClock
    lsr a
    bcs LaserKeepGroup
    lda #0
    jsr LaserBirth
    bcs LaserKeepGroup
    lda #$ff
    bne LaserSaveGroup
LaserKeepGroup:
    lda #$60
LaserSaveGroup:
    sta SteveLaserGroup
    rts

; $AEC9 searches 10..0. Ordinary $B174 advances only slots 7..0.
; Positive type $03 is the muzzle effect. Type $83/$88 is a live segment.
LaserBirth:
    sta SteveLaserBirthKind
    ldy #10
FindLaserSlot:
    lda SteveLaserShotType,y
    beq FoundLaserSlot
    dey
    bpl FindLaserSlot
    clc
    rts
FoundLaserSlot:
    ldx #0
    lda SteveBotPlayerState
    cmp #3
    bne CheckLaserPolarity
    inx
CheckLaserPolarity:
    bit SteveBotRoomPolarity
    bpl LaserMuzzleX
    inx
    inx
LaserMuzzleX:
    bit SteveBotFacing
    bmi LeftLaserMuzzle
    lda SteveBotX
    clc
    adc LaserMuzzleXLo,x
    sta SteveLaserShotXLo,y
    lda SteveBotX+1
    adc #0
    jmp StoreLaserX
LeftLaserMuzzle:
    lda SteveBotX
    sec
    sbc LaserMuzzleXLo,x
    sta SteveLaserShotXLo,y
    lda SteveBotX+1
    sbc #0
StoreLaserX:
    sta SteveLaserShotXHi,y
    lda SteveBotY
    clc
    adc LaserMuzzleYLo,x
    sta SteveLaserShotYLo,y
    lda SteveBotY+1
    adc LaserMuzzleYHi,x
    sta SteveLaserShotYHi,y
    lda SteveLaserBirthKind
    beq LiveLaserBirth
    sta SteveLaserShotType,y
    lda LaserDirection,x
    bne SetLaserVelocity
LiveLaserBirth:
    lda LaserTypes,x
    sta SteveLaserShotType,y
    lda LaserDirection,x
    bit SteveBotFacing
    bpl SetLaserVelocity
    eor #$f0
    clc
    adc #$10
SetLaserVelocity:
    sta SteveLaserShotPacked,y
    lda #2
    sta SteveLaserShotFlags,y
    lda #$7f
    sta SteveLaserShotPower,y
    sec
    rts

LaserTypes: .byte $88,$83,$88,$83
LaserDirection: .byte $74,$77,$7c,$78
LaserMuzzleXLo: .byte $80,$50,$80,$50
LaserMuzzleYLo: .byte $80,$90,$80,$70
LaserMuzzleYHi: .byte 0,0,$ff,$ff

; Bank 13 $B438 and positive $03/$08 cleanup. X selects one of slots 0..7.
; C returns a drawable segment with screen Q4 and two original tile cells.
SteveLaserSegmentTick:
    lda SteveLaserShotType,x
    cmp #$83
    beq MoveLaserSegment
    cmp #$88
    beq MoveLaserSegment
    cmp #8
    beq RetireLaserSegment
    cmp #3
    beq IdleLaserSpark
    clc
    rts
RetireLaserSegment:
    lda #0
    sta SteveLaserShotType,x
    clc
    rts
IdleLaserSpark:
    lda #0
    sta SteveLaserShotType,x
    jmp ProjectLaserSpark

MoveLaserSegment:
    lda SteveLaserShotXLo,x
    clc
    adc SteveLaserDeltaX
    sta SteveLaserShotXLo,x
    lda SteveLaserShotXHi,x
    adc SteveLaserDeltaX+1
    sta SteveLaserShotXHi,x
    lda SteveLaserShotYLo,x
    clc
    adc SteveLaserDeltaY
    sta SteveLaserShotYLo,x
    lda SteveLaserShotYHi,x
    adc SteveLaserDeltaY+1
    sta SteveLaserShotYHi,x
    dec SteveLaserShotFlags,x
    bne ProjectLaserSpark
    inc SteveLaserShotFlags,x
    ldy #0
    lda SteveLaserShotPacked,x
    and #$f0
    bpl LaserXVelocity
    dey
LaserXVelocity:
    clc
    adc SteveLaserShotXLo,x
    sta SteveLaserShotXLo,x
    tya
    adc SteveLaserShotXHi,x
    sta SteveLaserShotXHi,x
    ldy #0
    lda SteveLaserShotPacked,x
    asl a
    asl a
    asl a
    asl a
    bpl LaserYVelocity
    dey
LaserYVelocity:
    clc
    adc SteveLaserShotYLo,x
    sta SteveLaserShotYLo,x
    tya
    adc SteveLaserShotYHi,x
    sta SteveLaserShotYHi,x
    jsr LaserViewport
    bcc LaserSegmentDone
    jmp LaserBeamCells

ProjectLaserSpark:
    jsr LaserViewport
    bcc LaserSegmentDone
    lda #$57
    sta SteveLaserDrawTile1
    sta SteveLaserDrawTile2
    lda #1
    sta SteveLaserDrawAttr1
    lda #$c1
    sta SteveLaserDrawAttr2
    sec
LaserSegmentDone:
    rts

LaserViewport:
    lda SteveLaserShotXLo,x
    sec
    sbc SteveLaserCameraX
    sta SteveLaserRelX
    lda SteveLaserShotXHi,x
    sbc SteveLaserCameraX+1
    cmp #$10
    bcs LaserViewportOffscreen
    sta SteveLaserRelX+1
    lda SteveLaserShotYLo,x
    sec
    sbc SteveLaserCameraY
    sta SteveLaserRelY
    lda SteveLaserShotYHi,x
    sbc SteveLaserCameraY+1
    cmp #$10
    bcs LaserViewportOffscreen
    sta SteveLaserRelY+1
    sec
    rts
LaserViewportOffscreen:
    jmp RetireLaserSegment

LaserBeamCells:
    ldy #0
    lda SteveLaserShotPacked,x
    and #$0f
    cmp #8
    bcc LaserSlope
    eor #$0f
LaserSlope:
    cmp #5
    bcc LaserTilePair
    iny
    iny
LaserTilePair:
    lda SteveLaserShotPacked,x
    bpl LaserRightTiles
    lda LaserTiles+1,y
    sta SteveLaserDrawTile1
    lda LaserTiles,y
    sta SteveLaserDrawTile2
    lda #$41
    bne LaserTileAttr
LaserRightTiles:
    lda LaserTiles,y
    sta SteveLaserDrawTile1
    lda LaserTiles+1,y
    sta SteveLaserDrawTile2
    lda #1
LaserTileAttr:
    sta SteveLaserDrawAttr1
    lda SteveLaserShotPacked,x
    and #8
    beq LaserFinalAttr
    lda SteveLaserDrawAttr1
    ora #$80
    sta SteveLaserDrawAttr1
LaserFinalAttr:
    lda SteveLaserDrawAttr1
    sta SteveLaserDrawAttr2
    sec
    rts
LaserTiles: .byte $59,$5b,$5d,$5f
