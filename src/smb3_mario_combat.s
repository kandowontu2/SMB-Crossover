.pushseg
.segment "M3_LOGIC"
.proc M3Weapons
 lda MmDeathFlag
 ora TimerControl
 jne Done
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda M3Growth
 ora M3Poof
 jne Done
 lda M3Native::Player_TailAttack
 cmp #9
 beq TailBlock
 cmp #12
 bne Launch
 jsr M3TailEnemies
 jmp Launch
TailBlock:
 jsr M3TailEnemies
 lda Player_Y_Position
 clc
 adc #28
 sta MmProbeY
 lda #21
 ldy M3Native::Player_FlipBits
 beq :+
 lda #$fa
:clc
 adc Player_X_Position
 sta MmProbeX
 lda Player_PageLoc
 ldy M3Native::Player_FlipBits
 beq :+
 sbc #0
 jmp TailPage
:adc #0
TailPage:sta MmProbePage
 jsr M3TailBlock
Launch:
 lda M3Form
 cmp #2
 beq Fire
 cmp #6
 bne Update
Fire:lda M3Fresh
 and #B_Button
 beq Update
 lda CrouchingFlag
 bne Update
 lda M3ShotKind
 beq Throw
 lda M3ShotKind+1
 bne Update
Throw:farcall M3Throw
 lda #Sfx_Fireball
 sta Square1SoundQueue
Update:
 lda #1
 sta M3SavedSlot
Loop:ldx M3SavedSlot
 lda M3ShotKind,x
 jeq Next
 farcall M3AdvanceShot
 ldx M3SavedSlot
 lda M3ShotYHi,x
 cmp #1
 jne Remove
 lda M3ShotX,x
 sec
 sbc ScreenLeft_X_Pos
 sta R0
 lda M3ShotPage,x
 sbc ScreenLeft_PageLoc
 bne Remove
 lda M3ShotKind,x
 cmp #1
 bne Enemies
 lda M3ShotX,x
 clc
 adc #4
 sta MmProbeX
 lda M3ShotPage,x
 adc #0
 sta MmProbePage
 lda M3ShotY,x
 clc
 adc #14
 sta MmProbeY
 jsr M3ReadPoint
 beq Enemies
 ldx M3SavedSlot
 lda M3ShotVY,x
 bmi Remove
 lda #$fd
 sta M3ShotVY,x
 lda #3
 sta M3ShotAge,x
Enemies:jsr M3ShotEnemies
 jmp Next
Remove:lda #0
 sta M3ShotKind,x
Next:dec M3SavedSlot
 jpl Loop
Done:rts
.endproc
.proc M3TailEnemies
 ; Original PRG0 DB17: active only at12/9, X offsets17/-10,10x15
 ; rectangle at bodyY+16. Enemy classes/bounds use their SMB equivalents.
 lda #17
 ldy M3Native::Player_FlipBits
 beq :+
 lda #$f6
:clc
 adc Player_X_Position
 sta M3QueryX
 lda Player_PageLoc
 ldy M3Native::Player_FlipBits
 beq :+
 sbc #0
 jmp Page
:adc #0
Page:sta M3QueryPage
 lda Player_Y_Position
 clc
 adc #16
 sta M3QueryY
 ldx #5
Loop:stx M3EnemySlot
 lda Enemy_Flag,x
 jeq Next
 jmi Next
 lda Enemy_ID,x
 cmp #$15
 jcs Next
 cmp #Podoboo
 jeq Next
 lda Enemy_State,x
 and #$20
 jne Next
 lda M3QueryX
 sec
 sbc Enemy_X_Position,x
 sta R0
 lda M3QueryPage
 sbc Enemy_PageLoc,x
 sta R1
 lda R0
 clc
 adc #10
 sta R0
 lda R1
 adc #0
 bne Next
 lda R0
 cmp #27
 bcs Next
 lda M3QueryY
 sec
 sbc Enemy_Y_Position,x
 clc
 adc #15
 cmp #32
 bcs Next
 stx ObjectOffset
 jsr M3DefeatEnemy
Next:ldx M3EnemySlot
 dex
 jpl Loop
 rts
.endproc
; Exact canonical metatile point query; no temporary displacement of player.
.proc M3ReadPoint
 lda MmProbeY
 cmp #$20
 bcc Empty
 cmp #$f0
 bcs Empty
 and #$f0
 sec
 sbc #$20
 sta R2
 lda MmProbePage
 and #1
 asl
 asl
 asl
 asl
 sta R0
 lda MmProbeX
 lsr
 lsr
 lsr
 lsr
 ora R0
 jsr GetBlockBufferAddr
 ldy R2
 lda (R6),y
 cmp #$23
 beq Empty
 cmp #$26
 beq Empty
 cmp #$c2
 beq Empty
 cmp #$c3
 beq Empty
 sta R3
 ora #0 ; Public getter N/Z must describe the returned metatile.
 rts
Empty:lda #0
 rts
.endproc
.proc M3TailBlock
 jsr M3ReadPoint
 beq Done
 jsr BlockBumpedChk
 bcs Activate
 lda R3
 cmp #$51
 beq Brick
 cmp #$52
 bne Done
Brick:
 clc
 lda R6
 adc #<(MmSolidTerrain-Block_Buffer_1)
 sta M0
 lda R7
 adc #>(MmSolidTerrain-Block_Buffer_1)
 sta M1
 ldy R2
 lda (M0),y
 bne Done
Activate:
 lda #14
 sta MmBulletType
 lda MmProbeX
 sta MmBulletX
 lda MmProbePage
 sta MmBulletPage
 lda MmProbeY
 sta MmBulletY
 lda PlayerFacingDir
 sta MmBulletDir
 lda #0
 sta MmSlot
 tax
 farcall MegaManWeapons::BombPoint
 lda #0
 sta MmBulletType
Done:rts
.endproc
.proc M3ShotEnemies
 ldy #5
Loop:sty M3EnemySlot
 lda Enemy_Flag,y
 jeq Next
 bmi Next
 jsr M3ProjectileAdmission
 nop
 nop
 jcs Next
 cmp #Podoboo
 jeq Next
 cmp #BuzzyBeetle
 beq Next
 lda Enemy_State,y
 and #$20
 bne Next
 ldx M3SavedSlot
 lda M3ShotX,x
 sec
 sbc Enemy_X_Position,y
 sta R0
 lda M3ShotPage,x
 sbc Enemy_PageLoc,y
 sta R1
 lda R0
 clc
 adc #8
 sta R0
 lda R1
 adc #0
 bne Next
 lda R0
 cmp #25
 bcs Next
 lda M3ShotY,x
 sec
 sbc Enemy_Y_Position,y
 clc
 adc #12
 cmp #29
 bcs Next
 tya
 tax
 stx ObjectOffset
 jsr M3ProjectileDamage
 ldx M3SavedSlot
 lda M3ShotKind,x
 cmp #1
 bne Next
 lda #0
 sta M3ShotKind,x
 rts
Next:ldy M3EnemySlot
 dey
 jpl Loop
 rts
.endproc
.proc M3DefeatEnemy
 lda Enemy_ID,x
 cmp #PiranhaPlant
 bne :+
 lda Enemy_Y_Position,x
 clc
 adc #24
 sta Enemy_Y_Position,x
:jmp StnE
.endproc
.segment "M3_NATIVE"
.proc M3Throw
 jsr M3ShotNative::PlayerProj_ThrowWeapon
 lda Player_X_Position
 clc
 adc #4
 lda Player_PageLoc
 adc #0
 sta M3ShotPage,x
 rts
.endproc
.proc M3AdvanceShot
 lda M3ShotX,x
 sta M3ShotOldX
 jsr M3ShotNative::PRG007_A361
 lda M3ShotVX,x
 bmi Left
 lda M3ShotX,x
 cmp M3ShotOldX
 bcs Done
 inc M3ShotPage,x
 rts
Left:lda M3ShotX,x
 cmp M3ShotOldX
 bcc Done
 beq Done
 dec M3ShotPage,x
Done:rts
.endproc
.popseg
