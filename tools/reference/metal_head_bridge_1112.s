; Head-only event: original B798 is reached after a successful head sweep.
; X=0 is normal gravity; source72 is the actual pre-snap query Y.
; C/V are dead before original SEC/SBC after the replaced LDA source5B.
; No new RAM: alias only the existing native packet C880..C887 until HuHead.
.setcpu "6502"

.segment "CAPTURE"
MsHeadCapture:
    txa
    bne MsHeadCaptureDone
    lda $c570
    bpl MsHeadCaptureDone
    sta $c886
    lda FrameCounter
    sta $c881
    lda $c811
    sta $c882
    jmp MsHeadCaptureTail
MsHeadCaptureDone:
    lda $c05b
    rts

.segment "CAPTURE_TAIL"
MsHeadCaptureTail:
    lda $c072
    sta $c883
    lda $c05a
    lsr a
    lda $c812
    bcc MsHeadCellReady
    ora #$d0
MsHeadCellReady:
    sta $c884
    lda $c059
    sta $c885
    lda Player_Y_Position
    sta $c887
    lda #$a7
    sta $c880
    jmp MsHeadCaptureDone

; The sole production caller immediately restores original actor AXYP from
; its own frame. Its save-point helper's A/X/P are dead at this boundary.
.segment "SAVE_POINT"
MsHeadSavePoint:
    lsr $c880
    lda $c480
    sta $c807
    lda $c498
    sta $c808
    jsr MsHostReadY
    sta $c809
    stx $c80a
    rts
MsHeadScene:
    lda GameEngineSubroutine
    cmp #$08
    rts

.segment "GETTER"
MsHeadGetter:
    lda $c880
    cmp $c800
    bne MsHeadNoEvent
    eor #$a7
    bne MsHeadNoEvent
    sta $c880
    jsr MsHeadScene
    bne MsHeadNoEvent
    lda $c881
    cmp FrameCounter
    bne MsHeadNoEvent
    lda $c887
    and #$0f
    cmp #$04
    bcc MsHeadNoEvent
    sta R4
    lda $c884
    sta R6
    lda #>Block_Buffer_1
    sta R7
    lda $c883
    and #$f0
    sec
    sbc #$20
    sta R2
    tay
    lda (R6),y
    cmp $c882
    bne MsHeadNoEvent
    sta R3
    lda $c885
    sta R5
    lda $c886
    sta Player_Y_Speed
    sec
    rts
MsHeadNoEvent:
    clc
    rts

; Callable through the selected owner's native head route. The Core has
; already stored incoming A in SafecallA; the inner full-header transport
; preserves original X/Y/I/D and publishes only result carry plus BG scratch.
.segment "ROM_GATE"
MsHeadRomGate:
    ; Our BF8B entry has the same low byte as authenticated row10 AB8B.
    ; Leave that byte intact; only change its mapped high byte.
    lda #>MsHeadTypedRow
    sta $016d
    lda #$ce
    jsr $015a
    bcc MsHeadNative
    ; Accepted source row is in0..C0 and C1. ADC/SBC's paired borrow
    ; reconstructs the native row SBC's exact C/V without changing R2.
    lda R2
    adc #$20
    sbc #$20
    ldx #$00
    lda R3
    rts
MsHeadNative:
    jmp BlockBufferColli_Head

; The only copy caller follows successful Ms8Zero, whose X is exactly0.
; Both existing Map farcalls are identical. Their common helper also supplies
; the two original LDX4 instructions. Successful CMP12 already leaves C1.
.segment "COPY"
MsHeadColdCopy:
    stx R2
MsHeadColdRow:
    jsr MsHeadColdMap
MsHeadColdPage:
    lda $2007
    sta (R0),y
    iny
    bne MsHeadColdPage
    inc R1
    dex
    bne MsHeadColdPage
    jsr MsHeadColdMap
MsHeadColdVerify:
    lda $2007
    cmp (R0),y
    bne MsHeadColdNo
    iny
    bne MsHeadColdVerify
    inc R1
    dex
    bne MsHeadColdVerify
    inc R2
    lda R2
    cmp #12
    bne MsHeadColdRow
    rts
MsHeadColdNo:
    clc
    rts
MsHeadColdMap:
    sta $016a
    lda #<Ms8Map
    sta $016c
    lda #>Ms8Map
    sta $016d
    lda #$a2
    jsr $015a
    ldx #4
    rts
