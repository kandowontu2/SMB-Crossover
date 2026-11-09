; One native ID25 vertical girder, requested by Mini or Karnov's own Main.
; Y = signed platform-left offset from the player's X (-12 or -8).
; Return A=slot+1, or $80 to retry. The caller owns the pending latch.
.setcpu "6502"
.export ManualPlatform, ManualPlatformCreated, ManualPlatformEnd

Enemy_Flag = $10
Enemy_ID = $17
Enemy_State = $1f
Player_PageLoc = $5c
Enemy_PageLoc = $5d
Player_X_Position = $75
Enemy_X_Position = $76
Player_Y_HighPos = $a4
Enemy_Y_HighPos = $a5
Player_Y_Position = $bd
Enemy_Y_Position = $be
FloateyNum_Control = $010d
Enemy_BoundBoxCtrl = $0646
HpActorOwner = $73ae
EraseEnemyObject = $8d2f
FarTarget = $016c
FarCallCommon = $015a
CheckpointEnemyID = $b67f
ManualMarker = $41

.segment "MANUAL"
ManualPlatform:
    lda Player_Y_HighPos
    cmp #1
    bne Retry
    lda Player_Y_Position
    cmp #208                    ; The native top must fit on screen page 1.
    bcc Prepare
Retry:
    lda #$80
    rts
Prepare:
    tya
    pha                        ; Native erase uses its own nested farcall.
    ldy #$ff
    ldx #5
Find:
    lda HpActorOwner,x
    bne Next                    ; Never touch an authored manager's actor.
    lda Enemy_Flag,x
    lsr a                       ; Only flag0 and primary flag1 qualify.
    bne Next
    bcc Empty
    lda Enemy_ID,x
    cmp #$25
    bne Next
    lda Enemy_State,x
    cmp #ManualMarker
    beq Spawn
    bne Next                    ; Never touch an authored manager's actor.
Empty:
    lda FloateyNum_Control,x
    bne Next                    ; A native score or authored owner still uses it.
    txa
    tay
Next:
    dex
    bpl Find
    tya
    bpl FreeFound
    pla
    bmi Retry                  ; The two caller offsets are negative.
FreeFound:
    tax
Spawn:
    ; Both exact ID25 constructor and erase consume the explicit slot in X.
    jsr EraseEnemyObject
    pla
    clc
    adc Player_X_Position
    tay
    lda Player_PageLoc
    adc #$ff
    bcs Position
    lda #0
    tay                         ; Clamp the world origin, including X=0.
Position:
    sta Enemy_PageLoc,x
    tya
    sta Enemy_X_Position,x
    lda Player_Y_Position
    clc
    adc #32
    sta Enemy_Y_Position,x
    lda #1
    sta Enemy_Flag,x
    sta Enemy_Y_HighPos,x
    lda #$25
    sta Enemy_ID,x
    ; Manual actors are not entries in the level's enemy parser stream.
    ; Use the same typed native constructor without parser-offset filtering.
    lda #<CheckpointEnemyID
    sta FarTarget
    lda #>CheckpointEnemyID
    sta FarTarget+1
    lda #$87
    jsr FarCallCommon
    lda #5
    sta Enemy_BoundBoxCtrl,x
    lda #ManualMarker
    sta Enemy_State,x
ManualPlatformCreated:
    inx
    txa
    rts
ManualPlatformEnd:
