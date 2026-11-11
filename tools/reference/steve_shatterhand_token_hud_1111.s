.segment "TOKEN_INGRESS"

; Keep the three source columns and move them below the stock SMB status line.
SteveTokenHud:
    lda SteveTokenPattern
    beq HudDone
    sta $c3fb
    lda #96
    sta $07
    lda #34
    sta $09
HudSlot:
    lda $c3fb
    and #3
    beq HudNext
    lsr a
    jsr SteveDrawTokenPair
HudNext:
    lsr $c3fb
    lsr $c3fb
    beq HudDone
    lda $07
    clc
    adc #24
    sta $07
    bne HudSlot
HudDone:
    rts
