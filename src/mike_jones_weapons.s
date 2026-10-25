; Source weapon families/cadence; target HP and cross-game terrain are adaptations.
.pushseg
.segment "MIKE_COMBAT"
.proc JnWeapons
 lda TimerControl
 jne Done
 lda MmDeathFlag
 jne Done
 lda GameEngineSubroutine
 cmp #8
 jne Done
 jsr JnTrackEnemies
 jsr JnUpdateDrops
 lda JnPressed
 and #B_Button
 jeq Active
 ; Asterisk: fresh secondB splits the two blades, no second ammo charge.
 lda #0
 sta JnTemp
 ldx #5
Split:
 lda JnShotKind,x
 cmp #8
 jne NextSplit
 lda JnShotHit,x
 bmi NextSplit
 ora #$80
 sta JnShotHit,x
 lda #3
 ldy JnShotVY,x
 bpl :+
 lda #$fd
:sta JnShotVY,x
 inc JnTemp
NextSplit:dex
 jpl Split
 lda JnTemp
 jeq NoSplit
 lda #Sfx_Fireball
 sta Square1SoundQueue
 jmp Update
NoSplit:
 lda JnAttack
 jne Active
 lda JnSelected
 jeq Primary
 tax
 lda JnAmmo-1,x
 jeq Primary
 txa
 clc
 adc #3
 sta JnWeapon
 jmp Begin
Primary:jsr JnSelectPrimary
Begin:lda #1
 sta JnAttack
 lda #0
 sta JnHitMask
Active:
 lda JnAttack
 jeq Update
 cmp #6 ; native5-frame windup.
 jne Age
 jsr JnRelease
Age:inc JnAttack
 lda JnAttack
 cmp #19
 jcc Update
 lda #0
 sta JnAttack
Update:
 lda #5
 sta JnSlot
Loop:
 ldx JnSlot
 lda JnShotKind,x
 jeq Next
 jsr JnShotPhysics
 ldx JnSlot
 lda JnShotKind,x
 jeq Next
 jsr JnShotEnemies
Next:dec JnSlot
 jpl Loop
Done:rts
.endproc
.proc JnSelectPrimary
 lda JnTier
 sta JnWeapon
 rts
.endproc
.proc JnRelease
 ldx #5
Find:lda JnShotKind,x
 jeq Free
 dex
 jpl Find
 rts
Free:stx JnSlot
 lda JnWeapon
 sta JnShotKind,x
 lda #0
 sta JnShotAge,x
 sta JnShotHit,x
 sta JnShotVY,x
 lda #8
 ldy PlayerFacingDir
 cpy #2
 jne SpawnOffset
 lda #0
SpawnOffset:
 sta JnTemp
 lda Player_X_Position
 clc
 adc JnTemp
 sta JnShotX,x
 lda Player_PageLoc
 adc #0
 sta JnShotPage,x
 lda Player_Y_Position
 clc
 adc #16
 sta JnShotY,x
 ldy JnWeapon
 lda Speeds,y
Speed:ldy PlayerFacingDir
 cpy #2
 jne Store
 eor #$ff
 clc
 adc #1
Store:sta JnShotVX,x
 lda JnWeapon
 cmp #4
 jcc Sound
 sec
 sbc #4
 tay
 lda JnAmmo,y
 jeq NoAmmo
 sec
 sbc #1
 sta JnAmmo,y
 lda #1
 sta JnUiDirty
 lda JnWeapon
 cmp #7
 jne NotMirror
 lda #30
 sta JnHurt
 jne Sound
NotMirror:cmp #10
 jne NotSpikes
 jsr JnSpikes
 jmp Sound
NotSpikes:cmp #8
 jne Sound
 ; Two original cross-blades launch together, secondB splits their tracks.
 ldx JnSlot
 lda #1
 sta JnShotVY,x
 dex
 jmi Sound
 lda JnShotKind,x
 jne Sound
 lda #8
 sta JnShotKind,x
 lda JnShotX+1,x
 sta JnShotX,x
 lda JnShotPage+1,x
 sta JnShotPage,x
 lda JnShotY+1,x
 sta JnShotY,x
 lda JnShotVX+1,x
 sta JnShotVX,x
 lda #0
 sta JnShotAge,x
 sta JnShotHit,x
 lda #$ff
 sta JnShotVY,x
Sound:lda #Sfx_Fireball
 sta Square1SoundQueue
 rts
Speeds:.byte 0,0,3,4,0,2,2,0,2,2,0,3,4,4
NoAmmo:lda #0
 sta JnShotKind,x
 rts
.endproc
.proc JnShotPhysics
 inc JnShotAge,x
 lda JnShotKind,x
 cmp #1
 jeq Yoyo
 cmp #4
 jeq Bat
 cmp #7
 jeq Mirror
 cmp #10
 jeq Short
 ldy JnShotKind,x
 lda JnShotAge,x
 cmp MaxAge,y
 jcs Kill
 lda JnShotVX,x
 jpl Right
 lda #$ff
 jne Sign
Right:lda #0
Sign:sta JnTemp
 lda JnShotX,x
 clc
 adc JnShotVX,x
 sta JnShotX,x
 lda JnShotPage,x
 adc JnTemp
 sta JnShotPage,x
 lda JnShotY,x
 clc
 adc JnShotVY,x
 sta JnShotY,x
 cmp #240
 jcs Kill
 lda JnShotKind,x
 cmp #11
 jne Done
 lda JnShotAge,x
 and #3
 jne Done
 inc JnShotVY,x ; baseball's original thrown-arc identity, SMB-scaled.
 rts
Yoyo:
 lda JnShotAge,x
 cmp #12
 jcs Kill
 tay
 lda YoyoReach,y
 jmp Hand
Bat:
 lda JnShotAge,x
 cmp #12
 jcs Kill
 lda #22
 jmp Hand
Mirror:
 lda JnShotAge,x
 cmp #30
 jcs Kill
 lda #12
Hand:
 sta JnTemp
 lda #0
 sta JnTemp2
 lda PlayerFacingDir
 cmp #2
 jne Position
 lda #0
 sec
 sbc JnTemp
 sta JnTemp
 lda #$ff
 sta JnTemp2
 clc
 lda JnTemp
 adc #8
 sta JnTemp
 lda JnTemp2
 adc #0
 sta JnTemp2
Position:
 lda Player_X_Position
 clc
 adc JnTemp
 sta JnShotX,x
 lda Player_PageLoc
 adc JnTemp2
 sta JnShotPage,x
 lda Player_Y_Position
 clc
 adc #16
 sta JnShotY,x
Done:jsr JnShotTerrain
 rts
Short:
 lda JnShotAge,x
 cmp #20
 jcc Done
Kill:lda #0
 sta JnShotKind,x
 rts
YoyoReach:.byte 8,16,24,32,36,36,36,36,32,32,24,16
MaxAge:.byte 0,12,80,80,12,24,48,30,80,100,20,80,80,80
.endproc
.proc JnShotTerrain
 ldx JnSlot
 lda JnShotKind,x
 jeq Done
 cmp #7
 jeq Done
 cmp #10
 jeq Done
 lda JnShotX,x
 clc
 adc #4
 sta JnQueryX
 lda JnShotPage,x
 adc #0
 sta JnQueryPage
 lda JnQueryX
 sta MmProbeX
 lda JnQueryPage
 sta MmProbePage
 lda JnShotY,x
 clc
 adc #8
 sta MmProbeY
 farcall Cv3BlockPoint
 jcc Done
 ldx JnSlot
 lda #0
 sta JnShotKind,x
 lda #Sfx_Bump
 sta Square1SoundQueue
Done:rts
.endproc
.proc JnReadCell
 cmp #32
 jcc Empty
 cmp #240
 jcs Empty
 and #$f0
 sec
 sbc #32
 sta R2
 lda JnQueryPage
 and #1
 asl
 asl
 asl
 asl
 sta R0
 lda JnQueryX
 lsr
 lsr
 lsr
 lsr
 ora R0
 jsr GetBlockBufferAddr
 ldy R2
 lda (R6),y
 rts
Empty:lda #0
 rts
.endproc
.proc JnTrackEnemies
 ldx #5
Loop:
 lda Enemy_Flag,x
 jeq Clear
 jmi Clear
 lda Enemy_State,x
 and #$20
 jne Next
 lda Enemy_ID,x
 clc
 adc #1
 cmp JnEnemyType,x
 jeq Hurt
 sta JnEnemyType,x
 lda #0
 sta JnDropReceipt,x
 lda #2
 ldy Enemy_ID,x
 cpy #HammerBro
 bne :+
 lda #4
:cpy #Bowser
 bne :+
 lda #24
:sta JnEnemyHP,x
Hurt:lda JnEnemyHurt,x
 jeq Next
 dec JnEnemyHurt,x
 jmp Next
Clear:lda #0
 sta JnEnemyType,x
 sta JnEnemyHP,x
 sta JnEnemyHurt,x
 sta JnDropReceipt,x
Next:dex
 jpl Loop
 rts
.endproc
.proc JnEligible
 lda Enemy_Flag,x
 jeq No
 jmi No
 lda Enemy_State,x
 and #$20
 jne No
 lda Enemy_Y_HighPos,x
 cmp #1
 jne No
 lda Enemy_ID,x
 cmp #Bowser
 jeq Yes
 cmp #BulletBill_CannonVar
 jeq Yes
 cmp #$15
 jcs No
 cmp #Podoboo
 jeq No
Yes:sec
 rts
No:clc
 rts
.endproc
.proc JnShotEnemies
 ldx JnSlot
 lda JnShotKind,x
 tay
 lda Damage,y
 sta JnDamage
 lda #10
 sta JnRadius
 cpy #13
 bne :+
 lda #18
 sta JnRadius
:ldx #5
Loop:
 stx JnSavedX
 ldy JnSlot
 lda JnShotKind,y
 cmp #7
 jne Ordinary
 lda Enemy_Flag,x
 jeq Next
 jmi Next
 lda Enemy_ID,x
 cmp #BowserFlame
 jeq MirrorEligible
 cmp #BulletBill_CannonVar
 jeq MirrorEligible
 cmp #BulletBill_FrenzyVar
 jne Next
MirrorEligible:
 lda Enemy_Y_HighPos,x
 cmp #1
 jne Next
 jmp Eligible
Ordinary:
 jsr JnEligible
 jcc Next
Eligible:
 lda JnEnemyHurt,x
 jne Next
 ldy JnSlot
 lda JnShotHit,y
 and Bits,x
 jne Next
 lda Enemy_X_Position,x
 sec
 sbc JnShotX,y
 sta JnTemp
 lda Enemy_PageLoc,x
 sbc JnShotPage,y
 sta JnTemp2
 lda JnTemp
 clc
 adc #16
 sta JnTemp
 lda JnTemp2
 adc #0
 jne Next
 lda JnTemp
 cmp #33
 jcs Next
 lda Enemy_Y_Position,x
 clc
 adc #8
 sec
 sbc JnShotY,y
 clc
 adc JnRadius
 cmp #37
 jcs Next
 lda JnShotHit,y
 ora Bits,x
 sta JnShotHit,y
 lda #12
 sta JnEnemyHurt,x
 sta MmEnemyFlash,x
 lda #Sfx_EnemySmack
 sta Square1SoundQueue
 ldy JnSlot
 lda JnShotKind,y
 cmp #7
 jne ApplyDamage
 jsr JnReflectMagic
 jmp Next
ApplyDamage:
 lda JnEnemyHP,x
 sec
 sbc JnDamage
 jcc Defeat
 jeq Defeat
 sta JnEnemyHP,x
 jmp Next
Defeat:
 jsr JnDefeat
Next:
 ldx JnSavedX
 dex
 jpl Loop
 rts
Bits:.byte 1,2,4,8,16,32
Damage:.byte 0,1,2,3,3,2,2,2,2,3,4,3,4,6
.endproc
.proc JnDefeat
 lda ObjectOffset
 pha
 stx ObjectOffset
 lda Enemy_ID,x
 cmp #Bowser
 jne Normal
 lda #1
 sta BowserHitPoints
 stx R1
 jsr HandleEnemyFBallCol
 jmp Restore
Normal:jsr ShellOrBlockDefeat
Restore:pla
 sta ObjectOffset
 rts
.endproc
.proc JnReflectMagic
 ; Original MiracleMirror reflects magic. SMB flames/Bills become a free
 ; outbound source laser; this target conversion is explicitly adapted.
 lda Enemy_X_Position,x
 sta JnQueryX
 lda Enemy_PageLoc,x
 sta JnQueryPage
 lda Enemy_Y_Position,x
 clc
 adc #8
 sta JnReflectY
 lda ObjectOffset
 pha
 stx ObjectOffset
 jsr EraseEnemyObject
 pla
 sta ObjectOffset
 ldx #5
Find:lda JnShotKind,x
 jeq Free
 dex
 jpl Find
 rts
Free:
 lda #12
 sta JnShotKind,x
 lda #0
 sta JnShotAge,x
 sta JnShotHit,x
 sta JnShotVY,x
 lda JnQueryX
 sta JnShotX,x
 lda JnQueryPage
 sta JnShotPage,x
 lda JnReflectY
 sta JnShotY,x
 lda #3
 ldy PlayerFacingDir
 cpy #2
 jne Velocity
 lda #$fd
Velocity:sta JnShotVX,x
 lda #Sfx_Bump
 sta Square1SoundQueue
 rts
.endproc
.proc JnSpikes
 ldx #5
Loop:stx JnSavedX
 jsr JnEligible
 jcc Next
 lda JnEnemyHP,x
 sec
 sbc #4
 jcc Defeat
 jeq Defeat
 sta JnEnemyHP,x
 lda #12
 sta JnEnemyHurt,x
 sta MmEnemyFlash,x
 jmp Next
Defeat:jsr JnDefeat
Next:ldx JnSavedX
 dex
 jpl Loop
 rts
.endproc
.popseg

