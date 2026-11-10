; Four-state existing family byte; no new RAM, pattern pages or code grant.
.setcpu "6502"
.segment "RESOLVE"
.export SonicCursorHi,SonicFamilyResolve
SonicCursorHi:
 php
 tya
 lsr
 lsr
 lsr
 clc
 adc #1
 lsr
 ; Result0..16 has bit5 clear; saved P restores the temporary carry.
 ora #$20
 plp
 ora #0
 rts
SonicFamilyResolve:
 lda $a040,x
 php
 cpx #0
 bne Old
 lda $730a
 cmp #8
 bne Mario
 lda #41
 bne Done
Mario:
 lda #0
 beq Done
Old:
 cpx #25
 bne Arthur
 lda $5ffe
 beq Gimmick
 jsr SonicFamilyID
 bne Done
Gimmick:
 lda #26
 bne Done
Arthur:
 cpx #31
 bne Done
 bit $5fe5
 bpl Done
 lda #24
Done:
 plp
 rts

.segment "TAIL"
.export SonicFamilyCold,SonicFamilyID
SonicFamilyCold:
 lda #0
 sta $5ffe
 sta $5fe5
 sta $5fe8
 jmp $a9d0
SonicFamilyID:
 cmp #3
 lda #39
 bcc Return
 lda #43
Return:
 rts

.segment "PENDING"
.export SonicFamilyPending
SonicFamilyPending:
 ldx $7309
 cpx #25
 bne Foreign
 lda $5ffe
 beq Foreign
 cmp #3
 beq Native
 ; Preserve the existing Bob80 contract, including foreign flag states.
 lda #14
 bit $5fe8
 bmi Pending
 lda #9
Pending:
 sec
 rts
Native:
 clc
 rts
Foreign:
 jmp $b97c

.segment "NAME"
.export SonicFamilyNameGate
SonicFamilyNameGate:
 php
 lda $6002
 cmp #43
 bne Original
 lda #0
 sta $016a
 plp
 lda #$58
 ldx #$a3
 ldy #$e1
 bne Publish
Original:
 plp
 lda #$0e
 ldx #$a8
 ldy #$bf
Publish:
 jmp $acc6

.segment "COLORS"
.export SonicFamilyColors
SonicFamilyColors:
 sta $016a
 lda #$3d
 sta $016c
 lda #$a0
 sta $016d
 lda #$ce
 jsr $015a
 php
 pha
 txa
 pha
 tya
 pha
 lda $6002
 beq ColorMario
 cmp #43
 bne ColorsPop
 ldy #6
 bne ColorsCopy
ColorMario:
 lda $730a
 ldy #0
 cmp #5
 beq ColorsCopy
 cmp #6
 bne ColorsPop
ColorsCopy:
 ldx $04ae
 lda #2
 sta $03
ColorsLoop:
 lda Palette,y
 sta $04ac,x
 inx
 iny
 dec $03
 bpl ColorsLoop
ColorsPop:
 pla
 tay
 pla
 tax
 pla
 plp
 rts
Palette:
 .byte $16,$30,$27,$16,$30,$27,$16,$12,$30
