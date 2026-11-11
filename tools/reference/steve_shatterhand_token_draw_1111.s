.setcpu "6502"

.segment "ITEM_SELECT"
    lda InvPickup,x
    and #$7f
    tay
    cpy #12
    bcc NativeItem
    lda $730b
    and #$60
    cmp #$40
    beq NextWorldItem
NativeItem:
    lda $c04e,y
    sta $03
    lda $c05c,y
    sta $04

.segment "TOKEN_DRAW"
SteveDrawWorldToken:
    jsr SteveTokenOwned
    bcc WorldDone
    lda Enemy_State,x
    cmp #2
    bcc WorldDone
    ; The admitted CMP set carry. A zero page difference sets it again.
    lda Enemy_X_Position,x
    sbc ScreenLeft_X_Pos
    sta $07
    lda Enemy_PageLoc,x
    sbc ScreenLeft_PageLoc
    bne WorldDone
    lda Enemy_Y_Position,x
    adc #7
    sta $09
    lda InvPickup,x
    and #1
    jmp SteveDrawTokenPair
WorldDone:
    rts
SteveDrawTokenFlight:
    lda SteveTokenPending
    beq Done
    eor SteveTokenPattern
    beq Done
LocateSymbol:
    cmp #4
    bcc DrawFlight
    lsr a
    lsr a
    bne LocateSymbol
DrawFlight:
    lsr a
    ldx SteveTokenFlightX
    stx $07
    ldx SteveTokenFlightY
    stx $09
SteveDrawTokenPair:
    ldx #<Alpha
    lsr a
    bcc PairPointer
    ldx #<Beta
PairPointer:
    stx $03
    lda #>Alpha
    sta $04
    lda #0
    sta $08
    sta $06
    sta $016a
    lda #1
    sta $0a
    lda #<NativeRender
    sta $016c
    lda #>NativeRender
    sta $016d
    jmp SteveDrawInvoke
Done:
    rts
Alpha:
    .byte 8,$31,2,0,0,$33,2,0,8
Beta:
    .byte 8,$35,2,0,0,$37,2,0,8

.segment "DRAW_SCAN"
SteveDrawTokens:
    lda SteveTokenStamp
    beq AllWorldDone
    ldx #5
WorldSlot:
    txa
    pha
    jsr SteveDrawWorldToken
    pla
    tax
    dex
    bpl WorldSlot
AllWorldDone:
    jmp SteveDrawTokenFlight
