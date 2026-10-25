; Additional guests. Movement uses the same Q8.16 integration, native world
; collision and camera as the original six, with independent input rules.
.include "expanded_poses.inc"
.include "pit_metasprites.inc"
.include "rygar_metasprites.inc"
.include "luigi_metasprites.inc"
.include "bass_metasprites.inc"
.include "ryu_metasprites.inc"
.include "sophia_metasprites.inc"
.include "scrooge_metasprites.inc"
.pushseg
.segment "FIXED"
.if ::ENABLE_MMC5_EXPANDED
.proc ExpandedGraphicsBank
  jmp DwResidentGraphicsSelector
::X5PlayerOutlineFlag:
  ; Legacy records own optional masks; new profiles draw their own ink.
  ; Preserve the original LDA's C/V/D/I and report only returned A in N/Z.
  php
  cpx #13
  bcs NewProfile
  lda RlOutlineBypass
  bne NewProfile
  lda PlayerOutlineCharacters,x
  jmp RestoreFlags
NewProfile:
  lda #0
RestoreFlags:
  plp
  ora #0
  rts
  .res 1,$ea
  .assert *-ExpandedGraphicsBank=26,error,"original graphics bank span"
.endproc
.else
.proc ExpandedGraphicsBank
  lda SelectedCharacter
  sec
  sbc #CHARACTER_PIT
  tax
  lda Banks,x
.if ::MAPPER_MMC5
  ora #MMC5_PRG_ROM
.endif
  BankPRGC a
  rts
Banks: .byte .bank(XgPIT0_STANDRight),.bank(XgRYGAR0_STANDRight),.bank(XgLUIGI0_STANDRight),.bank(XgBASS0_STANDRight),.bank(XgRYU0_STANDRight),.bank(XgSOPHIA0_STANDRight),.bank(XgSCROOGE_STANDRight)
.endproc
.endif
.if ::ENABLE_MMC5_EXPANDED
.proc ExpandedCollisionAdder
  farcall HotCollisionAdder,jmp
::KbNativeHeadBridge:
  farcall TnFastHeadGate,jmp
::VvScrollBridge:
  farcall VvScrollGate,jmp
  .res 3,$ea
  .assert *-ExpandedCollisionAdder=57,error,"Original collision leaf span"
.endproc
.else
.proc ExpandedCollisionAdder
  ldy #6
  cmp #CHARACTER_SCROOGE
  beq Scrooge
  cmp #CHARACTER_LUIGI
  jeq Luigi
  cmp #CHARACTER_PIT
  beq Medium
  cmp #CHARACTER_BASS
  beq Medium
  cmp #CHARACTER_SOPHIA
  beq Medium
  lda GuestHurtTicks
  beq Crouch
  iny                          ; Ryu's25NESpx recoil head/feet profile.
  sec
  rts
Crouch:
  lda RgCrouch
  beq Yes
Short:
  ldy #8
  bne Yes
Medium:
  ldy #3
  lda RgCrouch
  bne Short
Yes:
  sec
  rts
Luigi:
  clc                          ; Use native PlayerSize/CrouchingFlag adders.
  rts
Scrooge:
  ldy #10
  sec
  rts
.endproc
.endif
.if ::ENABLE_MMC5_EXPANDED
.proc ExpandedCollisionBox
  farcall HotCollisionBox,jmp
::Cv3ResidentBox:
 cmp #CHARACTER_SIMON
 bne Cv3BoxLegacy
 lda Cv3Variant
 beq Cv3BoxLegacy
 cmp #4
 bcs Cv3BoxLegacy
 ldy Cv3CachedBox
 rts
Cv3BoxLegacy:
 lda SelectedCharacter
 cmp #CHARACTER_BILL
 bne Cv3BoxOther
 jmp Cv3LegacyBoxBill
Cv3BoxOther:jmp Cv3LegacyBoxOther
  .res 7,$ea
  .assert *-ExpandedCollisionBox=55,error,"Original collision leaf span"
.endproc
.else
.proc ExpandedCollisionBox
  cmp #CHARACTER_SCROOGE
  beq Scrooge
  cmp #CHARACTER_LUIGI
  beq Done                     ; Preserve native small/big/crouched Y.
  ldy #15
  cmp #CHARACTER_PIT
  beq Medium
  cmp #CHARACTER_BASS
  beq Medium
  cmp #CHARACTER_SOPHIA
  beq Medium
  lda GuestHurtTicks
  beq Crouch
  iny                          ; Ryu source recoil uses the25NESpx box.
  rts
Crouch:
  lda RgCrouch
  beq Done
Short:
  ldy #17
  rts
Medium:
  ldy #12
  lda RgCrouch
  bne Short
  rts
Done:
  rts
Scrooge:
  ldy #19
  lda RgCrouch
  beq Done
  iny
  rts
.endproc
.endif

.segment "EXPANDED"
.proc ExpandedMovement
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  bne :+
    lda RgCrouch
    sta RyWallOldHeight         ; old crouch token before shared reset.
    lda SelectedCharacter
  :
  cmp #CHARACTER_SCROOGE
  bne :+
.if ::ENABLE_MMC5_EXPANDED
    farcall DwScroogeMovement
.else
    farcall ScroogeMovement
.endif
  :
  lda SelectedCharacter
  sec
  sbc #CHARACTER_PIT
  tax
  stx XgIndex
  lda #0
  sta PlayerSize
  sta CrouchingFlag
  sta RgCrouch
  sta MmSliding
  sta SmBall
  sta MmOnVine
  sta MmUnderwater
  sta MmFrictionYActive
  lda A_B_Buttons
  and #A_Button
  bne :+
    sta XgHoverActive
  :
  ldx XgIndex
  lda GravityLo,x
  sta XgGravity
  lda GravityHi,x
  sta XgGravity+1
  lda #0
  sta RgFallCap
  sta RgFallCap+1
  lda FallCap,x
  sta RgFallCap+2
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  bne :+
    lda #$c0
    sta RgFallCap+1
  :
  cmp #CHARACTER_RYU
  bne :+
    lda #$55
    sta RgFallCap
    lda #$d5
    sta RgFallCap+1
  :
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne :+
    lda #$ab
    sta RgFallCap
    lda #$2a
    sta RgFallCap+1
  :
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  bne :+
    lda A_B_Buttons
    and #A_Button
    bne :+
    lda PreviousA_B_Buttons
    and #A_Button
    beq :+
    lda #1
    sta MmJumpReleased
  :
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  bne :+
    lda MmJumpReleased
    sta MmFrictionYActive
  :
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne :+
    lda A_B_Buttons
    and #A_Button
    bne :+
    lda PreviousA_B_Buttons
    and #A_Button
    beq :+
    lda #1
    sta MmJumpReleased          ; Release is an event, including after a spring.
  :
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  bne :+
    lda #$55
    sta RgFallCap
    lda #$d5
    sta RgFallCap+1
    lda #5                      ; 700 Flash px/s / 120.
    sta RgFallCap+2
    lda A_B_Buttons
    and #A_Button
    bne BassJumpHeld
    lda PreviousA_B_Buttons
    and #A_Button
    beq BassJumpHeld
    lda #1
    sta MmJumpReleased
BassJumpHeld:
    lda MmJumpReleased
    sta MmFrictionYActive
  :
  lda SavedJoypadBits
  eor RgPreviousButtons
  and SavedJoypadBits
  sta XgFresh
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  bne SourceWallPrepared
  lda Player_State
  bne RememberSourceWall
  lda XgFresh
  and #A_Button                ; stable edge consumed by Input below.
  bne RememberSourceWall
  lda #0                       ; ordinary ground: no added bank calls.
  sta RyWallSide
  sta RyWallResolved
  sta RyWallBlocked
  sta RyWallSupported
  sta RyWallWasGround
  beq SourceWallPrepared
RememberSourceWall:
  farcall RyuWallRemember
SourceWallPrepared:
  lda Player_State
  cmp #3
  jne Water
  farcall MegaManClimbing
  rts
Water:
  lda SwimmingFlag
  jeq Sync
  farcall CrossoverWaterCheck
  lda MmUnderwater
  jeq Sync
  lda XgIndex
  tax
  lda WaterGravityLo,x
  sta XgGravity
  lda WaterGravityHi,x
  sta XgGravity+1
Sync:
  lda SelectedCharacter
  cmp #CHARACTER_LUIGI
  jne Ground
  lda PlayerStatus
  jne Ground
  lda #1
  sta PlayerSize
Ground:
  lda Player_State
  jne AirSync
  lda #0
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  sta MmYFraction
  sta MmYFraction+1
  sta XgJumpUsed
  sta XgWall
  sta XgCeiling
  sta XgWallLock
  sta XgRise
  sta XgHoverActive
  sta XgBassDashJump
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  bne :+
    lda #60
    sta XgPitFuel               ; Recharge even if A launches on landing's next update.
    lda #0
    sta XgPitFlight
  :
  jmp Input
AirSync:
  lda Player_Y_Speed
  cmp MmVY+2
  jeq Input
  sta MmVY+2
  lda #0
  sta MmVY
  sta MmVY+1
  sta XgRise
Input:
  lda XgWallLock
  beq :+
    dec XgWallLock
  :
  lda XgFresh
  and #A_Button
  jeq Crouch
  lda XgWall
  jeq CheckGroundJump
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  bne :+
    farcall RyuPlatformJump
    jcc Crouch
    jmp AfterJumpVelocity
  :
  lda PlayerFacingDir
  eor #3
  sta PlayerFacingDir
  lda #12
  sta XgWallLock
  lda #0
  sta XgWall
  jmp Launch
CheckGroundJump:
  lda Player_State
  jeq CanJump
  lda SelectedCharacter
  cmp #CHARACTER_LUIGI
  bne :+
    lda SwimmingFlag
    jeq Crouch
    lda #$55
    sta MmVY
    sta MmVY+1
    lda #$fe
    sta MmVY+2
    jmp Crouch
  :
  cmp #CHARACTER_SOPHIA
  bne :+
    lda MmUnderwater
    jne Crouch
    lda #3
    farcall InventoryHas
    jcc Crouch
    lda XgHover
    jeq Crouch
    lda #1
    sta XgHoverActive
    lda #0
    sta XgRise
    jmp Crouch
  :
  cmp #CHARACTER_PIT
  bne :+
    lda PlayerStatus
    cmp #2
    jne Crouch
    lda MmUnderwater
    jne Crouch
    lda XgPitFuel
    jeq Crouch
    lda #1
    sta XgPitFlight
    lda #Sfx_BigJump
    sta Square1SoundQueue
    jmp Crouch
  :
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  jne Crouch
  lda XgJumpUsed
  jne Crouch
  inc XgJumpUsed
  lda #0
  sta XgBassDashJump
  jmp Launch
CanJump:
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  jne Launch
  lda XgDash
  jne BassDashLaunch
  lda SavedJoypadBits
  and #Down_Dir
  jeq Launch
  lda SavedJoypadBits
  and #B_Button
  jne Crouch
  lda #1
  sta XgDash
  lda #0
  sta MmSlideTravel
  sta MmSlideTravel+1
  sta MmSlideStop
  jmp Crouch
BassDashLaunch:
  jsr BassCeiling
  lda MmCeiling
  jne Crouch
  lda #1
  sta XgBassDashJump
  lda #0
  sta XgDash
Launch:
  ldx XgIndex
  lda JumpLo,x
  sta MmVY
  lda JumpMid,x
  sta MmVY+1
  lda JumpHi,x
  sta MmVY+2
  lda MmUnderwater
  beq :+
    lda WaterJumpLo,x
    sta MmVY
    lda WaterJumpMid,x
    sta MmVY+1
    lda WaterJumpHi,x
    sta MmVY+2
  :
AfterJumpVelocity:
  lda #1
  sta Player_State
  lda #0
  sta MmJumpReleased
  sta MmFrictionYActive
  lda #Sfx_BigJump
  sta Square1SoundQueue
  lda XgBassDashJump
  beq :+
    lda #$55
    sta MmVY
    lda #$95
    sta MmVY+1
    lda #$fa                    ; Dash jump: -650 / 120.
    sta MmVY+2
  :
  lda SelectedCharacter
  cmp #CHARACTER_LUIGI
  jeq LuigiLaunch
  cmp #CHARACTER_RYU
  bne :+
    inc XgJumpUsed            ; Source jumped is true on any accepted launch.
    lda #25
    sta RyuSourceBodyProfile  ; Accepted source jump replaces retained ground attack.
    jmp Horizontal            ; groundOnSide excludes the last grounded update.
  :
  cmp #CHARACTER_SOPHIA
  jne Crouch
  lda #1
  sta XgRise
  lda Player_Y_Position
  sta XgJumpStart
  lda #41                       ; Source vertical/horizontal rises: 82/130.
  sta XgJumpHeight
  lda MmUnderwater
  jeq Crouch
  lda #65
  sta XgJumpHeight
  jmp Crouch
LuigiLaunch:
  farcall ExpandedLuigiLaunch
  jmp Crouch
Crouch:
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  bne NotPitCrouch
  lda SavedJoypadBits
  and #Down_Dir
  ora XgPitCrouchHeld
  beq Wall
  farcall PitCrouchUpdate
  jmp Wall
NotPitCrouch:
  lda Player_State
  jne Wall
GroundCrouch:
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  bne :+
    lda XgDash
    jeq Wall
    lda #1
    sta RgCrouch
    lda #4
    sta CrouchingFlag
    jmp Wall
  :
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  jeq Wall
  cmp #CHARACTER_LUIGI
  bne :+
    lda PlayerStatus
    jeq Wall                     ; Small Luigi cannot crouch.
  :
  lda SavedJoypadBits
  and #Down_Dir
  jeq Wall
  lda #1
  sta RgCrouch
  lda #4
  sta CrouchingFlag
Wall:
  jsr SophiaCeiling
  lda #0
  sta XgWall
  lda Player_State
  jeq Horizontal
  lda XgWallLock
  jne Horizontal
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  beq SourceWall
  cmp #CHARACTER_SOPHIA
  jne Horizontal
SourceWall:
  farcall RyuSophiaWallBefore
  jcc Horizontal
  jmp Integrate
Horizontal:
  lda SelectedCharacter
  cmp #CHARACTER_LUIGI
  jeq LuigiMove
  cmp #CHARACTER_BASS
  jeq BassMove
  cmp #CHARACTER_SOPHIA
  jeq SophiaMove
  cmp #CHARACTER_RYU
  bne :+
    lda Player_State
    bne :+
    lda RgAttack
    jne Stop
  :
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  bne :+
    lda Player_State
    bne :+
    lda SavedJoypadBits
    and #Up_Dir
    jne Stop
  :
  lda XgDash
  jne LockedMove
  lda XgWallLock
  jne LockedMove
  lda SavedJoypadBits
  and #3
  cmp #1
  jeq Facing
  cmp #2
  jeq Facing
  jsr ZeroX
  jmp Abilities
Facing:
  sta PlayerFacingDir
LockedMove:
  ldx XgIndex
  lda SpeedLo,x
  sta MmVX+1
  lda SpeedHi,x
  sta MmVX+2
  lda SpeedFine,x
  sta MmVX
  lda XgDash
  jeq WaterSpeed
  lda #$80
  sta MmVX+1
  lda #2
  sta MmVX+2
WaterSpeed:
  lda MmUnderwater
  jeq Direction
  lda Player_State
  jne Direction
  lda #$c0
  sta MmVX+1
  lda #0
  sta MmVX+2
  sta MmVX
Direction:
  lda RgCrouch
  jne CrouchDirection
FacingDirection:
  lda PlayerFacingDir
  cmp #2
  jne Abilities
  farcall MegaManMovement::NegateX
  jmp Abilities
Stop:
  jsr ZeroX
Abilities:
  lda SelectedCharacter
  cmp #CHARACTER_SCROOGE
  bne :+
.if ::ENABLE_MMC5_EXPANDED
    farcall DwScroogePhysics
.else
    farcall ScroogePhysics
.endif
    jmp Integrate
  :
  cmp #CHARACTER_PIT
  bne :+
    farcall PitFlightUpdate
    jmp Integrate
  :
  cmp #CHARACTER_LUIGI
  jeq LuigiRise
  cmp #CHARACTER_SOPHIA
  jne Integrate
  farcall SophiaAbilities
  jmp Integrate
LuigiRise:
  lda XgRise
  jeq Integrate
  lda A_B_Buttons
  and #A_Button
  jne Height
  lda #26
  sta XgJumpHeight
  lda XgJumpStart
  sec
  sbc Player_Y_Position
  cmp #26
  jcs EndRise                   ; Releasing late must never rewind position.
  jmp Height
Height:
  lda XgJumpStart
  sec
  sbc Player_Y_Position
  cmp XgJumpHeight
  jcc KeepRising
  lda XgJumpStart
  sec
  sbc XgJumpHeight
  sta Player_Y_Position
EndRise:
  lda #0
  sta XgRise
  lda A_B_Buttons
  and #A_Button
  jne Integrate
  lda #1
  sta MmFrictionYActive
  jmp Integrate
KeepRising:
  lda #0
  sta XgGravity
  sta XgGravity+1
Integrate:
  farcall MegaManMovement::Horizontal
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  bne OtherAfterMotion
  lda RyWallSupported
  beq ClearSourceContact
  lda #0
  sta XgWallContact
  farcall RyuWallAfterMotion, jmp
ClearSourceContact:
  lda #0
  sta XgWallContact
  rts
OtherAfterMotion:
  cmp #CHARACTER_BASS
  bne :+
    lda XgBassStep
    cmp #6
    bne :+
      jsr ZeroX                 ; The initial step changes position, not vx.
  :
  lda #0
  sta XgWallContact
  rts
CrouchDirection:
  ; A low roof can retain Pit's short body after Down is released. Let him
  ; leave that space; deliberate Down keeps the original stationary crouch.
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  jne Stop
  lda SavedJoypadBits
  and #Down_Dir
  jne Stop
  jmp FacingDirection
ZeroX:
  lda #0
  sta MmVX
  sta MmVX+1
  sta MmVX+2
  rts
BassMove:
  lda XgBassStep
  beq :+
    dec XgBassStep
  :
  lda XgDash
  beq BassNotDashing
  lda Player_State
  jeq BassDash
  ; Walking off an edge ends the ground dash state but retains its air cap.
  lda #0
  sta XgDash
  sta RgCrouch
  sta CrouchingFlag
  lda #1
  sta XgBassDashJump
BassNotDashing:
  lda MmSlideStop
  beq :+
    lda #0
    sta MmSlideStop
    jsr ZeroX
  :
  lda SavedJoypadBits
  and #3
  cmp #1
  beq BassFacing
  cmp #2
  bne BassShootStop
BassFacing:
  sta PlayerFacingDir           ; Aim can turn while ground firing is locked.
BassShootStop:
  lda Player_State
  bne BassWalk
  lda InvSelected+CHARACTER_BASS
  bne BassWalk
  lda RgShootPose
  jne Stop
  lda SavedJoypadBits
  and #B_Button
  jne Stop
BassWalk:
  lda SavedJoypadBits
  and #3
  cmp #1
  jeq BassDirection
  cmp #2
  jne Stop                    ; MegaManBase.movePlayer overrides acceleration.
BassDirection:
  sta PlayerFacingDir
  lda Player_State
  bne BassSpeed
  lda XgBassStep
  jne Stop
  lda XgFresh
  and PlayerFacingDir
  beq BassSpeed
  lda PlayerFacingDir
  cmp #1
  bne BassLeftStep
  lda MmVX+2
  bmi BassStartStep
  lda MmVX
  ora MmVX+1
  ora MmVX+2
  bne BassSpeed
  beq BassStartStep
BassLeftStep:
  lda MmVX+2
  bmi BassSpeed
BassStartStep:
  lda #6                      ; STEP_TMR=100 ms, STEP_MOVE_AMT=4 Flash px.
  sta XgBassStep
  jsr ZeroX
  lda #2
  sta MmVX+2
  jmp BassSign
BassSpeed:
  lda #$60
  ldy #1
  ldx XgBassDashJump
  beq BassWaterCap
  lda #$80
  ldy #2
  ldx MmUnderwater
  beq BassWaterCap
  lda #$e0
  ldy #1
BassWaterCap:
  ldx MmUnderwater
  beq BassCapReady
  ldx Player_State
  bne BassCapReady
  lda #$c0
  ldy #0
BassCapReady:
  sta MmVX+1
  sty MmVX+2
  lda #0
  sta MmVX
BassSign:
  lda PlayerFacingDir
  cmp #1
  beq BassWalkDone
  farcall MegaManMovement::NegateX
BassWalkDone:
  jmp Integrate
BassDash:
  jsr BassCeiling
  lda XgWallContact
  and PlayerFacingDir
  bne BassDashWall
  lda SavedJoypadBits
  and #3
  beq BassDashDistance
  cmp #3
  beq BassDashDistance
  cmp PlayerFacingDir
  beq BassDashDistance
  ldx MmCeiling
  beq BassDashWall
  sta PlayerFacingDir         ; Reverse under a roof; stand as soon as clear.
BassDashWall:
  lda #1
  sta MmSlideStop
BassDashDistance:
  lda MmSlideStop
  beq BassDashSpeed
  lda MmCeiling
  jne BassDashSpeed
  lda #0
  sta XgDash
  sta RgCrouch
  sta CrouchingFlag
  sta MmSlideStop
  jsr ZeroX
  jmp BassMove
BassDashSpeed:
  lda #0
  sta MmVX
  lda #$80
  sta MmVX+1
  lda #2
  sta MmVX+2
  lda MmUnderwater
  beq :+
    lda #$e0
    sta MmVX+1
    lda #1
    sta MmVX+2
  :
  clc
  lda MmSlideTravel
  adc MmVX+1
  sta MmSlideTravel
  lda MmSlideTravel+1
  adc MmVX+2
  sta MmSlideTravel+1
  lda #$80
  sta RgTemp
  ldy #62
  lda MmUnderwater
  beq :+
    ldy #50
    lda #0
    sta RgTemp
  :
  cpy MmSlideTravel+1
  bcc BassDashEnd
  bne BassDashDirection
  lda RgTemp
  cmp MmSlideTravel
  bcs BassDashDirection
BassDashEnd:
  lda #1
  sta MmSlideStop
BassDashDirection:
  lda PlayerFacingDir
  cmp #1
  jeq BassWalkDone
  farcall MegaManMovement::NegateX
  jmp BassWalkDone
BassCeiling:
  lda CrouchingFlag
  pha
  lda RgCrouch
  pha
  lda #0
  sta CrouchingFlag
  sta RgCrouch
  farcall MegaManMovement::Ceiling
  pla
  sta RgCrouch
  pla
  sta CrouchingFlag
  rts
LuigiMove:
  lda #0
  sta XgLuigiSkid
  lda RgCrouch
  jne LuigiBrake
  lda SavedJoypadBits
  and #3
  cmp #1
  jeq LuigiAccel
  cmp #2
  jeq LuigiAccel
  lda Player_State
  jne Abilities
LuigiBrake:
  lda MmVX+2
  sta MmSign
  bpl :+
    farcall MegaManMovement::NegateX
  :
  jsr LoadXMultiply
  lda SavedJoypadBits
  and #B_Button
  ora RgCrouch
  beq :+
    jsr LuigiCrouchFrictionX
    jmp LuigiStoreBrake
  :
  jsr LuigiFrictionX
LuigiStoreBrake:
  jsr StoreXMultiply
  lda MmVX+2
  bne :+
    lda MmVX+1
    cmp #$55                    ; MIN_WALK_SPEED=40 /120.
    bcs :+
    jsr ZeroX
  :
  lda MmSign
  jpl LuigiClamp
  farcall MegaManMovement::NegateX
  jmp LuigiClamp
LuigiAccel:
  sta RgTemp3
  lda Player_State
  bne :+
    sta PlayerFacingDir         ; Set below from direction, on ground only.
    lda RgTemp3
    sta PlayerFacingDir
  :
  lda #$1c                      ; 200/7200 in Q8.16.
  sta RgTemp
  lda #$07
  sta RgTemp2
  lda SavedJoypadBits
  and #B_Button
  beq :+
    lda #$22                    ; 285/7200.
    sta RgTemp
    lda #$0a
    sta RgTemp2
  :
  lda RgTemp3
  cmp #1
  beq LuigiAccelRight
  sec
  lda MmVX
  sbc RgTemp
  sta MmVX
  lda MmVX+1
  sbc RgTemp2
  sta MmVX+1
  lda MmVX+2
  sbc #0
  sta MmVX+2
  jmp LuigiSkid
LuigiAccelRight:
  clc
  lda MmVX
  adc RgTemp
  sta MmVX
  lda MmVX+1
  adc RgTemp2
  sta MmVX+1
  lda MmVX+2
  adc #0
  sta MmVX+2
LuigiSkid:
  lda Player_State
  bne LuigiClamp
  lda MmVX+2
  sta MmSign
  bpl :+
    lda RgTemp3
    cmp #1
    bne LuigiClamp
    farcall MegaManMovement::NegateX
    jmp ApplySkid
  :
  lda RgTemp3
  cmp #2
  bne LuigiClamp
ApplySkid:
  lda #1
  sta XgLuigiSkid
  jsr LoadXMultiply
  farcall SamusFrictionY         ; FX_SKID=.0001, after input acceleration.
  jsr StoreXMultiply
  lda MmSign
  bpl LuigiClamp
  farcall MegaManMovement::NegateX
LuigiClamp:
  lda MmVX+2
  bpl :+
    farcall MegaManMovement::NegateX
    jsr CapLuigi
    farcall MegaManMovement::NegateX
    jmp Abilities
  :
  jsr CapLuigi
  jmp Abilities
CapLuigi:
  lda #$80
  ldy #2
  ldx MmUnderwater
  beq :+
    lda #$c0
    ldy #0
  :
  sta XgSpeed
  sty XgSpeed+1
  cpy MmVX+2
  bcc Cap
  bne CapDone
  cmp MmVX+1
  bcs CapDone
Cap:
  lda XgSpeed
  sta MmVX+1
  sty MmVX+2
  lda #0
  sta MmVX
CapDone:
  lda MmUnderwater
  bne CapReturn
  lda SavedJoypadBits
  and #B_Button
  bne CapReturn
  lda MmVX+2
  cmp #1
  bcc CapReturn
  bne LuigiAboveWalk
  lda MmVX+1
  cmp #$75
  bcc CapReturn
LuigiAboveWalk:
  lda SavedJoypadBits
  and #3
  beq CapReturn
  jsr LoadXMultiply
  jsr LuigiRunFrictionX
  jsr StoreXMultiply
CapReturn:
  rts
LoadXMultiply:
  lda MmVX
  sta MmMul
  lda MmVX+1
  sta MmMul+1
  lda MmVX+2
  sta MmMul+2
  rts
StoreXMultiply:
  lda MmMul
  sta MmVX
  lda MmMul+1
  sta MmVX+1
  lda MmMul+2
  sta MmVX+2
  rts
SophiaMove:
  lda XgWall
  jne LockedMove
  lda XgCeiling
  beq :+
    lda SavedJoypadBits
    and #3
    jeq Stop
    sta PlayerFacingDir
    jmp LockedMove
  :
  lda SavedJoypadBits
  and #3
  cmp #1
  beq SophiaRight
  cmp #2
  beq SophiaLeft
  lda Player_State
  jne Abilities
  ; Ground-only exponential braking, matching Sophia.FX.
  lda MmVX+2
  sta MmSign
  bpl :+
    farcall MegaManMovement::NegateX
  :
  jsr LoadXMultiply
  farcall MmFrictionX
  jsr StoreXMultiply
  lda MmSign
  bpl SophiaClamp
  farcall MegaManMovement::NegateX
  jmp SophiaClamp
SophiaRight:
  sta PlayerFacingDir
  clc
  lda MmVX
  adc #$72
  sta MmVX
  lda MmVX+1
  adc #$1c
  sta MmVX+1
  lda MmVX+2
  adc #0
  sta MmVX+2
  jmp SophiaClamp
SophiaLeft:
  sta PlayerFacingDir
  sec
  lda MmVX
  sbc #$72
  sta MmVX
  lda MmVX+1
  sbc #$1c
  sta MmVX+1
  lda MmVX+2
  sbc #0
  sta MmVX+2
SophiaClamp:
  lda MmVX+2
  sta MmSign
  bpl :+
    farcall MegaManMovement::NegateX
  :
  lda #$ab
  sta XgSpeed+2
  lda #$8a
  ldy #1
  ldx MmUnderwater
  beq :+
    ldx Player_State
    bne SophiaWaterAirCap
    ldx #0
    stx XgSpeed+2
    lda #$c0
    ldy #0
    beq SophiaCapReady
SophiaWaterAirCap:
    lda #$55
    sta XgSpeed+2
    lda A_B_Buttons
    and #A_Button
    ora XgRise
    beq :++
    lda #$ab
    sta XgSpeed+2
    lda #$aa
    bne SophiaCapReady
  :
  jmp SophiaCapReady
  :
    lda #$15
SophiaCapReady:
  sta XgSpeed
  cpy MmVX+2
  bcc SophiaCap
  bne SophiaSign
  cmp MmVX+1
  bcs SophiaSign
SophiaCap:
  lda XgSpeed+2
  sta MmVX
  lda XgSpeed
  sta MmVX+1
  sty MmVX+2
SophiaSign:
  lda MmSign
  bpl :+
    farcall MegaManMovement::NegateX
  :
  jmp Abilities
SophiaCeiling:
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  jne CeilingDone
  lda #6
  farcall InventoryHas
  jcc DropCeiling
  lda XgWallLock
  jne DropCeiling
  lda XgFresh
  and #A_Button
  jne DropCeiling
  lda XgCeiling
  jne CeilingProbe
  lda SavedJoypadBits
  and #Up_Dir
  jeq CeilingDone
CeilingProbe:
  lda Player_X_Position
  clc
  adc #8
  sta RgTempX
  lda Player_PageLoc
  adc #0
  sta RgTempPage
  lda Player_Y_Position
  clc
  adc #7
  sta RgTempY
  farcall ExpandedMapCell
  jcc DropCeiling
  lda #1
  sta XgCeiling
  sta Player_State
  lda #0
  sta XgGravity
  sta XgGravity+1
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  rts
DropCeiling:
  lda #0
  sta XgCeiling
CeilingDone:
  rts
SpeedLo: .byte $80,$80,$75,$60,$8a,$8a,$80
SpeedHi: .byte 1,1,1,1,1,1,1
SpeedFine:.byte 0,0,0,0,$ab,$ab,0
JumpLo: .byte $55,$00,$ab,$ab,$00,$ab,$00
JumpMid:.byte $d5,$80,$ea,$4a,$80,$aa,$00
JumpHi: .byte $fb,$fa,$fc,$fb,$fb,$fc,$fa
WaterJumpLo: .byte $55,$00,$55,$55,$ab,$ab,$00
WaterJumpMid:.byte $d5,$80,$55,$d5,$aa,$aa,$00
WaterJumpHi: .byte $fb,$fa,$fe,$fb,$fc,$fc,$fa
GravityLo: .byte $e4,$8e,$c7,$55,$c7,$55,$00
GravityHi: .byte $18,$23,$31,$35,$31,$25,$40
WaterGravityLo: .byte $39,$c7,$72,$c7,$c7,$39,$00
WaterGravityHi: .byte $0e,$11,$0c,$11,$11,$0e,$20
FallCap: .byte 3,5,4,5,5,4,6
.endproc

.pushseg
.segment "EXPANDED_EX"
; Keep the retired expanded Luigi profile in a cold bank. Playable Luigi
; uses the native Mario engine; this retains the old helper's calling contract.
.proc ExpandedLuigiLaunch
  lda MmUnderwater
  bne Ready
  lda #1
  sta XgRise
  lda Player_Y_Position
  sta XgJumpStart
  lda #65
  sta XgJumpHeight
  lda MmVX+2
  bpl RunJump
  farcall MegaManMovement::NegateX
  jsr RunJump
  farcall MegaManMovement::NegateX
Ready:
  rts
RunJump:
  lda MmVX+2
  cmp #2
  bcc Ready
  bne :+
    lda MmVX+1
    cmp #$80
    bcc Ready
  :
  lda #68
  sta XgJumpHeight
  lda #$ab
  sta MmVY
  lda #$6a
  sta MmVY+1
  lda #$fc
  sta MmVY+2
  rts
.endproc
.popseg

.proc ExpandedPortrait
  lda #XG_POSE_STAND
  sta RgPose
  jsr ExpandedPose
  lda SmChrBank
  sta PlayerChrBank
  inc ReloadCHRBank
  rts
.endproc
.proc ExpandedGraphics
  lda SelectedCharacter
  cmp #CHARACTER_SCROOGE
  bne :+
.if ::ENABLE_MMC5_EXPANDED
    farcall DwScroogeGraphics
.else
    farcall ScroogeGraphics
.endif
    rts
  :
  lda Player_SprAttrib
  and #$fc
  sta Player_SprAttrib
  lda GuestPowerupActive
  jeq Normal
  farcall GuestPowerupPalette
  lda GuestPowerupPose
  jmp Pose
Normal:
  lda GameEngineSubroutine
  cmp #$0b
  jne Movement
  lda MmDeathPit
  jne HideDead
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  jeq HideDead
  cmp #CHARACTER_SOPHIA
  jeq SophiaDeath
  cmp #CHARACTER_RYU
  bne :+
    lda RgDeathLanded
    bne :+
    lda #XG_POSE_HURT
    jmp Pose
  :
  lda #XG_POSE_DIE
  jmp Pose
SophiaDeath:
  lda MmDeathAge
  cmp #10
  jcs HideDead
  lsr
  tax
  lda DeathPoses,x
  jeq HideDead
  jmp Pose
HideDead:
  lda #0
  sta ObjectMetasprite
  rts
DeathPoses: .byte XG_POSE_DEATH1,XG_POSE_DEATH2,0,XG_POSE_DEATH3,XG_POSE_DEATH4
Movement:
  lda SelectedCharacter
  cmp #CHARACTER_LUIGI
  bne :+
    jsr LuigiNativeVisuals
  :
  inc RgClock
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne :+
    lda XgHoverActive
    beq :+
    lda RgClock
    and #2
    beq :++
    lda #XG_POSE_HOVERSMALL
    jmp Pose
  :
  jmp NormalMovement
  :
  lda #XG_POSE_HOVER
  jmp Pose
NormalMovement:
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  beq HurtProfile
  cmp #CHARACTER_RYU
  bne :+
HurtProfile:
    lda GuestHurtTicks
    beq :+
    lda #XG_POSE_HURT            ; Source static damage pose, world still live.
    jmp Pose
  :
  lda XgCeiling
  beq :+
    lda #XG_POSE_CEILING
    ldx SavedJoypadBits
    txa
    and #Down_Dir
    beq CeilingPose
      lda #XG_POSE_DIAGUP       ; Inverted cannon aimed away from the ceiling.
      jmp Pose
CeilingPose:
    lda #XG_POSE_CEILING
    jmp Pose
  :
  lda #XG_POSE_STAND
  ldx XgWall
  jeq Attack
  lda #XG_POSE_WALL
  ldy SelectedCharacter
  cpy #CHARACTER_SOPHIA
  bne WallPoseReady
    lda XgWall
    eor #3
    sta RgTemp
    lda SavedJoypadBits
    and #3
    cmp RgTemp
    beq WallAwayPose
    lda #XG_POSE_WALL
    ldx XgJumpUsed
    cpx #1
    bne WallPoseReady
    lda #XG_POSE_DIAGDOWN
    bne WallPoseReady
WallAwayPose:
    lda #XG_POSE_THROW
    ldx XgJumpUsed
    cpx #1
    bne WallPoseReady
    lda #XG_POSE_JUMPDIAGDOWN
WallPoseReady:
  jmp Pose
Attack:
  farcall RemainingAirPose
  jcs Pose
  ldx RgAttack
  jeq Shoot
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  bne :+
    farcall RyuAttackPose
    jmp Pose
  :
  lda RgAttackAge
  lsr
  lsr
  and #3
  cmp #3
  bcc :+
    lda #2
  :
  clc
  adc #XG_POSE_ATTACK1
  ldx SelectedCharacter
  cpx #CHARACTER_PIT
  jeq HammerStance
  cpx #CHARACTER_RYU
  jne Pose
HammerStance:
  ldx RgCrouch
  jeq AirHammer
  clc
  adc #XG_POSE_CROUCHATTACK1-XG_POSE_ATTACK1
  jmp Pose
AirHammer:
  ldx Player_State
  jeq Pose
  clc
  adc #XG_POSE_JUMPATTACK1-XG_POSE_ATTACK1
  jmp Pose
Shoot:
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  jne OtherShoot
  lda XgDash
  jne Crouch
  ldx RgShootPose
  jeq Crouch
  lda #XG_POSE_ATTACK2
  ldx Player_State
  beq BassAimPose
  lda #XG_POSE_JUMPSHOOT
BassAimPose:
  sta RgTemp
  lda SavedJoypadBits
  and #Up_Dir
  beq BassDownPose
  lda #XG_POSE_UP
  ldx Player_State
  beq :+
    lda #XG_POSE_JUMPUP
  :
  sta RgTemp
  lda SavedJoypadBits
  and #3
  beq BassPoseReady
  lda #XG_POSE_DIAGUP
  ldx Player_State
  beq :+
    lda #XG_POSE_JUMPDIAGUP
  :
  jmp Pose
BassDownPose:
  lda SavedJoypadBits
  and #Down_Dir
  beq BassPoseReady
  lda #XG_POSE_DIAGDOWN
  ldx Player_State
  jeq Pose
  lda #XG_POSE_JUMPDIAGDOWN
  jmp Pose
BassPoseReady:
  lda RgTemp
  jmp Pose
OtherShoot:
  ldx RgShootPose
  jeq Crouch
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  jeq BowDisk
  cmp #CHARACTER_RYGAR
  jne ShootDirection
BowDisk:
  lda #XG_POSE_CROUCHSHOOT
  ldx RgCrouch
  jne Pose
  ldx Player_State
  jeq ShootDirection
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  jne AirShoot
  lda SavedJoypadBits
  and #Up_Dir
  jeq AirShoot
  lda #XG_POSE_JUMPUP
  jmp Pose
AirShoot:
  lda #XG_POSE_JUMPSHOOT
  jmp Pose
ShootDirection:
  lda SavedJoypadBits
  and #Up_Dir
  beq :+
    lda #XG_POSE_UP
    jmp Pose
  :
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  bne :+
    lda #XG_POSE_THROW
    jmp Pose
  :
  lda #XG_POSE_ATTACK2
  jmp Pose
Crouch:
  lda XgLuigiSkid
  beq :+
    lda #XG_POSE_DASH
    jmp Pose
  :
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne :+
    lda SavedJoypadBits
    and #Up_Dir
    beq :+
    lda #XG_POSE_UP
    jmp Pose
  :
  lda SelectedCharacter
  cmp #CHARACTER_LUIGI
  bne :+
    lda SwimmingFlag
    beq :+
    lda Player_State
    beq :+
    lda #XG_POSE_HOVER
    jmp Pose
  :
  lda #XG_POSE_DASH
  ldx XgDash
  jne Pose
  lda #XG_POSE_CROUCH
  ldx RgCrouch
  jne Pose
  lda #XG_POSE_CLIMB1
  ldx Player_State
  cpx #3
  jeq Pose
  lda #XG_POSE_JUMP
  cpx #0
  jne Pose
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  bne :+
    lda XgBassStep
    beq :+
    lda #XG_POSE_WALKSTEP
    jmp Pose
  :
  lda #XG_POSE_STAND
  ldx Player_X_Speed
  jeq Pose
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  beq NativeWalk
  cmp #CHARACTER_RYGAR
  bne :+
NativeWalk:
    farcall ExpandedWalkPose
    jmp Pose
  :
  lda RgClock
  lsr
  lsr
  lsr
  and #3
  cmp #3
  bcc :+
    lda #1
  :
  clc
  adc #XG_POSE_WALK1
Pose:
  sta RgPose
  cmp #XG_POSE_WALK1
  bcc ResetWalk
  cmp #XG_POSE_WALK3+1
  bcc FlightPose
ResetWalk:
  lda #0
  sta XgWalkTick
  sta XgWalkPhase
  sta XgWalkDirection
FlightPose:
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  bne Render
  lda XgPitFlight
  beq Render
  lda RgAttack
  bne Render                   ; Preserve the visible hammer during a swing.
  lda GuestPowerupActive
  bne Render
  lda GameEngineSubroutine
  cmp #8
  bne Render
  lda #XG_POSE_FLAP1
  ldx RgShootPose
  beq FlapPhase
  lda #XG_POSE_FLAPSHOT1
  ldx SavedJoypadBits
  txa
  and #Up_Dir
  beq FlapShot
  lda #XG_POSE_FLAPUP1
  bne FlapPhase
FlapShot:
  lda #XG_POSE_FLAPSHOT1
FlapPhase:
  sta RgPose
  lda XgPitFuel
  and #4
  beq Render
  inc RgPose
Render:
  jmp ExpandedPose
.endproc
.pushseg
.segment "ROSTER"
.proc ExpandedWalkPose
  lda PlayerFacingDir
  cmp XgWalkDirection
  beq Frame
  sta XgWalkDirection
  lda #0
  sta XgWalkTick
  sta XgWalkPhase
Frame:
  ldx XgWalkPhase
  lda Cycle,x
  pha
  inc XgWalkTick
  ldy #6                       ; MegaManBase ANIM_SLOW_TMR = 100 ms.
  lda SelectedCharacter
  cmp #CHARACTER_RYGAR
  bne :+
    iny                        ; Native Rygar: three frames, seven updates each.
  :
  cpy XgWalkTick
  bne Done
  lda #0
  sta XgWalkTick
  inc XgWalkPhase
  ldx #4
  lda SelectedCharacter
  cmp #CHARACTER_RYGAR
  bne :+
    dex
  :
  cpx XgWalkPhase
  bne Done
  lda #0
  sta XgWalkPhase
Done:
  pla
  rts
Cycle: .byte XG_POSE_WALK1,XG_POSE_WALK2,XG_POSE_WALK3,XG_POSE_WALK2
.endproc
.popseg

.macro XgPoseCase Role
.local Left
  lda .ident(.concat("Xg",Role,"Banks")),x
  sta SmChrBank
  lda PlayerFacingDir
  cmp #1
  jne Left
  lda .ident(.concat("Xg",Role,"RightLo")),x
  sta SmPosePtr
  lda .ident(.concat("Xg",Role,"RightHi")),x
  jmp ExpandedPose::Pointer
Left:
  lda .ident(.concat("Xg",Role,"LeftLo")),x
  sta SmPosePtr
  lda .ident(.concat("Xg",Role,"LeftHi")),x
  jmp ExpandedPose::Pointer
.endmacro
.proc ExpandedPose
  jsr ExpandedGraphicsBank
  farcall SpecialBassPose
  jcs Pointer
  jsr GuestVisualStatus
  tax
  lda RgPose
AddPower:
  cpx #0
  jeq Index
  clc
  adc #XG_POSE_COUNT
  dex
  jne AddPower
Index:
  tax
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  jeq Pit
  cmp #CHARACTER_RYGAR
  jeq Rygar
  cmp #CHARACTER_LUIGI
  jeq Luigi
  cmp #CHARACTER_BASS
  jeq Bass
  cmp #CHARACTER_RYU
  jeq Ryu
  cmp #CHARACTER_SCROOGE
  jeq Scrooge
  jmp Sophia
Scrooge: XgPoseCase "SCROOGE"
Pit: XgPoseCase "PIT"
Rygar: XgPoseCase "RYGAR"
Luigi: XgPoseCase "LUIGI"
Bass:
  lda RgPose
  cmp #XG_POSE_WALK1
  beq BassLowPressure
  cmp #XG_POSE_WALK3
  beq BassLowPressure
  cmp #XG_POSE_DASH
  bne BassOriginal
BassLowPressure:
  farcall OrdinaryLowPressurePose
  bcs Pointer
BassOriginal:
  XgPoseCase "BASS"
Ryu: XgPoseCase "RYU"
Sophia: XgPoseCase "SOPHIA"
Pointer:
  sta SmPosePtr+1
  lda Player_Rel_XPos
  sta Player_Pos_ForScroll
  lda #METASPRITE_SAMUS_BODY
  sta ObjectMetasprite
  rts
.endproc
.proc ExpandedDeathUpdate
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  bne :+
    lda MmDeathPit
    bne :+
    farcall RosterCorpseUpdate
    rts
  :
  lda SelectedCharacter
  cmp #CHARACTER_LUIGI
  bne :+
    farcall LuigiDeathMotion
  :
  inc MmDeathAge
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  bne :+
    lda MmDeathPit
    bne DefaultDelay
    lda #168
    bne Delay
  :
  cmp #CHARACTER_LUIGI
  bne :+
    lda #180
    ldx MmDeathPit
    bne Delay
    lda #195
    bne Delay
  :
  cmp #CHARACTER_RYU
  bne :+
    lda #228
    bne Delay
  :
  cmp #CHARACTER_PIT
  bne DefaultDelay
  lda MmDeathPit
  bne DefaultDelay
  lda #180
  bne Delay
DefaultDelay:
  lda #150
Delay:
  cmp MmDeathAge
  jcc Finish
  jeq Finish
  rts
Finish:
  lda #6
  sta GameEngineSubroutine
  lda #0
  sta TimerControl
Done:
  rts
.endproc
.proc ExpandedChainPointer
  lda XgRYGARWeaponLo+8
  sta R0
  lda XgRYGARWeaponHi+8
  sta R1
  rts
.endproc
.popseg


