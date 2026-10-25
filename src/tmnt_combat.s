; Cross-game targets use explicit SMB HP values, native turtle damage/reach.
TnEnemyHurt=$5c40
.pushseg
.segment "TMNT_COMBAT"
.proc TnWeaponPosition
 lda TnAttack
 jeq Done
 sec
 sbc #1
 tax
 BankPRGC #.bank(TnArtStart)
 lda TnAttackOffsetLo,x
 sta R0
 lda TnAttackOffsetHi,x
 sta R1
 ldy TnPhase+1
 lda (R0),y
 ldy PlayerFacingDir
 cpy #2
 bne Facing
 eor #$ff
 clc
 adc #1
Facing:sta TnTemp
 lda #0
 ldy TnTemp
 bpl :+
 lda #$ff
:sta TnTemp2
 clc
 lda TnTemp
 adc #8
 sta TnTemp
 lda TnTemp2
 adc #0
 sta TnTemp2
 clc
 lda Player_X_Position
 adc TnTemp
 sta TnWeaponX
 lda Player_PageLoc
 adc TnTemp2
 sta TnWeaponPage
 lda TnAttackOffsetYLo,x
 sta R0
 lda TnAttackOffsetYHi,x
 sta R1
 ldy TnPhase+1
 lda (R0),y
 clc
 adc #8
 clc
 adc Player_Y_Position
 sta TnWeaponY
 lda TnSeq+1
 sec
 sbc #$9c
 tax
 lda TnWeaponRadiusX,x
 sta TnRadiusX
 lda TnWeaponRadiusY,x
 sta TnRadiusY
Done:rts
.endproc
.proc TnWeapons
 lda TimerControl
 jne Done
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda MmDeathFlag
 jne Done
 BankPRGC #.bank(TnArtStart)
 ldx TnVariant
 lda TnHealth,x
 cmp #64
 txa
 rol
 eor #1                         ; original damage pair: below64 uses odd index
 tax
 lda TnDamage,x
 sta TnDamageNow
 jsr TnWeaponPosition
 ldx #5
Enemy:
 stx TnSavedSlot
 lda TnUpdateTick
 beq Eligible
 lda TnEnemyHurt,x
 beq Eligible
 dec TnEnemyHurt,x
Eligible:
 jsr TnEnemyEligible
 jcc Clear
 lda Enemy_ID,x
 clc
 adc #1
 cmp TnEnemyType,x
 beq Active
 sta TnEnemyType,x
 ldy Enemy_ID,x
 lda EnemyHP,y
 sta TnEnemyHP,x
Active:
 lda TnAttack
 beq Next
 lda TnPose+1
 beq Next
 lda TnEnemyHurt,x
 bne Next
 lda BitMask,x
 and TnAttackHit
 bne Next
 jsr TnOverlap
 bcc Next
 lda BitMask,x
 ora TnAttackHit
 sta TnAttackHit
 lda #24                       ; original TMNT enemy hit protection
 sta TnEnemyHurt,x
 lda #12
 sta MmEnemyFlash,x
 lda #Sfx_EnemySmack
 sta Square1SoundQueue
 lda TnEnemyHP,x
 sec
 sbc TnDamageNow
 bcc Defeat
 beq Defeat
 sta TnEnemyHP,x
 jmp Next
Defeat:
 lda ObjectOffset
 pha
 stx ObjectOffset
 lda Enemy_ID,x
 cmp #Bowser
 bne Normal
 lda #0
 sta TnDropCounter               ; mapped native boss defeat clears source counter
 lda #1
 sta BowserHitPoints
 stx R1
 jsr HandleEnemyFBallCol
 jmp Restore
Normal:jsr ShellOrBlockDefeat
Restore:pla
 sta ObjectOffset
 jmp Next
Clear:
 lda #0
 sta TnEnemyType,x
 sta TnEnemyHP,x
 sta TnEnemyHurt,x
Next:ldx TnSavedSlot
 dex
 jpl Enemy
Done:rts
BitMask:.byte 1,2,4,8,16,32
EnemyHP:
 .repeat 256,I
 .if I=::Bowser
 .byte 112
 .elseif I=::HammerBro
 .byte 28
 .elseif I=::Goomba
 .byte 7
 .else
 .byte 14
 .endif
 .endrepeat
.endproc
.proc TnEnemyEligible
 lda Enemy_Flag,x
 beq No
 bmi No
 lda Enemy_State,x
 and #$20
 bne No
 lda Enemy_ID,x
 cmp #Goomba
 bne Kind
 lda Enemy_State,x
 cmp #2
 bcs No
Kind:lda Enemy_ID,x
 cmp #Bowser
 beq Yes
 cmp #BulletBill_CannonVar
 beq Yes
 cmp #$15
 bcs No
 cmp #Podoboo
 beq No
Yes:sec
 rts
No:clc
 rts
.endproc
.proc TnOverlap
 lda Enemy_Y_HighPos,x
 cmp #1
 bne No
 lda Enemy_X_Position,x
 clc
 adc #8
 sta TnTemp
 lda Enemy_PageLoc,x
 adc #0
 sta TnTemp2
 sec
 lda TnTemp
 sbc TnWeaponX
 sta TnTemp
 lda TnTemp2
 sbc TnWeaponPage
 sta TnTemp2
 clc
 lda TnRadiusX
 adc #8
 sta TnTempY
 clc
 adc TnTemp
 sta TnTemp
 lda TnTemp2
 adc #0
 bne No
 lda TnTempY
 asl
 cmp TnTemp
 bcc No
 lda Enemy_Y_Position,x
 clc
 adc #8
 sec
 sbc TnWeaponY
 sta TnTemp
 lda TnRadiusY
 clc
 adc #8
 sta TnTempY
 clc
 adc TnTemp
 sta TnTemp
 lda TnTempY
 asl
 cmp TnTemp
 bcc No
 sec
 rts
No:clc
 rts
.endproc
.proc TnInjuryStatus
 lda TnHurt
 bne Protected
 ldx TnVariant
 lda TnHealth,x
 cmp #17
 bcs Protected
 lda #0
 sta TnHealth,x
 rts
Protected:lda #1
 rts
.endproc
.proc TnInjuryStart
 lda TnHurt
 bne Protected
 ldx TnVariant
 lda TnHealth,x
 sec
 sbc #16                        ; explicit SMB contact-damage adaptation
 sta TnHealth,x
 lda #120
 sta TnHurt
 lda #20
 sta TnHurtMove
 lda #8
 sta InjuryTimer
 lda #0
 sta TnAttack
 sta TnThrow
 sta TnNativeFlags
 sta TnPose+1
 sta TnSeq+1
 sta TnVYLo
 lda #$fc
 sta TnVYHi
 sta Player_Y_Speed
 lda #0
 sta TnVXLo
 lda #2
 ldy PlayerFacingDir
 cpy #2
 beq Recoil
 lda #$fe
Recoil:sta TnVXHi
 lda #1
 sta Player_State
 lda #Sfx_Bump
 sta Square1SoundQueue
Protected:sec
 rts
.endproc
.proc TnHeal
 cmp #2
 bcs No
 cmp #0
 beq Mushroom
 lda #64
 bne Add
Mushroom:lda #32
Add:ldx TnVariant
 clc
 adc TnHealth,x
 bcs Cap
 cmp #129
 bcc Store
Cap:lda #128
Store:sta TnHealth,x
 lda TnFood
 eor #1
 sta TnFood
 lda #Sfx_PowerUpGrab
 sta Square2SoundQueue
 sec
 rts
No:clc
 rts
.endproc
.proc TnDeath
 inc MmDeathAge
 lda #0
 ldx TnVariant
 sta TnHealth,x
 sta TnAttack
 sta TnThrow
 sta TnPose+1
 sta TnSeq+1
 lda MmDeathAge
 cmp #180
 bcc Done
 lda #6
 sta GameEngineSubroutine
 lda #0
 sta TimerControl
Done:rts
.endproc
.popseg
