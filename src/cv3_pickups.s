; Native SMB powerup actors retain their 48-frame emergence/collision path.
; CV3 one-carried-subweapon replaces the old Simon inventory, never another
; character owner's records. SMB block locations and enemy drops are adaptations.
.pushseg
.segment "CV3_CORE"
.proc Cv3PreparePickupGate
 Cv3Gate Z2PreparePickupGate
 stx InvObject
 jsr Cv3Ensure
 ldx InvObject
 lda #0
 sta InvRisePhase,x
 sta InvPickupSaveLo,x
 lda Cv3Variant
 sta Cv3PickupVariant,x
 lda #CHARACTER_SIMON
 sta InvPickupOwner,x
 lda PowerUpType,x
 cmp #2
 jcs Vanilla
 jeq Vanilla
 cmp #0
 jne Upgrade
 lda #$d0
 jne Stamp
Upgrade:
 ldy Cv3Variant
 dey
 lda Cv3Subweapon,y
 clc
 adc #1
 cmp #4
 bcc :+
 lda #1
: clc
 adc #$d0
 ldy Cv3Variant
 cpy #3
 jne Stamp
 lda #$d4
Stamp:
 sta InvPickup,x
 lda #1
 sta PowerUpType,x
 lda InvPickup,x
 cmp #$d0
 bne :+
 lda #0
 sta PowerUpType,x
:
 rts
Vanilla:
 lda #$fc
 sta InvPickup,x
 rts
.endproc
.proc Cv3CollectPickupGate
 stx InvObject
 Cv3Gate Z2CollectPickupGate
 ldx InvObject
 lda InvPickupOwner,x
 cmp #CHARACTER_SIMON
 jne No
 lda Cv3PickupVariant,x
 cmp Cv3Variant
 jne No
 lda InvPickup,x
 cmp #$d0
 jcc No
 cmp #$d5
 jcs No
 sec
 sbc #$d0
 sta Cv3Temp
 ldy Cv3Variant
 dey
 lda Cv3Temp
 jeq Heal
 cmp #4
 jeq Power
 sta Cv3Subweapon,y
 lda Cv3Hearts,y
 clc
 adc #5
 cmp #100
 jcc Hearts
 lda #99
Hearts:sta Cv3Hearts,y
 jmp Sound
Power:
 lda Cv3Power,y
 cmp #2
 jcs Heal
 clc
 adc #1
 sta Cv3Power,y
 jne Sound
Heal:
 lda Cv3Health,y
 clc
 adc #16
 cmp #65
 bcc :+
 lda #64
: sta Cv3Health,y
Sound:
 lda #1
 sta PlayerStatus
 lda #Sfx_PowerUpGrab
 sta Square2SoundQueue
 ldx InvObject
 lda #0
 sta InvPickup,x
 sta Cv3PickupVariant,x
 sec
 rts
No:clc
 rts
.endproc
.proc Cv3PrivatePickupGate
 Cv3Gate DwPrivatePickup
 lda Enemy_ID,x
 cmp #PowerUpObject
 jne No
 lda Cv3PickupVariant,x
 cmp Cv3Variant
 jne No
 lda InvPickupOwner,x
 cmp #CHARACTER_SIMON
 jne No
 lda InvPickup,x
 cmp #$d1
 jcc No
 cmp #$d5
 jcs No
 sec
 rts
No:clc
 rts
.endproc
.proc Cv3RisePickupGate
 Cv3Gate DwRisePickup
 farcall InventoryRisePickup
 php
 lda InvPickup,x
 cmp #$d0
 jne Done
 lda Enemy_State,x
 jpl Done
 lda #1
 sta Enemy_MovingDir,x
 lda #$10
 sta Enemy_X_Speed,x
Done:plp
 rts
.endproc
.proc Cv3InjuryStatusGate
 Cv3Gate VvInjuryStatusDispatch
 lda #1
 tax
 rts
.endproc
.proc Cv3SupportedGate
 Cv3Gate Z2InventorySupportedGate
 sec
 rts
.endproc
.proc Cv3UiGate
 Cv3Gate Z2UiTickGate
 lda #0
 sta InvHudActive
 sta InvDirty
 rts
.endproc
.proc Cv3LegacyGate
 Cv3Gate Z2InventoryLegacyClassicGate
 sec
 rts
.endproc
.proc Cv3InjuryStartGate
 Cv3Gate VvInjuryDispatch
 ldy Cv3Variant
 dey
 lda Cv3Invul
 jne Protected
 lda #4
 ldx ObjectOffset
 ldy Enemy_ID,x
 cpy #Bowser
 jeq Major
 cpy #HammerBro
 jne Damage
 lda #8
 jne Damage
Major:lda #16
Damage:sta Cv3Temp
 ldy Cv3Variant
 dey
 lda Cv3Health,y
 sec
 sbc Cv3Temp
 jcc Dead
 jeq Dead
 sta Cv3Health,y
 lda #64
 sta Cv3Invul
 lda #16
 sta Cv3HurtAge
 lda #0
 sta Cv3AttackAge
 sta Cv3Climb
 sta Cv3Bat
 sta GuestHurtKind
 sta GuestHurtTicks
 sta PlayerChangeSizeFlag
 sta TimerControl
 sta Cv3VyLo
 lda #$fd
 sta Cv3VyHi
 lda #1
 sta Player_State
 lda #0
 sta Cv3VxLo
 lda #1
 ldx PlayerFacingDir
 cpx #2
 jeq Recoil
 lda #$ff
Recoil:sta Cv3VxHi
 jsr Cv3DmcInjuryQueue
 .res 2,$ea ; same five-byte injury cue span
Protected:sec
 rts
Dead:
 lda #0
 sta Cv3Health,y
 jmp KillPlayer
.endproc
.proc Cv3StatusNameGate
 pha
 jsr Cv3IsActive
 jcs Native
 pla
 farcall DwStatusName,jmp
Native:pla
 cmp #0
 jne Done
 phx
 lda Cv3Variant
 sec
 sbc #1
 sta Cv3Temp
 asl
 asl
 asl
 sec
 sbc Cv3Temp
 tax
 ldy #0
Loop:lda Names,x
 sta VRAM_Buffer1+11,y
 inx
 iny
 cpy #7
 jcc Loop
 plx
Done:rts
Names:.byte "GRANT  ","SYPHA  ","ALUCARD"
.endproc
.popseg
