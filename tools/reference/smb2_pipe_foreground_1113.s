; Proposal: current owned World207B, visible engine8 priority lifetime.
; Both coin-loop HeadPage stores were dead until the immediate caller reset.
.setcpu "6502"
.segment "S2_FOREGROUND_WORLD"
S2ForegroundWorld:
 lda S2HeadY
 beq WorldCoins
 sta R6
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
 ldx Player_Y_Position
 cpx #64
 bcc WorldKeepPriority
 sta Player_SprAttrib         ; A is the proved zero sourceYPage here.
WorldKeepPriority:
 txa
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
 dex
WorldPipe:
 lda S2Air
 bne WorldDone
 lda Up_Down_Buttons
 and #4
 beq WorldDone
 lda #3
 ldy #32
 jsr WorldPlayerCell
 sta R1
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
S2ForegroundWorldEnd:
