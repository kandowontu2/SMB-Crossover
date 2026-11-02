; Pure ROM-resident proposal. No PRG interval is claimed by this include.
; Both complete headers must authenticate before the caller maps RAM3 code.
; Cold entry is only from the existing forced-blank FamilyMainCommit boundary.
.export ShLoad,ShCheckCode,ShRetire,ShCookie,ShResidentEnd
.macro ShRomFar Target,Bank
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #Bank
 jsr FarCallCommon
.endmacro
.segment "SHINOBI_RESIDENT"
ShCheckCode:
 php
 pha
 txa
 pha
 lda CurrentBankC
 pha
 lda SelectedCharacter
 cmp #36
 bne ShCheckNo
 ldx #3
ShCheckBank:
 stx CurrentBankC
 stx $5116
 ldx #15
ShCheckByte:
 lda $dfe0,x
 cmp ShCookie,x
 bne ShCheckNo
 dex
 bpl ShCheckByte
 ldx CurrentBankC
 dex
 cpx #1
 bne ShCheckBank
 tsx
 lda $0104,x
 ora #1
 bne ShCheckSet
ShCheckNo:
 tsx
 lda $0104,x
 and #$fe
ShCheckSet:
 sta $0104,x
 pla
 sta CurrentBankC
 sta $5116
 pla
 tax
 pla
 plp
 rts

ShRetire:
 php
 pha
 txa
 pha
 lda CurrentBankC
 pha
 ldx #3
ShRetireBank:
 stx CurrentBankC
 stx $5116
 ldx #15
ShRetireByte:
 lda $dfe0,x
 cmp ShCookie,x
 bne ShRetireNext
 dex
 bpl ShRetireByte
 lda #0
 sta $dfe0
ShRetireNext:
 ldx CurrentBankC
 dex
 cpx #1
 bne ShRetireBank
 pla
 sta CurrentBankC
 sta $5116
 pla
 tax
 pla
 plp
 rts

ShLoad:
 php
 pha
 txa
 pha
 tya
 pha
 ldx #0
ShLoadSaveZp:
 lda R0,x
 pha
 inx
 cpx #8
 bne ShLoadSaveZp
 ldx #0
ShLoadSaveSmc:
 ldy ShSavedSmcOffsets,x
 lda $0100,y
 pha
 inx
 cpx #5
 bne ShLoadSaveSmc
 lda CurrentBankC
 pha
 lda ReloadCHRBank
 pha
 lda SelectedCharacter
 cmp #36
 jne ShLoadNo
 lda OperMode
 cmp #1
 jne ShLoadNo
 lda FamilyMainCommit
 and #1
 jeq ShLoadNo
 lda DisableScreenFlag
 jeq ShLoadNo
 lda Mirror_PPUMASK
 and #$18
 jne ShLoadNo
 lda NmiDisable
 jpl ShLoadNo
 jsr ShCheckCode
 jcs ShLoadYes
 sei
 lda #0
 sta ReloadCHRBank
 ShRomFar X5PublishChr,Bank_X5PublishChr
 jsr ShInvalidateBoth
 ; Clear and read back the complete conditional C2 state/context bank.
 lda #2
 sta CurrentBankC
 sta $5116
 lda #0
 sta R0
 lda #$c0
 sta R1
 ldy #0
 ldx #32
ShZeroPage:
 lda #0
ShZeroByte:
 sta (R0),y
 cmp (R0),y
 jne ShLoadFailed
 iny
 bne ShZeroByte
 inc R1
 dex
 bne ShZeroPage
 lda Mirror_PPUCTRL
 and #$fb
 ora #$20
 sta $2000
 lda #0
 sta R2
ShCopyRow:
 lda R2
 cmp #7
 bcc ShCodeRow
 sec
 sbc #7
 asl
 asl
 ora #$d0
 sta R1
 lda #2
 bne ShRowMapped
ShCodeRow:
 asl
 asl
 ora #$c0
 sta R1
 lda #3
ShRowMapped:
 sta CurrentBankC
 sta $5116
 jsr ShMapRow
 ldx #4
ShCopyByte:
 lda $2007
 sta (R0),y
 iny
 bne ShCopyByte
 inc R1
 dex
 bne ShCopyByte
 lda R1
 sec
 sbc #4
 sta R1
 jsr ShMapRow
 ldx #4
ShVerifyByte:
 lda $2007
 cmp (R0),y
 bne ShLoadFailed
 iny
 bne ShVerifyByte
 inc R1
 dex
 bne ShVerifyByte
 inc R2
 lda R2
 cmp #9
 bne ShCopyRow
 ldx #3
ShPublishBank:
 stx CurrentBankC
 stx $5116
 ldx #15
ShPublishByte:
 lda ShCookie,x
 sta $dfe0,x
 dex
 bne ShPublishByte
 ldx CurrentBankC
 dex
 cpx #1
 bne ShPublishBank
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
 jsr ShRestorePpu
ShLoadYes:
 tsx
 lda $0113,x
 ora #1
 bne ShLoadSet
ShLoadFailed:
 jsr ShInvalidateBoth
 jsr ShRestorePpu
ShLoadNo:
 tsx
 lda $0113,x
 and #$fe
ShLoadSet:
 sta $0113,x
 pla
 sta ReloadCHRBank
 pla
 sta CurrentBankC
 sta $5116
 ldx #4
ShLoadRestoreSmc:
 ldy ShSavedSmcOffsets,x
 pla
 sta $0100,y
 dex
 bpl ShLoadRestoreSmc
 ldx #7
ShLoadRestoreZp:
 pla
 sta R0,x
 dex
 bpl ShLoadRestoreZp
 pla
 tay
 pla
 tax
 pla
 plp
 rts
ShInvalidateBoth:
 ldx #3
ShInvalidateBank:
 stx CurrentBankC
 stx $5116
 lda #0
 sta $dfe0
 dex
 cpx #1
 bne ShInvalidateBank
 rts
ShMapRow:
 ldx R2
 lda ShCarrierUpper,x
 sta $5130
 lda ShCarrierLow,x
 sta $5123
 lda #0
 sta $5130
 bit $2002
 lda #$0c
 sta $2006
 lda #0
 sta $2006
 lda $2007                  ; mandatory buffered-read dummy
 ldy #0
 rts
ShRestorePpu:
 ShRomFar X5PublishChr,Bank_X5PublishChr
 lda Mirror_PPUCTRL
 sta $2000
 bit $2002
 lda HorizontalScroll
 sta $2005
 lda VerticalScroll
 sta $2005
 rts
ShSavedSmcOffsets:
 .byte <(NextBank_SMC+1),<(SafecallA_SMC+1),<(FarcallJmpTarget_SMC+1),<(FarcallJmpTarget_SMC+2),<(SafereturnA_SMC+1)
ShCarrierLow:.byte <506,<507,<508,<509,<510,<513,<515,<516,<517
ShCarrierUpper:.byte >506,>507,>508,>509,>510,>513,>515,>516,>517
ShCookie:.incbin "shinobi-cookie.bin"
ShResidentEnd:
