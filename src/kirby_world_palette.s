.pushseg
.segment "KIRBY_CORE"
.proc KbWorldPaletteIndex
  php
  ldy #0
  lda SelectedCharacter
  beq Mario
  cmp #CHARACTER_KIRBY
  beq Mario
  cmp #14
  beq Mario
  cmp #15
  beq Mario
  cmp #CHARACTER_MIKE
  beq Mario
  cmp #CHARACTER_TMNT
  beq Mario
  cmp #18
  beq Mario
  cmp #17
  beq Mario
  cmp #CHARACTER_RYGAR
  bne Guest
  jsr NativeIndex
Guest:
  plp                           ; Preserve the old guest entry C/V/I/D.
  rts
Mario:
  plp
NativeIndex:
  lda AreaType
  asl
  sta R0
  asl
  clc
  adc R0
  adc #6
  tay
  rts
.endproc
.popseg
