.pushseg
.segment "ICE_CLIMBERS_CORE"
; Loader-owned identity; AreaPointer may describe a future pipe destination.
.proc IcSceneKey
 lda AreaType
 .repeat 5
  asl
 .endrepeat
 ora AreaAddrsLOffset
 rts
.endproc

.proc IcGlobalInit
 lda #0
 sta IcVariant
 ldx #$17
Clear:sta IcReady,x
 dex
 bpl Clear
 rts
.endproc
.proc IcEnsure
 lda IcReady
 cmp #$49
 bne NewLife
 lda NumberofLives
 sec
 sbc IcLife
 bmi NewLife                    ; Modulo loss; actual INC gains/wrap preserve gear.
 lda NumberofLives
 sta IcLife
 jsr IcSceneKey
 cmp IcArea
 bne Area
 lda WorldNumber
 cmp IcWorld
 beq Done
 bne Area
NewLife:
 lda #0
 sta IcPower
 lda #$49
 sta IcReady
Area:jsr IcAreaReset
Done:rts
.endproc
.proc IcAreaReset
 lda SelectedCharacter
 cmp #CHARACTER_ICE_CLIMBERS
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
 lda #$ff
 sta IcPaletteAck
 lda SavedJoypadBits
 sta IcPrevious
 lda NumberofLives
 sta IcLife
 jsr IcSceneKey
 sta IcArea
 lda WorldNumber
 sta IcWorld
Done:rts
.endproc
.proc IcMovement
 jsr IcEnsure
 lda SavedJoypadBits
 eor IcPrevious
 and SavedJoypadBits
 sta IcFresh
 lda SavedJoypadBits
 sta IcPrevious
 inc IcClock
 lda IcPower
 sta PlayerStatus
 lda #0
 sta PlayerSize
 sta CrouchingFlag
 sta RgCrouch
 sta MmSliding
 sta SmBall
 sta MmOnVine
 sta MmUnderwater
 sta MmFrictionYActive
 lda Player_X_Position
 sta MmOldX
 lda Player_State
 sta IcWasGround
 cmp #3
 bne Ordinary
 ; Vine/flagpole remains the host's explicit climbing handoff.
 farcall MegaManClimbing,jmp
Ordinary:
 lda IcHurt
 beq :+
 dec IcHurt
 lda #1
 sta InjuryTimer
:lda IcHurtMove
 beq Controlled
 dec IcHurtMove
 jmp Vertical
Controlled:
 lda Player_State
 bne Air
 lda #0
 sta MmVY
 sta MmVY+1
 sta MmVY+2
 sta MmYFraction
 sta MmYFraction+1
 sta IcJumpAge
 sta IcJumpHits
 sta IcJumpActive
 lda IcAttack
 beq StartAttack
 inc IcAttack
 lda IcAttack
 cmp #20
 bcc Locked
 lda #0
 sta IcAttack
StartAttack:
 lda SavedJoypadBits
 and #B_Button
 beq Jump
 lda #1
 sta IcAttack
 lda #0
 sta IcAttackHits
 lda #Sfx_Fireball
 sta Square1SoundQueue           ; Host cue; no claim of original audio import.
Locked:
 jsr ZeroX
 jmp Move
Jump:
 jsr HorizontalGround           ; Original direction is chosen before A launch.
 lda IcFresh
 and #A_Button
 beq GroundX
 lda #1
 sta Player_State
 sta IcJumpActive
 lda #0
 sta MmVY
 sta IcJumpHits
 sta IcJumpAge
 lda #$d8                       ; Explicit SMB traversal adaptation -$0428.
 sta MmVY+1                     ; Original source -$03a8 cannot clear64px pipe.
 lda #$fb
 sta MmVY+2
 lda #Sfx_BigJump
 sta Square1SoundQueue
 jmp AirX
GroundX:
 jmp Move
Air:
 lda #0
 sta IcAttack
 lda Player_Y_Speed
 cmp MmVY+2
 beq AirX
 ; Native head/feet/spring collision owns its newly resolved vertical speed.
 sta MmVY+2
 lda #0
 sta MmVY
 sta MmVY+1
AirX:
 inc IcJumpAge
 ; Original fall steering can establish a direction only if initially still.
 ; It cannot reverse an established air trajectory.
 lda IcMoveDir
 bne AirDirection
 lda MmVY+2
 bmi NoAirX
 lda SavedJoypadBits
 and #3
 cmp #1
 beq NewAirDirection
 cmp #2
 bne NoAirX
NewAirDirection:
 sta IcMoveDir
 sta PlayerFacingDir
 lda #15
 sta IcRun
AirDirection:
 lda #0
 sta MmVX
 sta MmVX+2
 lda #$8a                       ; SMB gaps: twice native D160's69/256 air speed.
 ldx IcRun
 cpx #12
 bcc :+
 lda #1
 sta MmVX+2
 lda #$20                       ; Twice144/256=1.125, matching ground walking.
:sta MmVX+1
 lda IcMoveDir
 cmp #2
 bne Vertical
 jsr NegateX
 jmp Vertical
NoAirX:jsr ZeroX
Vertical:
 lda SwimmingFlag
 beq DryGravity
 ; Explicit SMB water adaptation: native game has no water stage.
 lda #1
 sta MmUnderwater
 lda IcFresh
 and #A_Button
 beq WaterGravity
 lda #0
 sta MmVY+1
 lda #$fe
 sta MmVY+2
WaterGravity:
 lda #$11
 bne AddGravity
DryGravity:
 lda IcJumpActive
 beq SteadyGravity
 lda IcJumpAge
 cmp #1
 bne SteadyGravity
 lda #$08                       ; Original C846 initialization, first jump phase.
 bne AddGravity
SteadyGravity:
 lda #$22                       ; Original C839; fixed arc/no A-release cutoff.
AddGravity:
 clc
 adc MmVY+1
 sta MmVY+1
 lda MmVY+2
 adc #0
 sta MmVY+2
 bmi Move
 cmp #4                        ; Source fall limit8 minus jump-base3.a8.
 bcc Move
 bne FallCap
 lda MmVY+1
 cmp #$58
 bcc Move
FallCap:lda #$58
 sta MmVY+1
 lda #4
 sta MmVY+2
Move:
 jsr Integrate
 lda Player_X_Speed
 sta IcLastVX
 rts
ZeroX:
 lda #0
 sta MmVX
 sta MmVX+1
 sta MmVX+2
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
HorizontalGround:
 lda SavedJoypadBits
 and #3
 cmp #1
 beq Input
 cmp #2
 bne Stop
Input:
 sta IcTemp
 lda IcCoast
 bne Coast
 lda IcMoveDir
 beq Begin
 cmp IcTemp
 bne Stop
Begin:
 lda IcTemp
 sta IcMoveDir
 sta PlayerFacingDir
 lda IcRun
 cmp #24
 bcs Walk
 inc IcRun
Walk:
 lda #0
 sta MmVX
 lda #$20                       ; Native D143:1px +extra1 every8updates.
 sta MmVX+1
 lda #1
 sta MmVX+2
 jmp Signed
Stop:
 lda IcMoveDir
 beq Stopped
 lda IcCoast
 bne Coast
 lda IcRun
 lsr
 sta IcCoast
 beq Stopped
Coast:
 dec IcCoast
 beq Stopped
 lda #0
 sta MmVX
 sta MmVX+1
 lda #1
 sta MmVX+2
Signed:
 lda IcMoveDir
 cmp #2
 bne XDone
 jmp NegateX
Stopped:
 lda #0
 sta IcMoveDir
 sta IcRun
 sta IcCoast
 jmp ZeroX
XDone:rts
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
 sta IcTemp
 lda MmVX+2
 asl
 asl
 asl
 asl
 ora IcTemp
 sta Player_X_Speed
 bpl :+
 eor #$ff
 clc
 adc #1
:sta Player_XSpeedAbsolute
 lda Player_State
 beq Moved
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
 bcc Top
 bne Report
 lda Player_Y_Position
 cmp #16
 bcs Report
Top:lda #16
 sta Player_Y_Position
 lda #1
 sta Player_Y_HighPos
 lda #0
 sta MmVY+1
 sta MmVY+2
 sta MmYFraction+1
Report:lda MmVY+2
 sta Player_Y_Speed
Moved:rts
.endproc

.proc IcWeapons
 lda SavedJoypadBits
 sta RgPreviousButtons
 lda TimerControl
 jne Done
 lda GameEngineSubroutine
 cmp #8
 jne Done
 ldx #5
Flash:lda MmEnemyFlash,x
 beq Stun
 dec MmEnemyFlash,x
Stun:lda RgEnemyStun,x
 beq NextFlash
 dec RgEnemyStun,x
NextFlash:dex
 bpl Flash
 lda IcAttack
 cmp #9                        ; Actual original D3E7 collision moment.
 beq Side
 lda Player_State
 cmp #1
 jne Done
 lda IcJumpActive
 jeq Done
 ; Source D3DB admits the whole genuine jump, including its falling half.
 ; A walk-off fall is not a jump-hammer attack.
 lda IcJumpHits
 sta IcWeaponHits
 lda Player_X_Position
 clc
 adc #4
 sta MmBulletX
 lda Player_PageLoc
 adc #0
 sta MmBulletPage
 lda PlayerFacingDir
 cmp #2
 beq OverY
 lda MmBulletX
 clc
 adc #8
 sta MmBulletX
 bcc OverY
 inc MmBulletPage
OverY:lda Player_Y_Position
 clc
 adc #4
 sta MmBulletY
 jsr Hit
 lda SmBombHits
 sta IcJumpHits
 rts
Side:
 lda IcAttackHits
 sta IcWeaponHits
 lda Player_X_Position
 ldx PlayerFacingDir
 cpx #2
 beq Left
 clc
 adc #20
 sta MmBulletX
 lda Player_PageLoc
 adc #0
 jmp Page
Left:sec
 sbc #4
 sta MmBulletX
 lda Player_PageLoc
 sbc #0
Page:sta MmBulletPage
 lda Player_Y_Position
 clc
 adc #12
 sta MmBulletY
 jsr Hit
 lda SmBombHits
 cmp IcAttackHits
 beq Keep
 lda #0                        ; Native swing ends on successful enemy strike.
 sta IcAttack
Keep:lda SmBombHits
 sta IcAttackHits
Done:rts
Hit:
 lda IcWeaponHits
 sta SmBombHits
 lda Player_Y_HighPos
 cmp #1
 jne NoHit
 lda #10                       ; Existing guarded100-damage melee consumer.
 sta MmBulletType
 lda #0
 sta MmSlot
 sta SmSlot
 lda MmBulletX
 sec
 sbc ScreenLeft_X_Pos
 sec
 sbc #4
 sta BoundingBox_UL_Corner+28
 clc
 adc #8
 sta BoundingBox_LR_Corner+28
 lda MmBulletY
 sec
 sbc #4
 sta BoundingBox_UL_Corner+29
 clc
 adc #8
 sta BoundingBox_LR_Corner+29
 farcall MegaManWeapons::BeginEnemyLoop
 lda IcPower
 cmp #2
 bne Cleanup
 ; Flower's second guarded hit is a crossover upgrade, never native Ice Climber.
 lda SmBombHits
 cmp IcWeaponHits
 beq Cleanup
 sta IcTemp
 lda IcWeaponHits
 sta SmBombHits
 lda #10
 sta MmBulletType
 lda #0
 sta MmSlot
 sta SmSlot
 farcall MegaManWeapons::BeginEnemyLoop
 lda SmBombHits
 ora IcTemp
 sta SmBombHits
Cleanup:lda #0
 sta MmBulletType
NoHit:rts
.endproc
.proc IcPickup
 ; A=actual normalized native food type. Caller owns actor erase/score.
 cmp #2
 bcs No
 jsr IcEnsure
 lda IcPower
 cmp #2
 bcs Sound
 inc IcPower
Sound:lda IcPower
 sta PlayerStatus
 lda #Sfx_PowerUpGrab
 sta Square2SoundQueue
 sec
 rts
No:clc
 rts
.endproc
.proc IcInjuryStatus
 lda IcHurt
 bne Protected
 lda IcPower
 rts
Protected:lda #1
 rts
.endproc
.proc IcInjuryStart
 lda IcHurt
 bne Protected
 lda IcPower
 beq Dead
 dec IcPower
 lda IcPower
 sta PlayerStatus
 lda #90
 sta IcHurt
 lda #12
 sta IcHurtMove
 lda #1
 sta InjuryTimer
 sta Player_State
 lda #0
 sta IcAttack
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
 jsr IcMovement::NegateX
Sound:lda #Sfx_PipeDown_Injury
 sta Square1SoundQueue
Protected:sec
 rts
Dead:jmp KillPlayer
.endproc
.proc IcFullPower
 jsr IcEnsure
 lda #2
 sta IcPower
 sta PlayerStatus
 rts
.endproc
.proc IcAdder
 ldy #3                        ; Exact16x24 body:head8, feet32, side12/24.
 sec
 rts
.endproc
.proc IcBox
 ldy #12                       ; Native prepared body1,8..15,32.
 rts
.endproc
.proc IcStompPolicy
 lda CrossoverBehaviorVersion   ; Explicit crossover Easy/Hard distinction.
 beq Yes
 clc
 rts
Yes:sec
 rts
.endproc
.proc IcHead
 jsr BlockBufferColli_Head      ; Ordinary native blocks/coins/bumps retained.
 rts
.endproc
.proc IcDeathStart
 lda #0
 sta IcAttack
 sta IcPower
 sta IcHurt
 sta IcHurtMove
 rts
.endproc
.proc IcDeathUpdate
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
.popseg
