; Exact ID16 admission. All legacy families retain their previous targets.
.pushseg
.segment "MIKE_CORE"
.proc JnMovementDispatch
 lda SelectedCharacter
 cmp #CHARACTER_MIKE
 jeq Own
 farcall M3MovementDispatch,jmp
Own:
 jmp JnMovement
.endproc
.proc JnGraphicsDispatch
 lda SelectedCharacter
 cmp #CHARACTER_MIKE
 jeq Own
 farcall M3GraphicsDispatch,jmp
Own:
 jmp JnGraphics
.endproc
.proc JnPortraitDispatch
 lda SelectedCharacter
 cmp #CHARACTER_MIKE
 jeq Own
 farcall M3PortraitDispatch,jmp
Own:
 jmp JnPortrait
.endproc
.proc JnWeaponsDispatch
 lda SelectedCharacter
 cmp #CHARACTER_MIKE
 jeq Own
 farcall M3WeaponsDispatch,jmp
Own:
 farcall JnWeapons,jmp
.endproc
.proc JnDeathDispatch
 lda SelectedCharacter
 cmp #CHARACTER_MIKE
 jeq Own
 farcall M3DeathDispatch,jmp
Own:
 jmp JnDeath
.endproc
.proc JnInjuryStartDispatch
 lda SelectedCharacter
 cmp #CHARACTER_MIKE
 jeq Own
 farcall M3InjuryDispatch,jmp
Own:
 jmp JnInjury
.endproc
.proc JnInjuryStatusDispatch
 lda SelectedCharacter
 cmp #CHARACTER_MIKE
 jeq Own
 farcall M3InjuryStatusDispatch,jmp
Own:
 jmp JnInjuryStatus
.endproc
.proc JnPrepareDispatch
 lda SelectedCharacter
 cmp #CHARACTER_MIKE
 jeq Own
 farcall M3PreparePickup,jmp
Own:
 farcall JnPreparePickup,jmp
.endproc
.proc JnPrivateDispatch
 lda SelectedCharacter
 cmp #CHARACTER_MIKE
 jeq Own
 farcall M3PrivatePickup,jmp
Own:
 farcall JnPrivatePickup,jmp
.endproc
.proc JnRiseDispatch
 lda SelectedCharacter
 cmp #CHARACTER_MIKE
 jeq Own
 farcall M3RisePickup,jmp
Own:
 farcall JnRisePickup,jmp
.endproc
.proc JnCollisionDispatch
 lda SelectedCharacter
 cmp #CHARACTER_MIKE
 jeq Own
 farcall M3PickupCollision,jmp
Own:
 farcall JnPickupCollision,jmp
.endproc
.proc JnDrawDispatch
 lda SelectedCharacter
 cmp #CHARACTER_MIKE
 jeq Own
 farcall M3NewDrawDispatch,jmp
Own:
 farcall JnDraw,jmp
.endproc
.proc JnResetDispatch
 farcall M3ResetDispatch
 jmp JnAreaReset
.endproc
.proc JnInventoryDeathDispatch
 lda SelectedCharacter
 cmp #CHARACTER_MIKE
 jeq Own
 farcall M3InventoryDeathDispatch,jmp
Own:jmp JnLifeLost
.endproc
.proc JnPickupDispatch
 lda SelectedCharacter
 cmp #CHARACTER_MIKE
 jne Legacy
 farcall JnCollectPickup
 jcc Legacy
 phx
 jsr EraseEnemyObject
 plx
 lda #6
 jsr SetupFloateyNumber
 rts
Legacy:farcall M3CollectPickup,jmp
.endproc
.proc JnBodyDispatch
 lda SelectedCharacter
 cmp #CHARACTER_MIKE
 jne Legacy
 lda AreaType
 sta GuestBodyStompAllowed
 lda CrossoverBehaviorVersion
 sta GuestBodyNoStomp
 clc
 rts
Legacy:farcall M3BodyDispatch,jmp
.endproc
.proc JnAdderDispatch
 cmp #CHARACTER_MIKE
 jeq Own
 farcall M3AdderDispatch,jmp
Own:ldy #0
 sec
 rts
.endproc
.proc JnBoxDispatch
 cmp #CHARACTER_MIKE
 jeq Own
 farcall M3BoxDispatch,jmp
Own:ldy #0
 rts
.endproc
.proc JnHeadDispatch
 lda SelectedCharacter
 cmp #CHARACTER_MIKE
 jeq Own
 farcall M3HeadDispatch,jmp
Own:
 jsr BlockBufferColli_Head
 pha
 beq Done
 cmp #$c2
 beq Done
 cmp #$c3
 beq Done
 ldy Player_Y_Speed
 bpl Done
 ldy R3
 lda MTileAttribute,y
 and #MTILE_SOLID|MTILE_CLIMB
 cmp #MTILE_SOLID
 bne Done
 ; The fixed grid-jump table would otherwise resume its8px rise through
 ; the temporary bumped-block cell and repeatedly trigger side separation.
 ; Separate the head at the actual tile bottom and end that jump arc.
 lda R2
 clc
 adc #48
 sec
 sbc #4
 sta Player_Y_Position
 and #15
 sta R4
 lda #0
 sta JnJump
 sta JnVY
 sta JnFallFrac
Done:
 pla
 rts
.endproc
.proc JnSpecialDrawDispatch
 lda SelectedCharacter
 cmp #CHARACTER_MIKE
 jeq Done
 farcall M3SpecialDrawGate,jmp
Done:rts
.endproc
.proc JnVisibleDispatch
 lda SelectedCharacter
 cmp #CHARACTER_MIKE
 jne Legacy
 lda JnHurt
 jeq Show
 lda FrameCounter
 and #4
 jne Hide
Show:sec
 rts
Hide:clc
 rts
Legacy:farcall M3VisibleDispatch,jmp
.endproc
.proc JnDropDispatch
 php
 pha
 txa
 pha
 tya
 pha
 lda SelectedCharacter
 cmp #CHARACTER_MIKE
 jeq Own
 pla
 tay
 pla
 tax
 pla
 plp
 farcall Cv3EnemyDropGate,jmp
Own:
 farcall JnEnemyDrop
 pla
 tay
 pla
 tax
 pla
 plp
 rts
.endproc
.proc JnGetColors
 farcall QueueMegaManFacePalette
 farcall QueueGuestWeaponPalette
 farcall X5QueueAreaBackdrop
 jmp JnPalette
.endproc
.proc JnStatusName
 pha
 lda SelectedCharacter
 cmp #CHARACTER_MIKE
 jeq Own
 pla
 farcall M3StatusNameDispatch,jmp
Own:
 pla
 cmp #0
 jne Done
 pha
 txa
 pha
 ldx #6
Copy:lda Name,x
 sta VRAM_Buffer1+11,x
 dex
 jpl Copy
 pla
 tax
 pla
Done:rts
Name:.byte "MIKE   "
.endproc
.popseg

; Publish the effective weapon name after a physical reward or HP gate change.
; This helper is appended in the same A-window bank; the original tier tail
; remains four bytes. Preserve the original caller's A/X/Y/status contract.
.pushseg
.segment "MIKE_CORE"
.proc JnPublishTier
 php
 cmp JnTier
 sta JnTier
 jeq Unchanged
 pha
 lda #1
 sta JnUiDirty
 pla
Unchanged:plp
 rts
.endproc
.popseg
