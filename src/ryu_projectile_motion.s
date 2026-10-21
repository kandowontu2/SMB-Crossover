; Pinned Crossover 2.02 RyuProjectile.setDirection/updateStats.
; STAR_BIG_FRICTION_X is assigned in the source but never applied by its
; update path. The active motion is the 2300 spring acceleration, 800 cap,
; 50 Flash-pixel reversal threshold and 85 vertical tracking speed.
.pushseg
.segment "ROSTER"
.proc RyuAttackPose
  ldx RgAttackAge
  lda Phases,x
  clc
  adc #XG_POSE_RYUSLASH1
  ldx RgAttackKind
  beq Stance
  clc
  adc #15
Stance:
  ldx RgCrouch
  beq Air
  clc
  adc #5
  rts
Air:
  ldx XgWall
  bne Wall
  ldx Player_State
  beq Done
  clc
  adc #10
Done:
  rts
Wall:
  ldx RgAttackAge
  lda Phases,x
  clc
  adc #XG_POSE_WALLTHROW1
  pha
  lda PlayerFacingDir
  eor #3
  and SavedJoypadBits
  and #3
  beq Forward
  pla
  clc
  adc #5
  rts
Forward:
  pla
  rts
Phases: .byte 0,0,0,1,1,1,2,2,2,3,3,4,4,4,4
.endproc
.proc RyuProjectileOrigin
  ldx RgSlot
  lda #15
  ldy RgCrouch
  beq :+
    lda #13
  :
  ldy Player_State
  beq :+
    lda #13
  :
  ldy XgWall
  beq :+
    lda #10
  :
  sta RgTemp
  lda PlayerFacingDir
  sta RgShotDir,x
  ldy XgWall
  beq FacingReady
  eor #3
  and SavedJoypadBits
  and #3
  beq FacingReady
  lda RgShotDir,x
  eor #3
  sta RgShotDir,x
  lda #20
  sta RgTemp
FacingReady:
  lda Player_X_Position
  clc
  adc #8
  sta RgShotX,x
  lda Player_PageLoc
  adc #0
  sta RgShotPage,x
  lda RgShotDir,x
  cmp #1
  bne Left
  clc
  lda RgShotX,x
  adc RgTemp
  sta RgShotX,x
  lda RgShotPage,x
  adc #0
  jmp StorePage
Left:
  sec
  lda RgShotX,x
  sbc RgTemp
  sta RgShotX,x
  lda RgShotPage,x
  sbc #0
StorePage:
  sta RgShotPage,x
  lda #11
  ldy RgCrouch
  beq :+
    lda #16
  :
  ldy XgWall
  beq :+
    lda #$80
    sta RgShotFracY,x
    lda #9
  :
  clc
  adc Player_Y_Position
  sta RgShotY,x
  lda Player_Y_HighPos
  adc #0
  sta RgShotYHigh,x
RyuProjectileOriginDone:
  rts
.endproc
.proc RyuProjectileSpawn
  jsr RyuProjectileOrigin
  lda #0
  sta XgWindmillFraction
  sta RgShotVXLo,x
  lda #5
  sta RgShotVXHi,x
  lda RgShotType,x
  cmp #8
  bne Direction
  lda #0
  sta XgWindmillSide
  sta XgWindmillReverse
  lda #$ab
  sta XgWindmillFraction
  lda #$aa
  sta RgShotVXLo,x
  lda #6
  sta RgShotVXHi,x
Direction:
  lda RgShotDir,x
  cmp #1
  beq Done
  jsr NegateX
Done:
  rts
NegateX:
  sec
  lda #0
  sbc XgWindmillFraction
  sta XgWindmillFraction
  lda #0
  sbc RgShotVXLo,x
  sta RgShotVXLo,x
  lda #0
  sbc RgShotVXHi,x
  sta RgShotVXHi,x
  rts
.endproc
.proc RyuWindmillMotion
  ldx RgSlot
  lda Player_X_Position
  clc
  adc #8
  sta RgTempX
  lda Player_PageLoc
  adc #0
  sta RgTempPage
  sec
  lda RgShotX,x
  sbc RgTempX
  sta RgBoomDx
  lda RgShotPage,x
  sbc RgTempPage
  sta RgBoomDx+1
  lda #1
  ldy RgBoomDx+1
  bpl :+
    lda #0
  :
  cmp XgWindmillSide
  beq SameSide
  sta XgWindmillSide
  lda #0
  sta XgWindmillReverse
SameSide:
  lda RgBoomDx+1
  bpl :+
    sec
    lda #0
    sbc RgBoomDx
    sta RgBoomDx
    lda #0
    sbc RgBoomDx+1
    sta RgBoomDx+1
  :
  lda RgBoomDx+1
  bne Reverse
  lda RgBoomDx
  cmp #25
  bcc Accelerate
Reverse:
  lda #1
  sta XgWindmillReverse
Accelerate:
  lda XgWindmillSide
  eor XgWindmillReverse
  beq Negative
  clc
  lda XgWindmillFraction
  adc #$c7
  sta XgWindmillFraction
  lda RgShotVXLo,x
  adc #$51
  sta RgShotVXLo,x
  lda RgShotVXHi,x
  adc #0
  sta RgShotVXHi,x
  jmp Cap
Negative:
  sec
  lda XgWindmillFraction
  sbc #$c7
  sta XgWindmillFraction
  lda RgShotVXLo,x
  sbc #$51
  sta RgShotVXLo,x
  lda RgShotVXHi,x
  sbc #0
  sta RgShotVXHi,x
Cap:
  lda RgShotVXHi,x
  pha
  bpl :+
    jsr RyuProjectileSpawn::NegateX
  :
  lda RgShotVXHi,x
  cmp #6
  bcc Sign
  bne Clamp
  lda RgShotVXLo,x
  cmp #$aa
  bcc Sign
  bne Clamp
  lda XgWindmillFraction
  cmp #$ab
  bcc Sign
Clamp:
  lda #$ab
  sta XgWindmillFraction
  lda #$aa
  sta RgShotVXLo,x
  lda #6
  sta RgShotVXHi,x
Sign:
  pla
  bpl :+
    jsr RyuProjectileSpawn::NegateX
  :
  lda Player_Y_Position
  clc
  adc #16
  sta RgTempY
  sec
  lda RgTempY
  sbc RgShotY,x
  sta RgBoomDy
  lda Player_Y_HighPos
  sbc RgShotYHigh,x
  sta RgBoomDy+1
  lda #0
  sta RgShotVYLo,x
  sta RgShotVYHi,x
  lda RgBoomDy
  ora RgBoomDy+1
  beq Catch
  lda #$b5                    ; 85 /120, Q8.8.
  sta RgShotVYLo,x
  lda RgBoomDy+1
  bpl Catch
  lda #$4b
  sta RgShotVYLo,x
  lda #$ff
  sta RgShotVYHi,x
Catch:
  lda RgShotAge,x
  cmp #18                     ; Catch collision enabled after 300ms.
  bcc Done
  lda RgBoomDx+1
  bne Done
  lda RgBoomDx
  cmp #9
  bcs Done
  lda RgBoomDy+1
  bpl :+
    sec
    lda #0
    sbc RgBoomDy
    sta RgBoomDy
    lda #0
    sbc RgBoomDy+1
    sta RgBoomDy+1
  :
  lda RgBoomDy+1
  bne Done
  lda RgBoomDy
  cmp #15
  bcs Done
  lda #0
  sta RgShotType,x
Done:
::RyuWindmillUpdated:
  rts
.endproc
.popseg
