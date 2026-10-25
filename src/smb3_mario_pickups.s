; SMB delivery adaptation: actual native actors, visible emergence, collect only.
.pushseg
.segment "M3_LOGIC"
.proc M3PreparePickup
 jsr M3IsActive
 bcs Own
 farcall VvPrepareDispatch,jmp
Own:
 lda #$fc
 sta InvPickup,x
 lda #$ff
 sta InvPickupOwner,x
 lda PowerUpType,x
 cmp #2
 bcs Done
 phx
 jsr M3Ensure
 plx
 lda M3Form
 beq Small
 lda PseudoRandomBitReg+2
Reduce:cmp #5
 bcc Form
 sec
 sbc #5
 bcs Reduce
Form:clc
 adc #2
 bne Stamp
Small:lda #1
Stamp:ora #$d0
 sta InvPickup,x
 lda #17
 sta InvPickupOwner,x
 lda #0
 sta InvRisePhase,x
 lda #1
 sta PowerUpType,x
Done:rts
.endproc
.proc M3PrivatePickup
 jsr M3IsActive
 bcs Own
 farcall TnPrivatePickupDispatch,jmp
Own:
 lda Enemy_ID,x
 cmp #PowerUpObject
 bne No
 lda InvPickupOwner,x
 cmp #17
 bne No
 lda InvPickup,x
 cmp #$d1
 bcc No
 cmp #$d7
 bcs No
 sec
 rts
No:clc
 rts
.endproc
.proc M3RisePickup
 jsr M3IsActive
 bcs Own
 farcall TnRisePickupDispatch,jmp
Own:
 jsr M3PrivatePickup
 bcc Done
 lda TimerControl
 bne Handled
 inc InvRisePhase,x
 lda InvRisePhase,x
 cmp #3
 bcc Handled
 lda #0
 sta InvRisePhase,x
 dec Enemy_Y_Position,x
 inc Enemy_State,x
 lda Enemy_State,x
 cmp #17
 bcc Handled
 lda #$80
 sta Enemy_State,x
 lda #0
 sta Enemy_SprAttrib,x
 sta Enemy_X_Speed,x
 lda InvPickup,x
 cmp #$d1
 bne Handled
 lda #0
 sta PowerUpType,x
 lda #$10
 sta Enemy_X_Speed,x
 lda #1
 sta Enemy_MovingDir,x
Handled:sec
Done:rts
.endproc
.proc M3PickupCollision
 jsr M3IsActive
 bcs Own
 farcall TnPickupCollisionDispatch,jmp
Own:
 jsr M3PrivatePickup
 bcc Allowed
 lda Enemy_State,x
 bmi Allowed
 ; A source-style reward cannot collect while inside its question block.
 ; SMB delivery uses a48-tick rise and becomes collectible when clear.
 bpl Hidden
Allowed:sec
 rts
Hidden:clc
 rts
.endproc
.proc M3CollectPickup
 jsr M3IsActive
 bcs Own
 farcall VvPickupDispatch,jmp
Own:
 lda PowerUpType,x
 cmp #2
 jcs LegacyStar
 lda InvPickupOwner,x
 cmp #17
 jne Done
 lda InvPickup,x
 sec
 sbc #$d0
 cmp #1
 jcc Done
 cmp #7
 jcs Done
 sta M3Scratch
 phx
 jsr EraseEnemyObject
 plx
 lda M3Form
 beq Grow
 lda M3Scratch
 cmp #2
 beq NoPoof
 lda #24
 sta M3Poof
 bne Apply
Grow:lda #47
 sta M3Growth
NoPoof:
Apply:jsr M3ClearSuitState
 lda M3Scratch
 sta M3Form
 lda #0
 sta M3PaletteValid
 lda #Sfx_PowerUpGrab
 sta Square2SoundQueue
 lda #6
 jsr SetupFloateyNumber
Done:rts
LegacyStar:farcall MarioSourcePowerupCollision,jmp
.endproc
.popseg
