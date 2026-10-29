.pushseg
.segment "PARODIUS_BELLS"
.export S2Graphics,S2DrawBody,S2DrawObjects,S2PalettePointer,S2GraphicsBank
.proc S2GraphicsBank
 lda SelectedCharacter
 cmp #CHARACTER_SMB2_ROSTER
 bne Done
 lda #80|$80
 sta CurrentBankC
 sta $5116
Done:
 rts
.endproc
.proc S2Graphics
 jsr S2Ensure
 bcc Foreign
 lda S2Hurt
 beq Pose
 lda S2Clock
 and #8
 bne No
Pose:jsr S2GraphicsBank
 ; 32 poses per profile: eight source actions x carry x facing.
 lda S2NativeCharacter
 asl
 ora S2Size
 .repeat 5
 asl
 .endrepeat
 sta R2
 lda S2Animation
 cmp #11
 bcs No
 tax
 lda AnimationIndex,x
 bmi No
 asl
 asl
 ora R2
 sta R2
 lda S2Holding
 asl
 ora R2
 ora S2Face
 tax
 lda S2BodyRecord,x
 jsr S2SetRecord
 lda S2NativeCharacter
 asl
 ora S2Size
 clc
 adc #<S2_FIRST_CHR
 sta SmChrBank
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 lda #0
 sta Player_SprAttrib
 lda Player_Rel_XPos
 sta Player_Pos_ForScroll
 sec
 rts
No:lda #0
 sta ObjectMetasprite
Foreign:
 clc
 rts
AnimationIndex:.byte 0,$ff,1,$ff,2,$ff,3,4,5,6,7
.endproc
.proc S2SetRecord
 tax
 lda S2ArtLo,x
 sta SmPosePtr
 lda S2ArtHi,x
 sta SmPosePtr+1
 rts
.endproc
.proc S2PublishBody
 lda SmChrBank
 ldy #0
 jmp S2Publish
.endproc
.proc S2Publish
 ; Genuine farcall ABI, C80 is retained for art. Body uses spritewindow0;
 ; vegetables use independent window6, so both survive the same DMA.
 sta SafecallA_SMC+1
 lda #<X5SetPhysicalChr
 sta FarcallJmpTarget_SMC+1
 lda #>X5SetPhysicalChr
 sta FarcallJmpTarget_SMC+2
 ldx #>S2_FIRST_CHR
 lda #62|$80
 jmp FarCallCommon
.endproc
.proc S2Render
 lda #0
 sta SafecallA_SMC+1
 lda #<MetaspriteRenderLoop
 sta FarcallJmpTarget_SMC+1
 lda #>MetaspriteRenderLoop
 sta FarcallJmpTarget_SMC+2
 lda #4|$80
 jmp FarCallCommon
.endproc
.proc S2DrawBody
 jsr S2Graphics
 bcc Done
 jsr S2PublishBody
 lda SmPosePtr
 sta R0
 lda SmPosePtr+1
 sta R1
 lda #0
 sta R3
 sta R5
 lda Player_Rel_XPos
 sta R4
 lda Player_Y_Position
 sta R6
 lda Player_Y_HighPos
 sta R7
 jmp S2Render
Done:rts
.endproc
.proc S2DrawObjects
 lda SelectedCharacter
 cmp #CHARACTER_SMB2_ROSTER
 bne Done
 jsr S2GraphicsBank
 lda #<(S2_FIRST_CHR+8)
 ldy #6
 jsr S2Publish
 ldx #0
Loop:stx S2Source12
 lda S2ObjectState,x
 beq Next
 lda S2ObjectType,x
 cmp #$32
 bcc Next                      ; original SMB actor renderer owns real enemies.
 cmp #$34
 bcs Next
 sec
 sbc #$32
 asl
 asl
 sta R2
 ; Real native32/33 init clears ObjectAnimationTimer; vegetable behavior
 ; does not increment it. Never invent an NMI-driven vegetable animation.
 lda S2ObjectFacing0,x
 and #1
 ora R2
 tay
 lda S2ObjectRecord,y
 jsr S2SetRecord
 lda SmPosePtr
 sta R0
 lda SmPosePtr+1
 sta R1
 ldx S2Source12
 lda S2X+1,x
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda S2Page+1,x
 sbc ScreenLeft_PageLoc
 sta R5
 lda S2Y+1,x
 sta R6
 lda S2YPage+1,x
 clc
 adc #1
 sta R7
 lda #0
 sta R3
 jsr S2Render
Next:ldx S2Source12
 inx
 cpx #3
 bcc Loop
Done:rts
.endproc
.proc S2PalettePointer
 ; Return two authentic source roles only. ROOT must compose world/P1 eye
 ; ownership deliberately. This does not publish a whole16B palette image.
 lda SelectedCharacter
 cmp #CHARACTER_SMB2_ROSTER
 bne No
 lda S2NativeCharacter
 asl
 asl
 tax
 lda #<Palettes
 clc
 adc NativePaletteOffset,x    ; table-index is native character*4.
 sta R0
 lda #>Palettes
 adc #0
 sta R1
 lda #<S2OriginalRole1
 sta R2
 lda #>S2OriginalRole1
 sta R3
 sec
 rts
No:clc
 rts
NativePaletteOffset:.byte 0,0,0,0,4,0,0,0,8,0,0,0,12,0,0,0
Palettes:.byte $0f,$01,$16,$27,$0f,$06,$25,$36,$0f,$01,$30,$27,$0f,$01,$2a,$36
S2OriginalRole1:.byte $0f,$30,$16,$0f
.endproc
.popseg
