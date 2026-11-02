.setcpu "6502"
.segment "START"
.export BubStartFlags,BubStartFlagsEnd
BubStartFlags:
 php
 txa
 pha
 tya
 pha
 jsr $b599
 ; Original savedX is two bytes above currentSP. Keep savedY on stack
 ; until the end so Y can index the immutable masks without extra saves.
 tsx
 lda $0102,x
 ldy #8
Search:
 cmp Slots,y
 beq Found
 dey
 bpl Search
 ldy #4
Found:
 lda Alts,y
 and $5fe5
 sta $5fe5
 lda Groups,y
 and $5fe8
 sta $5fe8
 pla
 tay
 pla
 tax
 plp
 lda #0
 rts
Slots:.byte 10,31,9,26,255,23,30,28,32
Alts:.byte $44,$80,$20,$08,0,0,0,0,0
Groups=Alts+4
 .byte $20,$18,7,$80
BubStartFlagsEnd:
 .res $4a-(*-BubStartFlags),$ea
