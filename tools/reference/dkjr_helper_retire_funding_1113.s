.setcpu "6502"
.segment "PREDICATE"
; Original X-axis then Y-axis field-read order, including equal-left skips.
; FE/FF index the two axes through these biased addresses. Preserve X/Y,
; return A0/1 and exact original C/V/N/Z. No source data scratch is written.
DkCompactPredicate:
    txa
    pha
    ldx #$fe
PredicateAxis:
    lda $bf40,x
    cmp $bf44,x
    bcc PredicateLeft
    beq PredicateAxisOK
    cmp $bf46,x
    beq PredicateAxisOK
    bcs PredicateNo
PredicateAxisOK:
    inx
    bne PredicateAxis
    pla
    tax
    lda #1
PredicateTrueRTS:
    rts
PredicateLeft:
    lda $bf42,x
    cmp $bf44,x
    bcs PredicateAxisOK
PredicateNo:
    pla
    tax
    lda #0
PredicateFalseRTS:
    rts
DkCompactPredicateEnd:
