; Same horizontal native export, retaining the old full native X/Page in the
; existing export-owned C0A7/A8 instead of a redundant copy of the endpoint.
.setcpu "6502"
.segment "EXPORT"
 lda Player_X_Position
 sta $c0a7
 lda Player_PageLoc
 sta $c0a8
 lda $c60f
 sec
 sbc #8
 sta Player_X_Position
 lda $c610
 sbc #0
 sta Player_PageLoc
 lda Player_X_Position
 sec
 sbc $c0a7
 sta Player_X_Scroll
 asl a
 asl a
 asl a
 asl a
 sta Player_X_Speed
 nop
 nop
