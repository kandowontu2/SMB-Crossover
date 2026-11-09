.setcpu "6502"
.export TypedGoomba, GoombaGeneric, GoombaReject, TypedGoombaEnd

Ptr=$03
Attr=$06
XLow=$07
XHigh=$08
YLow=$09
YHigh=$0a
Cursor=$06de
Rotation=$6c08
RotationActive=$6c0b
SpriteY=$0200
SpriteTile=$0201
SpriteAttr=$0202
SpriteX=$0203
Generic=$a5ba
Finish=$a65e

.segment "TYPED"
.org $bead
.proc TypedGoomba
    lda XHigh
    bne GoombaGeneric
    lda YHigh
    cmp #1
    bne GoombaGeneric
    lda YLow
    cmp #$f8
    bcs GoombaGeneric
    ; Both entries prove one of four immutable eight-byte descriptors.
    ldx Cursor
    lda #8
    jmp Capacity
ClipFirst:
    ; The legacy loop writes the wrapped X, then hides only this part.
    lda #$f8
    sta SpriteY,x
    jmp Next
    .res $bece-*, $ea
::GoombaGeneric:
    jmp Generic
Capacity:
    adc Cursor                 ; accepted Y comparison left carry clear
    bcs GoombaReject
    lda RotationActive
    beq First
    txa
    adc Rotation               ; accepted capacity also left carry clear
    tax
First:
    lda XLow
    clc
    adc #8
    sta SpriteX,x
    bcs ClipFirst
    lda YLow
    adc #8                     ; the first X addition did not wrap
    sta SpriteY,x
    ldy #6
    lda (Ptr),y
    ora Attr
    and #$f3
    sta SpriteAttr,x
    dey
    lda (Ptr),y
    sta SpriteTile,x
Next:
    inx
    inx
    inx
    inx
    lda XLow
    sta SpriteX,x
    lda YLow
    clc                        ; the first clipped X may have set carry
    adc #8
    sta SpriteY,x
    ldy #2
    lda (Ptr),y
    ora Attr
    and #$f3
    sta SpriteAttr,x
    dey
    lda (Ptr),y
    sta SpriteTile,x
    inx
    inx
    inx
    inx
    clv
    jmp Finish
    .res $bf2d-*, $ea
::GoombaReject:
    ldy #0
    lda #8
    clc
    rts
.endproc
TypedGoombaEnd:
.reloc
