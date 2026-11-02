; Private measured factor proposal. This is not an owner gate or loader API.
; Caller already owns forced-blank commit, saved R0..7/maps/SMC, invalidated
; both owner headers and SEI. R3/R4 point to immutable resident descriptor:
; rows,codeRows,zero256Bpages,metadataHi, then(lo,upper) physical-page pairs.
; The caller retains authentication, header commit and PPU/map restoration.
.segment "BB_COLD_PROPOSAL"
.export BbColdWorker,BbColdMapRow,BbColdWorkerEnd,BbColdMainEnd,BbColdMapEnd
BbColdWorker:
.ifndef BB_COLD_TRUSTED_CALLER
 lda OperMode
 cmp #1
 jne BbColdNo
 lda FamilyMainCommit
 and #1
 jeq BbColdNo
 lda DisableScreenFlag
 jeq BbColdNo
 lda Mirror_PPUMASK
 and #$18
 jne BbColdNo
 lda NmiDisable
 jpl BbColdNo
.endif
 lda #2
 sta CurrentBankC
 sta $5116
 lda #0
 sta R0
 lda #$c0
 sta R1
 ldy #2
 lda (R3),y
 tax
 ldy #0
BbColdZeroPage:
 lda #0
BbColdZeroByte:
 sta (R0),y
 cmp (R0),y
 jne BbColdNo
 iny
 bne BbColdZeroByte
 inc R1
 dex
 bne BbColdZeroPage
 lda Mirror_PPUCTRL
 and #$fb
 ora #$20
 sta $2000
 lda #0
 sta R2
BbColdCopyRow:
 lda R2
 ldy #1
 cmp (R3),y
 bcc BbColdCodeRow
 sbc (R3),y
 asl
 asl
.ifdef BB_COLD_FIXED_META_D0
 ora #$d0
.else
 sta R7
 ldy #3
 lda (R3),y
 ora R7
.endif
 sta R1
 lda #2
 bne BbColdMapped
BbColdCodeRow:
 asl
 asl
 ora #$c0
 sta R1
 lda #3
BbColdMapped:
 sta CurrentBankC
 sta $5116
 jsr BbColdMapRow
 ldx #4
BbColdCopyByte:
 lda $2007
 sta (R0),y
 iny
 bne BbColdCopyByte
 inc R1
 dex
 bne BbColdCopyByte
 lda R1
 sec
 sbc #4
 sta R1
 jsr BbColdMapRow
 ldx #4
BbColdVerifyByte:
 lda $2007
 cmp (R0),y
 bne BbColdNo
 iny
 bne BbColdVerifyByte
 inc R1
 dex
 bne BbColdVerifyByte
 inc R2
 ldy #0
 lda R2
 cmp (R3),y
 bne BbColdCopyRow
 sec
 rts
BbColdNo:
 clc
 rts
BbColdMainEnd:
.ifdef BB_COLD_SPLIT_MAP
.segment "BB_COLD_MAP"
.endif
BbColdMapRow:
 lda R2
 asl
 clc
 adc #5
 tay
 lda (R3),y
 sta $5130
 dey
 lda (R3),y
 sta $5123
 ldy #0
 sty $5130
 bit $2002
 lda #$0c
 sta $2006
 sty $2006
 lda $2007
 rts
BbColdMapEnd:
BbColdWorkerEnd:
.segment "BB_COLD_PROPOSAL"
.export BbColdDescriptors,BbColdBBDescriptor
BbColdDescriptors:
.ifndef BB_COLD_BB_ONLY
.ifndef BB_COLD_EX_BB_ONLY
.export BbColdShDescriptor
BbColdShDescriptor:
 .byte 9,7,32,$d0
 .word 506,507,508,509,510,513,515,516,517
.endif
.export BbColdExDescriptor
BbColdExDescriptor:
 .byte 8,6,32,$d0
 .word 728,729,730,731,732,733,734,735
.endif
BbColdBBDescriptor:
 .byte 9,8,4,$d0
 .word 301,305,337,362,363,440,819,666,441
.export BbColdProposalEnd
BbColdProposalEnd:
