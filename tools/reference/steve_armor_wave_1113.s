.setcpu "6502"
.segment "STEVE_ARMOR_RUNTIME"

ArmorWaveTick:
    lda SteveHitLife
    cmp #15
    bne WaveReadAge
    lda #$ff
    sta ArmorWaveAge
WaveReadAge:
    lda ArmorWaveAge
    cmp #$ff
    beq WaveMove
    inc ArmorWaveAge
WaveMove:
    lda ArmorWaveFacing
    cmp #2
    beq WaveMoveLeft
    clc
    lda SteveHitX
    adc #4
    sta SteveHitX
    lda SteveHitPage
    adc #0
    jmp WaveStorePage
WaveMoveLeft:
    sec
    lda SteveHitX
    sbc #4
    sta SteveHitX
    lda SteveHitPage
    sbc #0
WaveStorePage:
    sta SteveHitPage
    lda SteveHitHigh
    cmp #1
    bne WaveAgeFinished
    ; A native ring-buffer point is meaningful inside the current viewport.
    lda SteveHitX
    sec
    sbc ScreenLeft_X_Pos
    lda SteveHitPage
    sbc ScreenLeft_PageLoc
    bne WaveEnemies
    ; The original B93F probes one world cell. Reuse the current native
    ; one-cell brick/question adapter and retain its real block lifecycle.
    lda SprDataOffset_Ctrl
    pha
    lda SteveHitX
    sta WaveProbeX
    lda SteveHitPage
    sta WaveProbePage
    lda SteveHitY
    sta WaveProbeY
    lda #<NativeWaveBlockPoint
    sta $016c
    lda #>NativeWaveBlockPoint
    sta $016d
    lda #NativeWaveBlockBank
    jsr $015a
    lda #2
    jsr $80c2
    pla
    eor SprDataOffset_Ctrl
    and #1
    beq WaveEnemies
    lda #0
    sta ArmorWaveAge
WaveEnemies:
    ; Original enemy actors test the persistent slot-F hit separately.
    ; Preserve the wave across each native hit and visit all six slots.
    lda SteveHitLife
    pha
    lda ArmorWaveAge
    cmp #12
    bcc WaveRestoreLife
    jsr ArmorWavePunchToken
    bcs WaveRestoreLife
    lda #6
WaveEnemyPass:
    pha
    lda #<SteveHitEnemy
    ldy #>SteveHitEnemy
    jsr ArmorCallRaw3
    pla
    sec
    sbc #1
    bne WaveEnemyPass
WaveRestoreLife:
    pla
    sta SteveHitLife
WaveAgeFinished:
    dec SteveHitLife
    sec
    rts

ArmorWavePunchToken:
    ldx #5
WaveTokenSlot:
    jsr NativeWaveTokenOwned
    bcc WaveTokenNext
    lda Enemy_State,x
    bpl WaveTokenNext
    lda SteveHitHigh
    cmp Enemy_Y_HighPos,x
    bne WaveTokenNext
    cmp #1
    bne WaveTokenNext
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
    bne WaveTokenNext
    lda $03
    cmp #29
    bcs WaveTokenNext
    lda Enemy_Y_Position,x
    clc
    adc #26
    bcs WaveTokenNext
    sec
    sbc SteveHitY
    cmp #37
    bcs WaveTokenNext
    lda InvPickup,x
    eor #1
    sta InvPickup,x
    lda #0
    sta ArmorWaveAge
    sec
    rts
WaveTokenNext:
    dex
    bpl WaveTokenSlot
    clc
    rts

ArmorWaveDraw:
    lda SteveArmorTimer
    beq WaveDrawDeclined
    lda SteveHitLife
    beq WaveDrawDeclined
    ldx #0
    cmp #7
    bcs WaveDrawPhase
    inx
    cmp #3
    bcs WaveDrawPhase
    inx
WaveDrawPhase:
    lda WaveRecordLow,x
    sta $03
    lda WaveRecordHigh,x
    sta $04
    lda #0
    sta $c943
    sta $c944
    lda #0
    ldx ArmorWaveFacing
    cpx #2
    bne WaveMirrorReady
    lda #$40
WaveMirrorReady:
    sta $c942
    lda #$e0
    sta $05
    lda #$c8
    sta $06
    jsr $cf6a
    lda #$e0
    sta $03
    lda #$c8
    sta $04
    lda SteveHitX
    sec
    sbc ScreenLeft_X_Pos
    sta $07
    lda SteveHitPage
    sbc ScreenLeft_PageLoc
    sta $08
    lda SteveHitY
    sta $09
    lda SteveHitHigh
    sta $0a
    lda #<WavePhysicalPage
    sta $016a
    ldx #>WavePhysicalPage
    ldy #4
    lda #<X5SetSpecialChr
    sta $016c
    lda #>X5SetSpecialChr
    sta $016d
    lda #$be
    jsr $015a
    lda #<MetaspriteRenderLoop
    sta $016c
    lda #>MetaspriteRenderLoop
    sta $016d
    sec
    rts
WaveDrawDeclined:
    clc
    rts

.segment "STEVE_ARMOR_BRIDGE"
ArmorWaveGateway:
    lda SteveArmorTimer
    beq WaveNativeStationary
    lda #3
    jsr ArmorInvoke
    bcs WaveNativeDone
WaveNativeStationary:
    jsr NativeWaveOrdinaryHit
    dec SteveHitLife
WaveNativeDone:
    rts

ArmorWaveDrawGateway:
    pha
    lda #4
    jsr ArmorInvoke
    bcc WaveNativeOldDraw
    pla
    lda #0
    sta $06
    sta $016a
ArmorWaveNativeRender:
    jsr SteveDrawInvoke
    sec
    rts
WaveNativeOldDraw:
    pla
    tax
    ora CurrentOAMOffset
    jmp SteveDraw+4

.segment "STEVE_ARMOR_RECOVERY"
ArmorWaveBirth:
    lda StevePunchLives,x
    ldy SteveArmorTimer
    beq WaveBirthStore
    lda #15
WaveBirthStore:
    ldy PlayerFacingDir
    sty ArmorWaveFacing
    sta SteveHitLife
    rts
