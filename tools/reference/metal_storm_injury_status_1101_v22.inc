; Typed HuInjuryStatus result across the existing authenticated transport.
; Worker SP+18 is native Y (see Ms12Adder); +20 is A and +21 is P.
; Source armor is05D0, hurt immunity0648, barrier0660, GravityFire0630.
; Special-state contacts must reach the injury handler instead of the native
; unconditional unarmored death path. The handler itself is integrated next.
.import MsState
.export Ms22InjuryStatus
Ms22InjuryStatus:
 lda MsState+$5d0
 bne Ms22StatusOne
 lda MsState+$648
 ora MsState+$660
 ora MsState+$630
 and #$80
 beq Ms22StatusZero
Ms22StatusOne:
 lda #1
Ms22StatusZero:
 tsx
 sta $0114,x
 tay
 lda $0115,x
 and #$7d
 cpy #0
 bne Ms22StatusFlags
 ora #2
Ms22StatusFlags:
 sta $0115,x
 sec
 rts
