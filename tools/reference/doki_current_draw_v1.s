; Selected25 Doki modes only. Reuse the active-guest draw buffer used by
; Kirby at5C90; Kirby is a mutually exclusive selected13 foreground owner.
; Audio/IRQ have no draw-buffer consumer. No host global/ZP allocation.
.pushseg
.segment "PARODIUS_BELLS"
S2DokiDrawPacket=$5c90
.export S2DokiDrawPacket,DdqBuildPose,DdqStanding,DdqS2Standing,DdqMenuName
.segment "CD_GFX"
DdqStanding:
 lda #1
 sta R1
 lda #0
 beq DdqFrame
DdqBuildPose:
 lda S2Face
 sta R1
 lda S2Animation
 cmp #6
 bcs DdqFrame
 ora S2Holding
DdqFrame:
 ldx #$40
 cmp #4
 beq DdqSymmetric
 cmp #5
 beq DdqSymmetric
 cmp #7
 beq DdqSymmetric
 ldx #0
 stx R2
 pha
 lda R1
 lsr
 ror
 ror
 sta R3
 pla
 jmp DdqFrameIndex
DdqSymmetric:
 stx R2
 ldx #0
 stx R3
DdqFrameIndex:
 asl
 asl
 sta R0
 ldx #16
DdqTemplateCopy:
 lda DdqTemplate,x
 sta S2DokiDrawPacket,x
 dex
 bpl DdqTemplateCopy
 ldx #3
DdqCell:
 txa
 eor R1
 clc
 adc R0
 tay
 lda DdqFrames,y
 clc
 adc #6
 cmp #6
 bcs :+
 lda #58                    ; original FB is the transparent pair
:
 sta R4
 txa
 asl
 asl
 tay
 lda R4
 sta S2DokiDrawPacket+1,y
 txa
 lsr
 lda #0
 ror
 ror
 and R2
 ora R3
 sta S2DokiDrawPacket+2,y
 dex
 bpl DdqCell
 lda #<S2DokiDrawPacket
 sta SmPosePtr
 lda #>S2DokiDrawPacket
 sta SmPosePtr+1
 lda S2Variant
 clc
 adc #32                    ; variants4..7 select physical804..807
 sta SmChrBank
 rts
.segment "PARODIUS_BELLS"
DdqTemplate:
.byte 16,0,0,0,0,0,0,0,8,0,0,16,0,0,0,16,8
.segment "CD_GFX"
DdqFrames:
.incbin "doki-frames.bin"
.segment "PARODIUS_BELLS"
DdqS2Standing:
 lda S2Variant
 and #4
 beq DdqUSAStanding
 jsr DdqStanding
 jmp S2Graphics::DokiMeta
DdqUSAStanding:
 lda S2NativeCharacter
 cmp #3
 bne :+
 lda #0
:
 asl
 ora S2Size
 .repeat 5
 asl
 .endrepeat
 ora #1
 tax
 lda S2BodyRecord,x
 jmp S2Graphics::SetBody
DdqMenuName:
 lda S2Variant
 and #4
 beq DdqUSAName
 jsr S2GraphicsBank
 jmp S2MenuNameC
DdqUSAName:
 farcall FmQueueName,jmp
.assert *<=$c000,lderror,"Doki helpers stay in the existing S2 core bank"
.segment "CD_GFX"
DdqPalettes:
.incbin "doki-palettes.bin"
.assert *<=$d600,lderror,"Doki data stays in the existing S2 graphics bank"
.popseg
