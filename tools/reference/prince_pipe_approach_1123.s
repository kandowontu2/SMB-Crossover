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
 cmp #9
 beq Right
 cmp #10
 jne Clear
 lda $c615
 jne Clear
 lda #$f4
 ldx #$ff
 bne Approach
Right:
 lda $c615
 jpl Clear
 lda #27
 ldx #0
Approach:
 pha
 lda $c618
 cmp #2
 beq Hanging
 cmp #6
 beq Hanging
 ldy ClimbTime
 bne Pending
 cmp #2
 bcs Drop
 pla
 clc
 adc Player_X_Position
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
 lda #32
 sta ClimbTime
 lda Player_Y_Position
 sta ClimbStartY
 bne Climb
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
Drop:
 pla
 jmp Controls
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
ClimbStartY:
