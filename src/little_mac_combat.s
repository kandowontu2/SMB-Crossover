.pushseg
.segment "LM_COMBAT"
.proc LmWeaponsGate
 TnHotGate TnAllWeapons
 php
 pha
 farcall LmIsActive
 jcs Own
 pla
 plp
 farcall NrWeapons,jmp
Own:pla
 plp
 lda TimerControl
 jne Done
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda MmDeathFlag
 jne Done
 lda LmAttack
 bne Attack
 lda LmHurt
 jne Done
 lda LmFresh
 and #B_Button
 jeq Done
 jsr MacRosterCanAfford
 jcc Done
 lda #0
 sta LmHits
 sta LmBlockHit
 sta LmSuper
 lda SavedJoypadBits
 and #Up_Dir
 beq Normal
 lda LmStars
 jeq Done
 dec LmStars
 inc LmSuper
 jmp Begin
Normal:
Begin:
 jsr MacRosterAttackTotal
 sta LmAttack
 jsr MacRosterSpendHearts
 lda #1
 sta LmDirty
 lda #Sfx_Fireball
 sta Square1SoundQueue
Attack:
 jsr MacRosterAttackWindow
 jcc Done
 lda LmSuper
 bne Super
 lda MacRosterNormalHeight,x
 sta LmRectH
 lda Player_Y_Position
 clc
 adc #5
 ldx RgCrouch
 beq :+
 adc #16
:sta LmRectY
 jmp Rect
Super:
 lda MacRosterSuperHeight,x
 sta LmRectH
 lda Player_Y_Position
 sec
 sbc #20
 sta LmRectY
Rect:
 jsr MacRosterVariant
 tax
 lda MacRosterPunchReach,x
 sta LmRectW
 lda Player_X_Position
 clc
 adc #13
 sta LmRectX
 lda Player_PageLoc
 adc #0
 sta LmRectPage
 lda PlayerFacingDir
 cmp #2
 bne Hit
 lda Player_X_Position
 clc
 adc #2
 sta LmRectX
 lda Player_PageLoc
 adc #0
 sta LmRectPage
 lda LmRectX
 sec
 sbc LmRectW
 sta LmRectX
 lda LmRectPage
 sbc #0
 sta LmRectPage
Hit:
 jsr LmHitEnemies
 lda LmBlockHit
 jne Done
 lda PlayerFacingDir
 cmp #2
 beq LoadLeftProbe
 lda LmRectW
 sec
 sbc #1
 clc
 adc LmRectX
 sta MmProbeX
 lda LmRectPage
 adc #0
 jmp ProbePage
LoadLeftProbe:
 lda LmRectX
LeftProbe:
 sta MmProbeX
 lda LmRectPage
ProbePage:
 sta MmProbePage
 lda LmRectY
 clc
 adc #4
 sta MmProbeY
 jsr LmBlockPoint
 bcc Done
 inc LmBlockHit
Done:rts
.endproc
.proc LmHitEnemies
 ldx #5
Loop:stx LmHitSlot
 lda Enemy_Flag,x
 jeq Next
 jmi Next
 lda Enemy_State,x
 and #$20
 jne Next
 lda Enemy_ID,x
 cmp #Bowser
 jeq Eligible
 cmp #$15
 jcs Next
 cmp #Podoboo
 jeq Next
 cmp #BuzzyBeetle
 bne Eligible
 lda LmSuper
 jeq Next
Eligible:
 lda Enemy_Y_HighPos,x
 cmp #1
 jne Next
 lda Enemy_X_Position,x
 sec
 sbc LmRectX
 sta R0
 lda Enemy_PageLoc,x
 sbc LmRectPage
 sta R1
 lda R0
 clc
 adc #15
 sta R0
 lda R1
 adc #0
 jne Next
 lda LmRectW
 clc
 adc #15
 cmp R0
 jcc Next
 jeq Next
 lda Enemy_Y_Position,x
 sec
 sbc LmRectY
 clc
 adc #23
 sta R0
 lda LmRectH
 clc
 adc #23
 cmp R0
 jcc Next
 jeq Next
 lda Bits,x
 and LmHits
 jne Next
 lda Bits,x
 ora LmHits
 sta LmHits
 lda LmHearts
 clc
 adc #1
 cmp #21
 bcc :+
 lda #20
:sta LmHearts
 lda #1
 sta LmDirty
 lda Enemy_ID,x
 cmp #Bowser
 bne Normal
 stx R1
 jsr HandleEnemyFBallCol
 jmp Next
Normal:stx ObjectOffset
 jsr ShellOrBlockDefeat
 lda #Sfx_EnemySmack
 sta Square1SoundQueue
Next:ldx LmHitSlot
 dex
 jpl Loop
 rts
Bits:.byte 1,2,4,8,16,32
.endproc
.popseg

.pushseg
.segment "LM_COMBAT"
.proc LmBlockPoint
 lda MmProbeY
 cmp #32
 bcc Empty
 cmp #240
 bcs Empty
 and #$f0
 sec
 sbc #32
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
 beq Empty
 cmp #$23
 beq Empty
 cmp #$26
 beq Empty
 cmp #$c2
 beq Empty
 cmp #$c3
 beq Empty
 sta R3
 jsr BlockBumpedChk
 bcs Activate
 lda R3
 cmp #$51
 beq Activate
 cmp #$52
 bne OtherTerrain
 ; The parser marks foundation cells independently of shared brick artwork.
 clc
 lda R6
 adc #<(MmSolidTerrain-Block_Buffer_1)
 sta M0
 lda R7
 adc #>(MmSolidTerrain-Block_Buffer_1)
 sta M1
 ldy R2
 lda (M0),y
 beq Activate
 bne Solid
OtherTerrain:
 ldy R3
 lda MTileAttribute,y
 and #MTILE_SOLID
 beq Empty
Solid:sec
 rts
Empty:clc
 rts
Activate:
 phx
 lda ObjectOffset
 pha
 lda MmProbeX
 sta MmBulletX
 lda MmProbePage
 sta MmBulletPage
 lda MmProbeY
 sta MmBulletY
 lda PlayerFacingDir
 sta MmBulletDir
 lda #10 ; zero-extents native point; never enters the extra melee corner loop
 sta MmBulletType
 ldx #0
 stx MmSlot
 farcall MegaManWeapons::BombPoint
 lda #0
 sta MmBulletType
 pla
 sta ObjectOffset
 plx
 sec
 rts
.endproc

.popseg
