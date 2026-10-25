.pushseg
.segment "CD_MOTION"
.proc CdMovement
 lda SelectedCharacter
 cmp #14
 beq Active
 rts
Active:
 farcall CdEnsureInit
 lda CdReady
 cmp #$43
 beq Ready
 farcall CdResetTransient
Ready:
 farcall CdSpawnEntrance
 lda Player_X_Position
 sta CdOldX
 sta MmOldX
 lda Player_Y_Position
 sta CdOldY
 lda SavedJoypadBits
 eor CdPrevious
 and SavedJoypadBits
 sta CdPressed
 lda SavedJoypadBits
 sta CdPrevious
 lda #0
 sta MmSliding
 sta MmOnVine
 sta MmUnderwater
 sta RgCrouch
 sta CrouchingFlag
 sta PlayerSize
 sta CdHide
 lda Player_State
 cmp #3
 bne Ordinary
 farcall MegaManClimbing,jmp
Ordinary:
 lda CdHurtTimer
 beq Input
 dec CdHurtTimer
 jmp Vertical
Input:
 lda SavedJoypadBits
 and #Down_Dir
 beq Stand
 lda Player_State
 bne Stand
 lda #1
 sta RgCrouch
 sta CrouchingFlag
 lda CdHeld
 beq Stand
 inc CdHide
Stand:
 lda #0
 sta Player_X_Speed
 sta Player_XSpeedAbsolute
 lda SavedJoypadBits
 and #Left_Dir|Right_Dir
 beq NoHorizontal
 lda CdHide
 bne NoHorizontal
 lda SavedJoypadBits
 and #Left_Dir|Right_Dir
 cmp #Left_Dir
 beq Left
 lda #1
 sta PlayerFacingDir
 lda #0
 sta CdScratch
 jmp Horizontal
Left:
 lda #2
 sta PlayerFacingDir
 lda #1
 sta CdScratch
Horizontal:
 lda #128
 sta CdNX
 lda #5
 sta CdNXPage
 lda #$cc
 sta CdSXLo
 lda #1
 sta CdSXHi
 ldx #0
 lda CdScratch
 bne MoveLeft
 jsr CdNative::NF21E
 lda #$1c ; SMB camera speed format: native1CC /16.
 bne ExportX
MoveLeft:
 jsr CdNative::NF23C
 lda #$e3
ExportX:sta Player_X_Speed
 lda #$1c
 sta Player_XSpeedAbsolute
 lda CdNX
 sec
 sbc #128
 sta CdScratch
 lda #0
 ldy CdScratch
 bpl :+
 lda #$ff
:sta CdScratch2
 lda Player_X_Position
 clc
 adc CdScratch
 sta Player_X_Position
 lda Player_PageLoc
 adc CdScratch2
 sta Player_PageLoc
NoHorizontal:
 lda Player_State
 bne Vertical
 lda #$ab ; native resting downward velocity, originalF31D.
 sta CdVYLo
 lda #$ff
 sta CdVYHi
 lda CdPressed
 and #A_Button
 beq Vertical
 lda #$87 ; originalC9A9 jump: +$0687 upward.
 sta CdVYLo
 lda #6
 sta CdVYHi
 lda #1
 sta Player_State
 lda #$f9
 sta Player_Y_Speed
 sta CdLastExportVY
 lda #Sfx_BigJump
 sta Square1SoundQueue
Vertical:
 lda Player_State
 beq Export
 lda Player_Y_Speed
 bmi NotStopped
 lda CdLastExportVY
 beq NotStopped
 lda CdVYHi
 bmi NotStopped
 lda CdVYLo
 ora CdVYHi
 beq NotStopped
 lda #$ab
 sta CdVYLo
 lda #$ff
 sta CdVYHi
NotStopped:
 jsr X5ChipReleaseBridge ; Local release-only gate; actual input unchanged.
 nop                     ; Same4B as original zero-page LDA plus AND.
 bne Integrate
 lda CdVYHi
 bmi Integrate
 cmp #5
 bcs Integrate
 lda #$ab ; originalCBC2..CBC9 short-jump release.
 sta CdVYLo
 lda #$ff
 sta CdVYHi
Integrate:
 lda #128
 sta CdNY
 lda #5
 sta CdNYPage
 ldx #0
 lda CdVYHi
 bmi Fall
 jsr CdNative::NF2A2
 jmp Gravity
Fall:jsr CdNative::NF2C5
Gravity:
 jsr CdNative::NF2FB
 lda CdNY
 sec
 sbc #128
 sta CdScratch
 lda #0
 ldy CdScratch
 bpl :+
 lda #$ff
:sta CdScratch2
 lda Player_Y_Position
 clc
 adc CdScratch
 sta Player_Y_Position
 lda Player_Y_HighPos
 adc CdScratch2
 sta Player_Y_HighPos
Export:
 lda #0
 sec
 sbc CdVYHi
 sta Player_Y_Speed
 sta CdLastExportVY
 sta MmVY+2
 lda Player_X_Position
 sec
 sbc CdOldX
 sta Player_X_Scroll
 lda #0
 sta MmVX
 sta MmVY
 sta MmVY+1
 sta MmXFraction
 lda CdNXFrac
 sta MmXFraction+1
 lda Player_X_Speed
 asl
 asl
 asl
 asl
 sta MmVX+1
 lda Player_X_Speed
 lsr
 lsr
 lsr
 lsr
 cmp #8
 bcc :+
 ora #$f0
:sta MmVX+2
 lda CdVYHi
 bmi Down
 lda #1
 bne State
Down:lda #2
State:ldy Player_State
 beq Done
 sta Player_State
Done:rts
.endproc
.popseg
