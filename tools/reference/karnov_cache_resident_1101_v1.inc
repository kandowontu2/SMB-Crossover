; Included in the real menu bank29 residual FF lease, stable while C2/C3 map.
; No menu/scene/Main hook enables this private candidate yet.
.export KrLoad,KrCheckCode,KrRetire,KrSelected,KrResidentEnd,KrCookie
.export KrDispatch,KrServiceVeneers,KrLoadReturn,KrDispatchReturn
.import KrCacheServices
KrSelected:
 lda SelectedCharacter
 cmp #7                     ; genuine Rygar raw ID (menu slot7), Karnov alt1
 bne KrSelectedNo
 lda FmAlts
 and #1
 beq KrSelectedNo
 sec
 rts
KrSelectedNo:clc
 rts

; ROM-only authentication: both complete16-byte identity/revision headers.
; Caller AXYP retained, except returned C. Never execute an unauthenticated RAM
; opcode or inspect a foreign state field. A29 remains mapped throughout.
KrCheckCode:
 php
 pha
 txa
 pha
 lda CurrentBankC
 pha
 jsr KrSelected
 bcc KrCheckNo
 ldx #3
KrCheckBank:
 stx CurrentBankC
 stx $5116
 ldx #15
KrCheckByte:
 lda $dfe0,x
 cmp KrCookie,x
 bne KrCheckNo
 dex
 bpl KrCheckByte
 lda CurrentBankC
 cmp #2
 beq KrCheckYes
 ldx #2
 bne KrCheckBank
KrCheckYes:
 tsx
 lda $0104,x
 ora #1
 bne KrCheckSet
KrCheckNo:
 tsx
 lda $0104,x
 and #$fe
KrCheckSet:
 sta $0104,x
 pla
 sta CurrentBankC
 sta $5116
 pla
 tax
 pla
 plp
 rts

; Retire only our own complete header. Do not invalidate another player's
; conditional cache because its first byte happens to be the shared magic.
KrRetire:
 php
 pha
 txa
 pha
 lda CurrentBankC
 pha
 ldx #3
KrRetireBank:
 stx CurrentBankC
 stx $5116
 ldx #15
KrRetireByte:
 lda $dfe0,x
 cmp KrCookie,x
 bne KrRetireNext
 dex
 bpl KrRetireByte
 lda #0
 sta $dfe0
KrRetireNext:
 ldx CurrentBankC
 dex
 cpx #1
 bne KrRetireBank
 pla
 sta CurrentBankC
 sta $5116
 pla
 tax
 pla
 plp
 rts

; Cold load is allowed only inside the existing forced-blank family commit.
; Shared RAM0/1, SRAM selection/protection, and the caller's SMC are untouched.
KrLoad:
 php
 pha
 txa
 pha
 tya
 pha
 .repeat 8,I
 lda R0+I
 pha
 .endrepeat
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
 lda CurrentBankC
 pha
 lda ReloadCHRBank
 pha
 jsr KrSelected
 jcc KrLoadNo
 lda OperMode
 cmp #1
 jne KrLoadNo
 lda FamilyMainCommit
 and #1
 jeq KrLoadNo
 lda DisableScreenFlag
 jeq KrLoadNo
 lda Mirror_PPUMASK
 and #$18
 jne KrLoadNo
 lda NmiDisable
 jpl KrLoadNo
 jsr KrCheckCode
 jcs KrLoadYes
 sei
 lda #0
 sta ReloadCHRBank
 farcall X5PublishChr
 ; Invalidate BOTH first, before any producer writes/code replacement.
 ldx #3
KrInvalidate:
 stx CurrentBankC
 stx $5116
 lda #0
 sta $dfe0
 dex
 cpx #1
 bne KrInvalidate
 ; Zero the complete conditional state bank2 and read every byte back.
 lda #2
 sta CurrentBankC
 sta $5116
 lda #0
 sta R0
 lda #$c0
 sta R1
 ldy #0
 ldx #32
KrZeroPage:
 lda #0
KrZeroByte:
 sta (R0),y
 cmp (R0),y
 jne KrLoadFailed
 iny
 bne KrZeroByte
 inc R1
 dex
 bne KrZeroPage
 ; Source image is8KB at actual CHR pages399..406; $2007 buffered reads.
 lda Mirror_PPUCTRL
 and #$fb
 ora #$20
 sta $2000
 lda #3
 sta CurrentBankC
 sta $5116
 lda #0
 sta R2
KrCopyRow:
 lda #0
 sta R0
 lda R2
 asl
 asl
 ora #$c0
 sta R1
 jsr KrMapRow
 ldx #4
KrCopyByte:
 lda $2007
 sta (R0),y
 iny
 bne KrCopyByte
 inc R1
 dex
 bne KrCopyByte
 lda R1
 sec
 sbc #4
 sta R1
 jsr KrMapRow
 ldx #4
KrVerifyByte:
 lda $2007
 cmp (R0),y
 bne KrLoadFailed
 iny
 bne KrVerifyByte
 inc R1
 dex
 bne KrVerifyByte
 inc R2
 lda R2
 cmp #8
 bne KrCopyRow
 ; Image header is not an early validity publication. Rewrite both headers
 ; with magic cleared, then release bank3 followed by bank2 as the final writes.
 ldx #3
KrPublishBank:
 stx CurrentBankC
 stx $5116
 lda #0
 sta $dfe0
 ldx #15
KrPublishByte:
 lda KrCookie,x
 sta $dfe0,x
 dex
 bne KrPublishByte
 ldx CurrentBankC
 dex
 cpx #1
 bne KrPublishBank
 lda #3
 sta CurrentBankC
 sta $5116
 lda #$a7
 sta $dfe0
 lda #2
 sta CurrentBankC
 sta $5116
 lda #$a7
 sta $dfe0
 jsr KrRestorePPU
KrLoadYes:
 tsx
 lda $0113,x
 ora #1
 bne KrLoadSet
KrLoadFailed:
 ; No successful state publication survives any readback failure, even if
 ; the foreign cache's old magic matched. Both banks are explicitly invalid.
 ldx #3
KrFailInvalidate:
 stx CurrentBankC
 stx $5116
 lda #0
 sta $dfe0
 dex
 cpx #1
 bne KrFailInvalidate
 jsr KrRestorePPU
KrLoadNo:
 tsx
 lda $0113,x
 and #$fe
KrLoadSet:
 sta $0113,x
 pla
 sta ReloadCHRBank
 pla
 sta CurrentBankC
 sta $5116
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
 .repeat 8,I
 pla
 sta R7-I
 .endrepeat
 pla
 tay
 pla
 tax
 pla
 plp
KrLoadReturn:
 rts
KrMapRow:
 lda #1
 sta $5130
 lda R2
 clc
 adc #<399
 sta $512b
 bit $2002
 lda #$0c
 sta $2006
 lda #0
 sta $2006
 lda $2007
 ldy #0
 rts
KrRestorePPU:
 farcall X5PublishChr
 lda Mirror_PPUCTRL
 sta $2000
 bit $2002
 lda HorizontalScroll
 sta $2005
 lda VerticalScroll
 sta $2005
 rts

; Genuine 36 JMP rows retain the original caller Y; the SMC target identifies
; the service, as in the current Thomas dispatcher. Terrain probe Y stays live.
KrServiceVeneers:
.repeat 36
 jmp KrDispatch
.endrepeat
; Typed service ingress. Only a complete selected two-bank signature
; admits a RAM opcode. A valid child's real AXYP/results and scratch are live;
; rejection retains incoming AXYP except C. All five SMC operands are restored.
KrDispatch:
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
 lda FarcallJmpTarget_SMC+1
 sec
 sbc #<KrServiceVeneers
 sta FarcallJmpTarget_SMC+1  ; borrow only after all SMC operands are saved
 lda FarcallJmpTarget_SMC+2
 sbc #>KrServiceVeneers
 bne KrDispatchNo
 lda FarcallJmpTarget_SMC+1
 cmp #108
 bcs KrDispatchNo
 jsr KrCheckCode
 bcc KrDispatchNo
 lda FarcallJmpTarget_SMC+1
 clc
 adc #<KrCacheServices
 sta FarcallJmpTarget_SMC+1
 lda #>KrCacheServices
 adc #0
 sta FarcallJmpTarget_SMC+2
 lda #2
 sta CurrentBankC
 sta $5116
 tsx
 lda $010a,x
 pha                         ; restore caller C/V/D/I before genuine child call
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
 sta $010b,x                 ; child Y replaces saved incoming Y
 lda $0102,x
 sta $010c,x                 ; child X
 lda $0103,x
 sta $010d,x                 ; child A
 lda $0104,x
 sta $010e,x                 ; child P (outer farcall publishes NZ from A)
 txa
 clc
 adc #4
 tax
 txs
 jmp KrDispatchRestore
KrDispatchNo:
 tsx
 lda $010a,x
 and #$fe
KrDispatchSet:
 sta $010a,x
KrDispatchRestore:
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
KrDispatchReturn:
 rts
KrCookie:.incbin "kr-cookie.bin"
KrResidentEnd:
