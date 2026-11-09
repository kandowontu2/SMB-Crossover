.setcpu "6502"
.export GetXOffscreenBits, GetYOffscreenBits, YOnscreenUnit

R4=$07
R5=$08
R6=$09
R7=$0a
ObjectX=$75
ObjectXPage=$5c
ObjectY=$bd
ObjectYPage=$a4
ScreenEdgeX=$071f
ScreenEdgePage=$071d
XBits=$8b60
XDefault=$8b70
YBits=$8bb8
YDefault=$8bc1
YEdge=$8bc4

.segment "OFFSCREEN_X"
.proc GetXOffscreenBits
Start:
    stx R4
    ldy #1
Edge:
    lda ScreenEdgeX,y
    sec
    sbc ObjectX,x
    sta R7
    lda ScreenEdgePage,y
    sbc ObjectXPage,x
    bmi Negative
    bne Far
    lda #$38
    sta R6
    lda #8
    sta R5
    lda R7
    cmp #$38
    bcs Far
    ; Difference is below 56, so the shifted result is already 0..6.
    lsr
    lsr
    lsr
    cpy #1
    bcs Index
    adc #8
Index:
    tax
    bpl ReadBits
Far:
    ldx XDefault+1,y
    bne ReadBits                 ; both native defaults are nonzero
Negative:
    ldx XDefault,y
ReadBits:
    lda XBits,x
    ldx R4
    cmp #0
    bne Return
    dey
    bpl Edge
Return:
    rts
.assert *-Start <= $46, error, "X table address stays fixed"
.res $46-(*-Start),$ea
.endproc

.segment "OFFSCREEN_Y"
.proc GetYOffscreenBits
Start:
    stx R4
    lda ObjectYPage,x
    cmp #1
    beq YOnscreenUnit
    ldy #1
Edge:
    lda YEdge,y
    sec
    sbc ObjectY,x
    sta R7
    lda #1
    sbc ObjectYPage,x
    bmi YNegative
    bne Far
Near:
    lda #$20
    sta R6
    lda #4
    sta R5
    lda R7
    cmp #$20
    bcs Far
    ; Difference is below 32, so the shifted result is already 0..3.
    lsr
    lsr
    lsr
    cpy #1
    bcs Index
    adc #4
Index:
    tax
    bpl ReadBits
Far:
    ldx YDefault+1,y
ReadBits:
    lda YBits,x
    ldx R4
    cmp #0
    bne Return
    dey
    bpl Edge
Return:
    rts
.assert *-Start <= $45, error, "Y table address stays fixed"
.res $45-(*-Start),$ea
.endproc

; Keep these linked table bytes at their original addresses. A contiguous
; segment lets ca65 resolve the two short branches into the old outline.
.byte $00,$08,$0c,$0e,$0f,$07,$03,$01,$00
.byte $04,$00,$04
.byte $ff,$00
YOnscreenUnit:
    ; The installed path already skips the top edge for page 1. The
    ; bottom edge subtraction then has no borrow and its high delta is 0.
    ldy #0
    lda #$ff
    sec
    sbc ObjectY,x
    sta R7
    jmp GetYOffscreenBits::Near
YNegative:
    ldx YDefault,y
    jmp GetYOffscreenBits::ReadBits
.assert *-YOnscreenUnit <= $15, error, "Following shared veneer stays fixed"
.res $15-(*-YOnscreenUnit),$ea
