.setcpu "6502"
.export GiantBodyBox, GiantFeet, GiantHead, GiantSide, GiantProbeX, GiantProbeY

PlayerX = $75
PlayerPage = $5c
PlayerY = $bd
RelativeX = $0571
RelativeY = $057c
Offscreen = $05a0
Crouching = $0717
Box = $0658
GetBlockBufferAddr = $95dc
QueryRow = $05
QueryTile = $06
QueryIndex = $07
QueryX = $08
QueryPointer = $09

.segment "GIANT"

; Donor B12E..B13E selects native row 1 or crouching row 2. The four
; adders are literal donor E201..E208, followed by EB5F vertical wrap.
GiantBodyBox:
    lda RelativeX
    clc
    adc #$f0
    sta Box
    lda RelativeX
    clc
    adc #$20
    sta Box+2
    ldx Crouching
    beq Standing
    lda #$e8
    bne Upper
Standing:
    lda #$a8
Upper:
    clc
    adc RelativeY
    sta Box+1
    lda RelativeY
    clc
    adc #$20
    sta Box+3
    ldx #0
    ldy #0
    cmp Box+1
    bcs Done
    lda Offscreen
    and #$10
    bne ClipBottom
    sta Box+1
    rts
ClipBottom:
    lda #$ff
    sta Box+3
Done:
    rts

; Source E427..E474: signed X carry into the world page, native tile row,
; and identical raw packet. Callers still own vertical/sentinel admission.
GiantFeet:
    iny
GiantHead:
    lda #0
    beq Probe
GiantSide:
    lda #1
Probe:
    ldx #0
    pha
    sty QueryIndex
    lda GiantProbeX,y
    clc
    php
    adc PlayerX
    sta QueryX
    lda PlayerPage
    adc #0
    plp
    bpl WorldPage
    sbc #0
WorldPage:
    lsr a
    lda QueryX
    ror a
    lsr a
    lsr a
    lsr a
    jsr GetBlockBufferAddr
    ldy QueryIndex
    lda PlayerY
    clc
    adc GiantProbeY,y
    and #$f0
    sec
    sbc #$20
    sta QueryRow
    tay
    lda (QueryPointer),y
    sta QueryTile
    ldy QueryIndex
    pla
    bne Horizontal
    lda PlayerY
    jmp Subtile
Horizontal:
    lda PlayerX
Subtile:
    and #$0f
    sta QueryIndex
    lda QueryTile
    rts

GiantProbeX:
    .byte $08,$00,$10,$04,$14,$04,$04,$f1,$00,$0f,$1e,$00,$00,$00,$00,$00
    .byte $00,$00,$0f,$0f,$0f,$0f,$0f,$0f,$0f,$f0,$f0,$f0,$f0,$f0,$f0,$f0
    .byte $ff,$f0,$00,$0f,$1f,$1f,$1f,$1f,$1f,$1f,$1f,$1f,$ff,$ff,$00,$f0
    .byte $f0,$f0,$f0,$ff,$0f,$1f,$1f,$1f,$1f,$ff,$ff
GiantProbeY:
    .byte $18,$14,$14,$06,$06,$08,$10,$20,$20,$20,$20,$c8,$e8,$08,$b8,$d8
    .byte $f8,$18,$c8,$e8,$08,$b8,$d8,$f8,$18,$c8,$e8,$08,$b8,$d8,$f8,$18
    .byte $ff,$a8,$a8,$a8,$a8,$c8,$e8,$08,$b8,$d8,$f8,$18,$ff,$ff,$e8,$e8
    .byte $f8,$08,$18,$ff,$e8,$e8,$f8,$08,$18,$ff,$ff
    .assert GiantProbeY-GiantProbeX=59, error, "Donor 59 X adders"
    .assert *-GiantProbeY=59, error, "Donor 59 Y adders"
