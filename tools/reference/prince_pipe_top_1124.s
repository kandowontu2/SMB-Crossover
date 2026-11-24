; Called from the donor's run-to-fall transition. Use the host pipe
; surface, which can be one to three pixels above the projected sole.
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
 cmp #1
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
 cmp #4
 bcs NoSupport
 lda Player_Y_Position
 and #$f0
 sta NativeRow
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
 bcs SupportFound
 lda #13
PipeFoot:
 clc
 adc Player_X_Position
 sta CapColumn
 lda Player_PageLoc
 adc #0
 sta CapPage
 jsr ColumnAddress
 ldy NativeRow
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
SupportFound:
 sec
 rts
NoSupport:
 clc
 rts
