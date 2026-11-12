; Once per surviving robot update, before movement. Host normal enemies use
; collision flag $01. Existing projectiles keep their separate damage path.
.setcpu "6502"
.segment "THROW_SCAN"
SteveThrowScan:
    lda SteveBotActor
    cmp #1
    beq ThrowScanActor
    cmp #3
    bne ThrowScanReturn
ThrowScanActor:
    lda SteveBotAge
    cmp #12
    bcc ThrowScanAge
    lda SteveArmorTimer
    bne ThrowScanAge
    lda SteveUpgradeState
    bne ThrowScanAge
    bit SteveThrowSelector
    bpl ThrowScanAge
    lda SteveThrowTimer
    bpl ThrowScanVisible
    cmp #$ff
    bne ThrowScanAge
ThrowScanVisible:
    lda SteveBotPose+1
    beq ThrowScanAge
    lda ObjectOffset
    pha
    ldx #14
ThrowScanSave:
    lda $00,x
    pha
    dex
    bpl ThrowScanSave
    ldx #2
ThrowScanSaveDelta:
    lda $90,x
    pha
    dex
    bpl ThrowScanSaveDelta
    jsr SteveThrowWorldPoint
    jsr SteveThrowFindTarget
    bcc ThrowScanRestore
    stx ObjectOffset
    lda #1
    jsr SteveThrowContactDamage
ThrowScanRestore:
    ldx #0
ThrowScanRestoreDelta:
    pla
    sta $90,x
    inx
    cpx #3
    bne ThrowScanRestoreDelta
    ldx #0
ThrowScanRestoreScratch:
    pla
    sta $00,x
    inx
    cpx #15
    bne ThrowScanRestoreScratch
    pla
    sta ObjectOffset
ThrowScanAge:
    lda SteveBotActor
    cmp #$ff
    beq ThrowScanReturn
    lda SteveBotAge
    cmp #$ff
    beq ThrowScanReturn
    inc SteveBotAge
ThrowScanReturn:
    rts
