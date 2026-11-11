.setcpu "6502"

; F801's existing right-edge probe already examined the cells beside the
; coarse source edge at hand height. When both were empty, an action 8 hang
; can be below a floating question block in the far half of the source cell.
; Reuse the previous inside sample, one pixel left of the coarse edge.
.segment "ENTRY"
QuestionEdge:
    cmp #0
    bne OriginalAlign
    cpy #24
    bne OriginalAlign
    lda $c616
    cmp #8
    bne OriginalAlign
    lda $c618
    cmp #2
    bne OriginalAlign
    lda $c617
    cmp #78
    bne OriginalAlign
    jmp CheckCoordinate
OriginalAlign:
    jmp $c40b

.segment "COORDINATE"
CheckCoordinate:
    lda $b369
    and #31
    cmp #31
    bne CoordinateFailed
    jmp QuestionGeometry
CoordinateFailed:
    jmp $c40b

.segment "GEOMETRY"
QuestionGeometry:
    lda $c60f
    and #31
    bne GeometryFailed
    lda $b36b
    and #$f0
    ; CheckCoordinate's equal CMP still supplies carry.
    sbc #32
    bcc GeometryFailed
    sta $b36b
    jsr $b310
    cmp #$c0
    bne GeometryFailed
    ; A single exposed tile must have air on both sides, above and below.
    inc $b369
    bne RightNeighbor
    inc $b36a
    beq GeometryFailed
RightNeighbor:
    jsr $b310
    bcs GeometryFailed
    lda $b369
    sbc #16
    sta $b369
    bcs LeftNeighbor
    dec $b36a
LeftNeighbor:
    jsr $b310
    bcs GeometryFailed
    ; The left neighbor ends in $0F, $2F, ..., or $EF.
    inc $b369
Roof:
    dec $b36b
    jsr $b310
    bcs GeometryFailed
    lda $b36b
    ; A typed top derived from the one-byte hand row is at most Y208.
    adc #17
    sta $b36b
    jsr $b310
    bcs GeometryFailed
    ; QueryX now names the real left edge. The existing successful F801
    ; path applies the same original vertical alignment and edge-minus-8
    ; source actor position it uses for other typed right ledges.
    jmp $d844
GeometryFailed:
    jmp $c40b

.segment "SUPPORT_MATERIAL"
    ; B310 already required actual native solidity. Its only solid
    ; metatiles below $14 are the four existing $10–$13 pipe caps.
    cmp #$14
    bcc Exposed
    cmp #$58
    beq Exposed
    cmp #$51
    beq Ordinary
    cmp #$57
    beq Ordinary
    cmp #$c0
    bne Empty
Ordinary:
    lda $c616
    bne Empty
