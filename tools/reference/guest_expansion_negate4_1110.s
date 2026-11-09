; Exact short-period negative shift-four target in the existing MMC5 mixer.
.setcpu "6502"
.export SweepTarget, LowPeriod

Period = $72f7
Delta = $72f9
Control = $72fb

.segment "SWEEP_FOOTER"
LowPeriod:
    and #$0f
    cmp #$0c
    .assert * = $ac10, lderror, "Pinned branch into the shift dispatcher"
    .assert ShiftCount = $ac82, lderror, "Original shift operation entry"
    .byte $d0, $ac82-$ac12    ; BNE ShiftCount
    ; P is at least 8, the high bytes are zero, and Y is already zero.
    lda Period
    .repeat 4
    lsr a
    .endrepeat
    sta Delta
    lda Period
    clc
    sbc Delta                ; P - floor(P/16) - 1 is nonnegative.
    sta Delta
    clv                      ; Match the original high-byte subtraction.
    rts
.assert * = $ac28, lderror, "Original sweep clock stays at AC28"

.segment "SWEEP_TARGET"
SweepTarget:
    lda Period
    sta Delta
    ldy Period+1
    sty Delta+1
    bne ReadControl
    cmp #8
    bcc Muted
    lda Control
    jmp LowPeriod
ReadControl:
    lda Control
ShiftCount:
    and #7
    tay
    beq Direction
Shift:
    lsr Delta+1
    ror Delta
    dey
    bne Shift
Direction:
    lda Control
    and #8
    bne Negate
    clc
    lda Period
    adc Delta
    sta Delta
    lda Period+1
    adc Delta+1
    sta Delta+1
    jmp Range
Negate:
    clc
    lda Period
    sbc Delta
    sta Delta
    lda Period+1
    sbc Delta+1
    sta Delta+1
Range:
    ; A is the high target byte on both arithmetic paths.
    cmp #8
    bcs Muted
    sec
    rts
Muted:
    clc
    rts
.assert * = $acc8, lderror, "Next public audio entry stays at ACC8"
