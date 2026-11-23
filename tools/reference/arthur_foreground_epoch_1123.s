.setcpu "6502"

FrameCounter = $0e
GameEngineSubroutine = $0f
NmiDisable = $0139
ValidatedFrame = $bfdf
LiveHeader = $bfe0
OriginalHeader = $dc6e
RestoreBank = $c7d7

.segment "AUTH"
    ; Row 29 is called before the game update increments FrameCounter.
    ; Retire the previous update's stamp even when gameplay is paused.
    cpy #29
    bne CheckMain
    lda #0
    sta ValidatedFrame
    beq FullCheck
CheckMain:
    lda $01fa
    cmp #$83
    bne FullCheck
    lda $01f9
    cmp #$52
    bne FullCheck
    lda NmiDisable
    bpl FullCheck
    lda GameEngineSubroutine
    cmp #8
    bne FullCheck
    lda FrameCounter
    beq FullCheck
    cmp ValidatedFrame
    bne FullCheck
    lda LiveHeader
    cmp #$a7
    bne FullCheck
    lda LiveHeader+1
    cmp #32
    bne FullCheck
Cached:
    jmp RestoreBank

FullCheck:
    ; The original prefix at C7B9 has already compared bytes 14 and 15.
    tya
    pha
    ldy #13
CheckByte:
    lda LiveHeader,y
    cmp OriginalHeader,y
    bne Invalid
    dey
    bpl CheckByte
    pla
    tay
    cpy #0
    bne Accepted
    lda FrameCounter
    sta ValidatedFrame
Accepted:
    jmp RestoreBank
Invalid:
    pla
    tay
    lda #0
    sta ValidatedFrame
    clc
    jmp RestoreBank
