.setcpu "6502"
.segment "STEVE_ARMOR_INJURY"
; Preserve the original enemy index before the authenticated cache service.
; The enclosing InjurePlayer consumes carry and reloads ObjectOffset at exit.
ArmorNativeInjury:
    stx JnSavedX
    lda #<ArmorNativeMappedCall
    sta $016c
    lda #>ArmorNativeMappedCall
    sta $016d
    lda #$88
    jsr $015a
    ldx JnSavedX
    ora #0
    bne InjuryProtected
    lda JnHealth
    cmp #3
    bcc InjuryFatal
    sbc #2
    sta JnHealth
    lda #60
    sta JnHurt
    lda #1
    sta JnUiDirty
    lda #4
    sta InjuryTimer
    lda #0
    sta TimerControl
    sta PlayerChangeSizeFlag
    sta GuestHurtTicks
    sta GuestHurtKind
    lda #8
    sta Square1SoundQueue
InjuryProtected:
    rts                         ; the service and accepted subtraction set C
InjuryFatal:
    lda #0
    sta JnHealth
    jmp KillPlayer

.segment "STEVE_ARMOR_STATUS"
ArmorNativeStatus:
    lda JnHurt
    ora $5c85                   ; Steve-owned mirror, native area reset clears it
    bne StatusAlive
    lda JnHealth
    cmp #3
    bcs StatusAlive
    lda #0
    sta JnHealth
    rts
StatusAlive:
    lda #1
    rts

.segment "STEVE_ARMOR_AUTH"
ArmorNativeAuth:
    bit $730b
    bvc AuthFallback
    ldx #3
AuthBank:
    stx CurrentBankC
    stx $5116
    lda $dfe0
    cmp #ArmorCookieMarker
    bne AuthFallback
    dex
    cpx #1
    bne AuthBank
    jmp ArmorDamageGateway
AuthFallback:
    lda JnHurt
    sec
    rts

.segment "STEVE_ARMOR_MAP_CALL"
ArmorNativeMappedCall:
    lda CurrentBankC
    pha
    lda #<ArmorNativeAuth
    sta $016c
    lda #>ArmorNativeAuth
    sta $016d
    lda #$85
    jsr $015a
    tax
    pla
    jsr $80c2
    txa
    rts
