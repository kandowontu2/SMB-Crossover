PrinceReverseLedge:
 ; At a wrapping donor column, the second query can read an unrelated floor.
 ; Keep the original branch unless the native right lip and its headroom agree.
 php
 txa
 pha
 tya
 pha
 lda $c615                   ; The original right-facing clearance path is valid.
 jne Original
 lda $c616
 cmp #28                    ; Original standing Up action.
 jne Original
 lda $c40a
 and #8
 jeq Original
 lda Player_Y_HighPos
 cmp #1
 jne Original
 lda $c085
 jne Original
 lda $c60f                   ; Source center to the left hand's point.
 sec
 sbc #15
 tay
 lda $c610
 sbc #0
 bcs TileOnMap
 jmp Original
TileOnMap:
 sta CapPage
 tya
 and #$f0
 sta CapColumn
 ora #15
 cmp ScreenLeft_X_Pos
 lda CapPage
 sbc ScreenLeft_PageLoc
 bcs TileInView
 jmp Original
TileInView:
 jsr ColumnAddress
 lda $c084
 and #$f0
 sec
 sbc #48                    ; First sample, one tile above the feet, in buffer rows.
 bcc Original
 tay
 ldx #4                     ; The tallest native pipe is four tiles high.
FindCap:
 jsr ReadTile
 cmp #$11
 beq Cap
 cmp #$13
 beq Cap
 tya
 sec
 sbc #16
 bcc Original
 tay
 dex
 bne FindCap
 beq Original
Cap:
 sty CapRow
 jsr CeilingClear
 bcs Original
 lda CapColumn
 clc
 adc #16
 sta CapColumn
 lda CapPage
 adc #0
 bcs Original
 sta CapPage
 jsr ColumnAddress
 ldy CapRow
 jsr SolidTile               ; Check the exposed edge and the space for the body.
 bcs Original
 jsr CeilingClear
 bcs Original
 pla
 tay
 pla
 tax
 plp
 lda #0
 beq ChooseContinuation

Original:
 pla
 tay
 pla
 tax
 plp
 lda #$e5
 sta $016c
 lda #$bd
 sta $016d
 lda #3
 jsr $015a                  ; The original second WorldMaterial result.
ChooseContinuation:
 sta $016a                  ; Preserve the result expected by the resumed branch.
 beq ClearPath
 lda #$b6
 bne Resume
ClearPath:
 lda #$2f
Resume:
 sta $016c
 lda #$a5
 sta $016d
 lda #3
 jmp $015a

ColumnAddress:
 lda CapPage
 and #1
 tax
 lda CapColumn
 lsr
 lsr
 lsr
 lsr
 clc
 adc BlockBufferAddr,x
 sta ReadTileOperand
 rts

CeilingClear:
 tya
 sec
 sbc #16
 bcc Blocked
 tay
 jsr SolidTile
 bcs Blocked
 tya
 sec
 sbc #16
 bcc Blocked
 tay
SolidTile:
 jsr ReadTile
 tax
 lda MTileAttribute,x
 lsr
 rts
Blocked:
 sec
 rts

ReadTile:
 lda $03ff,y
 rts

CapColumn:
