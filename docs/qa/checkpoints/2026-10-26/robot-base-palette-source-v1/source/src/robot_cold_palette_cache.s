; Tail is called only after the original legacy producer appended6+6+7 bytes.
; No new RAM or NMI work. Retain the genuine resident RTS/caller registers.
.pushseg
.segment "ROBOT_COLD_PALETTE_CACHE"
.proc RobotColdPaletteCommit
  sta VRAM_Buffer1_Offset
  php
  pha
  phx
  ; A complete default GetColors body row is the normal palette source too.
  ; Preserve cold Ss admission below, including its stricter charge-zero rule.
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  bne ColdCache
  lda InvSelected+CHARACTER_MEGAMAN
  bne ColdCache
  lda GuestPowerupActive
  ora StarInvincibleTimer
  bne ColdCache
  lda MmChargeFrames
  cmp #33
  bcs ColdCache
  lda VRAM_Buffer1_Offset
  cmp #19
  bcc ColdCache
  cmp #84
  bcs ColdCache
  ldx #1
  lda PlayerStatus
  cmp #2
  bne BaseCache
  inx
BaseCache:
  stx MmLastPalette
ColdCache:
  lda GameEngineSubroutine
  bne Done
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  beq Robot
  cmp #CHARACTER_BASS
  bne Done
  lda RlVariant
  bne Done
Robot:
  lda SelectedCharacter
  tax
  lda InvSelected,x
  bne Done
  lda GuestPowerupActive
  ora StarInvincibleTimer
  ora MmChargeFrames
  ora MmCharging
  bne Done
  lda VRAM_Buffer1_Offset
  cmp #19
  bcc Done
  cmp #84
  bcs Done
  ; Final19..83 implies initial0..64 and all19 command bytes plus terminator
  ; fit the declared84-byte native buffer without arithmetic wrapping.
  lda #1
  sta SsLastPalette
Done:
  plx
  pla
  plp
  rts
.endproc
.assert *-RobotColdPaletteCommit<=$a0,error,"Cold palette tail remains before AC00"
.popseg
