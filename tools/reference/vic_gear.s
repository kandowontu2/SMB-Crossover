; Original Gradius USA $894B..$89E2. External HUD/sound/score calls become
; explicit events for the SMB adapter; ownership/refusal/wrap rules stay native.
.pushseg
.segment "VIC_CORE"
.proc VvTakeCapsule
  inc VvMeter
  lda VvMeter
  cmp #7
  bcc Cursor
  lda VvScoreDigit
  and #15
  bne CheckScore
  lda #4
  sta VvAutoFire
CheckScore:
  cmp #5
  bne Wrap
  lda #1
  sta VvScoreBonus
Wrap:
  lda #1
  sta VvMeter
Cursor:
  lda #13
  sta VvSfxEvent
  lda #1
  sta VvHudDirty
  rts
.endproc

.proc VvBuyUpgrade
  lda VvAlive
  cmp #1
  bne Done
  lda VvHeld
  and #B_Button
  beq Done
  lda VvMeter
  beq Done
  cmp #1
  beq Speed
  cmp #2
  beq Missile
  cmp #3
  beq Double
  cmp #4
  beq Laser
  cmp #5
  beq Option
  cmp #6
  bne Done
Shield:
  lda VvShield
  bne Done
  lda #5
  sta VvShield
  bne Consumed
Speed:
  inc VvSpeed                 ; native8-bit wrap; no artificial max/owned gate.
  lda #1
  sta VvHudDirty
  bne Consumed
Missile:
  lda VvMissile
  bne Done
  inc VvMissile
  bne Consumed
Double:
  lda #2
  bne Gun
Laser:
  lda #1
Gun:
  cmp VvGun
  beq Done
  sta VvGun
  bne Consumed
Option:
  lda VvOptions
  cmp #2
  bcs Done
  inc VvOptions
Consumed:
  lda #0
  sta VvMeter
  lda #14
  sta VvSfxEvent
Done:
  rts
.endproc
.popseg
