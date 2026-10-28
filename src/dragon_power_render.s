.pushseg
.segment "DRAGON_POWER_CORE"
.ifndef DP_CHR_PUBLISH_BANK
DP_CHR_PUBLISH_BANK=.bank(X5SetPhysicalChr)
.endif
.ifndef DP_RENDER_BANK
DP_RENDER_BANK=.bank(MetaspriteRenderLoop)
.endif
.proc DpGraphicsBank
 lda SelectedCharacter
 cmp #CHARACTER_DRAGON_POWER
 bne Done
 lda #<.bank(DpArtStart)|$80
 sta CurrentBankC
 sta $5116
Done:rts
.endproc
.proc DpGraphics
 jsr DpEnsure
 bcc Foreign
 lda DpProtection
 beq Pose
 lda DpClock
 and #8
 bne Hide
Pose:lda DpPose
 cmp #32
 bcs Hide
 asl
 sta DpRenderIndex
 lda DpAttribute
 and #$40
 beq Set
 inc DpRenderIndex
Set:jsr DpSetRecord
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 lda #0
 sta Player_SprAttrib
 lda Player_Rel_XPos
 sta Player_Pos_ForScroll
 sec
 rts
Hide:lda #0
 sta ObjectMetasprite
Foreign:
 clc
 rts
.endproc
.proc DpSetRecord
 lda SelectedCharacter
 cmp #CHARACTER_DRAGON_POWER
 bne Done
 jsr DpGraphicsBank
 ldx DpRenderIndex
 lda DpPoseLo,x
 sta SmPosePtr
 lda DpPoseHi,x
 sta SmPosePtr+1
 lda DpPosePage,x
 clc
 adc #<DP_FIRST_CHR
 sta SmChrBank
Done:
 rts
.endproc
.proc DpPublish
 ; Literal native farcall ABI; same stores as mmc5.s macro, genuine target.
 lda SelectedCharacter
 cmp #CHARACTER_DRAGON_POWER
 bne Foreign
 lda SmChrBank
 sta SafecallA_SMC+1
 lda #<X5SetPhysicalChr
 sta FarcallJmpTarget_SMC+1
 lda #>X5SetPhysicalChr
 sta FarcallJmpTarget_SMC+2
 ldx #>DP_FIRST_CHR
 ldy #0
 lda #DP_CHR_PUBLISH_BANK|$80
 jmp FarCallCommon
Foreign:clc
 rts
.endproc
.proc DpRender
 lda SelectedCharacter
 cmp #CHARACTER_DRAGON_POWER
 bne Foreign
 lda #0
 sta SafecallA_SMC+1
 lda #<MetaspriteRenderLoop
 sta FarcallJmpTarget_SMC+1
 lda #>MetaspriteRenderLoop
 sta FarcallJmpTarget_SMC+2
 lda #DP_RENDER_BANK|$80
 jmp FarCallCommon
Foreign:clc
 rts
.endproc
.proc DpDrawBody
 jsr DpGraphics
 bcc Done
 jsr DpPublish
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
 jmp DpRender
Done:rts
.endproc
.proc DpDrawShots
 jsr DpEnsure
 bcc Done
 lda DpShotState
 and #$0f
 cmp #2
 beq Right
 cmp #3
 bne Done
 lda #65
 bne Set
Right:lda #64
Set:sta DpRenderIndex
 jsr DpSetRecord
 jsr DpPublish
 lda SmPosePtr
 sta R0
 lda SmPosePtr+1
 sta R1
 lda DpShotX
 clc
 adc DpShotCamera
 sta R4
 lda DpShotCamera+1
 adc #0
 sta R5
 lda R4
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda R5
 sbc ScreenLeft_PageLoc
 sta R5
 lda DpShotY
 sec
 sbc #16
 sta R6
 lda #1
 sbc #0
 sta R7
 lda #0
 sta R3
 jmp DpRender
Done:rts
.endproc
.proc DpPalettePointer
 ; Six role values only. ROOT must compose these into native P0/P1 safely;
 ; world/pickup palette2 is not stolen and no complete16B image is queued.
 jsr DpEnsure
 bcc Done
 jsr DpGraphicsBank
 lda #<DpPaletteRoles
 sta R0
 lda #>DpPaletteRoles
 sta R1
 sec
Done:rts
.endproc
.export DpGraphics,DpGraphicsBank,DpDrawBody,DpDrawShots,DpPalettePointer
.export DpPublish,DpRender,DpSetRecord
.popseg
