; Rendering preference survives actor/area/inventory resets, until power/reset.
.pushseg
.segment "SRAM"
PlayerOutlinesOff: .res 1
CrossoverOptionsFocus: .res 1
OutlineBytesLeft: .res 1
OutlinePoseBuffer: .res 129
OutlineSourceLo: .res 1
OutlineSourceHi: .res 1
OutlineSourceBank: .res 1
; Four small immutable poses share the existing129-byte output reservation.
; Larger/mutable poses invalidate these keys and use the original full buffer.
OutlineTinyLo: .res 4
OutlineTinyHi: .res 4
OutlineTinyBank: .res 4
OutlineTinyNext: .res 1
OutlineTinyLast: .res 1
OutlineTinyOffset: .res 1

.segment "SAMUS"
.proc PlayerRemoveOutlines
  ldy #0
  lda (R0),y
  beq Invalid
  cmp #129
  bcs Invalid
  and #3
  beq Valid
Invalid:
  rts
Valid:
  lda (R0),y
  sta OutlineBytesLeft
  ; A long immutable pose can still use the original single full-buffer cache.
  lda R0+1
  cmp #$c0
  jcc Uncached
  cmp #$e0
  jcs Uncached
  cmp OutlineSourceHi
  bne Tiny
  lda R0
  cmp OutlineSourceLo
  bne Tiny
  lda CurrentBankC
  cmp OutlineSourceBank
  jeq UseBuffer
Tiny:
  ; Repeated standing poses check their last slot first. Animation cycles can
  ; reuse three other poses instead of rebuilding the mask on every change.
  ldx OutlineTinyLast
  jsr Match
  jeq TinyUse
  ldx #3
Find:
  jsr Match
  jeq TinyUse
  dex
  bpl Find
  lda #0
  sta OutlineSourceHi
  ldx OutlineTinyNext
  txa
  clc
  adc #1
  and #3
  sta OutlineTinyNext
  lda #0
  sta OutlineTinyHi,x          ; Evict before overwriting its output bytes.
  stx OutlineTinyLast
  txa
  asl
  asl
  asl
  asl
  asl
  sta OutlineTinyOffset
  tax
  ldy #1
SmallPart:
  iny
  lda (R0),y
  and #4
  bne SmallSkip
  txa
  sec
  sbc OutlineTinyOffset
  cmp #28                     ; Seven sprites plus header fit in32 bytes.
  bcs Overflow
  dey
  .repeat 4
    lda (R0),y
    sta OutlinePoseBuffer+1,x
    inx
    iny
  .endrepeat
  jmp SmallNext
SmallSkip:
  iny
  iny
  iny
SmallNext:
  lda OutlineBytesLeft
  sec
  sbc #4
  sta OutlineBytesLeft
  bne SmallPart
  txa
  sec
  sbc OutlineTinyOffset
  ldx OutlineTinyOffset
  sta OutlinePoseBuffer,x
  ldx OutlineTinyLast
  lda R0
  sta OutlineTinyLo,x
  lda CurrentBankC
  sta OutlineTinyBank,x
  lda R0+1
  sta OutlineTinyHi,x
TinyUse:
  stx OutlineTinyLast
  txa
  asl
  asl
  asl
  asl
  asl
  clc
  adc #<OutlinePoseBuffer
  sta R0
  lda #>OutlinePoseBuffer
  adc #0
  sta R1
  rts
Match:
  lda OutlineTinyHi,x
  beq Miss
  cmp R0+1
  bne Miss
  lda OutlineTinyLo,x
  cmp R0
  bne Miss
  lda OutlineTinyBank,x
  cmp CurrentBankC
  rts
Miss:
  lda #1                      ; Z clear for an invalid or different key.
  rts
Overflow:
  ; R0/R1 still name immutable ROM. Restart from its original header, after
  ; invalidating every output slot that the full result may overwrite.
  jsr InvalidateTiny
  ldy #0
  lda (R0),y
  sta OutlineBytesLeft
Remember:
  lda R0
  sta OutlineSourceLo
  lda R0+1
  sta OutlineSourceHi
  lda CurrentBankC
  sta OutlineSourceBank
  jmp Filter
Uncached:
  lda #0
  sta OutlineSourceHi
  jsr InvalidateTiny
Filter:
  ldx #0
  ldy #1
Part:
  iny                           ; Attribute follows the tile number.
  lda (R0),y
  and #4                        ; Only explicitly tagged extra black masks.
  bne Skip
  dey
  .repeat 4
    lda (R0),y
    sta OutlinePoseBuffer+1,x
    inx
    iny
  .endrepeat
  jmp Next
Skip:
  iny
  iny
  iny
Next:
  lda OutlineBytesLeft
  sec
  sbc #4
  sta OutlineBytesLeft
  bne Part
  stx OutlinePoseBuffer
UseBuffer:
  lda #<OutlinePoseBuffer
  sta R0
  lda #>OutlinePoseBuffer
  sta R1
Done:
  rts
InvalidateTiny:
  lda #0
  ldx #3
Clear:
  sta OutlineTinyHi,x
  dex
  bpl Clear
  rts
.endproc
.include "player_outline_flags.inc"
.popseg
