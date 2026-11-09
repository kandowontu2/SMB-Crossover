.setcpu "6502"
SavedA = $016a
TargetLo = $016c

.segment "ADDER"
Adder:
    sta SavedA
    eor #41
    bne Legacy
    lda SavedA
    ldy #2
    sec
    rts
Legacy:
    jmp $e4a7
    .res 18-(*-Adder), $ea

.segment "FORMER_SIDE"
FormerSide:
    lda #$04
    sta TargetLo
    jmp $ed5b                    ; identical high-byte/bank tail of the next veneer
    .res 12-(*-FormerSide), $ea
