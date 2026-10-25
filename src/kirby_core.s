; Kirby's Adventure base toolkit. SMB-enemy copies are an authored adaptation.
.pushseg
.segment "KIRBY_CORE"
.proc KbGlobalInit
  farcall Z2GlobalInit
ClearEntry:
  lda #0
  tax
Clear:
  sta $5c00,x
  inx
  jne Clear
  lda #6
  sta KbHealth
  lda #$a7
  sta KbMarker
  rts
.endproc
.proc KbAreaReset
  lda SelectedCharacter
  cmp #CHARACTER_KIRBY
  jne Done
  lda KbFoodKind
  pha
  lda #0
  ldx #4
Clear:
  sta $5c00,x
  inx
  jne Clear
  pla
  sta KbFoodKind
  lda #$ff
  sta KbInputFrame
  sta KbPullSlot
Done:
  rts
.endproc
.proc KbEnsure
  lda KbMarker
  cmp #$a7
  jeq Life
  lda #6
  sta KbHealth
  lda #0
  sta KbCopy
  lda #$a7
  sta KbMarker
Life:
  lda KbLife
  sec
  sbc NumberofLives
  cmp #1
  jne Store
  lda #6
  sta KbHealth
  lda #0
  sta KbCopy
  jsr KbAreaReset
Store:
  lda NumberofLives
  sta KbLife
  rts
.endproc
.proc KbInputs
  lda FrameCounter
  cmp KbInputFrame
  jeq Done
  sta KbInputFrame
  lda SavedJoypadBits
  eor KbPrevious
  and SavedJoypadBits
  sta KbFresh
  lda SavedJoypadBits
  sta KbPrevious
Done:
  rts
.endproc
.proc KbMovement
  jsr KbEnsure
  jsr KbInputs
  inc KbClock
  lda #1
  sta PlayerSize
  lda KbFoodKind
  sta PlayerStatus              ; food appearance bit; neither a tier nor HP
  lda #0
  sta SmBall
  sta MmSliding
  sta CrouchingFlag
  sta RgCrouch
  sta MmFrictionYActive
  sta MmOnVine
  sta MmUnderwater
  lda SwimmingFlag
  jeq Dry
  lda #1
  sta MmUnderwater
Dry:
  lda Player_State
  cmp #3
  jne Ordinary
  farcall MegaManClimbing,jmp
Ordinary:
  lda Player_X_Position
  sta MmOldX
  lda KbHurt
  jeq NoHurt
  dec KbHurt
NoHurt:
  lda KbHeal
  jeq NoHeal
  dec KbHeal
NoHeal:
  lda KbCooldown
  jeq NoCooldown
  dec KbCooldown
NoCooldown:
  lda Player_State
  jne AirSync
  lda #0
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  sta MmYFraction
  sta MmYFraction+1
  sta KbJumpPhase
AirSync:
  lda Player_Y_Speed
  cmp MmVY+2
  jeq Input
  lda Player_State
  jeq Input
  lda Player_Y_Speed
  sta MmVY+2
  lda #0
  sta MmVY
  sta MmVY+1
  sta KbJumpPhase
Input:
  lda Player_X_Speed
  jne WallReady
  lda KbLastVx
  jeq WallReady
  jsr ZeroX
WallReady:
  lda KbHurtMove
  jeq Controlled
  dec KbHurtMove
  jmp Vertical
Controlled:
  jsr Horizontal
  lda MmUnderwater
  jeq DryInput
  lda #0
  sta KbFloat
  sta KbJumpPhase
  lda #1
  sta Player_State
  jmp Vertical
DryInput:
  lda KbVariant
  beq KirbySlideInput
  jsr MkMovementInput
  jmp NotSliding
KirbySlideInput:
  lda KbFresh
  and #A_Button|B_Button
  jeq NotSlide
  lda SavedJoypadBits
  and #Down_Dir
  jeq NotSlide
  lda Player_State
  ora KbFloat
  ora KbMouth
  jne NotSlide
  lda #5
  sta KbAction
  lda #48
  sta KbActionAge
  lda #$b3
  sta MmVX+1
  lda #2
  sta MmVX+2
  lda PlayerFacingDir
  cmp #2
  jne NotSlide
  jsr NegateX
NotSlide:
  lda KbAction
  cmp #5
  jne NotSliding
  lda #1
  sta RgCrouch
  lda #4
  sta CrouchingFlag
  lda KbActionAge
  jeq EndSlide
  lda Player_State
  jne EndSlide
  jmp Vertical
EndSlide:
  lda #0
  sta KbAction
NotSliding:
  lda KbVariant
  jne GroundJump              ; NES Meta Knight has no inflation/Up-flight path.
  lda KbFloat
  jne Floating
  lda KbMouth
  jne GroundJump
  lda SavedJoypadBits
  and #Up_Dir
  jeq GroundJump
  lda MmUnderwater
  jne GroundJump
  lda #1
  sta KbFloat
  sta Player_State
  lda #24
  sta KbFloatAge
  lda KbVariant
  beq :+
  lda #0
  sta KbFloatAge
:
  lda #Sfx_EnemyStomp
  sta Square1SoundQueue
  jmp Floating
GroundJump:
  lda Player_State
  jne VariableJump
  lda SavedJoypadBits
  and #Down_Dir
  jeq JumpCheck
  lda #1
  sta RgCrouch
  lda #4
  sta CrouchingFlag
JumpCheck:
  lda KbFresh
  and #A_Button
  jeq Vertical
  lda CrouchingFlag
  jne Vertical
  lda #0
  sta MmVY
  sta KbJumpAge
  lda #$70
  sta MmVY+1
  lda #$fc                     ; native -$0390 (Q8.8)
  sta MmVY+2
  lda #1
  sta Player_State
  sta KbJumpPhase
  lda #Sfx_SmallJump
  sta Square1SoundQueue
VariableJump:
  ; Meta's NES boss jump has a continuous ballistic arc. Keep the port's
  ; slightly stronger takeoff for SMB's64px pipes, without Kirby's23-update
  ; forced apex or any inflation/flight input.
  lda KbVariant
  beq KirbyVariableJump
  inc KbJumpAge
  bne MetaJumpClockReady
  dec KbJumpAge                ; Saturate; a long fall must not restart poses.
MetaJumpClockReady:
  jmp Vertical
KirbyVariableJump:
  lda KbJumpPhase
  jeq Vertical
  inc KbJumpAge
  cmp #2
  jeq Peak
  lda KbJumpAge
  cmp #23
  jcs StartPeak
  lda SavedJoypadBits
  and #A_Button
  jne Vertical
StartPeak:
  lda MmVY+2
  jpl EndJump
  lda #$50
  sta MmVY+1
  lda #$ff
  sta MmVY+2
  lda #2
  sta KbJumpPhase
  lda #0
  sta KbJumpAge
  jeq Vertical
Peak:
  lda KbJumpAge
  cmp #5
  jcc Vertical
  lda #0
  sta MmVY+1
  sta MmVY+2
EndJump:
  lda #0
  sta KbJumpPhase
  jeq Vertical
Floating:
  lda KbFloatAge
  jeq FloatReady
  dec KbFloatAge
FloatReady:
  lda #1
  sta Player_State
Vertical:
  farcall KbAbilityMove
  lda Player_State
  jeq Integrate
  lda MmUnderwater
  jeq DryGravity
  lda KbSwimTimer
  jeq SwimStroke
  dec KbSwimTimer
  jne WaterGravity
SwimStroke:
  lda SavedJoypadBits
  and #A_Button|Up_Dir
  jeq WaterGravity
  lda #0
  sta MmVY+1
  lda #$ff
  sta MmVY+2
  lda #15
  sta KbSwimTimer
WaterGravity:
  lda SavedJoypadBits
  and #Down_Dir
  jeq WaterDrift
  lda #16
  sta KbTemp
  lda #0
  ldy #2
  jmp Gravity
WaterDrift:
  lda #8
  sta KbTemp
  lda #$e0
  ldy #0
  jmp Gravity
DryGravity:
  lda KbVariant
  beq CopyGravity
  lda KbAction
  cmp #7
  bne CopyGravity
  lda MkCombo
  cmp #4
  bne CopyGravity
  lda MkMoveTick
  cmp #32
  jcc Integrate
CopyGravity:
  lda KbAction
  cmp #4
  jne OrdinaryGravity
  lda KbCopy
  cmp #14
  jeq Integrate
  cmp #10
  jne OrdinaryGravity
  lda SavedJoypadBits
  and #B_Button
  jne Integrate
OrdinaryGravity:
  lda KbFloat
  jeq FallGravity
  lda SavedJoypadBits
  and #Up_Dir|A_Button
  jeq HoverDown
  lda KbFloatAge
  jne HoverDown
  sec
  lda MmVY+1
  sbc #80
  sta MmVY+1
  lda MmVY+2
  sbc #0
  sta MmVY+2
  cmp #$fe
  jcc ClampFloat
  jne Integrate
  lda MmVY+1
  cmp #$b3
  jcs Integrate
ClampFloat:
  lda #$b3
  sta MmVY+1
  lda #$fe
  sta MmVY+2
  jne Integrate
HoverDown:
  lda #20
  sta KbTemp
  lda #0
  ldy #1
  jmp Gravity
FallGravity:
  lda #32
  sta KbTemp
  lda KbVariant
  beq OrdinaryFallCap
  lda #21                     ; Original Meta Knight +$0015 Q8.8 gravity.
  sta KbTemp
  lda KbAction
  cmp #7
  bne OrdinaryFallCap
  lda MkCombo
  cmp #4
  bne OrdinaryFallCap
  lda #0
  ldy #4
  jmp Gravity
OrdinaryFallCap:
  lda #$80
  ldy #2
Gravity:
  pha
  tya
  pha
  clc
  lda MmVY+1
  adc KbTemp
  sta MmVY+1
  lda MmVY+2
  adc #0
  sta MmVY+2
  pla
  sta KbTemp2
  pla
  ldx MmVY+2
  jmi Integrate
  cpx KbTemp2
  jcc Integrate
  jne Cap
  cmp MmVY+1
  jcs Integrate
Cap:
  sta MmVY+1
  lda KbTemp2
  sta MmVY+2
Integrate:
  jsr Move
  lda Player_X_Speed
  sta KbLastVx
  rts
ZeroX:
  lda #0
  sta MmVX
  sta MmVX+1
  sta MmVX+2
  rts
Horizontal:
  lda KbDashWindow
  jeq Direction
  dec KbDashWindow
Direction:
  lda KbFresh
  and #3
  jeq DirectionReady
  cmp KbDashDirection
  jne Remember
  ldx KbDashWindow
  jeq Remember
  ldx #1
  stx KbDash
Remember:
  sta KbDashDirection
  lda #12
  sta KbDashWindow
DirectionReady:
  lda KbAction
  cmp #5
  jeq Friction
  lda SavedJoypadBits
  and #3
  cmp #1
  jeq Accelerate
  cmp #2
  jeq Accelerate
  lda #0
  sta KbDash
  jeq Friction
Accelerate:
  sta PlayerFacingDir
  cmp #2
  jne Right
  jsr NegateX
Right:
  lda #32
  ldx Player_State
  jeq AccelReady
  lda #22
AccelReady:
  sta KbTemp
  lda KbFloat
  ora MmUnderwater
  jeq Add
  lda #22
  sta KbTemp
  lda MmUnderwater
  jeq Add
  lda #8
  sta KbTemp
Add:
  clc
  lda MmVX+1
  adc KbTemp
  sta MmVX+1
  lda MmVX+2
  adc #0
  sta MmVX+2
  jmi RestoreDirection
  lda #$4c
  ldy #1
  ldx KbDash
  jeq CapCheck
  lda #$cc
CapCheck:
  ldx KbFloat
  jeq WaterCap
  lda #$c0
  ldy #0
WaterCap:
  ldx MmUnderwater
  jeq Limit
  lda #$0c
  ldy #1
Limit:
  cpy MmVX+2
  jcc SetCap
  jne RestoreDirection
  cmp MmVX+1
  jcs RestoreDirection
SetCap:
  sta MmVX+1
  sty MmVX+2
RestoreDirection:
  lda PlayerFacingDir
  cmp #2
  jne Return
  jmp NegateX
Friction:
  lda MmVX+2
  pha
  jpl Positive
  jsr NegateX
Positive:
  lda #14
  ldy KbFloat
  jne SoftFriction
  ldy MmUnderwater
  jeq SlideFriction
SoftFriction:
  lda #9
SlideFriction:
  ldy KbAction
  cpy #5
  jne FrictionReady
  lda #48
FrictionReady:
  sta KbTemp
  sec
  lda MmVX+1
  sbc KbTemp
  sta MmVX+1
  lda MmVX+2
  sbc #0
  sta MmVX+2
  jpl Sign
  jsr ZeroX
Sign:
  pla
  jpl Return
  jmp NegateX
Return:
  rts
NegateX:
  sec
  lda #0
  sbc MmVX+1
  sta MmVX+1
  lda #0
  sbc MmVX+2
  sta MmVX+2
  rts
Move:
  clc
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
  lda MmVX+1
  lsr
  lsr
  lsr
  lsr
  sta KbTemp
  lda MmVX+2
  asl
  asl
  asl
  asl
  ora KbTemp
  sta Player_X_Speed
  bpl :+
  eor #$ff
  clc
  adc #1
:
  sta Player_XSpeedAbsolute
  lda Player_State
  jeq Moved
  clc
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
  cmp #1
  jcc TopClamp
  jne ReportY
  lda Player_Y_Position
  cmp #16
  jcs ReportY
TopClamp:
  lda #16
  sta Player_Y_Position
  lda #1
  sta Player_Y_HighPos
  lda #0
  sta MmVY+1
  sta MmVY+2
  sta MmYFraction+1
ReportY:
  lda MmVY+2
  sta Player_Y_Speed
Moved:
  rts
.endproc

.proc KbInjuryStatus
  lda KbHurt
  jne Alive
  lda KbHealth
  cmp #2
  jcs Alive
  lda #0
  sta KbHealth
  rts
Alive:
  lda #1
  rts
.endproc
.proc KbInjuryStart
  lda KbHurt
  jne Protected
  dec KbHealth
  lda #120
  sta KbHurt
  lda #8
  sta InjuryTimer
  lda #20
  sta KbHurtMove
  lda #0
  sta KbMouth
  sta KbFloat
  sta KbJumpPhase
  sta KbAction
  farcall KbDropCopy
  lda #0
  sta MmVY
  sta MmVX
  sta MmVY+1
  lda #$fe
  sta MmVY+2
  sta Player_Y_Speed
  lda #$80
  sta MmVX+1
  lda #1
  sta MmVX+2
  lda PlayerFacingDir
  cmp #1
  jne Recoil
  jsr KbMovement::NegateX
Recoil:
  lda #1
  sta Player_State
  lda #Sfx_Bump
  sta Square1SoundQueue
Protected:
  sec
  rts
.endproc
.proc KbHealPickup
  cmp #2
  jcs NotHealth
  lda KbHealth
  clc
  adc #2
  cmp #7
  jcc Store
  lda #6
Store:
  sta KbHealth
  lda KbFoodKind
  eor #1
  sta KbFoodKind
  lda #24
  sta KbHeal
  lda #Sfx_PowerUpGrab
  sta Square2SoundQueue
  sec
  rts
NotHealth:
  clc
  rts
.endproc
.proc KbDeathUpdate
  inc MmDeathAge
  lda #0
  sta KbCopy
  sta KbMouth
  sta KbFloat
  lda MmDeathAge
  cmp #180
  jcc Done
  lda #6
  sta GameEngineSubroutine
  lda #0
  sta TimerControl
Done:
  rts
.endproc
.proc KbPortrait
  jsr KbEnsure
  lda KbVariant
  beq :+
  ldx #8
  jsr MkSetPose
  jmp KbPublishPortrait
:
  lda #0
  sta KbPoseGroup
  tax
  jsr KbSetPose
  jmp KbPublishPortrait
.endproc
.proc KbPublishPortrait
  ; Menu/lives portraits draw directly. Ordinary gameplay publishes in
  ; KbDrawShots, after an update has actually been admitted for drawing.
  lda SmChrBank
  ldx #>KB_FIRST_CHR
  ldy #0
  farcall X5SetPhysicalChr,jmp
.endproc
.proc KbGraphics
  jsr KbEnsure
  lda KbVariant
  beq :+
  jmp MkGraphics
:
  lda Player_SprAttrib
  and #$fc
  sta Player_SprAttrib
  lda Player_Rel_XPos
  sta Player_Pos_ForScroll
  lda #0
  sta KbPoseGroup
  ldx #0
  lda GameEngineSubroutine
  cmp #11
  jne Alive
  ldx #$2c
  jmp Facing
Alive:
  lda KbMouth
  jeq Normal
  lda #1
  sta KbPoseGroup
  ldx #$18
  lda Player_State
  jne FullAir
  lda Player_X_Speed
  jeq Facing
  ldx #$20
  jsr WalkFrame
  jmp Facing
FullAir:
  ldx #$30
  jmp Facing
Normal:
  lda KbAction
  cmp #1
  jne NotInhale
  lda #1
  sta KbPoseGroup
  ldx #0
  lda KbActionAge
  jne Facing
  ldx #2
  jne Facing
NotInhale:
  cmp #2
  jne NotSpit
  lda #1
  sta KbPoseGroup
  ldx #$38
  jne Facing
NotSpit:
  cmp #3
  jne NotSwallow
  lda #1
  sta KbPoseGroup
  ldx #$0c
  lda KbClock
  and #2
  jeq Facing
  inx
  inx
  jne Facing
NotSwallow:
  cmp #6
  jne NotWaterGun
  ldx #$56
  lda #12
  sec
  sbc KbActionAge
  lsr
  lsr
  and #3
  cmp #3
  bcc :+
  lda #2
  :asl
  clc
  adc #$56
  tax
  jmp Facing
NotWaterGun:
  cmp #4
  jne NotCopy
  ldx #$38
  lda KbCopy
  cmp #4
  jne CopyAttackPose
  ldx #$2e
  jne Facing
CopyAttackPose:
  cmp #1
  jeq Facing
  cmp #9
  jeq Facing
  cmp #14
  jeq Facing
  lda #1
  sta KbPoseGroup
  ldx #$38
  jne Facing
NotCopy:
  lda KbAction
  cmp #5
  jne NotSlide
  ldx #$38
  jne Facing
NotSlide:
  lda KbFloat
  jeq NotFloat
  lda KbFloatAge
  jeq Inflated
  ldx #$4a
  cmp #19
  jcs Facing
  ldx #$4c
  cmp #13
  jcs Facing
  ldx #$4e
  cmp #7
  jcs Facing
  ldx #$50
  jne Facing
Inflated:
  ldx #$52
  lda KbClock
  and #4
  jeq Facing
  inx
  inx
  jne Facing
NotFloat:
  lda RgCrouch
  jeq NotCrouch
  ldx #$2e
  jne Facing
NotCrouch:
  lda MmUnderwater
  jeq NotWater
  lda SavedJoypadBits
  and #Up_Dir|A_Button
  jeq WaterDownCheck
  lda KbClock
  lsr
  lsr
  lsr
  and #3
  cmp #3
  bcc :+
  lda #1
  :asl
  clc
  adc #$42
  tax
  jmp Facing
WaterDownCheck:
  lda SavedJoypadBits
  and #Down_Dir
  jeq WaterHorizontal
  ldx #$48
  jmp Facing
WaterHorizontal:
  ldx #$2a
  lda Player_X_Speed
  jeq Facing
  lda KbClock
  lsr
  lsr
  lsr
  and #3
  asl
  clc
  adc #$3a
  tax
  jmp Facing
NotWater:
  lda Player_State
  jeq Ground
  ldx #$22
  lda Player_Y_Speed
  jmi Facing
  ldx #$2a
  jne Facing
Ground:
  ldx #0
  lda Player_X_Speed
  jeq Facing
  ldx #$12
  jsr WalkFrame
Facing:
  lda PlayerFacingDir
  cmp #2
  beq :+
  jmp KbSetPose
  :
  inx
  jmp KbSetPose
WalkFrame:
  lda KbClock
  cmp KbPhaseFrame
  jeq Phase
  sta KbPhaseFrame
  inc KbAnimTick
  ldy KbWalkPhase
  lda KbAnimTick
  cmp WalkDelay,y
  jcc Phase
  lda #0
  sta KbAnimTick
  iny
  tya
  and #3
  sta KbWalkPhase
Phase:
  txa
  ldy KbWalkPhase
  clc
  adc WalkOffset,y
  tax
  rts
WalkDelay:.byte 10,8,10,8
WalkOffset:.byte 0,2,4,2
.endproc
.proc KbSetPose
  BankPRGC #.bank(KbArtStart)
  stx KbPose
  lda KbPoseGroup
  jne Full
  lda KbBodyChr,x
  sta SmChrBank
  lda KbBodyLo,x
  sta SmPosePtr
  lda KbBodyHi,x
  jmp Pointer
Full:
  lda KbFullChr,x
  sta SmChrBank
  lda KbFullLo,x
  sta SmPosePtr
  lda KbFullHi,x
Pointer:
  sta SmPosePtr+1
  lda #METASPRITE_SAMUS_BODY
  sta ObjectMetasprite
  lda #1
  sta KbPoseChr
  ; Keep physical CHR coupled to completed OAM on skipped-draw catch-up.
  rts
  .byte $ea,$ea ; constant body colors initialize through GetPlayerColors/Portrait.
.endproc
.proc KbQueuePalette
  ldx VRAM_Buffer1_Offset
  cpx #$4e ; 6-byte update and terminator fit the 84-byte queue.
  jcs Done
  lda #$3f
  sta VRAM_Buffer1,x
  lda #$11
  sta VRAM_Buffer1+1,x
  lda #3
  sta VRAM_Buffer1+2,x
  lda KbVariant
  beq KirbyColors
  lda #$36                    ; Original Meta boss palette3:36/14/0F.
  sta VRAM_Buffer1+3,x
  lda #$14
  jmp CommonColors
KirbyColors:
  lda #$35                     ; Original bank21:$9CD0 palette35/25/0F.
  sta VRAM_Buffer1+3,x
  lda #$25
CommonColors:
  sta VRAM_Buffer1+4,x
  lda #$0f
  sta VRAM_Buffer1+5,x
  txa
  clc
  adc #6
  tax
  stx VRAM_Buffer1_Offset
  lda #0
  sta VRAM_Buffer1,x
Done:
  rts
.endproc
.popseg



