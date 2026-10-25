; Only TnDraw::RenderHealth calls this private renderer, immediately after
; setting Ptr=$5ca0, X=80/page0, Y=7. Retain dynamic tiles and validate every
; cached coordinate/attribute before using the fixed four-cell composition.
.pushseg
.segment "TMNT_COMBAT"
.proc TnHealthRender
 lda #1
 sta R7
 lda #0
 sta R3
.if ::MAPPER_MMC3
 farcall MetaspriteRenderLoop,jmp
.else
 ldx CurrentOAMOffset
 ldy #0
 lda $5ca0
 cmp #16
 jne Legacy
 clc
 adc CurrentOAMOffset
 jcs Legacy
 lda $5ca2
 ora $5ca3
 ora $5ca6
 ora $5ca7
 ora $5caa
 ora $5cab
 ora $5cae
 ora $5caf
 jne Legacy
 lda $5ca4
 jne Legacy
 lda $5ca8
 cmp #8
 jne Legacy
 lda $5cac
 cmp #16
 jne Legacy
 lda $5cb0
 cmp #24
 jne Legacy
 lda GuestOamRotationActive
 beq Render
 txa
 clc
 adc RgOamRotation
 tax
Render:
 .repeat 4,I
  lda #80+(3-I)*8
  sta Sprite_X_Position,x
  lda #7
  sta Sprite_Y_Position,x
  lda #0
  sta Sprite_Attributes,x
  lda $5ca1+(3-I)*4
  sta Sprite_Tilenumber,x
  inx
  inx
  inx
  inx
 .endrepeat
 clv                           ; Original final main-page Y ADC clears V.
 txa
 ldy GuestOamRotationActive
 beq Save
 sec
 sbc RgOamRotation
Save:
 sta CurrentOAMOffset
 ldy #0
 ora #0                        ; Old farcall's final PLA sets N/Z from A.
 sec
 rts
Legacy:
 farcall MetaspriteRenderLoop,jmp
.endif
.endproc
.export TnHealthRender
.popseg
