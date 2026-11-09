.setcpu "6502"

R0 = $03
CombineOffscreen = $8afa
RawEdge = $8b1e

.export EnemyOffscreen, RawFar, RawNegative

.segment "ENEMY"
EnemyOffscreen:
    ; Same zero-page scratch publication, then the old X+1 modulo 256.
    stx R0
    inx
    ldy #1
    .byte $d0,<(CombineOffscreen-$8af0)

.segment "NEG_BRANCH"
    .byte $30,<($8b57-$8b2d)

.segment "FAR_TAIL"
RawFar:
    dey
    .byte $10,<(RawEdge-$8b52)
    iny                         ; Restore the final Y=0 on the left edge.
Outside:
    lda #$ff
    sec
    rts
RawNegative:
    cpy #1
    bcs Outside
    lda #0
    sec
    dey
    rts
    .assert RawNegative=$8b57,lderror,"Negative raw lane branch"
    .res 20-(*-RawFar),$ea
