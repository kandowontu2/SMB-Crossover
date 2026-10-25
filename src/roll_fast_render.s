; Interior Roll records have fixed palettes and audited signed offsets. Keep
; the general renderer for edges, menus and rejected/capacity-limited records.
.pushseg
.segment "DARKWING_DRAW_GUARD"
.proc RlNativeRenderDispatch
 lda RlOutlineBypass
 beq Legacy
 lda GameEngineSubroutine
 cmp #8
 bne Legacy
 lda R0
 cmp SmPosePtr
 bne Legacy
 lda R1
 cmp SmPosePtr+1
 bne Legacy
 farcall RlFastBodyRender,jmp
Legacy:jmp NativeGoombaRender
.endproc
.assert *-RlNativeRenderDispatch=46,error,"Roll admission uses reclaimed draw-guard space"
.segment "ROLL_CORE"
.proc RlFastBodyRender
 lda R6
 cmp #192
 bcs RlRenderFallback
 ; Body records can extend32 pixels below their origin.
 bcc RlFastShotRender
.endproc
.proc RlFastShotRender
 lda R5
 bne RlRenderFallback
 lda R7
 cmp #1
 bne RlRenderFallback
 lda R4
 cmp #32
 bcc RlRenderFallback
 cmp #208
 bcs RlRenderFallback
 lda R6
 cmp #48
 bcc RlRenderFallback
 cmp #224
 bcs RlRenderFallback
 jmp RlFastRenderLoop
.endproc
RlRenderFallback:
 farcall MetaspriteRenderLoop,jmp
.proc RlFastRenderLoop
 ldx CurrentOAMOffset
 ldy #0
 lda (R0),y
 beq Empty
 sta RlRenderLength
 and #3
 bne RlRenderFallback
 lda RlRenderLength
 clc
 adc CurrentOAMOffset
 bcs RlRenderFallback
 lda GuestOamRotationActive
 beq Start
 txa
 clc
 adc RgOamRotation
 tax
Start:ldy RlRenderLength
Loop:lda (R0),y
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
 clv                            ; Generic's final Y-page ADC clears V here.
 txa
 ldy GuestOamRotationActive
 beq Save
 sec
 sbc RgOamRotation
Save:sta CurrentOAMOffset
 ldy #0
 sec
 rts
Empty:clc
 rts
.endproc
.popseg
