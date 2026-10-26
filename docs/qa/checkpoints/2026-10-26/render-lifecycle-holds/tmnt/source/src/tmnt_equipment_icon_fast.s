; Private icon-call entry: the caller retains the exact original
; fixed coordinates/palette/page setup. Original fallback is literal.
.pushseg
.segment "TN_EQUIP_FAST"
.proc TnExactIconRender
EmitterStart:
 ; Only the original icon JSR calls here: X is its immutable right
 ; table index (Equipment+79), and R4/R5/R6/R7/R3=128/0/23/1/0.
 lda CurrentOAMOffset
 cmp #240
 bcs Legacy
 cpx #80
 beq Icon0Gate
 cpx #81
 beq Icon1Gate
 cpx #82
 beq Icon2Gate
 cpx #83
 beq Icon3Gate
Legacy:
 jmp TnWorldDraw
Icon0Gate:
 jmp Icon0
Icon1Gate:
 jmp Icon1
Icon2Gate:
 jmp Icon2
Icon3Gate:
 jmp Icon3
Icon0:
 ldx CurrentOAMOffset
 lda GuestOamRotationActive
 beq Draw0
 txa
 clc
 adc RgOamRotation
 tax
Draw0:
 lda #120
 sta Sprite_X_Position,x
 lda #7
 sta Sprite_Y_Position,x
 lda #3
 sta Sprite_Attributes,x
 lda #13
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 lda #120
 sta Sprite_X_Position,x
 lda #7
 sta Sprite_Y_Position,x
 lda #2
 sta Sprite_Attributes,x
 lda #15
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 lda #128
 sta Sprite_X_Position,x
 lda #7
 sta Sprite_Y_Position,x
 lda #3
 sta Sprite_Attributes,x
 lda #17
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 lda #128
 sta Sprite_X_Position,x
 lda #7
 sta Sprite_Y_Position,x
 lda #2
 sta Sprite_Attributes,x
 lda #19
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 clv
 txa
 ldy GuestOamRotationActive
 beq Save0
 sec
 sbc RgOamRotation
Save0:
 sta CurrentOAMOffset
 ldy #0
 ora #0
 sec
 BankPRGC #.bank(TnWorldArtStart)
 rts
Legacy0:
 jmp TnWorldDraw
Icon1:
 ldx CurrentOAMOffset
 lda GuestOamRotationActive
 beq Draw1
 txa
 clc
 adc RgOamRotation
 tax
Draw1:
 lda #120
 sta Sprite_X_Position,x
 lda #7
 sta Sprite_Y_Position,x
 lda #3
 sta Sprite_Attributes,x
 lda #21
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 lda #120
 sta Sprite_X_Position,x
 lda #7
 sta Sprite_Y_Position,x
 lda #2
 sta Sprite_Attributes,x
 lda #23
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 lda #128
 sta Sprite_X_Position,x
 lda #7
 sta Sprite_Y_Position,x
 lda #3
 sta Sprite_Attributes,x
 lda #25
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 lda #128
 sta Sprite_X_Position,x
 lda #7
 sta Sprite_Y_Position,x
 lda #2
 sta Sprite_Attributes,x
 lda #27
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 clv
 txa
 ldy GuestOamRotationActive
 beq Save1
 sec
 sbc RgOamRotation
Save1:
 sta CurrentOAMOffset
 ldy #0
 ora #0
 sec
 BankPRGC #.bank(TnWorldArtStart)
 rts
Legacy1:
 jmp TnWorldDraw
Icon2:
 ldx CurrentOAMOffset
 lda GuestOamRotationActive
 beq Draw2
 txa
 clc
 adc RgOamRotation
 tax
Draw2:
 lda #120
 sta Sprite_X_Position,x
 lda #7
 sta Sprite_Y_Position,x
 lda #3
 sta Sprite_Attributes,x
 lda #29
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 lda #120
 sta Sprite_X_Position,x
 lda #7
 sta Sprite_Y_Position,x
 lda #2
 sta Sprite_Attributes,x
 lda #31
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 lda #128
 sta Sprite_X_Position,x
 lda #7
 sta Sprite_Y_Position,x
 lda #3
 sta Sprite_Attributes,x
 lda #33
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 lda #128
 sta Sprite_X_Position,x
 lda #7
 sta Sprite_Y_Position,x
 lda #2
 sta Sprite_Attributes,x
 lda #35
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 clv
 txa
 ldy GuestOamRotationActive
 beq Save2
 sec
 sbc RgOamRotation
Save2:
 sta CurrentOAMOffset
 ldy #0
 ora #0
 sec
 BankPRGC #.bank(TnWorldArtStart)
 rts
Legacy2:
 jmp TnWorldDraw
Icon3:
 ldx CurrentOAMOffset
 lda GuestOamRotationActive
 beq Draw3
 txa
 clc
 adc RgOamRotation
 tax
Draw3:
 lda #120
 sta Sprite_X_Position,x
 lda #7
 sta Sprite_Y_Position,x
 lda #3
 sta Sprite_Attributes,x
 lda #37
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 lda #120
 sta Sprite_X_Position,x
 lda #7
 sta Sprite_Y_Position,x
 lda #2
 sta Sprite_Attributes,x
 lda #39
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 lda #128
 sta Sprite_X_Position,x
 lda #7
 sta Sprite_Y_Position,x
 lda #3
 sta Sprite_Attributes,x
 lda #41
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 lda #128
 sta Sprite_X_Position,x
 lda #7
 sta Sprite_Y_Position,x
 lda #2
 sta Sprite_Attributes,x
 lda #43
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 clv
 txa
 ldy GuestOamRotationActive
 beq Save3
 sec
 sbc RgOamRotation
Save3:
 sta CurrentOAMOffset
 ldy #0
 ora #0
 sec
 BankPRGC #.bank(TnWorldArtStart)
 rts
Legacy3:
 jmp TnWorldDraw
 .res 655-(*-EmitterStart),$ff ; preserve this private helper footprint
.endproc
.assert TnExactIconRender=$b700,lderror,"Only declared new A87 tail"
.assert *<=$c000,lderror,"Keep fixed bank layout"
.export TnExactIconRender
.popseg
