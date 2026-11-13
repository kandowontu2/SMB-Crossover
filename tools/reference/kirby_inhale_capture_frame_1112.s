; These two Kirby-owned spans keep inhale contact eligibility through the
; update that fills the mouth. The following weapons tick clears that action.
.setcpu "6502"

.segment "ACTION_CLOCK"
    lda KbActionAge
    beq KirbyWeaponInput
    dec KbActionAge
    bne KirbyWeaponInput
    lda KbAction
    cmp #1
    bne ClearAction
    lda KbMouth
    beq KirbyWeaponInput
ClearAction:
    lda #0
    sta KbAction
    ; Unchanged weapon input follows this span.

.segment "CAPTURE_TAIL"
    ; Suction already set action 1 and the mouth now holds the captured enemy.
    lda #1
    sta KbActionAge
    sta Square2SoundQueue
    jmp KirbyPullReturn
