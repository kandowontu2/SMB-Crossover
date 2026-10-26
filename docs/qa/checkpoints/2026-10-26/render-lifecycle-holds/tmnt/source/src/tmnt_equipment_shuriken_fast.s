; Private source ShotPointer caller sets attr0/page1 and restores C88.
; Exact original two palette layers; all unknown/edge/capacity paths legacy.
.pushseg
.segment "TN_EQUIP_FAST"
.proc TnExactShurikenRender
EmitterStart:
 ; Caller retains X=shot slot; R7=1 and R3=0 are fixed before this JSR.
 ; EOR preserves original C/V for the earliest legacy page rejection.
 lda TnShotKind,x
 eor #2
 bne Legacy
 lda R5
 bne Legacy
 lda CurrentOAMOffset
 cmp #248
 bcs Legacy
 lda R4
 cmp #8
 bcc Legacy
 lda R6
 cmp #24
 bcc Legacy
 lda R1
 cmp #$d1
 beq Right
 cmp #$d2
 bne Legacy
 lda R0
 cmp #$cb
 beq Record3Gate
 cmp #$d4
 beq Record4Gate
 cmp #$dd
 beq Record5Gate
 jmp Legacy
Right:
 lda R0
 cmp #$66
 beq Record0Gate
 cmp #$6f
 beq Record1Gate
 cmp #$78
 beq Record2Gate
Legacy:
 jmp TnWorldDraw
Record0Gate:
 jmp Record0
Record1Gate:
 jmp Record1
Record2Gate:
 jmp Record2
Record3Gate:
 jmp Record3
Record4Gate:
 jmp Record4
Record5Gate:
 jmp Record5
Record0:
 ldx CurrentOAMOffset
 lda GuestOamRotationActive
 beq Draw0
 txa
 clc
 adc RgOamRotation
 tax
Draw0:
 lda R4
 sec
 sbc #4
 sta Sprite_X_Position,x
 lda R6
 sec
 sbc #8
 sta Sprite_Y_Position,x
 lda #3
 sta Sprite_Attributes,x
 lda #9
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 lda R4
 sec
 sbc #4
 sta Sprite_X_Position,x
 lda R6
 sec
 sbc #8
 sta Sprite_Y_Position,x
 lda #2
 sta Sprite_Attributes,x
 lda #11
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
 sec
 BankPRGC #.bank(TnWorldArtStart)
 rts
Record1:
 ldx CurrentOAMOffset
 lda GuestOamRotationActive
 beq Draw1
 txa
 clc
 adc RgOamRotation
 tax
Draw1:
 lda R4
 sec
 sbc #4
 sta Sprite_X_Position,x
 lda R6
 sec
 sbc #8
 sta Sprite_Y_Position,x
 lda #67
 sta Sprite_Attributes,x
 lda #9
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 lda R4
 sec
 sbc #4
 sta Sprite_X_Position,x
 lda R6
 sec
 sbc #8
 sta Sprite_Y_Position,x
 lda #66
 sta Sprite_Attributes,x
 lda #11
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
 sec
 BankPRGC #.bank(TnWorldArtStart)
 rts
Record2:
 ldx CurrentOAMOffset
 lda GuestOamRotationActive
 beq Draw2
 txa
 clc
 adc RgOamRotation
 tax
Draw2:
 lda R4
 sec
 sbc #4
 sta Sprite_X_Position,x
 lda R6
 sec
 sbc #8
 sta Sprite_Y_Position,x
 lda #195
 sta Sprite_Attributes,x
 lda #9
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 lda R4
 sec
 sbc #4
 sta Sprite_X_Position,x
 lda R6
 sec
 sbc #8
 sta Sprite_Y_Position,x
 lda #194
 sta Sprite_Attributes,x
 lda #11
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
 sec
 BankPRGC #.bank(TnWorldArtStart)
 rts
Record3:
 ldx CurrentOAMOffset
 lda GuestOamRotationActive
 beq Draw3
 txa
 clc
 adc RgOamRotation
 tax
Draw3:
 lda R4
 sec
 sbc #4
 sta Sprite_X_Position,x
 lda R6
 sec
 sbc #8
 sta Sprite_Y_Position,x
 lda #67
 sta Sprite_Attributes,x
 lda #9
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 lda R4
 sec
 sbc #4
 sta Sprite_X_Position,x
 lda R6
 sec
 sbc #8
 sta Sprite_Y_Position,x
 lda #66
 sta Sprite_Attributes,x
 lda #11
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
 sec
 BankPRGC #.bank(TnWorldArtStart)
 rts
Record4:
 ldx CurrentOAMOffset
 lda GuestOamRotationActive
 beq Draw4
 txa
 clc
 adc RgOamRotation
 tax
Draw4:
 lda R4
 sec
 sbc #4
 sta Sprite_X_Position,x
 lda R6
 sec
 sbc #8
 sta Sprite_Y_Position,x
 lda #3
 sta Sprite_Attributes,x
 lda #9
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 lda R4
 sec
 sbc #4
 sta Sprite_X_Position,x
 lda R6
 sec
 sbc #8
 sta Sprite_Y_Position,x
 lda #2
 sta Sprite_Attributes,x
 lda #11
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 clv
 txa
 ldy GuestOamRotationActive
 beq Save4
 sec
 sbc RgOamRotation
Save4:
 sta CurrentOAMOffset
 ldy #0
 sec
 BankPRGC #.bank(TnWorldArtStart)
 rts
Record5:
 ldx CurrentOAMOffset
 lda GuestOamRotationActive
 beq Draw5
 txa
 clc
 adc RgOamRotation
 tax
Draw5:
 lda R4
 sec
 sbc #4
 sta Sprite_X_Position,x
 lda R6
 sec
 sbc #8
 sta Sprite_Y_Position,x
 lda #131
 sta Sprite_Attributes,x
 lda #9
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 lda R4
 sec
 sbc #4
 sta Sprite_X_Position,x
 lda R6
 sec
 sbc #8
 sta Sprite_Y_Position,x
 lda #130
 sta Sprite_Attributes,x
 lda #11
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 clv
 txa
 ldy GuestOamRotationActive
 beq Save5
 sec
 sbc RgOamRotation
Save5:
 sta CurrentOAMOffset
 ldy #0
 sec
 BankPRGC #.bank(TnWorldArtStart)
 rts
 .res 766-(*-EmitterStart),$ff ; preserve this private helper footprint
.endproc
.assert TnExactShurikenRender=$b98f,lderror,"Append only verified A87 tail"
.assert *<=$c000,lderror,"Keep fixed layout"
.export TnExactShurikenRender
.popseg
