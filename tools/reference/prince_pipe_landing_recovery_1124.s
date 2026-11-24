; Retain the falling-pose cap sweep during the original landing recovery.
; A recovery frame can project the foot below the pipe after contact.
 lda $c616
 cmp #49
 beq Sweep
 cmp #7
 bne Original
 lda $c618
 sec
 sbc #3
 cmp #2
 bcs Original
Sweep:
 lda $c085
 ora $c087
 bne Original
 sta $b36c
 lda $c086
 cmp #32
 bcc Original
 adc #14
 bcs Original
 and #$f0
 cmp $c084
 bcs Original
 sta $b36b
 lda $c60f
 sta $b369
 lda $c610
 sta $b36a
Probe:
 jsr $b310
 bcc NextRow
 and #$fc
 cmp #$10
 bne Original
 dec $b36b
 jsr $b310
 bcs Original
 lda $b36b
 sbc #$1e
 sta Player_Y_Position
Original:
 sec
 lda $c084
 jmp $bd45
NextRow:
 lda $b36b
 adc #16
 bcs Original
 sta $b36b
 cmp $c084
 bcc Probe
 bcs Original
