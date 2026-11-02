; Private complete two-owner cold/retire measurement. Raw39 is proposed only.
; No addresses in this include have been allocated or installed.
; Header core is usable only under a frame that saves R3..6 and live AXYP.
.segment "COMMON_OWNER_PROPOSAL"
.export CoCold,CoRetire,CoCheckCode,CoCheckHeaders,CoOwnerEnd
.export CoSmc
.macro CoFar Target,Bank
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #Bank
 jsr FarCallCommon
.endmacro
CoCold:
 php
 pha
 txa
 pha
 tya
 pha
 lda #0
 pha
 beq CoSave
CoRetire:
 php
 pha
 txa
 pha
 tya
 pha
 lda #1
 pha
CoSave:
 ldx #0
:
 lda R0,x
 pha
 inx
 cpx #8
 bne :-
 ldx #0
:
 ldy CoSmc,x
 lda $0100,y
 pha
 inx
 cpx #5
 bne :-
 lda CurrentBankC
 pha
 lda ReloadCHRBank
 pha
 tsx
 lda $0110,x
 beq CoColdMode
 jsr CoRetireOwners
 jmp CoRestore
CoColdMode:
 jsr CoSelect
 jcc CoNo
 lda OperMode
 cmp #1
 bne CoGuardNo
 lda FamilyMainCommit
 and #1
 beq CoGuardNo
 lda DisableScreenFlag
 beq CoGuardNo
 lda Mirror_PPUMASK
 and #$18
 bne CoGuardNo
 lda NmiDisable
 bpl CoGuardNo
 jsr CoCheckHeaders
 bcc CoColdBegin
 jmp CoYes
CoGuardNo:
 jmp CoNo
CoColdBegin:
 sei
 lda #0
 sta ReloadCHRBank
 jsr CoPublishChr
 jsr CoRetireOwners
 jsr CoInvalidate
 jsr CoSelect
 CoFar CoWorker,$fb
 bcc CoFailed
 ; The fixed worker preserves R5/R6. The immutable cookie remains in the
 ; resident caller bank while its scatter descriptor is in worker bank123.
 ldx #3
CoCommitBank:
 stx CurrentBankC
 stx $5116
 ldy #15
:
 lda (R5),y
 sta $dfe0,y
 dey
 bpl :-
 ldx CurrentBankC
 dex
 cpx #1
 bne CoCommitBank
 jsr CoRestorePpu
CoYes:
 tsx
 lda $0114,x
 ora #1
 bne CoResult
CoFailed:
 jsr CoInvalidate
 jsr CoRestorePpu
CoNo:
 tsx
 lda $0114,x
 and #$fe
CoResult:
 sta $0114,x
CoRestore:
 pla
 sta ReloadCHRBank
 pla
 sta CurrentBankC
 sta $5116
 ldx #4
:
 ldy CoSmc,x
 pla
 sta $0100,y
 dex
 bpl :-
 ldx #7
:
 pla
 sta R0,x
 dex
 bpl :-
 pla                         ; mode, not part of the public AXYP result
 pla
 tay
 pla
 tax
 pla
 plp
 rts

; Carry-only private service-auth helper. Its public callers save AXYP and
; consume only carry. All four descriptor scratch bytes survive this call.
CoCheckCode:
 ldx #3
:
 lda R3,x
 pha
 dex
 bpl :-
 jsr CoSelect
 bcc :+
 jsr CoCheckHeaders
:
 lda #0
 rol
 tay
 ldx #0
:
 pla
 sta R3,x
 inx
 cpx #4
 bne :-
 tya
 lsr
 rts

CoSelect:
 lda SelectedCharacter
 cmp #37
 beq CoSelectEx
 cmp #39
 bne CoSelectNo
 ldx #1
 bne CoSelectOwner
CoSelectEx:
 ldx #0
CoSelectOwner:
 lda CoCookieLo,x
 sta R5
 lda CoCookieHi,x
 sta R6
 lda CoDescriptorLo,x
 sta R3
 lda CoDescriptorHi,x
 sta R4
 sec
 rts
CoSelectNo:
 clc
 rts

CoCheckHeaders:
 lda CurrentBankC
 pha
 ldx #3
CoCheckBank:
 stx CurrentBankC
 stx $5116
 ldy #15
:
 lda $dfe0,y
 cmp (R5),y
 bne CoHeadersNo
 dey
 bpl :-
 ldx CurrentBankC
 dex
 cpx #1
 bne CoCheckBank
 sec
 bcs CoHeadersRestore
CoHeadersNo:
 clc
CoHeadersRestore:
 pla
 sta CurrentBankC
 sta $5116
 rts

; This is the required before-overwrite seam, including a foreign raw owner.
; Authentic BB code unwinds every still-valid trapped native AI association.
CoRetireOwners:
 lda #<CoBBCookie
 sta R5
 lda #>CoBBCookie
 sta R6
 jsr CoCheckHeaders
 bcc CoNoBB
 lda #2
 sta CurrentBankC
 sta $5116
 CoFar BbNativeRetire,3
 jsr CoInvalidate
CoNoBB:
 lda #<CoExCookie
 sta R5
 lda #>CoExCookie
 sta R6
 jsr CoCheckHeaders
 bcc CoNoEx
 jsr CoInvalidate
CoNoEx:
 jsr ShRetire
 rts
CoInvalidate:
 ldx #3
:
 stx CurrentBankC
 stx $5116
 lda #0
 sta $dfe0
 dex
 cpx #1
 bne :-
 rts
CoRestorePpu:
 jsr CoPublishChr
 lda Mirror_PPUCTRL
 sta $2000
 bit $2002
 lda HorizontalScroll
 sta $2005
 lda VerticalScroll
 sta $2005
 rts
CoPublishChr:
 CoFar X5PublishChr,Bank_X5PublishChr
 rts
CoSmc:
 .byte <(NextBank_SMC+1),<(SafecallA_SMC+1),<(FarcallJmpTarget_SMC+1),<(FarcallJmpTarget_SMC+2),<(SafereturnA_SMC+1)
CoCookieLo:.byte <CoExCookie,<CoBBCookie
CoCookieHi:.byte >CoExCookie,>CoBBCookie
CoDescriptorLo:.byte <CoExDescriptor,<CoBBDescriptor
CoDescriptorHi:.byte >CoExDescriptor,>CoBBDescriptor
CoExCookie:.incbin "common-current-Ex-cookie.bin"
CoBBCookie:.incbin "common-BB-cookie.bin"
CoOwnerEnd:
