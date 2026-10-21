; Water-only fast drawing proposal. Include in SPECIAL_MM and call with X equal
; to the visible Water Shield slot, before SpecialDrawShots switches C banks.
; Keeps both source hardware parts, their reverse metasprite drawing order,
; clipping, logical OAM allocation and global guest sprite priority rotation.
; No source change is required in MetaspriteRenderLoop.
.pushseg
.segment "SPECIAL_MM"
.proc SpecialDrawWaterShot
  lda SsArt,x
  cmp #SS_ART_WATER40
  jcc Done
  cmp #SS_ART_WATER41+1
  jcs Done
  lda SsDrawFamily
  cmp #4
  beq FamilyReady
  cmp #$ff
  jne Done
  lda #4
  sta SsDrawFamily
  BankPRGC #.bank(SsArt0Right)
  lda SsPhysicalBanks+4
.if ::MAPPER_MMC5
  ora #1
.endif
  sta SsChrPhysical
  lda #1
  sta SsChrActive
FamilyReady:
  ; An eight-byte reservation must not wrap the logical allocation pointer.
  lda CurrentOAMOffset
  clc
  adc #8
  jcs Done
  sta CurrentOAMOffset
  sec
  sbc #8
  ldy GuestOamRotationActive
  beq :+
    clc
    adc RgOamRotation
  :
  sta R4                       ; Hardware OAM write offset.
  ldx RgSlot
  lda RgShotX,x
  sec
  sbc ScreenLeft_X_Pos
  sta R0
  lda RgShotPage,x
  sbc ScreenLeft_PageLoc
  sta R1
  lda RgShotY,x
  sta R2
  lda RgShotYHigh,x
  sta R3
  ; Ordinary Water40 balls are wholly visible most of the time. Their two
  ; source pieces share a center; emit the exact bytes without per-part
  ; signed/page tests. Edge/wrap cases and Water41 keep the general path.
  cmp #1
  bne GeneralParts
  lda SsArt,x
  cmp #SS_ART_WATER40
  bne GeneralParts
  lda R1
  bne GeneralParts
  lda R0
  cmp #8
  bcc GeneralParts
  cmp #253
  bcs GeneralParts
  lda R2
  cmp #3
  bcc GeneralParts
  lda #$c2
  ldy RgShotDir,x
  cpy #2
  bne :+
    lda #$82
  :
  sta R3
  lda R0
  cpy #2
  bne :+
    sec
    sbc #8
  :
  ldx R4
  sta Sprite_X_Position,x
  lda R2
  sec
  sbc #1
  sta Sprite_Y_Position,x
  lda R3
  sta Sprite_Attributes,x
  lda #MetaspriteVramOffset{$3a},{SPRITE_BANK_4}
  sta Sprite_Tilenumber,x
.if ::MAPPER_MMC3
  lda R2
  cmp #35
  bcc MarkFastHud
  cmp #225
  bcc FastHudReady
  cmp #243
  bcs FastHudReady
MarkFastHud:
  inc GuestHudMixed
FastHudReady:
.endif
  inx
  inx
  inx
  inx
  lda R0
  sec
  sbc #4
  sta Sprite_X_Position,x
  lda R2
  sec
  sbc #3
  sta Sprite_Y_Position,x
  lda R3
  and #$fd
  sta Sprite_Attributes,x
  lda #MetaspriteVramOffset{$38},{SPRITE_BANK_4}
  sta Sprite_Tilenumber,x
  rts
GeneralParts:
  lda SsArt,x
  sec
  sbc #SS_ART_WATER40
  asl
  asl
  sta R5                       ; Two parts each for right and left.
  lda RgShotDir,x
  cmp #2
  bne :+
    inc R5
    inc R5
  :
  ldy R5
  jsr Part
  inc R5
  ldy R5
  jsr Part
Done:
  rts

Part:
  ldx R4
  clc
  lda XOffsets,y
  bpl PositiveX
  adc R0
  sta Sprite_X_Position,x
  lda R1
  adc #$ff
  bne Hidden
  beq DrawY
PositiveX:
  adc R0
  sta Sprite_X_Position,x
  lda R1
  adc #0
  bne Hidden
DrawY:
  clc
  lda YOffsets,y               ; Both source pieces have negative Y offsets.
  adc R2
  sta Sprite_Y_Position,x
  lda R3
  adc #$ff
  cmp #1
  bne Hidden
  lda Attributes,y
  sta Sprite_Attributes,x
  lda Tiles,y
  sta Sprite_Tilenumber,x
.if ::MAPPER_MMC3
  and #1
  bne Next
  lda Sprite_Y_Position,x
  cmp #32
  bcc MarkMixedHud
  cmp #224
  bcc Next
  cmp #240
  bcs Next
MarkMixedHud:
  inc GuestHudMixed
.endif
  jmp Next
Hidden:
  lda #$f8
  sta Sprite_Y_Position,x
Next:
  txa
  clc
  adc #4
  sta R4
  rts

; Reverse order matches MetaspriteRenderLoop exactly: overlay before base.
Tiles:
  .byte MetaspriteVramOffset{$3a},{SPRITE_BANK_4}, MetaspriteVramOffset{$38},{SPRITE_BANK_4}
  .byte MetaspriteVramOffset{$3a},{SPRITE_BANK_4}, MetaspriteVramOffset{$38},{SPRITE_BANK_4}
  .byte MetaspriteVramOffset{$3e},{SPRITE_BANK_4}, MetaspriteVramOffset{$3c},{SPRITE_BANK_4}
  .byte MetaspriteVramOffset{$3e},{SPRITE_BANK_4}, MetaspriteVramOffset{$3c},{SPRITE_BANK_4}
Attributes: .byte $c2,$c0,$82,$80, $c2,$c2,$82,$82
XOffsets:   .byte   0, -4, -8, -4,   3, -5,-11, -3
YOffsets:   .byte  -1, -3, -1, -3,  -4, -4, -4, -4
.endproc
.popseg
