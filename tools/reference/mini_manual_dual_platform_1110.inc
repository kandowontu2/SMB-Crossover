MiniAssistState=$c30e
MiniHorizontalState=$c30f
.export MiniManualInput,MiniManualDispatch

; Filled into the space recovered from the four-byte head-cache copies.
.macro MiniManualDispatchBody
MiniManualInput:
MiniManualDispatch:
    lda SavedJoypadBits
    sta MiniHeld
    and #$2c
    cmp #$24
    beq @chord
    cmp #$28
    bne @pending
@chord:
    tay
    eor MiniPrevious
    and #$2c
    beq @pending
    cpy #$28
    bcc @horizontal
@vertical:
    lda #0
    pha
    ldx #$41
    ldy #$f4
    bne @call
@pending:
    lda MiniAssistState
    bmi @vertical
    lda MiniHorizontalState
    bpl @done
@horizontal:
    lda #1
    pha
    ldx #$42
    ldy #20
    lda PlayerFacingDir
    cmp #2
    bne @call
    ldy #$d4
@call:
    lda #<$b378
    sta MiniNativeTarget+1
    jsr MiniManualHigh
    pla
    tay
    txa
    sta MiniAssistState,y
@done:
    rts
.endmacro
