; Contextual GQ+W6 rare native closures. No new RAM.
.pushseg
.segment "LEVEL"
.proc UnionMegaManClimbCheckCore
  pha
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  bne NotGuest
  pla
  cmp #$26
  bne NotVine
  pha
  lda R6
  asl
  asl
  asl
  asl
  sta MmVineX
  lda Player_X_Position
  sec
  sbc MmVineX
  clc
  adc #7
  cmp #15
  bcs Rejected
  pla
  sec
  rts
Rejected:
  pla
  clc
  bit FullMask
  rts
NotGuest:
  pla
NotVine:
  clc
  bit ZeroMask
  rts
ZeroMask: .byte 0
FullMask: .byte $ff
.endproc
.proc UnionMegaManClimbCheck
  jsr UnionMegaManClimbCheckCore
  jsr BillNativeCaptureP
.if ::MAPPER_MMC3
  txa
  pha
  tsx
  lda $0107,x
  sta BillNativeReturnSelector
  pla
  tax
  lda BillNativeReturnSelector
.else
  lda #0
  sta BillNativeReturnSelector
.endif
  rts
.endproc
.proc UnionMegaManVineAnchorCore
  php
  pha
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  bne Done
  lda GameEngineSubroutine
  cmp #8
  beq Anchor
  cmp #1
  bne Done
Anchor:
  lda R6
  asl
  asl
  asl
  asl
  sta MmVineX
  sec
  sbc Player_X_Position
  bcs LargerX
    bmi SetX
    inc Player_PageLoc
    bne SetX
LargerX:
  bpl SetX
    dec Player_PageLoc
SetX:
  lda MmVineX
  sta Player_X_Position
Done:
  pla
  plp
  rts
.endproc
.proc UnionMegaManVineAnchor
  jsr BillNativeRestoreP ; reestablish public-entry full P/A before PHP.
  jsr UnionMegaManVineAnchorCore
  jsr BillNativeCaptureP
.if ::MAPPER_MMC3
  txa
  pha
  tsx
  lda $0107,x
  sta BillNativeReturnSelector
  pla
  tax
  lda BillNativeReturnSelector
.else
  lda #0
  sta BillNativeReturnSelector
.endif
  rts
.endproc
.proc UnionPwrUpCore
  lda #$01                  ;this is a residual jump point in enemy object jump table
  sta Enemy_State,x         ;set power-up object's state
  sta Enemy_Flag,x          ;set buffer flag
  lda #$03
  sta Enemy_BoundBoxCtrl,x  ;set bounding box size control for power-up object
  lda PowerUpType,x
  cmp #$02                  ;check currently loaded power-up type
  bcs PutBehind             ;if star or 1-up, branch ahead
  lda PlayerStatus          ;otherwise check player's current status
  cmp #$02
  bcc StrType               ;if player not fiery, use status as power-up type
  lsr                       ;otherwise shift right to force fire flower type
StrType:
  sta PowerUpType,x         ;store type here
PutBehind:
  lda #%00100000
  sta Enemy_SprAttrib,x     ;set background priority bit
  lda #Sfx_GrowPowerUp
  sta Square2SoundQueue     ;load power-up reveal sound and leave
  lda #0
  sta EnemyMetasprite,x
.if ::ENABLE_CROSSOVER
.if ::ENABLE_MMC5_EXPANDED
  farcall RlPrepareDispatch
.else
  farcall InventoryPreparePickup
.endif
.endif
  rts
.endproc
.popseg
