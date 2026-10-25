; C-window art and this kernel are resident together. No extra bank trip.
; Admit only the actual immutable gameplay body table entry, with all of its
; audited signed offsets inside the visible page. Edges use the old renderer.
.pushseg
.segment "TMNT_GFX"
.proc TnBodyRender
 lda GameEngineSubroutine
 cmp #8
 jne Legacy
 lda R0
 cmp SmPosePtr
 jne Legacy
 lda R1
 cmp SmPosePtr+1
 jne Legacy
 ldx TnPose
 jeq Legacy
 cpx #99
 jcs Legacy
 lda PlayerFacingDir
 cmp #2
 beq Left
 lda TnBodyRLo,x
 cmp R0
 jne Legacy
 lda TnBodyRHi,x
 jmp Pointer
Left:
 lda TnBodyLLo,x
 cmp R0
 jne Legacy
 lda TnBodyLHi,x
Pointer:
 cmp R1
 jne Legacy
 lda R5
 jne Legacy
 lda R7
 cmp #1
 jne Legacy
 lda R4
 cmp #11
 jcc Legacy
 cmp #237
 jcs Legacy
 lda R6
 cmp #16
 jcc Legacy
 cmp #232
 jcs Legacy
 ldx CurrentOAMOffset
 ldy #0
 lda (R0),y
 jeq Legacy
 tay
 clc
 adc CurrentOAMOffset
 jcs Legacy
 lda GuestOamRotationActive
 beq Loop
 txa
 clc
 adc RgOamRotation
 tax
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
Legacy:
 jmp MetaspriteRenderLoop
.endproc
.export TnBodyRender
.popseg
