; Same-size native per-gameplay-update bridge and retained Karnov dispatcher.
; ROSTER_INGRESS0 reproduces the exact current31B+12B source preimage.
.setcpu "6502"
.export RosterFireballBridge,RosterFireballBridgeEnd,RosterDispatcherEnd
.ifndef Selected
Selected=$6002
.endif
.ifndef HpCount
HpCount=$7387
.endif
.ifndef HpSpawnAndTrack
HpSpawnAndTrack=$ad0b
.endif
NativeFireball=$ad2e
KarnovPlatformTick=$b198
RosterDispatcher=$b134

.segment "ROSTER_FIXED_BRIDGE"
RosterFireballBridge:
    jsr NativeFireball
    lda HpCount
    bne CallRoster
    lda Selected
.if ROSTER_INGRESS
    cmp #22
    bcc BridgeDone
.else
    cmp #34
    bne BridgeDone
.endif
CallRoster:
    lda #<RosterDispatcher
    sta $016c
    lda #>RosterDispatcher
    sta $016d
    lda #$9a
    jsr $015a
BridgeDone:
    rts
RosterFireballBridgeEnd:

.segment "ROSTER_DISPATCH"
.if ROSTER_INGRESS
    jmp ManualRosterDispatch
.else
    lda Selected
.endif
    cmp #34
    .assert * = $b139,lderror,"Retain native Karnov branch location"
    .byte $f0,KarnovPlatformTick-$b13b
.if ROSTER_INGRESS
    jmp ManualRosterSkipEmpty
.else
    jmp HpSpawnAndTrack
.endif
    nop
    nop
RosterDispatcherEnd:
