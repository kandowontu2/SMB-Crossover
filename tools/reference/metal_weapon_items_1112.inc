; Metal Storm (USA), fixed PRG bank15, original E7B3..E80C (90 bytes).
; Exact item-table entries 0/1/2. MsState is the owning original RAM image.
; No host allocation, native pickup admission or audio consumer is granted.
.setcpu "6502"
.segment "WEAPON_ITEMS"
.import MsState
.export MsWeaponItem0

; Item0: source upgraded shot mode. Both other weapon modes are cleared.
MsWeaponItem0:
    lda #$80
    sta MsState+$0718
    sta MsState+$0499
    lda #$00
    sta MsState+$0717
    sta MsState+$043c
    sta MsState+$0511
    jmp MsWeaponItemPose

; Item1: source GravityFire. Its source object82 remains outside host admission.
.ifndef MS_WEAPON_ITEM0_ONLY
.export MsWeaponItem1,MsWeaponItem2
MsWeaponItem1:
    lda #$80
    sta MsState+$0717
    lda MsState+$043f
    sta MsState+$043e
    lda #$02
    sta MsState+$074a
    lda #$00
    sta MsState+$043c
    sta MsState+$0718
.endif
MsWeaponItemPose:
    lda MsState+$04e0
    cmp #$05
    bne MsWeaponItemSound
    lda #$04
    sta MsState+$04e0
    rts
MsWeaponItemSound:
    lda #$0a
    sta MsState+$07e7
    rts

; Item2: source third weapon/effect flag. Its object1 path is not admitted here.
.ifndef MS_WEAPON_ITEM0_ONLY
MsWeaponItem2:
    lda #$80
    sta MsState+$043c
    sta MsState+$0499
    lda #$00
    sta MsState+$0717
    sta MsState+$0718
    sta MsState+$0511
    lda #$0a
    sta MsState+$07e7
    rts
.endif
