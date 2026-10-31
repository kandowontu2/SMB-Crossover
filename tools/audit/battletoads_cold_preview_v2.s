; Own cold source body, no RAM3 reads and no universal palette writes.
.setcpu "6502"
.import FmGroups,CurrentBankC,Player_X_Position,Player_Y_Position
.import X5SetPhysicalChr,MetaspriteRenderLoop,VRAM_Buffer1,VRAM_Buffer1_Offset,X5QueueAreaBackdrop
.import FarCallCommon,FarcallJmpTarget_SMC,SafecallA_SMC
.importzp R0,R1,R3,R4,R5,R6,R7
.export BtPortraitPending,BtColdPortrait,BtColdColors,BtColdStanding,BtColdEnd
.macro BtFar Target
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(Target)|$80)
 jsr FarCallCommon
.endmacro
.macro Save
 php
 pha
 txa
 pha
 tya
 pha
.endmacro
.macro Restore
 pla
 tay
 pla
 tax
 pla
 plp
.endmacro
.segment "BT_ROM_PREVIEW"
BtPortraitPending:
BtColdPortrait:
 Save
 lda CurrentBankC
 pha
 lda #.lobyte(915)
 ldx #.hibyte(915)
 ldy #0
 BtFar X5SetPhysicalChr
 lda #.lobyte(.bank(BtColdStanding)|$80)
 sta CurrentBankC
 sta $5116
 lda #<(BtColdStanding+$2000)
 sta R0
 lda #>(BtColdStanding+$2000)
 sta R1
 lda Player_X_Position
 clc
 adc #8
 sta R4
 lda Player_Y_Position
 clc
 adc #20
 sta R6
 lda #0
 sta R5
 sta R3
 lda #1
 sta R7
 BtFar MetaspriteRenderLoop
 pla
 sta CurrentBankC
 sta $5116
 Restore
 rts
BtColdStanding:
 .byte $20,$0c,$01,$ed,$04,$0a,$00,$fb,$04,$08,$00,$eb,$04
 .byte $00,$01,$ed,$fc,$0e,$00,$fb,$fc,$04,$00,$eb,$fc
 .byte $06,$00,$fd,$f4,$02,$00,$ed,$f4
BtColdColors:
 Save
 ldx VRAM_Buffer1_Offset
 cpx #68
 bcs ColorDone
 BtFar X5QueueAreaBackdrop
 ldx VRAM_Buffer1_Offset
 ldy #0
 lda FmGroups
 and #$20
 beq Copy
 ldy #13
Copy:
 lda Packets,y
 sta VRAM_Buffer1,x
 beq SetOffset
 inx
 iny
 bne Copy
SetOffset:
 stx VRAM_Buffer1_Offset
ColorDone:
 Restore
 rts
Packets:
 .byte $3f,$11,3,$0f,$0a,$1a,$3f,$15,3,$18,$28,$20,0
 .byte $3f,$11,3,$0f,$17,$27,$3f,$15,3,$18,$28,$20,0
BtColdEnd:
.assert *<=$b100,lderror,"Exact BT239B Quick partition"
