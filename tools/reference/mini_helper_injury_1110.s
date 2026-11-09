; Native Mini lift admission after the stock injury movement and camera update.
.setcpu "6502"
.export InjuryRoute, InjuryFar, InjuryScan

SelectedCharacter = $6002
PlayerCtrlRoutine = $a0c3
PowerupDispatchTail = $a51c
SamusMovementTail = $a650
CurrentBankC = $7da1
MapC = $80c2
MiniReady = $c300
Header = $dfe0
FarCall = $015a
FarTarget = $016c
DirectCallRestoreC = $b49f

.segment "POWER_DUP"
    jmp PowerupDispatchTail
InjuryRoute:
    lda SelectedCharacter
    cmp #41
    beq Mini
    jmp PlayerCtrlRoutine
Mini:
    jsr PlayerCtrlRoutine
    jmp InjuryFar

.segment "INJURY_JUMP"
    jmp InjuryRoute

.segment "SAMUS_DUP"
    jmp SamusMovementTail
InjuryFar:
    lda #<InjuryScan
    sta FarTarget
    lda #>InjuryScan
    sta FarTarget+1
    lda #$d4
    jmp FarCall
    nop

.segment "INJURY_SAVE_C"
InjuryScan:
    lda CurrentBankC
    pha
    jmp CheckMiniState

.segment "INJURY_AUTH"
Reject:
    pla
    jmp MapC
CheckMiniState:
    lda #2
    jsr MapC
    cmp MiniReady
    bne Reject
    lda Header
    cmp #$a7
    bne Reject
    lda Header+1
    cmp #41
    bne Reject
    jmp ScanMiniLifts

.segment "INJURY_SCAN"
ScanMiniLifts:
    ; The native ROM leaf uses C2 state only. Its constructor rechecks the
    ; active raw identity and authored 1-1 scene before publishing a slot.
    ; Use the original checked transport's live stack shape at B49F.
    php
    lda #$cf
    sta FarTarget
    lda #$bb
    sta FarTarget+1
    lda #$98
    jmp DirectCallRestoreC
