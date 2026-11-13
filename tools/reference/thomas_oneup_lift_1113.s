; Thomas's eighth native vertical platform, below the authored hidden 1UP.
.setcpu "6502"

.segment "LIFT_REFS"
    lda ThomasLiftLo,y
    sec
    sbc ScreenLeft_X_Pos
    sta R0
    lda ThomasLiftHi,y
    sbc ScreenLeft_PageLoc
    bmi ThomasLiftMark
    cmp #1
    bcc ThomasLiftMark
    bne ThomasLiftNext
    lda R0
    cmp #32
    bcs ThomasLiftNext

.segment "SEEN_REF"
    and ThomasLiftBits,y

.segment "CONSTRUCT_REFS"
    lda ThomasLiftLo,y
    sta Enemy_X_Position,x
    lda ThomasLiftHi,y
    sta Enemy_PageLoc,x

.segment "PUBLISH_REF"
    ora ThomasLiftBits,y

.segment "MARK_REF"
    ora ThomasLiftBits,y

.segment "LIMIT"
    cpy #8

.segment "LIFT_TABLE"
ThomasLiftLo:
    .byte $90,$30,$b0,$60,$00,$00,$b0,$f0
ThomasLiftHi:
    .byte $01,$02,$02,$03,$0a,$0b,$04,$03
ThomasLiftBits:
    .byte $01,$02,$04,$08,$10,$20,$40,$80
