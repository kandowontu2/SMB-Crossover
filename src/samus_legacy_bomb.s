; Samus.hitProj in linked1.0 calls updateLoc/setHitPoints immediately.
; No gravity/friction update occurs in this additional position step.
.pushseg
.segment "LEGACY_COLD"
.proc SamusLegacyBombStep
  lda Player_X_Position
  sta SmTempX
  lda Player_X_Scroll
  sta SmTempY
  ; AnimatedObject.updateLoc clamps Samus's horizontal speed to150Flash/s.
  lda MmVX+2
  bmi Negative
  cmp #1
  bcc Integrate
  bne ClampPositive
  lda MmVX+1
  cmp #$40
  bcc Integrate
  bne ClampPositive
  lda MmVX
  beq Integrate
ClampPositive:
  lda #0
  sta MmVX
  lda #$40
  sta MmVX+1
  lda #1
  sta MmVX+2
  bne Integrate
Negative:
  cmp #$fe
  bcc ClampNegative
  bne Integrate
  lda MmVX+1
  cmp #$c0
  bcs Integrate
ClampNegative:
  lda #0
  sta MmVX
  lda #$c0
  sta MmVX+1
  lda #$fe
  sta MmVX+2
Integrate:
  clc
  lda MmXFraction
  adc MmVX
  sta MmXFraction
  lda MmXFraction+1
  adc MmVX+1
  sta MmXFraction+1
  lda Player_X_Position
  adc MmVX+2
  sta Player_X_Position
  lda #0
  ldx MmVX+2
  bpl :+
    lda #$ff
  :
  adc Player_PageLoc
  sta Player_PageLoc
  clc
  lda MmYFraction
  adc MmVY
  sta MmYFraction
  lda MmYFraction+1
  adc MmVY+1
  sta MmYFraction+1
  lda Player_Y_Position
  adc MmVY+2
  sta Player_Y_Position
  lda #0
  ldx MmVY+2
  bpl :+
    lda #$ff
  :
  adc Player_Y_HighPos
  sta Player_Y_HighPos
  ; Preserve native movement mirrors and the total displacement this update.
  lda Player_X_Position
  sec
  sbc SmTempX
  sta SmTemp
  clc
  adc SmTempY
  sta Player_X_Scroll
  lda MmVX+1
  lsr
  lsr
  lsr
  lsr
  sta MmTemp
  lda MmVX+2
  asl
  asl
  asl
  asl
  ora MmTemp
  sta Player_X_Speed
  sta MmLastXSpeed
  bpl :+
    eor #$ff
    clc
    adc #1
  :
  sta Player_XSpeedAbsolute
  ; Native scrolling ran before projectiles. Account only for this additional
  ; rightward displacement, retaining the previous parser/scroll receipt.
  ; Do not repeat native screen-edge separation or platform force processing.
  lda SmTemp
  beq Cache
  bmi Cache
  lda ScrollLock
  ora SideCollisionTimer
  bne Cache
  lda Player_X_Position
  sec
  sbc ScreenLeft_X_Pos
  cmp #$71
  bcc Cache
  sec
  sbc #$70
  cmp SmTemp
  bcc Advance
  lda SmTemp
Advance:
  tay
  clc
  adc ScrollAmount
  sta ScrollAmount
  tya
  clc
  adc ScrollThirtyTwo
  sta ScrollThirtyTwo
  tya
  clc
  adc ScreenLeft_X_Pos
  sta ScreenLeft_X_Pos
  sta HorizontalScroll
  lda ScreenLeft_PageLoc
  adc #0
  sta ScreenLeft_PageLoc
  and #1
  sta R0
  lda Mirror_PPUCTRL
  and #$fe
  ora R0
  sta Mirror_PPUCTRL
  jsr GetScreenPosition
Cache:
  jsr GetPlayerOffscreenBits
  jsr RelativePlayerPosition
  ldy #0
  jsr MegaManCollisionBox
  sty Player_BoundBoxCtrl
  ldx #0
  ldy #0
  jsr BoundingBoxCore
  rts
.endproc
.popseg
