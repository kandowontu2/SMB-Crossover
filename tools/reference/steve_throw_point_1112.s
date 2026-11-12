; Convert the robot's wrapping Q4 coordinates to the native world rectangle
; convention. X is reconstructed within +/-2048 pixels of the camera; callers
; must admit a visible robot. Y is signed screen Q4 plus native page 1.
.setcpu "6502"
.segment "THROW_POINT"
SteveThrowWorldPoint:
    lda ScreenLeft_X_Pos
    sta ThrowPoint
    lda ScreenLeft_PageLoc
    sta ThrowPoint+1
    ldx #4
ThrowPointCamera:
    asl ThrowPoint
    rol ThrowPoint+1
    dex
    bne ThrowPointCamera
    sec
    lda SteveBotX
    sbc ThrowPoint
    sta ThrowPoint
    lda SteveBotX+1
    sbc ThrowPoint+1
    sta ThrowPoint+1
    lda SteveBotY
    sta ThrowPoint+2
    lda SteveBotY+1
    sta ThrowPoint+3
    ldx #4
ThrowPointPixels:
    lda ThrowPoint+1
    cmp #$80
    ror ThrowPoint+1
    ror ThrowPoint
    lda ThrowPoint+3
    cmp #$80
    ror ThrowPoint+3
    ror ThrowPoint+2
    dex
    bne ThrowPointPixels
    clc
    lda ThrowPoint
    adc ScreenLeft_X_Pos
    sta ThrowPoint
    lda ThrowPoint+1
    adc ScreenLeft_PageLoc
    eor #$80
    sta ThrowPoint+1
    inc ThrowPoint+3
    lda ThrowPoint+3
    eor #$80
    sta ThrowPoint+3
    rts
