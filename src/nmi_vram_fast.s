; NMI-only: bank116 is already owned by SamusFreezeUpdateScreen.
; Retain full native UpdateScreen results and ordered data/pointer wrap.
; Internal A/V are dead at the unchanged SEC/TYA/ADC continuation.
; No new RAM, foreground scratch, SMC, JSR or stack frame.
.pushseg
.segment "NMI_VRAM_FAST"
.proc FastNmiVramCopy
 bcs Repeat
 ; X=0 naturally follows the native256-byte literal tail.
 cpx #8
 bcc LiteralTail
Chunk:
 .repeat 8
  iny
  lda (NmiR0),y
  sta PPUDATA
 .endrepeat
 txa
 sec
 sbc #8
 tax
 cpx #8
 bcs Chunk
 cpx #0
 bne LiteralTail
 jmp OutputToVRAM+11
 nop ; unreachable: destination SEC replaces incoming C
LiteralTail:
 iny
 lda (NmiR0),y
 sta PPUDATA
 dex
 bne LiteralTail
LiteralDone:
 jmp OutputToVRAM+11
 nop ; unreachable: destination SEC replaces incoming C ; native SEC and pointer/next-command continuation
Repeat:
 lda (NmiR0),y
RepeatLoop:
 sta PPUDATA
 dex
 bne RepeatLoop
 jmp OutputToVRAM+11
 nop ; unreachable: destination SEC replaces incoming C
.endproc
 .res 3,$ea ; retain following genuine entry PCs
.proc FastNmiPaletteCapture
 .repeat 32,I
  lda PPUDATA
  sta PnBombPaletteShadow+I
 .endrepeat
 jmp FastNmiPaletteScrollRestore
 .res 4,$ea ; retain every existing private entry PC
.endproc
.popseg

; Capture necessarily changes t with PPUADDR3F00. Restore the native
; UpdateScreen coarse/fine scroll0. The following old MirrorPPUCTRL store
; restores its nametable bits; the regular NMI later applies its HUD AND#FC.
.pushseg
.segment "NMI_VRAM_SCROLL"
.proc FastNmiPaletteScrollRestore
 ldx #0
 stx PPUSCROLL
 stx PPUSCROLL
 ldx #32
 cpx #32
 jmp PnPaletteScreenUpdate::Copy+11
.endproc
.popseg
