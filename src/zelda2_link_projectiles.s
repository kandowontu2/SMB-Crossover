.pushseg
.segment "Z2_LOGIC"
.proc Z2TrySpawnBeam
 lda Z2ActiveSpells
 and #8
 jne Done
 lda Z2HurtTimer
 jne Done
 lda Z2AttackStage
 sec
 sbc #1
 cmp Z2NativeAttackStand
 jne Done
 lda Z2AttackTimer
 cmp #5
 jne Done
 lda Z2ActiveSpells
 and #16
 jne Fire
 jsr Z2MaxHp
 cmp Z2Hp
 jne Done
 lda #1
 sta R4
 ldx #0
 jeq Find
Fire:
 lda #2
 sta R4
 lda #0
 jsr Z2GetLevel
 ldx #0
 cmp #3
 jcc Find
 inx
Find:
 lda Z2ShotKind,x
 jeq Spawn
 dex
 jpl Find
 rts
Spawn:
 lda R4
 sta Z2ShotKind,x
 lda #0
 sta Z2ShotAge,x
 lda Player_X_Position
 clc
 adc #5 ; native spawnADC12 inherits carry1, then sourceanchor-8.
 sta Z2ShotX,x
 lda Player_PageLoc
 adc #0
 sta Z2ShotPage,x
 lda PlayerFacingDir
 sta Z2ShotDir,x
 cmp #2
 jeq Left
 lda #2
 jne Speed
Left:lda #$fe
Speed:sta Z2ShotVX,x
 ldy Z2NativeAttackStand
 lda R4
 cmp #1
 jeq BeamY
 lda FireY,y
 jne PlaceY
BeamY:lda BeamOffsets,y
PlaceY:clc
 adc Player_Y_Position
 sta Z2ShotY,x
 lda #Sfx_Fireball
 sta Square1SoundQueue
Done:rts
FireY:.byte 13,4
BeamOffsets:.byte 9,$ff
.endproc
.proc Z2Projectiles
 lda #1
 sta Z2ShotSlot
Loop:
 ldx Z2ShotSlot
 lda Z2ShotKind,x
 jeq Next
 cmp #1
 jne Move
 inc Z2ShotAge,x
 lda Z2ShotAge,x
 cmp #32
 jcs Kill
Move:
 lda #0
 ldy Z2ShotVX,x
 bpl :+
 lda #$ff
:sta R1
 clc
 lda Z2ShotX,x
 adc Z2ShotVX,x
 sta Z2ShotX,x
 lda Z2ShotPage,x
 adc R1
 sta Z2ShotPage,x
 sec
 lda Z2ShotX,x
 sbc ScreenLeft_X_Pos
 sta R0
 lda Z2ShotPage,x
 sbc ScreenLeft_PageLoc
 jne Kill
 lda R0
 cmp #248
 jcs Kill
 lda Z2ShotX,x
 sta MmProbeX
 lda Z2ShotPage,x
 sta MmProbePage
 lda Z2ShotY,x
 clc
 adc #7
 sta MmProbeY
 lda #1
 jsr Z2BlockPoint
 jcs Kill
 ldx Z2ShotSlot
 lda Z2ShotX,x
 sec
 sbc #4
 sta Z2RectX
 lda Z2ShotPage,x
 sbc #0
 sta Z2RectPage
 lda Z2ShotY,x
 clc
 adc #5
 sta Z2RectY
 lda #8
 sta Z2RectW
 lda #6
 sta Z2RectH
 lda #5
 sta Z2HitSlot
Enemies:
 ldx Z2HitSlot
 jsr Z2EnemyEligible
 jcc EnemyNext
 jsr Z2RectOverlap
 jcc EnemyNext
 lda #0
 jsr Z2GetLevel
 tax
 lda SwordDamage,x
 ldx Z2HitSlot
 jsr Z2HitEnemy
 ldx Z2ShotSlot
 jmp Kill
EnemyNext:
 dec Z2HitSlot
 jpl Enemies
 jmp Next
Kill:
 ldx Z2ShotSlot
 lda #0
 sta Z2ShotKind,x
Next:dec Z2ShotSlot
 jpl Loop
 rts
.endproc
.proc Z2SpellWorldEffects
 lda Z2ActiveSpells
 and #$c0
 jeq Done
 sta Z2BodyScratch+8
 lda Z2ActiveSpells
 and #$3f
 sta Z2ActiveSpells
 lda #8
 sta Z2SpecialFlash
 lda #5
 sta Z2HitSlot
Loop:
 ldx Z2HitSlot
 jsr Z2EnemyEligible
 jcc Next
 lda Z2BodyScratch+8
 jmi Thunder
 lda Enemy_ID,x
 cmp #Bowser
 jeq Next
 lda #Goomba
 sta Enemy_ID,x
 lda #0
 sta Enemy_State,x
 sta Z2EnemyExpReceipt,x
 sta Z2EnemyHp,x
 jmp Next
Thunder:
 lda #50
 jsr Z2HitEnemy
Next:dec Z2HitSlot
 jpl Loop
Done:rts
.endproc
.proc Z2DeferredThrustGate
 jsr Z2IsActive
 jcs Done
 farcall LinkDeferredThrust,jmp
Done:rts
.endproc
.proc Z2BodyContactGate
 stx Z2HitSlot
 jsr Z2IsActive
 jcc Original
 lda Z2CachedPose
 cmp #8
 jeq Thrust
 cmp #9
 jne Reflect
Thrust:
 ldx Z2HitSlot
 jsr Z2EnemyEligible
 jcc Ordinary
 jsr Z2SwordRect
 ldx Z2HitSlot
 jsr Z2RectOverlap
 jcc Ordinary
 lda Z2EnemyExpReceipt,x
 and #$40
 jne Protected
 lda Z2EnemyExpReceipt,x
 ora #$40
 sta Z2EnemyExpReceipt,x
 lda #0
 jsr Z2GetLevel
 tax
 lda SwordDamage,x
 ldx Z2HitSlot
 jsr Z2HitEnemy
 lda Z2CachedPose
 cmp #9
 jne StopRise
 lda #$fe
 sta Z2NativeVY
 sta Player_Y_Speed
 lda #2
 sta Z2NativeAir
 sta Player_State
 jne Protected
StopRise:lda #0
 sta Z2NativeVY
 sta Player_Y_Speed
 jeq Protected
Reflect:
 lda Z2ActiveSpells
 and #32
 jeq Ordinary
 ldx Z2HitSlot
 lda Enemy_ID,x
 cmp #BowserFlame
 jne Ordinary
 ; Original E9D8 shield rectangle translated from sourceX to canonicalX+8.
 lda PlayerFacingDir
 cmp #1
 bne ShieldLeft
 lda #14
 bne ShieldPlace
ShieldLeft:lda #$ff
ShieldPlace:sta R0
 lda #0
 ldy R0
 bpl :+
 lda #$ff
:sta R1
 lda Player_X_Position
 clc
 adc R0
 sta Z2RectX
 lda Player_PageLoc
 adc R1
 sta Z2RectPage
 lda #2
 ldy Z2NativeShield
 bne :+
 lda #17
:clc
 adc Player_Y_Position
 sta Z2RectY
 lda #5
 sta Z2RectW
 lda #12
 sta Z2RectH
 jsr Z2RectOverlap
 jcc Ordinary
Reflected:
 lda Enemy_X_Position,x
 sta R4
 lda Enemy_PageLoc,x
 sta R5
 lda Enemy_Y_Position,x
 sta R6
 lda #0
 sta Enemy_Flag,x
 sta EnemyMetasprite,x
 ldx #1
ReflectSlot:
 lda Z2ShotKind,x
 jeq ReflectShot
 dex
 jpl ReflectSlot
 jmi ReflectSound
ReflectShot:
 lda #2
 sta Z2ShotKind,x
 lda R4
 sta Z2ShotX,x
 lda R5
 sta Z2ShotPage,x
 lda R6
 sta Z2ShotY,x
 lda PlayerFacingDir
 sta Z2ShotDir,x
 cmp #1
 jeq ReflectRight
 lda #$fe
 jne ReflectSpeed
ReflectRight:lda #2
ReflectSpeed:sta Z2ShotVX,x
 lda #0
 sta Z2ShotAge,x
ReflectSound:
 lda #Sfx_Bump
 sta Square1SoundQueue
Protected:ldx Z2HitSlot
 sec
 rts
Ordinary:ldx Z2HitSlot
 clc
 rts
Original:ldx Z2HitSlot
 farcall LinkBodyContact,jmp
.endproc
.popseg
