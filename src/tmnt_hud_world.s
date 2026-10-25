; The old world helper rejects all origins below24 because some effects
; extend24 pixels upward. The eight immutable HUD icons extend only16.
; This entry is reached only from that original Y<24 branch; other draws
; keep the exact old path and its timing.
.pushseg
.segment "TMNT_CORE"
.proc TnHudWorldRender
 lda R6
 cmp #16
 jcc Legacy
 lda CurrentBankC
 cmp #$d8
 jne Legacy
 ldx R0
 lda TnHudWorldHigh,x
 jeq Legacy
 cmp R1
 jne Legacy
 lda R3
 and #3
 jne Legacy
 ldx CurrentOAMOffset
 ldy #0
 lda (R0),y
 cmp #16
 jne Legacy
 clc
 adc CurrentOAMOffset
 jcs Legacy
 lda GuestOamRotationActive
 beq Start
 txa
 clc
 adc RgOamRotation
 tax
Start:
 ldy #16
 .repeat 4
  lda (R0),y
  clc
  adc R4
  sta Sprite_X_Position,x
  lda R6
  sec
  sbc #16
  sta Sprite_Y_Position,x
  dey
  dey
  lda (R0),y
  ora R3
  and #$f3
  sta Sprite_Attributes,x
  dey
  lda (R0),y
  sta Sprite_Tilenumber,x
  inx
  inx
  inx
  inx
  dey
 .endrepeat
 clv
 txa
 ldy GuestOamRotationActive
 beq Save
 sec
 sbc RgOamRotation
Save:
 sta CurrentOAMOffset
 ldy #0
 ora #0                       ; old generic farcall's final PLA supplies N/Z
 sec
 rts
Legacy:
 jmp TnFastWorldRender::Legacy
.endproc
.export TnHudWorldRender
.include "tmnt_hud_world_high.inc"
.popseg
