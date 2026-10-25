; SMB3 projectiles retain source weapon admission/lifetime against SMB foes.
; Bowser damage uses the host's existing HP and native defeat progression.
.pushseg
.segment "M3_LOGIC"
.proc M3ProjectileAdmission
 lda Enemy_ID,y
 cmp #Bowser
 beq Allowed
 cmp #BuzzyBeetle
 bne Ordinary
 ldx M3SavedSlot
 lda M3ShotKind,x
 cmp #2
 bne BeetleFire
 lda #0 ; Only the following temporary ID filters see this value.
Allowed:clc
 rts
BeetleFire:lda #BuzzyBeetle
Ordinary:cmp #$15
 rts
.endproc
.proc M3ProjectileDamage
 lda Enemy_ID,x
 cmp #Bowser
 beq Boss
 jmp M3DefeatEnemy
Boss:stx R1
 jmp HandleEnemyFBallCol
.endproc
.popseg
