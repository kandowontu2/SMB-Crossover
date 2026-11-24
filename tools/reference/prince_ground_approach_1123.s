StaticFloor:
 lda AreaType
 cmp #1
 bne Reject
 lda $c085
 ora $c087
 bne Reject
 lda $c618
 cmp #3
 beq Falling
 cmp #4
 bne Reject
Falling:
 lda $c084
 sec
 sbc $c086
 bcc Reject
 beq Reject
 cmp #33
 bcs Reject
 lda $c086
 clc
 adc #15
 bcs Reject
 and #$f0
 cmp #48
 bcc Reject
 tay
 adc #15                    ; The CMP above set carry, so this adds 16.
 bcs Reject
 cmp $c084
 beq DeepCrossing
 bcs Reject
DeepCrossing:
 tya
 pha
 sec
 sbc #32
 tay
 lda $c610
 and #1
 tax
 lda $c60f
 lsr
 lsr
 lsr
 lsr
 clc
 adc BlockBufferAddr,x
 sta FloorOperand
 sta AboveOperand
Floor:
 lda $03ff,y
 cmp #$54
 bne PopReject
 tya
 sec
 sbc #16
 tay
Above:
 lda $03ff,y
 bne PopReject
 pla
 sec
 rts
PopReject:
 pla
Reject:
 clc
 rts

PrinceNativeFloor:
 php
 pha
 txa
 pha
 tya
 pha
 ldy Player_Y_Speed
 bmi OriginalNativeFloor
 jsr StaticFloor
 bcc OriginalNativeFloor
 sec
 sbc #32
 sta Player_Y_Position
 pla
 tay
 pla
 tax
 pla
 plp
 rts
OriginalNativeFloor:
 pla
 tay
 pla
 tax
 pla
 plp
 ldy Player_Y_Speed
 bmi NoChange
 lda $c084
 and #15
 cmp #5
 bcc NoChange
 sbc Player_Y_Speed
 beq NoChange
 bcc NoChange
 sta $016a
 lda #$d7
 sta $016c
 lda #$d4
 sta $016d
 lda #3
 jmp $015a
NoChange:
 rts
