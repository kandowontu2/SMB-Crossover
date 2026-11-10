; Derivative admission for the frozen103B geometry leaf at D4D7.
; PlayerBGCollision skips landing while rising. Otherwise its real window is
; five pixels for DY0..4, or DY+1 for DY5..127. Preserve every admitted native
; floor/rising case; only the rejected residue can require source geometry.
.setcpu "6502"
.segment "NATIVE_FOOT"
PpNativeFloorAdmission:
 php
 pha
 lda $0f
 cmp #8
 bne Original
 ldy $8e
 bmi Original
 lda $c084
 and #$0f
 cpy #5
 bcc Small
 cmp $8e
 bcc Original
 beq Original
 bcs Repair
Small:
 cmp #5
 bcc Original
Repair:
 pla
 plp
 jmp $d4d7
Original:
 pla
 plp
 ldy #6
 sec
 rts
