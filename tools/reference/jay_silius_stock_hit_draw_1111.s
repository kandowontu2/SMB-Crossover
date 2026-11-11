.setcpu "6502"

.segment "BULLET"
FlightAndHit:
 jsr StockFlight
 lda ShotRecords+9,x
 beq NoHit
 ; The donor enemy row 9 uses $E747 and 20-pixel strict bounds on
 ; both axes. Use the native Goomba center and its stock defeat ingress.
 ldy #5
NextEnemy:
 lda Enemy_Flag,y
 beq SkipEnemy
 bmi SkipEnemy
 lda Enemy_ID,y
 cmp #6
 bne SkipEnemy
 lda Enemy_State,y
 and #$20
 bne SkipEnemy
 lda Enemy_Y_HighPos,y
 cmp #1
 bne SkipEnemy
 lda Enemy_PageLoc,y
 bne SkipEnemy
 lda Enemy_X_Position,y
 clc
 adc #8
 bcs SkipEnemy
 sec
 sbc ShotRecords+6,x
 bcs CompareX
 eor #$ff
 clc
 adc #1
CompareX:
 cmp #20
 bcs SkipEnemy
 lda Enemy_Y_Position,y
 clc
 adc #8
 bcs SkipEnemy
 sec
 sbc ShotRecords+7,x
 bcs CompareY
 eor #$ff
 clc
 adc #1
CompareY:
 cmp #20
 bcs SkipEnemy
 lda #0
 sta ShotRecords+9,x
 stx ShotIndex
 lda ObjectOffset
 pha
 tya
 tax
 stx ObjectOffset
 jsr NativeDefeat
 pla
 sta ObjectOffset
 ldx ShotIndex
 lda #$1d
 jmp OriginalSoundRequest
SkipEnemy:
 dey
 bpl NextEnemy
NoHit:
 rts

; Native metasprite ABI. The one donor cell from bank 2 $83DA has
; offset -4/-8, palette 0 and an optional horizontal flip. The record
; lives in C2 so it survives the actual A4 rendering call.
DrawStock:
 ldx #$d0
DrawNext:
 stx ShotIndex
 lda ShotRecords+9,x
 beq DrawAdvance
 lda ShotRecords+8,x
 bne DrawAdvance
 lda ShotRecords+15,x
 cmp #1
 bne DrawAdvance
 lda #4
 sta ShotMetasprite
 lda #40
 sta ShotMetasprite+1
 lda ShotRecords+9,x
 and #2
 beq DrawFacing
 lda #$40
DrawFacing:
 sta ShotMetasprite+2
 lda #$f8
 sta ShotMetasprite+3
 lda #$fc
 sta ShotMetasprite+4
 lda #<ShotMetasprite
 sta $03
 lda #>ShotMetasprite
 sta $04
 lda #0
 sta $06
 sta $08
 lda ShotRecords+6,x
 sta $07
 lda ShotRecords+7,x
 sta $09
 lda #1
 sta $0a
 lda #<NativeRender
 sta $016c
 lda #>NativeRender
 sta $016d
 lda #$84
 jsr $015a
DrawAdvance:
 lda ShotIndex
 clc
 adc #$10
 tax
 bne DrawNext
 rts
