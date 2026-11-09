.setcpu "6502"
.segment "WORKER"
.export NormalEnemyOffscreenBits, WorkerEnd

; Preserve the public native/SMB2 ABI and both independent camera edge
; comparisons. Use the original right-edge high nibbles for 0..23 pixels.
NormalEnemyOffscreenBits:
    cpx #6
    bcs Native
    lda $a5,x
    cmp #1
    bne Native
    lda $be,x
    cmp #32
    bcc Native
    cmp #224
    bcs Native

    sec
    lda $76,x
    sbc $071f
    tay
    lda $5d,x
    sbc $071d
    bne Native
    tya
    beq Native

    sec
    lda $0720
    sbc $76,x
    tay
    lda $071e
    sbc $5d,x
    bne Native
    cpy #24
    bcs Publish                 ; A is zero from the matching high bytes.
    tya
    lsr
    lsr
    lsr
    tay
    lda $8b67,y                 ; fixed native [$07,$03,$01] lookup.

Publish:
    sta $05a1
    sta $03
    inx
    stx $07
    lda $bd,x                   ; same enemy Y, via the sprite-object index.
    eor #$ff
    sta $0a
    lda #4
    sta $08
    lda #32
    sta $09
    lda $03
    ldy #1
    clc
    clv
    ldx $0d
    rts
Native:
    jmp $8ae9
WorkerEnd:
