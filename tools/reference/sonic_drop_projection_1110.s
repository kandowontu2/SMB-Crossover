.setcpu "6502"
.segment "DROP_DRAW"

DrawDrop:
    lda DropRecord
    cmp #$55
    bne DropDone
    lda DropFlags
    lsr a
    bcc DropDone
    lda DropRecord+6
    bne DropDone
    lda DropRecord+5
    cmp #33
    bcc DropDone
    cmp #225
    bcs DropDone
    sec
    sbc #1
    sta DrawFlip
    lda DropRecord+2
    sec
    sbc ScreenLeft_X_Pos
    tay
    lda DropRecord+3
    sbc ScreenLeft_PageLoc
    bne DropDone
    cpy #241
    bcs DropDone

    ; NES drawing can sample only even SMS ticks. Alternate on actual draws
    ; while leaving the original type-$55 sprite pointer and timer intact.
    lda DropFlags
    eor #$80
    sta DropFlags
    bpl DropDone

    ; The donor selects art before advancing the pose on a timer reload.
    ldx DropRecord+18
    lda DropRecord+17
    cmp #6
    bne Art
    dex
    bpl Art
    ldx #5
Art:
    txa
    asl a
    tax
    lda drops+1,x
    sta DrawAttr
    lda drops,x
    jmp EmitPair
DropDone:
    rts
