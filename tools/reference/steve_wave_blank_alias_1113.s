; Excitebike's existing source-owned EX_HOST/CODE gap, after its18B powerup tick.
; Saved public ExHostGraphics frame is already on stack; retain its continuation.
.segment "BLANK_ALIAS"
ExBodyBlankAlias:
 ldx #3
ExBodyBlankLoop:
 lda ExBodyLow,x
 sta CurrentCHRBank4,x
 lda ExBodyBlankModes,x
 sta X5ChrMode4,x
 dex
 bpl ExBodyBlankLoop
 jmp ExGraphicsAfterLoop
ExBodyBlankModes:
 .byte $82,$82,$82,$80

