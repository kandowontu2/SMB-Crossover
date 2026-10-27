; Source recoil runs with the world live. The native engine10 timer remains
; available to Mario/Luigi and the custom non-2.02 guest profiles.
.pushseg
; The aligned controller reader occupies E000..E024. Its remaining resident
; padding holds this bridge without moving that reader or the FIXED segment.
.segment "OAMALIGNED"
.proc GuestGameRoutinesBridge
  lda GuestHurtKind
.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
  ora CheatInvincible
  beq Run
  farcall CheatsGameRoutinesGate,jmp
Run:
  farcall GameRoutines,jmp
  .byte $ea
.else
  beq Run
  farcall GuestInjuryGameRoutines,jmp
Run:
  farcall GameRoutines,jmp
.endif
.endproc
.segment "FIXED"
.proc GuestInjuryMovementBridge
  farcall GuestInjuryMovement, jmp
.endproc
.segment "LOWCODE"
.if ::ENABLE_MMC5_EXPANDED
.proc GuestPlayerVisible
  farcall RlVisibleDispatch,jmp
  .res 7,$ea
  .assert *-GuestPlayerVisible=25,error,"fixed original span"
.endproc
.else
.proc GuestPlayerVisible
  lda GuestHurtKind
  beq Native
  lda GuestHurtVisible
  cmp #1
  rts
Native:
  lda InjuryTimer
  beq Show
  lda FrameCounter
  lsr
  bcs Hide
Show:
  sec
  rts
Hide:
  clc
  rts
.endproc
.endif

.proc SamusSourceGravity
  ; AnimatedObject.gravityPull consumes onGround before moving the assigned
  ; damage hop. A normal grounded hit therefore skips exactly its first pull.
  lsr SmHurtFirstGround
  bcc Normal
  lda #0
  tay
  rts
Normal:
  lda #$e4
  ldy #$18                     ;700/7200, or400/7200 underwater.
  ldx MmUnderwater
  beq Done
  lda #$39
  ldy #$0e
Done:
  rts
.endproc

.segment "SAMUS"
.proc GuestLsrInjury
  lda GuestHurtKind
  cmp #CHARACTER_LINK
  beq Yes
  cmp #CHARACTER_SIMON
  beq Yes
  cmp #CHARACTER_RYU
  beq Yes
  clc
  rts
Yes:
  sec
  rts
.endproc

.proc GuestInjuryGameRoutines
  jsr GuestInjuryTick
  farcall GameRoutines
  jsr GuestLsrInjury
  bcc Done
  lda GameEngineSubroutine
  cmp #8
  bne Done
  lda GuestHurtTicks
  beq Done
  farcall LsrHurtAfterCollision
  bcc Done
  jsr GuestInjuryRecover
  ; sendPlayerBtns restores held flags, without synthesizing press events.
  lda SavedJoypadBits
  and #$c0
  sta A_B_Buttons
  lda SavedJoypadBits
  and #3
  sta Left_Right_Buttons
  lda SavedJoypadBits
  and #$0c
  sta Up_Down_Buttons
Done:
  rts
.endproc

.segment "INVENTORY"
.proc GuestInjuryStart
  jsr GuestLegacyInjuryTry
  bcc Modern
  rts
Modern:
  farcall LsrHurtPrepare
  pha                         ; Retain pre-removal friction/Jump Slash context.
  jsr InventoryHurt
  sta PlayerStatus
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  beq Source
  cmp #CHARACTER_BASS
  beq Source
  cmp #CHARACTER_SAMUS
  beq Source
  cmp #CHARACTER_LINK
  beq Source
  cmp #CHARACTER_SIMON
  beq Source
  cmp #CHARACTER_RYU
  jne Native
Source:
  sta GuestHurtKind
  lda #0
  sta GuestInvulTicks
  sta GuestFlickerPhase
  sta TimerControl
  sta PlayerChangeSizeFlag
  sta MmFrictionYActive
  sta RgAttack
  sta RgShootPose
  lda #1
  sta GuestHurtVisible
  sta InjuryTimer
  lda GuestHurtKind
  cmp #CHARACTER_SAMUS
  bne Mega
  pla
  farcall SamusHurtStart
  jmp Finish
Mega:
  farcall GuestLsrInjury
  bcs SourceLsrStart
  pla
  farcall MegaManHurtStart
  jmp Finish
SourceLsrStart:
  pla
  farcall LsrHurtStart
Finish:
  farcall GetPlayerColors
  lda GuestHurtKind
  cmp #CHARACTER_LINK
  bne StartReady
  farcall LsrHurtPalette
StartReady:
::GuestInjuryStarted:
  lda #0
  sec                         ; Skip native world freeze and shrink timeline.
  rts
Native:
  pla
  lda #0
  clc
  rts
.endproc

.segment "SAMUS"
.proc GuestInjuryTick
  lda GuestLegacyHurt
  beq Modern
  farcall GuestLegacyInjuryTick, jmp
Modern:
  phx
  phy
  lda GameEngineSubroutine
  cmp #8
  jne Cancel
  lda GamePauseStatus
  and #1
  jne Return
  lda GuestPowerupActive
  jne Return
  lda GuestHurtTicks
  beq Invulnerability
  jsr GuestLsrInjury
  bcc FixedTicks
  farcall LsrHurtTick
  bcc Locked
  jsr GuestInjuryRecover
  jmp Protected
FixedTicks:
  dec GuestHurtTicks
  bne Locked
  jsr GuestInjuryRecover
  jmp Protected
Locked:
  jsr GuestLsrInjury
  bcs Protected               ; Keep the physical latch across skipped DMAs.
  lda #0
  sta SavedJoypadBits          ; Releasing input also disables weapon edges.
  jmp Protected
Invulnerability:
  lda GuestInvulTicks
  beq Cancel
  dec GuestInvulTicks
  beq Cancel
Protected:
  lda #1
  sta InjuryTimer             ; Native InjuryTimer is an interval timer.
  jsr GuestLsrInjury
  bcs LsrVisual
  lda GuestHurtKind
  cmp #CHARACTER_SAMUS
  beq SamusFlash
  lda GuestFlickerPhase
  clc
  adc #5                      ;70ms at60Hz:21/5 updates, retained remainder.
  cmp #21
  bcc StorePhase
  sbc #21
  jmp Toggle
SamusFlash:
  lda GuestFlickerPhase
  clc
  adc #2                      ;25ms at60Hz:3/2 updates.
  cmp #3
  bcc StorePhase
  sbc #3
Toggle:
  pha
  lda GuestHurtVisible
  eor #1
  sta GuestHurtVisible
  pla
StorePhase:
  sta GuestFlickerPhase
  jmp Return
LsrVisual:
  jsr GuestLsrVisible
Return:
  ply
  plx
  rts
Cancel:
  jsr GuestLsrInjury
  bcc Clear
  farcall LsrHurtEnd
  lda #0
  sta GuestHurtKind
  sta GuestHurtTicks
  sta GuestInvulTicks
  sta InjuryTimer
  farcall GetPlayerColors       ; Remove Link's last replacement-color row.
  jmp Return
Clear:
  lda #0
  sta GuestHurtKind
  sta GuestHurtTicks
  sta GuestInvulTicks
  sta InjuryTimer
  jmp Return
.endproc

.proc GuestInjuryRecover
  jsr GuestLsrInjury
  bcc FixedProfile
  farcall LsrHurtEnd
  ; Injury disableInput suppresses press events. Resume held controls while
  ; retaining physical A/B/Select history through the last locked update.
  lda SavedJoypadBits
  sta RgPreviousButtons
  sta InvPrevious
  and #$c0
  sta PreviousA_B_Buttons
  lda #0
  sta RgWeaponButtons
  sta InvFresh
  lda GuestHurtKind
  cmp #CHARACTER_LINK
  beq Timers                  ; His color cycle continues across recovery.
  lda #7
  sta GuestFlickerPhase
  jmp Timers
FixedProfile:
  lda GuestHurtKind
  cmp #CHARACTER_SAMUS
  beq Timers
  jsr MegaManHurtEnd
Timers:
  lda #0
  sta GuestHurtTicks
::GuestInjuryRecovered:
  lda #75                     ; Separate1250ms protection starts at recoil end.
  sta GuestInvulTicks
  rts
.endproc

.proc GuestLsrVisible
  lda GuestHurtKind
  cmp #CHARACTER_LINK
  bne Other
  inc GuestFlickerPhase
  lda GuestFlickerPhase
  cmp #6
  bcc LinkPalette
  lda #0
  sta GuestFlickerPhase
LinkPalette:
  farcall LsrHurtPalette
  jmp Opaque
Other:
  lda GuestHurtTicks
  bne Opaque
  ; The NES has binary sprite opacity. Temporally approximate source0.65
  ; alpha after recoil, while keeping the actual recoil pose fully opaque.
  lda GuestFlickerPhase
  clc
  adc #13
  cmp #20
  bcc Hide
  sbc #20
  sta GuestFlickerPhase
Opaque:
  lda #1
  bne Store
Hide:
  sta GuestFlickerPhase
  lda #0
Store:
  sta GuestHurtVisible
  rts
.endproc

.proc GuestInjuryMovement
  ; NMI may refresh raw SavedJoypadBits after the pre-parser mask. Its input
  ; scan never touches these parsed action fields, so mask them after parsing
  ; as well. Recoil physics and weapons then see source disableInput reliably.
  jsr GuestLsrInjury
  bcs ParsedOnly
  lda #0
  sta SavedJoypadBits
ParsedOnly:
  lda #0
  sta A_B_Buttons
  sta Left_Right_Buttons
  sta Up_Down_Buttons
  jsr GuestLsrInjury
  bcc FixedProfile
  farcall LsrHurtMovement, jmp
FixedProfile:
  lda GuestHurtKind
  cmp #CHARACTER_SAMUS
  beq Samus
  jmp MegaManHurtMovement
Samus:
  phx
  phy
  lda ObjectOffset
  pha
  lda #0
  sta MmUnderwater
  sta CrouchingFlag
  sta SmFlip
  sta PlayerSize
  lda Player_State
  bne Air
  lda #0
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  sta MmYFraction
  sta MmYFraction+1
  beq Integrate
Air:
  lda Player_Y_Speed
  cmp MmVY+2
  beq Integrate
  sta MmVY+2
  lda #0
  sta MmVY
  sta MmVY+1
Integrate:
  farcall MegaManMovement::Horizontal
::SamusHurtIntegrated:
  pla
  sta ObjectOffset
  ply
  plx
  rts
.endproc

.proc SamusHurtStart
  lda #15                     ;250ms recoil; original vy survives airborne hits.
  sta GuestHurtTicks
  lda #0
  sta SmHurtFirstGround
  sta SmCrouch
  sta SmFlip
  sta SmShootPose
  sta CrouchingFlag
  lda Player_State
  bne Morph
  inc SmHurtFirstGround
  lda #1
  sta Player_State
  lda #$ab
  sta MmVY
  lda #$ea
  sta MmVY+1
  lda #$fd
  sta MmVY+2
  sta Player_Y_Speed
Morph:
  lda SmBall
  beq Recoil
  ; Normal difficulty removes Morph Ball before takeDamageStart. Source
  ; exitMorphBall keeps the short form if the standing rectangle is blocked.
  jsr SamusCanStand
  bne BallReady
  lda #0
  sta SmBall
  lda SmHurtFirstGround
  beq Recoil
  lda Player_Y_Position
  sec
  sbc #5                      ;BALL_DISPLACE10Flashpx on a grounded exit.
  sta Player_Y_Position
  bcs :+
    dec Player_Y_HighPos
  :
  lda #0                      ;exitMorphBall itself clears onGround.
  sta SmHurtFirstGround
  beq Recoil
BallReady:
  lda #4
  sta CrouchingFlag
Recoil:
  ldx ObjectOffset
  lda #0
  sta MmVX
  lda #$40                    ;185 input is clamped to vxMax150 by updateLoc.
  sta MmVX+1
  lda #1
  sta MmVX+2
  ; Samus recoils away from the actual attacker, independent of facing.
  lda Player_X_Position
  sec
  sbc Enemy_X_Position,x
  lda Player_PageLoc
  sbc Enemy_PageLoc,x
  bpl DirectionReady
  lda #$c0
  sta MmVX+1
  lda #$fe
  sta MmVX+2
DirectionReady:
  lda #Sfx_PipeDown_Injury
  sta Square1SoundQueue
  rts
.endproc
.popseg
