; HitTester.checkLastHitPoints uses the previous head for Ground's underside.
; A side cell already beside that head is not a ceiling. Keep each original
; full-width sample, including walking coins and the native effect-cell ABI.
.pushseg
.segment "LEGACY_COLD"
.proc SamusHeadAxisProbe
  pha
  cmp #$26
  beq Keep
  cmp #$c2
  beq Keep
  cmp #$c3
  beq Keep
  lda GameEngineSubroutine
  cmp #8
  bne Keep
  lda Player_Y_HighPos
  cmp #1
  bne Keep
  lda Player_Y_Speed
  bpl Keep
  lda R3
  tax
  lda MTileAttribute,x
  and #MTILE_CLIMB
  bne Keep
  ; Undo the actual Q8.16 movement without quantizing its fractional borrow.
  sec
  lda MmYFraction
  sbc MmVY
  lda MmYFraction+1
  sbc MmVY+1
  lda Player_Y_Position
  sbc MmVY+2
  bcs Allow                      ; Previous origin crossed below screen byte.
  clc
  adc BlockBuffer_Y_Adder,y
  bcs Allow                      ; Previous head is at/below256.
  sta SmClearance
  lda R2
  clc
  adc #48                        ; Actual sampled cell bottom, including HUD.
  bcs Reject                     ; Bottom256, previous head below256.
  cmp SmClearance
  bcc Allow
  beq Allow                      ; Previous head >= cell bottom.
Reject:
  pla
  lda #0
  ldx #0
  clc
  rts
Allow:
  pla
  ldx #0
  sec
  rts
Keep:
  pla
  ldx #0
  clc
  rts
.endproc
.assert *-SamusHeadAxisProbe<=101, error, "Samus axis leaf exceeds MMC5 cold gap"
.popseg
