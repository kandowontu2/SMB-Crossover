.setcpu "6502"

; The native owner already grants this complete source-program span.
; Keep the original EB75 entry and EBE3 predicate address. The original
; virtual pointer conversion is shared, not replaced by a native pointer.
.segment "RECT"
DkRectCommon:
    sta $c00f
    txa
    pha
    tya
    pha
    ldy #0
    lda $c00f
    cmp #2
    beq RectList
    asl a
    asl a
    tax
RectBuild:
    jsr RectDouble
    lda $c00f
    beq RectRestore
    jsr RectPredicate
RectResult:
    sta $c00f
RectRestore:
    pla
    tay
    pla
    tax
    lda $c00f
    rts
RectList:
    ldx #$fc
RectField:
    jsr RectRead
    cpx #$fc
    bne RectStore
    cmp #$ff
    beq RectEmpty
RectStore:
    sta $bf46,x ; X=FC..FF writes C042..45, in original order.
    iny
    inx
    bne RectField
    jsr RectPredicate
    beq RectList
    jmp RectResult
RectEmpty:
    lda #0
    beq RectResult
RectDouble:
    jsr RectPair
RectPair:
    jsr RectRead
    clc
    adc $c000
    sta $c03e,x
    inx
    iny
    jsr RectRead
    clc
    adc $c001
    sta $c03e,x
    inx
    iny
    rts
RectRead:
    php
    pha
    lda $c002
    sta RectReadCell+1
    lda $c003
    cmp #8
    bcs RectReadROM
    ora #$c0
RectReadROM:
    sta RectReadCell+2
    pla
    plp
RectReadCell:
    lda $ffff,y
    rts
DkRectCompactEnd:

; Only original D608 reaches this service, after its jumping-only wall
; rectangle accepted a contact. Require the top edge, entered from below.
; An ordinary side wall, foot/platform or projectile cannot queue this.
DkAcceptHead:
    php
    lda $c8da
    beq HeadCaptureEnd
    lda $c045
    sec
    sbc $c03f
    cmp #2
    bcs HeadCaptureEnd
    lda $c045
    cmp $c076
    bcs HeadCaptureEnd
    lda $c042
    clc
    adc ScreenLeftX
    sta HeadX
    lda ScreenLeftPage
    adc #0
    sta HeadPage
    lda $c043
    sta HeadTop
HeadCaptureEnd:
    plp
    rts

; Called within the same Main, after donor movement and before returning
; to the native background collision loop. Consume before any native call.
; The actual contacted cell is read again. Nonbump ceilings keep the donor
; response; native timer/noninteractive guards retain their native meaning.
DkHeadFlush:
    lda HeadTop
    beq HeadReturn
    ldy #0
    sty HeadTop
    sec
    sbc #32
    sta R2
    lda HeadX
    lsr a
    lsr a
    lsr a
    lsr a
    sta R6
    lda HeadPage
    lsr a
    bcc HeadBuffer
    lda R6
    ora #$d0
    sta R6
HeadBuffer:
    lda #3
    sta R7
    ldy R2
    lda (R6),y
    tax
    lda MTileAttribute,x
    and #7
    cmp #1
    bne HeadReturn
    lda BlockBounceTimer
    ora GuestHurtTicks
    ora TimerControl
    bne HeadReturn
    stx SafecallA
    lda #<NativeHeadEffect
    sta FarTarget
    lda #>NativeHeadEffect
    sta FarTarget+1
    lda #NativeHeadBank
    jmp FarCall
DkHeadCodeEnd:

.segment "SCORE"
DkScoreFlush:
    php
    pha
    txa
    pha
    tya
    pha
    lda ScoreAmount
    ora HeadTop
    beq AwardReturn
    ldx #7
AwardSaveScratch:
    lda R0,x
    sta $c460,x
    dex
    bpl AwardSaveScratch
    lda ObjectOffset
    sta $c489
    ldx #32
AwardSaveSMC:
    lda $015a,x
    sta $c468,x
    dex
    bpl AwardSaveSMC
    jsr DkHeadFlush
    ldx #5
    lda #0
AwardClearDigits:
    sta DigitModifier,x
    dex
    bpl AwardClearDigits
    lda ScoreAmount
    and #$0f
    sta DigitModifier+4
    lda ScoreAmount
    lsr a
    lsr a
    lsr a
    lsr a
    sta DigitModifier+3
    lda #0
    sta ScoreAmount
    jsr NativeAddScore
    ldx #0
AwardRestoreSMC:
    lda $c468,x
    sta $015a,x
    inx
    cpx #33
    bne AwardRestoreSMC
    lda $c489
    sta ObjectOffset
    ldx #0
AwardRestoreScratch:
    lda $c460,x
    sta R0,x
    inx
    cpx #8
    bne AwardRestoreScratch
AwardReturn:
    pla
    tay
    pla
    tax
    pla
    plp
    rts
OriginalFall:
    lda #4
    sta $c06b
    rts
DkScoreBridgeEnd:

.segment "HEAD_HOOK"
    jsr DkAcceptHead
    jmp OriginalFall
