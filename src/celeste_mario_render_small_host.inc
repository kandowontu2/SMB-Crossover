.export CmGraphics,CmGraphicsBank,CmDraw,CmUi,CmColors
.pushseg
.segment "CELESTE_MARIO_CORE"
.proc CmGraphics
 jsr CmEnsure
 lda Player_Rel_XPos
 sta Player_Pos_ForScroll
 ldx #25                      ; native big StandGFX
 lda GameEngineSubroutine
 cmp #11
 bne Live
 ldx #22                      ; native killed frame
 jmp Select
Live:
 lda CrouchingFlag
 beq Wall
 ldx #10
 jmp Still
Wall:
 lda CmState
 beq GroundActs
 cmp #3
 beq Climb
 lda CmWallGrace
 beq Air
 ldx #3                       ; native wall pose uses SkidGFX
 jmp Still
Air:
 lda CmState
 cmp #2
 beq Fall
 cmp #1
 bne GroundActs
 lda SwimmingFlag
 bne Swim
 ldx #4
 bne Still
GroundActs:
 lda Player_X_Speed
 ora Left_Right_Buttons
 beq Stand
 lda Player_XSpeedAbsolute
 cmp #9
 bcc Walk
 lda Player_MovingDir
 and PlayerFacingDir
 bne Walk
 ldx #3
 bne Still
Stand:
 ldx #25
 bne Still
Climb:
 ldx #8
 lda Player_Y_Speed
 beq Still
 lda #2
 bne Animated
Swim:
 ldx #5
 lda CmJumpTime
 ora PlayerAnimCtrl
 bne SwimAnimate
 lda A_B_Buttons
 bpl CurrentFrame
SwimAnimate:
 lda #3
 bne Animated
Walk:
 ldx #0
 lda #3
Animated:
 sta CmTemp
 lda PlayerAnimTimer
 beq Advance
 lda PlayerAnimCtrl
 cmp CmTemp
 bcc CurrentFrame
 lda #0
 beq SetFrame
Advance:
 lda PlayerAnimTimerSet
 sta PlayerAnimTimer
 lda PlayerAnimCtrl
 clc
 adc #1
 cmp CmTemp
 bcc SetFrame
 lda #0
SetFrame:
 sta PlayerAnimCtrl
CurrentFrame:
 txa
 clc
 adc PlayerAnimCtrl
 tax
 jmp Select
Fall:
 ldx #0
 jmp CurrentFrame
Still:
 lda #0
 sta PlayerAnimCtrl
Select:
 jsr CmSmallPoseSelect
 lda CmArtBanks,x
 sta CmGfxBank
 lda PlayerFacingDir
 cmp #2
 beq Left
 lda CmArtRLo,x
 sta SmPosePtr
 lda CmArtRHi,x
 bne High
Left:
 lda CmArtLLo,x
 sta SmPosePtr
 lda CmArtLHi,x
High:
 sta SmPosePtr+1
 lda CmGfxBank
 clc
 adc #<CM_FIRST_CHR
 sta SmChrBank
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 jmp CmGraphicsBank
.endproc
.proc CmGraphicsBank
 BankPRGC #.bank(CmArtStart)
 rts
.endproc
.proc CmDraw
 lda CmGfxBank
 clc
 adc #<CM_FIRST_CHR
 sta CmTemp
 ldy #0
Loop:
 lda CurrentCHRBank,y
 cmp CmTemp
 bne Changed
 lda X5ChrMode,y
 cmp #($80|>CM_FIRST_CHR)
 beq Next
Changed:
 lda CmTemp
 sta CurrentCHRBank,y
 lda #($80|>CM_FIRST_CHR)
 sta X5ChrMode,y
 lda #1
 sta ReloadCHRBank
Next:
 inc CmTemp
 iny
 cpy #4
 bne Loop
 lda #1
 sta X5WideChrActive
 rts
.endproc
.proc CmColors
 lda #0
 sta CmPalette
 jmp CmUi
.endproc
.proc CmUi
 ldy #1
 lda CmDashStock
 bne :+
 iny
:tya
 cmp CmPalette
 beq Done
 ldx VRAM_Buffer1_Offset
 cpx #78
 bcs Done
 sty CmPalette
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 lda #$16
 cpy #1
 beq :+
 lda #$21
:sta VRAM_Buffer1+3,x
 lda #$27
 sta VRAM_Buffer1+4,x
 lda #1
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
.popseg
.include "celeste_mario_art.inc"

; Host adaptation requested by user: original native small source records only.
; Legal CmGraphics selectors are0..10,22,25. Other original internal indices
; remain unchanged for compatibility;11/24 are not produced by CmGraphics.
.pushseg
.segment "CELESTE_MARIO_CORE"
.assert * = $bdd8,lderror,"Unexpected original Celeste core/art end"
CmSmallPoseStart:
.proc CmSmallPoseSelect
 lda Map,x
 tax
 stx CmPose
 rts
Map:.byte 12,13,14,15,16,17,18,19,20,21,23,11
 .byte 12,13,14,15,16,17,18,19,20,21,22,23,24,23
.endproc
CmSmallPoseEnd:
.assert * <= $c000,lderror,"Celeste small mapper exceeds original core tail"
.popseg
