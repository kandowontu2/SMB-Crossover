.setcpu "6502"
.export GiantDraw, GiantFirstPublishDone, GiantDrawEnd

; One owner code row in physical RAM3, accompanied by the immutable
; 13-pose table at RAM2:D000. Caller has already rendered native actors.
; A = donor pose, X = native world's saved nonrotated OAM tail.
; R0..R4/R6/R7 and the code row's A380..A397 scratch are volatile.

.segment "GIANT_RENDER"

Cursor = $a380
Pose = $a381
BaseX = $a382
GridX = $a384
StepX = $a388
Row = $a38d
ColumnMask = $a38e
ColumnX = $a390
GridY = R6
Attrib = R3
RowTile = R4
Mask = R2

GiantDraw:
    cmp #13
    bcs Rejected
    cpx #16
    bcc Rejected                 ; native full/wrapped cursor is zero
    sta Pose
    stx Cursor
    lda SelectedCharacter
    bne Rejected
    lda MarioVariant
    cmp #9
    bne Rejected
    lda OperMode
    cmp #1
    bne Rejected
    lda GameEngineSubroutine
    cmp #8
    bne Rejected
    lda CurrentBankC
    cmp #2
    bne Rejected
    lda GuestOamRotationActive
    bne Rejected
    lda ObjectMetasprite
    beq Rejected                 ; preserve native injury flicker
    ldx #15
Authenticate:
    lda $d000,x
    cmp GiantAtlasCookie,x
    bne Rejected
    dex
    bpl Authenticate
    bmi Ready
Rejected:
    clc
    rts
Ready:
    lda Pose
    asl
    asl
    clc
    adc Pose
    asl
    adc #16
    sta R0
    lda #$d0
    sta R1
    ldy #0
    lda (R0),y
    ldy #6
    jsr Publish
GiantFirstPublishDone:
    ldy #1
    lda (R0),y
    ldy #7
    jsr Publish

    lda #$f8
    sta $0200
    sta $0204
    sta $0208
    sta $020c
    lda Player_X_Position
    sec
    sbc ScreenLeft_X_Pos
    sta BaseX
    lda Player_PageLoc
    sbc ScreenLeft_PageLoc
    sta BaseX+1
    lda Player_Y_Position
    sec
    sbc #96
    sta GridY
    lda Player_Y_HighPos
    sbc #1
    sta GridY+1
    lda Player_SprAttrib
    sta Attrib
    lda PlayerFacingDir
    and #2
    bne Left
    lda #8
    sta StepX
    lda #0
    sta StepX+1
    lda BaseX
    sec
    sbc #24
    sta BaseX
    lda BaseX+1
    sbc #0
    jmp SetBase
Left:
    lda Attrib
    ora #$40
    sta Attrib
    lda #$f8
    sta StepX
    lda #$ff
    sta StepX+1
    lda BaseX
    clc
    adc #32
    sta BaseX
    lda BaseX+1
    adc #0
SetBase:
    sta BaseX+1
    sta GridX+1
    lda BaseX
    sta GridX
    lda #0
    sta ColumnMask
    ldx #0
PrepareColumn:
    lda GridX
    sta ColumnX,x
    lda GridX+1
    beq ColumnVisible
    clc
    bcc RecordColumn
ColumnVisible:
    sec
RecordColumn:
    ror ColumnMask
    lda GridX
    clc
    adc StepX
    sta GridX
    lda GridX+1
    adc StepX+1
    sta GridX+1
    inx
    cpx #8
    bcc PrepareColumn
    ldx Cursor
    lda #$81                     ; odd 8x16 tile, sprite windows 6 and 7
    sta RowTile
    lda #2
    sta Row
DrawRow:
    ldy Row
    lda (R0),y
    and ColumnMask
    beq AdvanceRow
    sta Mask
    lda GridY+1
    bne AdvanceRow
    lda GridY
    cmp #$f0
    bcs AdvanceRow
    ldy #0
DrawCell:
    lsr Mask
    bcc NextCell
    lda GridY
    sta $0200,x
    tya
    asl
    ora RowTile
    sta $0201,x
    lda Attrib
    sta $0202,x
    lda ColumnX,y
    sta $0203,x
    inx
    inx
    inx
    inx
    beq Complete                 ; preserve 64-entry OAM capacity
NextCell:
    iny
    lda Mask
    bne DrawCell
AdvanceRow:
    lda GridY
    clc
    adc #16
    sta GridY
    bcc :+
    inc GridY+1
:
    lda RowTile
    clc
    adc #16
    sta RowTile
    inc Row
    lda Row
    cmp #10
    bcc DrawRow
Complete:
    sec
    rts

Publish:
    sta $016a
    lda #<X5SetPhysicalChr
    sta $016c
    lda #>X5SetPhysicalChr
    sta $016d
    ldx #0
    lda #$be
    jmp $015a

GiantAtlasCookie:
    .byte GIANT_ATLAS_SIGNATURE
GiantDrawEnd:
.assert GiantDrawEnd <= $a380, lderror, "Giant draw exceeds its code row"
