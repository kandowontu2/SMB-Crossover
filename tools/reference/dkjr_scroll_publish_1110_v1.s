; Owner40 publishes the native scroll witness before its unchanged source step.
; The signed terrain helpers retain the same logic and exact column entry.
.export DkScrollPublish, DkScrollPublishEnd, DkWorldRow

WKind = $c8db
WTop = $c8ea
WBottom = $c8eb
WLeft = $c8e8
WRight = $c8e9
WX = $c8de
WPage = $c8df
WY = $c8e2
WEndY = $c8e3
WEndX = $c8e0
WEndPage = $c8e1
PlayerX = $75
PlayerPage = $5c
CameraX = $071f
CameraPage = $071d
PlayerPosForScroll = $075a
InvalidWindow = $b49c
EmptyWindow = $b4a4
DkWorldEndPage = $d2d5
DkPauseMain = $d540

.segment "CAMERA"
DkScrollPublish:
    ; The actual DkNativeMain successful anchor gate supplies C=1.
    ; PauseMain's first LDA overwrites A. Preserve the incoming P, X and Y.
    php
    lda PlayerX
    sbc CameraX
    pha
    lda PlayerPage
    sbc CameraPage
    beq InRange
    asl
    pla
    lda #0
    sbc #0
    bvc Publish                 ; zero minus carry/borrow cannot overflow
InRange:
    pla
Publish:
    sta PlayerPosForScroll
    plp
    jmp DkPauseMain
DkScrollPublishEnd:
    .assert *-DkScrollPublish = 30, error, "DK metadata before cold boot"

.segment "WORLD"
    .ifdef ORIGINAL
      ldx WKind
    .endif
    ; X is still the WKind loaded before the width comparison.
    cpx #3
    bne OrdinaryY
    clc
    adc #1
    sta WTop
    adc #1
    sta WBottom
OrdinaryY:
    .ifdef ORIGINAL
      lda WBottom
    .endif
    ; Both predecessors already leave WBottom in A.
    sec
    sbc WTop
    cmp #17
    bcc HeightOK
    jmp InvalidWindow
HeightOK:
    lda WTop
    cmp #240
    bcc ClipTop
    jmp EmptyWindow
ClipTop:
    cmp #32
    bcs AlignTop
    lda #32
AlignTop:
    and #$f0
    sta WY
    lda WBottom
    cmp #32
    bcs ClipBottom
    jmp EmptyWindow
ClipBottom:
    cmp #240
    bcc AlignBottom
    lda #239
AlignBottom:
    and #$f0
    sta WEndY
    lda WRight
    clc
    adc CameraX
    and #$f0
    sta WEndX
    lda CameraPage
    adc #0
    jsr DkWorldEndPage
DkWorldRow:
    lda WLeft
    clc
    adc CameraX
    and #$f0
    sta WX
    .ifdef ORIGINAL
      jsr $d240
      nop
      nop
    .else
      lda WEndX
      cmp WX
      lda WEndPage
      sbc #0
    .endif
    sta WPage
