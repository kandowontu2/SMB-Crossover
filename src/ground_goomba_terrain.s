; UNAPPLIED PROPOSAL ONLY. No object was assembled or executed.
; Append at the very end of entrypoint.s under ENABLE_CROSSOVER && MAPPER_MMC5,
; after all existing OBJECT contributions, so native code addresses stay put.
; At RunNormalEnemies' existing EnemyToBGCollisionDet JSR replace only its
; operand with this helper. Other callers and MMC3 retain the original target.
;
; One zero-byte source label must be inserted immediately after the existing
; `jsr BBChk_E` in DoEnemySideCheck: NativeEnemySideQueryReturn:
;
; Reconstruct exact settled-Goomba native output, including the five specific
; dead-stack bytes left by the last native side query. No blanket stack mask.
; Both block-buffer cells are read freshly on each accepted call. Any dynamic
; tile, bump, solid side, other state or page-edge case uses native code.
; X must be0..5 and match ObjectOffset; every foreign slot uses native code.
.segment "OBJECT"
.proc Mmc5GroundGoombaTerrain
  ; Preserve the native early state's incoming C/V/Y and stack without PHP.
  lda Enemy_State,x
  beq Active
  and #$20
  beq Native
  rts
Active:
  cpx #6
  bcs Native
  cpx ObjectOffset
  bne Native
  lda Enemy_ID,x
  cmp #Goomba
  bne Native
  lda Enemy_Y_Position,x
  cmp #$20
  bcc Native
  cmp #$c0
  bcs Native
  and #$0f
  cmp #8
  bne Native
  lda Enemy_X_Position,x
  and #$f0
  beq Native
  cmp #$f0
  beq Native
  lda Enemy_MovingDir,x
  cmp #1
  beq Query
  cmp #2
  beq Query
Native:
  jmp EnemyToBGCollisionDet
Query:
  ; For X16..239, both X+8 and X+16 remain on this actual world page.
  ; The foot cell is exactly (X+8, Y+24), with source nibble Y=8.
  lda Enemy_PageLoc,x
  and #1
  tay
  lda #>Block_Buffer_1
  sta R7
  lda Enemy_X_Position,x
  clc
  adc #8
  sta R5
  lsr
  lsr
  lsr
  lsr
  clc
  adc BlockBufferAddr,y
  sta R6
  lda Enemy_Y_Position,x
  and #$f0
  tay
  lda (R6),y
  cmp #$54
  bne Native
  ; Exact native direction-specific side cell (X or X+16, Y+20).
  lda Enemy_MovingDir,x
  cmp #1
  bne Left
  lda Enemy_X_Position,x
  adc #15                      ; CMP#1 supplies C=1, so this is X+16.
  bne SideX                    ; X16..239 guarantees a nonzero result.
Left:
  lda Enemy_X_Position,x
SideX:
  sta R5
  lsr
  lsr
  lsr
  lsr
  sta R6
  lda Enemy_PageLoc,x
  and #1
  tay
  lda R6
  clc
  adc BlockBufferAddr,y
  sta R6
  ; Keep the actual native ADC/AND/SEC/SBC sequence to reproduce V exactly.
  lda Enemy_Y_Position,x
  clc
  adc #$14
  and #$f0
  sec
  sbc #$20
  sta R2
  tay
  lda (R6),y
  bne Native
  sta R3                       ; Side tile is exactly0; all others fall back.
  sta Local_eb                 ; Native loop completes its two directions at0.
  lda Enemy_X_Position,x
  and #$0f
  sta R4
  ; Native BBChk_E last pushes these exact five bytes at entry SP..SP-4.
  ; No gameplay RAM, caller live stack or SMC bytes are excluded by the plan.
  lda #>(NativeEnemySideQueryReturn-1)
  pha
  lda #<(NativeEnemySideQueryReturn-1)
  pha
  lda #>(BBChk_E+2)
  pha
  lda #<(BBChk_E+2)
  pha
  lda #1
  pha
  pla
  pla
  pla
  pla
  pla
  lda Enemy_MovingDir,x
  lsr                          ; Right1->A0; Left2->A1, as native loop returns.
  ldy #$18
  cpy #$18                     ; Exact native final C=1,Z=1,N=0; V retained.
  rts
.endproc
