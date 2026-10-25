; Original per-character death animations / skin10. No shared NPC colors change.
; SMB retains the life/respawn timer. No new live state or SRAM is allocated.
.pushseg
.segment "VIC_WORLD"
.proc PnDeathStart
 lda #16
 sta PnActive
 lda #0
 sta PnDrawFlags
 sta PnPalette
 lda VvVariant
 cmp #2
 bne :+
 inc PnPalette
:
 lda #10
 sta PnSkin
 BankPRGC #.bank(PnAnimationTable)
 ldx VvVariant
 lda PnDeathAnimationIDs-1,x
 ldx #0
 ldy #0
 farcall PnNativeSetAnimation
 ldx #0
 farcall PnNativeAnimate,jmp
.endproc
.proc PnDeathUpdate
 BankPRGC #.bank(PnAnimationTable)
 ldx #0
 farcall PnNativeAnimate,jmp
.endproc
.proc PnDeathGraphics
 BankPRGC #.bank(PnDeathPose122)
 ldx VvVariant
 lda PnFrame
 sec
 sbc PnDeathFirstFrames-1,x
 cmp PnDeathFrameCounts-1,x
 bcs Hidden
 tay
 lda PnDeathRecordLoAddrLo-1,x
 sta R0
 lda PnDeathRecordLoAddrHi-1,x
 sta R1
 lda (R0),y
 sta SmPosePtr
 lda PnDeathRecordHiAddrLo-1,x
 sta R0
 lda PnDeathRecordHiAddrHi-1,x
 sta R1
 lda (R0),y
 sta SmPosePtr+1
 ldx VvVariant
 lda BodyLo-1,x
 sta SmChrBank
 lda Player_SprAttrib
 and #$fc
 sta Player_SprAttrib
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 jsr PnQueuePalette
 rts
Hidden:
 lda #0
 sta ObjectMetasprite
 rts
BodyLo:.byte <892,<956,<1020
.endproc
.proc PnDeathDraw
 BankPRGC #.bank(PnDeathPose122)
 lda SmChrBank
 ldx #3
 ldy #0
 farcall X5SetPhysicalChr,jmp
.endproc
.popseg
