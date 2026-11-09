.setcpu "6502"
.export ResetHealthColumn, ClearSecond, HealthProvenance

R0 = $03
R6 = $09
R7 = $0a
M0 = $0b
M1 = $0c
MetatileBuffer = $04a1
GuestTerrainColumn = $6871
BlockBuffer1 = $0300
BlockBuffer2 = $03d0
BrickHealth = $6051
CoinHits = $61f1
SolidTerrain = $66d1
SecondDelta = BlockBuffer2-BlockBuffer1

; X=0, Y=$c0|column, C=1. The absolute bases are the three original
; shadows at the selected native block-buffer page. No pointer is borrowed.
.macro ClearRows delta
@row:
    txa
    sta BrickHealth+delta,y
    sta CoinHits+delta,y
    sta SolidTerrain+delta,y
    tya
    sbc #$10
    tay
    bcs @row
.endmacro

.segment "FIXED"
ResetHealthColumn:
    bne Guest
    tay
    cpx #13
    rts

Guest:
    ; Native parser writes BlockBufferColumnPos in 0..31. GetBlockBufferAddr
    ; therefore produced R7=3 and R6=$00..0f or $d0..df before this entry.
    lda R6
    and #$0f
    ora #$c0
    tay
    ldx #0
    sec
    lda R6
    bmi Page2
    ClearRows 0
    bcc HealthProvenance
Page2:
    jsr ClearSecond

HealthProvenance:
    ; The last row subtract has C=0, just as in the old dual clear.
    lda #<(SolidTerrain-BlockBuffer1)
    adc R6
    sta M0
    lda #>(SolidTerrain-BlockBuffer1)
    adc R7
    sta M1
    lda #$c0
    sta R0

    ; Only these two rows can be true native terrain. All other provenance
    ; cells are already zero. Match the final native pointer and AXYP.
    ldx #11
    ldy #$b0
@row:
    lda GuestTerrainColumn,x
    beq @write
    cmp MetatileBuffer,x
    bne @absent
    lda #1
    bne @write
@absent:
    lda #0
@write:
    sta (M0),y
    tya
    clc
    adc #$10
    tay
    inx
    cpx #13
    bcc @row
    rts
    .res 92-(*-ResetHealthColumn),$ea

.segment "LEVEL"
ClearSecond:
    ClearRows SecondDelta
    rts
    .res 18-(*-ClearSecond),$ea
