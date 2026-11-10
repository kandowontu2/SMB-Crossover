; Experimental Prince native BG admission. An animation sole can remain
; inside a real floor between source physics phases. Query the actual native
; feet and top of that cell: only a solid cell with empty space directly above
; is a floor. Require the original logical support anchor exactly on that top
; or its already authenticated typed-support one-pixel offset. Preserve the
; physical source/render/body foot and all donor state.
.setcpu "6502"
.segment "NATIVE_FOOT"
PpNativeFootMotion:
 php
 pha
 lda $c085
 bne Done
 lda $c084
 cmp #32
 bcc Done
 ldy #2
Foot:
 tya
 clc
 adc Player_X_Position
 sta $b369
 lda Player_PageLoc
 adc #0
 sta $b36a
 lda $c084
 and #$f0
 sta $b36b
 lda $c084
 sec
 sbc $c088
 clc
 adc #3
 sec
 sbc $b36b
 cmp #2
 bcs Done
 lda #0
 sta $b36c
 jsr $b310
 bcc Next
 dec $b36b
 jsr $b310
 bcs Next
 lda $b36b
 sec
 sbc #31
 sta Player_Y_Position
 lda #1
 sta Player_Y_HighPos
 jmp Done
Next:
 cpy #14
 beq Done
 ldy #14
 bne Foot
Done:
 pla
 plp
 ldy #6
 sec
 rts
