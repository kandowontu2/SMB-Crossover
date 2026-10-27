; Existing cache acknowledgement after a real complete normal Proto palette.
; No NMI, new RAM or physical palette mutation; all caller AXYP preserved.
.pushseg
.segment "PROTO_PALETTE_ACK"
.proc ProtoFixAndAcknowledgePalette
 jsr ProtoFixQueuedPalette
 php
 pha
 txa
 pha
 tya
 pha
 lda SelectedCharacter
 cmp #CHARACTER_MEGAMAN
 bne Restore
 lda ProtoVariant
 beq Restore
 lda InvSelected+CHARACTER_MEGAMAN
 bne Restore
 lda GuestPowerupActive
 ora StarInvincibleTimer
 ora MmChargeFrames
 bne Restore
 lda PlayerStatus
 cmp #2
 bcs Restore
 ldx VRAM_Buffer1_Offset
 ; Legacy GetColors appended exactly6(face)+6(weapon)+7(body) bytes.
 ; An unsigned19-byte append cannot wrap into this safe19..83 range.
 cpx #19
 bcc Restore
 cpx #.sizeof(VRAM_Buffer1)
 bcs Restore
 lda VRAM_Buffer1,x
 bne Restore
 ; The successfully queued tail has the real4-color body command.
 lda VRAM_Buffer1-7,x
 cmp #$3f
 bne Restore
 lda VRAM_Buffer1-6,x
 cmp #$10
 bne Restore
 lda VRAM_Buffer1-5,x
 cmp #4
 bne Restore
 lda VRAM_Buffer1-3,x
 cmp #$0f
 bne Restore
 lda VRAM_Buffer1-2,x
 cmp #$16
 bne Restore
 lda VRAM_Buffer1-1,x
 cmp #$10
 bne Restore
 lda #1
 sta SsLastPalette
 sta MmLastPalette             ; Same successfully queued normal body colors.
Restore:
 pla
 tay
 pla
 tax
 pla
 plp
 rts
.endproc
.assert *-ProtoFixAndAcknowledgePalette<=192,error,"Explicit bank66 BE40..BEFF bound"
.popseg
