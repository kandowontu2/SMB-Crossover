.setcpu "6502"

.segment "LINK_PORTRAIT_PREFIX"
; Same native intermediate/lives setup. Its only directional exception is
; Zelda1 Link: the original selected right record contains left-facing pixels.
; Native gameplay never enters DrawPlayer_Intermediate.
MenuPortraitPrefix:
    lda #$1d
    ldx #$12
    ldy SelectedCharacter
    beq MenuPortraitBodyReady
    lda #$91
    ldx #$38
MenuPortraitBodyReady:
    sta ObjectMetasprite
    stx PlayerChrBank
    inc ReloadCHRBank
    lda #$58
    sta Player_Y_Position
    lda ScreenLeft_PageLoc
    sta Player_PageLoc
    lda #1
    sta Player_Y_HighPos
    lsr a
    sta Player_SprAttrib
    lda #$60
    sta Player_X_Position
    lda #1
    cpy #4
    bne MenuPortraitFacingReady
    ldy Z2Variant
    bne MenuPortraitFacingReady
    asl a
MenuPortraitFacingReady:
    sta PlayerFacingDir

.segment "SONIC_PORTRAIT_FACING"
; The sole native intermediate caller already incremented ReloadCHRBank.
; Its stored facing1 becomes2 so the native standing box mirrors the imported
; left-facing Sonic/Super Sonic art. The leaf restores P after this instruction.
    asl PlayerFacingDir
