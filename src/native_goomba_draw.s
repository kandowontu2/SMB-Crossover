; Proposed MMC5-only native Goomba kernel. Included LAST so accepted45's
; existing METASPRITE code/data/pointer addresses do not move.
; No new RAM, farcall, allocation, OAM priority, pose or palette policy.
.pushseg
.segment "METASPRITE"
.proc NativeGoombaRender
Ptr = R0
Atr = R3
Xlo = R4
Xhi = R5
Ylo = R6
Yhi = R7

  ; The outline filter may clobber incoming X. Admit actual immutable Ptr,
  ; never just the apparent two-piece pose ID.
  lda Ptr+1
  cmp #>MetaspriteData_GOOMBA_WALKING_1_LEFT
  beq CheckLow
Slow:
  jmp MetaspriteRenderLoop
CheckLow:
  lda Ptr
  cmp #<MetaspriteData_GOOMBA_WALKING_1_LEFT
  beq Interior
  cmp #<MetaspriteData_GOOMBA_WALKING_1_RIGHT
  beq Interior
  cmp #<MetaspriteData_GOOMBA_WALKING_2_LEFT
  beq Interior
  cmp #<MetaspriteData_GOOMBA_WALKING_2_RIGHT
  bne Slow
Interior:
  lda Xhi
  bne Slow
  lda Yhi
  cmp #1
  bne Slow
  lda Xlo
  cmp #248
  bcs Slow
  lda Ylo
  cmp #248
  bcs Slow

  ; Read the real header and preserve the original capacity-carry rejection.
  ; Unsupported headers fall back before ANY OAM/scratch write.
  ldx CurrentOAMOffset
  ldy #0
  lda (Ptr),y
  cmp #8
  beq Header
  jmp MetaspriteRenderLoop
Header:
  clc
  adc CurrentOAMOffset
  bcs Rejected
  lda GuestOamRotationActive
  beq RightPart
  txa
  clc
  adc RgOamRotation
  tax
RightPart:
::NativeGoombaFastBody:
  ; Reverse-record order exactly matches the generic loop. Preserve each
  ; individual X/Y/attributes/tile store, including unaligned OAM overflow.
  lda Xlo
  clc
  adc #8
  sta Sprite_X_Position,x
  lda Ylo
  clc
  adc #8
  sta Sprite_Y_Position,x
  ldy #6
  lda (Ptr),y
  ora Atr
  and #$f3
  sta Sprite_Attributes,x
  dey
  lda (Ptr),y
  sta Sprite_Tilenumber,x
  inx
  inx
  inx
  inx

  lda Xlo
  sta Sprite_X_Position,x
  lda Ylo
  clc
  adc #8
  sta Sprite_Y_Position,x
  ldy #2
  lda (Ptr),y
  ora Atr
  and #$f3
  sta Sprite_Attributes,x
  dey
  lda (Ptr),y
  sta Sprite_Tilenumber,x
  inx
  inx
  inx
  inx
  ; Generic final ADC #0 into Yhi always clears V in this interior case.
  ; The shared rotated subtraction may then set V exactly as before.
  clv
  jmp MetaspriteRenderLoop::LoopEnded
Rejected:
  ldy #0
  lda #8
  clc
  rts
.endproc
NativeGoombaRenderEnd:

; A changed layout must fail at link time rather than silently broaden Ptr.
.assert (>MetaspriteData_GOOMBA_WALKING_1_LEFT) = (>MetaspriteData_GOOMBA_WALKING_1_RIGHT), lderror, "Goomba pointer page"
.assert (>MetaspriteData_GOOMBA_WALKING_1_LEFT) = (>MetaspriteData_GOOMBA_WALKING_2_LEFT), lderror, "Goomba pointer page"
.assert (>MetaspriteData_GOOMBA_WALKING_1_LEFT) = (>MetaspriteData_GOOMBA_WALKING_2_RIGHT), lderror, "Goomba pointer page"
.assert NativeGoombaRenderEnd-NativeGoombaRender <= 285, error, "Goomba kernel exceeds accepted45 free METASPRITE bytes"
.popseg
