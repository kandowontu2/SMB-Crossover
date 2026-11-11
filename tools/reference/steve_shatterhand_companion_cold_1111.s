; The shared copier has staged the sixth code row at raw3 $B400.
; Raw2 is already mapped at C000. Authenticate the resident bytes before
; returning to the incumbent bootstrap, which restores the staging row.
.setcpu "6502"
.segment "COMPANION_COLD"
SteveCompanionCold:
.ifdef STEVE_SEVENTH_ROW
    ldx #8                          ; Y is zeroed by the fifth-row trampoline
.else
    ldx #4
    ldy #0
.endif
    sty $03
    sty $05
    lda #$b4
    sta $04
    lda #$c5
    sta $06
SteveCopyCompanion:
    lda ($03),y
    sta ($05),y
    cmp ($05),y
    bne SteveCompanionCopyFailed
    iny
    bne SteveCopyCompanion
    inc $04
    inc $06
    dex
.ifdef STEVE_SEVENTH_ROW
    beq SteveBeginCompanionState
    cpx #4
    bne SteveCopyCompanion
    inc $06                         ; skip C900, the shared state page
    bne SteveCopyCompanion
SteveBeginCompanionState:
    tya                             ; Y wrapped to zero at the last page end
    ldy #$7f
.else
    bne SteveCopyCompanion
    ldy #$3f
    lda #0
.endif
SteveClearCompanion:
    sta $c900,y
    cmp $c900,y
    bne SteveCompanionCopyFailed
    dey
    bpl SteveClearCompanion
    lda #$40                         ; displaced incumbent bootstrap prefix
    sta $03
    jmp $a004
SteveCompanionCopyFailed:
    clc
    rts
