; CV3-only ceiling separation after a real upward head crossing.
.pushseg
.segment "TMNT_COMBAT"
.proc TnCv3HeadGate
 cmp #CHARACTER_SIMON
 bne Legacy
 lda Cv3Variant
 beq Legacy
 pla
 plp
 jsr BlockBufferColli_Head
 php
 pha
 beq Done
 cmp #$26
 beq Done
 cmp #$c2
 beq Done
 cmp #$c3
 beq Done
 lda GameEngineSubroutine
 cmp #8
 bne Done
 lda Player_Y_HighPos
 cmp #1
 bne Done
 lda Player_Y_Speed
 bpl Done
 lda R4
 cmp #4
 bcc Done
 ldx R3
 lda MTileAttribute,x
 and #MTILE_CLIMB
 bne Done
 ; The CV3 integrator publishes Q8.8 velocity in the shared Q8.16 fields.
 ; A ceiling must have crossed the previous head, rather than already
 ; overlapping its side. Separate before SMB's later side queries: those
 ; otherwise mistake the head-hit block for a wall and move X by15 pixels.
 sec
 lda MmYFraction+1
 sbc MmVY+1
 lda Player_Y_Position
 sbc MmVY+2
 cmp Player_Y_Position
 bcc Done
 ldx Local_eb
 clc
 adc BlockBuffer_Y_Adder,x
 bcs Done
 sta Cv3Temp
 lda R2
 clc
 adc #48
 bcs Done
 cmp Cv3Temp
 bcc Separate
 bne Done
Separate:
 sec
 sbc BlockBuffer_Y_Adder,x
 sta Player_Y_Position
 lda #0
 sta MmYFraction
 sta MmYFraction+1
Done:
 ldx #0
 pla
 plp
 rts
Legacy:
 pla
 plp
 farcall JnHeadDispatch,jmp
.endproc
.export TnCv3HeadGate
.popseg
