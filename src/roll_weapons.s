.pushseg
.segment "ROLL_CORE"
.proc RlWeapons
 lda TimerControl
 jne Done
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda MmDeathFlag
 jne Done
 jsr RlEnsure
 lda ObjectOffset
 sta RlSavedObject
 inc MmWorldTime
 bne :+
 inc MmWorldTime+1
:ldx #5
Flash:lda MmEnemyFlash,x
 beq :+
 dec MmEnemyFlash,x
:dex
 bpl Flash
 lda RlHurt
 bne ResetCharge
 lda SavedJoypadBits
 and #B_Button
 beq ResetCharge
 lda RlFresh
 and #B_Button
 beq Charge
 ldy #0
 ldx #3
Count:lda MmBulletType,x
 cmp #1
 bne :+
 iny
:dex
 bpl Count
 cpy #3
 bcs Charge
 lda #1
 jsr Spawn
Charge:lda RlEnergy
 cmp #4
 bcc ResetCharge
 lda RlCharge
 cmp #60
 bcs Charged
 inc RlCharge
 jmp Update
Charged:
 lda #3
 jsr Spawn
 bcc Update
 lda RlEnergy
 sec
 sbc #4
 sta RlEnergy
 inc RlDirty
 inc RlChargeFired
ResetCharge:
 lda #0
 sta RlCharge
Update:
 lda #0
 sta RlEnemyEnvelope
 ldx #3
Loop:stx MmSlot
 lda MmBulletType,x
 beq Next
 inc MmBulletAge,x
 farcall MegaManWeapons::Move
 ldx MmSlot
 lda MmBulletType,x
 beq Next
 jsr RlBlocks
 ldx MmSlot
 lda MmBulletType,x
 beq Next
 jsr RlEnemies
Next:ldx MmSlot
 dex
 bpl Loop
 ; ProcFireball_Bubble already owns shared drop updates before weapons.
 ; Preserve the old farcall macro span and all subsequent public PCs.
 .res 18,$ea
 lda RlSavedObject
 sta ObjectOffset
Done:rts
Spawn:
 sta RlTemp
 lda Player_Y_HighPos
 cmp #1
 bne Rejected
 ldx #3
Find:lda MmBulletType,x
 beq Free
 dex
 bpl Find
Rejected:
 clc
 rts
Free:lda RlTemp
 sta MmBulletType,x
 lda #0
 sta MmBulletAge,x
 sta MmBulletFracLo,x
 sta MmBulletFracHi,x
 lda PlayerFacingDir
 sta MmBulletDir,x
 lda Player_X_Position
 clc
 adc #27
 sta MmBulletX,x
 lda Player_PageLoc
 adc #0
 sta MmBulletPage,x
 lda PlayerFacingDir
 cmp #2
 bne ShotY
 lda Player_X_Position
 sec
 sbc #11
 sta MmBulletX,x
 lda Player_PageLoc
 sbc #0
 sta MmBulletPage,x
ShotY:lda Player_Y_Position
 clc
 adc #17
 bcs BadY
 sta MmBulletY,x
 lda #12
 sta RlAttack
 lda #Sfx_Fireball
 sta Square1SoundQueue
 sec
 rts
BadY:lda #0
 sta MmBulletType,x
 clc
 rts
.endproc
.popseg
