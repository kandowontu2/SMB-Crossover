; Reserve all three shared projectile slots before spending one missile volley.
; Existing missile-type occupancy retains the native one-volley limit.
.pushseg
.segment "SPECIAL_EXTRA"
.proc SophiaTripletAdmission
 ldx #9
 ldy #3
Loop:
 lda RgShotType,x
 bne Next
 dey
 beq Enough
Next:
 dex
 bpl Loop
 sty AvCount
 rts
Enough:
 jmp RemainingWeapons::CountType
.endproc
.popseg
