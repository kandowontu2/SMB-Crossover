; Research only. Exact leased WorldMaterial envelope; not mounted gameplay.
; Symbols come from the independently authenticated current reconstruction.
PpWorldTile:
 ldy $c4b1
PpWorldTileY:
 php
 txa
 pha
 tya
 pha
 jsr Prepare
 lda #0
 sta Wall
 sta Sweep
 sta BestTop+1
 lda Row
 cmp CurrentRow
 bmi AboveRow
 bne Ready
 ; Only normal current-row queries need the physical-body refinement.
 lda $c618
 and #3
 cmp #2
 beq Ready
 lda $c616
 cmp #10
 beq FallingMode
 cmp #24
 beq FallingMode
 inc BestTop+1
FallingMode:
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
 ; The admitted unsigned comparison supplies C1: ADC14 rounds by15.
 adc #14
 and #$f0
 tax
 lda OldFoot+1
 adc #0
 tay
 cpy ScanEnd+1
 bcc UseSweep
 bne Ready
 cpx ScanEnd
 bcc UseSweep
 bne Ready
UseSweep:
 stx ScanStart
 sty ScanStart+1
 inc Sweep
 bne Ready
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
 ; CellStart+8 cannot overflow its low byte. Its full-width difference
 ; from sourceX must lie in -15..15 for the two physical spans to overlap.
 lda PpQueryX
 and #$f0
 ; Hand's positive result still supplies C1: ADC7 adds8.
 adc #7
 sec
 sbc $c60f
 tax
 lda PpQueryX+1
 sbc $c610
 beq PositiveDistance
 cmp #$ff
 bne WallDone
 cpx #$f1
 bcc WallDone
 bcs WallFound
PositiveDistance:
 cpx #16
 bcs WallDone
WallFound:
 inc Wall
WallDone:
 ; Native PointRead/Hand preserve X/Y. Retire private ScanY memory and
 ; carry the scan position in registers until a floor has been found.
 ldx ScanStart
 ldy ScanStart+1
Scan:
 cpy ScanEnd+1
 bcc InScan
 bne NextColumn
 cpx ScanEnd
 bcc InScan
 bne NextColumn
InScan:
 stx PpQueryY
 sty PpQueryY+1
 jsr PpHostReadPoint
 bcc AdvanceScan
 txa
 and #$f0
 sta Top
TopLoop:
 cmp #33
 bcc TopDone
 ; CMP33 supplies C1, and a positive PointRead supplies it below.
 sbc #1
 sta PpQueryY
 ; PpQueryY high was zero at the positive native point.
 jsr PpHostReadPoint
 bcc TopDone
 lda Top
 sbc #16
 sta Top
 jmp TopLoop
TopDone:
 lda BestTop+1
 beq KeepTop
 lda Foot+1
 bne KeepTop
 lda Top
 ora #15
 cmp Foot
 bcs KeepTop
 ; A higher remote column is a floor only when the current native feet
 ; really have support at that height. PointRead preserves X and Y.
 ldx PpQueryX
 ldy PpQueryX+1
 lda $c60f
 ; The higher-top comparison supplied C0: SBC5 subtracts6.
 sbc #5
 sta PpQueryX
 lda $c610
 sbc #0
 sta PpQueryX+1
 lda Top
 sta PpQueryY
 jsr PpHostReadPoint
 bcs RestoreProbe
 lda PpQueryX
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
 jmp NextColumn
AdvanceScan:
 txa
 and #$f0
 ; The empty PointRead supplied C0.
 adc #16
 tax
 bcc Scan
 iny
 jmp Scan
NextColumn:
 ; Prepare's Cell is 32px aligned: the original two samples have low
 ; bits24 then8. Bit4 therefore replaces the private column counter.
 lda PpQueryX
 and #16
 beq Decide
 lda PpQueryX
 clc
 adc #16
 sta PpQueryX
 bcc Column
 inc PpQueryX+1
 jmp Column
Decide:
 ; BestTop=$FF means no native floor; all positive tops are32..224.
 lda BestTop
 eor #$ff
 beq TestWall
 lda Sweep
 bne SolidFloor
TestWall:
 lda Wall
 beq TestFloor
 lda #20
 bne SaveMaterial
TestFloor:
 lda BestTop
 eor #$ff
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
 pla
 tay
 pla
 tax
 plp
 lda Material
 rts
