; Immediate numeric updates, coalescing only a whole final coin+score pair.
.pushseg
.segment "HUD_TAIL_COLD"
.proc HudUpdateNumberLocal
  pha
  cmp #$02
  beq CheckTail
  cmp #$13
  bne Print
CheckTail:
  jsr ReuseTail
Print:
  pla
  jsr HudPrintStatusNumbersLocal
  ldy VRAM_Buffer1_Offset
  lda VRAM_Buffer1-6,y
  bne NoZSup
  lda #$24
  sta VRAM_Buffer1-6,y
NoZSup:
  ldx ObjectOffset
  rts
ReuseTail:
  ldy VRAM_Buffer1_Offset
  cpy #14
  bcc Done
  cpy #85
  bcs Done
  lda VRAM_Buffer1,y
  bne Done
  lda VRAM_Buffer1-14,y
  cmp #$20
  bne Done
  lda VRAM_Buffer1-13,y
  cmp #$6d
  bne Done
  lda VRAM_Buffer1-12,y
  cmp #2
  bne Done
  lda VRAM_Buffer1-9,y
  cmp #$20
  bne Done
  lda VRAM_Buffer1-8,y
  cmp #$62
  bne Done
  lda VRAM_Buffer1-7,y
  cmp #6
  bne Done
  tya
  sec
  sbc #14
  sta R3
  ldx #0
Packet:
  cpx R3
  beq Reuse
  bcs Done
  lda VRAM_Buffer1,x
  beq Done
  ; The target is <=70. X<target, so reading X+2 stays within the
  ; 85-byte queue even for a truncated foreign header. Every packet
  ; advances at least4 bytes. Reject overshoot at Packet; no additional
  ; header/end comparison or 8-bit overflow check is required (sum<=135).
  lda VRAM_Buffer1+2,x
  and #$3f
  beq Done
  sta R2
  lda VRAM_Buffer1+2,x
  and #$40
  beq CountReady
  lda #1
  sta R2
CountReady:
  txa
  clc
  adc #3
  adc R2
  tax
  jmp Packet
Reuse:
  stx VRAM_Buffer1_Offset
Done:
  rts
.endproc
.popseg
