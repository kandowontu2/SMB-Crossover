; Whole PN records can stream directly into OAM in the exact old rotated
; reverse-record order. Only PnDrawRecord admits these paths. Its generated
; record offsets stay in X[-24,24],Y[-64,64], palettes contain no software tags,
; and the entire record must fit both the native body/world reservation and
; the124-byte per-effect cap. Edges retain explicit clipping; truncated effects
; use the existing buffered path. Both paths leave the input record read-only.
.pushseg
.segment "ROLL_CORE"
.proc PnFastDrawRecord
 lda #0
 sta R3
 lda #1
 sta R7
 ldx CurrentOAMOffset
 lda GuestOamRotationActive
 beq Start
 txa
 clc
 adc RgOamRotation
 tax
Start:
 lda VvTemp                    ; Source dx offset of the last copied part.
 bne Index
 lda OutlineBytesLeft
Index:tay
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
 and #$f3
 sta Sprite_Attributes,x
 dey
 lda (R0),y
 sta Sprite_Tilenumber,x
 dey
 inx
 inx
 inx
 inx
 lda VvTemp2
 sec
 sbc #4
 sta VvTemp2
 beq Complete
 cpy #0
 bne Loop
 ldy OutlineBytesLeft
 bne Loop
Complete:
 clv
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
.endproc
.proc PnFastDrawClippedRecord
 ; A complete record can also bypass the copy near viewport edges. Apply
 ; the old copy's Y filter before emitting, then the generic X clipping.
 ; Records cut short by the OAM reservation still use the buffered path.
 lda #0
 sta R3
 lda #1
 sta R7
 ldx CurrentOAMOffset
 lda GuestOamRotationActive
 beq Start
 txa
 clc
 adc RgOamRotation
 tax
Start:
 lda VvTemp
 bne Index
 lda OutlineBytesLeft
Index:tay
Loop:
 dey
 lda (R0),y
 bmi NegativeY
 clc
 adc R6
 bcs HiddenY
 bcc CheckY
NegativeY:
 clc
 adc R6
 bcc HiddenY
CheckY:
 cmp #32
 bcc HiddenY
 cmp #240
 bcs HiddenY
 sta VvTemp
 iny
 clc
 lda (R0),y
 bpl PositiveX
 adc R4
 sta Sprite_X_Position,x
 lda R5
 adc #$ff
 beq VisibleX
 bne HiddenX
PositiveX:
 adc R4
 sta Sprite_X_Position,x
 lda R5
 adc #0
 bne HiddenX
VisibleX:
 dey
 lda VvTemp
 sta Sprite_Y_Position,x
 dey
 lda (R0),y
 and #$f3
 sta Sprite_Attributes,x
 dey
 lda (R0),y
 sta Sprite_Tilenumber,x
 dey
 jmp AdvanceOam
HiddenY:
 dey
 dey
 dey
 jmp Next
HiddenX:
 lda #$f8
 sta Sprite_Y_Position,x
 dey
 dey
 dey
 dey
AdvanceOam:
 inx
 inx
 inx
 inx
Next:
 lda VvTemp2
 sec
 sbc #4
 sta VvTemp2
 beq Complete
 cpy #0
 jne Loop
 ldy OutlineBytesLeft
 jmp Loop
Complete:
 clv
 txa
 ldy GuestOamRotationActive
 beq Save
 sec
 sbc RgOamRotation
Save:
 cmp CurrentOAMOffset
 beq Empty
 sta CurrentOAMOffset
 ldy #0
 sec
 rts
Empty:
 ; The old zero-length generic renderer returns the unrotated X cursor.
 ldx CurrentOAMOffset
 ldy #0
 lda #0
 clc
 rts
.endproc
.popseg
