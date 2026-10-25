; Real SMB metatile queries, replacing the declared CPU-test callbacks.
; The Gradius logical sprite area is translated32px below the SMB HUD.
; X remains the original missile-loop owner,6..8; no actor/player is moved.
.pushseg
.segment "VIC_CORE"
.proc VvTerrainUnder
  lda VvObjAnim+3,x
  beq Empty
  lda VvObjY+3,x
  cpx #6
  bcc SetY
  adc #3                       ; original CPX carry makes the missile offset4.
SetY:
  sta VvProbeY
  lda VvObjSub+3,x
  cmp #1
  bne PlainX
  lda VvObjX+3,x
  adc #10                      ; original equality carry gives laser offset11.
  jmp SetX
PlainX:
  lda VvObjX+3,x
SetX:
  sta VvProbeX
  jmp VvTerrainSide
Empty:
  lda #0
  rts
.endproc
.proc VvTerrainSide
  phx
  phy
  lda VvProbeX
  clc
  adc #8                       ; leading edge, as in original$C3D3.
  sta RgTempX
  lda #0
  adc #0
  sta RgTempPage
  lda RgTempX
  clc
  adc ScreenLeft_X_Pos
  sta RgTempX
  lda RgTempPage
  adc ScreenLeft_PageLoc
  sta RgTempPage
  lda VvProbeY
  clc
  adc #32
  bcs Empty
  cmp #32
  bcc Empty
  cmp #240
  bcs Empty
  sta RgTempY
  farcall ExpandedMapCell
  bcc Empty
  tay
  lda MTileAttribute,y
  and #MTILE_SOLID
  jmp Restore
Empty:
  lda #0
Restore:
  sta VvWeaponScratch
  ply
  plx
  lda VvWeaponScratch
  rts
.endproc
.popseg
