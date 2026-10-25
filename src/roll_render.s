.pushseg
.segment "ROLL_CORE"
.proc RlGraphics
 jsr RlEnsure
 lda OperMode
 bne Live
 lda #0
 sta RlPalette
Live:ldx #0
 lda MmDeathFlag
 bne Hide
 lda RlHurt
 beq Air
 ldx #15
 and #4
 beq Pose
 inx
 bne Pose
Air:lda Player_State
 beq Ground
 ldx #5
 cmp #3
 bne Shooting
 ldx #11
 lda RlClock
 and #8
 beq Shooting
 inx
 bne Shooting
Ground:lda Player_X_Speed
 beq Shooting
 lda RlWalk
 ldx #2
 cmp #8
 bcc Shooting
 inx
 cmp #16
 bcc Shooting
 inx
Shooting:
 lda RlAttack
 beq Pose
 cpx #0
 bne NotStanding
 ldx #6
 bne Pose
NotStanding:
 cpx #5
 bne NotJump
 ldx #10
 bne Pose
NotJump:
 cpx #11
 bcc WalkShoot
 ldx #14
 bne Pose
WalkShoot:txa
 clc
 adc #5
 tax
Pose:jmp RlSetPose
Hide:lda #0
 sta ObjectMetasprite
 rts
.endproc
.proc RlPortrait
 jsr RlEnsure
 lda #0
 sta RlPalette
 ldx #0
 jsr RlSetPose
 jmp RlPublish                 ; Portraits draw directly through the front end.
.endproc
.proc RlSetPose
 stx RlPose
 BankPRGC #.bank(RlArtBegin)
 lda RlPosePools,x
 sta RlPool
 txa
 asl
 sta RlTemp
 lda PlayerOutlinesOff
 bne Index
 inc RlTemp
Index:ldx RlTemp
 lda PlayerFacingDir
 cmp #2
 beq Left
 lda RlPose1Lo,x
 sta SmPosePtr
 lda RlPose1Hi,x
 bne Store
Left:lda RlPose2Lo,x
 sta SmPosePtr
 lda RlPose2Hi,x
Store:sta SmPosePtr+1
 ldx RlPool
 lda RlPoolChrLo,x
 sta SmChrBank
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 lda Player_SprAttrib
 and #$fc
 sta Player_SprAttrib
 ; A catch-up update can skip OAM drawing. Keep the displayed CHR mapping
 ; until RlDraw builds matching sprite data, then publish them together.
 jmp RlPaletteUpdate
.endproc
.proc RlPublish
 BankPRGC #.bank(RlArtBegin)
 lda #0
 sta SsChrActive
 ldy RlPool
 lda RlPoolChrLo,y
 ldx RlPoolChrHi,y
 ldy #0
 farcall X5SetPhysicalChr
 ldy RlPool
 lda RlPoolChrLo,y
 clc
 adc #2
 ldx RlPoolChrHi,y
 ldy #6
 farcall X5SetPhysicalChr
 ldy RlPool
 lda RlPoolChrLo,y
 clc
 adc #3
 ldx RlPoolChrHi,y
 ldy #7
 farcall X5SetPhysicalChr,jmp
.endproc
.proc RlPaletteUpdate
 lda RlPalette
 bne Done
 ldx VRAM_Buffer1_Offset
 cpx #78
 bcs Done
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 lda #$1a
 sta VRAM_Buffer1+3,x
 lda #$28
 sta VRAM_Buffer1+4,x
 lda #$24
 sta VRAM_Buffer1+5,x
 txa
 clc
 adc #6
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 inc RlPalette
Done:rts
.endproc
.proc RlForcePalette
 lda #0
 sta RlPalette
 jmp RlPaletteUpdate
.endproc
.proc RlDraw
 lda MmDeathFlag
 beq Alive
 farcall X5ClearChrModes
 farcall MegaManDrawDeath
 BankPRGC #.bank(RlArtBegin)
 lda #<RlDeathReservation
 sta SmPosePtr
 lda #>RlDeathReservation
 sta SmPosePtr+1
 rts
Alive:
 jsr RlPublish
 lda GameEngineSubroutine
 cmp #8
 jne Done
 ldx #3
Loop:stx RlSlot
 lda MmBulletType,x
 beq Next
 ldy #0
 cmp #1
 beq Pose
 lda MmBulletAge,x
 lsr
 and #1
 clc
 adc #2
 tay
Pose:lda MmBulletDir,x
 cmp #2
 beq LeftShot
 lda RlShotLo,y
 sta R0
 lda RlShotHi,y
 bne ShotPointer
LeftShot:
 lda RlShotLeftLo,y
 sta R0
 lda RlShotLeftHi,y
ShotPointer:
 sta R1
 lda MmBulletX,x
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda MmBulletPage,x
 sbc ScreenLeft_PageLoc
 sta R5
 lda MmBulletY,x
 sta R6
 jsr RlDrawRecord
Next:ldx RlSlot
 dex
 bpl Loop
 ldx #3
Drops:stx RlSlot
 lda InvDropKind,x
 beq DropNext
 ldy #5                       ; Existing small/large energy-capsule art.
 lda AvDropItem,x
 bpl EnergySize
 ldy #1                       ; Supplied small/large white health orbs.
 lda InvDropKind,x
 cmp #2
 bne DropArt
 ldy #4
 bne DropArt
EnergySize:
 lda InvDropKind,x
 cmp #2
 bne DropArt
 iny
DropArt:lda RlShotLo,y
 sta R0
 lda RlShotHi,y
 sta R1
 lda InvDropX,x
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda InvDropPage,x
 sbc ScreenLeft_PageLoc
 sta R5
 lda InvDropY,x
 sta R6
 jsr RlDrawRecord
DropNext:ldx RlSlot
 dex
 bpl Drops
Done:
 BankPRGC #.bank(RlArtBegin)
 rts
.endproc
.proc RlDrawRecord
 lda CurrentOAMOffset
 cmp #160
 bcs Done
 ldy #0
 lda (R0),y
 beq Done
 sta RlTemp
 iny
 ldx #0
Copy:
 .repeat 4,I
 lda (R0),y
 sta OutlinePoseBuffer+1+I,x
 iny
 .endrepeat
 lda OutlinePoseBuffer+3,x
 bmi Negative
 clc
 adc R6
 bcs Hidden
 bcc Check
Negative:clc
 adc R6
 bcc Hidden
Check:cmp #32
 bcc Hidden
 cmp #240
 bcs Hidden
 inx
 inx
 inx
 inx
Hidden:dec RlTemp
 dec RlTemp
 dec RlTemp
 dec RlTemp
 bne Copy
 stx OutlinePoseBuffer
 lda #<OutlinePoseBuffer
 sta R0
 lda #>OutlinePoseBuffer
 sta R1
 lda #1
 sta R7
 lda #0
 sta R3
 jsr RlFastShotRender
Done:rts
.endproc
.popseg
