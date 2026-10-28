.export RcWeapons,RcEnemyEligible,RcOverlap,RcStartAttack,RcTryGrab,RcThrow
.pushseg
.segment "RIVER_CITY_CORE"
.proc RcWeapons
 lda TimerControl
 ora MmDeathFlag
 jne Done
 lda GamePauseStatus
 and #1
 jne Done
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda ObjectOffset
 sta RcSavedObject
 jsr RcUpdateEnemies
 lda RcThrowAge
 beq Input
 dec RcThrowAge
 bne ThrowContact
 lda #$ff
 sta RcThrowSlot
 jmp Input
ThrowContact:
 jsr RcThrownContact
Input:
 lda RcHurtMove
 jne Finish
 lda RcCarrySlot
 cmp #$ff
 beq Attack
 lda RcFresh
 and #B_Button
 beq Finish
 jsr RcThrow
 jmp Finish
Attack:
 lda RcAttack
 bne Hit
 lda RcFresh
 and #B_Button
 bne Start
 ldx RcVariant
 lda RcTier,x
 beq Finish
 lda RcHeld
 and #B_Button
 beq Finish
Start:
 lda RcHeld
 and #Up_Dir
 beq Strike
 jsr RcTryGrab
 bcs Finish
Strike:
 jsr RcStartAttack
Hit:
 lda RcAttack
 cmp #4
 bcc Finish
 cmp #11
 bcs Finish
 jsr RcAttackRectangle
 ldx #5
Loop:
 stx RcSlot
 jsr RcEnemyEligible
 bcc Next
 cpx RcThrowSlot
 beq Next
 lda RcBits,x
 and RcAttackHits
 bne Next
 jsr RcOverlap
 bcc Next
 lda RcBits,x
 ora RcAttackHits
 sta RcAttackHits
 jsr RcDamageEnemy
Next:
 ldx RcSlot
 dex
 bpl Loop
Finish:
 lda RcSavedObject
 sta ObjectOffset
Done:rts
.endproc
.proc RcUpdateEnemies
 ldx #5
Loop:
 jsr RcEnemyEligible
 bcc Clear
 lda Enemy_ID,x
 clc
 adc #1
 cmp RcEnemyType,x
 bne New
 lda Enemy_Flag,x
 cmp RcEnemyStamp,x
 bne New
 ; Slot reuse cannot retain a stun across a distant same-ID respawn.
 lda Enemy_X_Position,x
 sec
 sbc RcEnemyX,x
 sta RcTemp
 lda Enemy_PageLoc,x
 sbc RcEnemyPage,x
 bne High
 lda RcTemp
 cmp #64
 bcc Tick
 bcs New
High:
 cmp #$ff
 bne New
 lda RcTemp
 cmp #192
 bcs Tick
New:
 lda Enemy_ID,x
 clc
 adc #1
 sta RcEnemyType,x
 lda Enemy_Flag,x
 sta RcEnemyStamp,x
 lda #0
 sta RcEnemyStun,x
 lda #6
 ldy Enemy_ID,x
 cpy #Goomba
 bne :+
 lda #4
:cpy #HammerBro
 bne :+
 lda #8
:cpy #Bowser
 bne :+
 lda #24
:sta RcEnemyHP,x
Tick:
 lda RcEnemyStun,x
 beq Cache
 dec RcEnemyStun,x
Cache:
 lda Enemy_X_Position,x
 sta RcEnemyX,x
 lda Enemy_PageLoc,x
 sta RcEnemyPage,x
 jmp Next
Clear:
 lda #0
 sta RcEnemyHP,x
 sta RcEnemyType,x
 sta RcEnemyStun,x
 cpx RcCarrySlot
 bne Next
 lda #$ff
 sta RcCarrySlot
Next:
 dex
 jpl Loop
 rts
.endproc
.proc RcStartAttack
 lda #1
 sta RcAttackKind
 lda RcHeld
 and #Down_Dir
 beq Air
 inc RcAttackKind
Air:
 lda Player_State
 beq Running
 lda #3
 sta RcAttackKind
Running:
 lda #14                      ; finite three-frame windup/contact/recovery
 sta RcAttack
 lda #0
 sta RcAttackHits
 lda PlayerFacingDir
 sta RcAttackFace
 lda #Sfx_Fireball
 sta Square1SoundQueue
 rts
.endproc
.proc RcAttackRectangle
 lda #20
 sta RcRectW
 lda #12
 sta RcRectH
 lda Player_Y_Position
 clc
 adc #8
 ldy RcAttackKind
 cpy #2
 bne :+
 clc
 adc #8                       ; native low kick is lower than punch
:sta RcRectY
 lda Player_X_Position
 clc
 adc #8
 sta RcRectX
 lda Player_PageLoc
 adc #0
 sta RcRectPage
 lda RcAttackFace
 cmp #2
 bne Power
 sec
 lda RcRectX
 sbc #20
 sta RcRectX
 lda RcRectPage
 sbc #0
 sta RcRectPage
Power:
 ldx RcVariant
 lda RcTier,x
 clc
 adc #2
 sta RcDamage
 lda RcRun
 beq Done
 inc RcDamage                  ; running strikes have native-style extra force
Done:rts
.endproc
.proc RcEnemyEligible
 cpx #6
 bcs No
 lda Enemy_Flag,x
 beq No
 bmi No
 lda Enemy_State,x
 and #$20
 bne No
 lda Enemy_Y_HighPos,x
 cmp #1
 bne No
 lda Enemy_ID,x
 cmp #Bowser
 beq Yes
 cmp #$15
 bcs No
 cmp #Podoboo
 beq No
 cmp #Goomba
 bne Yes
 lda Enemy_State,x
 cmp #2
 bcs No
Yes:sec
 rts
No:clc
 rts
.endproc
.proc RcOverlap
 ; Signed page-aware native enemy16x24 against the authored action box.
 sec
 lda Enemy_X_Position,x
 sbc RcRectX
 sta RcTemp
 lda Enemy_PageLoc,x
 sbc RcRectPage
 sta RcTemp2
 clc
 lda RcTemp
 adc #15
 sta RcTemp
 lda RcTemp2
 adc #0
 bne No
 lda RcRectW
 clc
 adc #15
 cmp RcTemp
 bcc No
 beq No
 sec
 lda Enemy_Y_Position,x
 sbc RcRectY
 clc
 adc #23
 sta RcTemp
 lda RcRectH
 clc
 adc #23
 cmp RcTemp
 bcc No
 beq No
 sec
 rts
No:clc
 rts
.endproc
.proc RcDamageEnemy
 lda #Sfx_EnemySmack
 sta Square1SoundQueue
 lda #8
 sta MmEnemyFlash,x
 lda RcEnemyHP,x
 sec
 sbc RcDamage
 bcc Defeat
 beq Defeat
 sta RcEnemyHP,x
 lda #36                      ; private stun, native state/AI enum untouched
 sta RcEnemyStun,x
 rts
Defeat:
 lda #0
 sta RcEnemyHP,x
 sta RcEnemyStun,x
 stx ObjectOffset
 lda Enemy_ID,x
 cmp #Bowser
 bne Ordinary
 stx R1
 jsr HandleEnemyFBallCol
 rts
Ordinary:
 jmp ShellOrBlockDefeat          ; native score, drops, defeat, and actor motion
.endproc
.proc RcTryGrab
 lda Player_State
 bne No
 lda #24
 sta RcRectW
 sta RcRectH
 lda Player_X_Position
 sec
 sbc #4
 sta RcRectX
 lda Player_PageLoc
 sbc #0
 sta RcRectPage
 lda Player_Y_Position
 sta RcRectY
 ldx #5
Loop:
 jsr RcEnemyEligible
 bcc Next
 lda Enemy_ID,x
 cmp #Goomba
 beq Type
 cmp #GreenKoopa
 beq Type
 cmp #RedKoopa
 bne Next                       ; no carrying bosses/firebars/controller actors
Type:
 lda RcEnemyStun,x
 beq Next
 jsr RcOverlap
 bcc Next
 stx RcCarrySlot
 lda Enemy_X_Speed,x
 sta RcCarryVX
 lda Enemy_Y_Speed,x
 sta RcCarryVY
 lda Enemy_ID,x
 sta RcCarryType
 lda #0
 sta RcAttack
 sta RcRun
 lda #120
 sta RcGrabAge
 lda #Sfx_Bump
 sta Square1SoundQueue
 sec
 rts
Next:
 dex
 bpl Loop
No:clc
 rts
.endproc
.proc RcThrow
 ldx RcCarrySlot
 cpx #6
 bcs No
 lda Enemy_Flag,x
 beq No
 lda Enemy_ID,x
 cmp RcCarryType
 bne No
 stx ObjectOffset
 stx RcThrowSlot
 lda #48
 sta RcThrowAge
 lda PlayerFacingDir
 sta Enemy_MovingDir,x
 jsr ShellOrBlockDefeat          ; throws use genuine native defeated-enemy arc
 ldx RcThrowSlot
 lda #$30
 ldy PlayerFacingDir
 cpy #1
 beq Speed
 lda #$d0
Speed:
 sta Enemy_X_Speed,x             ; bounded 3px/update thrown-body adaptation
 lda #$fc
 sta Enemy_Y_Speed,x
 lda #4
 sta RcAttackKind
 lda PlayerFacingDir
 sta RcAttackFace
 lda #14
 sta RcAttack
No:
 lda #$ff
 sta RcCarrySlot
 rts
.endproc
.proc RcThrownContact
 ldx RcThrowSlot
 cpx #6
 bcs Done
 lda Enemy_Flag,x
 beq Done
 lda Enemy_ID,x
 cmp RcCarryType
 bne Done
 lda Enemy_State,x
 and #$20
 beq Done
 lda Enemy_X_Position,x
 sta RcRectX
 lda Enemy_PageLoc,x
 sta RcRectPage
 lda Enemy_Y_Position,x
 sta RcRectY
 lda #16
 sta RcRectW
 sta RcRectH
 lda #6
 sta RcDamage
 ldx #5
Loop:
 stx RcSlot
 cpx RcThrowSlot
 beq Next
 jsr RcEnemyEligible
 bcc Next
 lda RcEnemyStun,x
 bne Next
 jsr RcOverlap
 bcc Next
 jsr RcDamageEnemy
Next:
 ldx RcSlot
 dex
 bpl Loop
Done:rts
.endproc
RcBits:.byte 1,2,4,8,16,32
.popseg
