.setcpu "6502"

.segment "SOURCE"
    ; The world provider returns only 0, 1, or $14. Preserve the old
    ; zero/nonzero branch and use its impossible material cases for Hand.
    cmp #0
    beq NoLedge
    jmp TryLedge
Hand:
    jsr ReadPoint
    ; A=$25 implies that ReadPoint returned C=1. EOR leaves its original
    ; carry intact for other metatiles and the A=0/C=0 empty result.
    eor #$25
    bne HandDone
    lda $c616
    sbc #3
    cmp #2
HandDone:
    rts

.segment "NATIVE"
    ; The caller already rejected empty. Keep the native upper-side
    ; exclusions and use its own pole column and four-pixel contact window.
    cmp #$1c
    beq Lower
    cmp #$6b
    beq Lower
    tay
    lda MTileAttribute,y
    and #2
    beq Upper
    cpy #$25
    bne Lower
    jmp Flag
Upper:
    tya
    rts
Lower:
    lda #0
    rts
Normalize:
    lda #9
    sta $07
    jmp Upper

.segment "FLAG"
Flag:
    lda SelectedCharacter
    cmp #38
    bne Lower
    lda GameEngineSubroutine
    cmp #8
    bne Lower
    lda $07
    cmp #6
    bcc Lower
    cmp #10
    bcc Upper
    ; R6 names the actual shaft column, as in PutPlayerOnVine. A narrow
    ; sample that skipped past the pole can still have a real overlap
    ; between its center and Prince's 16-pixel body.
    lda $09
    asl a
    asl a
    asl a
    asl a
    ora #8
    sec
    sbc $75
    cmp #17
    bcs Lower
    jmp Normalize

.segment "CALLER"
    beq LowerSide
    sta $016a
    lda #$6d
    sta $016c
    lda #$b1
    sta $016d
    lda #$d2
    jsr $015a
    bne CheckSide
