; Native platform positioning already committed. X is the actual platform slot.
; Keep the existing R0..7, RgTemp, registers and mapper-call frame.
.export Z2RefreshPlatformBody, Z2RefreshPlatformBodyEnd

R0 = $03
RgTemps = $6c63
Selected = $6002
Z2Variant = $73f8
RelativePlayerPosition = $8a8c
Z2OriginalBodyBox = $ab99
NextBank = $0162
FarTargetLo = $016c
FarTargetHi = $016d
FarCallCommon = $015a

.segment "CODE"
Z2RefreshPlatformBody:
    php
    pha
    txa
    pha
    tya
    pha
.ifdef ORIGINAL
    .repeat 8,I
        lda R0+I
        pha
    .endrepeat
    .repeat 3,I
        lda RgTemps+2+I
        pha
    .endrepeat
    lda RgTemps
    pha
    lda RgTemps+1
    pha
.else
    ldx #7
SaveScratch:
    lda R0,x
    pha
    dex
    bpl SaveScratch
    ldx #4
SaveTemps:
    lda RgTemps,x
    pha
    dex
    bpl SaveTemps
    tsx
    lda $010f,x                  ; actual native X, above thirteen byte saves
    tax
.endif
    lda Selected
    cmp #4
.ifdef ORIGINAL
    bne Restore
.else
    beq Link
    cmp #40
    bne Restore

    lda NextBank
    pha
    lda FarTargetLo
    pha
    lda FarTargetHi
    pha
    ; B029 translates the typed-only event to virtual public row37.
    ; The owner router verifies both full headers before private execution.
    lda #$29
    sta FarTargetLo
    lda #$b0
    sta FarTargetHi
    lda #$c1
    jsr FarCallCommon
    pla
    sta FarTargetHi
    pla
    sta FarTargetLo
    pla
    sta NextBank
    bne Restore                  ; real native platform farcall's bank tag is $c7
Link:
.endif
    lda Z2Variant
    beq Restore
    jsr RelativePlayerPosition
    jsr Z2OriginalBodyBox
Restore:
.ifdef ORIGINAL
    pla
    sta RgTemps+1
    pla
    sta RgTemps
    .repeat 3,I
        pla
        sta RgTemps+4-I
    .endrepeat
    .repeat 8,I
        pla
        sta R0+7-I
    .endrepeat
.else
    ldx #0
RestoreTemps:
    pla
    sta RgTemps,x
    inx
    cpx #5
    bcc RestoreTemps
    ldx #0
RestoreScratch:
    pla
    sta R0,x
    inx
    cpx #8
    bcc RestoreScratch
.endif
    pla
    tay
    pla
    tax
    pla
    plp
    rts
Z2RefreshPlatformBodyEnd:
    .assert *-Z2RefreshPlatformBody <= 119, error, "native post-position span"
    .res 119-(*-Z2RefreshPlatformBody), $ea
