.setcpu "6502"

FarCallCommon = $015a
SavedA = $016a
TargetLo = $016c
TargetHi = $016d

.segment "HEAD"
HeadDispatch:
    ; Its unique fixed caller loads SelectedCharacter into A and saves it
    ; before the mapper entry. Keep the same P/A frame on the other routes.
    php
    pha
    eor #41
    beq Mini
    lda #$b0
    sta TargetLo
    lda #$bf
    sta TargetHi
    lda #$9c
    jsr FarCallCommon
    bcc Legacy
    pla
    plp
    sta SavedA
    lda #$fe
    sta TargetLo
    lda #$b6
    sta TargetHi
    lda #$02
    jmp FarCallCommon
Legacy:
    pla
    plp
    sta SavedA
    lda #$f1
    sta TargetLo
    lda #$b6
    sta TargetHi
    lda #$c2
    jmp FarCallCommon
Mini:
    pla
    plp
    ; Vector 10 is the same pending/filtered source head owner selected by
    ; NrHead, and still checks both live markers or uses the cold veneer.
    lda #$3e
    sta TargetLo
    lda #$b4
    sta TargetHi
    lda #$d4
    jmp FarCallCommon
    .assert *-HeadDispatch=80, error, "Existing head dispatcher and its 16-byte terminal fill"
