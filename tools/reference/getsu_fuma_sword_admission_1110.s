.setcpu "6502"

GameEngineSubroutine = $0f
GfSwordActive = $c00f
GfSwordPhase = $c010
GfSwordSlots = $a7f2

.segment "SWORD_GUARD"
.export GfSwordAdmission
GfSwordAdmission:
    lda GameEngineSubroutine
    cmp #8
    bne NoContact
    lda GfSwordActive
    beq NoContact
    lda GfSwordPhase
    cmp #2
    bcc NoContact
    jmp GfSwordSlots
NoContact:
    lda #0                     ; Original PLA reloads the final slot number.
    ldx #$ff                   ; Six original DEX operations leave this X/N/Z.
    clc
    rts
    .res 37-(*-GfSwordAdmission),$ea
