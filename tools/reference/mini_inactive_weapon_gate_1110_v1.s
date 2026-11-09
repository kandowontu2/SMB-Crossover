.setcpu "6502"
.export WeaponOwnerRouter, MiniNoWeapon, LegacyWeaponCall, WeaponOwnerRouterEnd

SelectedCharacter = $6002
PlayerStatus = $075b
FireballState = $25
SavedA = $016a
TargetLo = $016c
TargetHi = $016d
FarCallCommon = $015a
AirBubbles = $ae68

.segment "ROUTER"
WeaponOwnerRouter:
    lda SelectedCharacter
    cmp #6
    bcc Legacy
    sta SavedA
    cmp #41
    bne Expanded
    ; Equivalent to the linked Mini guard at bank79 $AADC. Keep the
    ; existing air-bubble path for sprite cleanup and swimming.
    lda PlayerStatus
    and #$fe
    ora FireballState
    ora FireballState+1
    beq MiniNoWeapon
Expanded:
    sec
    lda #$58
    sta TargetLo
    lda #$ad
    sta TargetHi
    lda #$fc
    jmp FarCallCommon

Legacy:
    cmp #1
    bcc WeaponOwnerRouterEnd
    sta SavedA
    cmp #3
    bcs BillLinkSimon
    cmp #2
    beq Samus
    sec
    lda #$93
    sta TargetLo
    lda #$a0
    sta TargetHi
    lda #$88
    bne LegacyWeaponCall
Samus:
    lda #$57
    sta TargetLo
    lda #$ae
    sta TargetHi
    lda #$f9
    bne LegacyWeaponCall
BillLinkSimon:
    lda #$00
    sta TargetLo
    lda #$a0
    sta TargetHi
    lda #$d4
LegacyWeaponCall:
    jsr FarCallCommon
MiniNoWeapon:
    jmp AirBubbles
WeaponOwnerRouterEnd:
.assert WeaponOwnerRouterEnd-WeaponOwnerRouter=103,error,"Retain the following native entry"
