; Entered only immediately after HostExport/NativeMotionExport. HostExport has
; already published Player_Pos_ForScroll=(nativeX-ScreenLeft)&255. Reuse that
; exact value instead of carrying a duplicate low difference on the stack.
; All native outputs and AX/Y are unchanged; the frozen67B source is retained.
.setcpu "6502"
.segment "CAMERA"
 lda ScrollLock
 ora SideCollisionTimer
 ora Platform_X_Scroll
 bne Keep
 lda Player_X_Scroll
 bmi Keep
 lda Player_X_Position
 cmp ScreenLeft_X_Pos
 lda Player_PageLoc
 sbc ScreenLeft_PageLoc
 bne BeyondPage
 lda Player_Pos_ForScroll
 sec
 sbc #120
 bcc Keep
 beq Keep
 cmp #5
 bcc Publish
Force:
 lda #5
Publish:
 sta Player_X_Scroll
Keep:
 sec
 jmp $bd42
BeyondPage:
 cmp #1
 bne Keep
 lda #$ff
 sta Player_Pos_ForScroll
 bne Force
