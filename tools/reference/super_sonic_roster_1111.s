.setcpu "6502"

.segment "NAME_GATE"
 php
 lda $6002
 cmp #43
 bne OriginalName
 lda $5ffe
 cmp #4
 lda #$58
 ldx #$a3
 bcc SonicName
 lda #<SuperSonicName
 ldx #>SuperSonicName
SonicName:
 plp
 ldy #$e1
 bne NamePublish
OriginalName:
 plp
 lda #$0e
 ldx #$a8
 ldy #$bf
NamePublish:
 jmp $acc6

.segment "SUPER_NAME"
SuperSonicName:
 ; The original leaf appends a complete 16-tile row and its terminator.
 ; Its final five spaces are also correct for this label.
 jsr $a358
 ldx $04ae
 ldy #10
SuperNameNext:
 lda SuperTitle,y
 sta $04a9,x
 dex
 dey
 bpl SuperNameNext
 rts

.segment "SUPER_TITLE"
SuperTitle:
 .byte $1c,$1e,$19,$0e,$1b,$24,$1c,$18,$17,$12,$0c

.segment "PORTRAIT"
 php
 cmp #43
 beq SonicPortrait
 plp
 ; PRG78:B8DD already supplies the outgoing FarCall A in $016a.
 lda #$28
 sta $016c
 lda #$a5
 sta $016d
 lda #$dd
 jmp $015a
SonicPortrait:
 lda #1
 sta $06e1
 sta $73ee
 sta $0146
 lda #$85
 sta $73e0
 lda $5ffe
 lsr
 lsr
 ora #$10
 sta $0147
 plp
 ora #0
 rts

.segment "PALETTE"
 pla
 plp
 ldx $04ae
 cpx #78
 bcs PaletteDone
 ldy #0
PaletteNext:
 lda PaletteData,y
 sta $04af,x
 inx
 iny
 cpy #7
 bne PaletteNext
 dex
 stx $04ae
 php
 pha
 lda $5ffe
 cmp #4
 bne PaletteReturn
 lda #$28
 sta $04ad,x
PaletteReturn:
 pla
 plp
PaletteDone:
 rts
PaletteData:
 .byte $3f,$11,3,$16,$12,$30,0

.segment "ACTIVE_PAGE"
 lda $5ffe
 lsr
 lsr
 ora #$10
 sta $0147
 rts
