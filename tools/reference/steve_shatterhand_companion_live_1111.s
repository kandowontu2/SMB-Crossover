.setcpu "6502"
.segment "COMPANION_HOST"

SteveCompanionTick:
    lda GamePauseStatus
    lsr a
    bcc TickUnpaused
    rts
TickUnpaused:
    lda PlayerFacingDir
    cmp #2
    lda #0
    ror a
    sta SteveBotPlayerFacing
    jsr SteveTokenTick
.ifdef STEVE_LASER_LIVE
    lda SteveBotActor
    cmp #3
    beq UpdateLaserLifecycle
    lda SteveLaserActive
    beq CheckFirstBot
UpdateLaserLifecycle:
    jsr SteveLaserLifecycle
    lda SteveUpgradeState
    beq LaserUpgradeReady
    rts
LaserUpgradeReady:
    lda SteveBotActor
    cmp #3
    beq PackBotPlayer
CheckFirstBot:
.endif
    jsr FirstBotActive
    bne TickDone
.ifdef STEVE_LASER_LIVE
PackBotPlayer:
.endif
    ; Keep world coordinates modulo 4096 in donor Q4. Subtract the
    ; camera only at the native collision and metasprite boundaries.
    lda Player_X_Position
    clc
    adc #8
    sta SteveBotPlayerX
    lda Player_PageLoc
    adc #0
    sta SteveBotPlayerX+1
    lda Player_Y_Position
    clc
    adc #16
    sta SteveBotPlayerY
    lda Player_Y_HighPos
    adc #0
    sec
    sbc #1
    sta SteveBotPlayerY+1
    ldx #4
PackPlayer:
    asl SteveBotPlayerX
    rol SteveBotPlayerX+1
    asl SteveBotPlayerY
    rol SteveBotPlayerY+1
    dex
    bne PackPlayer
    lda SteveHostXFrac
    ora SteveBotPlayerX
    sta SteveBotPlayerX
    lda SteveHostYFrac
    ora SteveBotPlayerY
    sta SteveBotPlayerY
    lda #0
    ldx Player_State
    bne PostureReady
    ldx SteveBotPad
    txa
    and #4
    beq PostureReady
    lda #3
PostureReady:
    sta SteveBotPlayerState
.ifdef STEVE_LASER_LIVE
    lda SteveBotActor
    cmp #3
    bne UpdateFirstCompanion
    jmp SteveLaserTick
UpdateFirstCompanion:
.endif
    jsr SteveFirstBotShotUpdate
    jsr SteveCompanionHit
.ifdef STEVE_LIFT_LIVE
    jsr SteveLiftOrbit
    lda SteveLiftState
    cmp #4
    bcs TickDone
.else
    jsr SteveCompanionOrbit
.endif
    jsr SteveFirstBotWeapon
    lda SteveBotShotTimer
    cmp #$33
    bne TickDone
    lda SteveBotClock
    sta SteveBotDrawPhase
TickDone:
    rts

FirstBotActive:
    lda SteveUpgradeState
    bne TickDone
    lda SteveBotActor
    cmp #1
    rts

SteveCompanionDraw:
    lda GameEngineSubroutine
    cmp #8
    bne TickDone
.ifdef STEVE_LIFT_POSE
    jsr SteveLiftDraw
    bcc OrdinaryCompanionDraw
    rts
OrdinaryCompanionDraw:
.endif
.ifdef STEVE_LASER_LIVE
    lda SteveLaserActive
    beq DrawFirstCompanion
    jmp SteveLaserDraw
DrawFirstCompanion:
.endif
    jsr FirstBotActive
    bne TickDone
    lda SteveBotPose+1
    beq DrawShot
    ldx #0
    lda SteveBotPose
    cmp #$c0
    bne TestPoseBe
    ldx #2
TestPoseBe:
    cmp #$be
    bne BodyFacing
    ldx #4
BodyFacing:
    bit SteveBotFacing
    bpl BodyPointer
    inx
BodyPointer:
    lda BodyMetaLo,x
    ldy BodyMetaHi,x
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
DrawShot:
    lda SteveBotShotType
    bpl TickDone
    lda SteveBotShotTimer
    cmp #$33
    beq TickDone
    ; Gameplay catch-up can skip every other draw. Advance the visual
    ; phase when drawing so both donor tiles reach the displayed OAM.
    lda SteveBotDrawPhase
    eor #1
    sta SteveBotDrawPhase
    lsr a
    lda #<ShotEven
    ldy #>ShotEven
    bcc ShotPointer
    lda #<ShotOdd
    ldy #>ShotOdd
ShotPointer:
    jsr SetCompanionMeta
    jsr ProjectShot
    jmp DrawCompanionMeta

SteveCompanionHit:
    lda SteveBotShotType
    bmi LiveContact
    rts
LiveContact:
    jsr ProjectShot
.ifdef STEVE_LASER_LIVE
    jsr FindCompanionTarget
    bcs ConsumeCompanionShot
    rts
FindCompanionTarget:
    lda $08
    bne TargetInvalid
    lda $0a
    cmp #1
    beq SearchTargets
TargetInvalid:
    clc
    rts
SearchTargets:
.else
    lda $08
    bne HitDone
    lda $0a
    cmp #1
    bne HitDone
.endif
    ldx #5
EnemyLoop:
    lda Enemy_Flag,x
    beq NextEnemy
    bmi NextEnemy
    lda Enemy_ID,x
    cmp #$0c
    beq NextEnemy
    cmp #$15
    bcs NextEnemy
    lda Enemy_State,x
    and #$20
    bne NextEnemy
    lda Enemy_Y_HighPos,x
    cmp #1
    bne NextEnemy
    lda JnEnemyHurt,x
    bne NextEnemy
    txa
    asl a
    asl a
    tay
    lda $07
    cmp BoundingBox_UL_Corner+4,y
    bcc NextEnemy
    cmp BoundingBox_UL_Corner+6,y
    bcs NextEnemy
    lda $09
    cmp BoundingBox_UL_Corner+5,y
    bcc NextEnemy
    cmp BoundingBox_UL_Corner+7,y
    bcc DamageEnemy
    bne NextEnemy
DamageEnemy:
.ifdef STEVE_LASER_LIVE
    sec
    rts
ConsumeCompanionShot:
.endif
    lda #$15
    sta SteveBotShotType
    lda #0
    sta SteveBotShotTimer
    sta SteveBotShotPower
ApplyCompanionDamage:
    lda #12
    sta JnEnemyHurt,x
    lda JnEnemyHP,x
    cmp #2
    bcc DefeatEnemy
    dec JnEnemyHP,x
    lda #8
    ora Square1SoundQueue
    sta Square1SoundQueue
    rts
DefeatEnemy:
    lda #<NativeDefeat
    sta $016c
    lda #>NativeDefeat
    sta $016d
    lda #$e2
    jmp $015a
NextEnemy:
    dex
    bpl EnemyLoop
HitDone:
.ifdef STEVE_LASER_LIVE
    clc
.endif
    rts

ProjectShot:
    lda SteveBotShotX
    sta $07
    lda SteveBotShotX+1
    sta $08
    lda SteveBotShotY
    sta $09
    lda SteveBotShotY+1
    sta $0a
ProjectToScreen:
    ; Unpack X as a 12-bit world position and Y as signed pixels
    ; relative to native page 1. Wrap X only after camera subtraction.
    ldx #4
UnpackPosition:
    lsr $08
    ror $07
    lda $0a
    cmp #$80
    ror $0a
    ror $09
    dex
    bne UnpackPosition
    lda $07
    sec
    sbc ScreenLeft_X_Pos
    sta $07
    lda $08
    sbc ScreenLeft_PageLoc
    and #$0f
    cmp #8
    bcc StoreRelativePage
    ora #$f0
StoreRelativePage:
    sta $08
    inc $0a
    rts

SetCompanionMeta:
    sta $03
    sty $04
    rts
DrawCompanionMeta:
    lda #0
    sta $06
    sta $016a
    lda #<NativeRender
    sta $016c
    lda #>NativeRender
    sta $016d
    jmp SteveDrawInvoke

BodyMetaLo: .byte <BodyIdleRight,<BodyIdleLeft,<BodyOpenRight,<BodyOpenLeft,<BodyCloseRight,<BodyCloseLeft
BodyMetaHi: .byte >BodyIdleRight,>BodyIdleLeft,>BodyOpenRight,>BodyOpenLeft,>BodyCloseRight,>BodyCloseLeft
BodyIdleRight:  .byte 8,$71,1,$f8,$f8,$6f,1,$f8,0
BodyIdleLeft:   .byte 8,$71,$41,$f8,0,$6f,$41,$f8,$f8
BodyOpenRight:  .byte 8,$73,1,$f8,$f8,$6f,1,$f8,0
BodyOpenLeft:   .byte 8,$73,$41,$f8,0,$6f,$41,$f8,$f8
BodyCloseRight: .byte 8,$75,1,$f8,$f8,$6f,1,$f8,0
BodyCloseLeft:  .byte 8,$75,$41,$f8,0,$6f,$41,$f8,$f8
ShotEven: .byte 8,$79,2,$f8,$f8,$79,$42,$f8,0
ShotOdd:  .byte 8,$77,1,$f8,$f8,$77,$41,$f8,0
