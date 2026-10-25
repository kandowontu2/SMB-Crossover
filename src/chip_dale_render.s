.pushseg
.segment "CD_LOGIC"
.proc CdGraphics
 jsr CdIsActive
 bcs Active
 rts
Active:
 lda OperMode
 bne Gameplay
 jsr CdResetTransient
 jmp CdPortrait
Gameplay:
 BankPRGC #.bank(CdArtBegin)
 lda MmDeathFlag
 beq Live
 lda MmDeathPit
 beq Hurt
 lda #0
 sta ObjectMetasprite
 rts
Hurt:lda #11
 bne Animation
Live:
 lda CdHide
 beq Visible
 lda #0
 sta ObjectMetasprite
 rts
Visible:
 lda CdHurtTimer
 bne Hurt
 lda CdThrowAge
 beq Ordinary
 lda #9
 bne Animation
Ordinary:
 lda Player_State
 beq Ground
 lda #7
 bne Held
Ground:
 lda RgCrouch
 beq Walk
 lda #5
 bne Animation
Walk:
 lda Player_X_Speed
 beq Standing
 lda #3
 bne Held
Standing:lda #1
Held:ldx CdHeld
 beq Animation
 clc
 adc #1
Animation:
 ldy CdVariant
 beq Chip
 clc
 adc #12
Chip:
 cmp CdAnim
 beq Tick
 sta CdAnim
 tax
 lda CdAnimRate,x
 sta CdAnimTimer
 lda #0
 cpx #1
 beq IdleFrame
 cpx #2
 beq IdleFrame
 cpx #13
 beq IdleFrame
 cpx #14
 bne Store
IdleFrame:lda #1
Store:sta CdAnimFrame
Tick:
 ldx CdAnim
 dec CdAnimTimer
 bne Pose
 lda CdAnimRate,x
 sta CdAnimTimer
 cpx #1
 beq Pose
 cpx #2
 beq Pose
 cpx #13
 beq Pose
 cpx #14
 beq Pose
 inc CdAnimFrame
 lda CdAnimFrame
 cmp CdAnimLength,x
 bcc Pose
 lda #0
 sta CdAnimFrame
Pose:
 lda CdAnimFirst,x
 clc
 adc CdAnimFrame
 tax
 jsr CdSetPose
 rts
  .byte $ea,$ea ; constant body colors initialize through GetPlayerColors/Portrait.
.endproc
.proc CdPortrait
 jsr CdIsActive
 bcs Active
 rts
Active:
 BankPRGC #.bank(CdArtBegin)
 lda #1
 ldx CdVariant
 beq :+
 lda #13
:tax
 lda CdAnimFirst,x
 clc
 adc #1
 tax
 jsr CdSetPose
 jsr CdPalette
 jmp CdPublishBody
.endproc
.proc CdSetPose
 stx CdPose
 lda CdPoseChrLo,x
 sta SmChrBank
 lda PlayerFacingDir
 cmp #2
 beq Left
 lda CdPoseRightLo,x
 sta SmPosePtr
 lda CdPoseRightHi,x
 bne Pointer
Left:
 lda CdPoseLeftLo,x
 sta SmPosePtr
 lda CdPoseLeftHi,x
Pointer:sta SmPosePtr+1
 lda Player_Rel_XPos
 sta Player_Pos_ForScroll
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 rts
.endproc
.proc CdPublishBody
 lda SmChrBank
 ldx #1 ; allocated pages412..459 all in upperCHR quadrant1.
 ldy #0
 farcall X5SetPhysicalChr,jmp
.endproc
.proc CdDrawWorld
 jsr CdIsActive
 jcc Done
 lda #.lobyte(CdWorldChr)
 ldx #.hibyte(CdWorldChr)
 farcall X5SetSpecialChr
 BankPRGC #.bank(CdArtBegin)
 lda #5
 sta CdSlot
Loop:
 ldx CdSlot
 lda CdBoxKind,x
 jeq Next
 lda #<CdBoxWood
 sta R0
 lda #>CdBoxWood
 sta R1
 lda CdBoxX,x
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda CdBoxPage,x
 sbc ScreenLeft_PageLoc
 sta R5
 lda CdBoxY,x
 sta R6
 lda #1
 sta R7
 lda #0
 sta R3
 farcall MetaspriteRenderLoop
Next:dec CdSlot
 jpl Loop
 jsr CdPublishBody
Done:rts
.endproc
.proc CdPalette
 ; Original opening native palette RAM310..313:0F,0F,37,16.
 ldx VRAM_Buffer1_Offset
 cpx #$4e ; 6-byte update and terminator fit the 84-byte queue.
 bcs Done
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 lda #$0f
 sta VRAM_Buffer1+3,x
 lda #$37
 sta VRAM_Buffer1+4,x
 lda #$16
 sta VRAM_Buffer1+5,x
 txa
 clc
 adc #6
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
Done:rts
.endproc
.proc CdGetPlayerColors
 ; Native palette0's transparent entry also changes the universal backdrop.
 ; Keep SMB's area/intermediate background-color policy, including black lives.
 ldx VRAM_Buffer1_Offset
 cpx #$4d ; 7-byte update and terminator fit the 84-byte queue.
 bcs Done
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$10
 sta VRAM_Buffer1+1,x
 lda #4
 sta VRAM_Buffer1+2,x
 ldy BackgroundColorCtrl
 bne :+
 ldy AreaType
:lda BackgroundColors,y
 sta VRAM_Buffer1+3,x
 lda #$0f
 sta VRAM_Buffer1+4,x
 lda #$37
 sta VRAM_Buffer1+5,x
 lda #$16
 sta VRAM_Buffer1+6,x
 txa
 clc
 adc #7
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
Done:rts
BackgroundColors:.byte $22,$22,$0f,$0f,$0f,$22,$0f,$0f
.endproc
.popseg
