; CV3 lives are a byte: native INC grants a life; native DEC loses one.
; Enter only on a changed count, with A=current. Active native gains between
; Ensure calls are bounded to fewer than128 INCs (six popup slots + coins).
; Signed modulo difference supports simultaneous gains and FF->00 rollover;
; native DEC losses, including00->FF, stay negative. Preserve original V/D/I.
; Keep the unchanged-life movement path and every old PC byte-for-byte.
.pushseg
.segment "CV3_GRIP"
.proc Cv3LifeChanged
 php
 sec
 sbc Cv3LastLife
 bmi Loss
 plp
 lda NumberofLives
 sta Cv3LastLife
 jmp Cv3Ensure::CheckArea
Loss:
 plp
 jmp Cv3Ensure::Life
.endproc
.popseg
