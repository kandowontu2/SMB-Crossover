; Proposal only: exact owned A118 probe+shared RTS and207B MainWorld.
; All non-flag source collision responses remain unchanged. No new RAM.
.setcpu "6502"
.segment "S2_FLAG_PROBE"
S2FlagProbe:
 txa
 pha
 lda S2DF011,y
 pha
 asl
 lda #0
 bcc ProbeXPositive
 lda #$ff
ProbeXPositive:
 sta R5
 pla
 clc
 adc S2X,x
 and #$f0
 sta R4
 lda S2Page,x
 adc R5
 sta R5
 lda S2DF055,y
 pha
 asl
 lda #0
 bcc ProbeYPositive
 lda #$ff
ProbeYPositive:
 sta R7
 pla
 clc
 adc S2Y,x
 and #$f0
 sta R6
 lda S2YPage,x
 adc R7
 bne ProbeEmpty
 lda R6
 cmp #32
 bcc ProbeEmpty
 cmp #240
 bcs ProbeEmpty
 lda R6
 sta R2
 lda R6
 sec
 sbc #32
 pha
 lda R5
 and #1
 asl
 asl
 asl
 asl
 sta R0
 lda R4
 lsr
 lsr
 lsr
 lsr
 ora R0
 jsr GetBlockBufferAddr
 pla
 tay
 lda (R6),y
 beq ProbeEmpty
 ; Original23/26 skips become the inclusive23..26 range. Y and A stay
 ; intact; SEC preserves both old nonzero empty cases' returned carry.
 cmp #$23
 bcc ProbeOtherTile
 cmp #$27
 bcc ProbeFlagEmpty
ProbeOtherTile:
 cmp #$c2
 beq ProbeEmpty
 cmp #$c3
 beq ProbeEmpty
 cmp #$5f
 beq ProbeEmpty
 cmp #$60
 beq ProbeEmpty
 tay
 lda MTileAttribute,y
 and #1
 beq ProbeEmpty
 lda S2ProbeDirection
 cmp #2
 bcs ProbeSolid
 lda R4
 sta S2HeadX
 lda R5
 sta S2HeadPage
 lda R2
 sta S2HeadY
ProbeSolid:
 lda #$ff
 bne ProbeResult
ProbeFlagEmpty:
 sec
ProbeEmpty:
 lda #0
ProbeResult:
 sta S2Math0
 pla
 tax
S2FlagSharedReturn:
 rts                         ; also the original S2WorldInteraction entry.

.segment "S2_FLAG_WORLD"
S2FlagWorld:
 lda S2HeadY
 beq WorldCoins
 sta R6                      ; same head operand, captured before gate loads.
 lda AreaType
 beq WorldCoins
 lda BlockBounceTimer
 bne WorldCoins
 lda S2HeadX
 sta R4
 lda S2HeadPage
 sta R5
 jsr S2MainCell
 beq WorldCoins
 tay
 lda MTileAttribute,y
 and #6
 bne WorldCoins
 tya
 jsr PlayerHeadCollision
 jsr S2MainVelocity
WorldCoins:
 lda S2YPage
 bne WorldDone
 ; These are exactly the native lower side probes for big/small/ducked:
 ; left2/right13, Y+24. The native function supplies PLAYER X&15 and the
 ; true buffer pointer. HandleClimbing retains its original6..9 thin gate.
 lda Player_Y_Position
 sec
 sbc #8
 cmp #200
 bcs WorldCoinStart
 ldy #4
 jsr BlockBufferColli_Side
 cmp #$24
 beq WorldFlag
 cmp #$25
 beq WorldFlag
 ldy #6
 jsr BlockBufferColli_Side
 cmp #$24
 beq WorldFlag
 cmp #$25
 bne WorldCoinStart
WorldFlag:
 jsr HandleClimbing
 lda GameEngineSubroutine
 cmp #8
 bne WorldDone
WorldCoinStart:
 ldx #0
WorldCoinLoop:
 stx S2HeadPage
 lda WorldCoinX,x
 ldy WorldCoinY,x
 jsr WorldPlayerCell
 jsr CheckForCoinMTiles
 bcc WorldCoinNext
 jsr HandleCoinMetatile
 jmp WorldPipe
WorldCoinNext:
 inx
 cpx #9
 bcc WorldCoinLoop
 stx S2HeadPage
 dex                         ; retain old no-coin X8 / HeadPage9 outputs.
WorldPipe:
 lda S2Air
 bne WorldDone
 lda Up_Down_Buttons         ; MainPlayer publishes the same source Down bit.
 and #4
 beq WorldDone
 lda #3
 ldy #32
 jsr WorldPlayerCell
 sta R1                      ; PlayerCell/MainCell never write R1.
 lda #12
 ldy #32
 jsr WorldPlayerCell
 sta R0
 jsr HandlePipeEntry
WorldDone:
 rts
WorldPlayerCell:
 clc
 adc S2X
 sta R4
 lda S2Page
 adc #0
 sta R5
 tya
 clc
 adc S2Y
 sta R6
 jmp S2MainCell
WorldCoinX:
 .byte $02,$07,$0c,$02,$07,$0c,$02,$07,$0c
WorldCoinY:
 .byte $0b,$0b,$0b,$16,$16,$16,$20,$20,$20
S2FlagWorldEnd:
