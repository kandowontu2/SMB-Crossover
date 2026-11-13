; Original CancelUpwardVelocity is reached only after an upward head probe
; blocked. The source query owns the exact native tile row and column.
.setcpu "6502"

.segment "REDIRECT"
    jmp JayHeadEffect
    nop
    nop
    nop

.segment "BRIDGE"
JayHeadEffect:
    txa
    pha
    ; TXA changes only the N/Z flags that the original final LDA #0 replaces.
    ; Save all other original status flags as well as both live registers.
    php
    tya
    pha
    jsr JayHeadAllowed
    bne Done
    ; The original resolver reuses QueryY for the decoded tile class after
    ; JayHostTile returns. Y retains its existing packed query index.
    tya
    lsr a
    lsr a
    lsr a
    sec
    sbc #2
    asl a
    asl a
    asl a
    asl a
    sta R2
    lda QueryX
    and #31
    jsr GetBlockBufferAddr
    jsr JayHeadCall
Done:
    pla
    tay
    plp
    pla
    tax
    lda #0
    jmp JayCancelReturn

.segment "FILTER"
JayHeadAllowed:
    ldx AreaType
    dex
    bmi FilterReturn
    lda QueryStatus
    ora BlockBounceTimer
    ora GuestHurtTicks
    bne FilterReturn
    lda QueryAttributes
    and #7
    eor #1
FilterReturn:
    rts

.segment "HEAD_CALL"
JayHeadCall:
    lda QueryTile
    sta R3
    jmp PlayerHeadCollision

.segment "CANCEL_RETURN"
JayCancelReturn:
    sta DonorVY
    rts
