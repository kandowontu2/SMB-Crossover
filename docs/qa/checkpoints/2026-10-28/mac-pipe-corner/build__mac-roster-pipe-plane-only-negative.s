.pushseg
.segment "LM_CORE"
.proc Z2LegacyBoundingBoxGate
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
 jsr MacRosterTerrainProfile
 lda Player_Rel_XPos
 clc
 adc MacTerrainLeft,x
 sta BoundingBox_UL_XPos
 lda Player_Rel_XPos
 clc
 adc MacTerrainRight,x
 sta BoundingBox_LR_Corner
 lda Player_Rel_YPos
 clc
 adc MacTerrainHead,x
 sta BoundingBox_UL_YPos
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
 LmGate NrHead
::MacRosterTerrainHead:
 sty LmSavedY
 lda Player_Y_Position
 sta LmOldY
 lda Player_X_Position
 sta LmOldX
 lda Player_PageLoc
 sta LmOldPage
 jsr MacRosterTerrainProfile
 lda LmOldY
 clc
 adc MacTerrainHeadAdjust,x
 sta Player_Y_Position
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
 jsr MacRosterTerrainProfile
 lda LmOldX
 sec
 sbc MacTerrainHeadLeftShift,x
 sta Player_X_Position
 lda LmOldPage
 sbc #0
 sta Player_PageLoc
 ldy LmSavedY
 jsr BlockBufferColli_Head
 bne Sampled
 jsr MacRosterTerrainProfile
 lda LmOldX
 clc
 adc MacTerrainHeadRightShift,x
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
 jsr MacRosterTerrainProfile
 ; A broad head edge can enter a pipe from its SIDE while rising. Only a
 ; crossed lower cell plane is a ceiling; otherwise the side owner separates
 ; horizontally. Quantized upward speed conservatively includes fractional
 ; movement, retaining real corner/ceiling contacts within that last step.
 lda R2
 clc
 adc #48
 sta LmTemp
 lda LmOldY
 clc
 adc MacTerrainHead,x
 sec
 sbc Player_Y_Speed
 cmp LmTemp
 bcc SideOnly
 lda R2
 clc
 adc #48
 sec
 sbc MacTerrainHead,x
 sta Player_Y_Position
 lda #12                     ; virtual native head Y = tile bottom minus4
 sta R4
 lda #0
 sta MarioJumpRise
 sta MarioJumpFraction
 sta MarioJumpFraction+1
 sta MmYFraction
 sta MmYFraction+1
EndY:ply
Finish:ldx #0
 pla
 rts
SideOnly:
 ply
 pla
 lda #0
 sta R3
 ldx #0
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
::MacRosterTerrainSide:
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
 jsr MacRosterTerrainProfile
 ldy LmSavedY
 cpy #5
 bcs Right
 lda MacTerrainSideExpand,x
 sta LmTemp
 lda LmOldX
 sec
 sbc LmTemp
 sta Player_X_Position
 lda LmOldPage
 sbc #0
 sta Player_PageLoc
 jmp Probe
Right:lda MacTerrainSideExpand,x
 clc
 adc LmOldX
 sta Player_X_Position
 lda LmOldPage
 adc #0
 sta Player_PageLoc
Probe:
 lda LmSavedY
 and #1
 beq Lower
 lda #0
 sta LmProbe
Loop:
 jsr MacRosterTerrainProfile
 lda MacTerrainSideTopAdjust,x
 ldy LmProbe
 beq :+
 lda MacTerrainSideMidAdjust,x
: 
 clc
 adc LmOldY
 sta Player_Y_Position
 ldy LmSavedY
::LmVisibleSideCall:
 jsr LmVisibleSideProbe
 bne Restore
 inc LmProbe
 lda LmProbe
 cmp #2
 bcc Loop
 lda R3
 jmp Restore
Lower:lda LmOldY
 clc
 adc #6                      ; native lower24 -> logical near-foot30
 sta Player_Y_Position
 ldy LmSavedY
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
 ldx #0
 ldy LmSavedY
 pla
 rts
.endproc
.proc LmSideLegacy
 lda SelectedCharacter
 cmp #CHARACTER_SOPHIA
 bne Native
 farcall SophiaSourceSideProbe,jmp
Native:jmp BlockBufferColli_Side
.endproc
.proc LmStandBlocked
 jsr MacRosterTerrainProfile
 txa
 and #$fe
 tax
 cpx #4
 bcc Save
 lda #0                      ; Tyson duck is not shorter than idle
 rts
Save:
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
Point:
 jsr MacRosterTerrainProfile
 txa
 and #$fe
 tax
 lda MacTerrainHeadRightShift,x
 sta LmTemp
 lda MacTerrainHeadLeftShift,x
 sta LmTemp2
 ldx LmProbe
 cpx #2
 beq Negative
 cpx #0
 bne Positive
 lda #0
 sta LmTemp
Positive:
 lda LmOldX
 clc
 adc LmTemp
 sta Player_X_Position
 lda LmOldPage
 adc #0
 jmp Page
Negative:lda LmOldX
 sec
 sbc LmTemp2
 sta Player_X_Position
 lda LmOldPage
 sbc #0
Page:sta Player_PageLoc
 jsr MacRosterTerrainProfile
 txa
 and #$fe
 tax
 lda MacTerrainHeadAdjust,x
 ldy LmStandLevel
 beq :+
 lda MacTerrainStandLowerAdjust,x
: 
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
 jcc Level
Restore:
 lda LmOldX
 sta Player_X_Position
 lda LmOldPage
 sta Player_PageLoc
 lda LmOldY
 sta Player_Y_Position
 lda LmResult
 rts
.endproc
.proc Z2WallLegacy
 LmGate CrossoverSourceWallDispatch
 lda GameEngineSubroutine
 cmp #8
 beq Native
 clc
 rts
Native:
 jsr MacRosterTerrainProfile
 lda MacTerrainRight,x
 sta LmTemp
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
 lda MacTerrainLeft,x
 sta LmTemp
 lda Player_X_Position
 clc
 adc LmTemp
 sta LmTemp2
 lda Player_PageLoc
 adc #0
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
 sec
 sbc LmTemp
 sta Player_X_Position
 lda Player_PageLoc
 sbc #0
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
.proc MacRosterTerrainProfile
 lda MacVariant
 cmp #3
 bcc :+
 lda #0
:asl
 ldx RgCrouch
 beq :+
 ora #1
:tax
 rts
.endproc
; Conservative body core inside actual idle/duck masks; feet stay+32.
; Tyson's guard remains tall when ducking. No former composite expansion.
MacTerrainLeft:             .byte 2,2,0,0,2,2
MacTerrainRight:            .byte 13,13,15,15,13,13
MacTerrainHead:             .byte 4,12,5,14,$fa,$f9
MacTerrainHeadAdjust:       .byte 0,8,1,10,$f6,$f5
MacTerrainHeadLeftShift:    .byte 6,6,8,8,6,6
MacTerrainHeadRightShift:   .byte 5,5,7,7,5,5
MacTerrainSideExpand:       .byte 0,0,2,2,0,0
MacTerrainSideTopAdjust:    .byte 0,8,1,10,$f6,$f5
MacTerrainSideMidAdjust:    .byte 11,15,11,16,6,5
MacTerrainStandLowerAdjust: .byte 7,7,9,9,$f5,$f5
.popseg
