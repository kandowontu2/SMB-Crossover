; Water behavior from the pinned hosted SWF, Character.updateObj and each
; character's setStats/pressJmpBtn. Guest characters jump underwater; only
; Mario can repeatedly paddle in mid-water. Units remain signed Q8.16.
.pushseg
.segment "SRAM"
MarioWaterActive: .res 1
MarioWaterPulled: .res 1
MarioWaterFrictionKind: .res 1
WaterBoundary: .res 2
MarioWaterAcceleration: .res 2
MarioWaterAnimPhase: .res 1
.segment "PLAYER"
.proc CrossoverWaterCheck
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bne Begin
  bit BillSourceFlagSeen
  jmi Done                       ; same previous-hitpoints water epoch, second native caller.
  lda BillSourceFlagSeen
  ora #$80
  sta BillSourceFlagSeen
Begin:
  lda #0
  sta MmUnderwater
  lda SwimmingFlag
  jeq Done
  lda Player_Y_HighPos
  cmp #1
  jcc Done
  jne Submerged
  lda SelectedCharacter
  beq Mario
  cmp #CHARACTER_LUIGI
  beq Mario
  cmp #CHARACTER_BASS
  beq MegaMan
  cmp #CHARACTER_SOPHIA
  beq MegaMan
  cmp #CHARACTER_PIT
  bcs Samus
  cmp #CHARACTER_MEGAMAN
  beq MegaMan
  cmp #CHARACTER_SAMUS
  beq Samus
  cmp #CHARACTER_LINK
  beq Short
  cmp #CHARACTER_SIMON
  beq Simon
  ; Character.updateStats reads the previous completed source hTop.
  jsr BillCachedWaterHeight
  jmp Boundary
Simon:
  lda RgCrouch
  beq :+
    lda #15
    ldy #$c0
    bne Boundary
  :
  lda RgAttack                   ; The airborne whip/throw uses the tall box.
  bne SimonTall
  lda Player_State
  bne Air25
SimonTall:
  lda #30
  bne Whole
Samus:
  lda SmBall
  beq :+
    lda #13
    bne Whole
  :
  jmp SamusCrouchWaterTail
  nop
  nop
  lda Player_State
  bne Air25
  lda #31
  bne Whole
Air25:
  lda #25
  bne Whole
MegaMan:
  lda MmSliding
  bne Short
  lda Player_State
  beq :+
    lda #27
    ldy #$80
    bne Boundary
  :
  lda #24
  bne Whole
Mario:
  lda CrouchingFlag
  bne Short
  lda PlayerSize
  beq MarioTall
  lda #15                       ; Small Mario's rectangle is 31.5 Flash px.
  ldy #$c0
  bne Boundary
MarioTall:
  lda #31
  bne Whole
Short:
  lda #15
Whole:
  ldy #0
Boundary:
  sta WaterBoundary+1
  sty WaterBoundary
  lda Player_Y_Position
  cmp WaterBoundary+1
  bcc Done
  bne Submerged
  lda MmYFraction+1
  cmp WaterBoundary
  bcc Done
  bne Submerged
  lda MmYFraction
  beq Done                      ; hTop == 2 tiles is above water in the source.
Submerged:
  inc MmUnderwater
Done:
  rts
.endproc

.segment "WATER"
.proc MarioWaterMovement
  lda SelectedCharacter
  bne :+
  farcall MarioSourceShotTick
:
  lda MarioWaterActive
  bne Sync
  lda #1
  sta MarioWaterActive
  lda #0
  sta MarioWaterPulled
  sta MarioWaterAnimPhase
  sta PlayerAnimTimer
  sta PlayerAnimCtrl
  ldx #2
Init:
  sta MmVX,x
  sta MmVY,x
  dex
  bpl Init
  sta MmXFraction
  sta MmXFraction+1
  sta MmYFraction
  sta MmYFraction+1
  sta MmLastXSpeed
Sync:
  lda Player_X_Speed
  bne Vertical
  lda MmLastXSpeed
  beq Vertical
  lda #0
  sta MmVX
  sta MmVX+1
  sta MmVX+2
  sta MmXFraction
  sta MmXFraction+1
Vertical:
  lda Player_State
  bne Air
  lda #0
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  sta MmYFraction
  sta MmYFraction+1
  beq Input
Air:
  lda Player_Y_Speed
  cmp MmVY+2
  beq Input
  sta MmVY+2
  lda #0
  sta MmVY
  sta MmVY+1
Input:
  lda #0
  sta CrouchingFlag
  lda Player_State
  ora PlayerSize
  bne Water
  lda SavedJoypadBits
  and #Down_Dir
  sta CrouchingFlag
Water:
  farcall CrossoverWaterCheck
  lda A_B_Buttons
  eor PreviousA_B_Buttons
  and A_B_Buttons
  and #A_Button
  beq Release
  lda Player_State
  beq Paddle
  lda MmUnderwater
  beq Release
Paddle:
  lda #$55
  sta MmVY
  sta MmVY+1
  lda #$fe                      ; -200 / 120.
  sta MmVY+2
  lda #1
  sta Player_State
  lda #0
  sta MmJumpReleased
  sta MmFrictionYActive
  lda #$20
  sta JumpSwimTimer
  lda #Sfx_EnemyStomp
  sta Square1SoundQueue
Release:
  lda A_B_Buttons
  and #A_Button
  bne Move
  lda PreviousA_B_Buttons
  and #A_Button
  beq Move
  lda #1
  sta MmJumpReleased
  sta MmFrictionYActive
Move:
  farcall MarioSourceWaterAcceleration
  lda CrouchingFlag
  bne Coast
  lda SavedJoypadBits
  and #3
  cmp #1
  beq Right
  cmp #2
  jeq Left
  cmp #3
  bne NoBoth
  lda SelectedCharacter
  bne Coast
  lda CrossoverBehaviorVersion
  beq Coast
  lda Player_State
  bne Coast
  farcall MarioSourceMagnitude
  lda MmMul+2
  jne Skid
  lda MmMul+1
  cmp #$55
  bcc Coast
  bne BothSkid
  lda MmMul
  cmp #$56
  bcc Coast
BothSkid:
  jmp Skid
NoBoth:
  lda Player_State
  jne Integrate                 ; No-input air motion keeps its momentum.
Coast:
  lda #0
  sta MarioWaterFrictionKind
  jsr Friction
  jmp Integrate
Right:
  lda SelectedCharacter
  bne MarioRightReady
  lda Player_CollisionBits
  and #1
  jeq Integrate
MarioRightReady:
  lda #1
  sta PlayerFacingDir
  clc
  lda MmVX
  adc MarioWaterAcceleration
  sta MmVX
  lda MmVX+1
  adc MarioWaterAcceleration+1  ; 400 / 7200, or 575 while being pulled.
  sta MmVX+1
  lda MmVX+2
  adc #0
  sta MmVX+2
  bmi Skid
  farcall MarioSourceWaterClamp
  jmp Integrate
Left:
  lda SelectedCharacter
  bne MarioLeftReady
  lda Player_CollisionBits
  and #2
  jeq Integrate
MarioLeftReady:
  lda #2
  sta PlayerFacingDir
  sec
  lda MmVX
  sbc MarioWaterAcceleration
  sta MmVX
  lda MmVX+1
  sbc MarioWaterAcceleration+1
  sta MmVX+1
  lda MmVX+2
  sbc #0
  sta MmVX+2
  bpl Skid
  farcall MegaManMovement::NegateX
  farcall MarioSourceWaterClamp
  farcall MegaManMovement::NegateX
  jmp Integrate
Skid:
  lda Player_State
  bne Integrate
  lda #1
  sta MarioWaterFrictionKind
  jsr Friction
Integrate:
  lda SelectedCharacter
  bne :+
  farcall MarioSourceWaterClamp
:
  farcall MegaManMovement::Horizontal
  lda Player_State
  bne SwimAnimation
  lda SelectedCharacter
  bne NativeGroundAnimation
  farcall MarioSourceAnimation
  jmp AnimationDone
NativeGroundAnimation:
  farcall GetPlayerAnimSpeed
  jmp AnimationDone
SwimAnimation:
  lda PlayerAnimTimer
  bne AnimationDone
  lda MarioWaterAnimPhase
  eor #1
  sta MarioWaterAnimPhase
  clc
  adc #4                        ; Hosted moderate timer: 75ms = 4.5 frames.
  sta PlayerAnimTimerSet
AnimationDone:
  lda #0
  sta MarioWaterPulled
  rts
Friction:
  lda MmVX+2
  sta MmSign
  bpl :+
    farcall MegaManMovement::NegateX
  :
  lda MmVX
  sta MmMul
  lda MmVX+1
  sta MmMul+1
  lda MmVX+2
  sta MmMul+2
  lda MarioWaterFrictionKind
  bne SkidFriction
  jsr MarioWaterCoast
  jmp Applied
SkidFriction:
  farcall SamusFrictionY         ; The same 0.0001^(1/60) multiplier.
Applied:
  lda MmMul
  sta MmVX
  lda MmMul+1
  sta MmVX+1
  lda MmMul+2
  sta MmVX+2
  bne Sign
  lda MarioWaterFrictionKind
  bne Sign
  lda MmVX+1
  cmp #$55                      ; Mario's 40 Flash px/s stop threshold.
  bcc Stop
  bne Sign
  lda MmVX
  cmp #$55
  bcs Sign
Stop:
  lda #0
  sta MmVX
  sta MmVX+1
Sign:
  lda MmSign
  bpl :+
    farcall MegaManMovement::NegateX
  :
  rts
.endproc
.proc MarioWaterCurrent
  lda #1
  sta MarioWaterPulled
  sta Whirlpool_Flag
  lda Player_PageLoc
  cmp R0
  bcc Right
  bne Left
  lda Player_X_Position
  cmp R1
  bcc Right
Left:
  sec
  lda MmVX
  sbc #$39
  sta MmVX
  lda MmVX+1
  sbc #$0e                    ; PitVacuum.horzPullPwr = 400.
  sta MmVX+1
  lda MmVX+2
  sbc #0
  sta MmVX+2
  jmp Down
Right:
  clc
  lda MmVX
  adc #$39
  sta MmVX
  lda MmVX+1
  adc #$0e
  sta MmVX+1
  lda MmVX+2
  adc #0
  sta MmVX+2
Down:
  clc
  lda MmVY
  adc #$55
  sta MmVY
  lda MmVY+1
  adc #$15                    ; PitVacuum.vertPullPwr = 600.
  sta MmVY+1
  lda MmVY+2
  adc #0
  sta MmVY+2
  sta Player_Y_Speed
  rts
.endproc
MmMultiplyRoutine MarioWaterCoast, 62344
.popseg
