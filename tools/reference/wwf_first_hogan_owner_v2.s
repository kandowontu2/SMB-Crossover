; Private first-Hogan physical owner APIs. No shared hook or audio gate.
.setcpu "6502"
.macpack longbranch
.import SelectedCharacter,FmGroups,FamilyMainCommit,OperMode,GamePauseStatus
.import Mirror_PPUMASK,Mirror_PPUCTRL,NmiDisable,DisableScreenFlag
.import CurrentBank,CurrentBankC,ReloadCHRBank,X5PublishChr
.import CurrentCHRBank,X5ChrMode,X5WideChrActive,ChrPhysicalMap
.import HorizontalScroll,VerticalScroll,FarCallCommon,SafecallA_SMC,FarcallJmpTarget_SMC
.import __SMCCODE_RUN__,__SMCCODE_SIZE__
.import WfHostCold,WfHostReady,WfOwnerCookie,WfExpectedCookie
.importzp R0,R1,R2,R3,R4,R5,R6,R7
.export WfLoad,WfCheck,WfRetire,WfConstructCold,WfRuntimeUnavailable
.export WfCopyCore,WfCopyPage,WfVerifyPage,WfPublishCookie,WfSourcePage

; 4 native AXYP +8 scoped bytes +33 actual transport bytes +C +reload.
WF_SAVED_P=47
.assert __SMCCODE_SIZE__=33,lderror,"Actual current transport image"
.macro SaveOwner
 php
 pha
 txa
 pha
 tya
 pha
 ldx #0
:
 lda R0,x
 pha
 inx
 cpx #8
 bcc :-
 ldx #0
:
 lda __SMCCODE_RUN__,x
 pha
 inx
 cpx #33
 bcc :-
 lda CurrentBankC
 pha
 lda ReloadCHRBank
 pha
.endmacro

.segment "WF_ROM_A"
WfIdentity:
 lda SelectedCharacter
 cmp #29
 bne WfIdentityNo
 lda FmGroups
 and #7
 bne WfIdentityNo             ; first original Hogan only
 lda OperMode
 cmp #1
 bne WfIdentityNo
 lda FamilyMainCommit
 and #1
 beq WfIdentityNo
 sec
 rts
WfIdentityNo:clc
 rts
WfBlank:
 jsr WfIdentity
 bcc WfBlankNo
 lda Mirror_PPUMASK
 and #$18
 bne WfBlankNo
 lda DisableScreenFlag
 beq WfBlankNo
 lda NmiDisable
 bpl WfBlankNo
 lda GamePauseStatus
 and #1
 bne WfBlankNo
 sec
 rts
WfBlankNo:clc
 rts

; Pure ROM reads of raw C2 cookie; never a cache opcode.
WfAuthC2:
 jsr WfIdentity
 bcc WfAuthNo
 lda #2
 sta CurrentBankC
 sta $5116
 ldx #15
WfAuthByte:
 lda WfOwnerCookie,x
 cmp WfExpectedCookie,x
 bne WfAuthNo
 dex
 bpl WfAuthByte
 sec
 rts
WfAuthNo:clc
 rts

WfCheck:
 SaveOwner
 jsr WfAuthC2
 jmp WfReturnC

WfLoad:
 SaveOwner
 jsr WfBlank
 jcc WfReturnC
 sei
 cld
 lda #0
 sta ReloadCHRBank
 lda #.lobyte(.bank(WfCopyCore)|$80)
 sta CurrentBankC
 sta $5116
 jsr WfCopyCore
 jmp WfReturnC

; Explicit cold API only. Before the first C2 opcode the ROM has checked
; selected identity, family/class/version/full fingerprint and busy epoch.
WfConstructCold:
 SaveOwner
 jsr WfBlank
 jcc WfReturnC
 jsr WfAuthC2
 jcc WfReturnC
 lda WfHostReady
 cmp #$a7
 beq WfConstructDone
 lda #5
 sta SafecallA_SMC+1
 lda #<WfHostCold
 sta FarcallJmpTarget_SMC+1
 lda #>WfHostCold
 sta FarcallJmpTarget_SMC+2
 ; Cold A=original Hogan, X=opponent Ted, Y=deterministic source seed0.
 ldx #0
 ldy #0
 lda #3
 jsr FarCallCommon
 lda #$a7
 sta WfHostReady
WfConstructDone:
 sec
 jmp WfReturnC

; Full preserving independent retirement. Caller must invoke this BEFORE
; foreign selected publication/overwrite. No such physical hook is installed.
WfRetire:
 SaveOwner
 lda #2
 sta CurrentBankC
 sta $5116
 lda $dfe1
 cmp #29
 bne :+
 lda #0
 sta $dfe0                    ; C2 validity FIRST
:
 lda #3
 sta CurrentBankC
 sta $5116
 lda $dfe1
 cmp #29
 bne :+
 lda #0
 sta $dfe0                    ; own raw3 marker only
:
 jmp WfReturnOriginal

WfRuntimeUnavailable:
 ; Ring/AI/audio callbacks still need their source-backed host phases.
 ; No public frame route is offered until those boundaries are complete.
 SaveOwner
 clc
 jmp WfReturnC

WfReturnC:
 tsx
 lda $0100+WF_SAVED_P,x
 and #$fe
 bcc :+
 ora #1
:
 sta $0100+WF_SAVED_P,x
WfReturnOriginal:
 pla
 sta ReloadCHRBank
 pla
 sta CurrentBankC
 sta $5116
 ldx #32
:
 pla
 sta __SMCCODE_RUN__,x
 dex
 bpl :-
 ldx #7
:
 pla
 sta R0,x
 dex
 bpl :-
 pla
 tay
 pla
 tax
 pla
 plp
 rts

; Each actual resident native-proxy phase opens a validated C2 view first.
.macro GuardedProxy Public,Raw
 .export Public
Public:
 SaveOwner
 jsr WfAuthC2
 bcc :+
 lda WfHostReady
 cmp #$a7
 bne :+
 ; Restore source native AXYP from the actual owner's saved frame before
 ; the existing proxy wrapper receives it. It saves its own scoped bytes.
 tsx
 lda $012e,x
 pha
 lda $012b,x
 tay
 lda $012c,x
 pha
 lda $012d,x
 tax
 pla
 ; X in the original packet is below A; use the temporary CPU stack only.
 ; This sequence is generated below by the builder with exact offsets.
 .error "Builder must expand GuardedProxy body"
:
 clc
 jmp WfReturnC
.endmacro
; WF_GUARDED_PROXY_GENERATED

.export WfResidentAEnd
WfResidentAEnd:
.assert *<=$b800,lderror,"Granted A96 phase partition"

.segment "WF_ROM_C"
WfCopyCore:
 lda CurrentBank
 pha
 ; Real native checkpoint from stable C96, before any CHR borrowing.
 lda #.lobyte(.bank(X5PublishChr)|$80)
 sta CurrentBank
 sta $5115
 jsr X5PublishChr
 ldx #2
WfInvalidatePrior:
 stx CurrentBank
 stx $5115
 lda #0
 sta $bfe0                    ; C2 first, then raw3, BEFORE first copy
 inx
 cpx #4
 bne WfInvalidatePrior
 lda Mirror_PPUCTRL
 and #$fb
 ora #$20
 sta $2000
 lda #0
 sta R0
 sta R2                       ; source1KiB page0..23
 lda #1
 sta R3                       ; actual destination A1, A2, A3
WfCopyBank:
 lda R3
 sta CurrentBank
 sta $5115
 lda #$a0
 sta R1
WfCopyPage:
 jsr WfSourcePage
 ldx #4
:
 lda $2007
 sta (R0),y
 iny
 bne :-
 inc R1
 dex
 bne :-
 lda R1
 sec
 sbc #4
 sta R1
 jsr WfSourcePage
 ldx #4
WfVerifyPage:
 lda $2007
 cmp (R0),y
 jne WfCopyFailed
 iny
 bne WfVerifyPage
 inc R1
 dex
 bne WfVerifyPage
 inc R2
 lda R2
 cmp #24
 beq WfCopyVerified
 lda R1
 cmp #$c0
 bne WfCopyPage
 inc R3
 jmp WfCopyBank
WfCopyVerified:
 ; Publish raw3 marker first, then full C2 cookie VALID last.
 ldx #3
WfPublishCookie:
 stx CurrentBank
 stx $5115
 ldy #15
:
 lda WfCookieC,y
 sta $bfe0,y
 dey
 bne :-
 lda #$a7
 sta $bfe0
 dex
 cpx #2
 beq WfPublishCookie
 sec
 bcs WfRestorePublication
WfCopyFailed:
 lda #2
 sta CurrentBank
 sta $5115
 lda #0
 sta $bfe0
 lda #3
 sta CurrentBank
 sta $5115
 lda #0
 sta $bfe0
 clc
WfRestorePublication:
 php
 lda X5WideChrActive
 beq WfLegacy11
 lda X5ChrMode+11
 bmi WfDirect11
WfLegacy11:
 lda #0
 sta $5130
 ldy CurrentCHRBank+11
 lda ChrPhysicalMap,y
 jmp WfWrite11
WfDirect11:
 and #3
 sta $5130
 lda CurrentCHRBank+11
WfWrite11:
 sta $512b
 lda #0
 sta $5130
 bit $2002
 lda Mirror_PPUCTRL
 sta $2000
 lda HorizontalScroll
 sta $2005
 lda VerticalScroll
 sta $2005
 plp
 pla
 sta CurrentBank
 sta $5115
 rts
WfSourcePage:
 lda #2
 sta $5130
 lda R2
 clc
 adc #<629
 sta $512b
 bit $2002
 lda #$0c
 sta $2006
 ldy #0
 sty $2006
 lda $2007                    ; discard true PPU buffered read
 rts
WfCookieC:
; WF_COOKIE_C_GENERATED
.export WfResidentCEnd
WfResidentCEnd:
.assert *<=$e000,lderror,"Granted stable C96 phase partition"
