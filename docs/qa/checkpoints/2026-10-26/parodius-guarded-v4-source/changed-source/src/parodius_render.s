.pushseg
.segment "VIC_WORLD"
.proc PnChoosePool
 lda PnFrame
 bne Valid
 ldx VvVariant
 lda StandFrames-1,x
Valid:
 tax
 lda PnBodyPoolTable,x
 cmp #$ff
 bne Save
 inc PnMissing
 ldx VvVariant
 lda StandFrames-1,x
 tax
 lda PnBodyPoolTable,x
Save:sta PnPool
 rts
StandFrames:.byte 71,1,164
.endproc
.proc PnRecordPointer
 sta PnDrawFrame
 ldx VvVariant
 lda PnFrameIndexLo-1,x
 sta R0
 lda PnFrameIndexHi-1,x
 sta R1
 ldy PnDrawFrame
 lda (R0),y
 sta VvTemp2
 ldx PnPool
 lda PnPoolBank,x
.if ::MAPPER_MMC5
 ora #MMC5_PRG_ROM
.endif
 BankPRGC a
 lda PnPoolLo,x
 sta R0
 lda PnPoolHi,x
 sta R1
 ldy VvTemp2
 lda (R0),y
 sta VvTemp
 lda PnPoolPtrHiLo,x
 sta R0
 lda PnPoolPtrHiHi,x
 sta R1
 lda (R0),y
 sta R1
 lda VvTemp
 sta R0
 ldy #0
 lda (R0),y
 bne Done
 inc PnMissing
Done:rts
.endproc
.proc PnPublish
 ; Native Bowser/Podoboo use window4. Private weapon art belongs in6.
 lda #0
 sta SsChrActive
 ldy PnPool
 lda PnPoolSpecialLo,y
 ldx PnPoolSpecialHi,y
 ldy #6
 farcall X5SetPhysicalChr
 ldy PnPool
 lda PnPoolPickupLo,y
 ldx PnPoolPickupHi,y
 ldy #7
 farcall X5SetPhysicalChr
 ldy PnPool
 lda PnPoolBodyLo,y
 ldx PnPoolBodyHi,y
 ldy #0
 farcall X5SetPhysicalChr,jmp
.endproc
.proc PnGraphics
 jsr PnChoosePool
 lda PnFrame
 bne Pose
 ldx VvVariant
 lda PnChoosePool::StandFrames-1,x
Pose:
 jsr PnRecordPointer
 lda R0
 sta SmPosePtr
 lda R1
 sta SmPosePtr+1
 ldx PnPool
 lda PnPoolBodyLo,x
 sta SmChrBank
 lda Player_SprAttrib
 and #$fc
 sta Player_SprAttrib
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta Player_Pos_ForScroll
 ; A catch-up update can skip sprite drawing. Keep the completed image's
 ; CHR pages until PnDraw constructs matching body/weapon/pickup OAM.
 rts
.endproc
.proc PnPortrait
 ldx VvVariant
 lda PnChoosePool::StandFrames-1,x
 tax
 lda PnBodyPoolTable,x
 sta PnPool
 txa
 jsr PnRecordPointer
 lda R0
 sta SmPosePtr
 lda R1
 sta SmPosePtr+1
 ldx PnPool
 lda PnPoolBodyLo,x
 sta SmChrBank
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 jsr PnPublish
 jmp PnQueuePalette
.endproc
.proc PnDraw
 lda MmDeathFlag
 beq :+
 jmp PnDeathDraw
:
 jsr PnPublish
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda MmDeathFlag
 jne Done
 inc VvDrawFirst
 lda VvDrawFirst
 cmp #27
 bcc :+
 lda #0
:sta VvSlot
 lda #27
 sta VvDrawCount
Actor:
 ldx VvSlot
 inx
 lda PnFrame,x
 beq Next
 jsr PnRecordPointer
 ldx VvSlot
 inx
 lda PnDrawFlags,x
 and #$c0
 bne Next
 lda PnDrawFlags,x
 and #$30
 lsr
 lsr
 lsr
 lsr
 tay
 lda PnX,x
 sec
 sbc #8
 sta R4
 lda PnCoordinateHigh,y
 sbc #0
 sta R5
 lda PnY,x
 clc
 adc #24
 bcs Next
 sta R6
 jsr Draw
Next:
 inc VvSlot
 lda VvSlot
 cmp #27
 bcc :+
 lda #0
:sta VvSlot
 dec VvDrawCount
 jne Actor
 lda #3
 sta VvSlot
Caps:
 ldx VvSlot
 lda PnCapActive,x
 beq CapNext
 ldy PnCapAnim,x
 farcall PnPickupFrame
 jsr PnRecordPointer
::PnPickupPoseReady:
.export PnPickupPoseReady
 ldx VvSlot
 lda PnCapX,x
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda PnCapPage,x
 sbc ScreenLeft_PageLoc
 sta R5
 lda PnCapY,x
 sta R6
 jsr Draw
CapNext:
 dec VvSlot
 bpl Caps
 lda #5
 sta VvSlot
Pickups:
 ldx VvSlot
 lda Enemy_Flag,x
 beq PickupNext
 lda Enemy_ID,x
 cmp #PowerUpObject
 bne PickupNext
 lda PowerUpType,x
 cmp #2
 bcs PickupNext
 lda #0
 sta EnemyMetasprite,x
 ldy VvClock
 lda #4
 farcall PnPickupFrame
 jsr PnRecordPointer
 ldx VvSlot
 lda Enemy_X_Position,x
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda Enemy_PageLoc,x
 sbc ScreenLeft_PageLoc
 sta R5
 lda Enemy_Y_Position,x
 sta R6
 jsr Draw
PickupNext:
 dec VvSlot
 bpl Pickups
Done:
 ; HpGraphicsBankCopy starts from the family's ordinary C bank. Big/body
 ; pools may live in a different bank even when no weapon needs drawing.
 ; Restore the pose's actual record bank before reserving/drawing the body.
 lda MmDeathFlag
 jne DrawDone
 ldx PnPool
 lda PnPoolBank,x
.if ::MAPPER_MMC5
 ora #MMC5_PRG_ROM
.endif
 .if ::ENABLE_MMC5_EXPANDED
 PnBodyBankHookStart=*
 jsr PnBodyOrderBankStub
 .res 3,$ea
 .assert *-PnBodyBankHookStart=6,error,"Native bank-store call span retained"
 .else
 BankPRGC a
 .endif
 rts
Draw:
::PnDrawRecord:
.export PnDrawRecord
 ; Large barriers share the real64-sprite budget with the player/world. Draw
 ; a rotating complete subset rather than rejecting the entire effect.
 ldy #0
 lda (R0),y
 jeq DrawDone
 sta OutlineBytesLeft
 ; Weapons are allocated before the body/world. Keep the complete player
 ; pose and at least8 world sprites reserved, even with a full source fleet.
 lda R0
 pha
 lda R1
 pha
 lda SmPosePtr
 sta R0
 lda SmPosePtr+1
 sta R1
 lda #220
 sec
 sbc (R0),y
 sta VvTempY
 pla
 sta R1
 pla
 sta R0
 lda VvTempY
 sec
 sbc CurrentOAMOffset
 jeq DrawDone
 jcc DrawDone
 cmp #125
 bcc Limit
 lda #124
Limit:
 and #$fc
 sta VvTempY
 lda OutlineBytesLeft
 sta VvTemp2
::PnDrawRotationOffset:
.export PnDrawRotationOffset
 ; Byte-sized power-of-two records need only a mask. Keep the exact old
 ; clockwise byte offset, including the VvClock*4 wrap at64 game updates.
 ; VvTemp is dead after PnRecordPointer and before the next actor lookup.
 tax
 dex
 stx VvTemp
 and VvTemp
 bne NonPowerRotation
 lda VvClock
 asl
 asl
 cmp OutlineBytesLeft
 bcc MaskRotation
 clv                         ; The old loop's final SBC clears V.
MaskRotation:
 and VvTemp
 clc
 jmp Start
NonPowerRotation:
 lda VvClock
 asl
 asl
Modulo:
 cmp OutlineBytesLeft
 bcc Start
 sec
 sbc OutlineBytesLeft
 jmp Modulo
Start:
::PnDrawRotationReady:
.export PnDrawRotationReady
 sta VvTemp
 lda OutlineBytesLeft
 cmp VvTempY
 bcc CheckInterior
 bne Buffered
CheckInterior:
 lda R7
 cmp #1
 bne Buffered
 lda R5
 bne Clipped
 lda R4
 cmp #32
 bcc Clipped
 cmp #224
 bcs Clipped
 lda R6
 cmp #96
 bcc Clipped
 cmp #176
 bcs Clipped
 farcall PnFastDrawRecord,jmp
Clipped:
 farcall PnFastDrawClippedRecord,jmp
Buffered:
 lda VvTemp
 tay
 iny
 ldx #0
Copy:
 .repeat 4, I
 lda (R0),y
 sta OutlinePoseBuffer+1+I,x
 iny
 .endrepeat
 cpy OutlineBytesLeft
 bcc Continue
 beq Continue
 ldy #1
Continue:
 ; Native viewport coordinates are translated below SMB's status bar.
 ; Do not let a high shot/Option select unrelated HUD split tiles.
 lda OutlinePoseBuffer+3,x
 bmi NegativeY
 clc
 adc R6
 bcs Hidden
 bcc CheckY
NegativeY:
 clc
 adc R6
 bcc Hidden
CheckY:
 cmp #32
 bcc Hidden
 cmp #240
 bcs Hidden
 inx
 inx
 inx
 inx
Hidden:
 lda VvTemp2
 sec
 sbc #4
 sta VvTemp2
 beq Complete
 cpx VvTempY
 bcc Copy
Complete:
 stx OutlinePoseBuffer
 lda #<OutlinePoseBuffer
 sta R0
 lda #>OutlinePoseBuffer
 sta R1
 lda #0
 sta R3
 lda #1
 sta R7
 farcall MetaspriteRenderLoop
DrawDone:rts
.endproc
PnCoordinateHigh:.byte 0,1,$ff,0
.proc PnQueuePalette
 lda VvVariant
 sec
 sbc #1
 sta VvTemp
 asl
 clc
 adc VvTemp
 tay
 ldx VRAM_Buffer1_Offset
 cpx #78
 bcs Done
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 lda MmDeathFlag
 beq LiveColors
 lda PnDeathPalettes,y
 sta VRAM_Buffer1+3,x
 lda PnDeathPalettes+1,y
 sta VRAM_Buffer1+4,x
 lda PnDeathPalettes+2,y
 bne LastColor
LiveColors:
 lda PnPrivatePalettes,y
 sta VRAM_Buffer1+3,x
 lda PnPrivatePalettes+1,y
 sta VRAM_Buffer1+4,x
 lda PnPrivatePalettes+2,y
LastColor:
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
.proc PnHud
.if ::MAPPER_MMC5

 ; All seven original frame/label cells fit inside the TV-safe28-column row.
 ; Like the Gradius HUD, renew font ownership even while its cells are clean.
.if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5
 jmp PnHudGate
.else
 lda DisableScreenFlag
.endif
 jne GraphicalDone
 lda VvVariant
 clc
 adc #.lobyte(395)
 sta InvHudPhysical
 lda #.hibyte(396)
 sta X5HudChrUpper
 lda InvHudActive
 bne FontActive
 inc ReloadCHRBank
FontActive:
 lda #1
 sta InvHudActive
 lda VvHudDirty
 jeq GraphicalDone
 ldx VRAM_Buffer1_Offset
 cpx #40                    ;42-byte append and terminator fit84-byte queue.
 jcs GraphicalDone
 lda #$20
 sta VRAM_Buffer1,x
 lda #$22                   ;row1, columns2..29: sixteen-pixel side margins.
 sta VRAM_Buffer1+1,x
 lda #28
 sta VRAM_Buffer1+2,x
 lda VvVariant
 sec
 sbc #1
 tay
 lda GraphicalOffsets,y
 tay
 lda #28
 sta VvTemp2
GraphicalCells:
 lda PnHudCells,y
 sta VRAM_Buffer1+3,x
 iny
 inx
 dec VvTemp2
 bne GraphicalCells
 inx
 inx
 inx
 lda #$23
 sta VRAM_Buffer1,x
 lda #$c0
 sta VRAM_Buffer1+1,x
 lda #8
 sta VRAM_Buffer1+2,x
 txa
 clc
 adc #3
 tax
 lda #1
 sta VvTemp
 ldy #8
GraphicalAttributes:
 lda #$aa
 sta VvTemp2
 ; A cell starts two tiles into an attribute byte. Highlight its right
 ; quadrant here and the next byte's left quadrant, covering all32pixels.
 lda VvTemp
 and VvMeter
 beq RightNormal
 lda #$a6
 sta VvTemp2
RightNormal:
 lda VvTemp
 lsr
 and VvMeter
 beq LeftNormal
 lda VvTemp2
 and #$fc
 ora #1
 sta VvTemp2
LeftNormal:
 lda VvTemp2
 sta VRAM_Buffer1,x
 inx
 asl VvTemp
 dey
 bne GraphicalAttributes
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 sta VvHudDirty
GraphicalDone:
 rts
GraphicalOffsets:.byte 0,28,56
.include "parodius_hud.inc"
.else
 lda VvHudDirty
 jeq Done
 lda DisableScreenFlag
 jne Done
 ldx VRAM_Buffer1_Offset
 cpx #40
 jcs Done
 lda #$20
 sta VRAM_Buffer1,x
 lda #$22
 sta VRAM_Buffer1+1,x
 lda #28
 sta VRAM_Buffer1+2,x
 lda VvVariant
 sec
 sbc #1
 tay
 lda LabelOffsets,y
 tay
 lda #28
 sta VvTemp2
Labels:
 lda Text,y
 sta VRAM_Buffer1+3,x
 iny
 inx
 dec VvTemp2
 bne Labels
 inx
 inx
 inx
 lda #$23
 sta VRAM_Buffer1,x
 lda #$c0
 sta VRAM_Buffer1+1,x
 lda #8
 sta VRAM_Buffer1+2,x
 txa
 clc
 adc #3
 tax
 lda #1
 sta VvTemp
 ldy #8
Attributes:
 lda #$aa
 pha
 lda VvTemp
 cmp VvMeter
 bne Normal
 pla
 lda #$a5
 bne Write
Normal:pla
Write:sta VRAM_Buffer1,x
 inx
 asl VvTemp
 dey
 bne Attributes
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 sta VvHudDirty
Done:rts
LabelOffsets:.byte 0,28,56
Text:.byte "SPD 2WY TAI RIP OPT RST OTR "
 .byte "SPD RKT TAI 3WY OPT RST FLD "
 .byte "SPD POT DBL SPR OPT RST BUB "
.endif
.endproc
.popseg

.if ::ENABLE_MMC5_EXPANDED
.include "parodius_body_guard.s"
.endif
