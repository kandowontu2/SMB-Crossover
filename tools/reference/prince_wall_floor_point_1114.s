; Unallocated primitive proposal. This is NOT a drop-in PointRead ABI.
; The three WorldMaterial callers consume C, reload A, and the enclosing
; routine restores its saved X/Y/P. Private A/X/V/N/Z may be clobbered.
.setcpu "6502"
.segment "WALL_FLOOR"
WallBodyPoint:
 jsr $a49a                    ; Preserve delivered Hand/flag25 filtering.
 bcc Done
 jmp InsideBody
FloorBodyPoint:
 jsr $b310
 bcc Done
 jsr InsideBody
 bcs Done
 ; Keep donor foot-cell admission even outside the physical body when
 ; this native tile has an exposed roof. Reject a higher solid column.
 lda $b36d
 pha
 lda $b36b
 pha
 and #$f0
 sec
 sbc #1
 sta $b36b
PeekRoof:
 jsr $b310
 pla
 sta $b36b
 pla
 sta $b36d
 bcs Clear
 sec
Done:
 rts
Clear:
 clc
 rts
InsideBody:
 lda $c07c
 eor $c083
 bne Done                     ; Original solid C remains1 off current row.
 lda $b369
 and #$f0
 clc
 adc #8
 sec
 sbc $c60f                    ; Source position is current before export.
 tax
 lda $b36a
 sbc $c610
 beq Positive
 cmp #$ff
 bne Clear
 cpx #$f1                     ; Negative distance -15..-1 admits.
 rts
Positive:
 txa
 eor #$ff
 cmp #$f0                     ; Positive distance0..15 admits.
 rts
