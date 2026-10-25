.pushseg
.segment "CD_LOGIC"
.proc CdInjury
 jsr CdIsActive
 bcs Active
 clc
 rts
Active:
 stx CdContactSlot
 lda CdHealth
 beq Fatal
 dec CdHealth
 beq Fatal
 lda #60 ; original hurt/invulnerability intervalD0C7.
 sta CdHurtTimer
 lda #4
 sta InjuryTimer
 lda #0
 sta GuestHurtKind
 sta GuestHurtTicks
 sta TimerControl
 sta PlayerChangeSizeFlag
 lda CdHeld
 beq NoBox
 tax
 dex
 lda #0
 sta CdBoxKind,x
 sta CdHeld
NoBox:
 lda #Sfx_EnemySmack
 sta Square1SoundQueue
 ldx CdContactSlot
 sec
 rts
Fatal:jmp KillPlayer
.endproc
.proc CdBodyContact
 jsr CdIsActive
 jcc Ordinary
 lda CdHide
 jeq Ordinary
 lda CdHeld
 jeq Ordinary
 lda Enemy_Flag,x
 jmi Ordinary
 lda Enemy_ID,x
 cmp #$15
 jcs Ordinary
 cmp #Podoboo
 jeq Ordinary
 stx CdContactSlot
 stx ObjectOffset
 jsr CdDefeatEnemy
 ldx CdHeld
 dex
 lda #0
 sta CdBoxKind,x
 sta CdHeld
 sta CdHide
 ldx CdContactSlot
 sec
 rts
Ordinary:clc
 rts
.endproc
.proc CdPreparePickup
 jsr CdIsActive
 bcc Done
 lda #$fc
 sta InvPickup,x
 lda #$ff
 sta InvPickupOwner,x ; Never index the12-family inventory withrawID14.
Done:rts
.endproc
.proc CdCollectPickup
 jsr CdIsActive
 bcc No
 lda PowerUpType,x
 cmp #2
 bcs No
 cmp #1
 beq Full
 lda CdHealth
 cmp #3
 bcs Sound
 inc CdHealth
 jmp Sound
Full:lda #3
 sta CdHealth
Sound:
 lda #Sfx_PowerUpGrab
 sta Square2SoundQueue
 jsr CdNextFoodStatus
 nop
 nop
 sec
 rts
No:clc
 rts
.endproc
.proc CdHud
 jsr CdIsActive
 bcc Done
 lda OperMode
 cmp #1
 bne Done
 lda DisableScreenFlag
 bne Done
 ldx VRAM_Buffer1_Offset
 cpx #$4d ; 7-byte update and terminator fit the 84-byte queue.
 bcs Done
 lda #$20
 sta VRAM_Buffer1,x
 lda #$4b ; Keep HP and its count together in the white HUD attribute.
 sta VRAM_Buffer1+1,x
 lda #4
 sta VRAM_Buffer1+2,x
 lda #$24
 sta VRAM_Buffer1+3,x
 lda CdHudText
 sta VRAM_Buffer1+4,x
 lda CdHudText+1
 sta VRAM_Buffer1+5,x
 lda CdHealth
 sta VRAM_Buffer1+6,x
 txa
 clc
 adc #7
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
Done:rts
.endproc
CdHudText:.byte "HP"
CdNames:
 .byte " CHIP          "," DALE          "
.export CdNames
.popseg
