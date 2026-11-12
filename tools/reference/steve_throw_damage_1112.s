; X is an admitted native enemy. Only surviving robot contacts enter here;
; fatal actor $FF must branch to destruction before this call.
.setcpu "6502"
.segment "THROW_DAMAGE"
SteveThrowDamageEnemy:
    lda SteveBotActor
    ora #$80
    sta SteveBotActor          ; Return receipt precedes enemy cooldown.
    lda JnEnemyHurt,x
    bne ThrowDamageDone
    lda #12
    sta JnEnemyHurt,x
    lda JnEnemyHP,x
    sec
    sbc #2
    bcc ThrowEnemyDefeat
    beq ThrowEnemyDefeat
    sta JnEnemyHP,x
    lda #8
    ora Square1SoundQueue
    sta Square1SoundQueue
ThrowDamageDone:
    rts
ThrowEnemyDefeat:
    jmp DefeatEnemy
