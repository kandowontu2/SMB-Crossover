.setcpu "6502"
SavedA = $016a
TargetLo = $016c

.segment "BOX_GATE"
BoxGate:
    sta SavedA
    eor #41
    ; Mini's separately linked leaf is in the same fixed CPU page.
    .byte $f0, <($edaa-($ed7a+7))
    lda #$0c
    sta TargetLo
    ; This nonzero immediate supplies the branch condition. Reuse the
    ; native head veneer's unchanged AF / E2 transport for foreign boxes.
    .byte $d0, <($ed5b-($ed7a+14))
    .res 18-(*-BoxGate), $ea

.segment "BOX_MINI"
MiniBox:
    eor #41                     ; A was zero on the branch from BoxGate
    ldy #1
    sec
    rts
    .res 7-(*-MiniBox), $ea
