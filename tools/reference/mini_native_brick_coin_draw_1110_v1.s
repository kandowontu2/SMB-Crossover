.setcpu "6502"
.export StaticDraw, PrimeDeathDistance

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
GoombaCompare=$be9d
CoinFrame1Right=$ae
GroundBrickRight=$ec
DeathAge=$6009
DeathPose=$6011
DeathDistance=$600f
LegacyOuterLow=$ba37
LegacyOuterHigh=$bae0

.segment "DRAW_TAIL"
.proc StaticDraw
    ; The masked high-byte check admits only $ad and $af. The ordinary
    ; typed Goomba caller still starts directly at $bead.
    lda Ptr+1
    cmp #$af
    bne CheckStatic
    lda Ptr
    jmp GoombaCompare
CheckStatic:
    lda Ptr
    ldy #8
    cmp #GroundBrickRight
    beq Admit
    cmp #CoinFrame1Right
    beq CoinHeader
Fallback:
    jmp Generic
CoinHeader:
    ldy #4
Admit:
    lda YHigh
    eor #1
    ora XHigh
    bne Fallback
    tya
    clc
    adc Cursor
    bcs Fallback
    ldx Cursor
    lda RotationActive
    beq Dispatch
    txa
    ; The accepted capacity ADC left carry clear.
    adc Rotation
    tax
Dispatch:
    cpy #4
    beq Coin

    ; The exact right-facing ground-brick record is two identical
    ; parts at dx=0/8 and dy=0. Preserve reverse record and store order.
    ; CPY #4 set carry for both the two-sprite and one-sprite records.
    lda XLow
    adc #7
    bcs Fallback
    sta SpriteX,x
    lda YLow
    sta SpriteY,x
    lda Attr
    and #$f3
    tay
    sta SpriteAttr,x
    lda #$62
    sta SpriteTile,x
    inx
    inx
    inx
    inx
    lda XLow
    sta SpriteX,x
    lda YLow
    sta SpriteY,x
    tya
    sta SpriteAttr,x
    lda #$62
    bcc FinishPart

Coin:
    ; The exact first coin frame is one part at dx=0, dy=8.
    lda YLow
    adc #7
    bcs Fallback
    tay
    lda XLow
    sta SpriteX,x
    tya
    sta SpriteY,x
    lda Attr
    ora #2
    and #$f3
    sta SpriteAttr,x
    lda #$6c
FinishPart:
    sta SpriteTile,x
    inx
    inx
    inx
    inx
    clv
    jmp Finish
.endproc

.proc CalculateDeathDistance
    ; The foreground death loop keeps one age across its eight outer
    ; pieces. The next four inner pieces still set their own distance.
    cpy #169
    bcc InRange
    jmp LegacySpill
InRange:
    lda LegacyOuterLow,y
    sta DeathDistance
    tya
    asl
    lda #0
    rol
SaveHigh:
    sta DeathDistance+1
    rts
.endproc

.segment "DEATH_PRIME"
.proc PrimeDeathDistance
    sta DeathPose
    ldy DeathAge
    jmp CalculateDeathDistance
.endproc

.segment "DEATH_SPILL"
LegacySpill:
    ; Invalid outer-low indices read the old first 87 zero high-table
    ; bytes. Invalid outer-high indices read beyond the entire table.
    lda #0
    sta DeathDistance
    lda LegacyOuterHigh,y
    jmp CalculateDeathDistance::SaveHigh
