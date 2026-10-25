; Pinned2.02 MegaManBase.takeDamageStart/End. Shared injury timing and input
; gating live in guest_injury.s; the ordinary world/collision engine keeps running.
.include "megaman_injury_art.inc"
.pushseg
.segment "SAMUS"

.proc MegaManHurtStart
  phx
  phy
  lda ObjectOffset
  pha
  lda #27                       ;450ms at60Hz; shared tick ends before update27.
  sta GuestHurtTicks
  lda #0
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  sta Player_Y_Speed
  sta MmSliding
  sta XgDash
  sta XgBassDashJump
  sta XgRise
  sta XgBassStep
  sta MmStepTimer
  sta MmPreviousDir
  sta CrouchingFlag
  sta RgCrouch
  sta MmOnVine
  sta MmCharging
  sta MmChargeFrames
  sta MmFlashTick
  sta MmFlashPhase
  sta MmLastXSpeed               ; Old walking/wall sync must not cancel new recoil.
  sta MmJumpReleased
  sta MmFrictionYActive
  sta MmSlideStop
  sta SsKick
  sta SsBodyStop
  sta MegaManShotPose
  sta RgShootPose
  sta XgBassFirePhase
  sta GuestFlickerPhase
  lda #1
  sta GuestHurtVisible
  lda Player_State
  beq Grounded
    lda #2                      ; A vine/slide/air state becomes ordinary falling.
    sta Player_State
Grounded:
  lda #$ab                      ; +80/120NESpx/update, rounded signedQ8.16.
  sta MmVX
  lda #$aa
  sta MmVX+1
  lda #0
  sta MmVX+2
  lda PlayerFacingDir
  cmp #1
  bne VelocityReady
    lda #$55                    ; Exact two's-complement of positiveQ16.
    sta MmVX
    sta MmVX+1
    lda #$ff
    sta MmVX+2
VelocityReady:
  lda #Sfx_PipeDown_Injury       ; Existing audio mapping: MM source3/Basssource22.
  ora Square1SoundQueue
  sta Square1SoundQueue
  jmp MegaManHurtRestore
.endproc

.proc MegaManHurtMovement
  phx
  phy
  lda ObjectOffset
  pha
  lda #0
  sta PlayerSize
  sta CrouchingFlag
  sta MmOnVine
  sta MmUnderwater
  sta MmFrictionYActive
  lda Player_X_Position
  sta MmOldX
  ; Collision may have stopped recoil against a wall on the preceding update.
  lda Player_X_Speed
  bne Ground
  lda MmLastXSpeed
  beq Ground
    lda #0
    sta MmVX
    sta MmVX+1
    sta MmVX+2
Ground:
  lda Player_State
  bne Water
    lda #0
    sta MmVY
    sta MmVY+1
    sta MmVY+2
    sta MmYFraction
    sta MmYFraction+1
Water:
  ; Raw2.02 takeDamage frame14 keeps stand's48Flashpx HRect even in air;
  ; jump frame15 alone uses55px. Reuse the stand boundary without changing
  ; the actual grounded state used by gravity and collision integration.
  lda Player_State
  pha
  lda #0
  sta Player_State
  farcall CrossoverWaterCheck
  pla
  sta Player_State
  ; Horizontal's common gravity dispatcher reads these for Bass, whose normal
  ; ExpandedMovement setup is intentionally bypassed during locked recoil.
  lda #$55
  sta XgGravity
  lda #$35                      ;1500/7200NESpx/update^2.
  sta XgGravity+1
  lda MmUnderwater
  beq FallCap
    lda #$c7
    sta XgGravity
    lda #$11                    ;500/7200 below the actual water hitbox boundary.
    sta XgGravity+1
FallCap:
  lda #$55
  sta RgFallCap
  lda #$d5
  sta RgFallCap+1
  lda #5                        ;700/120NESpx/update terminal speed.
  sta RgFallCap+2
  farcall MegaManMovement::IntegrateX
::MegaManHurtIntegrated:
  jmp MegaManHurtRestore
.endproc

.proc MegaManHurtEnd
.if ::ENABLE_MMC5_EXPANDED
  farcall ProtoHurtEndCore
  jmp MegaManHurtReturned
::MmRecoveryDrawGate:
  lda PlayerChrBank
  sec
  sbc #MM_HURT_BODY_BANK
  lsr
  bne RecoveryDrawReturn
  farcall ProtoRecoveryDrawCore
RecoveryDrawReturn:
  plp
Done:
  lda #0
  rts
  .assert *-MegaManHurtEnd=52,error,"Keep original recovery span/Done label"
.else
  phx
  phy
  lda ObjectOffset
  pha
  ; A hidden-body recovery frame must still restore the buster's common
  ; pattern window before any new shot. Only the hurt body lacks that pool.
  lda #MM_HURT_NORMAL_BANK
  ldx SelectedCharacter
  cpx #CHARACTER_BASS
  bne :+
    lda #BASS_HURT_NORMAL_BANK
  :
  cmp PlayerChrBank
  beq :+
    sta PlayerChrBank
    inc ReloadCHRBank
  :
  lda Player_State
  bne Done
    lda #0                      ; Source leaves airborne VX for normal input.
    sta MmVX
    sta MmVX+1
    sta MmVX+2
    sta Player_X_Speed
    sta MmLastXSpeed
Done:
  jmp MegaManHurtRestore
.endif
.endproc

; Called after ordinary world pickups/weapons. Injury glyphs share window0
; with their private hurt body, leaving the world/weapon window untouched.
; Source SimpleGraphics does not mirror splash or spark offsets with facing.
.proc MegaManHurtDraw
  lda GuestHurtTicks
.if ::ENABLE_MMC5_EXPANDED
::MmRecoveryDrawBranch:
  php
  beq MmRecoveryDrawGate
  plp
  nop
.else
  jeq Done
.endif
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  beq Mega
  cmp #CHARACTER_BASS
  jne Done
  lda #BASS_HURT_BODY_BANK
  bne Bank
Mega:
  lda #MM_HURT_BODY_BANK
Bank:
  cmp PlayerChrBank
  beq :+
    sta PlayerChrBank
    inc ReloadCHRBank
  :
  phx
  phy
  lda ObjectOffset
  pha
  BankPRGC #.bank(MmHurtFx0)
  lda Player_X_Position
  sec
  sbc ScreenLeft_X_Pos
  sta SmTempX
  lda Player_PageLoc
  sbc ScreenLeft_PageLoc
  sta SmTempPage
  lda GuestHurtVisible
  bne Sparks
  lda #0
  sta SmTemp
  lda #8
  jsr XCoordinate
  ; Both source hurt body masks are70Flashpx high. Splash is anchored at
  ; feet-height/2 = canonicalY+14.5NESpx, retaining the half-pixel phase.
  lda MmYFraction+1
  cmp #$80
  lda Player_Y_Position
  adc #14
  sta R6
  lda Player_Y_HighPos
  adc #0
  sta R7
  jsr Draw
Sparks:
  lda #27
  sec
  sbc GuestHurtTicks
  cmp #24                       ; Three130ms phases end at ceil(390ms*60)=24.
  bcs Restore
  ldx #1
  cmp #8
  bcc Phase
  inx
  cmp #16
  bcc Phase
  inx
Phase:
  stx SmTemp
  lda #0
  sta SmSlot
Loop:
  ldx SmSlot
  lda SparkX,x
  jsr XCoordinate
  ldx SmSlot
  lda Player_Y_Position
  sec
  sbc SparkY,x
  sta R6
  lda Player_Y_HighPos
  sbc #0
  sta R7
  jsr Draw
  inc SmSlot
  lda SmSlot
  cmp #3
  bcc Loop
Restore:
  pla
  sta ObjectOffset
  ply
  plx
Done:
::MegaManHurtDrawFinish:
  rts
XCoordinate:
  sta R4
  ldx #0
  cmp #$80
  bcc :+
    dex
  :
  clc
  adc SmTempX
  sta R4
  txa
  adc SmTempPage
  sta R5
  rts
Draw:
  ldx SmTemp
  lda MmHurtFxLo,x
  sta R0
  lda MmHurtFxHi,x
  sta R1
  lda #0
  sta R3
  farcall MetaspriteRenderLoop
  rts
SparkX: .byte $fc,8,20            ; Source centerX+[-12,0,+12]NESpx.
SparkY: .byte 7,10,7              ; Feet35NESpx high, plus[-4,-7,-4] head offsets.
.endproc

.proc MegaManHurtRestore
  pla
  sta ObjectOffset
  ply
  plx
::MegaManHurtReturned:
  rts
.endproc
.popseg
