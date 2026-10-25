; Native damage/thrust arithmetic; SMB enemy classification is adaptation data.
.pushseg
.segment "Z2_LOGIC"
Z2RectX=Z2BodyScratch
Z2RectPage=Z2BodyScratch+1
Z2RectY=Z2BodyScratch+2
Z2RectW=Z2BodyScratch+3
Z2RectH=Z2BodyScratch+4
Z2HitSlot=Z2BodyScratch+5
Z2HitDamage=Z2BodyScratch+6
Z2ShotSlot=Z2BodyScratch+7
.proc Z2WeaponsGate
 jsr Z2IsActive
 bcs Active
 farcall RosterWeapons,jmp
Active:
 lda TimerControl
 jne Done
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda MmDeathFlag
 jne Done
 lda Z2NativeSound2
 beq :+
 lda #1
 sta RgSfx ; Existing authentic Zelda1 sword driver until Z2 audio integration.
 lda #0
 sta Z2NativeSound2
:
 jsr Z2SpellWorldEffects
 jsr Z2Projectiles
 jsr Z2SwordRect
 jsr Z2SwordBlocks
 lda #5
 sta Z2HitSlot
Enemy:
 ldx Z2HitSlot
 jsr Z2EnemyEligible
 bcc Clear
 jsr Z2RectOverlap
 bcc NotContact
 lda Z2EnemyExpReceipt,x
 and #$40
 bne Next
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
 bne Upward
 lda #$fe ; native downward-thrust bounce, not a new jump impulse.
 sta Z2NativeVY
 sta Player_Y_Speed
 lda #2
 sta Z2NativeAir
 sta Player_State
 bne Next
Upward:cmp #8
 bne Next
 lda #0
 sta Z2NativeVY
 sta Player_Y_Speed
 beq Next
NotContact:
 lda Z2EnemyExpReceipt,x
 and #$bf
 sta Z2EnemyExpReceipt,x
 jmp Next
Clear:
 lda #0
 sta Z2EnemyExpReceipt,x
 sta Z2EnemyHp,x
Next:dec Z2HitSlot
 jpl Enemy
 jsr Z2TrySpawnBeam
Done:rts
.endproc
.proc Z2SwordRect
 lda #0
 sta Z2RectW
 lda Z2ActiveSpells
 and #8
 jne Done
 lda Z2CachedPose
 cmp #5
 beq Standing
 cmp #7
 beq Crouching
 cmp #8
 beq Up
 cmp #9
 beq Down
 rts
Standing:lda #7
 bne Horizontal
Crouching:lda #23
Horizontal:clc
 adc Player_Y_Position
 sta Z2RectY
 lda #14
 sta Z2RectW
 lda #3
 sta Z2RectH
 lda #16 ; E9A2: nativeSwordX+(-8), canonicalX=nativeX+8.
 ldy PlayerFacingDir
 cpy #1
 beq PlaceX
 lda #$f2 ; E9A2: nativeSwordX+2 => canonicalX-14.
 bne PlaceX
Up:lda #4
 ldy PlayerFacingDir
 cpy #1
 beq :+
 lda #$f8
:sta R2
 lda Player_Y_Position
 sec
 sbc #4
 jmp Vertical
Down:lda #0
 sta R2
 lda Player_Y_Position
 clc
 adc #33
Vertical:sta Z2RectY
 lda #14
 sta Z2RectW
 lda #3
 sta Z2RectH
 lda R2
PlaceX:sta R0
 lda #0
 ldy R0
 bpl :+
 lda #$ff
:sta R1
 clc
 lda Player_X_Position
 adc R0
 sta Z2RectX
 lda Player_PageLoc
 adc R1
 sta Z2RectPage
Done:rts
.endproc
.proc Z2RectOverlap
 lda Z2RectW
 beq No
 lda Enemy_Y_HighPos,x
 cmp #1
 bne No
 lda Enemy_X_Position,x
 sec
 sbc Z2RectX
 sta R0
 lda Enemy_PageLoc,x
 sbc Z2RectPage
 sta R1
 clc
 lda R0
 adc #16
 sta R0
 lda R1
 adc #0
 bne No
 lda Z2RectW
 clc
 adc #16
 cmp R0
 bcc No
 beq No
 lda Enemy_Y_Position,x
 clc
 adc #8
 sec
 sbc Z2RectY
 clc
 adc #16
 sta R0
 lda Z2RectH
 clc
 adc #16
 cmp R0
 bcc No
 beq No
 sec
 rts
No:clc
 rts
.endproc
.proc Z2EnemyEligible
 lda Enemy_Flag,x
 beq No
 bmi No
 lda Enemy_State,x
 and #$20
 bne No
 lda Enemy_ID,x
 cmp #Goomba
 bne Class
 lda Enemy_State,x
 cmp #2
 bcs No
Class:lda Enemy_ID,x
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
; A=actual native damage2..50, X=canonical live SMB enemy. HPzero survives.
.proc Z2HitEnemy
 sta Z2HitDamage
 jsr Z2EnemyEligible
 bcc Done
 lda Enemy_ID,x
 clc
 adc #1
 sta R0
 lda Z2EnemyExpReceipt,x
 and #$3f
 cmp R0
 beq Damage
 lda Z2EnemyExpReceipt,x
 and #$c0
 ora R0
 sta Z2EnemyExpReceipt,x
 ldy Enemy_ID,x
 lda EnemyHp,y
 sta Z2EnemyHp,x
Damage:
 lda Z2EnemyHp,x
 sec
 sbc Z2HitDamage
 bcc Defeat
 sta Z2EnemyHp,x
 lda #48 ; source enemy hit-state flash duration, not a sword cooldown.
 sta MmEnemyFlash,x
 lda #Sfx_EnemySmack
 sta Square1SoundQueue
Done:rts
Defeat:
 lda Enemy_ID,x
 cmp #Bowser
 bne Normal
 jsr Z2AwardEnemy
 lda #1
 sta BowserHitPoints
 stx R1
 jsr HandleEnemyFBallCol
 rts
Normal:
 stx ObjectOffset
 jsr ShellOrBlockDefeat
 rts
.endproc
.proc Z2EnemyDropGate
 php
 pha
 txa
 pha
 tya
 pha
 jsr Z2IsActive
 bcc Original
 jsr Z2AwardEnemy
 pla
 tay
 pla
 tax
 pla
 plp
 rts
Original:pla
 tay
 pla
 tax
 pla
 plp
 farcall InventoryEnemyDrop,jmp
.endproc
.proc Z2AwardEnemy
 jsr Z2EnemyEligible
 bcc Done
 lda Z2EnemyExpReceipt,x
 bmi Done
 ora #$80
 sta Z2EnemyExpReceipt,x
 stx Z2HitSlot
 ldy Enemy_ID,x
 lda EnemyExp,y
 ldy #0
 jsr Z2QueueExp
 ldx Z2HitSlot
 ldy Enemy_ID,x
 lda EnemyDropGroup,y
 beq Done
 pha
 lda PseudoRandomBitReg+1,x
 tax
 pla
 jsr Z2DropRoll
 beq Restore
 sta R4
 ldx #5
Find:lda Z2DropKind,x
 beq Spawn
 dex
 bpl Find
 bmi Restore
Spawn:lda R4
 sta Z2DropKind,x
 ldy Z2HitSlot
 clc
 lda Enemy_X_Position,y
 adc #8
 sta Z2DropX,x
 lda Enemy_PageLoc,y
 adc #0
 sta Z2DropPage,x
 lda Enemy_Y_Position,y
 clc
 adc #8
 sta Z2DropY,x
 lda #0
 sta Z2DropAge,x
 sta Z2DropVY,x
 sta Z2DropFraction,x
Restore:ldx Z2HitSlot
Done:rts
.endproc
; SMB counterpart classes, explicitly not originalZ2 enemy placements/stats.
; Index follows native SMB IDs00..2D. InclusiveHP3 means two level1 swordhits.
EnemyHp:
.repeat 52,I
 .if I=Bowser
 .byte 47
 .elseif I=HammerBro
 .byte 15
 .elseif I=Goomba
 .byte 3
 .else
 .byte 5
 .endif
.endrepeat
EnemyExp:
.repeat 52,I
 .if I=Bowser
 .byte 200
 .elseif I=HammerBro
 .byte 50
 .elseif I=PiranhaPlant
 .byte 20
 .elseif I=Goomba
 .byte 2
 .else
 .byte 5
 .endif
.endrepeat
EnemyDropGroup:
.repeat 52,I
 .if I=Bowser
 .byte 0
 .elseif (I=HammerBro) .or (I=PiranhaPlant) .or (I=Lakitu)
 .byte 2
 .else
 .byte 1
 .endif
.endrepeat
.popseg
