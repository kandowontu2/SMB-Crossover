; Already authenticated raw43. The caller owns the native collision frame.
; Preserve the host probe order and tail to the existing effect consumer.
.setcpu "6502"
.segment "SONIC_SIDE_BATCH"

SonicSideBatch:
 ldy SideAdder
 iny
 iny
 lda #2
 sta R0
SideNext:
 iny
 sty SideAdder
 lda PlayerY
 cmp #$20
 bcc SideLower
 cmp #$e4
 bcs SideEnd
 jsr SceneSide
 beq SideLower
 cmp #$1c
 beq SideLower
 cmp #$6b
 beq SideLower
 tay
 lda MTileAttribute,y
 and #$02
 bne SideLower
 tya
 jmp SideEffect
SideLower:
 ldy SideAdder
 iny
 lda PlayerY
 cmp #$08
 bcc SideEnd
 cmp #$d0
 bcs SideEnd
 jsr SceneSide
 bne SideEffectTail
 dec R0
 bne SideNext
SideEnd:
 rts
SideEffectTail:
 jmp SideEffect
