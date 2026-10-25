; Rygar's body, disk and chain use palette0; he has no2.02 inventory.
; Retain the area's native palette3 for bricks, debris and world actors.
; Other guests still require their face/special palette until their own
; artwork has a verified allocation. No extra OAM or CHR is introduced.
.pushseg
.segment "WORLD_SPRITE_PALETTE"
.proc GuestWorldPaletteIndex
  php
  ldy #0
  lda SelectedCharacter
  beq Mario
  cmp #CHARACTER_RYGAR
  bne Guest
  jsr NativeIndex
Guest:
  plp                           ; Preserve the old guest entry C/V/I/D.
  rts
Mario:
  plp
NativeIndex:
  lda AreaType
  asl
  sta R0
  asl
  clc
  adc R0
  adc #6
  tay
  rts
.endproc
.assert * <= $c000,error,"World palette helper exceeds bank3 tail"
.popseg
