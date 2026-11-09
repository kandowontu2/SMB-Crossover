.setcpu "6502"
.export InnerAtAge, GirderDraw, GoombaLowDispatch, WorkerEnd

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
TypedGoomba=$bead
GenericGate=$bece
DeathAge=$6009
DeathDistance=$600f
InnerTable=$b98e

.segment "WORKER"
.proc InnerAtAge
    cpy #169
    bcs LegacySpill
    cpy #19
    bcc Initial
    ; 5 + (age - 18) + floor((age - 18) / 4).
    tya
    sec
    sbc #18
    lsr
    lsr
    clc
    adc DeathAge
    sec
    sbc #13
    clc
    rts
Initial:
    lda #5
    rts
LegacySpill:
    ; Indices169..255 address the original OuterDistanceLo prefix.
    lda InnerTable,y
    clc
    rts
.endproc

.proc GoombaLowDispatch
    cmp #$2f
    beq Known
    cmp #$38
    beq Known
    cmp #$41
    beq Known
    cmp #$4a
    bne Other
Known:
    jmp TypedGoomba
Other:
    jmp GenericGate
.endproc

.proc GirderDraw
    ; The linked right and left tables share these two $B3 records.
    ; Both contain four tile-$5A, attr-2, dy-0 parts, with distinct dx order.
    lda Ptr
    cmp #$29
    beq Height
    cmp #$3a
    bne Fallback
Height:
    lda YHigh
    cmp #1
    bne Fallback
    lda #16
    clc
    adc Cursor
    bcs Fallback
    ldx Cursor
    lda RotationActive
    beq Begin
    txa
    adc Rotation                ; accepted capacity check left C clear
    tax
Begin:
    ldy #16
Part:
    lda (Ptr),y                 ; native reverse order, including rotated pose
    clc
    adc XLow
    sta SpriteX,x
    lda XHigh
    adc #0
    bne Clip
    lda YLow
    sta SpriteY,x
    lda Attr
    ora #2
    and #$f3
    sta SpriteAttr,x
    lda #$5a
    sta SpriteTile,x
    clv                         ; the original visible dy=0 high add clears V
Advance:
    inx
    inx
    inx
    inx
    dey
    dey
    dey
    dey
    bne Part
    jmp Finish
Clip:
    lda #$f8
    sta SpriteY,x
    bne Advance                 ; preserve V from the same high-coordinate ADC
Fallback:
    jmp Generic
.endproc
WorkerEnd:

.segment "DISPATCH"
.org $be92
    lda Ptr+1
    cmp #$b3
    beq Girder
    and #$fd
    cmp #$ad
    bne GenericGate
    jmp $bae0
Girder:
    jmp GirderDraw
    .res $bead-*, $ea           ; native typed-Goomba direct entry is fixed
.reloc

.segment "DEATH"
.org $b8d0
    ldy DeathAge
    cpx #3
    bne $b8ed                   ; unchanged eight outer and remaining inner draws
    jsr InnerAtAge               ; first inner draw owns all four inner distances
    sta DeathDistance
    lda #0
    sta DeathDistance+1
    beq $b8ed
.reloc
