.export CmEnabled,CmInit,CmEnter,CmEnsure,CmMovement,CmAfterBG,CmWeapons,CmPickup
.export CmInjuryStatus,CmInjuryStart,CmCollisionBox,CmBounce
.pushseg
.segment "CELESTE_MARIO_CORE"
CmCoreStart:
.proc CmEnabled
 lda SelectedCharacter
 bne No
 lda MarioVariant
 cmp #4
 beq Yes
No:clc
 rts
Yes:sec
 rts
.endproc
.proc CmInit
 lda #0
 sta CmMarker
 jmp CmEnsure
.endproc
.proc CmEnsure
 lda CmMarker
 cmp #$ce
 bne First
 lda CmLife
 sec
 sbc NumberofLives
 cmp #1
 beq First
 jsr LoadedArea
 cmp CmArea
 bne Clear
 lda WorldNumber
 cmp CmWorld
 bne Clear
 jmp Save
First:
 lda #0
 sta CmTier
 lda #$ce
 sta CmMarker
Clear:
 lda #0
 ldx #$7f
Loop:sta $5c00,x
 dex
 bpl Loop
 sta Player_X_Speed
 sta CmKernelXFrac
 sta CmPosXFrac
 sta CmVelYFrac
 sta CmPosYFrac
 sta PlayerAnimCtrl
 sta PlayerAnimTimer
 sta PlayerAnimTimerSet
 lda #2
 sta CmStaminaHi
 lda #99
 sta CmStaminaLo
 lda #1
 sta CmDashStock
 lda #$50
 sta CmFallForce
 lda #$29
 sta CmGravity
Save:
 lda NumberofLives
 sta CmLife
 jsr LoadedArea
 sta CmArea
 lda WorldNumber
 sta CmWorld
 rts
LoadedArea:
 lda AreaType
 asl
 asl
 asl
 asl
 asl
 ora AreaAddrsLOffset
 rts
.endproc
.proc CmEnter
 jsr CmEnsure
 jmp CmEnsure::Clear            ; activate after another identity used5C overlay
.endproc
.proc CmMovement
 jsr CmEnsure
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda GamePauseStatus
 and #1
 jne Done
 inc CmClock
 jsr CmTimers
 lda SavedJoypadBits
 eor CmPreviousAB
 and SavedJoypadBits
 and #$c0
 sta CmFresh
 lda SavedJoypadBits
 and #$c0
 sta CmPreviousAB
 lda Player_State
 sta CmLastState
 lda CmState
 cmp #6
 beq Input
Sync:
 lda Player_State
 sta CmState
Input:
 lda #0
 sta PlayerSize               ; native CM starts big; upgrades grant mechanics
 sta CmStartedJump
 lda CmState
 bne NoCrouch
 lda Up_Down_Buttons
 and #Down_Dir
 sta CrouchingFlag
NoCrouch:
 lda CmState
 bne NoRefill
 lda #2                       ; source StartingVIT=2, decimal2*100+99 stamina
 sta CmStaminaHi
 lda #99
 sta CmStaminaLo
 lda #1
 sta CmDashStock
NoRefill:
 lda CmFresh
 bpl CheckJump
 lda #6                       ; native six-update buffered A
 sta CmJumpBuffer
CheckJump:
 lda CmJumpBuffer
 beq DashState
 lda CmDashReady
 cmp #3
 bcs DashState
 lda CmState
 beq GroundJump
 cmp #3
 beq GroundJump
 lda CmCoyote
 bne GroundJump
 lda SwimmingFlag
 bne DashState                 ; literal MG airborne-water jump admission
 lda CmTier
 beq DashState
 lda CmWallGrace
 beq DashState
 jsr CmWallJump
GroundJump:
 jsr CmJump
DashState:
 lda CmState
 cmp #6
 beq Dashing
 lda CmDashTimer
 beq Ordinary
 lda CmState
 bne StopDash
 lda #6                       ; native ground contact resumes remaining dash
 sta CmState
 jmp Dashing
StopDash:
 cmp #6
 beq Dashing
 lda #0
 sta CmDashTimer
 sta CmBoost
Ordinary:
 lda CmState
 cmp #3
 bne Normal
 ; Host vines retain their actual collision/input owner, never a second axis.
 farcall MegaManClimbing
 jmp Export
Normal:
 jsr CmXPhysics
 lda CmState
 beq Ground
 jsr CmAir
 jmp Export
Ground:
 lda #5
 sta CmCoyote
 lda SwimmingFlag
 bne :+
 lda #$50
 sta CmFallForce
: 
 jsr CmGround
 jmp Export
Dashing:
 jsr CmDash
Export:
 lda CmState
 cmp #6
 bne :+
 lda #1                       ; host Player_State never sees native dispatch6
:sta Player_State
 lda Player_X_Speed
 beq Done
 tax
 ldy #1
 cpx #0
 bpl :+
 iny
:sty Player_MovingDir
Done:rts
.endproc
.proc CmTimers
 ; Called after the host's genuine master timer decrement. Native CM only
 ; advances these frame timers when master control is zero. First zero skips
 ; jump pre-input decrement, as native Dec_NoPreInput does.
 lda TimerControl
 bne Save
 lda CmOldMaster
 bne Timers
 lda CmDashTimer
 and #3
 bne Timers
 lda CmJumpBuffer
 beq Timers
 dec CmJumpBuffer
Timers:
 lda CmDashReady
 beq DashTick
 dec CmDashReady
 jmp Other
DashTick:
 lda CmDashTimer
 beq Other
 dec CmDashTimer
Other:
 ldx #4
Loop:
 lda CmCoyote,x               ; coyote,wall grace,wall kick,side (skip side)
 cpx #3
 beq Next
 cpx #4                       ; dash timer already owns its decrement
 beq Next
 cmp #0
 beq Next
 dec CmCoyote,x
Next:dex
 bpl Loop
 ldx #2
More:
 lda CmCooldown,x             ; cooldown,jump hold,jump interval
 beq :+
 dec CmCooldown,x
:dex
 bpl More
Save:
 lda TimerControl
 sta CmOldMaster
 rts
.endproc
.proc CmAfterBG
 lda #0
 ldx CmWallKick
 beq :+
 lda #1
:sta CmFootPhysics
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda SmCeilingHit
 beq Land
 lda #0
 sta CmDashTimer
 lda #$40
 sta CmVelYFrac
Land:
 lda Player_State
 bne Wall
 lda CmState
 cmp #6
 bne Ground
 lda CmDashReady
 bne Wall
 lda CmDashDir
 cmp #5
 bcc Wall
Ground:
 lda #0
 sta CmState
 sta CmVelYFrac
Wall:
 lda SwimmingFlag
 bne Done
 lda CmTier
 beq Done
 lda Player_CollisionBits
 and #3
 cmp #3
 beq Done
 eor #3
 and #3
 tay
 beq Done
 cmp #3
 beq Done
 sty CmWallSide
 lda CrouchingFlag
 bne Done
 lda Player_Y_HighPos
 beq Done
 lda Player_Y_Speed
 bmi Admit
 cpy PlayerFacingDir
 bne Done
 cpy Left_Right_Buttons
 bne Done
Admit:
 lda CmState
 beq Done
 cmp #3
 beq Done
 lda #10                      ; genuine StateCanWallClingTable, not old comment
 sta CmWallGrace
 lda Up_Down_Buttons
 and #Up_Dir
 beq Slide
 lda CmStaminaLo
 ora CmStaminaHi
 beq Slide
 lda Player_Y_Speed
 bmi Done
 lda #0
 sta Player_Y_Speed
 sta CmVelYFrac
 dec CmStaminaLo
 bpl Done
 lda #99
 sta CmStaminaLo
 dec CmStaminaHi
 rts
Slide:
 lda Player_Y_Speed
 cmp #2
 bmi Done
 lda #2
 sta Player_Y_Speed
 lda #0
 sta CmVelYFrac
Done:rts
.endproc
.proc CmWeapons
 ; ProcDash is a post-movement/post-BG owner in the actual MG GameCore.
 lda CmFresh
 and #B_Button
 beq Tick
 lda #4
 sta CmBBuffer
 bne Check
Tick:
 lda CmBBuffer
 beq Done
 dec CmBBuffer
Check:
 lda CmTier
 cmp #2
 bcc Done
 lda GameEngineSubroutine
 cmp #8
 bne Done
 lda CmCooldown
 bne Done
 lda Player_Y_HighPos
 beq Done
 lda AreaType
 beq Done
 lda CmState
 cmp #3
 bcs Done
 lda CmDashStock
 beq Done
 dec CmDashStock
 lda CmState
 beq Pos
 lda #$fd
 sta Player_Y_Speed
 sta CmVelYFrac
Pos:
 lda Player_Y_Position
 bne :+
 dec Player_Y_HighPos
:dec Player_Y_Position
 lda #6
 sta CmState
 lda #1
 sta Player_State
 lda #3
 cmp TimerControl
 bcc :+
 sta TimerControl
:lda #4
 sta CmDashReady
 lda #12
 sta CmDashTimer
 sta CmCooldown
 sta CmBoost
 lda #$3e
 sta CmGravity
 lda #Sfx_Fireball             ; crossover cue; no native CM music engine port
 sta Square1SoundQueue
Done:
 lda TimerControl
 sta CmOldMaster
 rts
.endproc
.proc CmPickup
 lda PowerUpType
 cmp #2
 bcs No
 lda CmTier
 cmp #2
 bcs Full
 inc CmTier
Full:
 lda CmTier
 sta PlayerStatus
 lda #0
 sta CmPalette
 ldx ObjectOffset
 jsr EraseEnemyObject
 lda #Sfx_PowerUpGrab
 sta Square2SoundQueue
 lda #$0b
 sta FloateyNum_Control,x
 sec
 rts
No:clc
 rts
.endproc
.proc CmInjuryStatus
 lda CmTier
 beq Done
 lda #1
Done:
 rts
.endproc
.proc CmInjuryStart
 lda CmTier
 beq No
 dec CmTier
 lda CmTier
 sta PlayerStatus
 lda #0
 sta CmDashTimer
 sta CmDashReady
 sta CmPalette
 lda #$90
 sta InjuryTimer
 sec
 rts
No:clc
 rts
.endproc
.proc CmCollisionBox
 ldy #0
 lda CrouchingFlag
 beq :+
 ldy #2
:rts
.endproc
.proc CmBounce
 ; Native MG SBnce, initial JumpPwr0 and default EnemyStompVerticalForce80.
 lda #$fc
 sta Player_Y_Speed
 lda #$60
 sta CmVelYFrac
 lda #$26
 sta CmGravity
 lda #$80
 sta CmFallForce
 lda #$20
 sta CmJumpTime
 lda #1
 sta CmState
 sta Player_State
 rts
.endproc
.popseg
