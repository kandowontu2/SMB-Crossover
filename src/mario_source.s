; Source Mario profiles. Only SelectedCharacter=0 dispatches here; Luigi keeps
; the explicitly requested native SMB engine. Shared guest state is exclusively
; owned by the selected avatar, so these aliases add no RAM or relocation.
MarioSourceActive := XgIndex
MarioRunCap := XgDash
MarioJustCrouched := XgJumpUsed
MarioJumpRise := XgRise
MarioJumpEnd := XgJumpStart
MarioJumpEndHigh := XgJumpHeight
MarioJumpMin := XgWall
MarioJumpMinHigh := XgWallContact
MarioJumpFraction := XgCeiling       ; Two bytes: XgCeiling/XgWallLock.

.pushseg
.segment "PLAYER"
.proc MarioSourceMovement
  jsr MarioSourceShotTick
  lda MarioSourceActive
  bne Sync
  inc MarioSourceActive
  lda #0
  sta MarioRunCap
  sta MarioJustCrouched
  sta MarioJumpRise
  sta MmJumpReleased
  sta MmFrictionYActive
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
  sta MarioJumpRise
  sta CrouchingFlag
  lda PlayerSize
  bne Input
  lda SavedJoypadBits
  and #Down_Dir
  sta CrouchingFlag
  beq Input
  lda #1
  sta MarioJustCrouched
  bne Input
Air:
  lda Player_Y_Speed
  cmp MmVY+2
  beq Input
  sta MmVY+2                    ; Actual native ceiling, stomp or spring contact.
  lda #0
  sta MmVY
  sta MmVY+1
  sta MarioJumpRise
Input:
  lda A_B_Buttons
  eor PreviousA_B_Buttons
  and A_B_Buttons
  and #A_Button
  beq Release
  lda Player_State
  bne Release
  farcall MarioSourceJump
Release:
  lda A_B_Buttons
  and #A_Button
  bne Rise
  lda PreviousA_B_Buttons
  and #A_Button
  beq Rise
  lda #1
  sta MmJumpReleased
  lda CrossoverBehaviorVersion
  bne Rise
  sta MarioJumpRise             ; Easy releases friction immediately, no min rise.
  lda #1
  sta MmFrictionYActive
Rise:
  farcall MarioSourceRise
  lda CrouchingFlag
  jne Coast
  lda SavedJoypadBits
  and #3
  cmp #1
  beq Right
  cmp #2
  jeq Left
  cmp #3
  beq Both
  lda Player_State
  jne Integrate                 ; No-input airborne velocity is retained.
Coast:
  lda #0
  sta MarioWaterFrictionKind
  farcall MarioSourceFriction
  jmp Cap
Both:
  lda CrossoverBehaviorVersion
  jeq Coast                     ; Easy's both-direction branch precedes skid.
  lda Player_State
  jne Coast
  farcall MarioSourceMagnitude
  lda MmMul+2
  jne Skid
  lda MmMul+1
  cmp #$55                      ; Source SKID_THRESHOLD=40 Flash px/s.
  jcs Skid
  bcc Coast
Right:
  lda Player_CollisionBits
  and #1
  jeq Cap
  lda #1
  ldx MarioJustCrouched
  beq :+
    dec MarioJustCrouched
    jmp Integrate               ; Source skips first directional move after crouch.
  :
  ldx Player_State
  bne :+
    sta PlayerFacingDir
  :
  jsr Acceleration
  clc
  lda MmVX
  adc MarioWaterAcceleration
  sta MmVX
  lda MmVX+1
  adc MarioWaterAcceleration+1
  sta MmVX+1
  lda MmVX+2
  adc #0
  sta MmVX+2
  bmi GroundSkid
  jmp Cap
Left:
  lda Player_CollisionBits
  and #2
  jeq Cap
  lda #2
  ldx MarioJustCrouched
  beq :+
    dec MarioJustCrouched
    jmp Integrate
  :
  ldx Player_State
  bne :+
    sta PlayerFacingDir
  :
  jsr Acceleration
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
  bmi Cap
GroundSkid:
  lda Player_State
  bne Cap
Skid:
  lda #1
  sta MarioWaterFrictionKind
  farcall MarioSourceFriction
Cap:
  farcall MarioSourceClamp
Integrate:
  farcall MegaManMovement::Horizontal
  farcall MarioSourceAnimation
  rts
Acceleration:
  lda #$39                      ; Easy400/7200, Q0.16 rounded once.
  ldy #$0e
  ldx CrossoverBehaviorVersion
  beq :+
    lda #$72                    ; Hard350/7200.
    ldy #$0c
  :
  sta MarioWaterAcceleration
  sty MarioWaterAcceleration+1
  rts
.endproc

.proc MarioSourceShotTick
  lda MegaManShotPose
  beq Done
  cmp #6
  bcc Count
  lda #5                        ; Native emission latch8 becomes five updates.
  sta MegaManShotPose
Count:
  dec MegaManShotPose
Done:
  rts
.endproc

.segment "INVENTORY"
.proc MarioSourceMagnitude
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
  lda MmSign
  bpl :+
    farcall MegaManMovement::NegateX
  :
  rts
.endproc

.proc MarioSourceFriction
  jsr MarioSourceMagnitude
  lda MarioWaterFrictionKind
  beq Coast
  cmp #1
  bne Run
  farcall SamusFrictionY        ; 0.0001^(1/60), shared exact multiplier.
  jmp Apply
Run:
  farcall LuigiRunFrictionX     ; 0.02^(1/60), not Luigi movement dispatch.
  jmp Apply
Coast:
  farcall MarioWaterCoast       ; 0.05^(1/60).
Apply:
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
  cmp #$55
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

.proc MarioSourceClamp
  jsr MarioSourceMagnitude
  jsr LoadWalk
  jmp Buttons
LoadWalk:
  lda #0
  sta XgSpeed
  lda #$40                      ; Easy150/120=1.25 NES px/update.
  ldy CrossoverBehaviorVersion
  beq :+
    lda #$55
    sta XgSpeed
    lda #$75                    ; Hard175/120=1.458333.
  :
  sta XgSpeed+1
  lda #1
  sta XgSpeed+2
  rts
Buttons:
  lda SavedJoypadBits
  and #B_Button
  beq ReleasedRun
  lda SwimmingFlag
  ora CrouchingFlag
  bne Ready
  lda #1
  sta MarioRunCap
  bne Running
ReleasedRun:
  lda MarioRunCap
  beq Ready
  ; Source clamps against the previous vxMax before run-to-walk friction.
  ; Ordinary acceleration past the walk cap is not a released run.
  jsr LoadRun
  jsr ApplyLimit
  jsr LoadWalk
  jsr Compare
  bcc OverWalk
  lda #0
  sta MarioRunCap
  beq Ready
OverWalk:
  lda SavedJoypadBits
  and #3
  beq Running
  lda #2
  sta MarioWaterFrictionKind
  jsr MarioSourceFriction
  jsr MarioSourceMagnitude
Running:
  lda MarioRunCap
  beq Ready
  jsr LoadRun
  jmp Ready
LoadRun:
  lda #0
  sta XgSpeed
  lda #$80
  sta XgSpeed+1
  lda #2
  sta XgSpeed+2
  rts
Ready:
  lda MmUnderwater
  beq Limit
  lda Player_State
  bne Limit
  lda #0
  sta XgSpeed
  sta XgSpeed+2
  lda #$c0                      ; Shared source ground-water max90/120.
  sta XgSpeed+1
Limit:
  jsr ApplyLimit
  rts
ApplyLimit:
  jsr Compare
  bcs Done
  lda XgSpeed
  sta MmVX
  sta MmMul
  lda XgSpeed+1
  sta MmVX+1
  sta MmMul+1
  lda XgSpeed+2
  sta MmVX+2
  sta MmMul+2
  lda MmSign
  bpl Done
  farcall MegaManMovement::NegateX
Done:
  rts
Compare:
  lda XgSpeed+2
  cmp MmMul+2
  bne Compared
  lda XgSpeed+1
  cmp MmMul+1
  bne Compared
  lda XgSpeed
  cmp MmMul
Compared:
  rts
.endproc

.proc MarioSourceWaterAcceleration
  ; Luigi retains its existing water profile. Hard Mario uses the source
  ; low-speed700 acceleration only while actually pulled sideways.
  lda #$39
  ldy #$0e
  ldx MarioWaterPulled
  beq Base
  lda #$72
  ldy #$14
Base:
  ldx SelectedCharacter
  bne Store
  ldx CrossoverBehaviorVersion
  beq Store
  ldx MarioWaterPulled
  bne Pulled
  lda #$72
  ldy #$0c
  bne Store
Pulled:
  jsr MarioSourceMagnitude
  lda MmMul+2
  bne StandardPull
  lda MmMul+1
  cmp #$80
  bcs StandardPull
  ora MmMul
  beq StandardPull
  lda #$e4                      ; 700/7200.
  ldy #$18
  bne Store
StandardPull:
  lda #$72
  ldy #$14
Store:
  sta MarioWaterAcceleration
  sty MarioWaterAcceleration+1
  rts
.endproc

.proc MarioSourceCrossSmallGap
  lda Player_State
  cmp #2
  jne Done
  lda Player_Y_HighPos
  cmp #1
  jne Done
  lda Player_Y_Position
  and #15
  jne Done
  lda MmVY
  ora MmVY+1
  ora MmVY+2
  ora MmYFraction
  ora MmYFraction+1
  jne Done
  lda Player_Y_Position
  cmp #208
  jcs Done
  sta MmProbeY
  clc
  lda Player_X_Position
  adc #8
  sta MmProbeX
  lda Player_PageLoc
  adc #0
  sta MmProbePage
  bne Left
  lda MmProbeX
  cmp #32                       ; Source excludes a left support grid <= zero.
  jcc Done
Left:
  sec
  lda MmProbeX
  sbc #16
  sta MmProbeX
  bcs :+
    dec MmProbePage
  :
  jsr MegaManSlideSmallGap::Tile
  jeq Done
  clc
  lda MmProbeX
  adc #32
  sta MmProbeX
  bcc :+
    inc MmProbePage
  :
  jsr MegaManSlideSmallGap::Tile
  jeq Done
  lda #0
  sta Player_State
  sta Player_Y_Speed
Done:
  rts
.endproc
.proc MarioSourceGapEligible
  jsr MarioSourceMagnitude
  lda MmMul+2
  cmp #1
  bcc No
  bne Yes
  lda MmMul+1
  cmp #$d5
  bcc No
  bne Yes
  lda MmMul
  cmp #$56                      ; Source fastest run timer requires >220.
  bcc No
Yes:
  sec
  rts
No:
  clc
  rts
.endproc

.proc MarioSourceWaterClamp
  lda SelectedCharacter
  bne Luigi
  ; The old water routine calls ClampX with a positive magnitude. Preserve
  ; its calling convention while applying the selected Mario walk cap.
  lda #0
  sta MarioRunCap
  jsr MarioSourceClamp
  rts
Luigi:
  farcall MegaManMovement::ClampX
  rts
.endproc

.proc MarioSourceAnimation
  jsr MarioSourceMagnitude
  ldx #0
Next:
  lda ThresholdLo,x
  sta XgSpeed
  lda ThresholdMid,x
  cpx #2
  bne StoreMid
  ldy CrossoverBehaviorVersion
  beq StoreMid
  lda #$60                      ; Hard run-animation threshold165/120.
StoreMid:
  sta XgSpeed+1
  lda ThresholdHigh,x
  sta XgSpeed+2
  jsr MarioSourceClamp::Compare
  bcs Selected
  inx
  cpx #4
  bcc Next
Selected:
  lda Timers,x                  ; Native frame countdown is interval minus1.
  cpx #2
  bne Store
  lda PlayerAnimTimer
  bne Moderate
  lda MarioWaterAnimPhase
  eor #1
  sta MarioWaterAnimPhase
Moderate:
  lda MarioWaterAnimPhase
  and #1
  clc
  adc #3                        ; Alternating4/5 updates=75ms source timer.
Store:
  sta PlayerAnimTimerSet
  rts
ThresholdLo: .byte $ab,$55,$00,$55
ThresholdMid: .byte $6a,$d5,$40,$d5
ThresholdHigh: .byte 0,0,1,1
Timers: .byte 6,5,3,2,1
.endproc

.proc MarioSourceBodyImmunity
  ; MarioBase.hitEnemy returns before even a star hit in this one case.
  lda SelectedCharacter
  bne No
  lda Enemy_ID,x
  cmp #Bloober
  bne No
  lda Player_State
  bne No
  lda Player_Y_HighPos
  cmp #1
  bne No
  lda Player_Y_Position
  cmp #176                      ; Source feet ny=416, canonical NES Y+32.
  bne No
  sec
  rts
No:
  clc
  rts
.endproc

.proc MarioSourceBounce
  lda #0
  sta MmVY
  sta MarioJumpRise
  sta MmFrictionYActive
  lda #$80
  sta MmVY+1
  lda #$fd                      ; Both Character sources bounce300.
  sta MmVY+2
  sta Player_Y_Speed
  rts
.endproc

.proc MarioSourceSpring
  lda JumpspringForce
  cmp #$f4
  beq Boost
  lda #$ab
  ldy #$aa
  ldx #$fc                      ; Both Mario spring profiles400/950.
  bne Store
Boost:
  lda #$55
  ldy #$15
  ldx #$f8
Store:
  sta MmVY
  sty MmVY+1
  stx MmVY+2
  stx Player_Y_Speed
  lda #0
  sta MarioJumpRise
  sta MmJumpReleased
  sta MmFrictionYActive
  lda #1
  sta Player_State
  rts
.endproc

.proc MarioSourceFireballBrick
  pha                           ; Incoming A is the actual bottom-probe tile.
  lda SelectedCharacter
  bne Disabled
  lda CrossoverBehaviorVersion
  beq Disabled
  pla
  cmp #$22
  beq Brick
  cmp #$51
  beq Brick
  cmp #$52
  beq Brick
  cmp #$88
  beq Brick
  cmp #$55
  bcc Solid
  cmp #$5f
  bcs Solid
Brick:
  sec
  rts
Disabled:
  pla
Solid:
  clc
  rts
.endproc

.proc MarioSourceInjuryStart
  lda PlayerStatus
  sta GuestPowerupOld
  sta GuestPowerupDisplay
  lda #0
  sta GuestPowerupTarget         ; Both source Mario profiles lose all powers.
  sta GuestInvulTicks
  sta GuestHurtTicks
  sta GuestFlickerPhase
  lda #$80                      ; Distinct Mario token, generic150-update clock.
  sta GuestHurtKind
  lda #1
  sta GuestLegacyHurt
  sta GuestHurtVisible
  sta InjuryTimer
  lda #Sfx_PipeDown_Injury
  sta Square1SoundQueue
  jmp MarioSourceBeginFreeze
.endproc

.proc MarioSourceBeginPowerup
  lda PlayerStatus
  cmp #2
  bcs Done
  sta GuestPowerupOld
  sta GuestPowerupDisplay
  lda CrossoverBehaviorVersion
  beq Easy
  lda PowerUpType,x
  clc
  adc #1                        ; Hard independent mushroom/flower upgrades.
  cmp GuestPowerupOld
  beq Done
  bcc Done
  bcs Target
Easy:
  lda GuestPowerupOld
  clc
  adc #1                        ; Old source advances one tier per pickup.
Target:
  sta GuestPowerupTarget
  lda #0
  sta GuestLegacyHurt
  jmp MarioSourceBeginFreeze
Done:
  rts
.endproc

.proc MarioSourceBeginFreeze
  lda ObjectMetasprite
  sta GuestPowerupPose
  lda #0
  sta GuestPowerupAge
  sta PlayerChangeSizeFlag
  sta MegaManShotPose
  sta FireballThrowingTimer
  lda #1
  sta GuestPowerupActive
  lda #$ff
  sta TimerControl
  lda #9
  sta GameEngineSubroutine
  rts
.endproc

.proc MarioSourcePowerupUpdate
  lda GuestPowerupActive
  jeq Done
  inc GuestPowerupAge
  lda GuestPowerupAge
  cmp #60
  jcs Finish
  lda GuestLegacyHurt
  beq Opaque
  lda GuestFlickerPhase
  clc
  adc #13
  cmp #20
  bcc Hidden
  sbc #20
  ldx #1
  bne Alpha
Hidden:
  ldx #0
Alpha:
  sta GuestFlickerPhase
  stx GuestHurtVisible
Opaque:
  lda #$ff
  sta TimerControl
  lda GuestPowerupOld
  sta GuestPowerupDisplay
  lda GuestPowerupAge
  ldy GuestLegacyHurt
  beq Growth
  ; Moderate75ms damage frame cadence: alternate4/5updates.
  asl
  ldy #9
  bne DivideSetup
Growth:
  ldy #3                        ; Growth uses MinFast50ms.
DivideSetup:
  sty GuestPowerupColor
  ldx #0
Divide:
  cmp GuestPowerupColor
  bcc Phase
  sec
  sbc GuestPowerupColor
  inx
  bne Divide
Phase:
  txa
  and #1
  beq Display
  lda GuestPowerupTarget
  sta GuestPowerupDisplay
Display:
  lda GuestPowerupDisplay
  sta PlayerStatus
  beq Small
  lda #0
  beq Size
Small:
  lda #1
Size:
  sta PlayerSize
  farcall GetPlayerColors
Done:
  rts
Finish:
  lda GuestPowerupTarget
  sta GuestPowerupDisplay
  sta PlayerStatus
  beq FinishSmall
  lda #0
  beq FinishSize
FinishSmall:
  lda #1
FinishSize:
  sta PlayerSize
  lda #0
  sta GuestPowerupActive
  sta TimerControl
  sta PlayerChangeSizeFlag
  sta MegaManShotPose
  sta FireballThrowingTimer
  lda #8
  sta GameEngineSubroutine
  farcall GetPlayerColors
  rts
.endproc

.segment "INVENTORY"
.proc MarioSourceGravity
  lda MarioJumpRise
  bne Zero
  lda #$c7                      ; Easy1400/7200.
  ldy #$31
  ldx CrossoverBehaviorVersion
  beq Done
  lda #$55                      ; Hard1500/7200.
  ldy #$35
Done:
  rts
Zero:
  lda #0
  tay
  rts
.endproc

.segment "TITLE"
MarioSourcePowerupCollision:
      jsr EraseEnemyObject    ;erase the power-up object
      lda #$06
      jsr SetupFloateyNumber  ;award 1000 points to player by default
      lda #Sfx_PowerUpGrab
      sta Square2SoundQueue   ;play the power-up sound
      lda PowerUpType,x       ;check power-up type
      cmp #$02
      bcc Shroom_Flower_PUp   ;if mushroom or fire flower, branch
      cmp #$03
      beq SetFor1Up           ;if 1-up mushroom, branch
      lda #$23                ;otherwise set star mario invincibility
      sta StarInvincibleTimer ;timer, and load the star mario music
      lda #StarPowerMusic     ;into the area music queue, then leave
      sta AreaMusicQueue
NearbyRTS:
      rts

Shroom_Flower_PUp:
.if ::ENABLE_CROSSOVER
.if ::ENABLE_MMC5_EXPANDED
      farcall RlCollectDispatch
.else
      farcall InventoryCollect
.endif
      bcc :+
        rts
      :
      lda SelectedCharacter
      bne :+
        farcall MarioSourceBeginPowerup
        rts
      :
        farcall GuestBeginPowerup
        rts
.endif
      lda PlayerStatus    ;if player status = small, branch
      beq UpToSuper
      cmp #$01            ;if player status not super, leave
      bne NearbyRTS
      ldx ObjectOffset    ;get enemy offset, not necessary
      lda #$02            ;set player status to fiery
      sta PlayerStatus
      jsr GetPlayerColors ;run sub to change colors of player
      ldx ObjectOffset    ;get enemy offset again, and again not necessary
      lda #$0c            ;set value to be used by subroutine tree (fiery)
      jmp UpToFiery       ;jump to set values accordingly

SetFor1Up:
      lda #$0b                 ;change 1000 points into 1-up instead
      sta FloateyNum_Control,x ;and then leave
      rts

UpToSuper:
       lda #$01         ;set player status to super
       sta PlayerStatus
       lda #$09         ;set value to be used by subroutine tree (super)

UpToFiery:
       ldy #$00         ;set value to be used as new player state
       jmp SetPRout     ;set values to stop certain things in motion

.proc MarioSourceJump
  farcall MarioSourceMagnitude
  ldx #0
  lda MmMul+2
  cmp #2
  bcc Class
  bne Run
  lda MmMul+1
  cmp #$80
  bcc Class
Run:
  inx
Class:
  lda CrossoverBehaviorVersion
  bne Hard
  lda EasyJumpLo,x
  sta MmVY
  lda EasyJumpMid,x
  sta MmVY+1
  lda EasyJumpHigh,x
  sta MmVY+2
  jmp Launch
Hard:
  lda HardJumpLo,x
  sta MmVY
  lda HardJumpMid,x
  sta MmVY+1
  lda HardJumpHigh,x
  sta MmVY+2
  lda #1
  sta MarioJumpRise
  sec
  lda Player_Y_Position
  sbc Height,x                  ; Source pixels are twice NES world pixels.
  sta MarioJumpEnd
  lda Player_Y_HighPos
  sbc #0
  sta MarioJumpEndHigh
  sec
  lda Player_Y_Position
  sbc #19                       ; JUMP_HEIGHT_MIN=38 Flash pixels.
  sta MarioJumpMin
  lda Player_Y_HighPos
  sbc #0
  sta MarioJumpMinHigh
  lda MmYFraction
  sta MarioJumpFraction
  lda MmYFraction+1
  sta MarioJumpFraction+1
Launch:
  lda MmVY+2
  sta Player_Y_Speed
  lda #1
  sta Player_State
  lda #0
  sta MmJumpReleased
  sta MmFrictionYActive
  lda #$20
  sta JumpSwimTimer
  lda PlayerSize
  beq Big
  lda #Sfx_SmallJump
  bne Sound
Big:
  lda #Sfx_BigJump
Sound:
  sta Square1SoundQueue
  rts
EasyJumpLo: .byte $55,$ab         ; -650/120, -700/120, rounded Q8.16.
EasyJumpMid: .byte $95,$2a
EasyJumpHigh: .byte $fa,$fa
HardJumpLo: .byte $ab,$00         ; -400/120, -420/120.
HardJumpMid: .byte $aa,$80
HardJumpHigh: .byte $fc,$fc
Height: .byte 42,56
.endproc

.proc MarioSourceRise
  lda MarioJumpRise
  beq Done
  lda MarioJumpEnd
  ldy MarioJumpEndHigh
  jsr Reached
  bcs Maximum
Minimum:
  lda MmJumpReleased
  beq Done
  lda MarioJumpMin
  ldy MarioJumpMinHigh
  jsr Reached
  bcc Done
MinReached:
  lda MarioJumpMin
  ldy MarioJumpMinHigh
  jmp Clamp
Maximum:
  lda MarioJumpEnd
  ldy MarioJumpEndHigh
Clamp:
  sta Player_Y_Position
  sty Player_Y_HighPos
  lda MarioJumpFraction
  sta MmYFraction
  lda MarioJumpFraction+1
  sta MmYFraction+1
  lda #0
  sta MarioJumpRise
  lda MmJumpReleased
  sta MmFrictionYActive
Done:
  rts
Reached:
  sta RgTempY
  sty RgTempPage
  lda Player_Y_HighPos
  cmp RgTempPage
  bcc Yes
  bne No
  lda Player_Y_Position
  cmp RgTempY
  bcc Yes
  bne No
  lda MmYFraction+1
  cmp MarioJumpFraction+1
  bcc Yes
  bne No
  lda MmYFraction
  cmp MarioJumpFraction
  bcc Yes
  beq Yes
No:
  clc
  rts
Yes:
  sec
  rts
.endproc
.popseg
