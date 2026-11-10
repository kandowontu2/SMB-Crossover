; Derivative of frozen5174. All original physical-foot successes stay first.
; D297 for actions1/42 is reached only after original WorldRow (not Adjusted).
; On original phase3 the previous-Main sole and current sole use the same
; projection Delta. Only careful42 may substitute their equal logical anchor.
.setcpu "6502"
.segment "SUPPORT"
PpLogicalCarefulSupport:
 jsr $bde2
 bne Done
 php
 lda $c616
 cmp #1
 beq ActionMode
 cmp #42
 bne Empty
ActionMode:
 lda $c618
 clc
 adc #1
 and #$fd
 bne Empty
 lda $00a4
 sec
 sbc #1
 ora $c085
 ora $c087
 ora $001e
 bne Empty
 lda $00bd
 adc #32
 bcs Empty
 cmp $c084
 bne Logical
 lda $c084
 cmp $c086
 beq Prepared
Logical:
 jsr LogicalSupport
 bne Empty
Prepared:
 sbc #1
 sta $b36b
 lda #0
 sta $b36c
 lda $c615
 and #11
 adc #1
 adc $0075
 sta $b369
 lda $005c
 adc #0
 sta $b36a
 jsr $b310
 bcc Empty
 and #$fc
 cmp #$10
 bne Empty
 dec $b36b
 jsr $b310
 bcs Empty
 ; PointRead's C0 contract is A0. Preserve the old exact surface values.
 sta $c080
 lda $b36b
 adc #1
 sta $c07f
 plp
 lda #1
 rts
Empty:
 plp
 lda #0
Done:
 rts

.segment "PROJECTION"
PpReadProjection:
 jsr $bcf4
 pha
 ; Signed7: ASL removes the width bit; CMP copies sign into ROR's carry.
 asl a
 cmp #$80
 ror a
 sta $c088
 clc
 adc $c611
 sta $c6f1
 lda $c088
 sec
 sbc #3
 sta $c4bc
 bpl Height
 eor #$ff
Height:
 asl a
 asl a
 sta $c4c3
 pla
 asl a
 lda $bda2
 ; Carry is width bit2, then original Header bits7/6 become bits1/0.
 rol a
 rol a
 rol a
 and #7
 asl a
 asl a
 asl a
 ; The preceding shifts of 0..7 prove C0.
 adc #8
 sta $c70f
 rts
LogicalSupport:
 lda $c616
 cmp #42
 bne LogicalDone
 lda $d4a6
 ora $c09c
 bne LogicalDone
 lda $c084
 cmp $d4b1
 bne LogicalDone
 lda $00bd
 sec
 adc #32
 cmp $c09b
LogicalDone:
 rts
