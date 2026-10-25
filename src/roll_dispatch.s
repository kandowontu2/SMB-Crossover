.pushseg
.segment "ROLL_WORLD"
.proc RlIsActive
 lda SelectedCharacter
 cmp #CHARACTER_BASS
 bne No
 lda RlVariant
 beq No
 sec
 rts
No:clc
 rts
.endproc
.macro RlGate Name,Legacy,Own
.proc Name
 php
 pha
 jsr RlIsActive
 bcs Active
 pla
 plp
 farcall Legacy,jmp
Active:pla
 plp
 farcall Own,jmp
.endproc
.endmacro
RlGate RlMovementDispatch,SpecialMovement,RlMovement
RlGate RlAdderDispatch,LmAdderGate,RlAdder
RlGate RlBoxDispatch,LmBoxGate,RlBox
RlGate RlGraphicsDispatch,LmGraphicsGate,RlGraphics
RlGate RlPortraitDispatch,LmPortraitGate,RlPortrait
RlGate RlWeaponsDispatch,LmWeaponsGate,RlWeapons
RlGate RlDrawDispatch,LmDrawGate,RlDraw
RlGate RlUiDispatch,LmUiGate,RlUi
RlGate RlInjuryDispatch,LmInjuryGate,RlInjury
RlGate RlInjuryStatusDispatch,LmInjuryStatusGate,RlInjuryStatus
RlGate RlVisibleDispatch,LmVisibleGate,RlVisible
RlGate RlPrepareDispatch,LmPrepareGate,RlPrepare
RlGate RlCollectDispatch,LmCollectGate,RlCollect
RlGate RlNameDispatch,LmStatusNameGate,RlStatusName
.proc RlResetDispatch
 farcall LmResetGate
 jsr RlIsActive
 bcc Done
 farcall RlResetOwn,jmp
Done:rts
.endproc
.proc RlDeathStartDispatch
 farcall LmDeathStartGate
 jsr RlIsActive
 bcc Done
 farcall RlDeathStart,jmp
Done:rts
.endproc
.proc RlDeathDispatch
 jsr RlIsActive
 bcc Original
 farcall MegaManDeathUpdate,jmp
Original:farcall LmDeathGate,jmp
.endproc
.proc RlSupportedDispatch
 jsr RlIsActive
 bcc Original
 clc
 rts
Original:farcall LmSupportedGate,jmp
.endproc
.proc RlLegacyDispatch
 jsr RlIsActive
 bcc Original
 clc
 rts
Original:farcall LmLegacyGate,jmp
.endproc
.proc RlDropDispatch
 php
 pha
 phx
 phy
 jsr RlIsActive
 bcc Original
 ldy #3
Find:lda InvDropKind,y
 beq Save
 dey
 bpl Find
 jmp Restore
Save:sty RlDropSlot
 farcall InventoryEnemyDrop
 ldy RlDropSlot
 lda InvDropKind,y
 beq Restore
 lda PseudoRandomBitReg+3
 and #1
 beq Energy
 lda #$80
Energy:sta AvDropItem,y
 jmp Restore
Original:
 ply
 plx
 pla
 plp
 farcall TnEnemyDropDispatch,jmp
Restore:ply
 plx
 pla
 plp
 rts
.endproc
.proc RlFullShotBankDispatch
 jsr RlIsActive
 bcc Legacy
 rts                          ; Own projectiles use window7; preserve native4.
Legacy:jmp RlOriginalFullShotBank
.endproc
.proc RlSpecialDrawDispatch
 jsr RlIsActive
 bcs Done
 farcall JnSpecialDrawDispatch,jmp
Done:rts
.endproc
.proc RlLegacyDrawDispatch
 jsr RlIsActive
 bcc Other
 farcall RlDraw,jmp
Other:
 lda SelectedCharacter
 cmp #CHARACTER_LINK
 bne Scrooge
 lda Z2Variant
 cmp #1
 bne Native
 farcall Z2DrawShots,jmp
Scrooge:
 cmp #CHARACTER_SCROOGE
 bne Native
 farcall DwDrawShots,jmp
Native:
 farcall RosterDrawShots,jmp
.endproc
.proc RlRefillDispatch
 pha
 jsr RlIsActive
 bcs Own
 pla
 farcall InventoryRefillAmount,jmp
Own:pla
 lsr
 lsr                         ; Native item amount2/10, not shared scaled8/40.
 sta RlTemp
 ldx InvDropSlot
 lda AvDropItem,x
 bmi Health
 lda RlEnergy
 clc
 adc RlTemp
 cmp #29
 bcc EnergySave
 lda #28
EnergySave:sta RlEnergy
 bne Feedback
Health:lda RlHealth
 clc
 adc RlTemp
 cmp #29
 bcc HealthSave
 lda #28
HealthSave:sta RlHealth
Feedback:lda #1
 sta RlDirty
 lda #Sfx_CoinGrab
 sta Square2SoundQueue
 rts
.endproc
.popseg
