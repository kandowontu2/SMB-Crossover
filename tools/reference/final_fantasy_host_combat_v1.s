; Actual native enemy consumers for the independently tested FF source leaves.
; This module is a typed RAM3 component, not an installed dispatch hook.
; No additional state: source FF scratch/receipts, existing native HP and stack.
.setcpu "6502"
.macpack longbranch
.import SelectedCharacter,GamePauseStatus,TimerControl,MmDeathFlag
.importzp GameEngineSubroutine,ObjectOffset,R1
.importzp Enemy_Flag,Enemy_ID,Enemy_State,Enemy_X_Position,Enemy_PageLoc
.importzp Enemy_Y_Position,Enemy_Y_HighPos
.import Enemy_BoundBoxCtrl,BoundBoxCtrlData,WorldNumber
.import MmEnemyHealthLo,MmEnemyHealthHi,MmEnemyFlash
.import BowserHitPoints,Square1SoundQueue,ShellOrBlockDefeat,HandleEnemyFBallCol
.importzp Goomba,Bowser,Podoboo,BuzzyBeetle,BulletBill_FrenzyVar,BulletBill_CannonVar,Sfx_EnemySmack
.import FfWeapons,FfEnemyContact,FfForgetEnemy,FfEnsure,FfReady
.import FfSlot,FfTemp,FfDamage,FfTargetX,FfTargetPage,FfTargetY,FfTargetW,FfTargetH
.export FfHostTarget,FfHostDamage,FfHostContact,FfHostWeapons,FfHostNewEnemy,FfHostFresh
.segment "FF_HOST_COMBAT"
FfHostCombatBegin:
.export FfHostCombatBegin,FfHostCombatEnd

; X=actual native slot. Cset gives the native inclusive box converted to a
; half-open world rectangle. Native actor X is retained, no screen-byte wrap.
FfHostTarget:
 lda SelectedCharacter
 cmp #22
 jne FfHostNo
 cpx #6
 jcs FfHostNo
 lda Enemy_Flag,x
 jeq FfHostNo
 jmi FfHostNo                 ; Bowser's rear is not another source object.
 lda Enemy_State,x
 and #$20
 jne FfHostNo
 lda Enemy_ID,x
 cmp #Goomba
 bne :+
 lda Enemy_State,x
 cmp #2
 jcs FfHostNo                 ; stomped/dead Goomba is not a fresh target.
:
 lda Enemy_ID,x
 cmp #$15
 bcc FfHostTargetKind
 cmp #Bowser
 beq FfHostTargetKind
 cmp #BulletBill_CannonVar
 jne FfHostNo
FfHostTargetKind:
 lda Enemy_Y_HighPos,x
 cmp #1
 jne FfHostNo
 lda Enemy_BoundBoxCtrl,x
 cmp #FF_NATIVE_BOX_COUNT
 jcs FfHostNo
 asl
 asl
 tay
 lda BoundBoxCtrlData,y
 sta FfTemp
 clc
 adc Enemy_X_Position,x
 sta FfTargetX
 lda #0
 bit FfTemp
 bpl :+
 lda #$ff                    ; signed source left offsets, with real carry.
:adc Enemy_PageLoc,x
 sta FfTargetPage
 lda Enemy_Y_Position,x
 clc
 adc BoundBoxCtrlData+1,y
 jcs FfHostNo                 ; below-screen top must not wrap into the HUD.
 sta FfTargetY
 lda BoundBoxCtrlData+2,y
 sec
 sbc BoundBoxCtrlData,y
 clc
 adc #1
 beq FfHostNo
 cmp #65
 bcs FfHostNo
 sta FfTargetW
 lda BoundBoxCtrlData+3,y
 sec
 sbc BoundBoxCtrlData+1,y
 clc
 adc #1
 beq FfHostNo
 cmp #65
 bcs FfHostNo
 sta FfTargetH
 sec
 rts
FfHostNo:
 clc
 rts

; X=actual enemy, source FfDamage is in 2.02 HP units. Cset means accepted
; damage. Default character/projectile pierce cannot defeat armored targets.
; Ice has its source damage; this adapter does not invent a freeze property.
FfHostDamage:
 lda SelectedCharacter
 cmp #22
 bne FfHostNo
 cpx #6
 bcs FfHostNo
 lda FfDamage
 beq FfHostNo
 lda Enemy_ID,x
 cmp #Podoboo
 beq FfHostNo
 cmp #BuzzyBeetle
 beq FfHostNo
 cmp #BulletBill_FrenzyVar
 beq FfHostNo
 cmp #BulletBill_CannonVar
 beq FfHostNo
 lda MmEnemyHealthLo,x
 ora MmEnemyHealthHi,x
 bne FfHostHealthReady
 lda Enemy_ID,x
 cmp #Bowser
 beq FfHostBossHealth
 cmp #21
 bcs FfHostNo
 tay
 lda FfHostHealth202,y
 ldy #0
 beq FfHostStoreHealth
FfHostBossHealth:
 lda WorldNumber
 cmp #7
 bcs FfHostBoss1100
 cmp #5
 bcs FfHostBoss900
 lda #<600
 ldy #>600
 bne FfHostStoreHealth
FfHostBoss900:
 lda #<900
 ldy #>900
 bne FfHostStoreHealth
FfHostBoss1100:
 lda #<1100
 ldy #>1100
FfHostStoreHealth:
 sta MmEnemyHealthLo,x
 tya
 sta MmEnemyHealthHi,x
FfHostHealthReady:
 lda MmEnemyHealthLo,x
 sec
 sbc FfDamage
 sta MmEnemyHealthLo,x
 lda MmEnemyHealthHi,x
 sbc #0
 sta MmEnemyHealthHi,x
 bcc FfHostDefeat
 ora MmEnemyHealthLo,x
 beq FfHostDefeat
 lda #2
 sta MmEnemyFlash,x
 lda #Sfx_EnemySmack
 sta Square1SoundQueue
 sec
 rts
FfHostDefeat:
 lda #0
 sta MmEnemyHealthLo,x
 sta MmEnemyHealthHi,x
 lda ObjectOffset
 pha
 txa
 pha
 stx ObjectOffset
 stx R1
 lda Enemy_ID,x
 cmp #Bowser
 bne FfHostOrdinaryDefeat
 lda #1
 sta BowserHitPoints
 jsr HandleEnemyFBallCol      ; real native transformation, score and defeat.
 jmp FfHostDefeatDone
FfHostOrdinaryDefeat:
 jsr ShellOrBlockDefeat       ; real native direction, number, score and SFX.
FfHostDefeatDone:
 pla
 tax
 pla
 sta ObjectOffset
 sec
 rts

; A=FF melee or genuine source projectile offset0/12/24. X is always retained.
FfHostContact:
 pha
 jsr FfHostTarget
 pla
 bcc FfHostContactDone
 sta FfSlot
 txa
 pha
 lda FfSlot
 jsr FfEnemyContact
 pla
 tax
 bcc FfHostContactDone
 jmp FfHostDamage
FfHostContactDone:
 rts

; One genuine source weapon update, followed by its existing per-object
; dictionaries. Dead targets cannot be processed by later shots in the loop.
FfHostWeapons:
 lda SelectedCharacter
 cmp #22
 bne FfHostWeaponsDone
 lda GameEngineSubroutine
 cmp #8
 bne FfHostWeaponsDone
 lda GamePauseStatus
 and #1
 bne FfHostWeaponsDone
 lda TimerControl
 ora MmDeathFlag
 bne FfHostWeaponsDone
 jsr FfWeapons
 ldx #5
FfHostActorLoop:
 lda #$ff
 jsr FfHostContact
 lda #0
 jsr FfHostContact
 lda #12
 jsr FfHostContact
 lda #24
 jsr FfHostContact
 dex
 bpl FfHostActorLoop
FfHostWeaponsDone:
 rts

; Genuine new native identity, including same-ID slot reuse. Preserve the
; native initialization caller's entire register/flag contract.
FfHostNewEnemy:
 php
 pha
 txa
 pha
 tya
 pha
 lda SelectedCharacter
 cmp #22
 bne FfHostNewEnemyDone
 jsr FfForgetEnemy
FfHostNewEnemyDone:
 pla
 tay
 pla
 tax
 pla
 plp
 rts

; Actual new-game owner constructor; preserve the class selected in the menu.
FfHostFresh:
 lda #0
 sta FfReady
 jmp FfEnsure
.include "ff-host-health.inc"
FfHostCombatEnd:
