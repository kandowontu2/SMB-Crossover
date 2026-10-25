; Original TMNT1 velocities, jump stages and animation streams; SMB scene adapter.
.pushseg
.segment "TMNT_CORE"
.proc TnEnsure
 lda TnMarker
 cmp #$c9
 beq Life
 ldx #3
 lda #128
InitHP:sta TnHealth,x
 dex
 bpl InitHP
 lda #0
 ldx #7
InitGear:sta TnEquipment,x
 dex
 bpl InitGear
 sta TnFood
 sta TnDropCounter
 lda #$c9
 sta TnMarker
 jsr TnAreaClear
Life:
 lda TnLife
 sec
 sbc NumberofLives
 cmp #1
 bne Store
 lda #128
 ldx TnVariant
 sta TnHealth,x
 lda #0
 sta TnEquipment,x
 sta TnAmmo,x
 jsr TnAreaClear
Store:lda NumberofLives
 sta TnLife
 rts
.endproc
.proc TnAreaReset
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 bne Done
::TnAreaClear:
 lda #0
 tax
Loop:sta $5c00,x
 inx
 bne Loop
 lda #$ff
 sta TnInputFrame
 lda #8
 sta TnJumpStage
 lda #$80
 ldx #0
 jsr TnSetSequence
Done:rts
.endproc
.proc TnInputs
 lda FrameCounter
 cmp TnInputFrame
 beq Done
 sta TnInputFrame
 lda SavedJoypadBits
 eor TnPrevious
 and SavedJoypadBits
 sta TnFresh
 lda SavedJoypadBits
 sta TnPrevious
 sta TnHeld
Done:rts
.endproc
; Retains the native actor0/1 animation index/timer/terminator behavior.
.proc TnSetSequence
 sta TnSeq,x
 lda #0
 sta TnPhase,x
 lda TnSeq,x
 sec
 sbc #$80
 tay
 lda TnSequenceDuration,y
 sta TnTimer,x
 rts
.endproc
.proc TnUseSequence
 cmp TnSeq,x
 beq Done
 jmp TnSetSequence
Done:rts
.endproc
.proc TnAdvanceAnimation
 lda TnSeq,x
 beq Done
 dec TnTimer,x
 bne Fetch
 sec
 sbc #$80
 tay
 lda TnSequenceDuration,y
 sta TnTimer,x
 inc TnPhase,x
Fetch:
 lda TnSeq,x
 sec
 sbc #$80
 tay
 lda TnSequenceLo,y
 sta R0
 lda TnSequenceHi,y
 sta R1
 ldy TnPhase,x
 bpl Read
 lda #0
 sta TnPhase,x
 tay
Read:lda (R0),y
 cmp #$ff
 beq StorePhase
 cmp #$fe
 beq Restart
 cmp #$fd
 beq NewSequence
 sta TnPose,x
Done:rts
Restart:lda #0
StorePhase:sta TnPhase,x
 rts
NewSequence:iny
 lda (R0),y
 jmp TnSetSequence
.endproc
.proc TnMovement
 jsr TnEnsure
 jsr TnInputs
 inc TnClock
 lda TnFresh
 ora TnPendingFresh
 sta TnPendingFresh
 lda #0
 sta PlayerSize
 sta SmBall
 sta MmSliding
 sta MmFrictionYActive
 sta MmOnVine
 sta Player_X_Scroll
 lda TnFood
 sta PlayerStatus
 lda SwimmingFlag
 sta MmUnderwater
 lda #0
 sta TnUpdateTick
 lda TnHurt
 beq Cadence
 dec TnHurt
Cadence:
 lda TnClock
 and #1
 beq Tick
 rts                          ; native TMNT actor updates exactly every2 frames
Tick:
 lda #1
 sta TnUpdateTick
 lda TnPendingFresh
 sta TnFresh
 lda #0
 sta TnPendingFresh
 sta RgCrouch
 sta CrouchingFlag
 lda Player_State
 cmp #3
 bne Ordinary
 jmp TnClimbing
Ordinary:
 lda Player_X_Position
 sta TnOldX
 sta MmOldX
GroundSync:
 lda Player_State
 sta TnWasAir
 bne AirSync
 lda #0
 sta TnVYHi
 sta TnVYLo
 sta TnYFraction
 sta TnNativeState
 lda #8
 sta TnJumpStage
 jmp WallSync
AirSync:
 lda Player_Y_Speed
 cmp TnLastVy
 beq WallSync
 sta TnVYHi
 lda #0
 sta TnVYLo
 sta TnYFraction
 lda #8
 sta TnJumpStage
WallSync:
 lda Player_X_Speed
 bne MovePrepared
 lda TnLastVx
 beq MovePrepared
 lda #0
 sta TnVXHi
 sta TnVXLo
 sta TnXFraction
MovePrepared:
 jsr TnIntegrate              ; native world integration precedes input/gravity
Controls:
 lda TnHurtMove
 beq Direction
 dec TnHurtMove
 jmp Vertical
Direction:
 lda TnHeld
 and #3
 cmp #3
 beq NoDirection
 tay
 bne HasDirection
NoDirection:
 lda Player_State
 bne Jump
 ldy #0
 beq Horizontal
HasDirection:
 sty PlayerFacingDir
 lda TnAttack
 beq Horizontal
 lda TnHeld
 and #Down_Dir
 beq Horizontal
 lda Player_State
 bne Horizontal
 ldy #0
Horizontal:jsr TnNativeXVelocity
Jump:
 lda TnFresh
 and #A_Button
 beq Variable
 lda MmUnderwater
 bne WaterStroke
 lda Player_State
 bne Variable
 lda #$fa
 sta TnVYHi
 lda #0
 sta TnVYLo
 sta TnJumpStage
 lda #$80
 sta TnJumpHold
 lda #7
 sta TnNativeState
 lda #1
 sta Player_State
 lda #Sfx_SmallJump
 sta Square1SoundQueue
 jmp Attack
WaterStroke:
 ; Source swimming is a separate top-down dam mode. This SMB-water
 ; stroke uses native launch speed with capped gravity (explicit adapter).
 lda #$fd
 sta TnVYHi
 lda #0
 sta TnVYLo
 lda #8
 sta TnJumpStage
 jmp Attack
Variable:
Attack:
 lda TnFresh
 and #Select_Button
 beq Primary
 ldx TnVariant
 lda TnEquipment,x
 beq Primary
 lda TnGearSelected
 eor #1
 sta TnGearSelected
Primary:
 lda TnFresh
 and #B_Button
 beq Crouch
 lda TnAttack
 bne Crouch
 lda TnThrow
 bne Crouch
 jsr TnTrySecondary
 bcs Crouch
 jsr TnStartAttack
Crouch:
 lda TnHeld
 and #Down_Dir
 beq Vertical
 lda Player_State
 bne Vertical
 lda #1
 sta RgCrouch
 sta CrouchingFlag
Vertical:
 lda Player_State
 beq Animate
 lda TnWasAir
 beq DryState                 ; jump launch stores FA00 for the next native tick
 jsr TnNativeGravity
 jsr TnNativeVariableJump      ; original gravity first, then stage4/8 override
 lda MmUnderwater
 beq DryState
 lda TnVYHi
 bmi DryState
 cmp #2
 bcc DryState
 lda #2
 sta TnVYHi
DryState:
 lda #1
 ldx TnVYHi
 bmi :+
 lda #2
:sta Player_State
Animate:
 lda TnAttack
 bne Advance
 lda TnThrow
 bne Advance
 ldx #0
 lda RgCrouch
 beq NotCrouch
 lda #$83
 bne SetPose
NotCrouch:
 lda Player_State
 beq GroundPose
 lda #$85
 ldy TnNativeState
 cpy #8
 bne SetPose
 lda #$87
 bne SetPose
GroundPose:lda #$80
 ldy TnVXHi
 bne Walking
 ldy TnVXLo
 beq SetPose
Walking:lda #$81
SetPose:jsr TnUseSequence
Advance:
 ldx #0
 jsr TnAdvanceAnimation
 lda TnThrow
 beq :+
 lda TnPhase
 cmp #$ff
 bne Integrate
 lda #0
 sta TnThrow
 sta TnNativeFlags
 jmp Integrate
:
 lda TnAttack
 beq Integrate
 ldx #1
 jsr TnAdvanceAnimation
 lda TnPhase
 cmp #$ff
 bne Integrate
 lda #0
 sta TnAttack
 sta TnSeq+1
 sta TnPose+1
 sta TnNativeFlags
Integrate:
 jsr TnSourceShape
 sta RgCrouch
 sta CrouchingFlag
 jsr TnExport
 lda Player_X_Speed
 sta TnLastVx
 lda Player_Y_Speed
 sta TnLastVy
 rts
.endproc
.proc TnSourceShape
 ldy #5
Loop:lda CrouchSequences,y
 cmp TnSeq
 beq Crouched
 dey
 bpl Loop
 lda #0
 rts
Crouched:lda #1
 rts
CrouchSequences:.byte $83,$84,$92,$95,$98,$9b ; original PRG4:$9C62 list
.endproc
.proc TnClimbing
 lda #1
 sta MmOnVine
 lda #0
 sta TnVXHi
 sta TnVXLo
 sta Player_X_Speed
 sta Player_X_Scroll
 lda TnFresh
 and #A_Button
 beq Ladder
 lda #1
 sta Player_State
 lda #$fa
 sta TnVYHi
 sta Player_Y_Speed
 sta TnLastVy
 lda #0
 sta TnVYLo
 sta TnJumpStage
 sta TnYFraction
 sta MmOnVine
 lda #$80
 sta TnJumpHold
 lda #7
 sta TnNativeState
 jmp TnMovement::Ordinary
Ladder:
 ldx #0
 lda #$88                     ; original first-sewer ladder poses17/7
 jsr TnUseSequence
 lda TnHeld
 and #Up_Dir|Down_Dir
 beq Done
 cmp #Up_Dir
 beq Up
 lda #2
 bne Move
Up:lda #$fe
Move:clc
 adc Player_Y_Position
 sta Player_Y_Position
 ldx #0
 jsr TnAdvanceAnimation
Done:rts
.endproc
.proc TnStartAttack
 ldx TnVariant
 lda TnHeld
 and #Up_Dir
 bne Direction
 txa
 clc
 adc #4
 tax
 lda TnHeld
 and #Down_Dir
 beq Direction
 txa
 clc
 adc #4
 tax
Direction:txa
 clc
 adc #1
 sta TnAttack
 lda #0
 sta TnAttackHit
 lda PlayerFacingDir
 sta TnAttackFace
 lda TnAttackBodySequence,x
 ldx #0
 jsr TnSetSequence
 clc
 lda TnSeq
 adc #12
 ldx #1
 jsr TnSetSequence
 lda TnTimer
 sta TnTimer+1
 lda #4
 sta TnNativeFlags
 lda #Sfx_Fireball
 sta Square1SoundQueue
 rts
.endproc
.proc TnIntegrate
 clc
 lda TnXFraction
 adc TnVXLo
 sta TnXFraction
 lda Player_X_Position
 adc TnVXHi
 sta Player_X_Position
 lda #0
 ldx TnVXHi
 bpl :+
 lda #$ff
:adc Player_PageLoc
 sta Player_PageLoc
 lda Player_X_Position
 sec
 sbc TnOldX
 sta Player_X_Scroll
 lda Player_State
 beq Done
 clc
 lda TnYFraction
 adc TnVYLo
 sta TnYFraction
 lda Player_Y_Position
 adc TnVYHi
 sta Player_Y_Position
 lda #0
 ldx TnVYHi
 bpl :+
 lda #$ff
:adc Player_Y_HighPos
 sta Player_Y_HighPos
 cmp #1
 bcc Clamp
 bne Done
 lda Player_Y_Position
 cmp #40
 bcs Done
Clamp:
 lda #40
 sta Player_Y_Position
 lda #1
 sta Player_Y_HighPos
 lda #0
 sta TnVYHi
 sta TnVYLo
 sta TnYFraction
Done:rts
.endproc
.proc TnExport
 lda TnVXLo
 lsr
 lsr
 lsr
 lsr
 sta TnTemp
 lda TnVXHi
 asl
 asl
 asl
 asl
 ora TnTemp
 sta Player_X_Speed
 bpl :+
 eor #$ff
 clc
 adc #1
:sta Player_XSpeedAbsolute
 lda TnVYHi
 sta Player_Y_Speed
 rts
.endproc
.popseg
