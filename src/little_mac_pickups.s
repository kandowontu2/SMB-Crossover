.pushseg
.segment "LM_CORE"
.proc LmPrepareGate
 LmGate NrPrepare
 stx InvObject
 jsr LmEnsure
 ldx InvObject
 lda #0
 sta InvRisePhase,x
 sta InvPickupSaveLo,x
 sta LmStamp,x
 lda #15
 sta InvPickupOwner,x
 lda PowerUpType,x
 cmp #2
 bcs Vanilla
 lda #$e0
 ldy PowerUpType,x
 beq Stamp
 lda #$e1
Stamp:sta LmStamp,x
 sta InvPickup,x
 rts
Vanilla:lda #$fc
 sta InvPickup,x
 rts
.endproc
.proc LmCollectGate
 LmGate Cv3CollectPickupGate
 lda InvPickupOwner,x
 cmp #15
 bne No
 lda LmStamp,x
 cmp #$e0
 beq Heal
 cmp #$e1
 bne No
 lda LmStars
 cmp #3
 bcs Sound
 inc LmStars
 bne Sound
Heal:lda LmHealth
 clc
 adc #24
 cmp #97
 bcc :+
 lda #96
:sta LmHealth
Sound:lda #1
 sta PlayerStatus
 sta LmDirty
 lda #Sfx_PowerUpGrab
 sta Square2SoundQueue
 lda #0
 sta InvPickup,x
 sta LmStamp,x
 sec
 rts
No:clc
 rts
.endproc
.proc LmIsStar
 lda Enemy_Flag,x
 beq No
 lda Enemy_ID,x
 cmp #PowerUpObject
 bne No
 lda PowerUpType,x
 cmp #1
 bne No
 lda InvPickupOwner,x
 cmp #15
 bne No
 lda LmStamp,x
 cmp #$e1
 bne No
 sec
 rts
No:clc
 rts
.endproc
.proc LmPrivateGate
 LmGate NrPrivate
 jmp LmIsStar
.endproc
.proc LmRiseGate
 LmGate NrRise
 farcall InventoryRisePickup
 php
 lda LmStamp,x
 cmp #$e0
 bne Done
 lda Enemy_State,x
 bpl Done
 lda #1
 sta Enemy_MovingDir,x
 lda #$10
 sta Enemy_X_Speed,x
Done:plp
 rts
.endproc
.proc LmSupportedGate
 LmGate Cv3SupportedGate
 sec
 rts
.endproc
.proc LmLegacyGate
 LmGate Cv3LegacyGate
 sec
 rts
.endproc
.popseg
