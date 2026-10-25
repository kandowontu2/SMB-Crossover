; Physical block contents are decided on reveal, granted only on collection.
.pushseg
.segment "MIKE_COMBAT"
.proc JnPreparePickup
 stx JnPickupSlot
 lda #0
 sta InvRisePhase,x
 lda #$fc
 sta InvPickup,x
 lda #CHARACTER_MIKE
 sta InvPickupOwner,x
 lda PowerUpType,x
 cmp #2
 jcs Done
 cmp #0
 jeq Heart
 lda JnOwnedTier
 cmp #3
 jcs Weapon
 clc
 adc #1
 jne Publish
Heart:lda #1
 jne Publish
Weapon:
 ldy #0
Find:lda JnAmmo,y
 jeq Found
 iny
 cpy #10
 jcc Find
 ; When every weapon is stocked, refill the currently selected weapon.
 ldy JnSelected
 jeq First
 dey
 jpl Found
First:ldy #0
Found:tya
 clc
 adc #4
Publish:ora #$80
 ldx JnPickupSlot
 sta InvPickup,x
 lda #1
 sta PowerUpType,x ; physical stationary item; no native grow or tier change.
Done:ldx JnPickupSlot
 rts
.endproc
.proc JnPrivatePickup
 lda SelectedCharacter
 cmp #CHARACTER_MIKE
 jne No
 lda Enemy_ID,x
 cmp #PowerUpObject
 jne No
 lda InvPickupOwner,x
 cmp #CHARACTER_MIKE
 jne No
 lda InvPickup,x
 cmp #$81
 jcc No
 cmp #$8e
 jcs No
 sec
 rts
No:clc
 rts
.endproc
.proc JnRisePickup
 jsr JnPrivatePickup
 jcc Done
 lda TimerControl
 jne Handled
 inc InvRisePhase,x
 lda InvRisePhase,x
 cmp #3
 jcc Handled
 lda #0
 sta InvRisePhase,x
 dec Enemy_Y_Position,x
 inc Enemy_State,x
 lda Enemy_State,x
 cmp #17
 jcc Handled
 lda #$80
 sta Enemy_State,x
 lda #0
 sta Enemy_X_Speed,x
 sta Enemy_SprAttrib,x
Handled:sec
Done:rts
.endproc
.proc JnPickupCollision
 jsr JnPrivatePickup
 jcc Allowed
 lda Enemy_State,x
 jmi Allowed
 cmp #2
 jcc Hidden
 txa
 asl
 asl
 tay
 lda Enemy_Y_Position,x
 clc
 adc #8
 sta EnemyBoundingBoxCoord+1,y
 lda Enemy_Y_Position,x
 clc
 adc Enemy_State,x
 adc #6
 sta EnemyBoundingBoxCoord+3,y
Allowed:sec
 rts
Hidden:clc
 rts
.endproc
.proc JnCollectPickup
 lda InvPickupOwner,x
 cmp #CHARACTER_MIKE
 jne No
 lda InvPickup,x
 cmp #$81
 jcc No
 cmp #$8e
 jcs No
 stx JnPickupSlot
 and #$7f
 cmp #1
 jne Tier
 lda JnMaxHearts
 cmp #22
 jcs Heal
 inc JnMaxHearts
Heal:lda JnMaxHearts
 asl
 sta JnHealth
 jmp Collected
Tier:cmp #4
 jcs Weapon
 cmp JnOwnedTier
 jcc Collected
 sta JnOwnedTier
 jmp Collected
Weapon:
 sec
 sbc #4
 tay
 lda AmmoRefill,y
 sta JnAmmo,y
 iny
 sty JnSelected
Collected:
 lda JnStars
 eor #$80
 sta JnStars
 lda #1
 sta JnUiDirty
 lda #Sfx_PowerUpGrab
 sta Square2SoundQueue
 ldx JnPickupSlot
 sec
 rts
No:clc
 rts
AmmoRefill:.byte 10,10,10,5,5,10,3,10,99,20
.endproc
.proc JnEnemyDrop
 stx JnSavedX
 lda JnDropReceipt,x
 jne Done
 lda #1
 sta JnDropReceipt,x
 ldy #3
Find:lda JnDropKind,y
 jeq Free
 dey
 jpl Find
 jmp Done
Free:
 lda PseudoRandomBitReg+1,x
 and #3
 cmp #0
 jeq Heart
 lda #2
 jne Store
Heart:lda #1
Store:sta JnDropKind,y
 lda Enemy_X_Position,x
 sta JnDropX,y
 lda Enemy_PageLoc,x
 sta JnDropPage,y
 lda Enemy_Y_Position,x
 clc
 adc #8
 sta JnDropY,y
 lda #0
 sta JnDropAge,y
Done:ldx JnSavedX
 rts
.endproc
.proc JnUpdateDrops
 ldx #3
Loop:
 stx JnSlot
 lda JnDropKind,x
 jeq Next
 inc JnDropAge,x
 lda JnDropAge,x
 cmp #240
 jcs Kill
 lda Player_X_Position
 sec
 sbc JnDropX,x
 sta JnTemp
 lda Player_PageLoc
 sbc JnDropPage,x
 sta JnTemp2
 lda JnTemp
 clc
 adc #12
 sta JnTemp
 lda JnTemp2
 adc #0
 jne Yoyo
 lda JnTemp
 cmp #25
 jcs Yoyo
 lda Player_Y_Position
 clc
 adc #16
 sec
 sbc JnDropY,x
 clc
 adc #24
 cmp #49
 jcc Collect
Yoyo:
 lda JnAttack
 cmp #6
 jcc Next
 lda JnWeapon
 cmp #4
 jcs Next
 lda Player_X_Position
 sec
 sbc JnDropX,x
 sta JnTemp
 lda Player_PageLoc
 sbc JnDropPage,x
 sta JnTemp2
 lda JnTemp
 clc
 adc #44
 sta JnTemp
 lda JnTemp2
 adc #0
 jne Next
 lda JnTemp
 cmp #89
 jcs Next
 lda Player_Y_Position
 clc
 adc #16
 sec
 sbc JnDropY,x
 clc
 adc #12
 cmp #25
 jcs Next
Collect:
 lda JnDropKind,x
 cmp #1
 jeq Heart
 lda JnStars
 and #7
 clc
 adc #1
 cmp #5
 jcc StoreStar
 lda #0
 sta JnTemp
 lda JnStars
 and #$80
 sta JnStars
 jmp Heart
StoreStar:sta JnTemp
 lda JnStars
 and #$80
 ora JnTemp
 sta JnStars
 jmp Sound
Heart:lda JnMaxHearts
 asl
 sta JnTemp
 lda JnHealth
 clc
 adc #2
 cmp JnTemp
 bcc :+
 lda JnTemp
:sta JnHealth
Sound:
 lda #1
 sta JnUiDirty
 lda #Sfx_PowerUpGrab
 sta Square2SoundQueue
Kill:
 ldx JnSlot
 lda #0
 sta JnDropKind,x
Next:ldx JnSlot
 dex
 jpl Loop
 rts
.endproc
.popseg
