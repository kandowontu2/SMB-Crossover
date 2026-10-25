; Private side probe: the source body can extend into the HUD. Never
; wrap those samples into unrelated block-buffer rows below the playfield.
.proc MAC_VISIBLE_NAME
 php
 pha
 lda Player_Y_Position
 clc
 adc BlockBuffer_Y_Adder,y
 cmp #32
 bcc Empty
 cmp #240
 bcs Empty
 pla
 plp
 jmp BlockBufferColli_Side
Empty:
 pla
 plp
 lda #0
 sta R3
 rts
.endproc
.export MAC_VISIBLE_NAME
