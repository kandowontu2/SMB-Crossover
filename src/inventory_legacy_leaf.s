; Flatten the read-only Easy/Hard inventory predicate. The former four-bank
; gate chain can leave insufficient hardware stack for an audio NMI. Preserve
; its complete returned A/X/Y/P, including Roll's alternate-specific A result.
.pushseg
.segment "INVENTORY_LEGACY_LEAF"
.proc InventoryLegacyLeaf
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  bne CheckMac
  lda RlVariant
  bne Modern
  jmp Original
CheckMac:
  cmp #15
  beq Classic
  cmp #CHARACTER_SIMON
  bne CheckZ2
  pha
  lda Cv3Variant
  cmp #1
  bcc RestoreOriginal
  cmp #4
  bcs RestoreOriginal
  pla
  sec
  rts
CheckZ2:
  cmp #CHARACTER_LINK
  bne Original
  pha
  lda Z2Variant
  cmp #1
  bne RestoreOriginal
  pla
  sec
  rts
RestoreOriginal:
  pla
Original:
  ldx CrossoverBehaviorVersion
  bne Modern
  ldx SelectedCharacter
  cpx #CHARACTER_MEGAMAN
  bcc Modern
  cpx #CHARACTER_SIMON+1
  bcs Modern
Classic:
  sec
  rts
Modern:
  clc
  rts
.endproc
.popseg

; Item queries/spending pass their requested local ID in A. The existing
; mode leaf publishes a character/alternate ID in A; retain its boolean C
; and X result while restoring the caller's requested item for the lookup.
.pushseg
.segment "INVENTORY_ITEM_RETURN"
.proc InventoryLegacyItemLeaf
 pha
 jsr InventoryLegacyLeaf
 pla
 rts
.endproc
.export InventoryLegacyItemLeaf
.popseg
