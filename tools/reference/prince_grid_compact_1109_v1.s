; Source-owned RAM2 renderer compatibility for the compact 5-bit cell format.
; The old GridY BIT has already set V=1 only for this format. No new ZP.
.setcpu "6502"
.export ReadCell, ReadTile, ResetPair, CompactEnd

ReadCell:
 bvc Wide
 lda Pending
 bmi Second
 jsr Byte
 pha
 ora #$80
 sta Pending
 pla
 lsr a
 lsr a
 lsr a
 lsr a
 bpl HaveNibble
Second:
 and #$0f
 lsr Pending
HaveNibble:
 sta GridCell
 jsr Byte
 pha
 and #$fe
 sta TileOut
 pla
 and #1
 asl a
 asl a
 sta ExtraY
 lda GridCell
 and #$0c
 asl a
 asl a
 ora ExtraY
 sta ExtraY
 lda GridCell
 and #3
 ora ExtraY
 rts
ReadTile:
 bit GridFlag
 bvc Wide
 lda TileOut
 rts
Wide:
 jmp Byte
ResetPair:
 lda #0
 sta Pending
 jmp ReadProjection
Pending: .byte 0
TileOut: .byte 0
ExtraY: .byte 0
CompactEnd:
