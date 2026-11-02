; Source death timing with native life-loss handoff. Explosion graphics pending.
Ms34DeathStart:
 lda #0
 sta MsState+$33
 sta MsState+$35
 sta MsState+$5d0
 lda #2
 sta MsState+$34
 lda #8
 sta MsState+$7e7
 lda FrameCounter
 sta MsHostEpoch
 lda #1
 sta MsHostHaveEpoch
 sec
 rts

Ms34DeathTick:
 lda GamePauseStatus
 and #1
 bne Ms34Done
 lda FrameCounter
 cmp MsHostEpoch
 beq Ms34Done
 sta MsHostEpoch
 lda MsState+$35
 beq Ms34Freeze
 cmp #1
 beq Ms34BeginExplosion
 cmp #2
 beq Ms34Explosion
 cmp #3
 bne Ms34Done
 dec MsState+$53
 bne Ms34Done
 inc MsState+$35
 ; Native engine6 owns losing one life, game-over and level restart.
 lda #6
 sta GameEngineSubroutine
Ms34Done:
 sec
 rts
Ms34Freeze:
 lda MsState+$33
 cmp #32
 bcs Ms34Next
 jsr Ms21HurtBlink
 inc MsState+$33
 sec
 rts
Ms34Next:
 inc MsState+$35
 sec
 rts
Ms34BeginExplosion:
 jsr Ms27DeathInit
 sec
 rts
Ms34Explosion:
 jsr Ms27DeathAnimate
 sec
 rts
