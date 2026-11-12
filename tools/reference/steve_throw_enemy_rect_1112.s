; X is the native enemy slot. Build the unclipped world rectangle using
; the same control table as BoundingBoxCore. Native Y includes page 1.
; Output uses the same $8000 bias as SteveThrowOverlap; X is preserved.
.setcpu "6502"
.segment "ENEMY_RECT"
SteveThrowEnemyRect:
    lda Enemy_BoundBoxCtrl,x
    asl a
    asl a
    tay
    lda Enemy_X_Position,x
    clc
    adc BoundBoxCtrlData,y
    sta ThrowLow
    lda Enemy_PageLoc,x
    adc #0
    eor #$80
    sta ThrowLow+1
    lda Enemy_X_Position,x
    clc
    adc BoundBoxCtrlData+2,y
    sta ThrowHigh
    lda Enemy_PageLoc,x
    adc #0
    eor #$80
    sta ThrowHigh+1
    lda Enemy_Y_Position,x
    clc
    adc BoundBoxCtrlData+1,y
    sta ThrowLow+2
    lda Enemy_Y_HighPos,x
    adc #0
    eor #$80
    sta ThrowLow+3
    lda Enemy_Y_Position,x
    clc
    adc BoundBoxCtrlData+3,y
    sta ThrowHigh+2
    lda Enemy_Y_HighPos,x
    adc #0
    eor #$80
    sta ThrowHigh+3
    rts

; Caller has already packed the robot's world center in ThrowPoint.
; Preserve the native enemy slot across the axis worker, which uses X.
SteveThrowEnemyOverlap:
    txa
    pha
    jsr SteveThrowEnemyRect
    jsr SteveThrowOverlap
    pla
    tax
    rts
