; Draw only through the authenticated Sonic row-2 OAM owner. DrawIndex,
; DrawFlip and DrawAttr are the existing body's scratch after MetaDraw.
.setcpu "6502"
.segment "RING_FEEDBACK"

SparkTick:
 php
 pha
 lda SparkTimer
 beq SparkContinue
 dec SparkTimer
SparkContinue:
 pla
 plp
 jmp RingProject

DrawFeedback:
 jsr MetaDraw
 lda OperMode
 cmp #1
 bne DrawDone
 lda OperMode_Task
 cmp #3
 bne DrawDone
 lda WorldNumber
 ora LevelNumber
 bne DrawDone
 lda AreaAddrsLOffset
 cmp #5
 bne DrawDone
 lda HostReady
 beq DrawDone
 lda GameEngineSubroutine
 cmp #8
 beq DrawOrdinary
 cmp #9
 bne DrawDone
DrawOrdinary:
 jsr DrawHud
 jsr DrawWorld
 jsr DrawSparkle
 jsr DrawDrop
DrawDone:
 sec
 rts

DrawHud:
 lda CurrentOAMOffset
 cmp #237
 bcs HudDone
 lda #34
 sta DrawFlip
 lda #glyphs0
 ldy #208
 jsr Emit
 lda #glyphs1
 ldy #216
 jsr Emit
 lda RingBCD
 lsr
 lsr
 lsr
 lsr
 tax
 lda digits,x
 ldy #224
 jsr Emit
 lda RingBCD
 and #$0f
 tax
 lda digits,x
 ldy #232
 jmp Emit
HudDone:
 rts

DrawWorld:
 lda #167
 sta DrawFlip
 lda #world1
 sta DrawAttr
 lda #0
 sta DrawIndex
WorldNext:
 ldx DrawIndex
 txa
 eor FrameCounter
 and #1
 bne WorldSkip
 ldy WorldCells,x
 lda SceneTiles,y
 and WorldBits,x
 beq WorldSkip
 lda WorldLow,x
 sec
 sbc ScreenLeft_X_Pos
 tay
 lda WorldHigh,x
 sbc ScreenLeft_PageLoc
 bne WorldSkip
 lda #world0
 jsr EmitPair
WorldSkip:
 inc DrawIndex
 lda DrawIndex
 cmp #5
 bcc WorldNext
 rts
WorldCells: .byte 0,1,1,2,2
WorldBits: .byte 2,1,2,1,2
WorldLow: .byte 208,224,240,0,16
WorldHigh: .byte 0,0,0,1,1

DrawSparkle:
 lda SparkTimer
 beq SparkDone
 lda SparkY+1
 bne SparkDone
 lda SparkY
 cmp #35
 bcc SparkDone
 cmp #222
 bcs SparkDone
 sec
 sbc #3
 sta DrawFlip
 lda SparkX
 sec
 sbc ScreenLeft_X_Pos
 tay
 lda SparkX+1
 sbc ScreenLeft_PageLoc
 bne SparkDone
 cpy #249
 bcs SparkDone
 lda SparkTimer
 cmp #4
 bcc SparkFirst
 lda #spark1
 jsr Emit
 tya
 clc
 adc #8
 bcs SparkDone
 tay
 lda DrawFlip
 clc
 adc #4
 sta DrawFlip
SparkFirst:
 lda #spark0
 jmp Emit
SparkDone:
 rts

DrawDrop:
 lda DropRecord
 cmp #$55
 bne DropDone
 lda DropRecord+15
 beq DropDone
 lda DropRecord+6
 bne DropDone
 lda DropRecord+5
 cmp #33
 bcc DropDone
 cmp #225
 bcs DropDone
 sec
 sbc #1
 sta DrawFlip
 lda DropRecord+2
 sec
 sbc ScreenLeft_X_Pos
 tay
 lda DropRecord+3
 sbc ScreenLeft_PageLoc
 bne DropDone
 ; $7B95 writes the actual pointer before advancing its pose. The low
 ; pointer selects one of three forms within the displayed six-slot art.
 ldx #0
 lda DropRecord+15
 cmp #$29
 beq DropArtBase
 inx
 inx
 cmp #$31
 beq DropArtBase
 inx
 inx
DropArtBase:
 lda DropRecord+17
 cmp #6
 bne DropPhaseCurrent
 lda DropRecord+18
 bne DropPhasePrior
 lda #5
 bne DropPhaseGroup
DropPhasePrior:
 sec
 sbc #1
 jmp DropPhaseGroup
DropPhaseCurrent:
 lda DropRecord+18
DropPhaseGroup:
 cmp #3
 bcc DropFirstArt
 txa
 clc
 adc #6
 tax
DropFirstArt:
 lda drops+1,x
 sta DrawAttr
 lda drops,x
 jmp EmitPair
DropDone:
 rts

EmitPair:
 cpy #241
 bcs PairDone
 ldx CurrentOAMOffset
 cpx #245
 bcs PairDone
 jsr Emit
 tya
 clc
 adc #8
 tay
 lda DrawAttr
 jmp Emit
PairDone:
 rts

Emit:
 cmp #255
 beq EmitBlank
 pha
 ldx CurrentOAMOffset
 cpx #252
 bcs EmitFull
 lda GuestOamRotationActive
 beq EmitAt
 txa
 clc
 adc RgOamRotation
 tax
EmitAt:
 pla
 sta Sprite_Tilenumber,x
 lda DrawFlip
 sta Sprite_Y_Position,x
 lda #2
 sta Sprite_Attributes,x
 tya
 sta Sprite_X_Position,x
 lda CurrentOAMOffset
 clc
 adc #4
 sta CurrentOAMOffset
 rts
EmitFull:
 pla
EmitBlank:
 rts
