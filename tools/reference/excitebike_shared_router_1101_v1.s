; Three native owners share exactly one3*row/add-tail transport. Native world
; palettes retain the existing immutable-ROM shortcut before owner selection.
; Ex's low parameter is biased -1 because raw37's LSR leaves C1; all other
; low parameters use C0. X is untouched and HuCommonRestore restores old Y/P.
.export ExThreeOwnerGate,ExThreeOwnerHigh,ExThreeOwnerAdd,ExThreeOwnerSetBank
.segment "EX_THREE_GATE"
ExThreeOwnerGate:
 cpy #32
 bne ExThreeOrdinary
 pla
 tay
 plp
 jmp HuNativeWorldPalette
ExThreeOrdinary:
 tya
 sta FarcallJmpTarget_SMC+1
 asl
 adc FarcallJmpTarget_SMC+1
 sta FarcallJmpTarget_SMC+1
 lda SelectedCharacter
 cmp #36
 bcc ExThreeMetal
 lsr
 jmp ExThreeOwnerHigh
ExThreeMetal:
 ldy #$6d
 lda #$ab
 sta FarcallJmpTarget_SMC+2
 lda #$ce
ExThreeOwnerSetBank:
 sta NextBank_SMC+1
 tya
 jmp ExThreeOwnerAdd
.segment "EX_THREE_ROUTE"
ExThreeOwnerHigh:
 lda #$aa
 bcc ExThreeHighReady
 lda #$b0
ExThreeHighReady:
 sta FarcallJmpTarget_SMC+2
 ldy #$88
 bcc ExThreeLowReady
 ldy #$8b                     ; +incomingC1 = actual Ex veneer low8C.
ExThreeLowReady:
 lda #$c1
 jmp ExThreeOwnerSetBank
ExThreeOwnerAdd:
 adc FarcallJmpTarget_SMC+1
 sta FarcallJmpTarget_SMC+1
 jmp HuCommonRestore
