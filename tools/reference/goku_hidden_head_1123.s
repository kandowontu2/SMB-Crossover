; Goku's native terrain query and hidden-block admission for the two head probes.
; These segments occupy the existing query and its former tile-read helper.
DpAction = $5c00
DpVertical = $5c07
DpTileIndex = $5c22
DpTileResult = $5c23
DpProbeY = $5c24
DpProbeX = $5c25
DpProbePage = $5c26
DpSavedR0 = $5c27
DpSavedR1 = $5c28
DpMath = $5c30
R0 = $03
R1 = $04
R6 = $09
R7 = $0a
ScreenLeft_PageLoc = $071d
ScreenLeft_X_Pos = $071f
GetBlockBufferAddr = $95dc
MTileAttribute = $ef36
FoundationOffset = $63d1

.segment "QUERY"
DpHostTileQuery:
  cmp #$f0
  bcc Query
  lda #1
  rts
Query:
  sty DpMath+2
  sta DpMath+3
  and #$f0
  sta R1
  tya
  lsr
  lsr
  lsr
  lsr
  ora R1
  sta DpTileIndex
  php
  txa
  pha
  lda R0
  sta DpSavedR0
  lda R1
  sta DpSavedR1
  lda DpMath+3
  cmp #32
  bcc Empty
  and #$f0
  sbc #32
  sta DpProbeY
  lda ScreenLeft_X_Pos
  clc
  adc DpMath+2
  sta DpProbeX
  lda ScreenLeft_PageLoc
  adc #0
  sta DpProbePage
  ; Shift the nine-bit (page parity, pixel X) coordinate to a tile column.
  lsr
  lda DpProbeX
  ror
  lsr
  lsr
  lsr
  jsr GetBlockBufferAddr
  ldy DpProbeY
  lda (R6),y
  beq Empty
  cmp #$23
  bcc Attribute
  cmp #$27
  bcc Empty
  cmp #$51
  beq Brick
  cmp #$52
  beq Foundation
  cmp #$55
  bcc Attribute
  cmp #$5f
  bcc Brick
  cmp #$61
  bcs :+
  jmp HiddenHead
:
  cmp #$c0
  bcc Attribute
  cmp #$c2
  bcc Brick
  cmp #$c4
  bcc Empty
Attribute:
  tay
  lda MTileAttribute,y
  and #1
  beq Empty
Solid:
  lda #$75
  bne Result
Foundation:
  clc
  lda R6
  adc #<FoundationOffset
  sta R6
  lda R7
  adc #>FoundationOffset
  sta R7
  lda (R6),y
  bne Solid
Brick:
  lda #$95
  bne Result
Empty:
  lda #0
Result:
  sta DpTileResult
  lda DpSavedR0
  sta R0
  lda DpSavedR1
  sta R1
  pla
  tax
  plp
  ldy DpTileIndex
  lda DpTileResult
  rts

.segment "HIDDEN"
HiddenHead:
  ; Only a rising normal jump can publish the original head-block command.
  lda DpAction
  lsr
  cmp #1
  bne PassThrough
  lda DpVertical
  bpl PassThrough
  tsx
  ; The query has saved P and X. The second stacked return identifies the
  ; head sensor ($AF48) or the head-block producer ($AA2E). The build checks
  ; the signatures against every caller. A side probe shares the low byte.
  lda $0105,x
  eor $0106,x
  cmp #$e8                     ; $AF xor $47
  beq HeadContact
  cmp #$87                     ; $AA xor $2D
  bne PassThrough
HeadContact:
  jmp Brick
PassThrough:
  jmp Empty
