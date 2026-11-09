.setcpu "6502"

R0 = $03
R4 = $07
R5 = $08
R6 = $09
R7 = $0a
ObjectOffset = $0d
ObjectYPage = $a4
ObjectY = $bd
Selected = $6002
SpriteOffscreen = $05a0
GetPlayerOffscreenBits = $8ace
GetOffscreenVertical = $8b05

.export PostScrollPlayerOffscreen, GetYOffscreenBitsHigh, CombineOffscreen

.segment "PLAYER_SITE"
    jsr PostScrollPlayerOffscreen

.segment "COMBINE"
CombineOffscreen:
    ; Old four ASLs always left C=0. The private leaf now supplies the
    ; already-shifted nibble and preserves the native geometry's V.
    clc
    ora R0
    sta R0
    pla
    tay
    lda R0
    sta SpriteOffscreen,y
    ldx ObjectOffset
    rts
    .res 18-(*-CombineOffscreen),$ea

.segment "Y_AND_POST_SCROLL"
GetYOffscreenBitsHigh:
    stx R4
    ldy #1
    lda ObjectYPage,x
    cmp #1
    bne Edge
    dey                     ; Unit 1 retains the original top-pass bypass.
Edge:
    lda YEdge,y
    sec
    sbc ObjectY,x
    sta R7
    lda #1
    sbc ObjectYPage,x
    bmi Negative
    bne Far
    lda #$20
    sta R6
    lda #4
    sta R5
    lda R7
    cmp #$20
    bcs Far
    lsr a
    lsr a
    lsr a
    cpy #1
    bcs Index
    adc #4
Index:
    tax
    lda YHighBits,x
    bne Done
    ldx R4                 ; The only next-edge path needing the original X.
    dey
    bpl Edge
Done:
    rts
Far:
    tya
    bne Full              ; Upper positive edge, or lower clear edge.
    rts
Negative:
    dey
    bmi Full              ; Lower negative edge is full; upper tries lower.
    bpl Edge
Full:
    lda #$f0
    rts
YEdge:
    .byte $ff,$00
YHighBits:
    .byte $00,$80,$c0,$e0,$f0,$70,$30,$10

PostScrollPlayerOffscreen:
    ; Only physical bank 1 A13F enters here, immediately after VvScroll.
    ; Ordinary ScrollHandler returned X=0 with its fresh horizontal R0.
    ; Zero took the no-clamp lane, so a repeat sees the same coordinates.
    lda Selected
    cmp #18
    beq FullPlayer
    lda R0
    bne FullPlayer
    pha                    ; Same destination offset pushed by the common entry.
    jmp GetOffscreenVertical
FullPlayer:
    jmp GetPlayerOffscreenBits

    .assert *-GetYOffscreenBitsHigh <= 104,error,"Original private Y footprint"
    .res 104-(*-GetYOffscreenBitsHigh),$ea
