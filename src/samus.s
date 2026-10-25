; Samus profile from the pinned hosted build: docs/reference/samus.json.
.pushseg
.segment "SRAM"
SamusRamStart:
SmBall: .res 1
SmCrouch: .res 1
SmPreviousDirections: .res 1
SmShootPose: .res 1
SmAnimClock: .res 1
SmPose: .res 1
SmPosePtr: .res 2
SmChrBank: .res 1
SmJumpStartY: .res 1
SmFlip: .res 1
SmTemp: .res 1
SmTempX: .res 1
SmTempPage: .res 1
SmTempY: .res 1
SmClearance: .res 1
SmSlot: .res 1
SmHeadX: .res 1
SmHeadPage: .res 1
SmWavePolarity: .res 1
SmSfx: .res 1
SmStepTimer: .res 1
SmHurtFirstGround: .res 1
SmShotType: .res 3
SmShotX: .res 3
SmShotPage: .res 3
SmShotY: .res 3
SmShotDir: .res 3
SmShotAge: .res 3
SmShotFraction: .res 3
SmShotCenter: .res 3
SmShotPolarity: .res 3
SmShotImpact: .res 3
SmBombAge: .res 3
SmBombX: .res 3
SmBombPage: .res 3
SmBombY: .res 3
SmBombHits: .res 3
SmBombBoosted: .res 3
SmBombBlocksDone: .res 3
SmBombCell: .res 1
SmDeathPart: .res 1
SmDeathX: .res 1
SmDeathPage: .res 1
SmDeathY: .res 1
SmDeathGfx: .res 1
SamusRamEnd:

.segment "SAMUS"
.proc SamusClearState
  lda #0
  ldx #SamusRamEnd-SamusRamStart-1
Loop:
  sta SamusRamStart,x
  dex
  bpl Loop
  sta SmCeilingHit
  sta SmSourceJumped
  jmp GuestClearPowerup
.endproc
.segment "FIXED"
.proc CrossoverGraphicsBank
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  bne :+
  lda ObjectMetasprite
  cmp #METASPRITE_SAMUS_BODY
  bne :+
    BankPRGC #.bank(SsMegaTHROWRight)
    rts
  :
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  bcc :+
    jmp ExpandedGraphicsBank
  :
  cmp #CHARACTER_BILL
  bcc :+
    jmp RosterGraphicsBank
  :
  cmp #CHARACTER_SAMUS
  beq Samus
  BankPRGC #.bank(MmMM_HAIR_STANDRight)
  rts
Samus:
  BankPRGC #.bank(SmP0_STANDRight)
  rts
.endproc

.proc SamusStopAtWall
  ; SMB pushes one integer pixel out of a wall. Guest fractional walking and
  ; Mega Man's two-pixel 2.02 startup step need their actual side probe clamped
  ; to the edge, with the position remainder cleared.
  ; Scripted flagpole/castle movement relies on SMB's collision bits to
  ; start the timer tally and next-area transition.
  lda GameEngineSubroutine
  cmp #8
  beq :+
    clc
    rts
  :
  lda SelectedCharacter
  cmp #CHARACTER_LUIGI
  beq Native
  cmp #CHARACTER_MEGAMAN
  bcs Guest
Native:
  clc
  rts
Guest:
  .if ::ENABLE_MMC5_EXPANDED
    farcall LmWallGate,jmp
  .else
    farcall CrossoverSourceWallDispatch,jmp
  .endif
.endproc

.proc SamusAfterBGCollisionBridge
  ; Called only by PlayerCtrlRoutine with PLAYER mapped at A000. The rare
  ; farcall restores that bank before its original position/box subroutines.
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  bne Done
  lda SmCeilingHit               ; Ordinary walking never enters another bank.
  beq Done
  farcall SamusAfterBGCollision
  jsr RelativePlayerPosition     ; Source setHitPoints follows the separation.
  ldx #0
  jsr BoundingBoxCore
Done:
  rts
.endproc

.segment "SAMUS"
.proc CrossoverSourceWallDispatch
  cmp #CHARACTER_SOPHIA
  beq Sophia
  jmp SamusStopAtWallBanked
Sophia:
  farcall SophiaSourceWall, jmp
.endproc
.proc SamusStopAtWallBanked
  ldy R0
  cmp #CHARACTER_PIT
  bcc SideDispatch
  ; Only expanded guests inspect Ryu state; Samus retains her native path.
  cmp #CHARACTER_RYU
  bne NativeGuest
  jmp SamusRyuWallHandled
NativeGuest:
  sty XgWallContact
SideDispatch:
  cpy #1
  bne Left
  ; Retain the prior right-contact clamp for every guest. The old CPY #1
  ; cleared N before its BMI, so it did not reject away-facing contacts.
RightClamp:
  clc
  lda Player_X_Position
  adc #14
  sta SmTempX
  lda Player_PageLoc
  adc #0
  sta SmTempPage
  lda SmTempX
  and #$f0
  sec
  sbc #15
  sta Player_X_Position
  lda SmTempPage
  sbc #0
  jmp Page
Left:
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  beq LeftClamp
  lda Player_X_Speed
  cmp #1
  jpl Away
LeftClamp:
  clc
  lda Player_X_Position
  adc #1
  sta SmTempX
  lda Player_PageLoc
  adc #0
  sta SmTempPage
  lda SmTempX
  and #$f0
  ora #15
  sta Player_X_Position
  lda SmTempPage
Page:
  sta Player_PageLoc
  ; Retain the native scroll hold while a real wall contact clamps position.
  ; Otherwise each attempted step advances the camera before this correction.
  ldy #$10
  sty SideCollisionTimer
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  beq HurtWallReceipt
  lda GuestHurtTicks
  beq :+
HurtWallReceipt:
    lda R0
    eor #$ff
    and Player_CollisionBits
    sta Player_CollisionBits      ; Preserve the native contacted-side contract.
  :
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  bne OtherWallVelocity
  ; Character.groundOnSide always separates a real contact. Only velocity
  ; pointing into that wall is cancelled; zero/away motion remains intact.
  ; Use Q8.16 rather than its quantized native mirror for small velocities.
  ldy R0
  cpy #2
  beq SamusLeftVelocity
  lda MmVX+2
  bmi KeepSamusVelocity
  ora MmVX+1
  ora MmVX
  beq KeepSamusVelocity
  bne StopSamusVelocity
SamusLeftVelocity:
  lda MmVX+2
  bpl KeepSamusVelocity
StopSamusVelocity:
  lda #0
  sta MmVX
  sta MmVX+1
  sta MmVX+2
  sta Player_X_Speed
KeepSamusVelocity:
  lda #0
  sta MmXFraction
  sta MmXFraction+1
  sta Player_X_Scroll
  sec
  rts
OtherWallVelocity:
  ; Simon resumes his launch velocity when he rises clear of a wall. Keep
  ; that velocity while clamping contact, as the hosted lastVX path does.
  ; A still holds SelectedCharacter from the Samus comparison above.
  cmp #CHARACTER_SIMON
  beq ClearWallRemainder
  lda #0
  sta MmVX
  sta MmVX+1
  sta MmVX+2
ClearWallRemainder:
  lda #0
  sta MmXFraction
  sta MmXFraction+1
  sta Player_X_Speed
  sta Player_X_Scroll
Away:
  sec
  rts
  ; Keep all subsequent native SAMUS code at its original CPU addresses.
  .byte $ea
  .assert *-SamusStopAtWallBanked=215, error, "Native wall body footprint changed"
.endproc

.segment "SAMUS"
.proc SamusHeadProbe
  ; The source checks the complete horizontal head span. A single center
  ; point can miss a ceiling edge and leave the later side check pushing
  ; Samus several pixels sideways after she rises into that corner.
  lda #0
  sta SmCeilingHit
  sty SmTemp
  lda Player_X_Position
  sta SmTempX
  lda Player_PageLoc
  sta SmTempPage
  jsr Probe
  bne Restore
  lda Player_Y_Speed
  bpl Empty
  sec
  lda SmTempX
  sbc #6                         ; Head left point = original X+2.
  sta Player_X_Position
  lda SmTempPage
  sbc #0
  sta Player_PageLoc
  jsr Probe
  bne Restore
  clc
  lda SmTempX
  adc #5                         ; Head right point = original X+13.
  sta Player_X_Position
  lda SmTempPage
  adc #0
  sta Player_PageLoc
  jsr Probe
  jmp Restore
Empty:
  lda #0
Restore:
  pha
  lda SmTempX
  sta Player_X_Position
  lda SmTempPage
  sta Player_PageLoc
  pla
  beq Done
  ; Character.groundAbove separates the complete head rectangle before a
  ; side test. Native SMB's low-origin-nibble gate and brick upward bounce
  ; otherwise leave Samus inside the ceiling, where a stationary side probe
  ; can incorrectly march her across successive sixteen-pixel cells.
  bcc Done                       ; Cold classifier admits source ceilings only.
  pha
  ldy SmTemp
  clc
  lda R2                         ; Authored cell top minus the HUD height.
  adc #48                        ; Actual cell bottom.
  sec
  sbc BlockBuffer_Y_Adder,y       ; hHeight = 32 - the active head offset.
  sta SmTempY                    ; Private until the immediate post-BG hook.
  sta Player_Y_Position
  lda #1
  sta SmCeilingHit
  lda #4
  sta R4                         ; The source has no native low-nibble gap.
  lda #0
  sta MmYFraction
  sta MmYFraction+1
NoCeiling:
  ldx #0                         ; BlockBufferColli_Head's player ABI.
  pla
Done:
  rts
Probe:
  clc
  lda Player_X_Position
  adc #8
  and #$f0
  sta SmHeadX
  lda Player_PageLoc
  adc #0
  sta SmHeadPage
  ldy SmTemp
  jsr BlockBufferColli_Head
  bne Classify                   ; Empty walking/air probes do not switch banks.
  rts
Classify:
  farcall SamusHeadAxisProbe, jmp
  .res 15, $ea
  .assert *-SamusHeadProbe=184, lderror, "Original complete head footprint must remain184"
.endproc

.proc SamusAfterBGCollision
  ; SmTempY is owned only between the head probe and this immediate hook.
  ; Native brick/reward effects keep their real cell, page and animation;
  ; their Mario-specific velocity must not replace Character.groundAbove.
  lda #0
  sta SmCeilingHit
  sta MmYFraction
  sta MmYFraction+1
  lda SmTempY
  sta Player_Y_Position
  lda SmSourceJumped
  beq KeepVelocity
  lda #$55
  sta MmVY
  lda #$d5
  sta MmVY+1
  lda #0                         ; CIELING_DISPLACE = 100 / 120.
  sta MmVY+2
KeepVelocity:
  lda MmVY+2
  sta Player_Y_Speed
  lda SmBall
  bne BallSound
  lda Square1SoundQueue
  ora #Sfx_Bump
  bne Sound
BallSound:
  ; Samus.groundAbove removes only the stored ceiling cue in Morph Ball.
  lda Square1SoundQueue
  and #$ff-Sfx_Bump
Sound:
  sta Square1SoundQueue
  rts
.endproc

.proc SamusMovement
  ; The hosted step timer runs only while walking upright on the ground.
  lda Player_State
  ora SmBall
  ora SmCrouch
  bne StepReady
  lda MmVX
  ora MmVX+1
  ora MmVX+2
  beq StepReady
  inc SmStepTimer
  lda SmStepTimer
  cmp #9                         ; STEP_TMR = 150 ms.
  bcc StepReady
  lda #0
  sta SmStepTimer
  lda SmSfx
  ora #16
  sta SmSfx
StepReady:
  lda #0
  sta PlayerSize
  sta MmSliding
  sta MmOnVine
  sta MmUnderwater
  sta CrouchingFlag
WaterReady:
  lda Player_State
  bne SyncAir
  lda #0
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  sta MmYFraction
  sta MmYFraction+1
  sta SmFlip
  sta SmSourceJumped
  beq Input
SyncAir:
  lda #0
  sta SmCrouch
  lda Player_Y_Speed
  cmp MmVY+2
  beq Input
  sta MmVY+2
  lda #0
  sta MmVY
  sta MmVY+1
Input:
  lda SavedJoypadBits
  eor SmPreviousDirections
  and SavedJoypadBits
  sta SmTemp
  and #Down_Dir
  beq CheckUnmorph
  lda SmBall
  bne CheckUnmorph
  lda CrossoverBehaviorVersion
  beq MorphIntrinsic             ; Linked1.0 has no crouch or Morph item gate.
  lda Player_State
  bne TryMorph
  lda SmCrouch
  bne TryMorph
  ; Non-classic 2.02: first grounded Down crouches without any upgrade.
  lda #1
  sta SmCrouch
  bne CheckUnmorph
TryMorph:
  lda #1
  farcall InventoryHas
  jcc CheckUnmorph
MorphIntrinsic:
  lda #1
  sta SmBall
  lda #0
  sta SmCrouch
  sta SmFlip
  lda SmSfx
  ora #2
  sta SmSfx
  lda Player_State
  bne CheckUnmorph
  farcall SamusMorphEnter
CheckUnmorph:
  lda A_B_Buttons
  eor PreviousA_B_Buttons
  and A_B_Buttons
  and #A_Button
  sta SmClearance
  lda SmBall
  beq CheckJump
  lda SmTemp
  and #Up_Dir
  ora SmClearance
  jeq BallReady
  jsr SamusCanStand
  jne BallReady
  lda #0
  sta SmBall
  sta SmClearance                  ; A exits Morph Ball without launching a jump.
  lda Player_State
  bne BallReady
  jsr MorphLift
CheckJump:
  lda SmCrouch
  beq CrouchReady
  lda SmTemp
  and #Up_Dir
  ora SmClearance
  beq CrouchReady
  lda SmClearance
  pha
  jsr SamusCanStand
  tax
  pla
  sta SmClearance
  cpx #0
  beq StandFromCrouch
  lda #0
  sta SmClearance
  beq BallReady
StandFromCrouch:
  lda #0
  sta SmCrouch
CrouchReady:
  lda SmClearance
  beq BallReady
  lda Player_State
  bne BallReady
  lda #1
  sta Player_State
  sta SmSourceJumped
  lda #0
  sta SmCrouch
  lda #$55
  sta MmVY
  lda #$d5
  sta MmVY+1
  lda #$fb                        ; -500 / 120 = -4.166667
  sta MmVY+2
  lda Player_Y_Position
  sta SmJumpStartY
  lda SavedJoypadBits
  and #3
  sta SmFlip
  lda #0
  sta MmJumpReleased
  sta MmFrictionYActive
  lda SmSfx
  ora #1
  sta SmSfx
BallReady:
  lda SmBall
  ora SmCrouch
  beq Release
  lda #4
  sta CrouchingFlag
Release:
  lda A_B_Buttons
  and #A_Button
  bne Move
  lda PreviousA_B_Buttons
  and #A_Button
  beq Move
  lda MmJumpReleased
  bne Move
  lda #1
  sta MmJumpReleased
  sta MmFrictionYActive
Move:
  lda SavedJoypadBits
  sta SmPreviousDirections
  lda #0
  sta MmVX
  sta MmVX+1
  sta MmVX+2
  lda SmBall
  bne Direction
  lda Player_State
  bne Direction
  lda SavedJoypadBits
  and #Down_Dir
  bne Integrate                   ; Holding Down never walks upright/crouched.
  lda SmCrouch
  beq Direction
  lda SavedJoypadBits
  and #3
  beq Integrate
  jsr SamusCanStand
  bne Integrate
  lda #0
  sta SmCrouch
  sta CrouchingFlag
Direction:
  ; Forms/stand-clearance are final before the grounded speed cap reads water.
  lda SwimmingFlag
  beq DirectionReady
  farcall CrossoverWaterCheck
DirectionReady:
  lda SavedJoypadBits
  and #3
  cmp #1
  beq Right
  cmp #2
  bne Integrate
  sta PlayerFacingDir
  jsr SetSpeed
  farcall MegaManMovement::NegateX
  jmp Integrate
Right:
  sta PlayerFacingDir
  jsr SetSpeed
Integrate:
  farcall MegaManMovement::Horizontal
  rts
SetSpeed:
  lda #1
  sta MmVX+2
  lda #$40                        ; Input is 180; updateLoc clamps it to 150.
  sta MmVX+1
  lda MmUnderwater
  beq SpeedDone
  lda Player_State
  bne SpeedDone
  lda #0
  sta MmVX+2
  lda #$c0
  sta MmVX+1
SpeedDone:
  rts
MorphLift:
  farcall SamusMorphExit
  rts
.endproc

.segment "SAMUS"
.proc SamusPortrait
  jsr CrossoverGraphicsBank
  lda #SM_POSE_STAND
  sta SmPose
  ldx PlayerStatus
  lda PortraitLo,x
  sta SmPosePtr
  lda PortraitHi,x
  sta SmPosePtr+1
  lda #0
AddPower:
  cpx #0
  beq Bank
  clc
  adc #SAMUS_POSE_COUNT
  dex
  jmp AddPower
Bank:
  tax
  lda SamusPoseBanks,x
  sta SmChrBank
  sta PlayerChrBank
  inc ReloadCHRBank
  lda #METASPRITE_SAMUS_BODY
  sta ObjectMetasprite
  rts
PortraitLo: .byte <SmP0_STANDRight,<SmP1_STANDRight,<SmP2_STANDRight
PortraitHi: .byte >SmP0_STANDRight,>SmP1_STANDRight,>SmP2_STANDRight
.endproc
.proc SamusCanStand
  lda Player_X_Position
  sta SmTempX
  lda Player_PageLoc
  sta SmTempPage
  lda Player_Y_Position
  sta SmTempY
  lda #0
  sta SmClearance
  ldx #3
Loop:
  stx SmTemp
  lda #$fb
  ldy Offsets,x
  beq :+
    lda #5
  :
  clc
  adc SmTempX
  sta Player_X_Position
  lda SmTempPage
  ldy Offsets,x
  bne :+
    sbc #0
    jmp Page
  :
  adc #0
Page:
  sta Player_PageLoc
  lda SmTemp
  and #2
  asl
  clc
  adc SmTempY
  sta Player_Y_Position
  ldy #0
  jsr BlockBufferColli_Head
  beq Next
  jsr ChkForNonSolids
  beq Next
  cmp #$23
  beq Next
  lda #1
  sta SmClearance
Next:
  ldx SmTemp
  dex
  bpl Loop
  lda SmTempX
  sta Player_X_Position
  lda SmTempPage
  sta Player_PageLoc
  lda SmTempY
  sta Player_Y_Position
  lda SmClearance
  rts
Offsets: .byte 0,1,0,1
.endproc

.proc SamusGraphics
  jsr CrossoverGraphicsBank
  lda #0
  sta PlayerSize
  lda Player_SprAttrib
  and #$fc
  sta Player_SprAttrib
  lda GameEngineSubroutine
  cmp #$0b
  bne :+
    lda #0
    sta ObjectMetasprite
    rts
  :
  lda GuestPowerupActive
  beq :+
    jsr GuestPowerupPalette
    lda GuestPowerupPose
    jmp Pose
  :
  lda GuestHurtTicks
  beq :+
    lda SmBall
    bne :+                    ; A blocked Morph Ball exit retains its ball art.
    lda #SM_POSE_JUMP           ; Samus.takeDamageStart holds FL_JUMP.
    jmp Pose
  :
  inc SmAnimClock
  lda SmBall
  beq NotBall
  lda SmAnimClock
  lsr
  and #3
  clc
  adc #SM_POSE_BALL1
  jmp Pose
NotBall:
  lda Player_State
  cmp #3
  bne NotClimbing
  lda Player_Y_Speed
  beq ClimbPose
  lda SmAnimClock
  lsr
  lsr
  and #1
  sta MmClimbFrame
ClimbPose:
  lda MmClimbFrame
  and #1
  clc
  adc #SM_POSE_CLIMB1
  jmp Pose
NotClimbing:
  cmp #0
  jne Air
  lda SmCrouch
  beq Ground
  lda #SM_POSE_CROUCH
  ldx SmShootPose
  jeq Pose
  lda #SM_POSE_CROUCHSHOOT
  jmp Pose
Ground:
  lda #SM_POSE_STAND
  sta SmPose
  lda Player_X_Speed
  beq GroundAim
  lda SmAnimClock
  ldx #0
WalkDivide:
  cmp #3
  bcc WalkModulo
  sbc #3
  inx
  jmp WalkDivide
WalkModulo:
  txa
WalkReduce:
  cmp #3
  bcc WalkFrame
  sbc #3
  jmp WalkReduce
WalkFrame:
  clc
  adc #SM_POSE_WALK1
  sta SmPose
GroundAim:
  lda SavedJoypadBits
  and #Up_Dir
  beq GroundShoot
  lda SmPose
  clc
  adc #8
  sta SmPose
GroundShoot:
  lda SmShootPose
  beq LoadPose
  lda SmPose
  ldx Player_X_Speed
  beq StandShoot
  clc
  adc #3
  bne Pose
StandShoot:
  clc
  adc #1
  bne Pose
Air:
  lda #SM_POSE_JUMP
  sta SmPose
  lda SavedJoypadBits
  and #Up_Dir
  beq AirShoot
  lda #SM_POSE_UPJUMP
  sta SmPose
AirShoot:
  lda SmShootPose
  beq CheckFlip
  lda SmPose
  clc
  adc #1
  bne Pose
CheckFlip:
  lda SmFlip
  beq LoadPose
  lda SavedJoypadBits
  and #Up_Dir
  bne LoadPose
  lda SmJumpStartY
  sec
  sbc Player_Y_Position
  cmp #30
  bcc LoadPose
  lda SmAnimClock
  lsr
  and #3
  clc
  adc #SM_POSE_FLIP1
  bne Pose
LoadPose:
  lda SmPose
Pose:
  sta SmPose
  jsr GuestVisualStatus
  ldy SmPose
  cpy #SM_POSE_CROUCH
  bcs CrouchIndex
  tax
  lda SmPose
  cpx #0
  beq IndexReady
PowerIndex:
  clc
  adc #SAMUS_POSE_COUNT
  dex
  bne PowerIndex
IndexReady:
  tax
  lda SamusPoseBanks,x
  sta SmChrBank
  lda PlayerFacingDir
  cmp #1
  bne Left
  lda SamusPoseRightLo,x
  sta SmPosePtr
  lda SamusPoseRightHi,x
  bne Pointer
Left:
  lda SamusPoseLeftLo,x
  sta SmPosePtr
  lda SamusPoseLeftHi,x
  jmp Pointer
CrouchIndex:
  asl
  sta SmTemp
  tya
  sec
  sbc #SM_POSE_CROUCH
  clc
  adc SmTemp
  tax
  lda SamusCrouchBanks,x
  sta SmChrBank
  lda PlayerFacingDir
  cmp #1
  bne CrouchLeft
  lda SamusCrouchRightLo,x
  sta SmPosePtr
  lda SamusCrouchRightHi,x
  jmp Pointer
CrouchLeft:
  lda SamusCrouchLeftLo,x
  sta SmPosePtr
  lda SamusCrouchLeftHi,x
Pointer:
  sta SmPosePtr+1
  lda #METASPRITE_SAMUS_BODY
  sta ObjectMetasprite
  lda Player_Rel_XPos
  sta Player_Pos_ForScroll
  rts
.endproc

.proc SamusDeathUpdate
  inc MmDeathAge
  lda #180
  ldx MmDeathPit
  beq :+
    lda #150
  :
  cmp MmDeathAge
  bne Done
  lda #6
  sta GameEngineSubroutine
  lda #0
  sta TimerControl
Done:
  rts
.endproc
.popseg
