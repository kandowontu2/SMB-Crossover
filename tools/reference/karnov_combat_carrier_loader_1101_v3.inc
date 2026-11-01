; PROPOSAL ONLY. Carrier1019/1020 is not granted until all host consumers close.
; Place these helpers AFTER the real source-aligned water table in ROM29tail.
; Replace original8B row-destination setup by JSR KrCarrierRowSetup (-5B).
; Replace original13B KrMapRow bank-map prefix by JSR KrCarrierMap (-10B).
; KrCopyRow: LDX #4 -> LDX R4; verify SBC #4 -> SBC R4, LDX #4 -> LDX R4.
; Last loop CMP #8 -> CMP #10. Existing copy/verify/publication/failure owners
; stay in their original order. No RAM opcode is used during this cold loader.
.export KrCarrierRowSetup,KrCarrierMap,KrCarrierHelpersEnd
.import CurrentBankC
.importzp R1,R2,R4
.pushseg
.segment "KR_CARRIER_HELPERS"
KrCarrierRowSetup:
 ldx R2
 lda KrCarrierDestHi,x
 sta R1
 lda #4
 cpx #9
 bne :+
 lda #1
:sta R4
 cpx #8
 bcc :+
 lda #2
 sta CurrentBankC
 sta $5116
:rts
KrCarrierMap:
 lda #1
 ldx R2
 cpx #8
 bcc :+
 lda #3
:sta $5130
 lda KrCarrierChrLo,x
 sta $512b
 rts
KrCarrierDestHi:.byte $c0,$c4,$c8,$cc,$d0,$d4,$d8,$dc,$c9,$cd
KrCarrierChrLo:.byte <399,<400,<401,<402,<403,<404,<405,<406,<1019,<1020
KrCarrierHelpersEnd:
.popseg
