.setcpu "6502"

SelectedCharacter = $6002
FarCallCommon = $015a
SavedA = $016a
TargetLo = $016c
TargetHi = $016d
BlockBufferColli_Side = $958b

.segment "SIDE_FIXED"
FixedSide:
    sta SavedA
    lda SelectedCharacter
    eor #41                      ; preserve the incoming carry for foreign callers
    .byte $f0, <($913d-($90e4+10)) ; BEQ, within fixed low-bank range
    lda #$a2
    sta TargetLo
    lda #$be
    sta TargetHi
    lda #$a1
    jmp FarCallCommon
    .res 27-(*-FixedSide), $ea
MiniTargetHi:
    lda #$ad
    sta TargetHi
    lda #$fc
    jmp FarCallCommon
    .assert *-FixedSide=37, error, "Fixed side prefix and tail span"

.segment "SIDE_VISIBLE_TAIL"
MiniTargetLo:
    lda #$9b
    sta TargetLo
    .byte $30, <($90ff-($913d+7)) ; BMI, guaranteed by the immediate above
    .assert *-MiniTargetLo=7, error, "GuestPlayerVisible post-JMP padding"

.segment "SIDE_BANK33"
ForeignSide:
    php
    lda #$b0
    sta TargetLo
    lda #$bf
    sta TargetHi
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

Legacy:
    lda SavedA
    plp
    jmp LegacySide

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

    .res 64-(*-ForeignSide), $ea
LegacySide:                      ; retain the distinct original BEE2 entry
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

    .assert LegacySide-ForeignSide=64, error, "Original BEE2 side entry"
    .res 94-(*-ForeignSide), $ff
    .assert *-ForeignSide=94, error, "No Rogue Dawn page at BF00"
