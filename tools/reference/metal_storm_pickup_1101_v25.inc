; Mushroom is the SMB adaptation of original Metal Storm armor item E8BE.
; Star/1UP retain the native Mario collectible behavior. Weapon items follow.
Ms25Pickup:
 cpx #6
 bcs Ms25No
 lda $c800
 cmp #$a7
 bne Ms25No
 lda Enemy_Flag,x
 beq Ms25No
 lda Enemy_ID,x
 cmp #$2e
 bne Ms25No
 lda Enemy_State,x
 bpl Ms25No
 lda PowerUpType,x
 cmp #2
 bcs Ms25Native
 cmp #0
 bne Ms25No
 ; Original E8BE..E8CD state writes, with host collection effects below.
 lda #$80
 sta MsState+$5d0
 lda #$30
 sta MsState+$528
 lda #$0a
 sta MsState+$7e7
 lda #1
 sta PlayerStatus
 lda #0
 sta PlayerSize
 lda #Sfx_PowerUpGrab
 sta Square2SoundQueue
 jsr EraseEnemyObject
 lda #0
 sta InvPickupOwner,x
 sta InvPickup,x
 sta InvRisePhase,x
 sta InvPickupSaveLo,x
 sta InvPickupSaveHi,x
 lda #6
 jsr SetupFloateyNumber
 sec
 rts
Ms25No:clc
 rts
Ms25Native:
 MsRFar MarioSourcePowerupCollision,MS25_NATIVE_PICKUP_BANK
 sec
 rts
