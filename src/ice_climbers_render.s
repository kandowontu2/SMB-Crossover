.pushseg
.segment "ICE_CLIMBERS_CORE"
.proc IcGraphics
 jsr IcEnsure
 lda Player_Rel_XPos
 sta Player_Pos_ForScroll
 lda Player_SprAttrib
 and #$fc
 sta Player_SprAttrib
 lda MmDeathFlag
 bne Death
 lda IcHurt
 beq Attack
 and #4
 bne Hide
Attack:
 lda IcAttack
 beq Ordinary
 ldx #7
 cmp #7
 bcc Pose
 ldx #9
 cmp #11
 bcc Pose
 ldx #10
 bne Pose
Ordinary:
 lda Player_State
 beq Ground
 cmp #3
 beq Climb
 ldx #6
 lda IcJumpAge
 cmp #11
 bcc Pose
 ldx #7
 bne Pose
Climb:ldx #0
 beq Pose
Ground:
 ldx #0
 lda Player_X_Speed
 beq Pose
 lda IcClock
 lsr
 and #3
 tax
Pose:jmp IcSetPose
Death:
 lda MmDeathPit
 bne Hide
 lda MmDeathAge
 lsr
 lsr
 lsr
 and #3
 clc
 adc #11
 tax
 jmp IcSetPose
Hide:lda #0
 sta ObjectMetasprite
 rts
.endproc
.proc IcSetPose
 stx IcPose
 txa
 asl
 sta IcTemp
 lda PlayerFacingDir
 cmp #2
 bne Variant
 inc IcTemp
Variant:lda IcVariant
 beq Index
 lda IcTemp
 clc
 adc #30
 sta IcTemp
Index:
 BankPRGC #.bank(IcArtStart)
 ldx IcTemp
 lda IcPoseLo,x
 sta SmPosePtr
 lda IcPoseHi,x
 sta SmPosePtr+1
 lda IcPosePage,x
 clc
 adc #<IC_FIRST_CHR
 sta SmChrBank
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 ; Wide physicalCHR is published only from IcDraw with matching actual OAM.
 jmp IcPalette
.endproc
.proc IcGraphicsBank
 BankPRGC #.bank(IcArtStart)
 rts
.endproc
.proc IcDraw
 BankPRGC #.bank(IcArtStart)
 lda SmChrBank
 ldx #>IC_FIRST_CHR
 ldy #0
 jmp X5SetPhysicalChr           ; Same actual A-bank62; retain its real RTS ABI.
.endproc
.proc IcPortrait
 jsr IcEnsure
 ldx #0
 jsr IcSetPose
 jsr IcDraw
 jmp IcForcePalette
.endproc
.proc IcVisible
 lda IcHurt
 beq Yes
 and #4
 bne No
Yes:sec
 rts
No:clc
 rts
.endproc
.proc IcForcePalette
 lda #$ff
 sta IcPaletteAck
 jmp IcPalette
.endproc
.proc IcPalette
 lda StarInvincibleTimer
 ora GuestPowerupActive
 beq Normal
 lda #$ff
 sta IcPaletteAck
 rts
Normal:
 lda IcVariant
 and #1
 cmp IcPaletteAck
 beq Done
 pha
 ldx VRAM_Buffer1_Offset
 cpx #78                       ;6payload bytes+terminator within84B queue.
 bcs Declined
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 lda #$30                      ; Native original source PPU12F1/12F5.
 sta VRAM_Buffer1+3,x
 lda #$11
 ldy IcVariant
 beq :+
 lda #$15
:sta VRAM_Buffer1+4,x
 lda #$26
 sta VRAM_Buffer1+5,x
 txa
 clc
 adc #6
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 pla
 sta IcPaletteAck              ; Acknowledge only an actually queued packet.
 rts
Declined:pla
Done:rts
.endproc
.popseg
