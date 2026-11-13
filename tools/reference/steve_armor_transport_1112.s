; Private armor-entry transport. The live host still needs the complete armor
; body, clock, damage and exit adapters before this may be delivered.
.setcpu "6502"
.segment "ARMOR_TRANSPORT"

; Same accepted token position/pattern/carry contract as the incumbent.
SteveTokenPreview:
    sta SteveTokenSymbol
    ldx #0
    ldy SteveTokenPattern
PreviewSlot:
    tya
    and #3
    beq TokenSlot
    cpx #2
    beq PreviewFull
    tya
    lsr a
    lsr a
    tay
    asl SteveTokenSymbol
    asl SteveTokenSymbol
    inx
    bne PreviewSlot
PreviewFull:
    clc
    rts
TokenSlot:
    lda SteveTokenSymbol
    ora SteveTokenPattern
    sec
    rts

; The token clock and source grant remain separate from the armor dispatcher.
SteveTokenTick:
    lda SteveTokenCountdown
    bne TokenCount
    lda SteveArmorTimer
    bne TokenTickDone
    lda SteveUpgradeState
    cmp #$0d
    beq TokenTickDone
    jsr SteveTokenIndex
    bcc TokenTickDone
    lda #$80
    sta SteveTokenCountdown
TokenCount:
    dec SteveTokenCountdown
    lda SteveTokenCountdown
    cmp #$30
    bne TokenTickDone
    jsr SteveTokenIndex
    bcc TokenTickDone
    lda #0
    sta SteveTokenPattern
    sta SteveTokenPreviewActor
    ; Index is now one-based, so the redundant actor-ID table is unnecessary.
    stx SteveTokenSymbol
    lda SteveRobotActor
    and #$3f
    cmp SteveTokenSymbol
    bne ReplaceRobot
    lda #$10
    sta SteveRobotArrival
    lda #$1d
    sta SteveUpgradeSound
    lda #$0d
    sta SteveUpgradeState
    lda #$7f
    sta SteveArmorWindup
    rts
ReplaceRobot:
    lda #$1e
    sta SteveUpgradeSound
    lda #$35
    bit SteveUpgradeFacing
    bpl RobotAngle
    lda #$2b
RobotAngle:
    sta SteveRobotAngle
    txa
    sta SteveRobotActor
    dex
    stx SteveRobotIndex
    lda #$10
    sta SteveRobotArrival
    lda #$ff
    sta SteveRobotLife
TokenTickDone:
    rts

SteveTokenIndex:
    ldx #8
FindTokenPattern:
    lda SteveTokenPatterns-1,x
    cmp SteveTokenPattern
    beq TokenIndexDone
    dex
    bne FindTokenPattern
    clc
TokenIndexDone:
    rts

SteveArmorTransportTick:
    lda SteveUpgradeState
    cmp #$0d
    bne ArmorTokenTail
    lda SteveTokenCountdown
    beq ArmorTransform
    cmp #$30
    bcc ArmorTokenTail
ArmorTransform:
    jsr SteveArmorTransformTick
ArmorTokenTail:
    jmp SteveTokenTick
SteveArmorTransformTick:
    sec
    lda SteveArmorWindup
    sbc #4
    sta SteveArmorWindup
    bcs ArmorWindupDone
    adc #4
    sta SteveArmorWindup
    jsr StevePunchReset
    sta SteveUpgradeState
    sta SteveUpgradeAnim
    sta SteveUpgradeCombo
    lda #$7f
    sta SteveArmorTimer
ArmorWindupDone:
    rts

SteveTokenPatterns: .byte $15,$2a,$25,$29,$1a,$16,$19,$26
