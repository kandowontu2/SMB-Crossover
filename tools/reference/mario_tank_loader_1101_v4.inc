; Real-ROM loader/retirement proposal. No shared source/admission is changed.
; CHR501 is a granted immutable1024B code carrier; CHR502 is shoe/pickup art.
; PhysicalRAM2 D600..D9FF and C880..88B remain conditional/ungranted.
; Ordinary FarCallCommon ABI: SMC operands are scratch; caller AXYP/R0..R7,
; Cmapping/shadow and Reload are restored. Exact final Main/ISR proof remains.

.segment "MT_LOAD_OUTER"
MtColdLoadV4:
 php
 pha
 txa
 pha
 tya
 pha
 lda R0
 pha
 lda R1
 pha
 lda CurrentBankC
 pha
 lda ReloadCHRBank
 pha
 MtV4Far MtColdAllowedV4,MT_PRECHECK_BANK
 bcc MtLoadRestoreV4
 sei
 lda #0
 sta ReloadCHRBank             ; native lag-NMI BankSwitchCHR is now fenced
 MtV4Far X5PublishChr,X5PublishChr_BANK
 MtV4Far MtLoadWorkerV4,MT_INIT_BANK
 MtV4Far X5PublishChr,X5PublishChr_BANK
 lda Mirror_PPUCTRL
 sta $2000
 bit $2002
 lda HorizontalScroll
 sta $2005
 lda VerticalScroll
 sta $2005
MtLoadRestoreV4:
 pla
 sta ReloadCHRBank
 pla
 sta CurrentBankC
 sta $5116
 pla
 sta R1
 pla
 sta R0
 pla
 tay
 pla
 tax
 pla
 plp
 rts
MtColdLoadEndV4:

.segment "MT_LOAD_PRECHECK"
MtColdAllowedV4:
 lda SelectedCharacter
 bne MtColdNoV4
 lda MarioVariant
 cmp #7
 bne MtColdNoV4
 lda OperMode
 cmp #1
 bne MtColdNoV4
 lda FamilyMainCommit
 and #1
 beq MtColdNoV4
 lda DisableScreenFlag
 beq MtColdNoV4
 lda Mirror_PPUMASK
 and #$18
 bne MtColdNoV4
 lda NmiDisable
 bpl MtColdNoV4
 MtV4Far MtRomReadyV3,MT_READY_BANK
 bcs MtColdNoV4                 ; complete warm owner is left untouched
 MtV4Far KrRetire,KrRetire_BANK  ; exact old owner/HUD cancellation before reuse
 sec
 rts
MtColdNoV4:
 clc
 rts
MtColdAllowedEndV4:

.segment "MT_LOAD_INIT"
MtLoadWorkerV4:
 lda #2
 sta CurrentBankC
 sta $5116
 lda #0
 sta $dfe0                     ; no complete Tank/Karnov2 header survives
 ldx #11
MtClearContextV4:
 sta $c880,x
 cmp $c880,x
 bne MtLoadFailV4
 dex
 bpl MtClearContextV4
 lda Mirror_PPUCTRL
 and #$fb                      ; byte increment, genuine8x16 sprite mode
 ora #$20
 sta $2000
 MtV4Far MtCopyRowV4,MT_COPY_BANK
 bcc MtLoadFailV4
 MtV4Far MtPublishHeaderV4,MT_PUBLISH_BANK
 rts
MtLoadFailV4:
 lda #0
 sta $dfe0
 clc
 rts
MtLoadWorkerEndV4:

.segment "MT_LOAD_COPY"
MtCopyRowV4:
 lda #0
 sta R0
 lda #$d6
 sta R1
 MtV4Far MtMapCodeV4,MT_MAP_BANK
 ldx #4
MtCopyByteV4:
 lda $2007
 sta (R0),y
 iny
 bne MtCopyByteV4
 inc R1
 dex
 bne MtCopyByteV4
 lda #$d6
 sta R1
 MtV4Far MtMapCodeV4,MT_MAP_BANK
 ldx #4
MtVerifyByteV4:
 lda $2007
 cmp (R0),y
 bne MtCopyNoV4
 iny
 bne MtVerifyByteV4
 inc R1
 dex
 bne MtVerifyByteV4
 sec
 rts
MtCopyNoV4:
 clc
 rts
MtCopyRowEndV4:

.segment "MT_LOAD_MAP"
MtMapCodeV4:
 lda #1
 sta $5130
 lda #245
 sta $512b
 bit $2002
 lda #$0c
 sta $2006
 lda #0
 sta $2006
 lda $2007                     ; original buffered PPU read, not payload
 ldy #0
 rts
MtMapCodeEndV4:

.segment "MT_LOAD_PUBLISH"
MtPublishHeaderV4:
 ldx #15
MtPublishByteV4:
 lda MtCookieV4,x
 sta $dfe0,x
 cmp $dfe0,x
 bne MtPublishNoV4
 dex
 bne MtPublishByteV4
 lda #$a7
 sta $dfe0                     ; magic is the final publication store
 cmp $dfe0
 bne MtPublishNoV4
 sec
 rts
MtPublishNoV4:
 lda #0
 sta $dfe0
 clc
 rts
MtCookieV4:
 .byte MT_COOKIE_BYTES
MtPublishEndV4:

.segment "MT_LOAD_RETIRE"
MtRetireV4:
 php
 pha
 MtV4Far MtRomHeaderOnlyV4,MT_READY_BANK
 bcc MtRetireDoneV4
 lda CurrentBankC
 pha
 lda #2
 sta CurrentBankC
 sta $5116
 lda #0
 sta $dfe0                     ; only exact complete Tank header is retired
 pla
 sta CurrentBankC
 sta $5116
MtRetireDoneV4:
 pla
 plp
 rts
MtRetireEndV4:

.segment "MT_MENU_RESOLVE"
MtMenuResolveV4:
 MtV4Far MtRetireV4,MT_RETIRE_BANK
 MtV4FarTail KrMenuResolve,KrMenuResolve_BANK
MtMenuResolveEndV4:
