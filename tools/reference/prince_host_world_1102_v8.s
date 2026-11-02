; Private source-world binding, no owner dispatch/menu admission.
; Original actor movement/control/contact instructions remain the caller.
.setcpu "6502"
.macpack longbranch
.export PpWorldTile,PpWorldTileY,PpWorldAlign,PpWorldPlaceAligned
.export PpWorldLandingAlign,PpWorldRoomAbove,PpWorldGateEmpty
.export PpWorldPhysicalFoot,PpWorldSourceContext,PpWorldSourceColumn
.export PpWorldBindingEnd

; All fields are within the source-proven dead prefix of exclusive RAM2.
PpRawQuery=$c078
PpBaseColumn=$c07a
Index=$c07b
Row=$c07c
CellX=$c07d
Surface=$c07f
SurfaceRow=$c081
RoomRows=$c082
CurrentRow=$c083
Foot=$c084
OldFoot=$c086
Delta=$c088
Origin=$c089
LastY=$c08b
Wall=$c08c
Floor=$c08d
Sweep=$c08e
ScanStart=$c08f
ScanEnd=$c091
ScanY=$c093
Top=$c095
BestTop=$c097
Offset=$c099
Baseline=$c09b
SavedX=$c09d
SavedY=$c09e
Material=$c09f
ColumnCount=$c0a0
AlignX=$c0a1
AlignY=$c0a2
FlagByte=$c0a3
QueryFoot=$c0a4
.export PpWorldRoomRows,PpWorldFoot,PpWorldOldFoot,PpWorldDelta
.export PpWorldOrigin,PpWorldLastY,PpWorldSurface,PpWorldSurfaceRow
PpWorldRoomRows=RoomRows
PpWorldFoot=Foot
PpWorldOldFoot=OldFoot
PpWorldDelta=Delta
PpWorldOrigin=Origin
PpWorldLastY=LastY
PpWorldSurface=Surface
PpWorldSurfaceRow=SurfaceRow

.segment "WORLD_EXTRA"
PpWorldSourceContext:
 php
 lda #0
 sta RoomRows
 plp
 jmp SourceWorldContext
PpWorldSourceColumn:
 php
 lda #0
 sta RoomRows
 plp
 jmp SourceWorldColumn
PpWorldRoomAbove:
 lda RoomRows
 sec
 sbc #3
 sta RoomRows
 lda #0
 rts
PpWorldGateEmpty:
 lda #0
 rts

; Track raw8bit source Y independently from native signed16 projection.
; A root/query can cross255 at the top or bottom without wrapping the screen.
PpWorldPhysicalFoot:
 lda $c611
 sec
 sbc LastY
 bmi NegativeStep
 bcs NoWrap
 inc Origin+1
 jmp NoWrap
NegativeStep:
 bcc NoWrap
 dec Origin+1
NoWrap:
 lda $c611
 sta LastY
 clc
 adc Origin
 sta Foot
 lda Origin+1
 adc #0
 sta Foot+1
 lda Delta
 bpl PositiveDelta
 dec Foot+1
PositiveDelta:
 clc
 adc Foot
 sta Foot
 bcc :+
 inc Foot+1
:
 rts

.segment "WORLD_GEOMETRY"
; Source index still uses its original30 cells. Preserve the complete raw
; predivision query so the source's clamp9 never clamps native world travel.
Cell:
 sta Index
 lda #0
 sta Row
 lda Index
Divide10:
 cmp #10
 bcc Remainder
 sbc #10
 inc Row
 bne Divide10
Remainder:
 sec
 sbc PpBaseColumn
 sta Offset
 ldx #0
 lda Offset
 bpl :+
 dex
:
 stx Offset+1
 ldx #5
ShiftColumn:
 asl Offset
 rol Offset+1
 dex
 bne ShiftColumn
 lda PpRawQuery
 and #$e0
 clc
 adc Offset
 sta CellX
 lda PpRawQuery+1
 adc Offset+1
 sta CellX+1
 lda Row
 clc
 adc RoomRows
 sta Row
 rts

Prepare:
 jsr Cell
 jsr PpWorldPhysicalFoot
 lda #29
 ldx $c616
 cpx #3
 beq Adjusted
 cpx #4
 beq Adjusted
 cpx #14
 bne :+
Adjusted:
 lda #36
:
 sta CurrentRow
 lda $c611
 sec
 sbc CurrentRow
 bcs :+
 lda #0
:
 lsr
 lsr
 lsr
 lsr
 lsr
 lsr
 sta CurrentRow
 lda Row
 sec
 sbc CurrentRow
 sta Offset
 ldx #0
 lda Offset
 bpl :+
 dex
:
 stx Offset+1
 ldx #6
ShiftRow:
 asl Offset
 rol Offset+1
 dex
 bne ShiftRow
 lda Foot
 clc
 adc Offset
 sta ScanStart
 sta ScanEnd
 sta QueryFoot
 lda Foot+1
 adc Offset+1
 sta ScanStart+1
 sta ScanEnd+1
 sta QueryFoot+1
 ; Wall/empty alignment keeps the source actor's current height. Only a
 ; genuine native floor substitutes a native surface in the original align.
 lda $c611
 clc
 adc Origin
 sta Baseline
 lda Origin+1
 adc #0
 sta Baseline+1
 lda Baseline
 clc
 adc Offset
 sta Baseline
 lda Baseline+1
 adc Offset+1
 sta Baseline+1
 lda Baseline
 clc
 adc #3
 sta Baseline
 bcc :+
 inc Baseline+1
:
 lda CellX
 clc
 adc #24
 sta PpQueryX
 lda CellX+1
 adc #0
 sta PpQueryX+1
 rts

.segment "WORLD_MATERIAL"
PpWorldTile:
 ldy $c4b1
PpWorldTileY:
 php
 stx SavedX
 sty SavedY
 tya
 jsr Prepare
 lda #0
 sta Wall
 sta Floor
 sta Sweep
 lda #2
 sta ColumnCount
 lda Row
 cmp CurrentRow
 bcc AboveRow
 bne Ready
 lda $c618
 cmp #3
 beq Falling
 cmp #4
 bne Ready
Falling:
 lda OldFoot+1
 cmp ScanEnd+1
 bcc StartSweep
 bne Ready
 lda OldFoot
 cmp ScanEnd
 bcc StartSweep
 beq StartSweep
 bcs Ready
StartSweep:
 lda #1
 sta Sweep
 lda OldFoot
 clc
 adc #15
 and #$f0
 sta ScanStart
 lda OldFoot+1
 adc #0
 sta ScanStart+1
 cmp ScanEnd+1
 bcc Ready
 bne NoBoundary
 lda ScanStart
 cmp ScanEnd
 bcc Ready
 beq Ready
NoBoundary:
 lda #0
 sta Sweep
 lda ScanEnd
 sta ScanStart
 lda ScanEnd+1
 sta ScanStart+1
 jmp Ready
AboveRow:
 lda ScanEnd
 clc
 adc #63
 sta ScanEnd
 bcc Ready
 inc ScanEnd+1
Ready:
 lda #$ff
 sta BestTop
 sta BestTop+1
Column:
 lda QueryFoot
 sec
 sbc #24
 sta PpQueryY
 lda QueryFoot+1
 sbc #0
 sta PpQueryY+1
 jsr PpHostReadPoint
 bcc :+
 inc Wall
:
 lda ScanStart
 sta ScanY
 lda ScanStart+1
 sta ScanY+1
Scan:
 lda ScanY+1
 cmp ScanEnd+1
 bcc InScan
 jne NextColumn
 lda ScanY
 cmp ScanEnd
 bcc InScan
 beq InScan
 jcs NextColumn
InScan:
 lda ScanY
 sta PpQueryY
 lda ScanY+1
 sta PpQueryY+1
 jsr PpHostReadPoint
 bcc AdvanceScan
 lda ScanY
 and #$f0
 sta Top
 lda ScanY+1
 sta Top+1
TopLoop:
 lda Top+1
 bne TopDone
 lda Top
 cmp #33
 bcc TopDone
 sec
 sbc #1
 sta PpQueryY
 lda #0
 sta PpQueryY+1
 jsr PpHostReadPoint
 bcc TopDone
 lda Top
 sec
 sbc #16
 sta Top
 jmp TopLoop
TopDone:
 lda Top+1
 cmp BestTop+1
 bcc BetterTop
 bne Found
 lda Top
 cmp BestTop
 bcs Found
BetterTop:
 lda Top
 sta BestTop
 lda Top+1
 sta BestTop+1
Found:
 inc Floor
 jmp NextColumn
AdvanceScan:
 lda ScanY
 and #$f0
 clc
 adc #16
 sta ScanY
 jcc Scan
 inc ScanY+1
 jmp Scan
NextColumn:
 dec ColumnCount
 beq Decide
 lda PpQueryX
 clc
 adc #16
 sta PpQueryX
 jcc Column
 inc PpQueryX+1
 jmp Column
Decide:
 lda Sweep
 beq TestWall
 lda Floor
 bne SolidFloor
TestWall:
 lda Wall
 beq TestFloor
 lda #20
 bne SaveMaterial
TestFloor:
 lda Floor
 bne SolidFloor
 lda #0
 beq SaveMaterial
SolidFloor:
 lda BestTop
 sta Baseline
 lda BestTop+1
 sta Baseline+1
 lda #1
SaveMaterial:
 sta Material
 lda Baseline
 sta Surface
 lda Baseline+1
 sta Surface+1
 lda Row
 sta SurfaceRow
 ldx SavedX
 ldy SavedY
 plp
 lda Material
 rts
PpWorldBindingEnd:

.segment "WORLD_ALIGN"
PpWorldAlign:
 tya
 ldx #64
PpWorldPlaceAligned:
 sta AlignX
 sta $c017
 stx AlignY
 stx $c018
 lda $c4b1
 jsr Cell
 lda CellX
 clc
 adc AlignX
 sta $c60f
 lda CellX+1
 adc #0
 sta $c610
 lda Row
 sec
 sbc SurfaceRow
 sec
 sbc #1
 asl
 asl
 asl
 asl
 asl
 asl
 clc
 adc Surface
 sec
 sbc Origin
 sec
 sbc #3
 clc
 adc AlignY
 sta $c611
 ; Preserve the original AE78 arithmetic C/V, while actual terrain has
 ; supplied the adapted coordinates. The map tail returns A=bank,Y=0,Z=1.
 lda Index
 ldx #0
OriginalRow:
 cmp #10
 bcc OriginalY
 sbc #10
 inx
 bne OriginalRow
OriginalY:
 txa
 lsr
 ror
 ror
 clc
 adc AlignY
 php
 lda $c615
 bne NoAlternate
 lda $c4fe
 beq NoAlternate
 plp
 lda $c60f
 sec
 sbc #30
 sta $c60f
 php
NoAlternate:
 lda Index
 asl
 adc Index
 tax
 ldy #0
 plp
 lda $c6d1
 jmp SourceWorldPrivateMap

.segment "WORLD_LANDING"
PpWorldLandingAlign:
 lda $c611,y
 sec
 sbc $c4e2
 sbc #8
 and #$c0
 clc
 adc #64
 php
 lda Surface
 sec
 sbc Origin
 sec
 sbc #3
 sta $c611,y
 plp
 lda $c611,y
 rts
