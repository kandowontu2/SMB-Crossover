; Replace only the live Mini preview's name fragment and palette publisher.
; The normal Mario preview supplies the three spaces on either side, as well
; as the final body color $18. The current menu compactor admits a four-byte
; palette packet only at $3F10. Its length and palette page guard these stores
; before changing the two colors in that packet's payload.
.setcpu "6502"

.segment "MINI_NAME"
    ldy #10
    lda MiniName-1,y
    sta VRAM_Buffer1+6,x

.segment "MINI_CHECK"
    ldx VRAM_Buffer1+2
    jmp MiniPalette

.segment "MINI_PALETTE"
MiniName:
    .byte $18,$12,$1b,$0a,$16,$24,$12,$17,$12,$16
MiniPalette:
    cpx #4
    bne MapPortrait
    lda VRAM_Buffer1
    cmp #$3f
    bne MapPortrait
    lda #$27
    sta VRAM_Buffer1+4
    lda #$16
    sta VRAM_Buffer1+5
MapPortrait:
    lda #$c8
    jmp $b0b2
