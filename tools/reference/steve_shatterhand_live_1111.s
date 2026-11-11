.setcpu "6502"

.segment "GATE"
SteveWeaponsGate:
    lda $730b
    eor #$40
    and #$60
    beq SteveWeapons
    lda StevePressed
    jmp $a022
SteveWeapons:
    lda #$ff
    sta $016a
    lda #<HotEntry
    sta $016c
    lda #>HotEntry
    sta $016d
    lda #$de
    jmp $015a

.segment "MUX"
SteveSharedMux:
    php
    bit $730b
    bvs StevePrivate
    plp
    jmp $b67b
StevePrivate:
    plp
    jmp SteveCombat
SteveDrawInvoke:
    lda #$84
    jsr $015a
    sec
    rts

.segment "COMBAT"
SteveCombat:
    cpy #$e2
    bne OtherSteveCaller
    cmp #$ff
    beq SteveAttackMain
    jmp SteveDraw
SteveAttackMain:
    lda GamePauseStatus
    lsr a
    bcs SteveAccepted
    lda JnHurt
    bne SteveCancel
    lda Player_State
    beq SteveGround
    lda #1
    bne SteveStep
SteveGround:
    lda SavedJoypadBits
    and #4
    beq SteveStep
    lda #3
SteveStep:
    jsr StevePunchControl
    bcc SteveExisting
    jsr StevePunchBirth
SteveExisting:
    lda StevePunchSelector
    sta JnAttack
    lda StevePunchSound
    beq SteveNoCue
    lda Square1SoundQueue
    ora #$20
    sta Square1SoundQueue
SteveNoCue:
    lda SteveHitLife
    beq SteveAccepted
    jsr SteveHitEnemy
    dec SteveHitLife
SteveAccepted:
    sec
    rts
OtherSteveCaller:
    clc
    rts
SteveCancel:
    lda #0
    sta StevePunchSelector
    sta JnAttack
    sta SteveHitLife
    beq SteveAccepted

.segment "BIRTH"
; The donor creates a stationary object relative to the center of its
; body. Convert that origin to SMB's player-left/player-top coordinates.
StevePunchBirth:
    lda StevePunchLives,x
    sta SteveHitLife
    lda PlayerFacingDir
    cmp #2
    beq PunchLeft
    lda SteveRightX,x
    ldy #0
    beq PunchX
PunchLeft:
    lda SteveLeftX,x
    ldy #$ff
PunchX:
    clc
    adc Player_X_Position
    sta SteveHitX
    tya
    adc Player_PageLoc
    sta SteveHitPage
    lda SteveTopY,x
    clc
    adc Player_Y_Position
    sta SteveHitY
    lda Player_Y_HighPos
    adc #0
    sta SteveHitHigh
    lda SteveDamage,x
    sta SteveHitDamage
    rts
SteveRightX: .byte 23,23,26,26
SteveLeftX: .byte $f9,$f9,$f6,$f6
SteveTopY: .byte 12,16,12,16
SteveDamage: .byte 2,2,4,4

SteveDraw:
    tax
    ora CurrentOAMOffset
    and #3
    bne SteveDrawDone
    txa
    clc
    adc CurrentOAMOffset
    bcs SteveDrawDone
    cmp #245
    bcs SteveDrawDone
    lda StevePunchSelector
    beq SteveDrawDone
    lda StevePunchPhase
    lsr a
    beq SteveDrawDone
    ldx Player_Y_HighPos
    cpx #1
    bne SteveDrawDone
    lda #<NativeRender
    sta $016c
    jmp SteveDrawProject
SteveDrawDone:
    sec
    rts

.segment "COMBAT"
; Native enemies use world X and absolute Y. Center their 16px box and
; bias the signed delta so page carry, offscreen actors and pits stay exact.
SteveHitEnemy:
    lda SteveHitHigh
    cmp #1
    beq SteveHitPlayfield
    rts
SteveHitPlayfield:
    ldx #5
SteveCheckEnemy:
    lda Enemy_Flag,x
    beq SteveNextEnemy
    bmi SteveNextEnemy
    lda Enemy_ID,x
    cmp #$0c
    beq SteveNextEnemy
    cmp #$15
    bcs SteveNextEnemy
    lda Enemy_State,x
    and #$20
    bne SteveNextEnemy
    lda Enemy_Y_HighPos,x
    cmp #1
    bne SteveNextEnemy
    lda JnEnemyHurt,x
    bne SteveNextEnemy
    lda Enemy_X_Position,x
    clc
    adc #22
    sta $03
    lda Enemy_PageLoc,x
    adc #0
    tay
    lda $03
    sec
    sbc SteveHitX
    sta $03
    tya
    sbc SteveHitPage
    bne SteveNextEnemy
    lda $03
    cmp #29
    bcs SteveNextEnemy
    lda Enemy_Y_Position,x
    clc
    adc #26
    bcs SteveNextEnemy
    sec
    sbc SteveHitY
    bcc SteveNextEnemy
    cmp #37
    bcs SteveNextEnemy
    lda #1
    sta SteveHitLife
    lda #12
    sta JnEnemyHurt,x
    lda JnEnemyHP,x
    sec
    sbc SteveHitDamage
    bcc SteveDefeat
    beq SteveDefeat
    sta JnEnemyHP,x
    lda #8
    ora Square1SoundQueue
    sta Square1SoundQueue
    rts
SteveDefeat:
    lda #<NativeDefeat
    sta $016c
    lda #>NativeDefeat
    sta $016d
    lda #$e2
    jmp $015a
SteveNextEnemy:
    dex
    bmi SteveHitDone
    jmp SteveCheckEnemy
SteveHitDone:
    rts

; Retain the native metasprite clipping, OAM rotation, and cursor handling.
SteveDrawProject:
    lda Player_X_Position
    sec
    sbc ScreenLeft_X_Pos
    sta $07
    lda Player_PageLoc
    sbc ScreenLeft_PageLoc
    sta $08
    lda Player_Y_Position
    sta $09
    stx $0a
    dex
    stx $06
    jmp SteveDrawEmit

.segment "DRAW"
SteveDrawEmit:
    lda PlayerFacingDir
    lsr a
    ldx #<SteveDrawRight
    bcs SteveDrawPointer
    ldx #<SteveDrawLeft
SteveDrawPointer:
    stx $03
    lda #>SteveDrawRight
    sta $04
    lda #>NativeRender
    sta $016d
    jmp SteveDrawInvoke
SteveDrawRight: .byte 8,32,0,0,16,34,0,0,24
SteveDrawLeft:  .byte 8,32,$40,0,$f8,34,$40,0,$f0
