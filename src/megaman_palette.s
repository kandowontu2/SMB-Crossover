.pushseg
.segment "INVENTORY"
.proc MegaManPaletteState
  lda CrossoverBehaviorVersion
  beq ClassicPalette
  lda InvSelected+CHARACTER_MEGAMAN
  beq :+
    lda GuestPowerupActive
    bne :+
    lda StarInvincibleTimer
    bne :+
    rts
  :
ClassicPalette:
  lda GuestPowerupActive
  beq :+
    farcall GuestPowerupPalette
    rts
  :
  ldy #0
  lda PlayerStatus
  cmp #2
  bne :+
    iny
  :
  sty MmPaletteIndex
  lda StarInvincibleTimer
  beq Charge
    lda MmFlashPhase
    cmp #3
    bcc :+
      sbc #3
    :
    clc
    adc #14
    tay
    jmp Queue
Charge:
  lda MmChargeFrames
  cmp #33
  bcc Queue
  cmp #87
  bcs Full
  lda MmFlashPhase
  and #1
  beq Queue
  ldy #2
  lda MmChargeFrames
  cmp #48
  bcc Outline
  iny
  cmp #66
  bcc Outline
  iny
Outline:
  lda MmPaletteIndex
  beq Queue
  tya
  clc
  adc #3
  tay
  bne Queue
Full:
  lda MmFlashPhase
  cmp #3
  bcc :+
    sbc #3
  :
  clc
  adc #8
  ldx MmPaletteIndex
  beq :+
    adc #3
  :
  tay
Queue:
  ldx VRAM_Buffer1_Offset
  cpx #$40
  bcs Done
  tya
  clc
  adc #1
  cmp MmLastPalette
  beq Done
  sta MmLastPalette
  tya
  asl
  sta MmPaletteIndex
  tya
  clc
  adc MmPaletteIndex
  tay
  ldx VRAM_Buffer1_Offset
  lda #$3f
  sta VRAM_Buffer1,x
  lda #$11
  sta VRAM_Buffer1+1,x
  lda #3
  sta VRAM_Buffer1+2,x
  lda Colors,y
  sta VRAM_Buffer1+3,x
  lda Colors+1,y
  sta VRAM_Buffer1+4,x
  lda Colors+2,y
  sta VRAM_Buffer1+5,x
  txa
  clc
  adc #6
  tax
  stx VRAM_Buffer1_Offset
  lda #0
  sta VRAM_Buffer1,x
Done:
  rts
Colors:
  .byte $0f,$11,$2c, $0f,$16,$28
  .byte $06,$11,$2c, $15,$11,$2c, $25,$11,$2c
  .byte $06,$16,$28, $15,$16,$28, $25,$16,$28
  .byte $11,$2c,$0f, $2c,$0f,$11, $2c,$10,$11
  .byte $16,$28,$0f, $28,$0f,$16, $28,$10,$16
  .byte $06,$27,$38, $0a,$16,$30, $0c,$24,$34
.endproc
.popseg
