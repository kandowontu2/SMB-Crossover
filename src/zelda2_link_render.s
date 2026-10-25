; Private native-art stage. Selector is not enabled by this file.
.pushseg
.segment "Z2_LOGIC"
.proc Z2IsActive
 lda SelectedCharacter
 cmp #CHARACTER_LINK
 bne No
 lda Z2Variant
 cmp #1
 beq Yes
No:clc
 rts
Yes:sec
 rts
.endproc
.proc Z2SpecialDrawGate
 jsr Z2IsActive
 bcc Original
 rts ; Own C0..CD rewards must never enter originalLink's upgrade tables.
Original:farcall SpecialDrawShots,jmp
.endproc
.proc Z2GraphicsGate
 jsr Z2IsActive
 bcs Native
 farcall RosterGraphics,jmp
Native:
 lda Player_SprAttrib
 and #$fc
 sta Player_SprAttrib
 lda MmDeathFlag
 beq Alive
 lda MmDeathPit
 beq HurtDeath
 lda #0
 sta ObjectMetasprite
 rts
HurtDeath:
 ldx #10 ; Authentic original hurt pose; SMB death timing remains inherited.
 jmp Pose
Alive:
 ldx Z2CachedPose
 cpx #11
 bcc Pose
 ldx #3
Pose:
 lda Z2ActiveSpells
 and #8
 beq Ready
 lda FrameCounter
 and #$3c
 lsr
 lsr
 clc
 adc #11
 tax
Ready:
 jsr Z2SetPose
 lda Z2ActiveSpells
 and #1
 ora #$80
 cmp Z2PaletteCache
 beq :+
 jsr Z2QueueBodyPalette
: 
 rts
.endproc
.proc Z2PortraitGate
 jsr Z2IsActive
 bcs Native
 farcall RosterPortrait,jmp
Native:
 ldx #3
 jsr Z2SetPose
 jsr Z2QueueBodyPalette
 jmp Z2PublishBody
.endproc
; X=original frame0..10 or native fairy clock phase11..26.
.proc Z2SetPose
 cpx #27
 bcc :+
 ldx #3
:
 BankPRGC #.bank(Z2ArtBegin)
 lda Z2PoseChrLo,x
 sta SmChrBank
 lda PlayerFacingDir
 cmp #2
 beq Left
 lda Z2PoseRightLo,x
 sta SmPosePtr
 lda Z2PoseRightHi,x
 jmp Ready
Left:
 lda Z2PoseLeftLo,x
 sta SmPosePtr
 lda Z2PoseLeftHi,x
Ready:
 sta SmPosePtr+1
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 rts
.endproc
.proc Z2PublishBody
 lda SmChrBank
 ldx #.hibyte(308)
 ldy #0
 farcall X5SetPhysicalChr,jmp
.endproc
.proc Z2DrawShots
 BankPRGC #.bank(Z2ArtBegin)
 lda MmDeathFlag
 bne BodyOnly
 jsr Z2DrawWorld
BodyOnly:
 jsr Z2PublishBody
 jmp Z2Hud
.endproc
.proc Z2QueueBodyPalette
 ldx VRAM_Buffer1_Offset
 cpx #$4e ;6B palette + terminator must fit84B native queue
 bcs Done
 lda Z2ActiveSpells
 and #1
 ora #$80
 sta Z2PaletteCache
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 lda #$18
 sta VRAM_Buffer1+3,x
 lda #$36
 sta VRAM_Buffer1+4,x
 lda #$2a
 ldy Z2ActiveSpells
 tya
 and #1
 beq Green
 lda #$16 ; Native Shield changes the tunic's green to red.
 bne Put
Green:lda #$2a
Put:sta VRAM_Buffer1+5,x
 txa
 clc
 adc #6
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
Done:rts
.endproc
.segment "Z2_DRAW_GATE"
.proc Z2DrawGuard
 farcall RlLegacyDrawDispatch,jmp
 .assert *-Z2DrawGuard=18,error,"Live legacy dispatch fits after Roll admission"
.endproc
.popseg
