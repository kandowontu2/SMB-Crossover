; Reviewed physical85 gap, run A85:B33A; no shared ingress/admission edits.
.setcpu "6502"
.macpack longbranch
.import SelectedCharacter,FmAlts,OperMode,FamilyMainCommit,DisableScreenFlag,NmiDisable
.import Mirror_PPUMASK,Mirror_PPUCTRL,HorizontalScroll,VerticalScroll,ReloadCHRBank
.import CurrentBankC,CurrentPlayer,NumberofLives,WorldNumber,AreaAddrsLOffset
.import X5PublishChr,X5SetPhysicalChr,MetaspriteRenderLoop,FmQueueName,BmFresh,JnResetDispatch,BwMenuResolve,BwScene,HuNativeWorldPalette
.import SafecallA_SMC,FarcallJmpTarget_SMC,FarCallCommon,NextBank_SMC
.import Player_SprAttrib,ObjectMetasprite,SmPosePtr,VRAM_Buffer1,VRAM_Buffer1_Offset
.importzp Player_X_Position,Player_PageLoc,Player_Y_Position,Player_Y_HighPos
.importzp R0,R1,R2,R3,R4,R5,R6,R7
.export ThServiceVeneers,ThResidentStart,ThResidentEnd,ThLoad,ThCheckCode,ThCheck,ThRetire,ThSceneLoad
.export ThColdPrepare,ThColdPortrait,ThColors,ThFresh,ThScene,ThCookie,ThMenuResolve,ThSceneInit
.import ThCacheServices,ArGenCheckForeground,ArOwnServices,FwServiceVeneers
.export ThArExtended,ThGmHeadWithinOwn
.import ThLoadBank,ThLoadHigh,ThLoadCHR,ThLoadFill,ThBodyPage
.segment "THOMAS_RESIDENT"
ThResidentStart:
.macro ThFar Target,Mode
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(Target)|$80)
 .if .xmatch({Mode},{jmp})
 jmp FarCallCommon
 .else
 jsr FarCallCommon
 .endif
.endmacro
.macro Save
 php
 pha
 txa
 pha
 tya
 pha
.endmacro
.macro SaveAX
 php
 pha
 txa
 pha
.endmacro
.macro RestoreAX
 pla
 tax
 pla
 plp
.endmacro
.macro Restore
 pla
 tay
 pla
 tax
 pla
 plp
.endmacro
ThSelected:
 lda SelectedCharacter
 cmp #10
 bne No
 lda FmAlts
 and #$44
 cmp #$40
 bne No
 sec
 rts
No:clc
 rts
; Only the two signature headers are read. No selected state/opcode is read
; until BOTH complete16-byte signatures match the exact compiled producer.
ThCheckCode:
 php
 pha
 txa
 pha
 lda CurrentBankC
 pha
 jsr ThSelected
 bcc CheckNo
 ldx #3
CheckBank:
 stx CurrentBankC
 stx $5116
 ldx #15
CheckByte:
 lda $dfe0,x
 cmp ThCookie,x
 bne CheckNo
 dex
 bpl CheckByte
 lda CurrentBankC
 cmp #2
 beq CheckYes
 ldx #2
 bne CheckBank
CheckYes:
 tsx
 lda $0104,x
 ora #1
 bne CheckSet
CheckNo:
 tsx
 lda $0104,x
 and #$fe
CheckSet:
 sta $0104,x
 pla
 sta CurrentBankC
 sta $5116
 pla
 tax
 pla
 plp
 rts
; Active context check remains ROM-resident while inspecting selected C2.
ThCheck:
 jsr ThCheckCode
 bcc CheckReturn
 SaveAX
 lda CurrentBankC
 pha
 lda #2
 sta CurrentBankC
 sta $5116
 lda $c800
 cmp $c845
 bne EpochNo
 cmp $c844
 bne EpochNo
 cmp #$a7
 bne EpochNo
 lda CurrentPlayer
 cmp $c840
 bne EpochNo
 lda NumberofLives
 cmp $c841
 bne EpochNo
 lda WorldNumber
 cmp $c842
 bne EpochNo
 lda AreaAddrsLOffset
 cmp $c843
 bne EpochNo
 tsx
 lda $0104,x
 ora #1
 bne EpochSet
EpochNo:
 tsx
 lda $0104,x
 and #$fe
EpochSet:
 sta $0104,x
 pla
 sta CurrentBankC
 sta $5116
 RestoreAX
CheckReturn:rts

.res $c6-(*-ThResidentStart),$ff
ThServiceVeneers:
.repeat 36,I
 .if I=3
 jmp ThColdPrepare
 .elseif I=15
 jmp ThFresh
 .elseif I=17
 jmp ThColdPortrait
 .elseif I=18
 jmp ThName
 .elseif I=19
 jmp ThScene
 .elseif I=26
 jmp ThColors
 .elseif I=32
 jmp ThWorld
 .else
 jmp ThDispatch
 .endif
.endrepeat
ThUnavailable:clc
 rts

.assert .lobyte(ThServiceVeneers)=0,lderror,"Thomas shares genuine FF page-high transport"
.assert .hibyte(ThServiceVeneers)=.hibyte(FwServiceVeneers),lderror,"Shared high expression"
; Real JMP rows keep the original outer FarCallCommon frame. Capture the row
; offset before any SMC writer; nested CheckCode does not touch any SMC byte.
ThDispatch:
 Save
 lda FarcallJmpTarget_SMC+1
 sec
 sbc #<ThServiceVeneers
 pha
 cmp #9
 bcc DispatchBootstrap
 cmp #90
 beq DispatchBootstrap
 jsr ThCheck
 jmp DispatchChecked
DispatchBootstrap:
 jsr ThCheckCode
DispatchChecked:
 bcc DispatchNo
 pla
 sta FarcallJmpTarget_SMC+1
 lda #>ThCacheServices
 sta FarcallJmpTarget_SMC+2
 lda #3
 sta NextBank_SMC+1
 lda #2
 sta CurrentBankC
 sta $5116
 Restore
 jmp FarCallCommon+3
DispatchNo:
 pla
 tsx
 lda $0104,x
 and #$fe
 sta $0104,x
 Restore
 rts
; No foreign payload is written on retirement. Only a completed Thomas family
; header may lose validity. Called before resolved-owner publication/overwrites.
ThRetire:
 SaveAX
 lda CurrentBankC
 pha
 ldx #3
RetireBank:
 stx CurrentBankC
 stx $5116
 lda $dfe0
 cmp #$a7
 bne RetireNext
 lda $dfe1
 cmp #10
 bne RetireNext
 lda $dfe2
 cmp #$40
 bne RetireNext
 lda #0
 sta $dfe0
RetireNext:
 ldx CurrentBankC
 dex
 cpx #1
 bne RetireBank
 pla
 sta CurrentBankC
 sta $5116
 RestoreAX
 rts
ThFresh:
 ThFar BmFresh,jsr
 jmp ThRetire
ThScene:
 ThFar JnResetDispatch,jsr
 php
 pha
 jsr ThCheckCode
 bcc SceneDone
 lda CurrentBankC
 pha
 lda #2
 sta CurrentBankC
 sta $5116
 lda #0
 sta $c844                     ; force source context reconciliation next Main
 pla
 sta CurrentBankC
 sta $5116
SceneDone:
 pla
 plp
 rts
ThName:ThFar FmQueueName,jmp
ThWorld: ThFar HuNativeWorldPalette,jmp
ThMenuResolve:
 jsr ThRetire
 ThFar BwMenuResolve,jmp
ThSceneInit:
 ThFar BwScene,jsr
 php
 jsr ThLoad
 plp
 rts
ThSceneLoad: jmp ThLoad
; A85 remains mapped throughout all C2/C3 replacement and publication.
ThLoad:
 Save
 .repeat 8,I
 lda R0+I
 pha
 .endrepeat
 lda CurrentBankC
 pha
 lda ReloadCHRBank
 pha
 jsr ThSelected
 jcc LoadNo
 lda OperMode
 jeq LoadNo
 lda FamilyMainCommit
 and #1
 jeq LoadNo
 lda DisableScreenFlag
 jeq LoadNo
 lda Mirror_PPUMASK
 and #$18
 jne LoadNo
 lda NmiDisable
 jpl LoadNo
 jsr ThCheckCode
 jcs LoadYes
 sei
 lda #0
 sta ReloadCHRBank
 ThFar X5PublishChr,jsr
 ldx #3
Invalidate:
 stx CurrentBankC
 stx $5116
 lda #0
 sta $dfe0                     ; both cache validities invalidated FIRST
 dex
 cpx #1
 bne Invalidate
 lda Mirror_PPUCTRL
 and #$fb
 ora #$20
 sta $2000
 lda #0
 sta R2
LoadRow:
 ldx R2
 lda ThLoadBank,x
 sta CurrentBankC
 sta $5116
 lda ThLoadHigh,x
 sta R1
 lda #0
 sta R0
 lda ThLoadCHR,x
 cmp #$ff
 beq FillRow
 jsr MapRow
 ldx #4
Copy:
 lda $2007
 sta (R0),y
 iny
 bne Copy
 inc R1
 dex
 bne Copy
 lda R1
 sec
 sbc #4
 sta R1
 jsr MapRow
 ldx #4
Verify:
 lda $2007
 cmp (R0),y
 bne LoadFailed
 iny
 bne Verify
 inc R1
 dex
 bne Verify
 beq NextRow
FillRow:
 lda ThLoadFill,x
 sta R3
 ldy #0
 ldx #4
Fill:
 lda R3
 sta (R0),y
 cmp (R0),y
 bne LoadFailed
 iny
 bne Fill
 inc R1
 dex
 bne Fill
NextRow:
 inc R2
 lda R2
 cmp #16
 bne LoadRow
 ldx #3
PublishBank:
 stx CurrentBankC
 stx $5116
 ldx #15
Publish:
 lda ThCookie,x
 sta $dfe0,x
 dex
 bne Publish
 lda #$a7
 sta $dfe0                     ; C2 validity is the LAST payload write
 ldx CurrentBankC
 dex
 cpx #1
 bne PublishBank
 jsr RestorePPU
LoadYes:
 tsx
 lda $010e,x
 ora #1
 bne LoadSet
LoadFailed:
 jsr ThRetire
 jsr RestorePPU
LoadNo:
 tsx
 lda $010e,x
 and #$fe
LoadSet:
 sta $010e,x
 pla
 sta ReloadCHRBank
 pla
 sta CurrentBankC
 sta $5116
 .repeat 8,I
 pla
 sta R7-I
 .endrepeat
 Restore
 rts
MapRow:
 ldx R2
 lda #1
 sta $5130
 lda ThLoadCHR,x
 sta $512b
 bit $2002
 lda #$0c
 sta $2006
 lda #0
 sta $2006
 lda $2007
 ldy #0
 rts
RestorePPU:
 ThFar X5PublishChr,jsr
 lda Mirror_PPUCTRL
 sta $2000
 bit $2002
 lda HorizontalScroll
 sta $2005
 lda VerticalScroll
 sta $2005
 rts
ThColors:
 SaveAX
 jsr ThSelected
 bcc ColorsDone
 jsr ThLoad                    ; active screen rejects copying; colors still queue
 ldx VRAM_Buffer1_Offset
 cpx #72
 bcs ColorsDone
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 lda #$27
 sta VRAM_Buffer1+3,x
 lda #$30
 sta VRAM_Buffer1+4,x
 lda #$0f
 sta VRAM_Buffer1+5,x
 lda #0
 sta VRAM_Buffer1+6,x
 txa
 clc
 adc #6
 sta VRAM_Buffer1_Offset
ColorsDone:
 RestoreAX
 rts
ThColdPrepare:
 Save
 jsr ThSelected
 bcc PrepareDone
 ldy #0
 lda #<ThBodyPage
 ldx #>ThBodyPage
 ThFar X5SetPhysicalChr,jsr
PrepareDone:
 Restore
 rts
; ROM-only exact standing record. No cold hover read/constructor in C2/A3.
ThColdPortrait:
 Save
 .repeat 8,I
 lda R0+I
 pha
 .endrepeat
 lda CurrentBankC
 pha
 jsr ThSelected
 bcc PortraitDone
 jsr ThColdPrepare
 lda #$d5
 sta CurrentBankC
 sta $5116
 lda #<(ThStanding+$2000)
 sta R0
 lda #>(ThStanding+$2000)
 sta R1
 lda Player_X_Position
 sec
 sbc #16
 sta R4
 lda #0
 sbc #0
 sta R5
 lda Player_Y_Position
 sec
 sbc #49
 sta R6
 lda #1
 sbc #0
 sta R7
 lda Player_SprAttrib
 and #$20
 sta R3
 ThFar MetaspriteRenderLoop,jsr
PortraitDone:
 pla
 sta CurrentBankC
 sta $5116
 .repeat 8,I
 pla
 sta R7-I
 .endrepeat
 Restore
 rts
; Proposed private common funding: actual Arthur selected-only checker moved
; as source, with true live imports; sourceA remains in original SafecallA.
ThArExtended:
 lda CurrentBankC
 pha
 lda #.lobyte(.bank(ArGenCheckForeground)|$80)
 sta CurrentBankC
 sta $5116
 jsr ArGenCheckForeground
 pla
 sta CurrentBankC
 sta $5116
 bcs ThArCookieReady
 ldy #36
ThArCookieReady:
 lda #>ArOwnServices
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(ArOwnServices)|$80)
 rts
; Exact eight genuine original Gimmick head-within bytes, moved only after
; the genuine Main table/call consumers have been source-rebound.
ThGmHeadWithinOwn:
 lda Player_Y_Position
 clc
 adc #18
 cmp #32
 rts
ThStanding:
.include "standing.inc"
ThCookie:
.incbin "cookie.bin"
ThResidentEnd:
.assert ThResidentStart=$b33a,lderror,"Exact reviewed Thomas resident origin"
.assert ThResidentEnd<=$b900,lderror,"Thomas1478B resident grant"
