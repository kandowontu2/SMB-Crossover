PrincePipeControls:
 php
 txa
 pha
 tya
 pha
 lda #3
 sta $c02c
 lda SavedJoypad1Bits
 sta $c40a
 and #$0f
 cmp #8
 beq Facing
 cmp #9
 beq Right
 cmp #10
 beq Left
 jmp Clear
Left:
 lda $c615
 jne Clear
 lda #$ee                 ; Look eighteen pixels back after a wall recoil.
 ldx #$ff
 bne Approach
Facing:
 lda $c615
 bpl Left
Right:
 lda $c615
 jpl Clear
 lda #31
 ldx #0
Approach:
 pha
 lda $c618
 cmp #2
 jeq Hanging
 cmp #6
 jeq Hanging
 ldy ClimbTime
 jne Pending
 pla
 clc
 adc Player_X_Position
 sta ProbeX
 pha
 txa
 adc Player_PageLoc
 and #1
 tax
 pla
 lsr
 lsr
 lsr
 lsr
 clc
 adc BlockBufferAddr,x
 sta ReadPipeOperand
 lda Player_Y_Position
 sec
 sbc #32
 cmp #$d0
 bcs Controls
 and #$f0
 tay
ReadPipe:
 lda $03ff,y
 sec
 sbc #$10
 cmp #6
 bcs Controls
 tay
 ldx $c615
 bmi NearRight
 tya
 and #1
 beq StartClimb
 lda ProbeX
 and #15
 cmp #10
 bcc StartClimb
 lda #2
 bne WalkToLip
NearRight:
 tya
 and #1
 bne StartClimb
 lda ProbeX
 and #15
 cmp #4
 bcs StartClimb
 lda #1
WalkToLip:
 sta $c40a
 jmp Controls
StartClimb:
 lda $c618
 cmp #2
 bcs Controls
 lda #32
 sta ClimbTime
 lda Player_Y_Position
 sta ClimbStartY
 jmp Climb
Pending:
 cmp #2
 bcs Held
 lda ClimbStartY
 sec
 sbc Player_Y_Position
 bcc Held
 cmp #24
 bcs DropAndClear
Held:
 dec ClimbTime
Hanging:
 pla
Climb:
 lda #8
 sta $c40a
 bne Controls
DropAndClear:
 pla
Clear:
 lda #0
 sta ClimbTime
Controls:
 pla
 tay
 pla
 tax
 plp
 lda #$92
 sta $016c
 lda #$ab
 sta $016d
 lda $c40a
 sta $016a
 lda #3
 jsr $015a
 jmp $c383
ClimbTime:
