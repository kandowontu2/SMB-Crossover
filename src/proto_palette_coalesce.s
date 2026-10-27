.pushseg
.segment "PALETTE_COALESCE"
.proc CompactMegaManPaletteState

 ; Death's early Graphics return has no later pose farcall to replace the SMC
 ; target latch. Invoke the genuine old routine there to preserve every latch.
 ; EOR changes neither carry nor overflow; original code reloads A/NZ.
 lda GameEngineSubroutine
 eor #$0b
 bne Authentic
 lda SafecallA_SMC+1
 farcall MegaManPaletteState,tail
Authentic:
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
  jsr CompactMegaManPaletteTail
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

.pushseg
.segment "PALETTE_COALESCE"
; Foreground-only, after this source owner's complete3F11/3 append.
; The12-byte fastcase is two whole commands. General parsing is rare>=48.
; No NMI work/newRAM. Unknown formats or intervening overlaps decline folding.
.proc CompactMegaManPaletteTail
 cpx #12
 beq TwoCommands
 cpx #48
 bcs Scan
Done:
 lda #0
 clc
 rts
TwoCommands:
 lda VRAM_Buffer1
 cmp #$3f
 bne Done
 lda VRAM_Buffer1+1
 cmp #$11
 bne Done
 lda VRAM_Buffer1+2
 cmp #3
 bne Done
 lda VRAM_Buffer1+9
 sta VRAM_Buffer1+3
 lda VRAM_Buffer1+10
 sta VRAM_Buffer1+4
 lda VRAM_Buffer1+11
 sta VRAM_Buffer1+5
 lda #6
 sta VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1+6
 clc
 rts
Scan:
 php
 phx
 phy
 lda R0
 pha
 lda R1
 pha
 lda R2
 pha
 txa
 sec
 sbc #6
 sta R1                      ; End of old commands/current append's beginning.
 lda #$ff
 sta R0                      ; Last eligible complete3F11/3 command.
 ldx #0
Loop:
 cpx R1
 jeq Scanned
 jcs Restore
 lda VRAM_Buffer1,x
 jeq Restore                 ; Premature terminator/incomplete prefix.
 lda VRAM_Buffer1+2,x
 jeq Restore                 ; Native0=256; unknown long transfer declines.
 cmp #64
 jcs Restore                 ; RLE/vertical, including every alias: unchanged.
 clc
 adc #3
 sta R2
 txa
 adc R2
 jcs Restore
 cmp R1
 beq Bounded
 jcs Restore
Bounded:
 sta R2                      ; Next complete command, never a payload pattern.
 lda VRAM_Buffer1,x
 cmp #$40
 jcs Restore                 ; High address aliases decline, never guessed.
 cmp #$3f
 beq Palette
 cmp #$3e
 bne Advance
 lda VRAM_Buffer1+1,x
 clc
 adc VRAM_Buffer1+2,x
 bcs Restore                 ; Could enter palette RAM at3F00.
 jmp Advance
Palette:
 lda VRAM_Buffer1+1,x
 cmp #$11
 bne OtherPalette
 lda VRAM_Buffer1+2,x
 cmp #3
 bne OtherPalette
 stx R0
 jmp Advance
OtherPalette:
 lda VRAM_Buffer1+1,x
 and #31
 ldy VRAM_Buffer1+2,x
Overlap:
 cmp #$11
 bcc NextAddress
 cmp #$14
 bcs NextAddress
 lda #$ff
 sta R0                      ; Partial/full/mirrored writes break eligibility.
 jmp Advance
NextAddress:
 clc
 adc #1
 and #31
 dey
 bne Overlap
Advance:
 ldx R2
 jmp Loop
Scanned:
 ldy R0
 cpy #$ff
 beq Restore
 ; Remove the earlier complete6B command, retaining newest3F11 last.
 ; This also preserves the genuine pose parser's finalA/SafereturnA SMC.
 ; Forward memmove is safe: every source index is destination+6.
 tya
 clc
 adc #6
 tax
Move:
 lda VRAM_Buffer1,x
 sta VRAM_Buffer1,y
 inx
 iny
 cpx VRAM_Buffer1_Offset
 bcc Move
 lda #0
 sta VRAM_Buffer1,y
 sty VRAM_Buffer1_Offset
Restore:
 pla
 sta R2
 pla
 sta R1
 pla
 sta R0
 ply
 plx
 plp
 lda #0
 clc
 rts
.endproc

.assert * <= $bf00,error,"Declared B800..BEFF cold owner"
.popseg
