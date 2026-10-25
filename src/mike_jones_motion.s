; Source measured grid step16/14 and jump38 updates,17px apex.
; Geometry conversion: jumpdelta4x, horizontalcarry2x while airborne.
.pushseg
.segment "MIKE_CORE"
.proc JnMovement
 jsr JnEnsure
 jsr JnInputs
 jsr JnEffectiveTier
 inc JnClock
 lda JnHurt
 beq :+
 dec JnHurt
:lda JnStars
 asl
 lda #0
 rol
 sta PlayerStatus
 lda #0
 sta PlayerSize
 sta MmSliding
 sta SmBall
 sta RgCrouch
 sta CrouchingFlag
 sta MmOnVine
 sta MmUnderwater
 sta MmFrictionYActive
 lda Player_X_Position
 sta JnOldX
 sta MmOldX
 lda Player_State
 cmp #3
 jne Ordinary
 farcall MegaManClimbing,jmp
Ordinary:
 lda Player_State
 jne Air
 lda #0
 sta JnJump
 sta JnFallFrac
 sta JnVY
 sta Player_Y_Speed
 lda JnPressed
 and #A_Button
 jeq Air
 lda #1
 sta JnJump
 sta Player_State
 lda #Sfx_BigJump
 sta Square1SoundQueue
Air:
 lda SwimmingFlag
 jeq Horizontal
 ; Original top-down water isn't a platform swim. Explicit SMB stroke.
 lda #1
 sta Player_State
 lda #0
 sta JnJump
 lda JnPressed
 and #A_Button
 jeq Horizontal
 lda #$fd
 sta JnVY
Horizontal:
 lda #0
 sta Player_X_Speed
 sta Player_XSpeedAbsolute
 lda SavedJoypadBits
 and #3
 jeq Vertical
 ldx Player_State
 jne MoveInput
 ldx JnAttack
 jne Vertical ; native grounded attack locks grid movement.
MoveInput:
 cmp #2
 jeq Left
 lda #1
 sta PlayerFacingDir
 jne Step
Left:lda #2
 sta PlayerFacingDir
Step:
 inc JnStep
 lda JnStep
 cmp #7
 bcc :+
 lda #0
 sta JnStep
:tax
 lda GroundStep,x
 ldy Player_State
 jeq Signed
 lda AirStep,x
Signed:
 sta JnTemp
 lda #0
 sta JnTemp2
 lda PlayerFacingDir
 cmp #2
 jne Move
 lda #0
 sec
 sbc JnTemp
 sta JnTemp
 lda #$ff
 sta JnTemp2
Move:
 clc
 lda Player_X_Position
 adc JnTemp
 sta Player_X_Position
 lda Player_PageLoc
 adc JnTemp2
 sta Player_PageLoc
 lda #$12
 ldx Player_State
 jeq Speed
 lda #$24
Speed:sta Player_XSpeedAbsolute
 ldx PlayerFacingDir
 cpx #2
 jne ExportX
 eor #$ff
 clc
 adc #1
ExportX:sta Player_X_Speed
Vertical:
 lda Player_State
 jeq Export
 lda JnJump
 jeq Fall
 lda Player_Y_Speed
 jne Jump
 lda JnVY
 jpl Jump
 lda #0
 sta JnJump
 sta JnVY
 jeq Fall
Jump:
 lda JnJump
 sec
 sbc #1
 tax
 lda JumpDelta,x
 sta JnVY
 inc JnJump
 lda JnJump
 cmp #39
 jcc Integrate
 lda #0
 sta JnJump
 jmp Integrate
Fall:
 lda JnFallFrac
 clc
 adc #$40
 sta JnFallFrac
 lda JnVY
 adc #0
 cmp #5
 bmi :+
 lda #5
:sta JnVY
Integrate:
 lda JnVY
 sta Player_Y_Speed
 sta MmVY+2
 clc
 adc Player_Y_Position
 sta Player_Y_Position
 lda #0
 ldx JnVY
 bpl :+
 lda #$ff
:adc Player_Y_HighPos
 sta Player_Y_HighPos
 cmp #1
 jcc Top
 jne State
 lda Player_Y_Position
 cmp #16
 jcs State
Top:lda #16
 sta Player_Y_Position
 lda #1
 sta Player_Y_HighPos
 lda #0
 sta JnJump
 sta JnVY
State:lda JnVY
 jmi Rising
 lda #2
 jne SetState
Rising:lda #1
SetState:sta Player_State
Export:
 lda Player_X_Position
 sec
 sbc JnOldX
 sta Player_X_Scroll
 lda #0
 sta MmVX
 sta MmVX+1
 sta MmVX+2
 sta MmVY
 sta MmVY+1
 sta MmXFraction
 sta MmXFraction+1
 sta MmYFraction
 sta MmYFraction+1
 rts
GroundStep:.byte 1,1,1,2,1,1,1
AirStep:.byte 2,2,2,3,2,2,3
JumpDelta:.byte 248,248,248,248,252,252,252,252,252,252,252,0,252,0,252,0,0,0,0,0,0,0,4,0,4,0,4,4,4,4,4,4,4,4,4,8,8,8
.endproc
.popseg
