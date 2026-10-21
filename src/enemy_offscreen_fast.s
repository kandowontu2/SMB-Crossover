.segment "OBJECT"

; Ordinary-enemy interior shortcut. Every boundary/high-position/foreign-slot
; case tail-calls the unchanged resident helper. No persistent cache is used.
;
; The native caller keeps only GetXOffscreenBits' high nibble: a right-edge
; distance of24 already produces zero after its four shifts. Its left-edge
; result must still be excluded at distance0. Check both actual16-bit edges,
; without assuming a particular viewport width or page relationship.
.proc NormalEnemyOffscreenBits
  cpx #6
  bcs Native
  lda Enemy_Y_HighPos,x
  cmp #1
  bne Native
  lda Enemy_Y_Position,x
  cmp #32
  bcc Native
  cmp #224
  bcs Native

  sec
  lda Enemy_X_Position,x
  sbc ScreenLeft_X_Pos
  sta R0
  lda Enemy_PageLoc,x
  sbc ScreenLeft_PageLoc
  bne Native
  lda R0
  beq Native

  sec
  lda ScreenRight_X_Pos
  sbc Enemy_X_Position,x
  sta R7
  lda ScreenRight_PageLoc
  sbc Enemy_PageLoc,x
  bne Native
  lda R7
  cmp #24
  bcc Native

  ; Exact native ABI, including scratch and flags. R1..R3 remain untouched.
  ; Do not write R5/R6 before committing: rejected far-offscreen native calls
  ; may legitimately preserve their incoming values.
  lda #0
  sta Enemy_OffscreenBits
  sta R0
  txa
  clc
  adc #1
  sta R4
  lda Enemy_Y_Position,x
  eor #$ff
  sta R7
  lda #4
  sta R5
  lda #32
  sta R6
  lda #0
  ldy #Enemy_OffscreenBits - SprObject_OffscrBits
  clc
  ldx ObjectOffset
  rts
Native:
  jmp GetEnemyOffscreenBits
.endproc

; RunNormalEnemies supplies a native enemy slot. With no offscreen bits,
; either native mask is zero, so use the unchanged box construction directly.
; BoundingBoxCore/CheckRightScreenBBox overwrite the prelude's R0/R1 values.
; Keep the original mask and rejection path for every nonzero bit pattern.
.proc NormalEnemyBoundBox
  lda Enemy_OffscreenBits
  bne Native
  lda #0
  sta EnemyOffscrBitsMasked,x
  jmp SetupEOffsetFBBox
Native:
  jmp GetEnemyBoundBox
.endproc
