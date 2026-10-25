.pushseg
.segment "M3_LOGIC"
.proc M3Graphics
 jsr M3IsActive
 jcc Done
 jsr M3Ensure
 lda OperMode
 beq Menu
 lda M3Ready
 cmp #$b3
 beq Ready
Menu:jsr M3Reset
Ready:
 lda M3Poof
 beq Form
 lda #0
 sta ObjectMetasprite
 rts ; Native SuitLost poof replaces the player during its24-frame effect.
Form:
 lda #0
 sta ObjectVerticalFlip
 lda M3Form
 sta M3RenderForm
 lda M3Native::Player_Frame
 sta M3RenderFrame
 lda MmDeathFlag
 beq Live
 lda MmDeathPit
 bne Hidden
 lda #0
 sta M3RenderForm
 lda #$4b
 sta M3RenderFrame
 bne Draw
Live:
 lda M3Growth
 beq Draw
 lda M3Growth
 lsr
 lsr
 tax
 lda M3Form
 bne Grow
 stx M3Scratch
 lda #11
 sec
 sbc M3Scratch
 tax
Grow:
 BankPRGC #.bank(M3ArtBegin)
 lda M3GrowFrames,x
 sta M3RenderFrame
 lda #1
 sta M3RenderForm
Draw:
 ldx M3RenderFrame
 jsr M3SetFrame
 lda M3Growth
 beq Palette
 ; Authenticated original growth CHR override: native84..87 or68..71.
 ; Native shrink reverses the growth index before choosing CHR phase.
 ; Frame39 is every odd final index; frames11/14 are even. Bit5
 ; therefore supplies the native phase for either direction. The
 ; existing consumer tests this private scratch only for zero.
 lda M3RenderFrame
 lsr
 lsr
 and #8
 sta M3Scratch
 lda SmChrBank
 and #3
 clc
 adc #28 ; physical540..543
 ldx M3Scratch
 beq :+
 sec
 sbc #8 ; physical532..535, original68..71
:sta SmChrBank
 dec M3Growth
Palette:jsr M3PaletteCached
 lda GuestInvulTicks
 and #2
 beq :+
 lda #0
 sta ObjectMetasprite
:
 rts
Hidden:lda #0
 sta ObjectMetasprite
Done:rts
.endproc
.proc M3Portrait
 jsr M3Ensure
 jsr M3Reset
 jsr M3Graphics
 jmp M3PublishBody
.endproc
.proc M3SetFrame
 cpx #81
 bcc :+
 ldx #$0e
:stx M3RenderFrame
 BankPRGC #.bank(M3ArtBegin)
 lda PlayerFacingDir
 cmp #2
 beq Left
 lda M3FrameRightLo,x
 sta SmPosePtr
 lda M3FrameRightHi,x
 bne Pointer
Left:
 lda M3FrameLeftLo,x
 sta SmPosePtr
 lda M3FrameLeftHi,x
Pointer:sta SmPosePtr+1
 lda M3Native::Player_Flip
 beq Chr
 lda M3RenderFrame
 sec
 sbc #26
 cmp #4
 bcs Chr
 sta M3Scratch
 lda M3Native::Player_FlipBits
 and #$c0
 lsr
 lsr
 lsr
 lsr
 clc
 adc M3Scratch
 tax
 lda M3FlipPtrLo,x
 sta SmPosePtr
 lda M3FlipPtrHi,x
 sta SmPosePtr+1
Chr:
 ldx M3RenderForm
 cpx #7
 bcc :+
 ldx #0
:lda M3ChrLoTableLo,x
 sta R0
 lda M3ChrLoTableHi,x
 sta R1
 ldy M3RenderFrame
 lda (R0),y
 sta SmChrBank
 lda M3ChrHiTableLo,x
 sta R0
 lda M3ChrHiTableHi,x
 sta R1
 lda (R0),y
 sta M3SpritePageHi
 lda Player_Rel_XPos
 sta Player_Pos_ForScroll
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 rts
.endproc
.proc M3PublishBody
 lda SmChrBank
 ldx M3SpritePageHi
 ldy #0
 farcall X5SetPhysicalChr,jmp
.endproc
.proc M3Palette
 ldx VRAM_Buffer1_Offset
 cpx #78 ; Six command bytes plus terminator fit the84-byte buffer.
 jcs Done
 BankPRGC #.bank(M3ArtBegin)
 lda M3RenderForm
 cmp #2
 bcc Identity
 cmp #3
 bne Pick
Identity:lda M3Variant
Pick:
 ldy M3RenderForm
 cpy #5
 bne :+
 ldy M3Native::Player_Statue
 beq :+
 lda #7
:sta M3Scratch
 asl
 clc
 adc M3Scratch
 tay
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 lda M3NativePalettes,y
 sta VRAM_Buffer1+3,x
 lda M3NativePalettes+1,y
 sta VRAM_Buffer1+4,x
 lda M3NativePalettes+2,y
 sta VRAM_Buffer1+5,x
 txa
 clc
 adc #6
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 lda M3RenderForm
 sta M3PaletteForm
 lda M3Variant
 sta M3PaletteVariant
 lda M3Native::Player_Statue
 beq :+
 lda #1
:sta M3PaletteStatue
 lda #$b3
 sta M3PaletteValid
Done:rts
.endproc
.proc M3PaletteCached
 lda M3PaletteValid
 cmp #$b3
 bne Changed
 lda M3RenderForm
 cmp M3PaletteForm
 bne Changed
 lda M3Variant
 cmp M3PaletteVariant
 bne Changed
 lda M3Native::Player_Statue
 beq :+
 lda #1
:cmp M3PaletteStatue
 bne Changed
 rts
Changed:jmp M3Palette
.endproc
.proc M3GetPlayerColors
 jsr M3Ensure
 lda M3Form
 sta M3RenderForm
 farcall X5QueueAreaBackdrop
 jmp M3Palette
.endproc
.popseg
