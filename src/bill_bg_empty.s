; Private W. This is an EMPTY-only BG consumer optimization, not a new
; source head getter. Original source top-epsilon floors are contained in
; [Y+min,Y+min+1], min={0,15,16}. X endpoints are contained in [X+1,X+15].
; For rows not crossing a tile boundary, column(X+1) and its successor are
; a conservative superset. Only literal zero tiles admit the shortcut.
; Any row seam/status-domain edge/nonzero byte uses the exact V9 consumer.
; R0/R5/R6/R7 are BG scratch; caller read-before-overwrite is audited apart
; from public raw/filtered getters. No actor/pickup/solid predicate changes.
.pushseg
.segment "LOWCODE"
.proc BillBGEmptyEnvelope
  ldx BillSourceBodyForm
  lda Player_Y_Position
  clc
  adc BillBGTopMin,x
  cmp #32
  bcc Fallback
  cmp #239
  bcs Fallback
  tay
  and #15
  cmp #15
  beq Fallback
  tya
  and #$f0
  sec
  sbc #32
  tay
  lda Player_X_Position
  clc
  adc #1
  sta R5
  lda Player_PageLoc
  adc #0
  and #1
  tax
  lda #>Block_Buffer_1
  sta R7
  lda R5
  lsr
  lsr
  lsr
  lsr
  clc
  adc BlockBufferAddr,x
  sta R6
  lda (R6),y
  bne Fallback
  ; The successor is deliberately checked even for a one-column source
  ; rectangle. A nonempty surplus cell merely falls back to the old code.
  lda R6
  and #15
  cmp #15
  bne NextColumn
  lda R6
  eor #$df ; buffer1 col15=$0f -> buffer2 col0=$d0, and vice versa.
  sta R6
  jmp ReadNext
NextColumn:
  inc R6
ReadNext:
  lda (R6),y
  bne Fallback
  lda #0
  sta BillHeadFiltering
  clv ; raw ReadCell's BIT filtering=0 has V=0 on the empty path.
  rts
Fallback:
  jmp BillBGHeadFallback
.endproc
.popseg

.pushseg
.segment "SAMUS_CROUCH_WATER"
; Background-only caller. Raw/filtered public head-query ABI is unchanged.
.proc BillBGHeadConsumer
  php
  pha
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  beq Bill
  pla
  plp
  jmp BillHeadConsumer
Bill:
  pla
  plp
  jmp BillBGEmptyEnvelope
.endproc
BillBGTopMin: .byte 0,15,16
BillBGHeadFallback:
  ldy Local_eb ; actual PlayerBGCollision source head-entry Y
  jmp BillHeadConsumer
.popseg
