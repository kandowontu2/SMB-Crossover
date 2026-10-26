; Original A889..A9DB bat acceleration/friction and source Grant wall speeds.
; Solid-point mapping is an explicit SMB metatile adapter. No ground mutation,
; enemy replacement, invisible source-only staircase or invented jump boost.
.pushseg
.segment "CV3_CORE"
.proc Cv3Abilities
 lda Player_Y_Position
 clc
 adc #32
 sta Cv3OldFoot
 lda Cv3Variant
 cmp #3
 jeq Bat
 cmp #1
 jeq Grant
 clc
 rts
Bat:jmp Cv3BatUpdate
Grant:jmp Cv3GrantClimb
.endproc
; Signed offset X from native left, Y from native top. C=typed solid cell.
.proc Cv3SolidPoint
 sty Cv3Temp2
 txa
 clc
 adc Player_X_Position
 sta MmProbeX
 txa
 jmi Negative
 lda #0
 jeq Page
Negative:lda #$ff
Page:adc Player_PageLoc
 sta MmProbePage
 lda Player_Y_Position
 clc
 adc Cv3Temp2
 sta MmProbeY
 cmp #$20
 jcc No
 cmp #$f0
 jcs No
 and #$f0
 sec
 sbc #$20
 sta R2
 lda MmProbePage
 and #1
 asl
 asl
 asl
 asl
 sta R0
 lda MmProbeX
 lsr
 lsr
 lsr
 lsr
 ora R0
 jsr GetBlockBufferAddr
 ldy R2
 lda (R6),y
 tay
 lda MTileAttribute,y
 and #MTILE_SOLID|MTILE_CLIMB
 cmp #MTILE_SOLID
 jeq Yes
No:clc
 rts
Yes:sec
 rts
.endproc
.proc Cv3GrantClimb
 lda Cv3ClimbDelay
 jeq Ready
 dec Cv3ClimbDelay
 clc
 rts
Ready:
 lda Cv3Climb
 jne Holding
 lda Player_State
 jeq No
 lda SavedJoypadBits
 and #3
 cmp #1
 jeq Right
 cmp #2
 jne CeilingFind
 ldx #$ff
 lda #2
 jne Probe
Right:ldx #16
 lda #1
Probe:sta Cv3Temp3
 ldy #20
 jsr Cv3SolidPoint
 jcc CeilingFind
 lda Cv3Temp3
 sta Cv3Climb
 sta PlayerFacingDir
 jmp Freeze
CeilingFind:
 lda SavedJoypadBits
 and #Up_Dir
 jeq No
 ldx #8
 ldy #7
 jsr Cv3SolidPoint
 jcc No
 lda #3
 sta Cv3Climb
 jmp Freeze
No:clc
 rts
Holding:
 lda Cv3Fresh
 and #A_Button
 jeq Retain
 lda #8
 sta Cv3ClimbDelay
 lda #0
 sta Cv3Climb
 jsr Cv3StartFall
 lda #0
 sta Cv3JumpPhase
 lda #45 ; source wall leap begins -2, then its Grant table descent.
 sta Cv3JumpIndex
 lda #$fe
 sta Cv3VyHi
 lda #1
 sta Player_State
 clc
 rts
Retain:
 lda Cv3AttackAge
 jne Freeze
 lda Cv3Climb
 cmp #3
 jeq Ceiling
 tax
 and SavedJoypadBits
 jeq Lost
 cpx #2
 jeq LeftPoint
 ldx #16
 jne WallPoint
LeftPoint:ldx #$ff
WallPoint:
 ldy #31
 jsr Cv3GripWall
 jcc Lost
 lda SavedJoypadBits
 and #Up_Dir
 jne Up
 lda SavedJoypadBits
 and #Down_Dir
 jeq Freeze
 lda #1
 sta Cv3VyHi
 jne MoveWall
Up:lda #$ff
 sta Cv3VyHi
MoveWall:
 lda #0
 sta Cv3VxLo
 sta Cv3VxHi
 sta Cv3VyLo
 lda #1
 sta Player_State
 sec
 rts
Ceiling:
 lda SavedJoypadBits
 and #Up_Dir
 jeq Lost
 ldx #8
 ldy #7
 jsr Cv3SolidPoint
 jcc Lost
 jsr Cv3GroundVelocity
 lda #0
 sta Cv3VyLo
 sta Cv3VyHi
 lda #1
 sta Player_State
 sec
 rts
Lost:
 lda #0
 sta Cv3Climb
 jsr Cv3StartFall
 clc
 rts
Freeze:
 lda #0
 sta Cv3VxLo
 sta Cv3VxHi
 sta Cv3VyLo
 sta Cv3VyHi
 lda #1
 sta Player_State
 sec
 rts
.endproc
.proc Cv3BatUpdate
 lda Cv3Bat
 jeq TryEnter
 lda Cv3Fresh
 and #A_Button
 jeq Transform
 lda SavedJoypadBits
 and #Down_Dir
 jeq Transform
 lda Cv3Bat
 cmp #2
 jne Transform
 ; Exact source clearance intent: both shoulders must be empty before
 ; restoring the tall human. Failed expansion leaves a controllable bat.
 ldx #3
 ldy #0
 jsr Cv3SolidPoint
 jcs Transform
 ldx #13
 ldy #0
 jsr Cv3SolidPoint
 jcs Transform
 lda #3
 sta Cv3Bat
 lda #36
 sta Cv3BatTransform
 jmp Still
TryEnter:
 lda Cv3Fresh
 and #A_Button
 jeq No
 lda SavedJoypadBits
 and #Down_Dir
 jeq No
 lda Cv3AttackAge
 ora Cv3HurtAge
 jne No
 ldx #2
 lda Cv3Hearts,x
 jeq No
 .if ::MAPPER_MMC5
 jsr Cv3FxBatEnter
 .res 2,$ea
 .else
 lda #1
 sta Cv3Bat
 .endif
 lda #36
 sta Cv3BatTransform
 jmp Still
No:clc
 rts
Transform:
 lda Cv3Bat
 cmp #2
 jeq Flying
 dec Cv3BatTransform
 jne Still
 lda Cv3Bat
 cmp #1
 jne End
 lda #2
 sta Cv3Bat
 lda #1
 sta Cv3BatDrain
 jne Still
End:lda #0
 sta Cv3Bat
 jsr Cv3StartFall
 clc
 rts
Still:
 lda #0
 sta Cv3VxLo
 sta Cv3VxHi
 sta Cv3VyLo
 sta Cv3VyHi
 lda #1
 sta Player_State
 sec
 rts
Flying:
 dec Cv3BatDrain
 jne Axes
 lda #60
 sta Cv3BatDrain
 ldx #2
 lda Cv3Hearts,x
 jeq Exhaust
 dec Cv3Hearts,x
 jne Axes
Exhaust:
 lda #3
 sta Cv3Bat
 lda #36
 sta Cv3BatTransform
 jmp Still
Axes:
 ldx #0
 lda SavedJoypadBits
 and #3
 jsr Axis
 ldx #2
 lda SavedJoypadBits
 and #Up_Dir|Down_Dir
 lsr
 lsr
 ; Source Up is negative; input right/Down positive and left/Up negative.
 jsr Axis
 lda SavedJoypadBits
 and #3
 beq :+
 sta PlayerFacingDir
: lda #1
 sta Player_State
 sec
 rts
; X0 horizontal/X2 vertical, A1positive/2negative/0friction.
Axis:
::Cv3BatAxis:
 cmp #1
 jeq Positive
 cmp #2
 jeq Negative
 lda Cv3VxHi,x
 jmi DragNegative
 lda Cv3VxLo,x
 sec
 sbc #8
 sta Cv3VxLo,x
 lda Cv3VxHi,x
 sbc #0
 jcc Zero
 sta Cv3VxHi,x
 rts
DragNegative:
 lda Cv3VxLo,x
 clc
 adc #8
 sta Cv3VxLo,x
 lda Cv3VxHi,x
 adc #0
 jcs Zero
 sta Cv3VxHi,x
 rts
Zero:lda #0
 sta Cv3VxLo,x
 sta Cv3VxHi,x
 rts
Positive:
 lda Cv3VxLo,x
 clc
 adc #16
 sta Cv3VxLo,x
 lda Cv3VxHi,x
 adc #0
 sta Cv3VxHi,x
 jmi Done
 cmp #1
 jcc Done
 lda Cap,x
 cmp Cv3VxLo,x
 jcs Done
 sta Cv3VxLo,x
 rts
Negative:
 lda Cv3VxLo,x
 sec
 sbc #16
 sta Cv3VxLo,x
 lda Cv3VxHi,x
 sbc #0
 sta Cv3VxHi,x
 jpl Done
 cmp NegativeCapHi,x
 jcc Limit
 jne Done
 lda Cv3VxLo,x
 cmp NegativeCapLo,x
 jcs Done
Limit:
 lda NegativeCapHi,x
 sta Cv3VxHi,x
 lda NegativeCapLo,x
 sta Cv3VxLo,x
Done:rts
Cap:.byte $40,0,$00
NegativeCapHi:.byte $fe,0,$ff
NegativeCapLo:.byte $c0,0,$00
.endproc
.popseg
