; Mini polls the chord at the existing accepted source-update boundary.
MiniAssistState = $c30e       ; 0 none, 1..6 native slot, $80 pending retry.

.export MiniManualInput
MiniManualInput:
    lda SavedJoypadBits
    sta MiniHeld
    and #$28                 ; Up + Select, in either press order.
    cmp #$28
    bne @status
    eor MiniPrevious
    and #$28
    bne @spawn
@status:
    lda MiniAssistState
    bpl @done
@spawn:
    ldy #$f4                 ; Player X+4 minus half the native 32px girder.
    lda #<$b378
    sta MiniNativeTarget+1
    jmp MiniManualHigh
@done:
    rts
