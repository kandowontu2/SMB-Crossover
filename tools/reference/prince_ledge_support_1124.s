; Preserve the source's running-to-falling decisions when neither foot
; is over the exposed native ledge.
PrincePipeCapSupport:
 php
 txa
 pha
 tya
 pha
 jsr RunningSupport
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

RunningSupport:
 lda $c616
 cmp #1
 bne RejectRunning
 lda $c618
 cmp #1
 bne RejectRunning
 lda Player_Y_HighPos
 cmp #1
 bne RejectRunning
 lda $c085
 bne RejectRunning
 jsr LoadSurface
 bcc RejectRunning
 jmp BothFeet
RejectRunning:
 clc
 rts

; Called only after the native grounded check on a missed donor sample.
; The caller retains the original careful-step fallback.
LedgeSupport:
 jsr LoadSurface
 bcc NoSupport
 lda $c086
 sec
 sbc LedgeSurface
 cmp #4
 bcs NoSupport
 txa
 pha
 tya
 pha
 jsr BothFeet
 pla
 tay
 pla
 tax
 bcc NoSupport
 lda #0
 sta $c080
 lda LedgeSurface
 rts
NoSupport:
 lda #0
 rts

LoadSurface:
 lda Player_Y_Position
 cmp #$d0
 bcs RejectSurface
 and #15
 cmp #4
 bcs RejectSurface
 lda Player_Y_Position
 and #$f0
 sta LedgeRow
 clc
 adc #32
 sta LedgeSurface
 lda $c084
 sec
 sbc LedgeSurface
 cmp #4
 bcs RejectSurface
 sec
 rts
RejectSurface:
 clc
 rts

BothFeet:
 lda #2
 jsr LedgeFoot
 bcs Done
 lda #13
 jmp LedgeFoot
Done:
 rts

LedgeFoot:
 clc
 adc Player_X_Position
 sta CapColumn
 lda Player_PageLoc
 adc #0
 sta CapPage
 jsr ColumnAddress
 ldy LedgeRow
 jsr ReadTile
 cmp #$10
 bcc Reject
 cmp #$14
 bcc CheckAbove
 cmp #$51
 beq CheckAbove
 cmp #$57
 beq CheckAbove
 cmp #$58
 beq CheckAbove
 cmp #$c0
 beq CheckAbove
 cmp #$c1
 beq CheckAbove
 cmp #$c4
 bne Reject
CheckAbove:
 tya
 sec
 sbc #16
 bcc Reject
 tay
 jsr ReadTile
 tax
 lda MTileAttribute,x
 lsr
 bcs Reject
 sec
 rts
Reject:
 clc
 rts
LedgeWork:
