.setcpu "6502"
.segment "WORKER"
.export BoundingBoxCore, WorkerEnd

BoundingBoxCore:
    stx $03
    lda $057c,y
    sta $05
    lda $0571,y
    sta $04
    txa
    asl
    asl
    tay
    lda $0645,x
    asl
    asl
    tax
    lda $04
    clc
    adc $e20d,x
    sta $0658,y
    lda $04
    clc
    adc $e20f,x
    sta $065a,y
    ; Both indices are multiples of four. Fold the axis increment into
    ; the absolute operands and leave Y equal to the original box index.
    lda $05
    clc
    adc $e20e,x
    sta $0659,y
    lda $05
    clc
    adc $e210,x
    sta $065b,y
    tya
    ldx $03
    rts
WorkerEnd:
