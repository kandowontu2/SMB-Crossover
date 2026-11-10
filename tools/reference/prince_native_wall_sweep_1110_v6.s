; Local Prince native BG prepass. No donor actor/action/sole/health stores.
; Full pre-export native X/Page comes from owned C0A7/A8; native side effects
; and wall response execute through the unchanged ordinary native BG caller.
.setcpu "6502"
.segment "BOUNDS"
Bounds:
 lda $b369
 ora #15
 cmp ScreenLeft_X_Pos
 lda $b36a
 sbc ScreenLeft_PageLoc
 rts
.segment "ENTRY"
PpNativeWallSweep:
 php
 pha
 jmp Begin
.segment "CORE"
Cell:
 lda Player_Y_Position
 clc
 adc #8
 sta $b36b
 jsr Probe
 bcs Found
 lda $b36b
 adc #16
 sta $b36b
 jsr Probe
 bcs Found
 lda $b369
EndLowOp:
 eor #0
 bne Advance
 lda $b36a
EndHighOp:
 eor #0
 beq Done
Advance:
 ; Empty Probe returned C0; LDA/EOR/branches above retain it.
 lda $b369
StepLowOp:
 adc #16
 sta $b369
 lda $b36a
StepHighOp:
 adc #0
 sta $b36a
 jmp Cell
Found:
 beq Done
 ; The BCS admission above already proves C1 for the real wall.
 lda $b369
SubtractEdgeOp:
 sbc #14
 sta Player_X_Position
 lda $b36a
 sbc #0
 sta Player_PageLoc
Done:
 pla
 plp
 ldy #6
 sec
 rts
Begin:
 lda GameEngineSubroutine
 cmp #8
 bne Done
 jsr $d53e
 lda GamePauseStatus
 lsr a
 bcs Done
 lda $c0aa
 beq Done
 lda FrameCounter
 cmp $c0a9
 bne Done
 lda Player_Y_Position
 cmp #32
 bcc Done
 lda Player_OffscreenBits
 and #15
 bne Done
 lda Player_PageLoc
 cmp $c0a8
 bne Direction
 lda Player_X_Position
 cmp $c0a7
 beq Done
Direction:
 lda #0
 sbc #0
 sta StepHigh
 pha
 and #$f0
 ora #$10
 sta StepLow
 pla
 and #15
 eor #14
 tay
 sty SubtractEdge
 clc
 adc $c0a7
 and #$f0
 sta $b369
 lda $c0a8
 adc #0
 bcs Done
 sta $b36a
 tya
 clc
 adc Player_X_Position
 and #$f0
 sta EndLow
 lda Player_PageLoc
 adc #0
 bcs Done
 sta EndHigh
 jsr Bounds
 bne Done
 ; Valid Bounds returned A0, which is also the native screen-Y page.
 sta $b36c
 jmp Cell
.segment "PROBE_HEAD"
Probe:
 jsr $b310
 bcc PointReturn
 jsr ChkForNonSolids
 beq PointReturn
 cmp #$1c
 bcc ProbeOrdinary
 jmp ProbeTail
ProbeOrdinary:
 sec
 rts
.segment "PROBE_TAIL"
ProbeTail:
 ; Native effect families are unavailable to this pure geometry prepass.
 ; Defer1C..26 and67..6D as a whole, retaining native sidepipe/climb/spring,
 ; temporary23 and the ordinary endpoint path of neighboring uncommon tiles.
 cmp #$27
 bcc ProbeUnavailable
 cmp #$67
 bcc ProbeSolid
 cmp #$6e
 bcc ProbeUnavailable
ProbeSolid:
 sec
 rts
ProbeUnavailable:
 lda #0
 sec
 rts
