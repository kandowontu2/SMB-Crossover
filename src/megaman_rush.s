; Pinned2.02 MegaManBase/Rush:4-unit summon gate, free summon,
; existingRush->ordinaryBuster, clamped12-unit bounce and source jump flags.
.pushseg
.segment "SPECIAL_ROSTER"
.proc MegaManRushAttack
  lda StarInvincibleTimer
  bne Funded
  lda InvAmmo+CHARACTER_MEGAMAN*16+8
  cmp #4
  jcc Done
Funded:
  ldx #9
FindRush:
  lda RgShotType,x
  cmp #SS_RUSH
  jeq ActiveRush
  dex
  bpl FindRush
  farcall SpecialWeapons::FindSlot
  jcc Done
  lda #SS_RUSH
  farcall SpecialWeapons::Spawn
  ldx RgSlot
  lda #0
  sta RgShotVXLo,x
  sta RgShotVXHi,x
  sta RgShotVYLo,x
  sta RgShotVYHi,x
  sta RgShotY,x
  lda #1
  sta RgShotYHigh,x
  lda #20
  ldy SavedJoypadBits
  tya
  and #Up_Dir
  beq RushSide
  lda #0
  beq RushX
RushSide:
  lda #20
  ldy PlayerFacingDir
  cpy #1
  beq RushX
  lda #$ec
RushX:
  clc
  adc #8
  sta SsTmp
  clc
  adc Player_X_Position
  sta RgShotX,x
  lda #0
  bit SsTmp
  bpl :+
    lda #$ff
  :
  adc Player_PageLoc
  sta RgShotPage,x
  rts

ActiveRush:
  ldy #0
  ldx #3
CountBuster:
  lda MmBulletType,x
  beq NextBuster
  cmp #3
  jeq Done
  cmp #6
  jeq Done
  iny
NextBuster:
  dex
  bpl CountBuster
  ldx #9
CountOther:
  lda RgShotType,x
  beq NextOther
  cmp #SS_RUSH
  beq NextOther
  iny
NextOther:
  dex
  bpl CountOther
  cpy #3
  jcs Done
  farcall MegaManRushBusterSpawn
Done:
  rts
.endproc
.proc MegaManRushBounce
  lda StarInvincibleTimer
  bne JumpFlags
  lda InvAmmo+CHARACTER_MEGAMAN*16+8
  sec
  sbc #12
  bcs Store
  lda #0
Store:
  sta InvAmmo+CHARACTER_MEGAMAN*16+8
  inc InvDirty
JumpFlags:
  lda #0
  sta MmFrictionYActive
  lda #1
  sta MmJumpReleased
  sta MmRushLandRequest
  sec
  rts
.endproc
.segment "GUEST"
.proc MegaManRushBusterSpawn
  lda #1
  jsr MegaManWeapons::PowerType
  jmp MegaManWeapons::Spawn
.endproc
.popseg
