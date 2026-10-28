; MG Bank05 core: selected normal/no-shell/no-slope/no-RPG-ability path.
; Arithmetic and fractional integration retain the original sequence.
.pushseg
.segment "CELESTE_MARIO_CORE"
.proc CmWallJump
 lda #1
 sta CmFootPhysics
 lda Up_Down_Buttons
 and #Up_Dir
 beq Ordinary
 lda CmStaminaHi
 ora CmStaminaLo
 beq Ordinary
 dec CmStaminaHi
 bpl :+
 lda #0
 sta CmStaminaHi
 sta CmStaminaLo
:ldy CmWallSide
 cpy Left_Right_Buttons
 bne LowTimer
 lda Fast-1,y
 sta Player_X_Speed
 lda #1
 sta CmWallKick
 rts
LowTimer:
 lda #3
 bne Set
Ordinary:
 lda #20
Set:sta CmWallKick
 ldy CmWallSide
 lda Ultra-1,y
 sta Player_X_Speed
 rts
Fast:.byte $e0,$20
Ultra:.byte $d0,$30
.endproc
.proc CmJump
 lda #0
 sta CmJumpBuffer
 lda CmJumpInterval
 jne Done
 lda #5
 sta CmJumpInterval
 lda #32
 sta CmJumpTime
 lda #$60
 sta CmFallForce
 lda #$29
 sta CmGravity
 lda #$10
 sta CmVelYFrac
 lda #$fc                     ; source PlayerYSpdData[initial jump level0]
 ldx SwimmingFlag
 beq DashAdder
 lda #$0e
 sta CmFallForce
 sta CmGravity
 lda #$d0
 sta CmVelYFrac
 lda #$fd
DashAdder:
 ldx CmDashTimer
 beq Speed
 ldx CmWallKick
 beq Speed
 ldx Player_Y_Speed
 bpl Speed
 lda #$fa                     ; actual native upward-dash wall-bounce adderFE
Speed:
 cmp Player_Y_Speed
 bpl :+
 sta Player_Y_Speed
:lda CmBoost
 beq State
 eor #$ff
 sec
 ror
 tay
 adc CmFallForce
 sta CmFallForce
 tya
 lsr
 lsr
 ora #$c0
 adc CmGravity
 sta CmGravity
 lda CmVelYFrac
 sec
 sbc CmBoost
 sta CmVelYFrac
 lda #$ff
 adc Player_Y_Speed
 sta Player_Y_Speed
State:
 lda #1
 sta CmState
 sta CmStartedJump
 lda #0
 sta CmPosYFrac
 sta CmCoyote
 sta CmWallGrace
 lda SwimmingFlag
 beq Sound
 lda Player_Y_Position
 cmp #$14
 lda Player_Y_HighPos
 sbc #1
 bcs SwimSound
 lda #0
 sta Player_Y_Speed
SwimSound:
 lda #Sfx_EnemyStomp
 bne QueueSound
Sound:
 lda #Sfx_BigJump
QueueSound:
 sta Square1SoundQueue
Done:rts
.endproc
.proc CmAnimStop
 ; Native GetPlayerAnimSpeed considers every physical input except A.
 lda SavedJoypadBits
 and #$7f
 beq Done
 and #3
 cmp Player_MovingDir
 beq Done
 lda Player_XSpeedAbsolute
 cmp #11
 bcs Done
 lda PlayerFacingDir
 sta Player_MovingDir
 lda #0
 sta Player_X_Speed
 sta CmKernelXFrac
Done:
 ldy #0
 lda Player_XSpeedAbsolute
 cmp #$1c
 bcs Timing
 iny
 cmp #$0e
 bcs Timing
 iny
Timing:
 lda AnimTimes,y
 sta PlayerAnimTimerSet
 lda CmBoost
 cmp #12
 bcc Return
 lda #1
 sta PlayerAnimTimerSet
Return:rts
AnimTimes:.byte 2,4,7
.endproc
.proc CmGround
 jsr CmAnimStop
Facing:
 lda Left_Right_Buttons
 beq Move
 sta PlayerFacingDir
Move:
 jsr CmFriction
 jmp CmMoveX
.endproc
.proc CmAir
 lda Left_Right_Buttons
 beq :+
 sta PlayerFacingDir
:lda CmState
 cmp #2
 beq Falling
 lda CmJumpTime
 beq Dump
 ldy Player_Y_Speed
 bpl Dump
 lda A_B_Buttons
 bmi Horizontal
Dump:
 lda CmFallForce
 ldy CmWallGrace
 beq NoWall
 ldy Player_Y_Speed
 bpl Float
 bmi SetForce
NoWall:
 ldy Player_Y_Speed
 bne FallingFast
Float:
 lda #$30
 cmp CmFallForce
 bcc Store
 lda CmFallForce
 bne Store
FallingFast:
 cpy #$fe
 bpl Store
 lda #$c0
Store:
 sta CmGravity
 lda CmWallKick
 cmp #8
 bcc Horizontal
 lda #7
 sta CmWallKick
 bne Horizontal
SetForce:
 sta CmGravity
 jmp Horizontal
Falling:
 lda Player_Y_Speed
 bmi :+
 lda SwimmingFlag
 bne :+
 lda #$50
 sta CmFallForce
:lda CmFallForce
 sta CmGravity
Horizontal:
 lda SwimmingFlag
 beq :+
 lda CmState
 cmp #2
 beq :+
 jsr CmAnimStop
 lda Player_Y_HighPos
 cmp #1
 bmi Surface
 bne :+
 lda Player_Y_Position
 cmp #$14
 bcs :+
Surface:
 lda #$18
 sta CmGravity
: 
 lda Left_Right_Buttons
 jsr CmFriction
 jsr CmMoveX
 jmp CmMoveY
.endproc
.proc CmXPhysics
 lda #0
 sta CmFrictionLo
 lda #1
 sta CmFrictionHi
 ldy #0
 lda SwimmingFlag
 beq Dry
 iny
 lda CmState
 bne SetMax
 iny
 jmp SetMax
Dry:
 lda CmState
 bne SetMax
 lda CrouchingFlag
 beq NotCrouched
 iny
 lda Player_XSpeedAbsolute
 cmp #$18
 bcs SetMax
 iny
 jmp SetMax
NotCrouched:
 lda Left_Right_Buttons
 cmp Player_MovingDir
 beq SetMax
 iny
SetMax:
 lda Right,y
 sta CmMaxRight
 lda Left,y
 sta CmMaxLeft
 lda CmFootPhysics
 beq Normal
 lda #$60
 sta CmFrictionLo
 lda #0
 sta CmFrictionHi
 rts
Normal:
 lda Left_Right_Buttons
 beq Slow
 cmp Player_MovingDir
 bne Reverse
 lda Player_XSpeedAbsolute
 cmp #$18
 bcc Fast
 lda CmBoost
 beq Done
 clc
 adc #30
 cmp Player_XSpeedAbsolute
 bcs Double
 rts
Fast:
 lda #8
 ldy CmState
 beq Store
 lda #4
 bne Store
Slow:
 lda Player_XSpeedAbsolute
 cmp #2
 bcc Done
 cmp #$21
 bcc :+
 lsr
 lsr
:lsr
 cmp #2
 bcc Double
 cmp #8
 bcc Store
 lda #8
 bne Store
Reverse:
 lda Player_XSpeedAbsolute
 cmp #2
 bcc Done
 cmp #$21
 bcc :+
 lsr
 lsr
:lsr
 cmp #2
 bcc Double
 cmp #12
 bcc Store
 lda #12
Store:
 sta CmFrictionHi
 rts
Double:
 asl CmFrictionLo
 rol CmFrictionHi
Done:rts
Right:.byte $20,$18,$10
Left:.byte $e0,$e8,$f0
.endproc
.proc CmFriction
 ; Native A/flags argument is LR bits. Fractional accel is distinct from X
 ; position fraction. Preserve soft cap and overflow behavior, not a clamp.
 bne Joy
 lda Player_X_Speed
 jeq Abs
 bpl Subtract
 bmi Add
Joy:
 lsr
 bcc Subtract
Add:
 lda CmKernelXFrac
 clc
 adc CmFrictionLo
 sta CmKernelXFrac
 lda Player_X_Speed
 adc CmFrictionHi
 sta Player_X_Speed
 jmp Cap
Subtract:
 lda CmKernelXFrac
 sec
 sbc CmFrictionLo
 sta CmKernelXFrac
 lda Player_X_Speed
 sbc CmFrictionHi
 sta Player_X_Speed
Cap:
 lda Player_X_Speed
 bmi CapLeft
 lda CmMaxRight
 sec
 adc CmBoost
 bpl :+
 lda #$7f
:sbc Player_X_Speed
 bpl Sign
 cmp #$ff
 bcs One
 lda #$40
 clc
 adc CmKernelXFrac
 sta CmKernelXFrac
 lda #$fe
 bne ApplyRight
One:clc
ApplyRight:
 adc Player_X_Speed
 ldy CmState
 bne :+
 cmp #72
 bcc :+
 lda #72
: 
 sta Player_X_Speed
 jmp Abs
CapLeft:
 lda CmMaxLeft
 sec
 sbc CmBoost
 bmi :+
 lda #$81
:sbc Player_X_Speed
 bmi Sign
 cmp #2
 bcc ApplyLeft
 lda #$c0
 clc
 adc CmKernelXFrac
 sta CmKernelXFrac
 lda #1
ApplyLeft:
 adc Player_X_Speed
 ldy CmState
 bne :+
 cmp #$b8
 bcs :+
 lda #$b8
: 
 sta Player_X_Speed
Sign:
 lda Player_X_Speed
 bpl Abs
 eor #$ff
 clc
 adc #1
Abs:
 sta Player_XSpeedAbsolute
 ; Genuine CM's ordinary P-meter (unowned SpeedBooster): threshold88,
 ; max116, ordinary extra16/16. Dash temporarily also uses this adder.
 cmp #9
 bcc Clear
 ldy #$fc
 cmp #$18
 bcc DecMeter
 ldy #$fe
 cmp #$20
 bcc DecMeter
 lda Left_Right_Buttons
 and Player_CollisionBits
 and PlayerFacingDir
 beq DecMeter
 lda CmRunMeter
 cmp #116
 bcs Done
 lda CmState
 bne Recalc
 inc CmRunMeter
Recalc:
 lda CmRunMeter
 cmp #88
 bcs Boost
 lda #0
 sta CmBoost
 rts
Boost:
 cmp #117
 bcc :+
 lda #116
 sta CmRunMeter
:lda #16
 sta CmBoost
Done:rts
DecMeter:
 tya
 clc
 adc CmRunMeter
 bcs Meter
Clear:lda #0
Meter:sta CmRunMeter
 jmp Recalc
.endproc
.proc CmMoveX
 lda Player_X_Speed
 asl
 asl
 asl
 asl
 sta CmTemp
 lda Player_X_Speed
 lsr
 lsr
 lsr
 lsr
 ldy #0
 cmp #8
 bcc :+
 dey
 ora #$f0
:sta CmTemp2
 lda CmPosXFrac
 clc
 adc CmTemp
 sta CmPosXFrac
 php
 lda CmTemp2
 adc Player_X_Position
 sta Player_X_Position
 tya
 adc Player_PageLoc
 sta Player_PageLoc
 plp
 lda CmTemp2
 adc #0
 sta Player_X_Scroll
 rts
.endproc
.proc CmMoveY
 lda CmPosYFrac
 clc
 adc CmVelYFrac
 sta CmPosYFrac
 ldy #0
 lda Player_Y_Speed
 bpl :+
 dey
:adc Player_Y_Position
 sta Player_Y_Position
 tya
 adc Player_Y_HighPos
 sta Player_Y_HighPos
 lda CmVelYFrac
 clc
 adc CmGravity
 sta CmVelYFrac
 lda Player_Y_Speed
 adc #0
 cmp #4
 bmi :+
 lda #0
 sta CmVelYFrac
 lda #4
:sta Player_Y_Speed
 rts
.endproc
.proc CmDash
 lda #$48
 sta CmFallForce
 lda CmDashTimer
 bne Active
 lda #1
 sta CmState
 lsr
 sta CmBoost
 lda Player_Y_Speed
 cmp #$80
 ror
 cmp #1
 bmi :+
 lda #1
 sta CmVelYFrac
:sta Player_Y_Speed
 lda Left_Right_Buttons
 beq Quarter
 lsr
 ror
 eor Player_X_Speed
 bmi Half
Quarter:
 lda Player_X_Speed
 cmp #$80
 ror
 bne NextRor
Half:
 lda Player_X_Speed
NextRor:
 cmp #$80
 ror
 sta Player_X_Speed
 rts
Active:
 lda CmDashReady
 beq Smooth
 lda SavedJoypadBits
 and #$0f
 bne Direction
 lda PlayerFacingDir
 sec
 sbc #1
 beq SetDir
 lda #4
 bne SetDir
Direction:
 tay
 lda Directions,y
SetDir:
 sta CmDashDir
 tay
 lda XSpeed,y
 sta Player_X_Speed
 jmp YSpeed
Smooth:
 ldx Player_X_Speed
 ldy CmDashDir
 lda XSpeed,y
 sec
 sbc Player_X_Speed
 beq YSpeed
 bpl Positive
 cmp #$f0
 bcs Add
 lda #$f0
 cpx #$fe
 bcc Add
 lda #$fa
 bne Add
Positive:
 cmp #16
 bcc Add
 lda #16
 cpx #3
 bcs Add
 lda #4
Add:
 clc
 adc Player_X_Speed
 sta Player_X_Speed
YSpeed:
 lda YSpeedTable,y
 bne ChangeY
 sta Player_Y_Speed
 beq Facing
ChangeY:
 cmp Player_Y_Speed
 beq Facing
 bmi Up
 inc Player_Y_Speed
 jmp Facing
Up:dec Player_Y_Speed
Facing:
 lda Player_X_Speed
 beq Abs
 ldy #1
 cmp #0
 bpl :+
 iny
:sty PlayerFacingDir
Abs:
 jsr CmFriction::Sign
 lda CmDashReady
 bne Done
 lda #0
 sta CmVelYFrac
 jsr CmMoveX
 cmp #$80
 ror
 sta Player_X_Scroll          ; native non-shinespark dash smooth-scroll adder
 ; Native Dash_HighDownSpd uses zero gravity and cap5 while dashing.
 lda CmPosYFrac
 clc
 adc CmVelYFrac
 sta CmPosYFrac
 ldy #0
 lda Player_Y_Speed
 bpl :+
 dey
:adc Player_Y_Position
 sta Player_Y_Position
 tya
 adc Player_Y_HighPos
 sta Player_Y_HighPos
 lda Player_Y_Speed
 cmp #5
 bmi Done
 lda #5
 sta Player_Y_Speed
Done:rts
Directions:.byte 0,0,4,0,6,7,5,6,2,1,3,2,0,0,4,0
XSpeed:.byte $60,$44,0,$bc,$a0,$bc,0,$44
YSpeedTable:.byte 0,$fc,$fa,$fc,0,4,6,4
.endproc
.popseg
