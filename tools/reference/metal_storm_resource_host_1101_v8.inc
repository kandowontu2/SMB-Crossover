; Split ROM-only cold loader. Every segment has an audited physical FF-hole
; proposal, not a resource grant. Source caches execute no opcode while loading.
.import CurrentBankC,ReloadCHRBank,SelectedCharacter,OperMode,FamilyMainCommit
.import DisableScreenFlag,Mirror_PPUMASK,Mirror_PPUCTRL,NmiDisable,GameEngineSubroutine
.import HorizontalScroll,VerticalScroll,X5PublishChr,FarCallCommon
.import SafecallA_SMC,FarcallJmpTarget_SMC,NextBank_SMC,SafereturnA_SMC
.import MsRenderGraphics,MsRenderDraw,MsRenderColors
.importzp R0,R1,R2,R3,R4,R5,R6,R7
.export Ms8Load,Ms8Auth,Ms8EntryEnd,Ms8WorkEnd,Ms8CheckEnd,Ms8AuthEnd
.export Ms8ZeroEnd,Ms8CopyEnd,Ms8MapEnd,Ms8FinishEnd
.export MsRenderGate,MsGraphicsGate,MsColorsGate,MsGateEnd
.macro Ms8Far Target,Bank
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #($80|Bank)
 jsr FarCallCommon
.endmacro

.segment "GATE"
; Caller transport already maps C2. Authenticate C3 through the C window too:
; this A-ROM gate must never mistake its own BFE0 for the RAM3 header.
MsGraphicsGate:
 jsr Ms8GateAuth
 rts
MsRenderGate:
 jsr Ms8GateAuth
 rts
MsColorsGate:
 jsr Ms8GateAuth
 rts
Ms8GateAuth:
 php
 pha
 txa
 pha
 tya
 pha
 ldx #0
Ms8GateSave:
 ldy Ms8GateSmc,x
 lda $0100,y
 pha
 inx
 cpx #5
 bne Ms8GateSave
 Ms8Far Ms8WarmAuth,25
 bcc Ms8GateBad
 lda $c800                 ; only after both complete headers validated
 cmp #$a7
 bne Ms8GateBad
 ; Saved entry return address identifies only these three legal services.
 ; Keep5caller SMC bytes on stack until after the actual C2 renderer returns.
 tsx
 lda $010a,x
 cmp #<(MsGraphicsGate+2)
 beq Ms8GateGraphics
 cmp #<(MsRenderGate+2)
 beq Ms8GateDraw
 jsr MsRenderColors
 jmp Ms8GateAccepted
Ms8GateGraphics:
 jsr MsRenderGraphics
 jmp Ms8GateAccepted
Ms8GateDraw:jsr MsRenderDraw
Ms8GateAccepted:
 tsx
 lda $0109,x
 ora #1
 bne Ms8GateResult
Ms8GateBad:
 tsx
 lda $0109,x
 and #$fe
Ms8GateResult:
 sta $0109,x
 ldx #4
Ms8GateRestore:
 ldy Ms8GateSmc,x
 pla
 sta $0100,y
 dex
 bpl Ms8GateRestore
 pla
 tay
 pla
 tax
 pla
 plp
 rts
Ms8GateSmc:.byte <(NextBank_SMC+1),<(SafecallA_SMC+1),<(FarcallJmpTarget_SMC+1),<(FarcallJmpTarget_SMC+2),<(SafereturnA_SMC+1)
MsGateEnd:

.segment "MS8_ENTRY"
; AXYP except carry retained, all foreground R0..R7 and5public SMC retained.
Ms8Load:
 php
 pha
 txa
 pha
 tya
 pha
 ldx #0
Ms8SaveZp:
 lda R0,x
 pha
 inx
 cpx #8
 bne Ms8SaveZp
 ldx #0
Ms8SaveSmc:
 ldy Ms8SmcOffsets,x
 lda $0100,y
 pha
 inx
 cpx #5
 bne Ms8SaveSmc
 lda CurrentBankC
 pha
 lda ReloadCHRBank
 pha
 Ms8Far Ms8Work,37
 tsx
 bcc Ms8ResultNo
 lda $0113,x
 ora #1
 bne Ms8Result
Ms8ResultNo:
 lda $0113,x
 and #$fe
Ms8Result:
 sta $0113,x
 pla
 sta ReloadCHRBank
 pla
 sta CurrentBankC
 sta $5116
 ldx #4
Ms8RestoreSmc:
 ldy Ms8SmcOffsets,x
 pla
 sta $0100,y
 dex
 bpl Ms8RestoreSmc
 ldx #7
Ms8RestoreZp:
 pla
 sta R0,x
 dex
 bpl Ms8RestoreZp
 pla
 tay
 pla
 tax
 pla
 plp
 rts
Ms8SmcOffsets:.byte <(NextBank_SMC+1),<(SafecallA_SMC+1),<(FarcallJmpTarget_SMC+1),<(FarcallJmpTarget_SMC+2),<(SafereturnA_SMC+1)
Ms8EntryEnd:

.segment "MS8_WORK"
Ms8Work:
 Ms8Far Ms8Check,21
 bcc Ms8WorkNo
 cmp #1
 beq Ms8WorkYes
 Ms8Far Ms8Zero,116
 bcc Ms8WorkNo
 Ms8Far Ms8Copy,95
 lda #0
 rol a                       ; failure0/success1 passed through real farcall
 Ms8Far Ms8Finish,99
 rts
Ms8WorkYes:sec
 rts
Ms8WorkNo:clc
 rts
Ms8WorkEnd:

.segment "MS8_CHECK"
Ms8Check:
 lda SelectedCharacter
 cmp #35
 bne Ms8CheckNo
 lda OperMode
 cmp #1
 bne Ms8CheckNo
 lda FamilyMainCommit
 and #1
 beq Ms8CheckNo
 lda DisableScreenFlag
 beq Ms8CheckNo
 lda Mirror_PPUMASK
 and #$18
 bne Ms8CheckNo
 lda NmiDisable
 bpl Ms8CheckNo
 Ms8Far Ms8Auth,25
 lda #0
 bcc Ms8ColdAllowed
 lda #1
Ms8ColdAllowed:sec
 rts
Ms8CheckNo:clc
 rts
Ms8CheckEnd:

.segment "MS8_AUTH"
; Complete shared revision fingerprint for both banks, no foreign-state read.
Ms8WarmAuth:
 lda SelectedCharacter
 cmp #35
 bne Ms8WarmNo
 lda OperMode
 cmp #1
 bne Ms8WarmNo
 lda GameEngineSubroutine
 cmp #8
 bne Ms8WarmNo
 lda CurrentBankC
 cmp #2
 beq Ms8Auth
Ms8WarmNo:clc
 rts
Ms8Auth:
 lda CurrentBankC
 pha
 ldx #3
Ms8AuthBank:
 stx CurrentBankC
 stx $5116
 ldy #15
Ms8AuthByte:
 lda $dfe0,y
 cmp Ms8AuthCookie,y
 bne Ms8AuthNo
 dey
 bpl Ms8AuthByte
 ldx CurrentBankC
 dex
 cpx #1
 bne Ms8AuthBank
 pla
 sta CurrentBankC
 sta $5116
 sec
 rts
Ms8AuthNo:
 pla
 sta CurrentBankC
 sta $5116
 clc
 rts
Ms8AuthCookie:.incbin "cookie.bin"
Ms8AuthEnd:

.segment "MS8_ZERO"
Ms8Zero:
 sei
 lda #0
 sta ReloadCHRBank
 Ms8Far X5PublishChr,62
 ; Revoke both owners before zeroing state or writing code.
 ldx #3
Ms8Invalidate:
 stx CurrentBankC
 stx $5116
 lda #0
 sta $dfe0
 dex
 cpx #1
 bne Ms8Invalidate
 lda #0
 sta R0
 lda #$c0
 sta R1
 ldy #0
 ldx #32
Ms8ZeroPage:
 lda #0
Ms8ZeroByte:
 sta (R0),y
 cmp (R0),y
 bne Ms8ZeroNo
 iny
 bne Ms8ZeroByte
 inc R1
 dex
 bne Ms8ZeroPage
 lda Mirror_PPUCTRL
 and #$fb
 ora #$20
 sta $2000
 sec
 rts
Ms8ZeroNo:clc
 rts
Ms8ZeroEnd:

.segment "MS8_COPY"
Ms8Copy:
 lda #0
 sta R2
Ms8CopyRow:
 Ms8Far Ms8Map,34
 ldx #4
Ms8CopyPage:
 lda $2007
 sta (R0),y
 iny
 bne Ms8CopyPage
 inc R1
 dex
 bne Ms8CopyPage
 Ms8Far Ms8Map,34             ; restarts both RAM and buffered CHR row
 ldx #4
Ms8VerifyPage:
 lda $2007
 cmp (R0),y
 bne Ms8CopyNo
 iny
 bne Ms8VerifyPage
 inc R1
 dex
 bne Ms8VerifyPage
 inc R2
 lda R2
 cmp #11
 bne Ms8CopyRow
 sec
 rts
Ms8CopyNo:clc
 rts
Ms8CopyEnd:

.segment "MS8_MAP"
Ms8Map:
 ldx R2
 lda Ms8DestHi,x
 sta R1
 lda #0
 sta R0
 lda #3
 cpx #8
 bcc :+
 lda #2
:sta CurrentBankC
 sta $5116
 lda Ms8CarrierHi,x
 sta $5130
 lda Ms8CarrierLo,x
 sta $512b
 bit $2002
 lda #$0c
 sta $2006
 lda #0
 sta $2006
 lda $2007                   ; exact PPU read-buffer dummy
 ldy #0
 rts
Ms8DestHi:.byte $c0,$c4,$c8,$cc,$d0,$d4,$d8,$dc,$cd,$d1,$d5
Ms8CarrierLo:.lobytes 247,248,249,250,827,828,829,830,831,1023,494
Ms8CarrierHi:.hibytes 247,248,249,250,827,828,829,830,831,1023,494
Ms8MapEnd:

.segment "MS8_FINISH"
; InputA1: verified all11 rows. A0: revoke both after any copy failure.
Ms8Finish:
 sta R3
 beq Ms8Failed
 ldx #3
Ms8PublishBank:
 stx CurrentBankC
 stx $5116
 lda #0
 sta $dfe0
 ldy #15
Ms8PublishByte:
 lda Ms8PublishCookie,y
 sta $dfe0,y
 dey
 bne Ms8PublishByte
 ldx CurrentBankC
 dex
 cpx #1
 bne Ms8PublishBank
 ldx #3
Ms8Release:
 stx CurrentBankC
 stx $5116
 lda #$a7
 sta $dfe0
 dex
 cpx #1
 bne Ms8Release
 jmp Ms8RestorePpu
Ms8Failed:
 ldx #3
Ms8Revoke:
 stx CurrentBankC
 stx $5116
 lda #0
 sta $dfe0
 dex
 cpx #1
 bne Ms8Revoke
Ms8RestorePpu:
 Ms8Far X5PublishChr,62
 lda Mirror_PPUCTRL
 sta $2000
 bit $2002
 lda HorizontalScroll
 sta $2005
 lda VerticalScroll
 sta $2005
 lda R3
 cmp #1
 rts
Ms8PublishCookie:.incbin "cookie.bin"
Ms8FinishEnd:
