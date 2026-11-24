; Called only by the Prince's running-to-falling alignment entry.
PrincePipeCapSupport:
 php
 txa
 pha
 tya
 pha
 jsr StandingOnPipe
 bcs Supported
 pla
 tay
 pla
 tax
 plp
 ; Resume the two original decisions displaced by the bank gateway.
 lda $c616
 cmp #7
 beq EnterFall
 lda $c610
 bne AlignFall
 lda $c60f
 cmp #$28
 bcc EnterFall
AlignFall:
 lda #$ab
 bne Resume
EnterFall:
 lda #$c2
Resume:
 sta $016c
 lda #$a7
 sta $016d
 lda #3
 jmp $015a
Supported:
 pla
 tay
 pla
 tax
 plp
 rts

StandingOnPipe:
 lda $c616
 cmp #1                    ; Ordinary run. Leave jumps and drops to the source.
 bne NoSupport
 lda $c618
 cmp #1
 bne NoSupport
 lda Player_Y_HighPos
 cmp #1
 bne NoSupport
 lda $c085
 bne NoSupport
 lda Player_Y_Position
 cmp #$d0
 bcs NoSupport
 and #15
 bne NoSupport
 ldy Player_Y_Position
 tya
 clc
 adc #32
 sta NativeSurface
 lda $c084
 sec
 sbc NativeSurface
 cmp #4
 bcs NoSupport
 lda #2
 jsr PipeFoot
 bcc NoSupport
 lda #13
PipeFoot:
 clc
 adc Player_X_Position
 sta CapColumn
 lda Player_PageLoc
 adc #0
 sta CapPage
 jsr ColumnAddress
 ldy Player_Y_Position    ; Index in the block buffer, whose first row is Y32.
 jsr ReadTile
 sec
 sbc #$10
 cmp #4
 bcs NoSupport
 tya
 sec
 sbc #16
 bcc NoSupport
 tay
 jsr ReadTile
 tax
 lda MTileAttribute,x
 lsr
 bcs NoSupport
 sec
 rts
NoSupport:
 clc
 rts
