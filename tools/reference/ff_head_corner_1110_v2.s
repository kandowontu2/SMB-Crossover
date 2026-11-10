; Derivative of frozen ff_head_corner_1110.s. Native coins are effect-owned
; pass-through cells despite their SOLID bit and must reach CheckForCoinMTiles.
; The separate graphics leaf retains native pipe priority while keeping FF's
; existing palette/flip reset. No source motor, dimensions or attacks change.
.setcpu "6502"
.segment "HEAD"
FfCornerHeadRead:
 jsr FfHostRead
 beq ReadDone
 cmp #$c2
 beq Return
 cmp #$c3
 beq Return
 ldx Player_Y_Speed
 bpl Return
 tax
 lda MTileAttribute,x
 and #3
 cmp #1
 bne Return
 lda FfCornerPreviousX
 clc
 adc #1
 eor R5
 and #$f0
 bne RightEndpoint
 lda FfCornerPreviousPage
 adc #0
 cmp FfTerrainPage
 beq Return
RightEndpoint:
 lda FfCornerPreviousX
 clc
 adc #14
 eor R5
 and #$f0
 bne SideOnly
 lda FfCornerPreviousPage
 adc #0
 cmp FfTerrainPage
 beq Return
SideOnly:
 lda #0
 sta R3
Return:
 sec
ReadDone:
 jmp FfHostReadReturn
FfCornerHeadReadEnd:

.segment "SNAPSHOT"
FfCornerCapture:
 jsr FfEnsure
 lda Player_X_Position
 sta FfCornerPreviousX
 lda Player_PageLoc
 sta FfCornerPreviousPage
 rts
FfCornerCaptureEnd:

.segment "PRIORITY"
FfNativePipePriority:
 lda Player_SprAttrib
 and #$20
 sta Player_SprAttrib
 rts
FfNativePipePriorityEnd:
