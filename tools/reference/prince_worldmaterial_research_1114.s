; Research only. Exact leased WorldMaterial envelope; not mounted gameplay.
; Symbols come from the independently authenticated current reconstruction.
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
 bmi AboveRow
 bne Ready
 lda $c618
 cmp #3
 beq Falling
 cmp #4
 bne Ready
Falling:
 lda ScanEnd
 cmp OldFoot
 lda ScanEnd+1
 sbc OldFoot+1
 bcc Ready
 lda OldFoot
 clc
 adc #15
 and #$f0
 sta ScanStart
 lda OldFoot+1
 adc #0
 sta ScanStart+1
 lda ScanEnd
 cmp ScanStart
 lda ScanEnd+1
 sbc ScanStart+1
 bcc NoBoundary
 inc Sweep
 bne Ready
NoBoundary:
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
 ; BestTop high is retired: a positive native point has Y high zero.
 ; Its owned byte instead records the current-row ordinary-body policy.
 lda $c618
 and #3
 cmp #2
 beq Unfiltered
 lda $c616
 cmp #10
 beq Unfiltered
 cmp #24
 beq Unfiltered
 lda Row
 cmp CurrentRow
 bne Unfiltered
 lda #1
 bne SetFilter
Unfiltered:
 lda #0
SetFilter:
 sta BestTop+1
 lda #$ff
 sta BestTop
Column:
 lda QueryFoot
 sec
 sbc #24
 sta PpQueryY
 lda QueryFoot+1
 sbc #0
 sta PpQueryY+1
 jsr Hand
 bcc WallDone
 lda BestTop+1
 beq WallFound
 jsr BodyCell
 bcc WallDone
WallFound:
 inc Wall
WallDone:
 lda ScanStart
 sta ScanY
 lda ScanStart+1
 sta ScanY+1
Scan:
 lda ScanEnd
 cmp ScanY
 lda ScanEnd+1
 sbc ScanY+1
 bcc NextColumn
 lda ScanY
 sta PpQueryY
 lda ScanY+1
 sta PpQueryY+1
 jsr PpHostReadPoint
 bcc AdvanceScan
 lda ScanY
 and #$f0
 sta Top
TopLoop:
 lda Top
 cmp #33
 bcc TopDone
 sec
 sbc #1
 sta PpQueryY
 ; PpQueryY high was zero at the positive native point.
 jsr PpHostReadPoint
 bcc TopDone
 lda Top
 sec
 sbc #16
 sta Top
 jmp TopLoop
TopDone:
 lda BestTop+1
 beq KeepTop
 lda Foot+1
 bne KeepTop
 lda Foot
 and #$f0
 cmp Top
 bcc KeepTop
 beq KeepTop
 ; A higher remote column is a floor only when the current native feet
 ; really have support at that height. PointRead preserves X and Y.
 ldx PpQueryX
 ldy PpQueryX+1
 lda $c60f
 sec
 sbc #6
 sta PpQueryX
 lda $c610
 sbc #0
 sta PpQueryX+1
 lda Top
 sta PpQueryY
 jsr PpHostReadPoint
 bcs RestoreProbe
 lda PpQueryX
 clc
 adc #11
 sta PpQueryX
 bcc SecondFoot
 inc PpQueryX+1
SecondFoot:
 jsr PpHostReadPoint
RestoreProbe:
 stx PpQueryX
 sty PpQueryX+1
 bcc NextColumn
KeepTop:
 lda Top
 cmp BestTop
 bcs Found
 sta BestTop
Found:
 inc Floor
 jmp NextColumn
AdvanceScan:
 lda ScanY
 and #$f0
 clc
 adc #16
 sta ScanY
 bcc Scan
 inc ScanY+1
 jmp Scan
NextColumn:
 dec ColumnCount
 beq Decide
 lda PpQueryX
 clc
 adc #16
 sta PpQueryX
 bcc Column
 inc PpQueryX+1
 jmp Column
Decide:
 lda Floor
 beq TestWall
 lda Sweep
 bne SolidFloor
TestWall:
 lda Wall
 beq TestFloor
 lda #20
 bne SaveMaterial
TestFloor:
 lda Floor
 beq SaveMaterial
SolidFloor:
 lda BestTop
 sta Baseline
 lda #0
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
BodyCell:
 ; Native sampled cell intersects sourceX-8 .. sourceX+7. The two-byte
 ; difference rejects page-distant cells rather than assuming 8-bit range.
 lda PpQueryX
 and #$f0
 sec
 sbc $c60f
 sta Top
 lda PpQueryX+1
 sbc $c610
 beq PositiveDistance
 cmp #$ff
 bne OutsideBody
 lda Top
 cmp #$e9
 rts
PositiveDistance:
 lda Top
 cmp #8
 bcs OutsideBody
 sec
 rts
OutsideBody:
 clc
 rts
