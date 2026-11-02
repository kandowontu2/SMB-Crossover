.segment "CODE"
.export Ms18ColdRoute
Ms18ColdRoute:
 cpy #32
 bne Ms18WarmRoute
 ; HuCommon saved native Y/P. This ROM-only query is legal before cold load.
 pla
 tay
 plp
 jmp HuNativeWorldPalette
Ms18WarmRoute:
 lda #$ab
 sta FarcallJmpTarget_SMC+2
 tya
 sta FarcallJmpTarget_SMC+1
 asl
 adc FarcallJmpTarget_SMC+1
 adc #$6d
 sta FarcallJmpTarget_SMC+1
 lda #($80|78)
 sta NextBank_SMC+1
 jmp HuCommonRestore
.assert *-Ms18ColdRoute<=48,error,"Chip HUD unreachable padding capacity"
