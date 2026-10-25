; A32px standing/crouched side interval needs the intervening tile row.
; Lower and rolling calls keep the native query through a direct tail.
.pushseg
.segment "TMNT_COMBAT"
.proc TnSideMiddleProbe
 tya
 and #1
 beq Original
 lda TnSeq
 cmp #$87
 beq Original
 jsr TnNativeSideQuery
 bne Done
 php
 ldy R2
 cpy #$c0
 bcs No
 tya
 clc
 adc #16
 tay
 lda (R6),y
 beq No
 sta R3
 sty R2
 ldy TnSavedY
 plp
 lda R3
 rts
No:
 ldy TnSavedY
 plp
 lda #0
Done:rts
Original:jmp TnNativeSideQuery
.endproc
.export TnSideMiddleProbe
.popseg

; This private caller always requests player object0 and horizontal output.
; Retain every native pointer/row/nibble result and arithmetic flag; omit
; only the generic mode push/pop/branch and object-indexed loads.
.pushseg
.segment "TMNT_COMBAT"
.proc TnNativeSideQuery
.if ::MAPPER_MMC5
 ldx #0
 sty R4
 lda BlockBuffer_X_Adder,y
 clc
 adc Player_X_Position
 sta R5
 lda Player_PageLoc
 adc #0
 and #1
 tay
 lda #>Block_Buffer_1
 sta R7
 lda R5
 lsr
 lsr
 lsr
 lsr
 clc
 adc BlockBufferAddr,y
 sta R6
 ldy R4
 lda Player_Y_Position
 clc
 adc BlockBuffer_Y_Adder,y
 and #$f0
 sec
 sbc #$20
 sta R2
 tay
 lda (R6),y
 sta R3
 ldy R4
 lda Player_X_Position
 and #15
 sta R4
 lda R3
 rts
.else
 jmp BlockBufferColli_Side
.endif
.endproc
.export TnNativeSideQuery
.popseg
