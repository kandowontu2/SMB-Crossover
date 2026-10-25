; Water50-only MM/Bass enemy consumer. Exact native live predicates and
; original inclusive/wrapping SprObjectCollisionCore; no cached geometry.
; The original DamageEnemy owns all injury, armor, stun, defeat and sound.
.pushseg
.segment "WATER_ENEMY_COLD"
; Direct A-window view of the original bank$24 FF tail; old C graphics fixed.
.proc WaterShieldEnemies
  lda MmBulletX,x
  sec
  sbc ScreenLeft_X_Pos
  sta MmTemp
  ldy #50
  lda #4                       ; Literal original RadiusX[49] / RadiusY[49].
  sta MmDamage
  lda MmTemp
  sec
  sbc MmDamage
  sta BoundingBox_UL_Corner+28
  lda MmTemp
  clc
  adc MmDamage
  sta BoundingBox_LR_Corner+28
  lda #4
  sta MmDamage
  lda MmBulletY,x
  sec
  sbc MmDamage
  sta BoundingBox_UL_Corner+29
  lda MmBulletY,x
  clc
  adc MmDamage
  sta BoundingBox_LR_Corner+29
  ; Old MM/Bass dispatch's SEC/SBC/compare sequence leaves V=0.
  clv
  ldx #5
Loop:
  stx MmEnemySlot
  ; Old per-slot character comparisons end with MM/Bass < SOPHIA: C=0.
  clc
  lda Enemy_Flag,x
  jeq Next
  jmi Next
  lda Enemy_State,x
  and #$20
  jne Next
  lda Enemy_ID,x
  cmp #$15
  bcc Check
  cmp #BulletBill_CannonVar
  beq Check
  cmp #Bowser
  jne Next
Check:
  cmp #Goomba
  bne Visible
  lda Enemy_State,x
  cmp #2
  jcs Next
Visible:
  lda EnemyOffscrBitsMasked,x
  jne Next
  ldy SelectedCharacter
  ; Original MM/Bass path skips Bill and Ryu body alternatives.
  lda Enemy_X_Position,x
  sec
  sbc ScreenLeft_X_Pos
  sta BoundingBox_UL_Corner+32
  clc
  adc #16
  sta BoundingBox_LR_Corner+32
  lda Enemy_Y_Position,x
  clc
  adc #8
  sta BoundingBox_UL_Corner+33
  clc
  adc #16
  sta BoundingBox_LR_Corner+33
  ldy #28
  ldx #32
  jsr SprObjectCollisionCore
  bcc Next
  ldx MmEnemySlot
  farcall MegaManWeapons::DamageEnemy
  ldx MmSlot
  lda MmBulletType,x
  beq Done
Next:
  ldx MmEnemySlot
  dex
  jpl Loop
Done:
  rts
.endproc
.popseg
