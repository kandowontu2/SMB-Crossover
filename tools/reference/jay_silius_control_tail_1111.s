; State-changing branches of original bank6 $8304..$8426.
; The native pose dispatch is omitted. Its turn/crouch transitions run once
; after the original integrator, using the existing donor actor fields.
.setcpu "6502"
.segment "HANDOFF"

AdvanceControl:
 lda DonorFlags
 bmi ControlDone
 lda DonorControl
 and #$30
 bne CrouchTransition
 lda DonorFlags
 and #$1c
 beq GroundControl
 lda DonorFlags
 and #$10
 bne ControlDone
 lda DonorFlags
 and #$04
 beq ControlDone
 lda DonorControl
 and #$28
 beq ControlDone
 and #$20
 bne FinishCrouch
 jmp AdvanceTurn
GroundControl:
 lda DonorVX
 bne ControlDone
 lda DonorControl
 and #$08
 beq ControlDone
AdvanceTurn:
 dec DonorControlTimer
 beq FinishTurn
 lda DonorControlTimer
 cmp #2
 bne ControlDone
 lda DonorFlags
 eor #2
 sta DonorFlags
 rts
FinishTurn:
 lda DonorControl
 and #$f7
 sta DonorControl
 rts
CrouchTransition:
 and #$20
 bne FinishCrouch
 dec DonorControlTimer
 bne ControlDone
 lda DonorControl
 and #$ef
 sta DonorControl
 lda DonorFlags
 eor #8
 sta DonorFlags
 rts
FinishCrouch:
 dec DonorControlTimer
 bne ControlDone
 lda DonorControl
 and #$df
 sta DonorControl
ControlDone:
 rts
