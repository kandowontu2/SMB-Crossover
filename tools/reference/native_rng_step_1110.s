.setcpu "6502"
.segment "RNG_STEP"

; Same seven-byte LFSR and feedback bit as the original GameLoop.
; Keep the caller's A, X, Y, flags and R0 at the continuation.
PseudoRandomBitReg = $07a0
R0 = $03

RngStep:
    lda PseudoRandomBitReg
    and #2
    sta R0
    eor PseudoRandomBitReg+1
    and #2
    cmp #1                      ; A is 0 or 2, so carry is the feedback bit.
    ror PseudoRandomBitReg
    ldx #1
    ldy #6
RotateRemaining:
    ror PseudoRandomBitReg,x
    inx
    dey
    bne RotateRemaining
    nop                         ; Preserve the following native farcall address.

.assert *-RngStep=$1d,error,"Keep the GameLoop continuation fixed"
