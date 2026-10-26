.pushseg
.segment "SOPHIA_WAVE_GATE"
.proc SophiaWaveGate
 lda SelectedCharacter
 cmp #CHARACTER_SOPHIA
 bne Fallback
 lda R1
 cmp #>XgSOPHIAWeapon4Right
 bne Fallback
 lda R0
 cmp #<XgSOPHIAWeapon4Right
 beq PointerReady
 cmp #<XgSOPHIAWeapon4Left
 bne Fallback
PointerReady:
 lda R3
 bne Fallback
 lda R5
 bne Fallback
 lda R7
 cmp #1
 bne Fallback
 lda R4
 cmp #12
 bcc Fallback
 cmp #252
 bcs Fallback
 lda R6
 cmp #3
 bcc Fallback
 lda CurrentOAMOffset
 cmp #244
 bcs Fallback
 tax
 lda GuestOamRotationActive
 beq PhysicalReady
 txa
 clc
 adc RgOamRotation
 tax
PhysicalReady:
 lda R0
 cmp #<XgSOPHIAWeapon4Right
 beq Right
 jmp SophiaWaveLeft
Right:
 jmp SophiaWaveRight
Fallback:
 jmp MetaspriteRenderLoop
.endproc
::SophiaWaveGateEnd:
.assert SophiaWaveGate=$bf33,error,"Fixed current3cee FF gate tail"
.assert *<=$bf8b,error,"Must not reach Darkwing draw owner"
.popseg
.pushseg
.segment "SOPHIA_WAVE_EMITTER"
.proc SophiaWaveLeft
 lda R4
 clc
 adc #$f4
 sta Sprite_X_Position,x
 lda R6
 clc
 adc #$fd
 sta Sprite_Y_Position,x
 lda #$80
 sta Sprite_Attributes,x
 lda #$06
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 lda R4
 clc
 adc #$fc
 sta Sprite_X_Position,x
 lda R6
 clc
 adc #$fd
 sta Sprite_Y_Position,x
 lda #$80
 sta Sprite_Attributes,x
 lda #$04
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 lda R4
 clc
 adc #$04
 sta Sprite_X_Position,x
 lda R6
 clc
 adc #$fd
 sta Sprite_Y_Position,x
 lda #$c0
 sta Sprite_Attributes,x
 lda #$02
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 jmp SophiaWaveTail
.endproc
.proc SophiaWaveRight
 lda R4
 clc
 adc #$04
 sta Sprite_X_Position,x
 lda R6
 clc
 adc #$fd
 sta Sprite_Y_Position,x
 lda #$c0
 sta Sprite_Attributes,x
 lda #$06
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 lda R4
 clc
 adc #$fc
 sta Sprite_X_Position,x
 lda R6
 clc
 adc #$fd
 sta Sprite_Y_Position,x
 lda #$c0
 sta Sprite_Attributes,x
 lda #$04
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
 lda R4
 clc
 adc #$f4
 sta Sprite_X_Position,x
 lda R6
 clc
 adc #$fd
 sta Sprite_Y_Position,x
 lda #$80
 sta Sprite_Attributes,x
 lda #$02
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
.endproc
::SophiaWaveTail:
 ; All admitted parts have Yhigh1 and -3<=Yoffset with no underflow.
 ; The native final Y-high ADC therefore leaves V0. Other flags are set by
 ; the identical cursor/rotation epilogue below, including decimal-bit carry.
 clv
 txa
 ldy GuestOamRotationActive
 beq :+
 sec
 sbc RgOamRotation
:
 sta CurrentOAMOffset
 ldy #0
 sec
 rts
::SophiaWaveEmitterEnd:
.assert SophiaWaveLeft=$d523,error,"Current3cee Sophia GFX FF tail"
.assert *<=$d600,error,"Bank36 A-window Water/Ryu/score code begins here"
.popseg
