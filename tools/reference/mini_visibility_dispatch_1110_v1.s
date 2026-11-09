; Same 94-byte ROLL_WORLD span in physical PRG78. Both public entries stay put.
; RlIsActive reads the selected owner and Roll variant. It leaves A equal to the
; selected owner for non-Bass, with C clear. It never touches the farcall packet.
.export RlInjuryStatusDispatch, RlVisibleDispatch, MiniVisible, VisibleEnd

SavedA = $016a
NextBank = $0162
TargetLo = $016c
TargetHi = $016d
FarCallCommon = $015a
RlIsActive = $b808

.segment "CODE"
RlInjuryStatusDispatch:
    sta SavedA
    php
    jsr RlIsActive
    bcs StatusRoll
    lda #$85
    sta TargetLo
    lda #$a2
    bne Legacy
StatusRoll:
    lda #$e0
    bne Roll

Legacy:
    sta TargetHi
    plp
    lda #$dd
    jmp FarCallCommon
Roll:
    sta TargetLo
    lda #$ad
    sta TargetHi
    plp
    lda #$cf
    jmp FarCallCommon
    .res 47 - (* - RlInjuryStatusDispatch), $ea

RlVisibleDispatch:
    sta SavedA
    php
    jsr RlIsActive
    bcs VisibleRoll
    cmp #41
    beq MiniVisible
    lda #$ec
    sta TargetLo
    lda #$a3
    bne Legacy
VisibleRoll:
    lda #$e4
    bne Roll

MiniVisible:
    ; The exact old Mini target is physical PRG84:B43B -> B3E4 (SEC/RTS).
    ; Publish the same final transport operands without entering its map chain.
    plp
    lda #$d4
    sta NextBank
    lda #$3b
    sta TargetLo
    lda #$b4
    sta TargetHi
    lda SavedA
    sec
    rts
VisibleEnd:
    .assert VisibleEnd - RlInjuryStatusDispatch = 94, error, "fixed dispatch span"
