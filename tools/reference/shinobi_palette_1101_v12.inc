; Cold-safe player palette callback. Source visible P0 colors, native backdrop.
.export ShColors
.segment "SHINOBI_RESIDENT"
ShColors:
 php
 pha
 txa
 pha
 tya
 pha
 lda SelectedCharacter
 cmp #36
 bne ShColorsReject
 ldx VRAM_Buffer1_Offset
 cpx #$39
 bcs ShColorsHandled
 ldy #0
ShColorCopy:
 lda ShColorPacket,y
 sta VRAM_Buffer1,x
 inx
 iny
 cpy #7
 bne ShColorCopy
 ldy BackgroundColorCtrl
 bne ShColorBackdrop
 ldy AreaType
ShColorBackdrop:
 lda ShBackgroundColors,y
 sta VRAM_Buffer1-4,x
 lda #0
 sta VRAM_Buffer1,x
 stx VRAM_Buffer1_Offset
ShColorsHandled:
 tsx
 lda $0104,x
 ora #1
 bne ShColorFlags
ShColorsReject:
 tsx
 lda $0104,x
 and #$fe
ShColorFlags:
 sta $0104,x
 pla
 tay
 pla
 tax
 pla
 plp
 rts
ShColorPacket: .byte $3f,$10,4,0,$0f,$36,$1c
