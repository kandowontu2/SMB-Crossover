; Existing PRG74 A5D1..A61A: red-shell homing and the adjacent wave decision.
; Preserve the installed 32-update turn age and +/-3px integer speed.
.setcpu "6502"
.segment "KIRBY_RETURN"

KirbyReturnMotion:
    lda KbShotKind,x
    cmp #3
    bne KirbyWaveMotion
    lda KbShotAge,x
    cmp #32
    bcc KirbyShotMove
    sec
    lda KbShotX,x
    sbc Player_X_Position
    tay
    lda KbShotPage,x
    sbc Player_PageLoc
    bcc KirbyShellLeft
    bne KirbyShellRightFar
    cpy #4
    bcc KirbyShellCatch
KirbyShellRightFar:
    lda #$fd
    bne KirbyShellSpeed
KirbyShellLeft:
    cmp #$ff
    bne KirbyShellLeftFar
    cpy #$fd
    bcs KirbyShellCatch
KirbyShellLeftFar:
    lda #3
KirbyShellSpeed:
    sta KbShotVXHi,x
    bne KirbyShotMove
KirbyShellCatch:
    jmp KirbyShotKill

KirbyWaveMotion:
    cmp #8
    bne KirbyShotMove
    lda KbShotAge,x
    and #8
    lsr a
    lsr a
    ; Both admitted values 0/2 have carry clear after the second shift.
    ; Subtract the borrow to produce the existing -1/+1 vertical half-wave.
    sbc #0
    sta KbShotVYHi,x
