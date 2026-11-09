.setcpu "6502"

SelectedCharacter = $6002
FarCallCommon = $015a
NextBank = $0162
SavedA = $016a
TargetLo = $016c
TargetHi = $016d
ReturnA = $0179
BlockBufferColli_Side = $958b

.segment "SIDE"
.export ForeignSide, LegacySide, Rejected
ForeignSide:
    php
    lda #$b0
    sta TargetLo
    lda #$bf
    sta TargetHi
    lda SelectedCharacter
    bne Rejected
    lda #$9c
    jsr FarCallCommon
    bcc Legacy

    lda #$55
    sta TargetLo
    lda #$b7
    sta TargetHi
    plp
    lda #$02
    jmp FarCallCommon

SourceSide:
    pla
    plp
    sta SavedA
    lda #$58
    sta TargetLo
    lda #$bc
    sta TargetHi
    lda #$d9
    jmp FarCallCommon

    .res 60-(*-ForeignSide), $ea
Legacy:
    lda SavedA
    plp
LegacySide:
    php
    pha
    lda SelectedCharacter
    cmp #4
    beq SourceSide
    cmp #11
    bcs SourceSide
    pla
    plp
    jmp BlockBufferColli_Side

Rejected:
    sta ReturnA                 ; Exact nonzero A from the original predicate.
    lda #$9c
    sta NextBank                ; Preserve the original packet's final operand.
    bne Legacy

    .assert LegacySide-ForeignSide=64,error,"Original public BEE2 side entry"
    .res 94-(*-ForeignSide), $ff
