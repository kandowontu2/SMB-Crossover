; Enter from the existing mature Metal pickup after native types2+ diverge.
; A is exactly0/1. Existing armor and common native cleanup remain in place.
.setcpu "6502"
.segment "FLOWER_DISPATCH"
.import Ms25Armor,Ms25TierStore,MsWeaponItem0
.export MsFlowerDispatch
MsFlowerDispatch:
    cmp #$00
    bne MsFlowerGrant
    jmp Ms25Armor
MsFlowerGrant:
    jsr MsWeaponItem0
    lda #$02
    jmp Ms25TierStore
