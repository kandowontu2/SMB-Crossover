.setcpu "6502"

ProcessAreaData = $a314
BlockBufferColumnPos = $04a0
GetBlockBufferAddr = $95dc
MetatileBuffer = $04a1
MTileAttribute = $ef36
GuestTerrainColumn = $6871
SelectedCharacter = $6002
R0 = $03
BlockPointer = $09
BlockPage = $0a
Provenance = $0b
BrickHealth = $6051
CoinHits = $61f1
SolidTerrain = $66d1
SecondDelta = $d0
FarCallCommon = $015a
TargetLo = $016c
TargetHi = $016d

.segment "COLUMN"
.export StoreColumn
    jsr NativeThenVariant
StoreColumn:
    lda BlockBufferColumnPos
    jsr GetBlockBufferAddr
    ldx #0
    ldy #0
Row:
    sty R0
    ldy MetatileBuffer,x
    beq Tile
    lda MTileAttribute,y
    and #$3f
    beq Store
Tile:
    tya
Store:
    ldy R0
    sta (BlockPointer),y
    tya
    adc #$10
    tay
    inx
    cpx #13
    bcc Row
    ldy SelectedCharacter
    jmp ResetHealthColumn
    .res $30-(*-StoreColumn)-3,$ea

.macro TripleClear delta
    sta BrickHealth+delta,y
    sta CoinHits+delta,y
    sta SolidTerrain+delta,y
.endmacro

.segment "FIXED"
.export ResetHealthColumn, HealthProvenance
ResetHealthColumn:
    bne Guest
    tay
    cpx #13
    rts
Guest:
    lda BlockPointer
    and #$0f
    ora #$c0
    tay
    ldx #0
    sec
    txa
    bit BlockPointer
    bmi Lower
    jsr ClearFirst
    bcc HealthProvenance
Pair:
    txa
    TripleClear SecondDelta+$10
Lower:
    TripleClear SecondDelta
    tya
    sbc #$20
    tay
    bcs Pair

HealthProvenance:
    lda #<(SolidTerrain-$0300)
    adc BlockPointer
    sta Provenance
    lda #>(SolidTerrain-$0300)
    adc BlockPage
    sta Provenance+1
    ; StoreColumn's final STY left R0=$c0. Both clears already wrote zero to
    ; every provenance row, so only matching nonzero rows need another store.
    ldx #11
    ldy #$b0
Match:
    lda GuestTerrainColumn,x
    beq Next
    cmp MetatileBuffer,x
    bne Next
    lda #1
    sta (Provenance),y
Next:
    tya
    clc
    adc #$10
    tay
    inx
    cpx #13
    bcc Match
    rts
    .res $5c-(*-ResetHealthColumn),$ea

.segment "LEVEL"
.export ClearFirst, NativeThenVariant
ClearFirst:
    txa
    TripleClear 0
    tya
    sbc #$10
    tay
    bcs ClearFirst
    rts
    .assert *-ClearFirst=17,error,"Retain the native level tail bounds"
NativeThenVariant:
    jsr ProcessAreaData
    lda #$12
    sta TargetLo
    lda #$a0
    sta TargetHi
    lda #$9a
    jmp FarCallCommon
    .assert *-ClearFirst=35,error,"Retain the native level tail bounds"
