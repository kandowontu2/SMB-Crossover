; Only TnWorldDraw calls this helper. All linked world records have signed
; X offsets -8..0 and Y offsets -24..0. Keep general clipping/capacity handling
; at the edges. No additional RAM, sprites, CHR pages or gameplay state.
.pushseg
.segment "TMNT_CORE"
.proc TnFastWorldRender
.if ::MAPPER_MMC3
 farcall MetaspriteRenderLoop,jmp
.else
 lda R5
 bne Legacy
 lda R7
 cmp #1
 bne Legacy
 lda R4
 cmp #8
 bcc Legacy
 lda R6
 cmp #24
::TnHudWorldBranch:
 bcc TnHudWorldRender
 lda R3
 and #3                        ; preserve source records' fixed palettes
 bne Legacy
 ldx CurrentOAMOffset
 ldy #0
 lda (R0),y
 beq Empty
 bmi Legacy                    ; generic owns unusual/rejected headers
 tay
 and #3
 bne Legacy
 tya
 clc
 adc CurrentOAMOffset
 bcs Legacy
 lda GuestOamRotationActive
 beq Start
 txa
 clc
 adc RgOamRotation
 tax
Start:
Loop:
 lda (R0),y
 clc
 adc R4
 sta Sprite_X_Position,x
 dey
 lda (R0),y
 clc
 adc R6
 sta Sprite_Y_Position,x
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
 bne Loop
 clv                           ; same final valid Y-page ADC overflow flag
 txa
 ldy GuestOamRotationActive
 beq Save
 sec
 sbc RgOamRotation
Save:
 sta CurrentOAMOffset
 ldy #0
 sec
 rts
Empty:
 clc
 rts
Legacy:
 farcall MetaspriteRenderLoop,jmp
.endif
.endproc
.export TnFastWorldRender
.popseg
