.pushseg
.segment "Z2_LOGIC"
.proc Z2InjuryStatusGate
 jsr Z2IsActive
 bcc Original
 ldx #1
 txa
 rts
Original:
 farcall DwInjuryStatus,jmp
.endproc
.proc Z2InjuryStartGate
 jsr Z2IsActive
 bcs Active
 farcall DwInjuryStart,jmp
Active:
 ldy ObjectOffset
 lda Enemy_ID,y
 cmp #Bowser
 beq BowserHit
 cmp #HammerBro
 beq HammerHit
 cmp #PiranhaPlant
 beq PlantHit
 cmp #Goomba
 beq SmallHit
 lda #1
 bne Damage
BowserHit:lda #6
 bne Damage
HammerHit:lda #3
 bne Damage
PlantHit:lda #2
 bne Damage
SmallHit:lda #0
Damage:
 jsr Z2Damage
 bcc Survive
 jmp KillPlayer
Survive:
 lda #32
 sta Z2HurtTimer
 lda #4
 sta InjuryTimer
 lda #0
 sta GuestHurtKind
 sta GuestHurtTicks
 sta Z2AttackStage
 sta TimerControl
 sta PlayerChangeSizeFlag
 lda #$fe
 sta Z2NativeVY
 sta Player_Y_Speed
 lda #2
 sta Z2NativeAir
 sta Player_State
 ldy ObjectOffset
 lda Enemy_X_Position,y
 cmp Player_X_Position
 bcc EnemyLeft
 lda #$f3
 bne Recoil
EnemyLeft:lda #13
Recoil:sta Z2NativeVX
 lda #Sfx_PipeDown_Injury
 sta Square1SoundQueue
 sec
 rts
.endproc
.popseg
