.pushseg
.segment "CD_LOGIC"
.proc CdMovementDispatch
 jsr CdIsActive
 bcc Legacy
 farcall CdMovement,jmp
Legacy:farcall KbMovementDispatch,jmp
.endproc
.macro CdDispatch Name,Own,LegacyTarget
.proc Name
 jsr CdIsActive
 bcc Legacy
 jmp Own
Legacy:farcall LegacyTarget,jmp
.endproc
.endmacro
CdDispatch CdGraphicsDispatch,CdGraphics,KbGraphicsDispatch
CdDispatch CdPortraitDispatch,CdPortrait,KbPortraitDispatch
CdDispatch CdWeaponsDispatch,CdWeapons,KbWeaponsDispatch
CdDispatch CdInjuryStartDispatch,CdInjury,KbInjuryStartDispatch
CdDispatch CdInventoryDeathDispatch,CdDeath,Z2InventoryDeathGate
.proc CdResetDispatch
 farcall KbResetDispatch
 jmp CdResetTransient
.endproc
.proc CdDeathDispatch
 jsr CdIsActive
 bcc Legacy
 inc MmDeathAge
 lda MmDeathAge
 cmp #120
 bcc Done
 lda #6
 sta GameEngineSubroutine
 lda #0
 sta TimerControl
Done:rts
Legacy:farcall KbDeathDispatch,jmp
.endproc
.proc CdInjuryStatusDispatch
 jsr CdIsActive
 bcc Legacy
 ldx #1
 txa
 rts
Legacy:farcall KbInjuryStatusDispatch,jmp
.endproc
.proc CdPickupDispatch
 jsr CdCollectPickup
 bcc Legacy
 phx
 jsr EraseEnemyObject
 plx
 lda #6
 jsr SetupFloateyNumber
 rts
Legacy:farcall KbPickupDispatch,jmp
.endproc
.proc CdBodyDispatch
 jsr CdIsActive
 bcc Legacy
 lda AreaType
 sta GuestBodyStompAllowed ; Refresh land/water eligibility for this cold family.
 lda CrossoverBehaviorVersion
 sta GuestBodyNoStomp
 phx
 phy
 jsr CdBodyContact
 ply
 plx
 rts
Legacy:farcall KbBodyDispatch,jmp
.endproc
.proc CdAdderDispatch
 cmp #14
 bne Legacy
 ldy #6
 lda RgCrouch
 beq :+
 iny
:sec
 rts
Legacy:farcall KbAdderDispatch,jmp
.endproc
.proc CdBoxDispatch
 cmp #14
 bne Legacy
 ldy #15
 lda RgCrouch
 beq :+
 iny
:rts
Legacy:farcall KbBoxDispatch,jmp
.endproc
.proc CdNewDrawDispatch
 jsr CdIsActive
 bcc Kirby
 jsr CdDrawWorld
 jmp CdHud
Kirby:farcall KbDrawShots,jmp
.endproc
.proc CdStatusNameDispatch
 pha
 jsr CdIsActive
 bcs Own
 pla
 farcall Cv3StatusNameGate,jmp
Own:
 pla
 cmp #0
 bne Done
 pha
 txa
 pha
 ldx #0
 lda CdVariant
 beq :+
 ldx #7
:stx CdScratch
 ldy #0
Loop:
 ldx CdScratch
 lda StatusNames,x
 sta VRAM_Buffer1+11,y
 inc CdScratch
 iny
 cpy #7
 bcc Loop
 pla
 tax
 pla
Done:rts
StatusNames:.byte "CHIP   ","DALE   "
.endproc
.popseg

; SMB's health-food appearance is independent of Rescue Rangers' three HP.
; Advance from the collected type, so normal blocks expose both real foods.
.pushseg
.segment "CD_LOGIC"
.proc CdNextFoodStatus
 lda PowerUpType,x
 eor #1
 sta PlayerStatus
 lda #0 ; Preserve the old collection leaf's A/N/Z; carry is set by its caller.
 rts
.endproc
.popseg
