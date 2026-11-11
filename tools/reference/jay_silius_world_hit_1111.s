.setcpu "6502"
.segment "WORLD_HIT"

; Enter after stock or spread flight resolves terrain and projection. The
; shot record holds unsigned world X in Q4. Use whole pixels, as the donor
; collision does after projection, and keep the native enemy page in the
; subtraction. The terrain query scratch is free after flight returns.
WorldHit:
 lda ShotRecords+9,x
 bne LiveShot
 rts
LiveShot:
 lda ShotRecords+1,x
 sta ProjectileX
 lda ShotRecords,x
 lsr a
 ror ProjectileX
 lsr a
 ror ProjectileX
 lsr a
 ror ProjectileX
 lsr a
 ror ProjectileX
 sta ProjectilePage
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

 ; The native Goomba center is left edge +8. Bias its signed delta by
 ; 19 so the strict 20-pixel bound is the unsigned interval 0..38.
 lda Enemy_X_Position,y
 clc
 adc #27
 sta DeltaX
 lda Enemy_PageLoc,y
 adc #0
 bcs SkipEnemy
 sta EnemyPage
 lda DeltaX
 sec
 sbc ProjectileX
 sta DeltaX
 lda EnemyPage
 sbc ProjectilePage
 bne SkipEnemy
 lda DeltaX
 cmp #39
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
 jsr CaptureAmmoDefeat
 pla
 sta ObjectOffset
 ldx ShotIndex
 lda #$1d
 jmp OriginalSoundRequest
SkipEnemy:
 dey
 bpl NextEnemy
 rts
