; Same real service-offset/AXYP/R0..7 ABI as the37 native owner services.
; Cold-only ShLoad is separate. Every RAM call verifies both full headers.
; Unimplemented private vector rows reject; this is not admission by default.
.export ShDispatch,ShServiceVeneers,ShDispatchEnd
.segment "SHINOBI_RESIDENT"
ShServiceVeneers:
.repeat 37
 jmp ShDispatch
.endrepeat
ShDispatch:
 php
 pha
 txa
 pha
 tya
 pha
 lda CurrentBankC
 pha
 .repeat 5,I
 .if I=0
 lda NextBank_SMC+1
 .elseif I=1
 lda SafecallA_SMC+1
 .elseif I=2
 lda FarcallJmpTarget_SMC+1
 .elseif I=3
 lda FarcallJmpTarget_SMC+2
 .else
 lda SafereturnA_SMC+1
 .endif
 pha
 .endrepeat
 lda SelectedCharacter
 cmp #36
 jne ShDispatchNo
 lda FarcallJmpTarget_SMC+1
 sec
 sbc #<ShServiceVeneers
 sta FarcallJmpTarget_SMC+1
 lda FarcallJmpTarget_SMC+2
 sbc #>ShServiceVeneers
 jne ShDispatchNo
 lda FarcallJmpTarget_SMC+1
 cmp #111
 jcs ShDispatchNo
 ; Hot path uses the fully saved outer frame; no redundant helper frames.
 ldx #3
ShDispatchAuthBank:
 stx CurrentBankC
 stx $5116
 ldx #15
ShDispatchAuthByte:
 lda $dfe0,x
 cmp ShCookie,x
 jne ShDispatchNo
 dex
 bpl ShDispatchAuthByte
 ldx CurrentBankC
 dex
 cpx #1
 bne ShDispatchAuthBank
 lda FarcallJmpTarget_SMC+1
 clc
 adc #<ShCacheServices
 sta FarcallJmpTarget_SMC+1
 lda #>ShCacheServices
 adc #0
 sta FarcallJmpTarget_SMC+2
 ; Header loop ends with C2 mapped. Restore original live arguments.
 tsx
 lda $010a,x
 pha
 lda $0109,x
 sta SafecallA_SMC+1
 lda $0108,x
 tax
 plp
 lda #3
 jsr FarCallCommon
 php
 pha
 txa
 pha
 tya
 pha
 tsx
 lda $0101,x
 sta $010b,x
 lda $0102,x
 sta $010c,x
 lda $0103,x
 sta $010d,x
 lda $0104,x
 sta $010e,x
 txa
 clc
 adc #4
 tax
 txs
 jmp ShDispatchRestore
ShDispatchNo:
 tsx
 lda $010a,x
 and #$fe
 sta $010a,x
ShDispatchRestore:
 .repeat 5,I
 pla
 .if I=0
 sta SafereturnA_SMC+1
 .elseif I=1
 sta FarcallJmpTarget_SMC+2
 .elseif I=2
 sta FarcallJmpTarget_SMC+1
 .elseif I=3
 sta SafecallA_SMC+1
 .else
 sta NextBank_SMC+1
 .endif
 .endrepeat
 pla
 sta CurrentBankC
 sta $5116
 pla
 tay
 pla
 tax
 pla
 plp
 rts
ShDispatchEnd:
