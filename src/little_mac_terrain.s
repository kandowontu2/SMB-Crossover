.pushseg
.segment "LM_CORE"
.proc LmBoundingBoxGate
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 bne LegacyGate
 pla
 plp
 farcall TnBoundingBoxGate
 jmp FootBox
LegacyGate:
 pla
 plp
 php
 pha
 jsr LmIsActive
 bcs Own
 pla
 plp
 farcall M3BoundingBoxGate
 jmp FootBox
Own:pla
 plp
 jsr BoundingBoxCore
 lda Player_Rel_XPos
 ldx RgCrouch
 beq :+
 sec
 sbc #5
:sta BoundingBox_UL_XPos
 lda Player_Rel_XPos
 clc
 adc #15
 ldx RgCrouch
 beq :+
 clc
 adc #5
:sta BoundingBox_LR_Corner
 lda Player_Rel_YPos
 sec
 sbc #14
 ldx RgCrouch
 beq :+
 clc
 adc #16
:sta BoundingBox_UL_YPos
 lda Player_Rel_YPos
 clc
 adc #32
 sta BoundingBox_LR_Corner+1
 ldx #0
 ldy #0
FootBox:
 farcall X5EasyFootBox,jmp
.endproc
.proc LmHeadGate
 TnHotGate TnHeadDispatch
 LmGate JnHeadDispatch
 sty LmSavedY
 lda Player_Y_Position
 sta LmOldY
 lda Player_X_Position
 sta LmOldX
 lda Player_PageLoc
 sta LmOldPage
 lda LmOldY
 sec
 sbc #18
 ldx RgCrouch
 beq :+
 clc
 adc #16
:sta Player_Y_Position
 clc
 adc #4
 cmp #32
 bcs :+
 lda #0
 sta R3
 jmp Sampled
:jsr BlockBufferColli_Head
 bne Sampled
 lda Player_Y_Speed
 bpl Sampled
 lda LmOldX
 sec
 sbc #6
 sta Player_X_Position
 lda LmOldPage
 sbc #0
 sta Player_PageLoc
 ldy LmSavedY
 jsr BlockBufferColli_Head
 bne Sampled
 lda LmOldX
 clc
 adc #6
 sta Player_X_Position
 lda LmOldPage
 adc #0
 sta Player_PageLoc
 ldy LmSavedY
 jsr BlockBufferColli_Head
Sampled:pha
 lda LmOldX
 sta Player_X_Position
 lda LmOldPage
 sta Player_PageLoc
 lda LmOldY
 sta Player_Y_Position
 pla
 pha
 beq Finish
 ldx Player_Y_Speed
 bpl Finish
 phy
 ldy R3
 lda MTileAttribute,y
 and #MTILE_SOLID|MTILE_CLIMB
 cmp #MTILE_SOLID
 bne EndY
 lda R2
 clc
 adc #62
 ldx RgCrouch
 beq :+
 sec
 sbc #16
:sta Player_Y_Position
 and #15
 sta R4
 lda #0
 sta MarioJumpRise
 sta MarioJumpFraction
 sta MarioJumpFraction+1
 sta MmYFraction
 sta MmYFraction+1
EndY:ply
Finish:pla
 rts
.endproc
.proc LmSideGate
 TnHotGate TnSideDispatch
 php
 pha
 jsr LmIsActive
 bcs Own
 pla
 plp
 farcall M3SideDispatch,jmp
Own:pla
 plp
 lda GameEngineSubroutine
 cmp #8
 beq Gameplay
 jmp BlockBufferColli_Side
Gameplay:sty LmSavedY
 lda R0
 sta LmSavedR0
 lda Local_eb
 sta LmSavedEb
 lda Player_X_Position
 sta LmOldX
 lda Player_PageLoc
 sta LmOldPage
 lda Player_Y_Position
 sta LmOldY
 ldy LmSavedY
 cpy #5
 bcs Right
 lda #2
 ldx RgCrouch
 beq :+
 lda #7
:sta LmTemp
 lda LmOldX
 sec
 sbc LmTemp
 sta Player_X_Position
 lda LmOldPage
 sbc #0
 sta Player_PageLoc
 jmp Probe
Right:lda #2
 ldx RgCrouch
 beq :+
 lda #7
:clc
 adc LmOldX
 sta Player_X_Position
 lda LmOldPage
 adc #0
 sta Player_PageLoc
Probe:
 lda LmSavedY
 and #1
 beq Lower
 lda RgCrouch
 bne Duck
 lda #0
 sta LmProbe
Loop:ldy LmProbe
 lda Offsets,y
 clc
 adc LmOldY
 sta Player_Y_Position
 ldy LmSavedY
::LmVisibleSideCall:
 jsr LmVisibleSideProbe
 bne Restore
 inc LmProbe
 lda LmProbe
 cmp #3
 bcc Loop
 lda R3
 jmp Restore
Duck:lda LmOldY
 clc
 adc #14
 sta Player_Y_Position
Lower:ldy LmSavedY
::LmVisibleLowerCall:
 jsr LmVisibleSideProbe
Restore:pha
 lda LmOldX
 sta Player_X_Position
 lda LmOldPage
 sta Player_PageLoc
 lda LmOldY
 sta Player_Y_Position
 lda LmSavedR0
 sta R0
 lda LmSavedEb
 sta Local_eb
 pla
 rts
Offsets:.byte $ec,$f8,4 ; native upper sideadder8 -> actualY−12,0,+12
.endproc
.proc LmSideLegacy
 lda SelectedCharacter
 cmp #CHARACTER_SOPHIA
 bne Native
 farcall SophiaSourceSideProbe,jmp
Native:jmp BlockBufferColli_Side
.endproc
.proc LmStandBlocked
 lda Player_X_Position
 sta LmOldX
 lda Player_PageLoc
 sta LmOldPage
 lda Player_Y_Position
 sta LmOldY
 lda #0
 sta LmStandLevel
 sta LmResult
Level:lda #2
 sta LmProbe
Point:ldx LmProbe
 cpx #2
 beq Negative
 lda LmOldX
 clc
 adc Xoffs,x
 sta Player_X_Position
 lda LmOldPage
 adc #0
 jmp Page
Negative:lda LmOldX
 sec
 sbc #6
 sta Player_X_Position
 lda LmOldPage
 sbc #0
Page:sta Player_PageLoc
 ldx LmStandLevel
 lda Yoffs,x
 clc
 adc LmOldY
 sta Player_Y_Position
 ldy #0
 jsr BlockBufferColli_Head
 tay
 lda MTileAttribute,y
 and #MTILE_SOLID
 beq Next
 inc LmResult
 jmp Restore
Next:dec LmProbe
 bpl Point
 inc LmStandLevel
 lda LmStandLevel
 cmp #2
 bcc Level
Restore:
 lda LmOldX
 sta Player_X_Position
 lda LmOldPage
 sta Player_PageLoc
 lda LmOldY
 sta Player_Y_Position
 lda LmResult
 rts
Xoffs:.byte 0,6,$fa
Yoffs:.byte $ee,$fa
.endproc
.proc Z2WallLegacy
 LmGate CrossoverSourceWallDispatch
 lda GameEngineSubroutine
 cmp #8
 beq Native
 clc
 rts
Native:
 lda #15
 ldx RgCrouch
 beq :+
 lda #20
:sta LmTemp
 ldy R0
 cpy #1
 bne Left
 lda Player_X_Position
 clc
 adc LmTemp
 sta LmTemp2
 lda Player_PageLoc
 adc #0
 sta LmOldPage
 lda LmTemp2
 and #$f0
 sec
 sbc LmTemp
 sta Player_X_Position
 lda LmOldPage
 sbc #0
 sta Player_PageLoc
 lda Player_X_Position
 bne :+
 dec Player_PageLoc
:dec Player_X_Position
 jmp Stop
Left:
 lda #0
 ldx RgCrouch
 beq :+
 lda #5
:sta LmTemp
 lda Player_X_Position
 sec
 sbc LmTemp
 sta LmTemp2
 lda Player_PageLoc
 sbc #0
 sta LmOldPage
 lda LmTemp2
 and #$f0
 clc
 adc #16
 sta Player_X_Position
 lda LmOldPage
 adc #0
 sta Player_PageLoc
 lda Player_X_Position
 clc
 adc LmTemp
 sta Player_X_Position
 lda Player_PageLoc
 adc #0
 sta Player_PageLoc
Stop:
 lda #16
 sta SideCollisionTimer
 lda R0
 eor #$ff
 and Player_CollisionBits
 sta Player_CollisionBits
 lda #0
 sta MmVX
 sta MmVX+1
 sta MmVX+2
 sta MmXFraction
 sta MmXFraction+1
 sta Player_X_Speed
 sta Player_X_Scroll
 sec
 rts
.endproc
.popseg
