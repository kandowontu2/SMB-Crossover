;2.02 MegaManBase.pressAtkBtn -> shootStart: charge only the throw.
; Caller has verified modern MM/Bass Arm ownership and a real held slot.
; Insufficient stock leaves held slot, projectile, movement and ammo intact.
.pushseg
.segment "SPECIAL_ROSTER"
.proc MegaManSuperArmThrow
  lda #1
  ldy #8
  farcall InventorySpend
  bcc Rejected
  ldx SsHeld
  dex
  stx RgSlot
  lda #0
  sta SsHeld
  sta SsMode,x
  lda #$55
  sta RgShotVXLo,x
  lda #2
  sta RgShotVXHi,x
  lda RgShotDir,x
  cmp #2
  bne SetY
  sec
  lda #0
  sbc RgShotVXLo,x
  sta RgShotVXLo,x
  lda #0
  sbc RgShotVXHi,x
  sta RgShotVXHi,x
SetY:
  lda #$55
  sta RgShotVYLo,x
  lda #$fd
  sta RgShotVYHi,x
  sec
  rts
Rejected:
  clc
  rts
.endproc
.popseg
