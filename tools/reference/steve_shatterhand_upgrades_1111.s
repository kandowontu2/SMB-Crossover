; Detached Shatterhand token/companion/armor decisions. Actor flight, sprite
; composition and terrain remain caller-owned. The caller commits the packed
; preview only when the physical donor token completes its flight.
.setcpu "6502"
.segment "UPGRADE"

; A = Alpha (1) or Beta (2). On success C = 1, A = candidate pattern,
; X = token position. A saturated three-slot pattern rejects the pickup.
SteveTokenPreview:
    sta SteveTokenSymbol
    ldx #0
    lda SteveTokenPattern
    and #3
    beq TokenSlot
    asl SteveTokenSymbol
    asl SteveTokenSymbol
    inx
    lda SteveTokenPattern
    and #$0c
    beq TokenSlot
    asl SteveTokenSymbol
    asl SteveTokenSymbol
    inx
    lda SteveTokenPattern
    and #$30
    beq TokenSlot
    clc
    rts
TokenSlot:
    lda SteveTokenSymbol
    ora SteveTokenPattern
    sec
    rts

; Original $9250/$92CA. One ordinary player decision advances the full
; pattern's display countdown. Grant begins as it crosses $31 to $30.
SteveTokenTick:
    lda SteveArmorTimer
    ora SteveTokenCountdown
    bne TokenCount
    lda SteveUpgradeState
    cmp #$0d
    beq TokenTickDone
    jsr SteveTokenIndex
    bcc TokenTickDone
    lda #$80
    sta SteveTokenCountdown
TokenCount:
    lda SteveTokenCountdown
    beq TokenTickDone
    dec SteveTokenCountdown
    lda SteveTokenCountdown
    cmp #$30
    bne TokenTickDone
    jsr SteveTokenIndex
    bcc TokenTickDone
    lda #0
    sta SteveTokenPattern
    sta SteveTokenPreviewActor
    lda SteveRobotActor
    and #$3f
    beq ReplaceRobot
    cmp SteveRobotActors,x
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
    lda SteveRobotActors,x
    sta SteveRobotActor
    stx SteveRobotIndex
    lda #$10
    sta SteveRobotArrival
    lda #$ff
    sta SteveRobotLife
TokenTickDone:
    rts

SteveTokenIndex:
    ldx #7
FindTokenPattern:
    lda SteveTokenPatterns,x
    cmp SteveTokenPattern
    beq FoundTokenPattern
    dex
    bpl FindTokenPattern
    clc
    rts
FoundTokenPattern:
    sec
    rts

; Original $97E1 decision after native support/visual setup. Caller invokes
; this only in the $0D transform state. Match its countdown and punch reset.
SteveArmorTransformTick:
    sec
    lda SteveArmorWindup
    sbc #4
    sta SteveArmorWindup
    bcs ArmorWindupDone
    adc #4
    sta SteveArmorWindup
    lda #0
    sta SteveUpgradeState
    sta SteveUpgradeAnim
    sta SteveUpgradeCombo
    lda #$7f
    sta SteveArmorTimer
ArmorWindupDone:
    rts

SteveTokenPatterns: .byte $15,$2a,$25,$29,$1a,$16,$19,$26
SteveRobotActors: .byte 1,2,3,4,5,6,7,8
