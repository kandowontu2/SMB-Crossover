; Exact native Little Mac probe bodies, copied without mechanical edits.
.proc TnMacHeadProbe
 sty LmSavedY
 lda Player_Y_Position
 sta LmOldY
 lda Player_X_Position
 sta LmOldX
 lda Player_PageLoc
 sta LmOldPage
 lda LmOldY
 sec
 sbc #18
 ldx RgCrouch
 beq :+
 clc
 adc #16
:sta Player_Y_Position
 clc
 adc #4
 cmp #32
 bcs :+
 lda #0
 sta R3
 jmp Sampled
:jsr BlockBufferColli_Head
 bne Sampled
 lda Player_Y_Speed
 bpl Sampled
 lda LmOldX
 sec
 sbc #6
 sta Player_X_Position
 lda LmOldPage
 sbc #0
 sta Player_PageLoc
 ldy LmSavedY
 jsr BlockBufferColli_Head
 bne Sampled
 lda LmOldX
 clc
 adc #6
 sta Player_X_Position
 lda LmOldPage
 adc #0
 sta Player_PageLoc
 ldy LmSavedY
 jsr BlockBufferColli_Head
Sampled:pha
 lda LmOldX
 sta Player_X_Position
 lda LmOldPage
 sta Player_PageLoc
 lda LmOldY
 sta Player_Y_Position
 pla
 pha
 beq Finish
 ldx Player_Y_Speed
 bpl Finish
 phy
 ldy R3
 lda MTileAttribute,y
 and #MTILE_SOLID|MTILE_CLIMB
 cmp #MTILE_SOLID
 bne EndY
 lda R2
 clc
 adc #62
 ldx RgCrouch
 beq :+
 sec
 sbc #16
:sta Player_Y_Position
 and #15
 sta R4
 lda #0
 sta MarioJumpRise
 sta MarioJumpFraction
 sta MarioJumpFraction+1
 sta MmYFraction
 sta MmYFraction+1
EndY:ply
Finish:pla
 rts
.endproc
.export TnMacHeadProbe
.proc TnMacSideProbe
 lda GameEngineSubroutine
 cmp #8
 beq Gameplay
 jmp BlockBufferColli_Side
Gameplay:sty LmSavedY
 lda R0
 sta LmSavedR0
 lda Local_eb
 sta LmSavedEb
 lda Player_X_Position
 sta LmOldX
 lda Player_PageLoc
 sta LmOldPage
 lda Player_Y_Position
 sta LmOldY
 ldy LmSavedY
 cpy #5
 bcs Right
 lda #2
 ldx RgCrouch
 beq :+
 lda #7
:sta LmTemp
 lda LmOldX
 sec
 sbc LmTemp
 sta Player_X_Position
 lda LmOldPage
 sbc #0
 sta Player_PageLoc
 jmp Probe
Right:lda #2
 ldx RgCrouch
 beq :+
 lda #7
:clc
 adc LmOldX
 sta Player_X_Position
 lda LmOldPage
 adc #0
 sta Player_PageLoc
Probe:
 lda LmSavedY
 and #1
 beq Lower
 lda RgCrouch
 bne Duck
 lda #0
 sta LmProbe
Loop:ldy LmProbe
 lda Offsets,y
 clc
 adc LmOldY
 sta Player_Y_Position
 ldy LmSavedY
::TnMacVisibleSideCall:
 jsr TnMacVisibleSideProbe
 bne Restore
 inc LmProbe
 lda LmProbe
 cmp #3
 bcc Loop
 lda R3
 jmp Restore
Duck:lda LmOldY
 clc
 adc #14
 sta Player_Y_Position
Lower:ldy LmSavedY
::TnMacVisibleLowerCall:
 jsr TnMacVisibleSideProbe
Restore:pha
 lda LmOldX
 sta Player_X_Position
 lda LmOldPage
 sta Player_PageLoc
 lda LmOldY
 sta Player_Y_Position
 lda LmSavedR0
 sta R0
 lda LmSavedEb
 sta Local_eb
 pla
 rts
Offsets:.byte $ec,$f8,4 ; native upper sideadder8 -> actualY−12,0,+12
.endproc
.export TnMacSideProbe
; Private side probe: the source body can extend into the HUD. Never
; wrap those samples into unrelated block-buffer rows below the playfield.
.proc TnMacVisibleSideProbe
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
.export TnMacVisibleSideProbe
