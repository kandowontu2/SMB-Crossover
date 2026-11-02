.segment "GATE"
 lda SelectedCharacter
 cmp #36
 bne MetalRoute
 jmp ShinobiRoute
MetalRoute:
 cpy #32
 bne MetalOrdinary
 pla
 tay
 plp
 jmp HuNativeWorldPalette
MetalOrdinary:
 lda #$ab
 sta FarcallJmpTarget_SMC+2
 tya
 sta FarcallJmpTarget_SMC+1
 asl
 adc FarcallJmpTarget_SMC+1
 adc #$6d
 sta FarcallJmpTarget_SMC+1
 lda #$ce
 sta NextBank_SMC+1
 jmp HuCommonRestore
.segment "ROUTE"
ShinobiRoute:
 lda #>ShServiceVeneers
 sta FarcallJmpTarget_SMC+2
 tya
 sta FarcallJmpTarget_SMC+1
 asl
 adc FarcallJmpTarget_SMC+1
 adc #<ShServiceVeneers
 sta FarcallJmpTarget_SMC+1
 lda #$c1
 sta NextBank_SMC+1
 jmp HuCommonRestore
