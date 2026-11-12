; Point against an enemy rectangle expanded by eight pixels. Coordinates
; are signed 16-bit screen pixels, biased by $8000 by the caller. Expansion
; cannot overflow that representation within the native screen neighborhood.
.setcpu "6502"
.segment "OVERLAP"
SteveThrowOverlap:
    ; (point - low + 8) must fit in one byte and be smaller than width+16.
    ldx #0
    jsr ThrowAxis
    bcc ThrowMiss
    lda ThrowDelta
    cmp ThrowExtent
    bcs ThrowMiss               ; X upper edge is exclusive.
    ldx #2
    jsr ThrowAxis
    bcc ThrowMiss
    lda ThrowExtent
    cmp ThrowDelta              ; Y upper edge is inclusive.
    rts
ThrowMiss:
    clc
    rts

ThrowAxis:
    sec
    lda ThrowPoint,x
    sbc ThrowLow,x
    sta ThrowDelta
    lda ThrowPoint+1,x
    sbc ThrowLow+1,x
    sta ThrowDelta+1
    clc
    lda ThrowDelta
    adc #8
    sta ThrowDelta
    lda ThrowDelta+1
    adc #0
    bne ThrowMiss
    sec
    lda ThrowHigh,x
    sbc ThrowLow,x
    clc
    adc #16
    sta ThrowExtent
    sec
    rts
