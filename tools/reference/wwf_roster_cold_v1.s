.setcpu "6502"
.macpack longbranch
.import CurrentBank,CurrentBankC,FmGroups,WfHoganMetadata
.import WfIdleLow,WfIdleHigh,WfIdleBanks,WfIdlePages
.import Player_X_Position,Player_Y_Position,MetaspriteRenderLoop
.import WfMapBodyPage,FarCallCommon,FarcallJmpTarget_SMC,SafecallA_SMC
.importzp R0,R1,R2,R3,R4,R5,R6,R7
.export WfLoadRosterMeta,WfPageSourceTable,WfColdBody
.segment "WF_ROM_C"
WfLoadRosterMeta:
 lda #2
 sta CurrentBank
 sta $5115
 lda #<(WfHoganMetadata-$2000)
 sta R0
 lda #>(WfHoganMetadata-$2000)
 sta R1
 lda FmGroups
 and #7
 asl
 tax
 lda WfMetadataOffsets,x
 sta R3
 lda WfMetadataOffsets+1,x
 pha
 lsr
 lsr
 clc
 adc #<658
 sta R2
 pla
 and #3
 sta R4
 jsr WfMetaSource
MetaByte:
 ldy #0
 lda $2007
 sta (R0),y
 cmp (R0),y
 bne MetaFailed
 inc R0
 bne :+
 inc R1
:
 lda R0
 cmp #<(WfHoganMetadata-$2000+1687)
 bne MoreBytes
 lda R1
 cmp #>(WfHoganMetadata-$2000+1687)
 beq MetaDone
MoreBytes:
 inc R3
 bne MetaByte
 inc R4
 lda R4
 cmp #4
 bne MetaByte
 lda #0
 sta R4
 inc R2
 jsr WfMetaSource
 jmp MetaByte
MetaDone:sec
 rts
MetaFailed:clc
 rts
WfMetaSource:
 lda R2
 sta $512b
 bit $2002
 lda R4
 ora #$0c
 sta $2006
 lda R3
 sta $2006
 lda $2007
 rts
WfPageSourceTable:
.incbin "wf-page-sources.bin"
WfMetadataOffsets:
.incbin "wf-meta-offsets.bin"

.segment "WF_ALIAS_A"
; Outer runtime has saved R0..7, SMC, mapper C and incoming registers.
WfColdBody:
 lda #$c1                    ; data0 physical65, genuine C view
 sta CurrentBankC
 sta $5116
 lda FmGroups
 and #7
 tax
 lda WfIdlePages+$2000,x
 jsr WfMapBodyPage
 lda FmGroups
 and #7
 tax
 lda WfIdleLow+$2000,x
 sta R0
 lda WfIdleHigh+$2000,x
 sta R1
 lda WfIdleBanks+$2000,x
 sta CurrentBankC
 sta $5116
 lda Player_X_Position
 sta R4
 lda #0
 sta R5
 sta R3
 lda Player_Y_Position
 clc
 adc #24
 sta R6
 lda #1
 adc #0
 sta R7
 sta SafecallA_SMC+1
 lda #<MetaspriteRenderLoop
 sta FarcallJmpTarget_SMC+1
 lda #>MetaspriteRenderLoop
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(MetaspriteRenderLoop)|$80)
 jsr FarCallCommon
 rts
