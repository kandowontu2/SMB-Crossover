; Shared host adapter for the genuine Celeste Mario kernel. Variant4 only.
; No stock-Mario integrator after an admitted CmMovement update.
.pushseg
.segment "CELESTE_MARIO_HOST"
.proc CmHostEnabled
 lda SelectedCharacter
 bne No
 lda MarioVariant
 cmp #4
 beq Yes
No:clc
 rts
Yes:sec
 rts
.endproc
.proc CmHostInvalidate
 lda #0
 sta CmMarker
 sta CmActive
 rts
.endproc
.proc CmHostFresh
 jsr CmHostInvalidate
 jsr CmHostEnabled
 bcc Done
 jmp CmHostEnsure
Done:rts
.endproc
.proc CmHostEnsure
 lda CmActive
 bne Warm
 farcall CmEnter
 lda #1
 sta CmActive
 jmp Sync
Warm:farcall CmEnsure
Sync:lda CmTier
 sta PlayerStatus
 lda #0
 sta PlayerSize
 rts
.endproc
.proc CmHostEnter
 farcall CmEnter
 lda #1
 sta CmActive
 jmp CmHostEnsure::Sync
.endproc
CmHostMarioMovement:
  lda SelectedCharacter
  bne :+
  lda MarioVariant
  cmp #4
  bne :+
  jmp CmHostMovement
:
  lda SwimmingFlag
  beq CrossoverDryMario
  lda GameEngineSubroutine
  cmp #8
  jne CmHostVanilla
  farcall MarioWaterMovement
  rts
CrossoverDryMario:
  lda #0
  sta MarioWaterActive
  lda SelectedCharacter
  bne CrossoverNativeDryMario  ; Luigi's requested native profile is unchanged.
  lda GameEngineSubroutine
  cmp #8
  bne CrossoverNativeDryMario
  lda Player_State
  cmp #3
  beq CrossoverNativeDryMario
  lda JumpspringAnimCtrl
  bne CrossoverNativeDryMario
  farcall MarioSourceMovement,jmp
CrossoverNativeDryMario:
  farcall CrossoverVanillaMovement,jmp
CmHostVanilla:
  farcall CrossoverVanillaMovement,jmp

.proc CmHostMovement
 jsr CmHostEnsure
 lda GameEngineSubroutine
 cmp #8
 bne Native
 lda GamePauseStatus
 and #1
 bne Done
 lda JumpspringAnimCtrl
 bne Native
 lda #0
 sta SmCeilingHit
 farcall CmMovement
 lda Player_Y_Speed
 sta SmTempY                 ; private until the immediate complete BG hook
 rts
Native:farcall CrossoverVanillaMovement,jmp
Done:rts
.endproc
.proc CmHostAfterBG
 ; The exact Celeste branch is called after the entire real BG owner.
 lda SmTempY
 bpl :+
 lda Player_Y_Speed
 cmp #1
 bne :+
 sta SmCeilingHit            ; native upward solid response is the sole +1 BG writer
:
 farcall CmAfterBG,jmp
.endproc
.proc CmHostGraphics
 jsr CmHostEnsure
 farcall CmGraphics
 farcall CmDraw,jmp
.endproc
.proc CmHostDraw
 farcall CmDraw,jmp
.endproc
.proc CmHostColors
 jsr CmHostEnsure
 farcall CmColors,jmp
.endproc
.proc CmHostUi
 jsr CmHostEnsure
 farcall X5NativeInventoryUiLeaf
 farcall CmUi,jmp
.endproc
.proc CmHostPickup
 jsr CmHostEnsure
 farcall CmPickup
 bcs Done
 farcall MarioSourcePowerupCollision,jmp
Done:rts
.endproc
.proc CmHostInjuryStatus
 jsr CmHostEnsure
 farcall CmInjuryStatus
 tax
 rts
.endproc
.proc CmHostMarioInjury
 jsr CmHostEnabled
 bcc Native
 farcall CmInjuryStart,jmp
Native:farcall MarioSourceInjuryStart,jmp
.endproc
.proc CmHostStomp
 php
 pha
 phx
 phy
 farcall CmBounce
 ply
 plx
 pla
 plp
 rts
.endproc
.proc CmHostSpring
 ; Import the actual native spring's signed integer impulse to CM Q8 state.
 php
 pha
 phx
 phy
 jsr CmHostEnsure
 lda JumpspringForce
 sta Player_Y_Speed
 lda #0
 sta CmVelYFrac
 sta CmPosYFrac
 sta CmDashTimer
 sta CmDashReady
 sta CmBoost
 lda #1
 sta CmState
 sta Player_State
 lda #$26
 sta CmGravity
 lda #$80
 sta CmFallForce
 lda #32
 sta CmJumpTime
 ply
 plx
 pla
 plp
 rts
.endproc
.proc CmHostDashTail
 farcall CmWeapons
 farcall ProcFireball_Bubble::ProcAirBubbles,jmp
.endproc
.proc CmHostFullPower
 jsr CmHostEnsure
 lda #2
 sta CmTier
 sta PlayerStatus
 sta CmStaminaHi
 lda #99
 sta CmStaminaLo
 lda #1
 sta CmDashStock
 lda #0
 sta CmPalette
 rts
.endproc
.proc CmHostStatusName
 php
 cmp #0
 bne RestoreP
 pha
 phx
 phy
 ldy #6
Loop:lda Name,y
 sta VRAM_Buffer1+11,y
 dey
 bpl Loop
 ply
 plx
 pla
RestoreP:plp
Done:rts
Name:.byte "CELESTE"
.endproc
.proc CmHostResolveCharacter
 php
 ldx CrossoverMenuIndex
 farcall NrMenuCharacter
 bne Publish
 ldx MarioVariant
 cpx #1
 bne Mario
 lda #CHARACTER_LUIGI
 bne Publish
Mario:lda #0
Publish:sta SelectedCharacter
 pha
 phx
 phy
 jsr CmHostEnabled
 bcc Inactive
 jsr CmHostEnsure
 jmp Restore
Inactive:lda #0
 sta CmActive
Restore:ply
 plx
 pla
 plp
 lda SelectedCharacter
 rts
.endproc
.assert * <= $c000,lderror,"Celeste host adapter exceeds audited81BB10 tail"
.popseg
