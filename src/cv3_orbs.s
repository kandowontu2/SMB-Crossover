; Source lightning B0AC/B195/B208/B259/B2BB/B30A. Actor admission is the
; explicit six-slot SMB mapping; ratio quantization/vectors/turning use the
; original USA32-direction arithmetic and source-authenticated constants.
.pushseg
.segment "CV3_COMBAT"
.proc Cv3OrbUpdate
 lda Cv3ShotTarget,x
 jne Turn
 lda Cv3OrbRetarget,x
 jeq Aim
 dec Cv3OrbRetarget,x
 jmp Vector
Aim:
 lda #16
 sta Cv3OrbRetarget,x
 ldy #0
Find:
 sty Cv3HitSlot
 phx
 tya
 tax
 jsr Cv3Eligible
 plx
 jcc Next
 ldy Cv3HitSlot
 lda Enemy_X_Position,y
 clc
 adc #8
 sta R0
 lda Enemy_PageLoc,y
 adc #0
 sta R1
 lda R0
 sec
 sbc Cv3ShotX,x
 sta Cv3Temp
 lda R1
 sbc Cv3ShotPage,x
 jeq Positive
 cmp #$ff
 jne Next
 lda Cv3Temp
 eor #$ff
 clc
 adc #1
 sta Cv3Temp
 lda #2
 jne Quad
Positive:lda #0
Quad:sta Cv3Temp3
 lda Cv3Temp
 cmp #64
 jcs Next
 lda Enemy_Y_Position,y
 clc
 adc #16
 sec
 sbc Cv3ShotY,x
 jcs PositiveY
 eor #$ff
 clc
 adc #1
 inc Cv3Temp3
PositiveY:
 cmp #128
 jcs Next
 sta Cv3Temp2
 jsr Cv3OrbAimAngle
 sta Cv3OrbDesired,x
 lda #1
 sta Cv3ShotTarget,x
 jmp Turn
Next:
 ldy Cv3HitSlot
 iny
 cpy #6
 jcc Find
 lda Cv3OrbAngle,x
 sta Cv3OrbDesired,x
Turn:
::Cv3OrbTurnLeaf:
 dec Cv3OrbTurn,x
 jne Vector
 lda #2
 sta Cv3OrbTurn,x
 lda Cv3OrbDesired,x
 sec
 sbc Cv3OrbAngle,x
 jeq Aligned
 jcs PositiveDifference
 cmp #$f0
 jcs Reverse
 jmp Advance
PositiveDifference:
 cmp #17
 jcs Reverse
Advance:
 inc Cv3OrbAngle,x
 lda Cv3OrbAngle,x
 and #31
 sta Cv3OrbAngle,x
 jmp Reached
Reverse:
 dec Cv3OrbAngle,x
 lda Cv3OrbAngle,x
 and #31
 sta Cv3OrbAngle,x
Reached:
 cmp Cv3OrbDesired,x
 jne Vector
Aligned:
 lda #0
 sta Cv3ShotTarget,x
 lda #16
 sta Cv3OrbRetarget,x
Vector:
::Cv3OrbVector:
 ldy Cv3OrbAngle,x
 lda Cv3OrbXLo,y
 sta Cv3ShotVXLo,x
 lda Cv3OrbXHi,y
 sta Cv3ShotVXHi,x
 lda Cv3OrbYLo,y
 sta Cv3ShotVYLo,x
 lda Cv3OrbYHi,y
 sta Cv3ShotVYHi,x
 rts
.endproc
; Source exact ratio andoctant leaf: Temp=absDX,Temp2=absDY,Temp3=quadrant.
; X preserved, R0..R5 and Y volatile. Return original angle0..31.
.proc Cv3OrbAimAngle
 lda Cv3Temp2
 sta R1
 lda #0
 sta R0
 ldy #0
 lda Cv3Temp
 jsr Divide
 ldy #0
Threshold:
 lda R1
 cmp Cv3OrbThreshold,y
 jcc Found
 jne Advance
 lda R0
 cmp Cv3OrbThreshold+1,y
 jcc Found
 jeq Found
Advance:iny
 iny
 cpy #16
 jcc Threshold
Found:tya
 lsr
 sta R0
 ldy Cv3Temp3
 jeq Return
 dey
 jeq UpperRight
 dey
 jeq LowerLeft
 clc
 adc #16
 jne Return
LowerLeft:lda #16
 jne Subtract
UpperRight:lda #32
Subtract:sec
 sbc R0
Return:and #31
 rts
; Original AE0D division, preserving its zero-denominator behavior.
Divide:
 sta R2
 sty R3
 lda #0
 sta R4
 sta R5
 ldy #16
Loop:
 asl R0
 rol R1
 rol R4
 rol R5
 lda R5
 cmp R3
 jne Low
 lda R4
 cmp R2
Low:bcc Next
 lda R4
 sbc R2
 sta R4
 lda R5
 sbc R3
 sta R5
 inc R0
Next:dey
 jne Loop
 rts
.endproc
.popseg
