; Crossover 2.02 MegaManBase movement, in NES pixels at 60 Hz.
; Signed Q8.16 velocity and Q0.16 position remainders avoid SMB's 4.4-speed
; quantization. Gravity precedes integration, as in AnimatedObject.updateObj.
.pushseg
.segment "TITLE"
.proc MegaManMovement
  lda #0
  sta PlayerSize
  sta CrouchingFlag
  sta MmOnVine
  sta MmUnderwater
WaterReady:
  lda Player_X_Position
  sta MmOldX
  lda A_B_Buttons
  and #A_Button
  bne ReleaseReady
  lda PreviousA_B_Buttons
  and #A_Button
  beq ReleaseReady
  lda MmJumpReleased
  bne ReleaseReady
    lda #1
    sta MmJumpReleased
    sta MmFrictionYActive
ReleaseReady:
  lda Player_X_Speed
  bne :+
  lda MmLastXSpeed
  beq :+
    lda #0
    sta MmVX
    sta MmVX+1
    sta MmVX+2
  :
  lda CrossoverBehaviorVersion
  bne StepHard
  lda #0
  sta MmStepTimer
  jmp StepReady
StepHard:
  jsr StepTick
StepReady:
  lda Player_State
  bne AirSync
    lda #0
    sta MmVY
    sta MmVY+1
    sta MmVY+2
    sta MmYFraction
    sta MmYFraction+1
    beq CheckJump
AirSync:
  lda Player_Y_Speed
  cmp MmVY+2
  beq CheckJump
    sta MmVY+2
    lda #0
    sta MmVY
    sta MmVY+1
CheckJump:
  lda A_B_Buttons
  and #A_Button
  jeq CheckSlide
  and PreviousA_B_Buttons
  jne CheckSlide
  lda Player_State
  jne CheckSlide
  lda SavedJoypadBits
  and #Down_Dir
  beq Jump
    lda CrossoverBehaviorVersion
    beq StartSlide             ; Classic Down+A restarts an existing slide.
    lda MmSliding
    jne CheckSlide
    lda SsHeld
    jne CheckSlide             ; Only2.02 can carry a Super Arm brick.
StartSlide:
    lda #1
    sta MmSliding
    lda #0
    sta MmSlideTravel
    sta MmSlideTravel+1
    sta MmSlideStop
    jeq CheckSlide
Jump:
  lda MmSliding
  beq JumpReady
  lda CrossoverBehaviorVersion
  jeq CheckSlide             ; Classic cannot jump-cancel a slide.
  jsr Ceiling
  lda MmCeiling
  jne CheckSlide
  lda #0
  sta MmSliding
  sta CrouchingFlag
JumpReady:
  lda #0
  sta MmJumpReleased
  sta MmFrictionYActive
  lda #1
  sta Player_State
  lda CrossoverBehaviorVersion
  beq JumpClassic
  lda #$55
  sta MmVY
  lda #$95
  sta MmVY+1
  lda #$fa                       ; -650 /120, no double-jump skill.
  sta MmVY+2
  lda SwimmingFlag
  jeq CheckSlide
    lda #$55
    sta MmVY+1
    lda #$fb                     ; -560 /120 in a water level.
    sta MmVY+2
  jmp CheckSlide
JumpClassic:
  lda #$ab
  sta MmVY
  lda #$2a
  sta MmVY+1
  lda #$fb                     ; -580/120, classic dry.
  sta MmVY+2
  lda SwimmingFlag
  jeq CheckSlide
  lda #$6a                     ; -550/120, classic water level.
  sta MmVY+1
CheckSlide:
  lda MmSliding
  jeq Walk
  lda Player_State
  beq SlideGround
  lda CrossoverBehaviorVersion
  jne EndSlide
  lda #0
  sta MmSliding
  sta CrouchingFlag
  jmp Walk                      ; Classic retains VX on leaving an edge.
SlideGround:
  lda #4
  sta CrouchingFlag
  jsr Ceiling
  lda SavedJoypadBits
  and #3
  beq SlideEndCheck
  cmp #3
  beq SlideEndCheck
  cmp PlayerFacingDir
  beq SlideEndCheck
  ldy CrossoverBehaviorVersion
  bne TurnSlide
  ldy MmCeiling
  beq SlideEndCheck             ; Classic ignores free reversal during slide.
TurnSlide:
    sta PlayerFacingDir
    lda #1
    sta MmSlideStop
SlideEndCheck:
  lda MmCeiling
  bne Slide
  lda MmSlideStop
  bne EndSlide
  lda Player_CollisionBits
  and PlayerFacingDir
  beq EndSlide
  lda SwimmingFlag
  beq DryDistance
    lda MmSlideTravel+1
    cmp #50
    bcs EndSlide
    bcc Slide
DryDistance:
  lda MmSlideTravel+1
  cmp #63
  bcc Slide
EndSlide:
  lda #0
  sta MmVX
  sta MmVX+1
  sta MmVX+2
  sta MmSliding
  sta CrouchingFlag
  jmp Walk
Slide:
  lda #0
  sta MmVX
  lda #$80
  sta MmVX+1
  lda #2
  sta MmVX+2
  lda SwimmingFlag
  beq SlideDistance
    lda #$e0
    sta MmVX+1
    lda #1
    sta MmVX+2
SlideDistance:
  clc
  lda MmSlideTravel
  adc MmVX+1
  sta MmSlideTravel
  lda MmSlideTravel+1
  adc MmVX+2
  sta MmSlideTravel+1
  lda PlayerFacingDir
  cmp #1
  jeq Horizontal
    jsr NegateX
    jmp Horizontal
Walk:
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  bne WalkClassic
  lda CrossoverBehaviorVersion
  jne Walk202
WalkClassic:
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  bne ClassicInput
  lda SavedJoypadBits
  and #3
  cmp #1
  beq ClassicWall
  cmp #2
  bne ClassicInput
ClassicWall:
  and Player_CollisionBits
  jeq Horizontal                ; Old movePlayer ignores the blocked held side.
ClassicInput:
  lda SavedJoypadBits
  and #3
  cmp #1
  jeq Right
  cmp #2
  jeq Left
  ; Coasting uses the reference's exponential friction, including L+R.
  lda MmVX+2
  sta MmSign
  bpl :+
    jsr NegateX
  :
  lda MmVX
  sta MmMul
  lda MmVX+1
  sta MmMul+1
  lda MmVX+2
  sta MmMul+2
  farcall MmFrictionX
  lda MmMul
  sta MmVX
  lda MmMul+1
  sta MmVX+1
  lda MmMul+2
  sta MmVX+2
  bne SignX
  lda MmVX+1
  cmp #$0a                       ; snap below 5 Flash px/sec
  bcc ZeroX
  bne SignX
  lda MmVX
  cmp #$ab
  bcs SignX
ZeroX:
    lda #0
    sta MmVX
    sta MmVX+1
SignX:
  lda MmSign
  jpl Horizontal
  jsr NegateX
  jmp Horizontal
Right:
  sta PlayerFacingDir
  clc
  lda MmVX
  adc #$55
  sta MmVX
  lda MmVX+1
  adc #$15
  sta MmVX+1
  lda MmVX+2
  adc #0
  sta MmVX+2
  jmi Horizontal
  jsr ClampX
  jmp Horizontal
Left:
  sta PlayerFacingDir
  sec
  lda MmVX
  sbc #$55
  sta MmVX
  lda MmVX+1
  sbc #$15
  sta MmVX+1
  lda MmVX+2
  sbc #0
  sta MmVX+2
  jpl Horizontal
  jsr NegateX
  jsr ClampX
  jsr NegateX
Horizontal:
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  beq OldXReady                  ; Include the source's direct two-pixel step.
  lda Player_X_Position
  sta MmOldX
OldXReady:
  lda SwimmingFlag
  beq ClassicCapCheck
    farcall CrossoverWaterCheck
ClassicCapCheck:
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  bne IntegrateX
  lda CrossoverBehaviorVersion
  ora MmSliding
  bne IntegrateX
  lda MmVX+2
  bpl WaterClassicPositive
  jsr NegateX
  jsr ClampX
  jsr NegateX
  jmp IntegrateX
WaterClassicPositive:
  jsr ClampX
IntegrateX:                       ; Entry for source recoil with prepared hurt waterline.
  clc
  lda MmXFraction
  adc MmVX
  sta MmXFraction
  lda MmXFraction+1
  adc MmVX+1
  sta MmXFraction+1
  lda Player_X_Position
  adc MmVX+2
  sta Player_X_Position
  lda #0
  ldx MmVX+2
  bpl :+
    lda #$ff
  :
  adc Player_PageLoc
  sta Player_PageLoc
  lda Player_X_Position
  sec
  sbc MmOldX
  sta Player_X_Scroll
  ; Keep SMB's camera, enemy reactions and collision direction informed.
  lda MmVX+1
  lsr
  lsr
  lsr
  lsr
  sta MmTemp
  lda MmVX+2
  asl
  asl
  asl
  asl
  ora MmTemp
  sta Player_X_Speed
  sta MmLastXSpeed
  bpl :+
    eor #$ff
    clc
    adc #1
  :
  sta Player_XSpeedAbsolute
  lda Player_State
  jeq Done
  lda MmFrictionYActive
  jeq BeforeGravity
  lda MmVY+2
  bmi FrictionUpward
    lda #0
    sta MmFrictionYActive
    jeq BeforeGravity
FrictionUpward:
  jsr NegateY
  lda MmVY
  sta MmMul
  lda MmVY+1
  sta MmMul+1
  lda MmVY+2
  sta MmMul+2
  lda SelectedCharacter
  bne MarioReleaseReady
  lda CrossoverBehaviorVersion
  beq SamusFriction
  farcall MmFrictionY            ; Mario Hard FY=.000001, Easy=.0001.
  jmp AppliedFriction
MarioReleaseReady:
  cmp #CHARACTER_LUIGI            ; Keep the original ID for every other guest.
  beq SamusFriction
  cmp #CHARACTER_SAMUS
  beq SamusFriction
  cmp #CHARACTER_LINK
  beq SamusFriction
  cmp #CHARACTER_PIT
  beq SamusFriction
  cmp #CHARACTER_LUIGI
  bne :+
    farcall LuigiFrictionY
    jmp AppliedFriction
  :
  farcall MmFrictionY
  jmp AppliedFriction
SamusFriction:
  farcall SamusFrictionY
AppliedFriction:
  lda MmMul
  sta MmVY
  lda MmMul+1
  sta MmVY+1
  lda MmMul+2
  sta MmVY+2
  jsr NegateY
BeforeGravity:
  lda MmUnderwater
  beq Gravity
  lda SelectedCharacter
  beq Gravity                    ; Mario caps400 after gravity in updateLoc.
  cmp #CHARACTER_LUIGI
  bne CheckWaterCap
MarioCurrentCap:
  lda MarioWaterPulled
  bne Gravity
CheckWaterCap:
  lda MmVY+2
  bmi Gravity
  cmp #2
  bcc Gravity
  bne CapWater
  lda MmVY+1
  cmp #$15
  bcc Gravity
  bne CapWater
  lda MmVY
  cmp #$55
  bcc Gravity
CapWater:
  lda #$55
  sta MmVY
  lda #$15
  sta MmVY+1
  lda #2
  sta MmVY+2
Gravity:
  lda SelectedCharacter
  beq MarioGravity
  cmp #CHARACTER_LUIGI
  bne GuestGravity
MarioGravity:
  lda SelectedCharacter
  bne MarioRoomWaterGravity
  lda SwimmingFlag
  bne MarioRoomWaterGravity
  farcall MarioSourceGravity
  jmp AddGravity
MarioRoomWaterGravity:
  lda #$e4
  ldy #$18                       ; Mario above the surface: 700 / 7200.
  ldx MmUnderwater
  beq AddGravity
    lda #$72
    ldy #$0c                     ; Mario submerged: 350 / 7200.
    jmp AddGravity
GuestGravity:
  cmp #CHARACTER_PIT
  bcc :+
    lda XgGravity
    ldy XgGravity+1
    jmp AddGravity
  :
  cmp #CHARACTER_BILL
  bcc :+
    cmp #CHARACTER_SIMON
    beq SimonGravity
    cmp #CHARACTER_LINK
    beq LinkGravity
    lda #$8e
    ldy #$23                     ; Bill: 1000.
    ldx MmUnderwater
    beq AddGravity
BillLinkWaterGravity:
    lda #$c7
    ldy #$11                     ; Bill and Link submerged:500.
    jmp AddGravity
LinkGravity:
    lda CrossoverBehaviorVersion
    bne HardLinkGravity
    lda #$8e
    ldy #$23                    ; Easy original1000/7200.
    jmp LinkGravityWater
HardLinkGravity:
    lda #$39
    ldy #$2e                     ; Link2.02: 1300/7200.
LinkGravityWater:
    ldx MmUnderwater
    beq AddGravity
    jmp BillLinkWaterGravity
SimonGravity:
    lda #$55
    ldy #$35                     ; Simon: 1500.
    ldx MmUnderwater
    beq AddGravity
    lda #$ab
    ldy #$1a                     ; Simon submerged: 750.
    jmp AddGravity
  :
  cmp #CHARACTER_SAMUS
  bne MegaGravity
  jsr SamusSourceGravity
  jmp AddGravity
MegaGravity:
  lda CrossoverBehaviorVersion
  bne GravityHard
  lda #$1c
  ldy #$27                     ; Classic1100/7200 dry.
  jmp GravityWater
GravityHard:
  lda #$55
  ldy #$35                     ;2.02:1500/7200 dry.
GravityWater:
  ldx MmUnderwater
  beq :+
    lda #$c7
    ldy #$11
  :
AddGravity:
  clc
  adc MmVY
  sta MmVY
  tya
  adc MmVY+1
  sta MmVY+1
  lda MmVY+2
  adc #0
  sta MmVY+2
  jmi Vertical
DryFall:
  lda SelectedCharacter
  beq MarioDryFall
  cmp #CHARACTER_LUIGI
  bne GuestFall
MarioDryFall:
  lda SelectedCharacter
  bne MarioWaterFall
  lda SwimmingFlag
  bne MarioWaterFall
  lda MmVY+2
  cmp #5                        ; Both source dry profiles cap600/120.
  jcc Vertical
  lda #0
  sta MmVY
  sta MmVY+1
  lda #5
  jmp StoreFall
MarioWaterFall:
  lda MmVY+2
  cmp #3
  jcc Vertical
  bne MarioFallCap
  lda MmVY+1
  cmp #$55
  jcc Vertical
MarioFallCap:
  lda #$55
  sta MmVY
  sta MmVY+1
  lda #3
  jmp StoreFall
GuestFall:
  cmp #CHARACTER_SIMON
  jeq Vertical                  ; Simon's source never sets a fall cap.
  cmp #CHARACTER_BILL
  bcc :+
    lda MmVY+2
    cmp RgFallCap+2
    jcc Vertical
    bne ClampGuestFall
    lda MmVY+1
    cmp RgFallCap+1
    jcc Vertical
    bne ClampGuestFall
    lda MmVY
    cmp RgFallCap
    jcc Vertical
ClampGuestFall:
    lda RgFallCap
    sta MmVY
    lda RgFallCap+1
    sta MmVY+1
    lda RgFallCap+2
    jmp StoreFall
  :
  cmp #CHARACTER_SAMUS
  bne MegaFall
  lda MmVY+2
  cmp #3
  bcc Vertical
  bne SamusFallCap
  lda MmVY+1
  cmp #$c0
  bcc Vertical
SamusFallCap:
  lda #0
  sta MmVY
  lda #$c0
  sta MmVY+1
  lda #3
  jmp StoreFall
MegaFall:
  lda MmVY+2
  cmp #5
  bcc Vertical
  bne CapFall
  lda MmVY+1
  cmp #$d5
  bcc Vertical
  bne CapFall
  lda MmVY
  cmp #$55
  bcc Vertical
CapFall:
  lda #$55
  sta MmVY
  lda #$d5
  sta MmVY+1
  lda #5
StoreFall:
  sta MmVY+2
  jmp Vertical
Vertical:
  clc
  lda MmYFraction
  adc MmVY
  sta MmYFraction
  lda MmYFraction+1
  adc MmVY+1
  sta MmYFraction+1
  lda Player_Y_Position
  adc MmVY+2
  sta Player_Y_Position
  lda #0
  ldx MmVY+2
  bpl :+
    lda #$ff
  :
  adc Player_Y_HighPos
  sta Player_Y_HighPos
  lda MmVY+2
  sta Player_Y_Speed
::MegaMan202Integrated:
Done:
  lda MmVX
  ora MmVX+1
  ora MmVX+2
  bne Walking
  lda #0
  sta MmWalkTimer
  sta MmWalkFrame
  sta MmWasWalking
  rts
Walking:
  lda MmWasWalking
  bne :+
    inc MmWasWalking
    lda #5
    sta MmWalkTimer
    rts
  :
  lda MmWalkTimer
  beq AdvanceWalk
  dec MmWalkTimer
  rts
AdvanceWalk:
  lda #5
  sta MmWalkTimer
  lda MmWalkFrame
  clc
  adc #1
  and #3
  sta MmWalkFrame
  rts
ClampX:
  lda #$40
  ldy #1
  ldx SelectedCharacter
  cpx #CHARACTER_LINK
  bne :+
    lda #$75
  :
  ldx MmUnderwater
  beq :+
  ldx Player_State
  bne :+
    lda #$c0
    ldy #0
  :
  sta MmTemp
  cpy MmVX+2
  bcc CapX
  bne PhysicsReturn
  cmp MmVX+1
  bcs PhysicsReturn
CapX:
  sty MmVX+2
  sta MmVX+1
  lda #0
  sta MmVX
  rts
NegateX:
  sec
  lda #0
  sbc MmVX
  sta MmVX
  lda #0
  sbc MmVX+1
  sta MmVX+1
  lda #0
  sbc MmVX+2
  sta MmVX+2
  rts
NegateY:
  sec
  lda #0
  sbc MmVY
  sta MmVY
  lda #0
  sbc MmVY+1
  sta MmVY+1
  lda #0
  sbc MmVY+2
  sta MmVY+2
  rts
Ceiling:
  lda #0
  sta MmCeiling
  ; Above the playfield there is no ceiling tile. Do not let the native
  ; row subtraction turn a high jump into an out-of-buffer RAM probe.
  lda Player_Y_HighPos
  cmp #1
  bne PhysicsReturn
  lda Player_Y_Position
  cmp #28
  bcc PhysicsReturn
  cmp #236
  bcs PhysicsReturn
  ldy #0
  jsr BlockBufferColli_Head
  jeq PhysicsReturn
  jsr ChkForNonSolids
  jeq PhysicsReturn
  cmp #$23
  jeq PhysicsReturn
  inc MmCeiling
PhysicsReturn:
  rts
; The source press-direction callbacks move nx by four Flash pixels, then
; STEP_TMR holds ground movement for 100ms. They do not accelerate vx.
StepTick:
  lda MmStepTimer
  beq :+
    dec MmStepTimer
  :
  lda SavedJoypadBits
  and #3
  tax
  eor MmPreviousDir
  and SavedJoypadBits
  and #3
  sta MmTemp
  stx MmPreviousDir
  cpx #1
  beq StepDirection
  cpx #2
  bne PhysicsReturn
StepDirection:
  lda MmTemp
  beq PhysicsReturn
  lda Player_State
  ora MmStepTimer
  bne PhysicsReturn
  lda MmSliding
  beq :+
    jsr Ceiling
    lda MmCeiling
    bne PhysicsReturn
  :
  ldx MmPreviousDir
  cpx #2
  beq StepLeft
  lda MmVX+2
  bmi StepRight
  lda MmVX
  ora MmVX+1
  ora MmVX+2
  bne PhysicsReturn
StepRight:
  lda Player_CollisionBits
  and #1
  beq StepStart
  clc
  lda Player_X_Position
  adc #2
  sta Player_X_Position
  bcc StepStart
  inc Player_PageLoc
  jmp StepStart
StepLeft:
  lda MmVX+2
  bmi PhysicsReturn
  lda Player_CollisionBits
  and #2
  beq StepStart
  sec
  lda Player_X_Position
  sbc #2
  sta Player_X_Position
  bcs StepStart
  dec Player_PageLoc
StepStart:
  lda #6
  sta MmStepTimer
  rts
Walk202:
  lda SavedJoypadBits
  and #3
  cmp #1
  beq Direction202
  cmp #2
  bne Stop202
Direction202:
  sta PlayerFacingDir
  lda Player_State
  bne Speed202
  lda MmStepTimer
  bne Stop202
  lda SwimmingFlag
  beq Speed202
  farcall CrossoverWaterCheck          ; Use the new pose after a slide ends.
Speed202:
  lda #$60
  ldy #1                         ; WALK_SPEED=165 /120, immediate movePlayer.
  ldx MmUnderwater
  beq SpeedReady202
  ldx Player_State
  bne SpeedReady202
  lda #$c0
  ldy #0                         ; Character.vxMaxGroundWater=90 /120.
SpeedReady202:
  sta MmVX+1
  sty MmVX+2
  lda #0
  sta MmVX
  lda PlayerFacingDir
  cmp #1
  jeq Horizontal
  jsr NegateX
  jmp Horizontal
Stop202:
  lda #0
  sta MmVX
  sta MmVX+1
  sta MmVX+2
  jmp Horizontal
.endproc

; Level.checkCrossSmallGap bridges exactly one static tile while sliding.
; This runs after native BG collision, so support is restored in the same
; update instead of allowing a visible fall/jump state for an extra frame.
.segment "PLAYER"
.proc MegaManSlideSmallGap
.if ::ENABLE_MMC5_EXPANDED
  lda SelectedCharacter
  bne :+
  lda MarioVariant
  cmp #4
  bne :+
  farcall CmHostAfterBG,jmp
:
.endif
  lda CrossoverBehaviorVersion
 .if ::ENABLE_MMC5_EXPANDED
  beq Done
 .else
  jeq Done
 .endif
  lda SelectedCharacter
  beq MarioGap
  cmp #CHARACTER_MEGAMAN
 .if ::ENABLE_MMC5_EXPANDED
  bne Done
 .else
  jne Done
 .endif
  lda MmSliding
 .if ::ENABLE_MMC5_EXPANDED
  beq Done
 .else
  jeq Done
 .endif
  bne Common
MarioGap:
  farcall MarioSourceGapEligible
 .if ::ENABLE_MMC5_EXPANDED
  bcc Done
 .else
  jcc Done
 .endif
Common:
  farcall MarioSourceCrossSmallGap
Done:
  rts
.pushseg
.segment "FIXED"
Tile:
  lda MmProbePage
  and #1
  asl
  asl
  asl
  asl
  sta MmTemp
  lda MmProbeX
  lsr
  lsr
  lsr
  lsr
  ora MmTemp
  jsr GetBlockBufferAddr
  ldy MmProbeY
  lda (R6),y
  beq Empty
  jsr ChkForNonSolids
  beq Empty
  cmp #$23
  beq Empty
  lda #1
  rts
Empty:
  lda #0
  rts
.popseg
.endproc

; A 24-bit magnitude times a Q0.16 constant, with the full product retained
; until truncation. Three small byte-product tables make this inexpensive.
.segment "PLAYER"
.macro MmMultiplyRoutine Name, Factor
.proc Name
  ldx MmMul
  lda ProductMid,x
  sta MmProduct+1
  lda ProductHi,x
  sta MmProduct+2
  lda #0
  sta MmProduct+3
  sta MmProduct+4
  ldx MmMul+1
  clc
  lda MmProduct+1
  adc ProductLo,x
  lda MmProduct+2
  adc ProductMid,x
  sta MmProduct+2
  lda MmProduct+3
  adc ProductHi,x
  sta MmProduct+3
  lda #0
  adc #0
  sta MmProduct+4
  ldx MmMul+2
  clc
  lda MmProduct+2
  adc ProductLo,x
  sta MmMul
  lda MmProduct+3
  adc ProductMid,x
  sta MmMul+1
  lda MmProduct+4
  adc ProductHi,x
  sta MmMul+2
  rts
ProductLo:
  .repeat 256,I
    .byte .lobyte(I * Factor)
  .endrepeat
ProductMid:
  .repeat 256,I
    .byte .hibyte(I * Factor)
  .endrepeat
ProductHi:
  .repeat 256,I
    .byte .bankbyte(I * Factor)
  .endrepeat
.endproc
.endmacro
MmMultiplyRoutine MmFrictionX, 50097
MmMultiplyRoutine MmFrictionY, 52057
MmMultiplyRoutine SamusFrictionY, 56210
; Luigi source FX_WALK=.2, FX_RUN_CROUCH=.05, FX_RUN_TO_WALK=.02.
.segment "EXPANDED"
MmMultiplyRoutine LuigiFrictionX, 63801
MmMultiplyRoutine LuigiCrouchFrictionX, 62344
MmMultiplyRoutine LuigiRunFrictionX, 61399
MmMultiplyRoutine LuigiFrictionY, 60180
.popseg
