; Exact ID19 admission only. Legacy inventory and raw-ID tables are not widened.
.pushseg
.segment "TMNT_COMBAT"
.proc TnMovementDispatch
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 beq Native
 farcall CdMovementDispatch,jmp
Native:farcall TnMovement,jmp
.endproc
.proc TnGraphicsDispatch
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 beq Native
 farcall CdGraphicsDispatch,jmp
Native:farcall TnGraphics,jmp
.endproc
.proc TnPortraitDispatch
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 beq Native
 farcall CdPortraitDispatch,jmp
Native:farcall TnPortrait,jmp
.endproc
.proc TnDeathDispatch
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 beq Native
 farcall CdDeathDispatch,jmp
Native:jmp TnDeath
.endproc
.proc TnWeaponsDispatch
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 beq Native
 farcall CdWeaponsDispatch,jmp
Native:jmp TnAllWeapons
.endproc
.proc TnDrawDispatch
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 beq Native
 farcall CdNewDrawDispatch,jmp
Native:jmp TnDraw
.endproc
.proc TnSpecialDrawDispatch
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 beq Native
 farcall Z2SpecialDrawGate,jmp
Native:
 lda #0
 sta SsChrActive
 rts
.endproc
.proc TnInjuryStatusDispatch
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 beq Native
 farcall CdInjuryStatusDispatch,jmp
Native:jmp TnInjuryStatus
.endproc
.proc TnInjuryStartDispatch
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 beq Native
 farcall CdInjuryStartDispatch,jmp
Native:jmp TnInjuryStart
.endproc
.proc TnPickupDispatch
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 bne Legacy
 phx
 farcall TnCollectEquipment
 plx
 bcs Collected
 phx
 lda PowerUpType,x
 jsr TnHeal
 plx
 bcc Legacy
Collected:
 phx
 jsr EraseEnemyObject
 plx
 lda #6
 jsr SetupFloateyNumber
 rts
Legacy:farcall CdPickupDispatch,jmp
.endproc
.proc TnBodyDispatch
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 bne Legacy
 pha
 lda AreaType
 sta GuestBodyStompAllowed
 lda CrossoverBehaviorVersion
 sta GuestBodyNoStomp
 pla
 clc
 rts
Legacy:farcall CdBodyDispatch,jmp
.endproc
.proc TnResetDispatch
 farcall CdResetDispatch
 farcall TnAreaReset,jmp
.endproc
.proc TnAdderDispatch
 cmp #CHARACTER_TMNT
 beq Native
 farcall CdAdderDispatch,jmp
Native:ldy #0                 ; native big profile side/feet, custom signed head
 sec
 rts
.endproc
.proc TnBoxDispatch
 cmp #CHARACTER_TMNT
 beq Native
 farcall CdBoxDispatch,jmp
Native:ldy #0
 rts
.endproc
.proc TnHeadDispatch
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 beq Native
 farcall KbHeadDispatch,jmp
Native:
 sty TnSavedY
 lda Player_Y_Position
 sta TnTempY
 lda Player_X_Position
 sta TnTempX
 lda Player_PageLoc
 sta TnTempPage
 jsr TnHeadTop
 sta TnTemp2
 lda #32
 sec
 sbc TnTemp2
 cmp TnTempY
 bcc HeadVisible
 beq HeadVisible
 lda #0
 sta R3
 rts                         ; terrain buffers begin below the32px HUD
HeadVisible:
 lda TnTemp2
 sec
 sbc #4                      ; original big-profile head sample is+4
 clc
 adc Player_Y_Position
 sta Player_Y_Position
 jsr BlockBufferColli_Head
 ; The source-width side probes resolve corner contact on X. Off-center
 ; head samples would mistake pipe/stair sides for ceilings and push down.
Sampled:
 pha
 lda TnTempX
 sta Player_X_Position
 lda TnTempPage
 sta Player_PageLoc
 lda TnTempY
 sta Player_Y_Position
 pla
 pha
 beq Restore
 ldx Player_Y_Speed
 bpl Restore
 phy
 ldy R3
 lda MTileAttribute,y
 and #MTILE_SOLID|MTILE_CLIMB
 cmp #MTILE_SOLID
 bne RestoreY
 lda R2
 clc
 adc #48                     ; tile bottom=R2+48
 sec
 sbc TnTemp2                 ; actual source top:−8 stand,+2 roll,+5 crouch
 sta Player_Y_Position
 and #15
 sta R4
 lda #0
 sta TnYFraction
RestoreY:ply
Restore:pla
 rts
.endproc
.proc TnHeadTop
 lda TnSeq
 cmp #$87
 beq Roll
 lda RgCrouch
 bne Crouch
 lda #$f8                    ; center+8 minus native standing radius16
 rts
Roll:lda #2                  ; center+8 minus native somersault radius6
 rts
Crouch:lda #5                ; center+16 minus native crouching radius11
 rts
.endproc
.proc TnSideDispatch
 lda GameEngineSubroutine
 cmp #8
 beq Gameplay
 jmp BlockBufferColli_Side    ; retain the native pole/castle exit samples
Gameplay:
 sty TnSavedY
 lda Player_Y_Position
 sta TnTempY
 tya
 and #1
 beq Lower
 jsr TnHeadTop
 sta TnTemp
 lda #32
 sec
 sbc TnTemp
 cmp TnTempY
 bcc UpperVisible
 beq UpperVisible
 lda #0
 sta R3
 ldy TnSavedY
 rts
UpperVisible:
 lda TnTemp
 sec
 sbc #8                      ; native upper side sample+8
 jmp Shift
Lower:
 lda #24
 ldy TnSeq
 cpy #$87
 bne :+
 lda #14
 bne Bottom
:ldy RgCrouch
 beq Bottom
 lda #27
Bottom:
 sta TnTemp
 lda #32
 sec
 sbc TnTemp
 cmp TnTempY
 bcc LowerVisible
 beq LowerVisible
 lda #0
 sta R3
 ldy TnSavedY
 rts
LowerVisible:
 lda TnTemp
 sec
 sbc #24                     ; native lower side sample+24
Shift:clc
 adc Player_Y_Position
 sta Player_Y_Position
 ldy TnSavedY
::TnMiddleProbeSpan:
 jsr TnSideMiddleProbe
 pha
 lda TnTempY
 sta Player_Y_Position
 pla
 rts
.endproc
.proc TnBoundingBoxGate
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 beq Native
 pla
 plp
 jmp BoundingBoxCore
Native:
 pla
 plp
 jsr BoundingBoxCore
 lda Player_Rel_XPos
 clc
 adc #3
 sta BoundingBox_UL_XPos
 lda Player_Rel_XPos
 clc
 adc #13
 sta BoundingBox_LR_Corner
 ; Exact native player radii: standing5x16; crouched5x11+8Y;
 ; somersault5x6. Native actor center is SMB origin+(8,8).
 lda #$f8
 ldx #24
 ldy TnSeq
 cpy #$87
 bne Crouch
 lda #2
 ldx #14
 bne Store
Crouch:ldy RgCrouch
 beq Store
 lda #5
 ldx #27
Store:clc
 adc Player_Rel_YPos
 sta BoundingBox_UL_YPos
 txa
 clc
 adc Player_Rel_YPos
 sta BoundingBox_LR_Corner+1
 ldx #0
 ldy #0
Done:rts
.endproc
.proc TnVisibleDispatch
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 bne Legacy
 lda TnHurt
 beq Show
 lda FrameCounter
 lsr
 bcs Hide
Show:sec
 rts
Hide:clc
 rts
Legacy:farcall DwPlayerVisible,jmp
.endproc
.popseg
