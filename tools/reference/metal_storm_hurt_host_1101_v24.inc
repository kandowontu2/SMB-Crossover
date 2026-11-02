; A3 is still mapped by Ms12ActorBridge while this C2 worker runs.
; Original BA1A owns terrain-style injury admission and armor scene state.
; Enemy-specific destruction/flashing and source audio playback remain separate.
Ms24Injury:
 lda MsState+$648
 bmi Ms24Handled
 lda MsState+$630
 bmi Ms24Handled
 jsr Ms_BA1A
 lda MsState+$34
 cmp #2
 bne Ms24Handled
 lda #8
 sta MsState+$7e7
Ms24Handled:sec
 rts

; C1 freezes the actor this callback. C0 permits the original movement step.
; Shared source epoch prevents duplicate callbacks and preserves pause clocks.
Ms24HurtTick:
 lda GamePauseStatus
 and #1
 bne Ms24Phase
 lda MsHostHaveEpoch
 beq Ms24New
 lda FrameCounter
 cmp MsHostEpoch
 beq Ms24Phase
Ms24New:
 lda MsState+$34
 cmp #2
 bne Ms24Timer
 lda MsState+$5d0
 bpl Ms24Phase
 lda MsState+$33
 cmp #32
 bcs Ms24Return
 jsr Ms21HurtBlink
 inc MsState+$33
 jmp Ms24Mark
Ms24Return:
 jsr Ms21ArmorReturn
 jsr Ms23ArmorTimer
Ms24Mark:
 lda FrameCounter
 sta MsHostEpoch
 lda #1
 sta MsHostHaveEpoch
 sec
 rts
Ms24Timer:
 jsr Ms23ArmorTimer
 clc
 rts
Ms24Phase:
 lda MsState+$34
 cmp #2
 beq Ms24Handled
 clc
 rts
Ms24Frozen:
 lda #0
 sta Player_X_Scroll
 sta Player_X_Speed
 sta Player_XSpeedAbsolute
 sta Player_Y_Speed
 jmp MsRRestore
