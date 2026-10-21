; Source HitTester.checkLastHitPoints direct-below normal-flat branch.
; Strict prior horizontal interior is a direct head contact. Either prior
; horizontal corner uses calcAxis(false,rightCorner): zero vx chooses the
; side, zero vy chooses the head, otherwise verticalPen<=horizontalPen.
; The native terrain pass resolves that final axis without Flash's deferred
; Ground-list scheduling. Input is the actual queried cell and source caches.
; Preserve R2/R3/R4/R6/R7, SmTemp, RgTemp2 and query X/page for native effects.
.pushseg
.segment "SOPHIA_TERRAIN_COLD"
.proc SophiaHeadSourceAxis
  lda RgTempX
  and #$f0
  sta SmHeadX
  lda RgTempPage
  sta SmHeadPage

  ; floor(priorRight) = oldX+17+carry(xf>=.5).
  lda RyWallOldXFrac
  cmp #$80
  lda RyWallOldX
  adc #17
  sta SmTempX
  lda RyWallOldPage
  adc #0
  cmp SmHeadPage
  jcc CornerRight
  bne CheckLeft
  lda SmTempX
  cmp SmHeadX
  jcc CornerRight
  bne CheckLeft
  lda RyWallOldXFrac
  eor #$80
  ora RyWallOldXFine
  jeq CornerRight             ; exact right==left remains a corner.

CheckLeft:
  ; floor(priorLeft) = oldX-2+carry(xf>=.5).
  lda RyWallOldXFrac
  cmp #$80
  lda RyWallOldX
  sbc #1
  sta SmTempX
  lda RyWallOldPage
  sbc #0
  sta SmTempPage
  clc
  lda SmHeadX
  adc #16
  sta SmHeadX
  lda SmHeadPage
  adc #0
  sta SmHeadPage
  lda SmTempPage
  cmp SmHeadPage
  jcc Yes
  bne CornerLeft
  lda SmTempX
  cmp SmHeadX
  jcc Yes
CornerLeft:
  ldx #0
  beq Corner
CornerRight:
  ldx #1
Corner:
  lda MmVX
  ora MmVX+1
  ora MmVX+2
  jeq No                     ; source vx==0 selects the side, not the head.
  lda MmVY
  ora MmVY+1
  ora MmVY+2
  jeq Yes                    ; with nonzero vx and zero vy, head wins.

  ; V = cellBottom - (PY+16.5+yf), exact unsigned Q8.16 depth.
  lda RgTemp2
  sec
  sbc Player_Y_Position
  sec
  sbc #17
  sta SmTempY
  sec
  lda #0
  sbc MmYFraction
  sta SmTempX
  lda #$80
  sbc MmYFraction+1
  sta SmTempPage
  lda SmTempY
  sbc #0
  sta SmTempY
  cpx #0
  beq LeftDepth

  ; H = PX+17.5+xf - cellLeft.
  lda RgTempX
  and #$f0
  sta RgTempY
  lda MmXFraction
  sta SmHeadX
  clc
  lda MmXFraction+1
  adc #$80
  sta SmHeadPage
  lda Player_X_Position
  adc #17
  sec
  sbc RgTempY
  sta RgTempY
  jmp Compare
LeftDepth:
  ; H = cellRight - (PX-1.5+xf).
  lda RgTempX
  and #$f0
  sec
  sbc Player_X_Position
  clc
  adc #17
  sta RgTempY
  sec
  lda #0
  sbc MmXFraction
  sta SmHeadX
  lda #$80
  sbc MmXFraction+1
  sta SmHeadPage
  lda RgTempY
  sbc #0
  sta RgTempY
Compare:
  lda SmTempY
  cmp RgTempY
  bcc Yes
  bne No
  lda SmTempPage
  cmp SmHeadPage
  bcc Yes
  bne No
  lda SmTempX
  cmp SmHeadX
  bcc Yes
  bne No
Yes:
  sec
  rts
No:
  clc
  rts
.endproc
.popseg
