; Private typed cold staging only: forcedblank, SEI, both headers invalid,
; previous foreign owner retired. Resident FarCallCommon enters BOOT in RAM2
; while mapping RAM3 into A000. The common worker supplies exactly the two
; declared bootstrap CHR rows; this component does not grant that routing.
.setcpu "6502"
.macpack longbranch
.segment "BOOT"
.export PpColdBoot,PpColdBootEnd
PpColdBoot:
 php
 pla
 and #4
 beq BootFailed
 lda SelectedCharacter
 cmp #38
 bne BootFailed
 lda DisableScreenFlag
 beq BootFailed
 lda Mirror_PPUMASK
 and #$18
 bne BootFailed
 lda NmiDisable
 bpl BootFailed
 lda $dfe0
 ora $bfe0
 bne BootFailed
 lda $c0ab
 ora $c60e
 bne BootFailed
 ldx #0
BootPage0:
 lda PpColdBootEnd,x
 sta $c100,x
 cmp $c100,x
 bne BootFailed
 inx
 bne BootPage0
BootPage1:
 lda PpColdBootEnd+$100,x
 sta $c200,x
 cmp $c200,x
 bne BootFailed
 inx
 bne BootPage1
BootDecoder:
 lda $d160,x
 sta $c000,x
 cmp $c000,x
 bne BootFailed
 inx
 cpx #DecoderBytes
 bne BootDecoder
 jmp PpColdRun
BootFailed:
 clc
 rts
PpColdBootEnd:

.segment "WORKER"
.export PpColdRun,PpColdWorkerEnd
PpColdRun:
 ldy #0
 jsr Stage
 jsr PpLdDecode
 ldy #8
 jsr Stage
 jsr PpLdDecode
 ldy #16
 jsr Stage
 ; State output overwrites this worker. The decoder is still below C100,
 ; and returns directly into the already decoded RAM3 finalizer.
 lda #>(PpHostColdFinalize-1)
 pha
 lda #<(PpHostColdFinalize-1)
 pha
 jmp PpLdDecode
Stage:
 sty ConfigIndex
 lda SrcPage
 sta SavedPage
 lda SrcLo
 sta SavedLo
 lda SrcHi
 sta SavedHi
 lda #$91                    ; STA(R0),Y, then independent reread pass CMP
 sta DataOp
StageAgain:
 ldy ConfigIndex
 lda Config,y
 sta PpLdLoad+1
 sta R0
 iny
 lda Config,y
 sta PpLdLoad+2
 sta R1
 iny
 lda Config,y
 sta OutLo
 iny
 lda Config,y
 sta OutHi
 iny
 lda Config,y
 sta Remaining
 iny
 lda Config,y
 sta Remaining+1
 iny
 lda Config,y
 sta PpLdRemain
 iny
 lda Config,y
 sta PpLdRemain+1
 ldy #0
 jsr MapSource
StageByte:
 jsr ReadSource
DataOp:sta (R0),y
 cmp (R0),y
 bne StageFailed
 inc R0
 bne StagePointer
 inc R1
 lda R1
 cmp #$dc
 bne StagePointer
 lda #$c3
 sta R1
StagePointer:
 lda Remaining
 bne :+
 dec Remaining+1
:
 dec Remaining
 lda Remaining
 ora Remaining+1
 bne StageByte
 lda DataOp
 cmp #$d1
 beq StageDone
 lda #$d1                    ; verify with a fresh physical PPU read
 sta DataOp
 lda SavedPage
 sta SrcPage
 lda SavedLo
 sta SrcLo
 lda SavedHi
 sta SrcHi
 jmp StageAgain
StageDone:
 lda OutLo
 sta R0
 lda OutHi
 sta R1
 rts
StageFailed:
 pla                         ; discard Stage return, return C0 to resident
 pla
 clc
 rts
ReadSource:
 lda SrcHi
 cmp #$10
 bne SourceReady
 inc SrcPage
 lda #$0c
 sta SrcHi
 jsr MapSource
SourceReady:
 lda $2007
 inc SrcLo
 bne :+
 inc SrcHi
:
 rts
MapSource:
 ldx SrcPage
 lda PhysicalHi,x
 sta $5130
 lda PhysicalLo,x
 sta $5123
 lda #0
 sta $5130
 bit $2002
 lda SrcHi
 sta $2006
 lda SrcLo
 sta $2006
 lda $2007
 rts
ConfigIndex:.byte 0
OutLo:.byte 0
OutHi:.byte 0
Remaining:.word 0
SavedPage:.byte 0
SavedLo:.byte 0
SavedHi:.byte 0
SrcPage:.byte InitialSourcePage
SrcLo:.byte <InitialSourceAddress
SrcHi:.byte >InitialSourceAddress
Config:
 .word RuntimeInput,$a000,RuntimePacked,RuntimeBytes
 .word MetadataInput,$c800,MetadataPacked,MetadataBytes
 .word StateInput,$c100,StatePacked,StateBytes
PhysicalLo:
 .byte <617,<619,<621,<623,<625,<627,<690,<691,<692,<693,<695,<795,<291
PhysicalHi:
 .byte >617,>619,>621,>623,>625,>627,>690,>691,>692,>693,>695,>795,>291
PpColdWorkerEnd:
