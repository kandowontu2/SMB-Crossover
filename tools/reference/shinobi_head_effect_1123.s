; Extend the cached Shinobi host worker with an SMB block-bump transaction.
; The original pair of upper probes still governs the source jump response.

ShPendingTile = $c811
ShPendingColumn = $c812
ShPendingRow = $c813
ShSourceBlockRow = $c004
ShSourceBlockColumn = $c006
ShSourceQueryTile = $c804
ShSourceQueryClass = $c805
ShSourceDirection = $c3fd
ShDrawBits = $c810
ShCountDown = $b3ba

.segment "SHINOBI_QUERY"
.export ShNativeQuery, ShBeginFrame
ShNativeQuery:
    txa
    pha
    lda R3
    bne QueryOutside
    lda R2
    cmp #32
    bcc QueryOutside
    cmp #240
    bcs QueryOutside
    ; The upper-bound comparison leaves carry clear: subtract 31 plus borrow.
    sbc #31
    sta $c009
    and #$f0
    sta ShSourceBlockRow
    lsr
    and #$f0
    sta $c005
    lda R0
    clc
    adc ScreenLeft_X_Pos
    sta ShSourceBlockColumn
    sta $c00a
    lda R1
    adc ScreenLeft_PageLoc
    ; Shift page parity and pixel X together into the native column index.
    lsr
    lda ShSourceBlockColumn
    ror
    lsr
    lsr
    lsr
    cmp #$10
    bcc ColumnReady
    adc #$bf                     ; carry adds the remaining byte of $c0
ColumnReady:
    sta R6
    lda #>Block_Buffer_1
    sta R7
    ldy ShSourceBlockRow
    lda (R6),y
    sta ShSourceQueryTile
    tax
    lda MTileAttribute,x
    and #3
    cmp #1
    beq QuerySolid
    lda #0
    beq QueryReturn
QuerySolid:
    lda #1
    sta $c007
    sta $c008
    bne QueryReturn
QueryOutside:
    lda #$ff
QueryReturn:
    sta ShSourceQueryClass
    pla
    tax
    lda ShSourceQueryClass
    rts

ShBeginFrame:
    sta ShDrawBits
    sta ShPendingTile
    rts

.segment "SHINOBI_KERNEL"
.export ShUpperProbe, ShAfterSource
ShUpperProbe:
    jsr ShNativeQuery
    php
    cmp #1
    bne ProbeDone
    txa
    bne ProbeDone
    lda ShSourceDirection
    and #$0c
    cmp #4
    bne ProbeDone
    lda ShPendingTile
    bne ProbeDone
    ldx ShSourceQueryTile
    lda MTileAttribute,x
    and #4                      ; Hard terrain uses the original solid response.
    bne ProbeRestoreX
    stx ShPendingTile
    lda R6
    sta ShPendingColumn
    sty ShPendingRow
ProbeRestoreX:
    ldx #0
ProbeDone:
    lda ShSourceQueryClass
    plp
    rts

ShAfterSource:
    jsr ShCountDown
    ldx ShPendingTile
    beq NoBump
    lda AreaType
    beq NoBump
    lda BlockBounceTimer
    ora GuestHurtTicks
    bne NoBump
    lda ShPendingRow
    sta R2
    lda ShPendingColumn
    sta R6
    lda #>Block_Buffer_1
    sta R7
    txa
    jmp PlayerHeadCollision
NoBump:
    rts
