; Proposed authenticated row16 body box. Assembly/CPU design only.
; The donor pose's original six-offset rectangle is the authority.
.segment "SHINOBI_KERNEL"
.export ShFullBox
ShFullBox:
 php
 pha
 txa
 pha
 tya
 pha
 .repeat 8,I
 lda R0+I
 pha
 .endrepeat
 ; Native scroll has advanced since source movement. Import current viewport
 ; only for the box transaction; preserve the source renderer's state.
 lda $c379
 pha
 lda $c384
 pha
 lda $c38f
 pha
 lda $c39a
 pha
 jsr ShImportPosition
 ldx #0
 jsr ShSourceBounds
 ; PLA/STA preserve the returned carry while restoring the four actor bytes.
 pla
 sta $c39a
 pla
 sta $c38f
 pla
 sta $c384
 pla
 sta $c379
 bcc ShFullBoxHidden
 lda $c009
 bne ShFullBoxHidden
 lda $c008
 sta BoundingBox_UL_Corner
 lda $c00b
 beq ShFullBoxRightByte
 lda #$ff
 bne ShFullBoxRightReady
ShFullBoxRightByte:
 lda $c00a
ShFullBoxRightReady:
 sta BoundingBox_LR_Corner
 ; Translate the donor +32 feet alignment in sixteen bits, then clip the
 ; actually visible native viewport rather than wrapping negative Y to224.
 lda $c00c
 sec
 sbc #32
 sta BoundingBox_UL_Corner+1
 lda $c00d
 sbc #0
 bmi ShFullBoxTopZero
 bne ShFullBoxHidden
 beq ShFullBoxBottom
ShFullBoxTopZero:
 lda #0
 sta BoundingBox_UL_Corner+1
ShFullBoxBottom:
 lda $c00e
 sec
 sbc #32
 sta BoundingBox_LR_Corner+1
 lda $c00f
 sbc #0
 bmi ShFullBoxHidden
 beq ShFullBoxDone
 lda #$ff
 sta BoundingBox_LR_Corner+1
 bne ShFullBoxDone
ShFullBoxHidden:
 lda #$ff
 sta BoundingBox_UL_Corner
 sta BoundingBox_UL_Corner+1
 sta BoundingBox_LR_Corner
 sta BoundingBox_LR_Corner+1
ShFullBoxDone:
 .repeat 8,I
 pla
 sta R0+7-I
 .endrepeat
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts
