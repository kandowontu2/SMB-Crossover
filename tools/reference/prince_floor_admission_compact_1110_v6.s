; Private predicate of the frozen44B admission. The public sweep wrapper owns
; engine8 admission and saves/restores A/P; original floor103B is unchanged.
; After residue>=5, SBC uses C1; nonzero C1 means residue>DY. Negative DY is
; rejected first. This is exactly residue>max(4,DY), without any new SMC.
.setcpu "6502"
.segment "ADMISSION"
PpFloorAdmission:
 ldy Player_Y_Speed
 bmi Original
 lda $c084
 and #15
 cmp #5
 bcc Original
 sbc Player_Y_Speed
 beq Original
 bcs $d4d7
Original:
 rts
