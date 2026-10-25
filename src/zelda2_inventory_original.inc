.pushseg
.segment "Z2_LOGIC"
.proc Z2OriginalInventoryLegacyClassic
  ldx CrossoverBehaviorVersion
  bne No
  ldx SelectedCharacter
  cpx #CHARACTER_MEGAMAN
  bcc No
  cpx #CHARACTER_SIMON+1
  bcs No
  sec
  rts
No:
  clc
  rts

.endproc
.proc Z2OriginalInventorySupported
  jsr Z2OriginalInventoryLegacyClassic
  bcc ModernRules
  clc                           ; No2.02 ownership, ammo or UI in classic Easy.
  rts
ModernRules:
  ldx SelectedCharacter
  ; Enable each inventory only together with its native weapon migration.
  cpx #CHARACTER_MEGAMAN
  beq Supported
  cpx #CHARACTER_BASS
  beq Supported
  cpx #CHARACTER_SAMUS
  beq Supported
  cpx #CHARACTER_BILL
  beq Supported
  cpx #CHARACTER_LINK
  beq Supported
  cpx #CHARACTER_SIMON
  beq Supported
  cpx #CHARACTER_RYU
  beq Supported
  cpx #CHARACTER_SOPHIA
  beq Supported
  clc
  rts
Supported:
  sec
  rts

.endproc
.proc Z2OriginalInventoryHurt
  jsr Z2OriginalInventorySupported
  bcc Done
  ldx SelectedCharacter
  lda Z2OriginalMushroomLo,x
  ora #1
  eor #$ff
  and InvOwnedLo,x
  sta InvStoredLo,x
  lda Z2OriginalMushroomHi,x
  eor #$ff
  and InvOwnedHi,x
  sta InvStoredHi,x
  lda InvViewedLo,x
  sta InvStoredViewLo,x
  lda InvViewedHi,x
  sta InvStoredViewHi,x
  farcall InventoryRemove
Done:
  lda #0
  rts

.endproc
Z2OriginalMushroomLo:
.byte 0,0,128,0,64,0,0,0,0,0,0,128
Z2OriginalMushroomHi:
.byte 0,4,0,0,0,2,0,0,0,0,0,0
.popseg
