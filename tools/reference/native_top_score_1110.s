.setcpu "6502"
.segment "TOP_SCORE"

PrimaryScore = $07af
SecondaryScore = PrimaryScore+6
TopScore = $07a9

; Use fixed addresses for the second player's low-to-high subtraction.
; Preserve its final borrow and overflow even on non-decimal display bytes.
UpdateTopScore:
    jsr CheckPrimary
    sec
    .repeat 6, I
        lda SecondaryScore+5-I
        sbc TopScore+5-I
    .endrepeat
    ldx #5
    ldy #$ff
    bcc Done
    inx
    iny

; Both paths write the same six bytes in the original order. The last
; CPY recreates the original secondary return flags without changing V.
CopyScore:
    .repeat 3
        lda PrimaryScore,x
        sta TopScore,y
        inx
        iny
    .endrepeat
    cpy #6
    bcc CopyScore
Done:
    rts

CheckPrimary:
    .repeat 5, I
        lda PrimaryScore+I
        cmp TopScore+I
        bne PrimaryDiff
    .endrepeat
    lda PrimaryScore+5
    cmp TopScore+5
    beq Done
PrimaryDiff:
    bcc Done
    ldx #0
    ldy #0
    beq CopyScore

.assert *-UpdateTopScore<=$85,error,"Keep the following bank-3 data fixed"
.res $85-(*-UpdateTopScore),$ea
