.pushseg
.segment "CV3_COMBAT"
.proc Cv3WeaponsGate
 php
 pha
 farcall Cv3IsActive
 jcs Active
 pla
 plp
 farcall Z2WeaponsGate,jmp
Active:pla
 plp
 lda TimerControl
 jne Done
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda MmDeathFlag
 jne Done
 jsr Cv3FreezeTick
 jsr Cv3UpdateDrops
 lda Cv3Bat
 jne Move
 lda Cv3AttackAge
 jeq Input
 lda Cv3AttackKind
 cmp #2
 jeq Cast
 lda Cv3Variant
 cmp #3
 jeq Fireball
 jsr Cv3Melee
 jmp Move
Fireball:
 lda Cv3AttackAge
 cmp #8
 jne Move
 lda #6
 jsr Cv3Spawn
 ldy #2
 lda Cv3Power,y
 jeq Move
 lda #6
 jsr Cv3Spawn
 jcc Move
 jsr Cv3AlucardDiagonal
 lda #$4c
 sta Cv3ShotVYLo,x
 lda #$fe
 sta Cv3ShotVYHi,x
 ldy #2
 lda Cv3Power,y
 cmp #2
 jcc Move
 lda #6
 jsr Cv3Spawn
 jcc Move
 jsr Cv3AlucardDiagonal
 lda #$b4
 sta Cv3ShotVYLo,x
 lda #1
 sta Cv3ShotVYHi,x
 jmp Move
Cast:
 lda Cv3AttackAge
 cmp #14
 jne Move
 ldy Cv3Variant
 dey
 lda Cv3Subweapon,y
 jsr Cv3SpawnSub
 jmp Move
Input:
 lda Cv3HurtAge
 jne Move
 lda Cv3Fresh
 and #B_Button
 jeq Move
 lda #0
 sta Cv3MeleeHits
 sta Cv3MeleeBlockHit
 lda RgCrouch
 sta Cv3AttackCrouch
 lda #0
 sta Cv3AttackProfile
 lda Cv3Climb
 jeq GroundAttack
 sta Cv3AttackProfile
 lda SavedJoypadBits
 and #Down_Dir
 jeq WallSub
 lda #2
 sta Cv3AttackProfile
WallSub:
 ldy Cv3Variant
 dey
 lda Cv3Subweapon,y
 jeq Move
 jmp Subweapon
GroundAttack:
 lda SavedJoypadBits
 and #Up_Dir
 jeq Primary
Subweapon:
 ldy Cv3Variant
 dey
 lda Cv3Subweapon,y
 jeq Primary
 lda Cv3Hearts,y
 cmp #1
 jcc Move
 lda Cv3Subweapon,y
 cmp #3
 jne Pay
 lda Cv3Variant
 cmp #1
 jne Pay
 lda Cv3Hearts,y
 cmp #5
 jcc Move
 sec
 sbc #4
 sta Cv3Hearts,y
Pay:lda Cv3Hearts,y
 sec
 sbc #1
 sta Cv3Hearts,y
 lda #26
 ldx Cv3Variant
 cpx #1
 bne :+
 lda #22
: 
 sta Cv3AttackAge
 lda #2
 sta Cv3AttackKind
 jmp Sound
Primary:
 lda #1
 sta Cv3AttackKind
 lda #16
 ldx Cv3Variant
 cpx #3
 bne :+
 lda #24
: sta Cv3AttackAge
Sound:
.if ::MAPPER_MMC5
 jsr Cv3DmcPrimaryQueue
 .res 2,$ea
.else
 lda #4
 sta RgSfx
.endif
Move:
 ldx #3
Loop:
 stx Cv3Slot
 lda Cv3ShotType,x
 jeq Next
 inc Cv3ShotAge,x
 lda Cv3ShotType,x
 cmp #3
 jne NotFlame
 jsr Cv3FlameTick
 jcs Kill
NotFlame:
 lda Cv3ShotType,x
 cmp #4
 jne NotIce
 lda Cv3ShotAge,x
 cmp #32
 jcs Kill
 jsr Cv3IceMirror
NotIce:
 lda Cv3ShotAge,x
 ldy Cv3ShotType,x
 cpy #6
 bne :+
 cmp #24
 jcs Kill
: lda Cv3ShotAge,x
 cmp #100
 jcs Kill
 lda Cv3ShotType,x
 cmp #2
 jne Travel
 clc
 lda Cv3ShotVYLo,x
 adc #$40
 sta Cv3ShotVYLo,x
 lda Cv3ShotVYHi,x
 adc #0
 sta Cv3ShotVYHi,x
Travel:
 lda Cv3ShotType,x
 cmp #5
 bne :+
 jsr Cv3OrbUpdate
:
 lda Cv3ShotFx,x
 clc
 adc Cv3ShotVXLo,x
 sta Cv3ShotFx,x
 lda Cv3ShotX,x
 adc Cv3ShotVXHi,x
 sta Cv3ShotX,x
 lda Cv3ShotVXHi,x
 jmi Negative
 lda #0
 jeq Page
Negative:lda #$ff
Page:adc Cv3ShotPage,x
 sta Cv3ShotPage,x
 lda Cv3ShotFy,x
 clc
 adc Cv3ShotVYLo,x
 sta Cv3ShotFy,x
 lda Cv3ShotY,x
 adc Cv3ShotVYHi,x
 sta Cv3ShotY,x
 cmp #$f0
 jcs Kill
 jsr Cv3ShotRect
 jsr Cv3ProjectileBlock
 jcs Kill
 jsr Cv3AttackEnemies
 jmp Next
Kill:lda #0
 sta Cv3ShotType,x
Next:ldx Cv3Slot
 dex
 jpl Loop
Done:rts
.endproc
.proc Cv3AlucardDiagonal
 lda #$26
 sta Cv3ShotVXLo,x
 lda #4
 sta Cv3ShotVXHi,x
 lda Cv3ShotFlags,x
 cmp #2
 jne Done
 lda #$da
 sta Cv3ShotVXLo,x
 lda #$fb
 sta Cv3ShotVXHi,x
Done:rts
.endproc
.proc Cv3SpawnSub
 sta Cv3Temp
 lda Cv3Variant
 cmp #2
 jeq Sypha
 lda Cv3Temp
 cmp #3
 jeq Stopwatch
 cmp #2
 jeq Axe
 lda #1
 jmp Cv3Spawn
Axe:lda #2
 jmp Cv3Spawn
Stopwatch:
 lda #180
 sta AvStopwatch
 rts
Sypha:
 lda Cv3Temp
 cmp #1
 jeq Flame
 cmp #2
 jeq Ice
 lda #5
 jsr Cv3Spawn
 lda #5
 jsr Cv3Spawn
 jcc Done
 lda #$fe
 sta Cv3ShotVYHi,x
 lda #5
 jsr Cv3Spawn
 jcc Done
 lda #$fe
 sta Cv3ShotVYHi,x
 lda #$80
 sta Cv3ShotVYLo,x
Done:rts
Ice:
 lda #4
 jsr Cv3Spawn
 jcc Done
 lda #4
 jsr Cv3Spawn
 jcc Done
 lda #1
 sta Cv3ShotVXHi,x
 lda #$9e
 sta Cv3ShotVXLo,x
 lda #$fe
 sta Cv3ShotVYHi,x
 lda #$d4
 sta Cv3ShotVYLo,x
 lda #4
 jsr Cv3Spawn
 jcc Done
 lda #0
 sta Cv3ShotVXHi,x
 lda #$9e
 sta Cv3ShotVXLo,x
 lda #$fe
 sta Cv3ShotVYHi,x
 lda #$1a
 sta Cv3ShotVYLo,x
 rts
Flame:lda #3
 jmp Cv3Spawn
.endproc
; A=projectile1dagger,2axe,3flame,4ice,5homing orb,6fireball.
.proc Cv3Spawn
 pha
 ldx #3
Find:lda Cv3ShotType,x
 jeq Found
 dex
 jpl Find
 pla
 clc
 rts
Found:pla
.if ::MAPPER_MMC5
 jsr Cv3FxProducerFast
.else
 jsr Cv3SpawnAudioType
.endif
 lda #0
 sta Cv3ShotAge,x
 sta Cv3ShotFx,x
 sta Cv3ShotFy,x
 sta Cv3ShotVXLo,x
 sta Cv3ShotVYLo,x
 sta Cv3ShotVYHi,x
 sta Cv3ShotHits,x
 sta Cv3ShotTarget,x
 sta Cv3OrbRetarget,x
 lda #2
 sta Cv3OrbTurn,x
 txa
 and #3
 cmp #3
 bne :+
 lda #0
: tay
 lda PlayerFacingDir
 cmp #2
 bne :+
 iny
 iny
 iny
: lda Cv3OrbInitial,y
 sta Cv3OrbAngle,x
 sta Cv3OrbDesired,x
 lda PlayerFacingDir
 sta Cv3ShotFlags,x
 lda Player_X_Position
 clc
 adc #8
 sta Cv3ShotX,x
 lda Player_PageLoc
 adc #0
 sta Cv3ShotPage,x
 lda Player_Y_Position
 clc
 adc #16
 ldy Cv3AttackCrouch
 beq :+
 adc #8
: sta Cv3ShotY,x
 lda #2
 sta Cv3ShotVXHi,x
 lda Cv3ShotType,x
 cmp #1
 bne :+
 lda #4
 sta Cv3ShotVXHi,x
: lda Cv3ShotType,x
 cmp #6
 jne Facing
 lda #4
 sta Cv3ShotVXHi,x
 lda #$80
 sta Cv3ShotVXLo,x
Facing:
 lda Cv3ShotFlags,x
 cmp #2
 jne Axis
 lda #0
 sec
 sbc Cv3ShotVXLo,x
 sta Cv3ShotVXLo,x
 lda #0
 sbc Cv3ShotVXHi,x
 sta Cv3ShotVXHi,x
Axis:
 lda Cv3ShotType,x
 cmp #3
 jeq FlameOrigin
 cmp #4
 jeq IceOrigin
 cmp #2
 jne Done
 lda #$fa
 sta Cv3ShotVYHi,x
 lda #$80
 sta Cv3ShotVYLo,x
Done:sec
 rts
IceOrigin:
 lda #1
 sta Cv3ShotFlags,x
 lda Cv3ShotX,x
 sta Cv3IceOtherX,x
 lda Cv3ShotPage,x
 sta Cv3IceOtherPage,x
 lda #0
 sta Cv3IceOtherFx,x
 sta Cv3ShotVXLo,x
 lda #2
 sta Cv3ShotVXHi,x
 sec
 rts
FlameOrigin:
 lda Cv3ShotY,x
 sec
 sbc #8
 sta Cv3ShotY,x
 lda Cv3ShotFlags,x
 cmp #2
 jeq FlameLeft
 lda Cv3ShotX,x
 clc
 adc #24
 sta Cv3ShotX,x
 lda Cv3ShotPage,x
 adc #0
 sta Cv3ShotPage,x
 sec
 rts
FlameLeft:
 lda Cv3ShotX,x
 sec
 sbc #24
 sta Cv3ShotX,x
 lda Cv3ShotPage,x
 sbc #0
 sta Cv3ShotPage,x
 sec
 rts
.endproc
.proc Cv3FlameTick
 lda Cv3ShotAge,x
 cmp #28
 jcs Done
 tay
 lda Delta,y
 sta Cv3ShotVXHi,x
 lda Pose,y
 sta Cv3ShotSpec,x
 lda Cv3ShotFlags,x
 cmp #2
 jne Positive
 lda #0
 sec
 sbc Cv3ShotVXHi,x
 sta Cv3ShotVXHi,x
Positive:clc
Done:rts
Delta:.byte 0,0,0,0,4,0,0,4,0,0,12,0,0,8,0,0,8,0,0,4,0,0,8,0,0,0,0,0
Pose:.byte 30,30,30,30,31,31,31,31,31,31,32,32,32,32,32,32,33,33,33,33,33,33,34,34,34,43,43,43
.endproc
.proc Cv3IceMirror
 ; Source1D:B8A9 swaps the two symmetric endpoints, reverses horizontal
 ; velocity, then updates both endpoints. World page carry is SMB-only.
 lda Cv3ShotX,x
 ldy Cv3IceOtherX,x
 sta Cv3IceOtherX,x
 tya
 sta Cv3ShotX,x
 lda Cv3ShotPage,x
 ldy Cv3IceOtherPage,x
 sta Cv3IceOtherPage,x
 tya
 sta Cv3ShotPage,x
 lda Cv3ShotFx,x
 ldy Cv3IceOtherFx,x
 sta Cv3IceOtherFx,x
 tya
 sta Cv3ShotFx,x
 lda #0
 sec
 sbc Cv3ShotVXLo,x
 sta Cv3ShotVXLo,x
 lda #0
 sbc Cv3ShotVXHi,x
 sta Cv3ShotVXHi,x
 lda Cv3IceOtherFx,x
 sec
 sbc Cv3ShotVXLo,x
 sta Cv3IceOtherFx,x
 lda Cv3IceOtherX,x
 sbc Cv3ShotVXHi,x
 sta Cv3IceOtherX,x
 lda #0
 ldy Cv3ShotVXHi,x
 jpl Positive
 lda #$ff
Positive:sta Cv3Temp
 lda Cv3IceOtherPage,x
 sbc Cv3Temp
 sta Cv3IceOtherPage,x
 rts
.endproc
.proc Cv3Melee
 lda Cv3AttackAge
 cmp #12
 jcs Done
 cmp #3
 jcc Done
 lda #20
 ldy Cv3Variant
 cpy #1
 bne :+
 lda #12
: sta Cv3RectW
 lda Player_X_Position
 clc
 adc #14
 sta Cv3RectX
 lda Player_PageLoc
 adc #0
 sta Cv3RectPage
 lda PlayerFacingDir
 cmp #2
 jne PlaceY
 lda Player_X_Position
 sec
 sbc Cv3RectW
 sta Cv3RectX
 lda Player_PageLoc
 sbc #0
 sta Cv3RectPage
PlaceY:lda Player_Y_Position
 clc
 adc #12
 ldy Cv3AttackCrouch
 beq :+
 adc #8
: sta Cv3RectY
 lda #8
 sta Cv3RectH
 lda #$ff
 sta Cv3Slot
 jsr Cv3MeleeBlocks
 jsr Cv3AttackEnemies
Done:rts
.endproc
.proc Cv3ShotRect
 lda Cv3ShotX,x
 sec
 sbc #4
 sta Cv3RectX
 lda Cv3ShotPage,x
 sbc #0
 sta Cv3RectPage
 lda Cv3ShotY,x
 sec
 sbc #4
 sta Cv3RectY
 lda #8
 sta Cv3RectW
 sta Cv3RectH
 rts
.endproc
.proc Cv3Eligible
 lda Enemy_Flag,x
 jeq No
 jmi No
 lda Enemy_State,x
 and #$20
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
 cmp #Goomba
 jne Yes
 lda Enemy_State,x
 cmp #2
 jcs No
Yes:sec
 rts
No:clc
 rts
.endproc
.proc Cv3Overlap
 lda Enemy_Y_HighPos,x
 cmp #1
 jne No
 lda Enemy_X_Position,x
 sec
 sbc Cv3RectX
 sta R0
 lda Enemy_PageLoc,x
 sbc Cv3RectPage
 sta R1
 lda R0
 clc
 adc #15
 sta R0
 lda R1
 adc #0
 jne No
 lda Cv3RectW
 clc
 adc #15
 cmp R0
 jcc No
 jeq No
 lda Enemy_Y_Position,x
 sec
 sbc Cv3RectY
 clc
 adc #23
 sta R0
 lda Cv3RectH
 clc
 adc #23
 cmp R0
 jcc No
 jeq No
 sec
 rts
No:clc
 rts
.endproc
.proc Cv3AttackEnemies
 ldx #5
Loop:
 stx Cv3HitSlot
 jsr Cv3Eligible
 jcc Next
 jsr Cv3Overlap
 jcc Next
 ldy Cv3Slot
 jmi Melee
 lda Cv3HitBits,x
 and Cv3ShotHits,y
 jne Next
 lda Cv3HitBits,x
 ora Cv3ShotHits,y
 sta Cv3ShotHits,y
 lda Cv3ShotType,y
 cmp #4
 jeq Freeze
 jmp Hit
Melee:
 lda Cv3HitBits,x
 and Cv3MeleeHits
 jne Next
 lda Cv3HitBits,x
 ora Cv3MeleeHits
 sta Cv3MeleeHits
 lda Cv3FrozenTimer,x
 jne Shatter
Hit:
 lda Enemy_ID,x
 cmp #BuzzyBeetle
 jeq Next
 cmp #BulletBill_CannonVar
 jeq Next
 cmp #BulletBill_FrenzyVar
 jeq Next
 cmp #Bowser
 jne Normal
 stx R1
 jsr HandleEnemyFBallCol
 jmp Next
Normal:
 stx ObjectOffset
 jsr ShellOrBlockDefeat
 lda #Sfx_EnemySmack
 sta Square1SoundQueue
 jmp Next
Freeze:
 lda Enemy_ID,x
 cmp #Bowser
 jeq Next
 lda #180
 sta Cv3FrozenTimer,x
 sta AvFrozen,x
 lda #0
 sta AvFrozenHi,x
 lda Enemy_ID,x
 sta Cv3FrozenID,x
 lda #1
 sta RgEnemyStun,x
 lda EnemyMetasprite,x
 sta LsrFrozenPose,x
 jmp Next
Shatter:
 lda #0
 sta Cv3FrozenTimer,x
 sta AvFrozen,x
 sta AvFrozenHi,x
 sta LsrFrozenPose,x
 jmp Normal
Next:ldx Cv3HitSlot
 dex
 jpl Loop
 ldx Cv3Slot
 rts
.endproc
.proc Cv3FreezeTick
 lda AvStopwatch
 beq :+
 dec AvStopwatch
: ldx #5
Loop:
 lda Cv3FrozenTimer,x
 jeq Next
 lda AvFrozen,x
 ora AvFrozenHi,x
 jeq Clear
 lda Enemy_Flag,x
 jeq Clear
 lda Enemy_ID,x
 cmp Cv3FrozenID,x
 jne Clear
 dec Cv3FrozenTimer,x
 lda Cv3FrozenTimer,x
 sta AvFrozen,x
 jne Standing
Clear:
 lda #0
 sta Cv3FrozenTimer,x
 sta AvFrozen,x
 sta AvFrozenHi,x
 sta LsrFrozenPose,x
 jmp Next
Standing:
 phx
 farcall X5Cv3IcePlatform
 plx
Next:dex
 jpl Loop
 rts
.endproc
.proc Cv3BodyGate
 php
 pha
 farcall Cv3IsActive
 jcc Legacy
 lda Cv3FrozenTimer,x
 jeq Legacy
 lda AvFrozen,x
 ora AvFrozenHi,x
 jeq Legacy
 pla
 plp
 sec
 rts
Legacy:pla
 plp
 farcall VvBodyDispatch,jmp
.endproc
Cv3HitBits:.byte 1,2,4,8,16,32
.popseg
