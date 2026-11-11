; D297's translated material provider returns only 0, 1 or $14. All
; three already pass through to D2BC. Reuse the unreachable branches for
; $11, $10, $02 and $0B while preserving the original reachable continuation.
.segment "DISPATCH"
    jmp $a71b
SupportAction:
    lda $c616
    beq Idle
    cmp #1
    beq Moving
    cmp #42
    bne ActionDone
Moving:
    lda $c618
    adc #0
    and #$fd
ActionDone:
    rts
Idle:
    lda $c617
    eor #15
    ora $c618
    rts

; Keep the original source tile result first. If it was empty, require the
; native grounded state, the same sole across updates and a solid exposed
; cell directly under Prince's facing foot. The logical fallback remains
; restricted to the original careful step.
.segment "SUPPORT"
Support:
    jsr $bde2
    bne Done
    php
    jsr SupportAction
    bne Empty
    lda $a4
    sec
    sbc #1
    ora $c085
    ora $c087
    ora $1e
    bne Empty
    lda $bd
    adc #32
    bcs Empty
    cmp $c084
    bne Logical
    cmp $c086
    beq Prepared
Logical:
    jsr $bd82
    bne Empty
Prepared:
    sbc #1
    sta $b36b
    lda #0
    sta $b36c
    lda $c615
    and #11
    adc #1
    adc $75
    sta $b369
    lda $5c
    adc #0
    sta $b36a
    jsr $b310
    bcc Empty
    cmp #$58
    beq Exposed
    cmp #$51
    beq Ordinary
    cmp #$57
    bne Pipe
Ordinary:
    lda $c616
    beq Exposed
Pipe:
    and #$fc
    cmp #$10
    bne Empty
Exposed:
    dec $b36b
    jsr $b310
    bcs Empty
    sta $c080
    lda $b36b
    adc #1
    sta $c07f
    plp
    lda #1
    rts
Empty:
    plp
    lda #0
Done:
    rts
