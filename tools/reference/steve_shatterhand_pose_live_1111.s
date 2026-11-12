.setcpu "6502"
.segment "POSE_GATE"
; The reclaimed high-pointer table contains fourteen identical C1 bytes.
; CECE on the stack enters CECF after the fixed bank setter returns.
StevePoseGate:
    cmp #$dc
    bne GateReturn
    lda #$ce
    pha
    pha
    lda #2
    jmp $80c2
GateReturn:
    rts

.segment "POSE_BANK"
    lda FmGroups
    and #$60
    beq MikeBank
    cmp #$60
    beq MikeBank
    cpx #3
    bcc BodyReady
    ldx Player_State
    beq BodyReady
    ldx #4
BodyReady:
    lsr a
    lsr a
    lsr a
    adc #$d4
    ldy OperMode
    beq BankReturn
    ldy #0
    jmp StevePoseGate
MikeBank:
    lda #$c4
    ldy #2
BankReturn:
    rts

.segment "POSE_WORKER"
StevePoseSelect:
    txa
    pha
    lda SteveLiftState
    cmp #4
    bcc StockPose
    cmp #8
    bcs StockPose
    lda GameEngineSubroutine
    cmp #8
    bne StockPose
    lda SteveLiftPlayerPose
    jsr FindPose
    bcc StockPose
    lda #8
    sta PoseAnchorX
    lda #16
    sta PoseAnchorY
    lda #0
    ldx PlayerFacingDir
    cpx #2
    bne BodyMirror
    lda #$40
BodyMirror:
    sta PoseMirror
    lda #<PoseBuffer
    sta $02
    lda #>PoseBuffer
    sta $03
    jsr BuildPose
    lda #<PoseBuffer
    sta SmPosePtr
    lda #>PoseBuffer
    sta SmPosePtr+1
    lda #$e9
    sta ObjectMetasprite
    lda #$53
    sta SmChrBank
    sta PlayerChrBank
    pla
    pla
    pla
    ldx #1
    ldy #0
    lda #$53
    sta $016a
    lda #$75
    sta $016c
    lda #$a2
    sta $016d
    lda #$be
    jmp $015a

StockPose:
    pla
    tax
    ldy #0
    ; Bank publication changes the executing C window. The fixed native
    ; PLA/RTS tail restores the original CHR return value after that change.
    lda #$dc
    pha
    lda #$a9
    pha
    lda #$17
    pha
    lda #$e1
    jmp $80c2

FindPose:
    ldx #9
FindNext:
    cmp PoseIds,x
    beq FoundPose
    dex
    bpl FindNext
    clc
    rts
FoundPose:
    lda PoseOffsets,x
    sta $00
    lda #$ce
    sta $01
    sec
    rts

; Donor records are relative to the actor's center. Construct a native
; record with the exact reflection and the appropriate anchor offset.
BuildPose:
    ldy #0
    lda ($00),y
    sta ($02),y
    tay
BuildCell:
    lda ($00),y
    bit PoseMirror
    bvc BuildX
    eor #$ff
    sec
    sbc #7
BuildX:
    clc
    adc PoseAnchorX
    sta ($02),y
    dey
    lda ($00),y
    clc
    adc PoseAnchorY
    sta ($02),y
    dey
    lda ($00),y
    eor PoseMirror
    sta ($02),y
    dey
    lda ($00),y
    sta ($02),y
    dey
    bne BuildCell
    rts

SteveLiftDraw:
    lda SteveLiftState
    cmp #4
    bcc NoLiftDraw
    cmp #8
    bcs NoLiftDraw
    lda SteveLiftBotPose
    jsr FindPose
    bcc NoLiftDraw
    lda #0
    sta PoseAnchorX
    sta PoseAnchorY
    lda SteveBotFacing
    lsr a
    and #$40
    sta PoseMirror
    lda #<(PoseBuffer+32)
    sta $02
    lda #>(PoseBuffer+32)
    sta $03
    jsr BuildPose
    lda $02
    ldy $03
    jsr SetCompanionMeta
    ldx #3
CopyLiftPosition:
    lda SteveBotX,x
    sta $07,x
    dex
    bpl CopyLiftPosition
    jsr ProjectToScreen
    jsr DrawCompanionMeta
    sec
    rts
NoLiftDraw:
    clc
    rts
