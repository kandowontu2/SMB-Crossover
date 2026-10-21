; Character.as takeDamageStart/End, freezeTmrDur1000/noDamageTmrDur2500.
; Tail allocation leaves every existing RAM address stable.
.pushseg
.segment "SRAM"
GuestLegacyHurt: .res 1       ;0=off,1=frozen swap,2=protection.
.segment "INVENTORY"
.proc GuestLegacyInjuryTry
  phx
  phy
  jsr InventoryLegacyClassic
  bcc Modern
  lda PlayerStatus
  sta GuestPowerupOld
  sta GuestPowerupDisplay
  lda #0
  sta GuestPowerupTarget
  sta GuestPowerupAge
  sta GuestHurtTicks
  sta GuestInvulTicks
  sta GuestFlickerPhase
  sta PlayerChangeSizeFlag
  lda SelectedCharacter
  sta GuestHurtKind
  cmp #CHARACTER_MEGAMAN
  bne Samus
  ; MegaMan.takeDamageStart releases charge without firing it.
  lda #0
  sta MmCharging
  sta MmChargeFrames
  lda #15                    ;Character.hitAnimation: takeDamage for MegaMan.
  bne Pose
Samus:
  cmp #CHARACTER_SAMUS
  bne Roster
  lda SmPose
  jmp Pose
Roster:
  cmp #CHARACTER_SIMON
  bne SavedPose
  lda #RG_POSE_HURT           ;Character.hitAnimation: takeDamage for Simon.
  bne Pose
SavedPose:
  lda RgPose
Pose:
  sta GuestPowerupPose
  lda #1
  sta GuestLegacyHurt
  sta GuestHurtVisible
  sta InjuryTimer
  sta GuestPowerupActive
  lda #$ff
  sta TimerControl
  lda #9
  sta GameEngineSubroutine
  lda #Sfx_PipeDown_Injury
  sta Square1SoundQueue
  ply
  plx
  sec
  rts
Modern:
  ply
  plx
  clc
  rts
.endproc

.proc GuestLegacyInjuryTick
  phx
  phy
  lda GameEngineSubroutine
  cmp #9
  bne Playing
  lda GuestPowerupActive
  bne Done                   ;World and protection clock freeze during swaps.
Playing:
  lda GameEngineSubroutine
  cmp #8
  bne Clear                  ;Death, area transfer and scripted life changes.
  lda GamePauseStatus
  and #1
  bne Done
  lda GuestLegacyHurt
  cmp #1
  bne Count
  lda #2
  sta GuestLegacyHurt
  lda #150                   ;2500ms, starts after the1000ms frozen shrink.
  sta GuestInvulTicks
  lda #7
  sta GuestFlickerPhase
  bne Protected
Count:
  dec GuestInvulTicks
  beq Clear
Protected:
  lda #1
  sta InjuryTimer
  ; NES opacity is binary. Approximate source alpha0.65 over20updates,
  ; using the existing LSR visual cadence without Link's Hard color cycle.
  lda GuestFlickerPhase
  clc
  adc #13
  cmp #20
  bcc Hide
  sbc #20
  sta GuestFlickerPhase
  lda #1
  bne Store
Hide:
  sta GuestFlickerPhase
  lda #0
Store:
  sta GuestHurtVisible
Done:
  ply
  plx
  rts
Clear:
  lda #0
  sta GuestLegacyHurt
  sta GuestHurtKind
  sta GuestHurtTicks
  sta GuestInvulTicks
  sta InjuryTimer
  lda #1
  sta GuestHurtVisible
  bne Done
.endproc
.popseg
