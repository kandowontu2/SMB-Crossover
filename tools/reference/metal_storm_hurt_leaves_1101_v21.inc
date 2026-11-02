; Original Metal Storm injury leaves. Caller owns scene timing and host effects.
; No cartridge allocation or service admission is implied by this component.
; Ms21HurtBlink is donor9548..9566: incoming A is the original scene clock.
; Native-enemy flashing at9567 is a separate host contact boundary.
; Ms21ArmorReturn is donor95BB..95D5: enemy release/palette follows separately.
.import MsState
.export Ms21HurtBlink,Ms21ArmorReturn
Ms21HurtBlink:
 and #$02
 bne Ms21HurtVisible
 lda MsState+$33
 cmp #$10
 bcc Ms21HurtVisible
 lda MsState+$540
 and #$f0
 ora #$01
 sta MsState+$540
 jmp Ms21HurtDone
Ms21HurtVisible:
 lda MsState+$540
 and #$f0
 sta MsState+$540
Ms21HurtDone:
 rts
Ms21ArmorReturn:
 lda #$00
 sta MsState+$5d0
 sta MsState+$528
 lda #$b4
 sta MsState+$74b
 lda MsState+$750
 sta MsState+$34
 lda MsState+$751
 sta MsState+$35
 lda #$80
 sta MsState+$70
 rts
