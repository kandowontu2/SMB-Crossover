; Exact original bank4 $8471..$848E. Called once per active source update,
; including the armor-return frame, AFTER Ms21ArmorReturn sets074B=B4.
; No pause/epoch ownership here; host movement owns that qualification.
.import MsState
.export Ms23ArmorTimer
Ms23ArmorTimer:
 lda MsState+$648
 bpl Ms23ArmorTimerDone
 dec MsState+$74b
 bne Ms23ArmorTimerToggle
 lda #$00
 sta MsState+$648
 lda #$80
 sta MsState+$70
 sta MsState+$74e
 rts
Ms23ArmorTimerToggle:
 lda MsState+$70
 eor #$80
 sta MsState+$70
Ms23ArmorTimerDone:
 rts
