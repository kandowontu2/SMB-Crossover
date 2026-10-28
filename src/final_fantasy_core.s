.pushseg
.segment "FINAL_FANTASY_CORE"
.export FfGlobalInit,FfEnsure,FfAreaReset,FfMovement,FfPickup,FfFullPower
.export FfInjuryStatus,FfInjuryStart,FfDeathStart,FfStompPolicy,FfBox,FfAdder,FfHead
.export FfCollisionBounds
.export FfDeathUpdate
.export FfSide
.proc FfSceneKey
 lda AreaType
 .repeat 5
 asl
 .endrepeat
 ora AreaAddrsLOffset
 rts
.endproc
.proc FfGlobalInit
 lda #0
 sta FfVariant
 sta FfReady
 rts
.endproc
.proc FfEnsure
 lda SelectedCharacter
 cmp #CHARACTER_FINAL_FANTASY
 bne Done
 lda FfReady
 cmp #$f7
 bne NewLife
 lda NumberofLives
 sec
 sbc FfLife
 bmi NewLife
 lda NumberofLives
 sta FfLife
 jsr FfSceneKey
 cmp FfArea
 bne Area
 lda WorldNumber
 cmp FfWorld
 beq Done
 bne Area
NewLife:
 lda #0
 sta FfPower
 sta FfEarned
 sta FfHealCharges
 lda #$f7
 sta FfReady
Area:jsr FfAreaReset
Done:rts
.endproc
.proc FfAreaReset
 lda SelectedCharacter
 cmp #CHARACTER_FINAL_FANTASY
 bne Done
 lda #0
 ldx #$7f
Clear:sta $5c00,x
 dex
 bpl Clear
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
 sta RgCrouch
 sta MmSliding
 sta FfWalk
 sta FfWalkDelay
 sta FfFireClock
 sta FfFireClock+1
 sta FfModerateClock
 sta FfModerateClock+1
 lda SavedJoypadBits
 sta FfPrevious
 lda #$ff
 sta FfPaletteAck
 lda NumberofLives
 sta FfLife
 jsr FfSceneKey
 sta FfArea
 lda WorldNumber
 sta FfWorld
Done:rts
.endproc
; Call once per active movement update. Carry clear = genuine climb handoff;
; caller then runs its existing native climbing path, never this dry integrator.
.proc FfMovement
 lda SelectedCharacter
 cmp #CHARACTER_FINAL_FANTASY
 bne Foreign
 jsr FfEnsure
 lda Player_State
 cmp #3
 beq Climb
 lda SavedJoypadBits
 eor FfPrevious
 and SavedJoypadBits
 sta FfFresh
 lda SavedJoypadBits
 sta FfPrevious
 lda FfPower
 sta PlayerStatus
 lda #0
 sta PlayerSize
 sta CrouchingFlag
 sta RgCrouch
 sta MmSliding
 sta SmBall
 sta MmOnVine
 sta MmFrictionYActive
 jsr FfWaterMode
 cmp MmUnderwater
 beq :+
 lda #0
 sta FfGPhase
:jsr FfWaterMode
 sta MmUnderwater
 lda Player_X_Position
 sta MmOldX
 lda FfHurt
 beq :+
 dec FfHurt
 lda #1
 sta InjuryTimer
:lda FfHurtMove
 beq Controlled
 dec FfHurtMove
 jmp Vertical
Climb:
 lda SavedJoypadBits
 sta FfPrevious                ; no spurious held-A edge after real vine exit.
 lda #0
 sta FfFresh
Foreign:clc
 rts
Controlled:
 jsr FfActionTick
 lda Player_State
 bne Air
 lda #0
 sta MmVY
 sta MmVY+1
 sta MmVY+2
 sta MmYFraction+1
 sta FfJump
 sta FfGPhase
 lda FfFresh
 and #A_Button
 beq Horizontal
 ; Source ground A cancels attack/preparation/cast; no release-height cut.
 lda #0
 sta FfAction
 sta FfAge
 sta MmVY
 lda #$c0
 sta MmVY+1
 lda #$fa                       ; exact -5.25px/update = -630/120.
 sta MmVY+2
 sta Player_Y_Speed
 lda #1
 sta FfJump
 sta Player_State
 lda #Sfx_BigJump
 sta Square1SoundQueue
 bne Horizontal
Air:
 lda Player_Y_Speed             ; import genuine head/feet/spring resolution.
 cmp MmVY+2
 beq Horizontal
 sta MmVY+2
 lda #0
 sta MmVY
 sta MmVY+1
Horizontal:
 lda #0
 sta MmVX
 sta MmVX+1
 sta MmVX+2
 lda Player_State
 bne Direction
 lda FfAction
 bne Vertical
 lda SavedJoypadBits
 and #Down_Dir
 beq Direction
 lda #1
 sta RgCrouch
 sta CrouchingFlag
 bne Vertical
Direction:
 lda SavedJoypadBits
 and #3
 cmp #1
 beq MoveX
 cmp #2
 bne Vertical
MoveX:
 sta PlayerFacingDir
 lda #$aa
 sta MmVX+1
 lda #1
 sta MmVX+2
 lda FfHPhase
 clc
 adc #2
 cmp #3
 bcc Phase
 sbc #3
 inc MmVX+1
Phase:sta FfHPhase
 lda MmUnderwater
 beq Signed
 lda #1
 sta MmUnderwater
 lda Player_State
 bne Signed
 lda #$c0                      ; inherited ground-water cap90/120=.75.
 sta MmVX+1
 lda #0
 sta MmVX+2
Signed:
 lda PlayerFacingDir
 cmp #2
 bne Vertical
 jsr NegateX
Vertical:
 lda Player_State
 beq Move
 lda MmUnderwater
 beq Dry
 ; Source water750/7200:26+2/3 Q8.8. Separate phase on water entry
 ; is a bounded fixed-point adaptation; native springs still import above.
 lda FfGPhase
 clc
 adc #2
 cmp #3
 bcc WaterPhase
 sbc #3
 ldx #27
 bne Gravity
WaterPhase:ldx #26
 bne Gravity
Dry:
 lda FfGPhase
 clc
 adc #28
 cmp #36
 bcc DryPhase
 sbc #36
 ldx #50
 bne Gravity
DryPhase:ldx #49
Gravity:
 sta FfGPhase
 txa
 clc
 adc MmVY+1
 sta MmVY+1
 lda MmVY+2
 adc #0
 sta MmVY+2
 lda MmUnderwater
 beq Move
 lda MmVY+2
 bmi Move
 cmp #2
 bcc Move
 bne Cap
 lda MmVY+1
 cmp #$16                      ; inherited250/120=2+1/12.
 bcc Move
Cap:lda #$15
 sta MmVY+1
 lda #2
 sta MmVY+2
Move:jsr Integrate
 lda Player_State
 ora FfAction
 ora RgCrouch
 bne NoWalk
 lda Player_X_Speed
 beq NoWalk
 lda FfWalk
 beq StartWalk
 inc FfWalkDelay
 lda FfWalkDelay
 cmp #6                        ; inherited ANIM_SLOW_TMR100ms.
 bcc Moved
 lda #0
 sta FfWalkDelay
 inc FfWalk
 lda FfWalk
 cmp #6
 bcc Moved
StartWalk:lda #2
 sta FfWalk
 bne Moved
NoWalk:lda #0
 sta FfWalk
 sta FfWalkDelay
Moved:
 sec
 rts
NegateX:
 sec
 lda #0
 sbc MmVX+1
 sta MmVX+1
 lda #0
 sbc MmVX+2
 sta MmVX+2
 rts
Integrate:
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
 sbc MmOldX
 sta Player_X_Scroll
 lda MmVX+1
 lsr
 lsr
 lsr
 lsr
 sta FfTemp
 lda MmVX+2
 asl
 asl
 asl
 asl
 ora FfTemp
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
 bcs Report
 lda #1                        ; SMB screen-top clamp is a host adaptation.
 sta Player_Y_HighPos
 lda #0
 sta Player_Y_Position
 sta MmVY+1
 sta MmVY+2
 sta MmYFraction+1
Report:lda MmVY+2
 sta Player_Y_Speed
Done:rts
.endproc
.proc FfWaterMode
 lda SwimmingFlag
 beq Dry
 lda Player_Y_HighPos
 cmp #1
 bcc Dry
 bne Wet
 ; Character inherited aboveWater cutoff hTop<=64Flash=32NES.
 ldx #6
 lda Player_State
 ora FfAction
 bne Position
 lda SavedJoypadBits
 and #Down_Dir
 beq Position
 ldx #17
Position:txa
 clc
 adc Player_Y_Position
 bcs Wet
 cmp #33
 bcc Dry
Wet:lda #1
 rts
Dry:lda #0
 rts
.endproc
.proc FfPickup
 ; Actual normalized Mushroom0/Flower1 only. Actor erase/score owned by caller.
 cmp #2
 bcs No
 pha
 lda SelectedCharacter
 cmp #CHARACTER_FINAL_FANTASY
 bne Foreign
 jsr FfEnsure
 pla
 tax
 lda FfPower
 cmp #2
 bcs Charges
 inc FfPower                    ; explicit crossover tier progression.
Charges:
 lda FfPower
 cmp FfEarned
 bcc :+
 sta FfEarned
:lda FfVariant
 cmp #1
 bne Finish
 lda FfHealCharges
 clc
 adc #1
 cpx #0
 beq :+
 clc
 adc #1                        ; Flower earns two, Mushroom one, max3.
:cmp #4
 bcc :+
 lda #3
:sta FfHealCharges
Finish:
 lda FfPower
 sta PlayerStatus
 lda #Sfx_PowerUpGrab
 sta Square2SoundQueue
 sec
 rts
Foreign:pla
No:clc
 rts
.endproc
.proc FfFullPower
 jsr FfEnsure
 lda #2
 sta FfPower
 sta FfEarned
 sta PlayerStatus
 lda #3                        ; explicit enabled cheat API, not earned test.
 sta FfHealCharges
 rts
.endproc
.proc FfInjuryStatus
 lda FfHurt
 bne Protected
 lda FfPower
 rts
Protected:lda #1
 rts
.endproc
.proc FfInjuryStart
 lda FfHurt
 bne Protected
 lda FfPower
 beq Dead
 dec FfPower
 lda FfPower
 sta PlayerStatus
 lda #90
 sta FfHurt
 lda #12
 sta FfHurtMove
 lda #1
 sta InjuryTimer
 sta Player_State
 lda #0
 sta FfAction
 sta MmVX
 sta MmVY
 sta MmVY+1
 lda #$fe
 sta MmVY+2
 sta Player_Y_Speed
 lda #$80
 sta MmVX+1
 lda #1
 sta MmVX+2
 lda PlayerFacingDir
 cmp #1
 bne Sound
 jsr FfMovement::NegateX
Sound:lda #Sfx_PipeDown_Injury
 sta Square1SoundQueue
Protected:sec
 rts
Dead:jmp KillPlayer
.endproc
.proc FfDeathStart
 lda #0
 sta FfPower
 sta FfEarned
 sta FfHealCharges
 sta FfAction
 sta FfHurt
 sta FfHurtMove
 ldx #35
Clear:sta FfProjectile,x
 dex
 bpl Clear
 rts
.endproc
.proc FfDeathUpdate
 inc MmDeathAge
 lda MmDeathAge
 cmp #120
 bcc Done
 lda #6
 sta GameEngineSubroutine
 lda #0
 sta TimerControl
Done:rts
.endproc
.proc FfStompPolicy
 lda MmUnderwater
 bne No
 lda CrossoverBehaviorVersion
 beq Yes
No:
 clc
 rts
Yes:sec
 rts
.endproc
.proc FfBox
 ldy #12                       ; native16x24/32 collision adapter, disclosed.
 rts
.endproc
.proc FfCollisionBounds
 ; Exact original authored HRect relative to native top-left/32px foot.
 ; Shared adapter must consume these bounds, not silently use fallback box12.
 lda #1
 sta R0
 lda #6
 ldx RgCrouch
 beq :+
 lda #17
:sta R1
 lda #15
 sta R2
 lda #32
 sta R3
 rts
.endproc
.proc FfAdder
 ldy #3
 sec
 rts
.endproc
.proc FfHead
 jmp BlockBufferColli_Head
.endproc
.proc FfSide
 jmp BlockBufferColli_Side
.endproc
.popseg
