.setcpu "6502"
.segment "MOVEMENT"
.export X5OwnMovement, MovementPrefixEnd

SelectedCharacter = $6002
FamilyAlts = $5fe5
SavedA = $016a
TargetLo = $016c
TargetHi = $016d
FarCall = $015a
MiniMovementTail = $a3d9
SavedCameraDispatch = $a741

X5OwnMovement:
    sta SavedA
    php
    lda SelectedCharacter
    cmp #41
    beq Mini
    cmp #10
    bne Camera
    lda FamilyAlts
    and #$44
    cmp #$40
    bne Camera
    plp
    lda #$00
    sta TargetLo
    lda #$b4
    sta TargetHi
    lda #$d5
    jmp FarCall
Mini:
    plp
    jmp MiniMovementTail
Camera:
    ; The existing dispatch loads SelectedCharacter at this point.
    ; Its saved A and P have already been staged by this entry.
    jmp SavedCameraDispatch
MovementPrefixEnd:
    .assert *-X5OwnMovement=47,error,"Original movement prefix allocation"
    .res 49-(*-X5OwnMovement),$ea
