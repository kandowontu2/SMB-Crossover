; Ordinary Peach float from Infidelity SMB3+:
; 31:B6F0/B662/B5ED/BC4D, 30:BAC0/B9F3, 32:A003.
; Single active player uses the original P1 controller; native SMB terrain
; remains the host's responsibility after movement. Kuribo is disabled by
; the existing host, and the donor ground-pound extension is still unjoined.
MbFloatExpired=$5c64
MbFloatTimer=$5c65
MbFloatAnchor=$5c66
MbFloatReady=$5c67

.proc MbPeachVelocityEnd
 sta M3Native::Player_XHi,x ; Original final integrator write.
 php
 pha
 lda M3Variant
 cmp #3
 bne Done
 lda M3Native::Player_InAir
 beq Reset
 lda M3Native::Player_InWater
 ora M3Native::Player_Kuribo
 bne Reset
 lda MbFloatReady
 bne Check
 lda M3Form
 cmp #3
 bpl Check
 lda #1
 sta MbFloatReady
 lda M3Native::Player_Y
 sta MbFloatAnchor
Check:jmp MbPeachFloatCheck
Reset:jsr MbPeachFloatClear
Done:jmp MbPeachFloatReturn
.endproc

.proc MbPeachFloatCheck
 lda MbFloatReady
 cmp #2
 beq Active
 lda MbFloatExpired
 cmp #1
 beq Clear
 lda MbFloatReady
 cmp #1
 bne Done
Clear:
 lda #0
 sta MbFloatTimer
Done:jmp MbPeachFloatReturn
Active:
 lda M3Form
 cmp #4
 bpl Done
 lda MbFloatExpired
 bne Done
 jmp MbPeachFloatActive
.endproc

.proc MbPeachFloatActive
 lda M3Native::Pad_Holding
 and #$80
 beq End
 lda #0
 sta M3Native::Player_YVel
 inc MbFloatTimer
 lda M3Native::Player_Frame
 cmp #$2c
 bne Count
 lda #0
 sta MbFloatReady
Count:
 lda MbFloatTimer
 cmp #$a0
 beq End
 jsr MbPeachFloatWobble
 jmp MbPeachFloatReturn
End:jmp MbPeachFloatExpire
.endproc

.proc MbPeachFloatExpire
 lda #1
 sta MbFloatExpired
 sta MbFloatReady
 jmp MbPeachFloatReturn
.endproc

.proc MbPeachFloatClear
 lda #0
 sta MbFloatExpired
 sta MbFloatTimer
 sta MbFloatAnchor
 sta MbFloatReady
 rts
.endproc

.proc MbPeachFloatReturn
 pla
 plp
 rts
.endproc

.proc MbPeachJumpRoot
 lda M3Variant
 cmp #3
 bne Root
 lda M3Form
 cmp #4
 bpl Root
 lda MbFloatReady
 cmp #2
 beq Store
 inc MbFloatReady
Store:
 lda M3Native::Player_Y
 sta MbFloatAnchor
Root:
 lda M3Native::Player_RootJumpVel
 rts
.endproc

.proc MbPeachAfterJump
 jsr M3Native::Player_JumpFlyFlutter
 php
 pha
 lda M3Variant
 cmp #3
 bne Done
 lda M3Form
 cmp #4
 bpl Done
 lda MbFloatReady
 cmp #2
 beq Maintain
 lda M3Native::Pad_Holding
 and #$80
 beq Override
 lda M3Native::Player_YVel
 bmi Override
 lda MbFloatExpired
 bne Override
Maintain:
 lda M3Native::Player_SandSink
 bne Sink
 lda #2
 sta MbFloatReady
Override:
 lda MbFloatReady
 cmp #2
 bne Done
 lda MbFloatExpired
 bne Done
 lda #$ff
 sta M3Native::Player_YVel
Done:jmp MbPeachFloatReturn
Sink:
 jsr MbPeachFloatSink
 jmp Override
.endproc

.proc MbPeachFloatSink
 lda #0
 sta MbFloatExpired
 sta MbFloatAnchor
 sta MbFloatReady
 rts
.endproc

; The original64-byte table has only six nonzero entries. This exact
; factorization is checked for every timer value before integration.
.proc MbPeachFloatWobble
 lda MbFloatTimer
 and #$1f
 cmp #7
 beq Two
 and #$0f
 beq One
 rts
Two:lda #2
 bne Sign
One:lda #1
Sign:
 pha
 lda MbFloatTimer
 and #$20
 bne Positive
 pla
 eor #$ff
 clc
 adc #1
 jmp MbPeachFloatApply
Positive:
 pla
 jmp MbPeachFloatApply
.endproc

.proc MbPeachFloatApply
 bpl Add
 dec M3Native::Player_YHi
Add:
 clc
 adc M3Native::Player_Y
 sta M3Native::Player_Y
 bcc Done
 inc M3Native::Player_YHi
Done:rts
.endproc
