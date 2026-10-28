.export RcEnsure,RcReset,RcMovement,RcInjuryStatus,RcInjuryStart,RcDeathStart,RcDeath
.export RcPickup,RcHeal,RcVisible,RcBodyContact,RcCollisionAdder,RcCollisionBox
.export RcHeadProbe,RcSideProbe,RcEnemyControl
.export RcGlobalInit,RcReleaseCarry
.pushseg
.segment "RIVER_CITY_CORE"
; Loader-owned identity; AreaPointer may describe a future pipe destination.
.proc RcSceneKey
 lda AreaType
 .repeat 5
  asl
 .endrepeat
 ora AreaAddrsLOffset
 rts
.endproc

.proc RcGlobalInit
 lda #0
 sta RcMarker
 jmp RcEnsure
.endproc
.proc RcEnsure
 lda RcMarker
 cmp #$c7
 beq CheckLife
 lda #48
 sta RcHealth
 sta RcHealth+1
 lda #0
 sta RcTier
 sta RcTier+1
 lda #$c7
 sta RcMarker
 jsr RcClear
CheckLife:
 lda RcLife
 sec
 sbc NumberofLives
 cmp #1                       ; earned lives do not erase earned books/stamina
 bne Context
 ldx RcVariant
 lda #48
 sta RcHealth,x
 lda #0
 sta RcTier,x
 jsr RcClear
Context:
 lda NumberofLives
 sta RcLife
 jsr RcSceneKey
 cmp RcArea
 bne ResetArea
 lda WorldNumber
 cmp RcWorld
 bne ResetArea
 lda RcVariant
 cmp RcSavedVariant
 beq Done
ResetArea:
 jsr RcClear
Done:rts
.endproc
.proc RcClear
 lda #0
 ldx #$7f
Loop:sta $5c00,x
 dex
 bpl Loop
 sta MmVX
 sta MmVX+1
 sta MmVX+2
 sta MmVY
 sta MmVY+1
 sta MmVY+2
 sta MmXFraction
 sta MmXFraction+1
 sta MmYFraction
 sta MmYFraction+1
 sta GuestHurtKind
 sta GuestHurtTicks
 lda #$ff
 sta RcCarrySlot
 sta RcThrowSlot
 sta RcInputStamp
 lda NumberofLives
 sta RcLife
 jsr RcSceneKey
 sta RcArea
 lda WorldNumber
 sta RcWorld
 lda RcVariant
 and #1
 sta RcVariant
 sta RcSavedVariant
 lda #1
 sta RcHudDirty
 rts
.endproc
.proc RcReset
 lda SelectedCharacter
 cmp #CHARACTER_RIVER_CITY
 bne Done
 jsr RcEnsure
 jmp RcClear
Done:rts
.endproc
.proc RcMovement
 jsr RcEnsure
 lda TimerControl
 jne Done
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda GamePauseStatus
 and #1
 jne Done
 lda SavedJoypadBits
 sta RcHeld
 eor RcPrevious
 and RcHeld
 sta RcFresh
 lda RcHeld
 sta RcPrevious
 inc RcClock
 lda #0
 sta PlayerSize                 ; native32px body, native crouch profile
 sta SmBall
 sta MmSliding
 sta MmFrictionYActive
 sta MmUnderwater
 sta MmOnVine
 sta CrouchingFlag
 sta RgCrouch
 sta Player_X_Scroll
 ldx RcVariant
 lda RcTier,x
 sta PlayerStatus
 lda RcHurt
 beq :+
 dec RcHurt
:lda RcHurtMove
 beq :+
 dec RcHurtMove
:lda RcAttack
 beq :+
 dec RcAttack
:lda RcTapWindow
 beq :+
 dec RcTapWindow
:lda Player_State
 cmp #3
 bne Ordinary
 lda #1
 sta MmOnVine
 farcall MegaManClimbing,jmp
Ordinary:
 lda Player_X_Position
 sta MmOldX
 sta RcOldX
 lda Player_State
 bne AirSync
 lda #0
 sta MmVY
 sta MmVY+1
 sta MmVY+2
 sta MmYFraction
 sta MmYFraction+1
AirSync:
 lda Player_State
 beq WallSync
 lda Player_Y_Speed
 cmp MmVY+2
 beq WallSync
 sta MmVY+2                   ; honor real ceiling/stomp/spring resolution
 lda #0
 sta MmVY+1
 sta MmYFraction+1
WallSync:
 lda Player_X_Speed
 bne Input
 lda RcLastVx
 beq Input
 jsr RcZeroX
Input:
 lda RcHurtMove
 bne Vertical
 lda RcFresh
 and #3
 beq MoveInput
 cmp RcTapDir
 bne Remember
 ldx RcTapWindow
 beq Remember
 ldx #1
 stx RcRun
Remember:sta RcTapDir
 lda #12
 sta RcTapWindow
MoveInput:
 jsr RcHorizontal
 lda RcFresh
 and #A_Button
 beq Duck
 lda Player_State
 bne Duck
 lda #1
 sta Player_State
 lda #$80                    ; SMB traversal adaptation: -6.5px/update
 sta MmVY+1
 lda #$f9
 sta MmVY+2
 lda #Sfx_BigJump
 sta Square1SoundQueue
Duck:
 lda RcHeld
 and #Down_Dir
 beq Vertical
 lda Player_State
 ora RcAttack
 bne Vertical
 lda #1
 sta RgCrouch
 sta CrouchingFlag
Vertical:
 lda SwimmingFlag
 beq Dry
 lda #1
 sta MmUnderwater
 lda RcFresh
 and #A_Button
 beq SwimGravity
 lda #$80
 sta MmVY+1
 lda #$fd
 sta MmVY+2
SwimGravity:
 lda #$18
 ldy #2
 bne Gravity
Dry:
 lda Player_State
 beq Integrate
 lda #$40                    ; .25px/update²: explicitly stronger SMB jump
 ldy #7
Gravity:
 sty RcTemp2
 clc
 adc MmVY+1
 sta MmVY+1
 lda MmVY+2
 adc #0
 sta MmVY+2
 bmi Integrate
 cmp RcTemp2
 bcc Integrate
 sty MmVY+2
 lda #0
 sta MmVY+1
Integrate:
 lda RcAttack
 beq :+
 lda RcAttackFace
 sta PlayerFacingDir
:
 lda Player_Y_Position
 sta RcTerrainOldY
 jsr RcIntegrate
 jsr RcTerrainWallPrepass
 lda Player_X_Speed
 sta RcLastVx
Done:rts
.endproc
.proc RcHorizontal
 lda RcHeld
 and #3
 cmp #1
 beq Direction
 cmp #2
 beq Direction
 lda #0
 sta RcRun
 jmp RcFriction
Direction:
 sta PlayerFacingDir
 lda RcAttack
 beq Speed
 lda Player_State
 bne Speed
 jmp RcFriction                 ; grounded attacks have a finite recovery
Speed:
 lda #$80                     ; native RCR walk12/8=1.5, run28/8=3.5
 sta MmVX+1
 lda #1
 ldx RcRun
 beq Sign
 lda #3
Sign:sta MmVX+2
 lda PlayerFacingDir
 cmp #2
 bne Done
 jmp RcNegateX
Done:rts
.endproc
.proc RcZeroX
 lda #0
 sta MmVX
 sta MmVX+1
 sta MmVX+2
 rts
.endproc
.proc RcNegateX
 sec
 lda #0
 sbc MmVX+1
 sta MmVX+1
 lda #0
 sbc MmVX+2
 sta MmVX+2
 rts
.endproc
.proc RcFriction
 lda MmVX+2
 pha
 bpl Positive
 jsr RcNegateX
Positive:
 sec
 lda MmVX+1
 sbc #$80
 sta MmVX+1
 lda MmVX+2
 sbc #0
 sta MmVX+2
 bpl Restore
 jsr RcZeroX
Restore:
 pla
 bpl Done
 jmp RcNegateX
Done:rts
.endproc
.proc RcIntegrate
 clc
 lda MmXFraction+1
 adc MmVX+1
 sta MmXFraction+1
 lda Player_X_Position
 adc MmVX+2
 sta Player_X_Position
 lda #0
 ldx MmVX+2
 bpl :+
 lda #$ff
:adc Player_PageLoc
 sta Player_PageLoc
 lda Player_X_Position
 sec
 sbc RcOldX
 sta Player_X_Scroll
 lda MmVX+1
 lsr
 lsr
 lsr
 lsr
 sta RcTemp
 lda MmVX+2
 asl
 asl
 asl
 asl
 ora RcTemp
 sta Player_X_Speed
 bpl :+
 eor #$ff
 clc
 adc #1
:sta Player_XSpeedAbsolute
 lda Player_State
 beq Done
 clc
 lda MmYFraction+1
 adc MmVY+1
 sta MmYFraction+1
 lda Player_Y_Position
 adc MmVY+2
 sta Player_Y_Position
 lda #0
 ldx MmVY+2
 bpl :+
 lda #$ff
:adc Player_Y_HighPos
 sta Player_Y_HighPos
 cmp #1
 bcc Clamp
 bne Report
 lda Player_Y_Position
 cmp #16
 bcs Report
Clamp:
 lda #16
 sta Player_Y_Position
 lda #1
 sta Player_Y_HighPos
 lda #0
 sta MmVY+1
 sta MmVY+2
 sta MmYFraction+1
Report:
 lda MmVY+2
 sta Player_Y_Speed
Done:rts
.endproc
.proc RcInjuryStatus
 lda RcHurt
 bne Protected
 ldx RcVariant
 lda RcHealth,x
 cmp #9
 bcs Protected
 lda #0
 sta RcHealth,x
 rts
Protected:lda #1
 rts
.endproc
.proc RcInjuryStart
 lda RcHurt
 bne Protected
 ldx RcVariant
 lda RcHealth,x
 sec
 sbc #8                       ; explicit SMB contact/stamina adaptation
 bcc Dead
 beq Dead
 sta RcHealth,x
 lda #90
 sta RcHurt
 lda #16
 sta RcHurtMove
 lda #8
 sta InjuryTimer
 lda #0
 sta RcAttack
 sta TimerControl
 sta PlayerChangeSizeFlag
 jsr RcReleaseCarry
 lda #1
 sta RcHudDirty
 sta Player_State
 lda #0
 sta MmVY+1
 lda #$fd
 sta MmVY+2
 sta Player_Y_Speed
 lda #$80
 sta MmVX+1
 lda #1
 sta MmVX+2
 lda PlayerFacingDir
 cmp #2
 beq Sound
 jsr RcNegateX
Sound:
 lda #Sfx_Bump
 sta Square1SoundQueue
Protected:sec
 rts
Dead:
 lda #0
 sta RcHealth,x
 jmp KillPlayer
.endproc
.proc RcHeal
 cmp #2
 bcs No
 pha
 ldx RcVariant
 lda RcHealth,x
 clc
 adc #24
 cmp #65
 bcc :+
 lda #64
:sta RcHealth,x
 pla
 lda RcTier,x
 cmp #2
 bcs TierReady
 inc RcTier,x                 ; mushroom/flower replace native food/book shops
TierReady:
 lda RcTier,x
 sta PlayerStatus
 lda #1
 sta RcHudDirty
 lda #Sfx_PowerUpGrab
 sta Square2SoundQueue
 sec
 rts
No:clc
 rts
.endproc
.proc RcPickup
 phx
 lda PowerUpType,x
 jsr RcHeal
 plx
 bcc No
 phx
 jsr EraseEnemyObject
 plx
 lda #6
 jsr SetupFloateyNumber
 sec
 rts
No:clc
 rts
.endproc
.proc RcDeathStart
 jsr RcReleaseCarry
 ldx RcVariant
 lda #0
 sta RcHealth,x
 sta RcAttack
 sta RcThrowAge
 lda #$ff
 sta RcCarrySlot
 sta RcThrowSlot
 rts
.endproc
.proc RcDeath
 inc MmDeathAge
 lda MmDeathAge
 cmp #180
 bcc Done
 lda #6
 sta GameEngineSubroutine
 lda #0
 sta TimerControl
Done:rts
.endproc
.proc RcVisible
 lda RcHurt
 beq Show
 lda FrameCounter
 lsr
 bcs Hide
Show:sec
 rts
Hide:clc
 rts
.endproc
.proc RcBodyContact
 pha
 lda AreaType
 sta GuestBodyStompAllowed
 lda CrossoverBehaviorVersion
 sta GuestBodyNoStomp
 pla
 ldx ObjectOffset
 cpx #6
 bcs No
 cpx RcCarrySlot
 beq Protected
 lda RcEnemyStun,x
 bne Protected
No:clc
 rts
Protected:sec
 rts
.endproc
.proc RcCollisionAdder
 clc                           ; standard PlayerSize/CrouchingFlag profile
 rts
.endproc
.proc RcCollisionBox
 ldy #0
 lda CrouchingFlag
 beq Done
 ldy #2
Done:rts
.endproc
.proc RcHeadProbe
 jmp BlockBufferColli_Head
.endproc
.proc RcSideProbe
 jmp BlockBufferColli_Side
.endproc
; Optional root actor-movement gate: X=native actor; C1 means movement consumed.
; Never changes the actor's native state enum, ID, life, score, or health.
.proc RcEnemyControl
 lda SelectedCharacter
 cmp #CHARACTER_RIVER_CITY
 bne No
 cpx #6
 bcs No
 cpx RcCarrySlot
 bne Stun
 lda Enemy_Flag,x
 beq Release
 lda Enemy_ID,x
 cmp RcCarryType
 bne Release
 lda RcHurt
 bne Release
 lda Player_X_Position
 sta Enemy_X_Position,x
 lda Player_PageLoc
 sta Enemy_PageLoc,x
 lda Player_Y_Position
 sec
 sbc #16
 sta Enemy_Y_Position,x
 lda #1
 sta Enemy_Y_HighPos,x
 lda #0
 sta Enemy_X_Speed,x
 sta Enemy_Y_Speed,x
 sec
 rts
Release:
 jsr RcReleaseCarry
Stun:
 lda RcEnemyStun,x
 beq No
 lda Enemy_Flag,x
 cmp RcEnemyStamp,x
 bne Stale
 lda Enemy_ID,x
 clc
 adc #1
 cmp RcEnemyType,x
 bne Stale
 lda #0
 sec
 rts
Stale:
 lda #0
 sta RcEnemyStun,x
No:clc
 rts
.endproc
.proc RcReleaseCarry
 ldx RcCarrySlot
 cpx #6
 bcs Clear
 lda Enemy_Flag,x
 beq Clear
 lda Enemy_ID,x
 cmp RcCarryType
 bne Clear
 lda RcCarryVX
 sta Enemy_X_Speed,x
 lda RcCarryVY
 sta Enemy_Y_Speed,x
Clear:
 lda #$ff
 sta RcCarrySlot
 rts
.endproc
.popseg
