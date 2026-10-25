; Bill Rizer, Link and Simon Belmont. Reference: docs/reference/roster.json.
.pushseg
.segment "SRAM"
BillVariant: .res 1              ; Menu choice, retained across areas/lives.
RosterRamStart:
RgPose: .res 1
RgOamPlayerStart: .res 1
RgOamRotation: .res 1
RgOamFirst: .res 1
RgOamUsed: .res 1
GuestOamRotationActive: .res 1
RgDrawFirst: .res 1
RgDrawRemaining: .res 1
RgClock: .res 1
RgCrouch: .res 1
RgAttack: .res 1
RgAttackAge: .res 1
RgAttackKind: .res 1
RgAttackPower: .res 1
RgMeleeHits: .res 1
RgShootPose: .res 1
RgCooldown: .res 1
RgBillCadence: .res 1
RgBillBurst: .res 1
RgBillBurstDelay: .res 1
RgBoomStartX: .res 1
RgBoomStartPage: .res 1
RgBoomStartY: .res 1
RgBoomPower: .res 1
RgBoomReturning: .res 1
RgBoomFriction: .res 1
RgBoomDx: .res 2
RgBoomDy: .res 2
RgBoomNear: .res 1
RgBoomAxis: .res 1
RgBoomSign: .res 1
RgBoomDelta: .res 2
RgBoomVelocity: .res 2
RgDeathLanded: .res 1
RgDeathDelay: .res 1
RgDeathTotal: .res 2
RgDeathOldFeet: .res 1
RgDoubleJump: .res 1
RgPreviousButtons: .res 1
RgWeaponButtons: .res 1
RgThrust: .res 1
RgThrustReset: .res 1
; Link's previous completed native hurtboxes mirror2.02 lh* contact sides.
; Keep distinct storage: expanded movement/audio may run during transitions.
LinkLastBoxes: .res 28
LinkLastIds: .res 6
LinkLastValid: .res 1
LinkThrustPrev: .res 1
LinkThrustNow: .res 1
LinkThrustReceipt: .res 1
.assert LinkThrustReceipt-LinkLastBoxes+1=38, error, "Link contact state must remain38 bytes"
RgGravity: .res 2
RgFallCap: .res 3
RgSlot: .res 1
RgCount: .res 1
RgTemp: .res 1
RgTemp2: .res 1
RgTemp3: .res 1
RgTempX: .res 1
RgTempPage: .res 1
RgTempY: .res 1
RgAim: .res 1
RgSpread: .res 1
RgSpawnType: .res 1
RgShotType: .res 10
RgShotX: .res 10
RgShotPage: .res 10
RgShotY: .res 10
RgShotYHigh: .res 10
RgShotVXLo: .res 10
RgShotVXHi: .res 10
RgShotVYLo: .res 10
RgShotVYHi: .res 10
RgShotFracX: .res 10
RgShotFracY: .res 10
RgShotAge: .res 10
RgShotDir: .res 10
RgShotHits: .res 10
RgShotHitsNow: .res 10
RgShotImpact: .res 10
RgEnemiesPresent: .res 1
RgEnemyStun: .res 6
RgMeleeBlocks: .res 416
; State shared by the six additional guests; reset with every new area/life.
XgIndex: .res 1
XgFresh: .res 1
XgDash: .res 1
XgJumpUsed: .res 1
XgRise: .res 1
XgJumpStart: .res 1
XgJumpHeight: .res 1
XgWall: .res 1
XgWallContact: .res 1
XgCeiling: .res 1
XgWallLock: .res 1
XgHover: .res 1
XgHoverActive: .res 1
XgHoverDrain: .res 1
XgHoverRegen: .res 1
XgGravity: .res 2
XgSpeed: .res 3
XgShotAim: .res 10
XgBassFirePhase: .res 1
XgBassDashJump: .res 1
XgBassStep: .res 1
XgWalkTick: .res 1
XgWalkPhase: .res 1
XgWalkDirection: .res 1
XgPitFlight: .res 1
XgPitFuel: .res 1
XgPitBlocked: .res 1
XgLuigiSkid: .res 1
XgWindmillSide: .res 1
XgWindmillReverse: .res 1
XgWindmillFraction: .res 1
XgDiskReach: .res 1
XgDiskReturning: .res 1
XgChainReach: .res 1
XgWeaponFrame: .res 1
XgWeaponPtr: .res 2
XgWeaponAge: .res 1
XgMeleeType: .res 1
.pushseg
.segment "ZEROPAGE"
XgAudioPtr: .res 2
.popseg
XgEventAge: .res 1
InvDropKind: .res 4
InvDropX: .res 4
InvDropPage: .res 4
InvDropY: .res 4
InvDropVY: .res 4
InvDropVYMid: .res 4
InvDropVYHi: .res 4
InvDropFraction: .res 4
InvDropFractionHi: .res 4
InvDropAge: .res 4
InvDropAgeHi: .res 4
InvDropEnemy: .res 1
InvDropSlot: .res 1
InvDrawSlot: .res 1
InvDrawArt: .res 1
InvDropAmount: .res 1
XgPitCrouchHeld: .res 1
GuestBodyNoStomp: .res 1
GuestBodyAttack: .res 1
GuestBodyPrev: .res 1
GuestBodyNow: .res 1
GuestHurtKind: .res 1
GuestHurtTicks: .res 1
GuestInvulTicks: .res 1
GuestFlickerPhase: .res 1
GuestHurtVisible: .res 1
; Source STOP pauses native per-object timers and optionally the current pose.
LsrFrozenPose: .res 6
LsrFrameTimer: .res 5
LsrIntervalTimer: .res 6
.assert *-LsrFrozenPose=17, error, "LSR enemy effects must remain17 bytes"
; Link's exact damage endpoint is Q16 fractional world X. The packed flags
; retain recoil direction and released-jump friction.
LsrHurtEndX: .res 4
LsrHurtFlags: .res 1
.assert *-LsrHurtEndX=5, error, "LSR injury state must remain5 bytes"
RosterRamEnd:

; NMI-owned decoder state must survive foreground area/life clearing. The
; decoder restarts atomically on a new character or queued area/event song.
XgAudioCharacter: .res 1
XgAudioSong: .res 1
XgAudioBank: .res 1
XgAudioDelay: .res 1
XgAudioSfx: .res 1
XgAudioEvent: .res 1

.segment "SAMUS"
.proc RosterClearState
  lda #0
  sta ScPogo
  sta ScAttack
  sta ScPrevious
  sta BillSourceBodyForm
  sta BillSourceFlagSeen
  sta BillBodyPrevValid
  sta BillHeadFiltering
.if ::ENABLE_MMC5_EXPANDED
  farcall RlResetDispatch
.else
  farcall SpecialRosterClear
.endif
  farcall RemainingClear
  lda #<RosterRamStart
  sta R0
  lda #>RosterRamStart
  sta R1
  lda #0
  ldy #0
Loop:
  sta (R0),y
  inc R0
  bne :+
    inc R1
  :
  ldx R1
  cpx #>RosterRamEnd
  bne Loop
  ldx R0
  cpx #<RosterRamEnd
  bne Loop
  lda #8
  sta XgHover
  lda #60
  sta XgPitFuel
  rts
.endproc
.segment "FIXED"
.proc RosterGraphicsBank
  phx
  lda SelectedCharacter
  sec
  sbc #CHARACTER_BILL
  tax
 .if ::ENABLE_MMC5_EXPANDED
  jsr Cv3ResidentRosterBank
 .else
  lda Banks,x
 .endif
.if ::MAPPER_MMC5
  ora #MMC5_PRG_ROM
.endif
  BankPRGC a
  plx
  lda CurrentBankC             ; Preserve the original X/Y and returned bank.
  rts
Banks:
.if ::ENABLE_MMC5_EXPANDED
::Cv3LegacyBanks:
.endif
  .byte .bank(RgBILL0_STANDRight),.bank(RgLINK0_STANDRight),.bank(RgSIMON0_STANDRight)
.endproc

.segment "TITLE"
.proc RosterMovement
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne WaterEpoch
    farcall LinkPrepareContacts
    farcall EasyLinkCycle
    jmp BodyInput
WaterEpoch:
  cmp #CHARACTER_BILL
  bne BodyInput
  lda BillSourceFlagSeen
  and #1
  sta BillSourceFlagSeen          ; source updateStats consumes old hitpoints once.
  lda BillBodyPrevValid
  bne BodyInput
  lda #6
  jsr BillHotCache ; exact resident first-use initialization.

BodyInput:
  lda #0
  sta PlayerSize
  sta CrouchingFlag
  sta MmSliding
  sta MmOnVine
  sta MmUnderwater
  sta RgCrouch
  sta RgThrust
  lda SwimmingFlag
  beq WaterReady
  farcall CrossoverWaterCheck
WaterReady:
  lda SelectedCharacter
  sec
  sbc #CHARACTER_BILL
  tax
  lda GravityLo,x
  sta RgGravity
  lda GravityHi,x
  sta RgGravity+1
  lda MmUnderwater
  beq Dry
  cpx #CHARACTER_LINK-CHARACTER_BILL
  bne :+
    lda #$c7                    ; Link2.02 water gravity is500, not half1300.
    sta RgGravity
    lda #$11
    sta RgGravity+1
    bne Dry
  :
  lsr RgGravity+1
  ror RgGravity
Dry:
  lda #0
  sta RgFallCap
  sta RgFallCap+1
  lda FallCap,x
  sta RgFallCap+2
  cpx #CHARACTER_LINK-CHARACTER_BILL
  bne :+
    lda #$ab                    ; Link2.02: 800/120, or 500/120 in a water room.
    sta RgFallCap
    lda #$aa
    sta RgFallCap+1
    lda SwimmingFlag
    beq :+
      lda #$2a
      sta RgFallCap+1
      lda #4
      sta RgFallCap+2
  :
  lda CrossoverBehaviorVersion
  bne EasyFallReady
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne EasyFallReady
  lda #0
  sta RgFallCap
  sta RgFallCap+1
  lda #5
  sta RgFallCap+2
EasyFallReady:
  lda Player_State
  cmp #3
  bne NotVine
  farcall MegaManClimbing
  rts
NotVine:
  lda Player_State
  bne Air
  lda #0
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  sta MmYFraction
  sta MmYFraction+1
  sta RgDoubleJump
  sta LsrHurtFlags                ; Clear Link's persistent source jumped bit.
  cpx #CHARACTER_SIMON-CHARACTER_BILL
  bne :+
    inc RgDoubleJump              ; Simon.checkState grants the unused air jump on ground.
  :
  jmp Input
Air:
  lda Player_Y_Speed
  cmp MmVY+2
  beq Input
  sta MmVY+2
  lda #0
  sta MmVY
  sta MmVY+1
Input:
  lda A_B_Buttons
  eor PreviousA_B_Buttons
  and A_B_Buttons
  and #A_Button
  jeq Crouch
  lda Player_State
  beq Jump
  lda SelectedCharacter
  cmp #CHARACTER_SIMON
  jne Crouch
  lda RgDoubleJump
  jeq Crouch
  lda #0
  sta RgDoubleJump
  jmp Launch
Jump:
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne JumpAllowed
  lda RgAttack
  jne Crouch
  lda CrossoverBehaviorVersion
  beq JumpAllowed
  lda SavedJoypadBits
  and #Down_Dir
  jne Crouch
JumpAllowed:
  lda SelectedCharacter
  cmp #CHARACTER_SIMON
  bne Launch
  lda #1
  sta RgDoubleJump
Launch:
  lda SelectedCharacter
  sec
  sbc #CHARACTER_BILL
  tax
  cpx #CHARACTER_BILL-CHARACTER_BILL
  bne :+
    lda #$80
    sta RgDoubleJump              ; Bill's source jumped bit; ground clears it.
  :
  lda JumpLo,x
  sta MmVY
  lda JumpMid,x
  sta MmVY+1
  lda JumpHi,x
  sta MmVY+2
  cpx #CHARACTER_LINK-CHARACTER_BILL
  bne :+
    lda #8
    sta LsrHurtFlags              ; Actual Link launch, also under water.
    lda CrossoverBehaviorVersion
    bne HardLinkJump
    lda #$55                    ; Easy530/120, same jump power in water rooms.
    sta MmVY
    lda #$95
    sta MmVY+1
    jmp LinkJumpReady
HardLinkJump:
    lda SwimmingFlag            ; Source setStats chooses the water-room jump.
    beq :+
      lda #$55                  ; -500/120 = $fbd555 (Q8.16).
      sta MmVY
      lda #$d5
      sta MmVY+1
LinkJumpReady:
  :
  lda #1
  sta Player_State
  lda #0
  sta MmJumpReleased
  sta MmFrictionYActive
  sta RgCrouch
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne SoundJump
  lda CrossoverBehaviorVersion
  bne SoundJump
  lda #17                       ; Link.jump selects the ordinary jump clip.
  sta RgBillBurst
  bne JumpSoundReady
SoundJump:
  lda #Sfx_BigJump
  sta Square1SoundQueue
JumpSoundReady:
  lda SelectedCharacter
  cmp #CHARACTER_SIMON
  bne Crouch
  lda #0                        ; Source jump stops the pending whip/throw timer.
  sta RgAttack
  sta RgAttackAge
  sta RgAttackKind
  sta RgShootPose
  lda CrossoverBehaviorVersion
  bne SimonLaunchDirection
  lda SavedJoypadBits
  and #3
  cmp #1
  beq SimonLaunchDirection
  cmp #2
  bne Crouch                    ; Old neutral/both doublejump retainsVX.
SimonLaunchDirection:
  jsr ImmediateInput
Crouch:
  lda Player_State
  bne Release
  lda SavedJoypadBits
  and #Down_Dir
  beq Release
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  beq Release
  cmp #CHARACTER_BILL
  bne SetCrouch
  lda SavedJoypadBits
  and #3
  bne Release
SetCrouch:
  lda #1
  sta RgCrouch
  lda #4
  sta CrouchingFlag
Release:
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne Horizontal
  lda A_B_Buttons
  and #A_Button
  bne Horizontal
  lda PreviousA_B_Buttons
  and #A_Button
  beq Horizontal
  lda #1
  sta MmJumpReleased
  sta MmFrictionYActive
Horizontal:
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  beq LinkMove
  cmp #CHARACTER_SIMON
  bne BillMove
  lda Player_State
  beq BillMove
  lda CrossoverBehaviorVersion
  jeq Integrate                ; Easy committedair retains launchVX/facing.
  ; Nonclassic2.02 Simon steers in air, while movePlayer keeps his launch
  ; facing. A fresh/double jump updates that facing separately at Launch.
  lda PlayerFacingDir
  pha
  jsr ImmediateInput
  pla
  sta PlayerFacingDir
  jmp Integrate
BillMove:
  ; Default2.02 Simon has air direction control; Classic Simon is a cheat.
  ; ImmediateInput retains Bill's separate airborne-neutral coast behavior.
  lda RgCrouch
  bne Stop
  lda RgAttack
  beq :+
  lda SelectedCharacter
  cmp #CHARACTER_SIMON
  beq Stop
  :
  jsr ImmediateInput
  jmp Integrate
Stop:
  jsr ZeroX
  jmp Integrate
LinkMove:
  lda CrossoverBehaviorVersion
  jeq EasyLinkMove
  ; 2.02 Link.movePlayer assigns +/-175 directly, including in the air.
  ; Only a grounded sword/throw sequence stops his directional movement.
  lda RgAttack
  beq LinkWalk
  lda Player_State
  bne LinkWalk
  jsr ZeroX
  jmp Integrate
LinkWalk:
  lda SavedJoypadBits
  and #3
  cmp #1
  beq LinkDirection
  cmp #2
  beq LinkDirection
  jsr ZeroX                     ; Neutral and both directions stop immediately.
  jmp Integrate
LinkDirection:
  sta PlayerFacingDir
  lda #$55                      ; round((175/120)*65536) = $017555.
  sta MmVX
  lda #$75
  sta MmVX+1
  lda #1
  sta MmVX+2
  lda MmUnderwater
  beq LinkSigned
  lda Player_State
  bne LinkSigned
  ; Character.update applies its shared 90px/s water-ground cap after move.
  lda #0
  sta MmVX
  sta MmVX+2
  lda #$c0
  sta MmVX+1
LinkSigned:
  lda PlayerFacingDir
  cmp #1
  beq :+
    jsr MegaManMovement::NegateX
  :
  jmp Integrate
Integrate:
  lda CrossoverBehaviorVersion
  bne NormalIntegrate
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne NormalIntegrate
  lda RgAttack
  beq NormalIntegrate
  lda MmFrictionYActive        ; OldcheckState bypassesreleasefriction inattack.
  pha
  lda #0
  sta MmFrictionYActive
  jsr MegaManMovement::Horizontal
  pla
  sta MmFrictionYActive
  rts
NormalIntegrate:
  jsr MegaManMovement::Horizontal
  rts
EasyLinkMove:
  lda RgAttack
  bne EasyNoAccel
  lda SavedJoypadBits
  and #3
  cmp #1
  beq EasyRight
  cmp #2
  jeq EasyLeft
EasyNoAccel:
  lda Player_State
  jne EasyClamp
  lda MmVX+2
  sta MmSign
  bpl EasyFrictionPositive
  jsr MegaManMovement::NegateX
EasyFrictionPositive:
  lda MmVX
  sta MmMul
  lda MmVX+1
  sta MmMul+1
  lda MmVX+2
  sta MmMul+2
  farcall MmFrictionX            ; Factor50097 ~= (1e-7)^(1/60)*65536.
  lda MmMul
  sta MmVX
  lda MmMul+1
  sta MmVX+1
  lda MmMul+2
  sta MmVX+2
  lda MmSign
  bpl EasyClamp
  jsr MegaManMovement::NegateX
  jmp EasyClamp
EasyRight:
  sta PlayerFacingDir
  clc
  lda MmVX
  adc #$55                     ;600/7200, roundedQ16 once.
  sta MmVX
  lda MmVX+1
  adc #$15
  sta MmVX+1
  lda MmVX+2
  adc #0
  sta MmVX+2
  jmp EasyClamp
EasyLeft:
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
EasyClamp:
  lda MmVX+2
  sta MmSign
  bpl EasyMagnitude
  jsr MegaManMovement::NegateX
EasyMagnitude:
  lda MmVX+2
  cmp #1
  bcc EasyMin
  bne EasyLimit
  lda MmVX+1
  cmp #$75
  bcc EasyMin
  bne EasyLimit
  lda MmVX
  cmp #$56
  bcc EasyMin
EasyLimit:
  lda #$55
  sta MmVX
  lda #$75
  sta MmVX+1
  lda #1
  sta MmVX+2
EasyMin:
  lda MmVX+2
  bne EasyWater
  lda MmVX+1
  cmp #$0a
  bcc EasyZero
  bne EasyWater
  lda MmVX
  cmp #$ab
  bcs EasyWater
EasyZero:
  jsr ZeroX
EasyWater:
  lda MmUnderwater
  beq EasySigned
  lda Player_State
  bne EasySigned
  lda MmVX+2
  bne EasyWaterLimit
  lda MmVX+1
  cmp #$c0
  bcc EasySigned
EasyWaterLimit:
  lda #0
  sta MmVX
  sta MmVX+2
  lda #$c0
  sta MmVX+1
EasySigned:
  lda MmSign
  bpl EasyIntegrated
  jsr MegaManMovement::NegateX
EasyIntegrated:
  jmp Integrate
ImmediateInput:
  lda SavedJoypadBits
  and #3
  cmp #1
  beq Right
  cmp #2
  beq Left
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bne ZeroX
  lda Player_State
  bne Return
ZeroX:
  lda #0
  sta MmVX
  sta MmVX+1
  sta MmVX+2
Return:
  rts
Right:
  sta PlayerFacingDir
  jsr Speed
  rts
Left:
  sta PlayerFacingDir
  jsr Speed
  jsr MegaManMovement::NegateX
  rts
Speed:
  lda #0
  sta MmVX
  lda #$40
  sta MmVX+1
  lda #1
  sta MmVX+2
  lda MmUnderwater
  beq Return
  lda Player_State
  bne Return
  lda #0
  sta MmVX+2
  lda #$c0
  sta MmVX+1
  rts
JumpLo:  .byte $ab,0,$ab
JumpMid: .byte $6a,0,$6a
JumpHi:  .byte $fb,$fb,$fb
GravityLo: .byte $8e,$39,$55
GravityHi: .byte $23,$2e,$35
FallCap: .byte 5,6,7
.endproc

.segment "ROSTER"
.proc RosterPortrait
  lda #RG_POSE_STAND
  sta RgPose
  jsr RosterPose
  lda SmChrBank
  sta PlayerChrBank
  inc ReloadCHRBank
  rts
.endproc
.proc RosterGraphics
  jsr RosterGraphicsBank
  lda Player_SprAttrib
  and #$fc
  sta Player_SprAttrib
  lda GuestPowerupActive
  beq :+
    farcall GuestPowerupPalette
    lda GuestPowerupPose
    jmp Pose
  :
  lda GameEngineSubroutine
  cmp #$0b
  jne Normal
  lda MmDeathPit
  beq Death
  lda #0
  sta ObjectMetasprite
  rts
Death:
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  jeq LinkDeathPose
  lda MmDeathPit
  jne RotatingDeath
  lda RgDeathLanded
  beq CorpseAir
  lda #RG_POSE_DIE2
  ldx SelectedCharacter
  cpx #CHARACTER_SIMON
  jne Pose
  ldx RgDeathDelay
  cpx #102
  jcc Pose
  lda #RG_POSE_DIE1
  jmp Pose
CorpseAir:
  lda #RG_POSE_HURT
  jmp Pose
LinkDeathPose:
  lda CrossoverBehaviorVersion
  bne NativeLinkDeathPose
  farcall EasyLinkDeathVisual
  jcs Pose
  rts
NativeLinkDeathPose:
  lda MmDeathPit
  jne RotatingDeath
  lda MmDeathAge
  cmp #41
  bcc LinkFlash
  cmp #59
  bcc LinkWait
  cmp #131
  bcc LinkSpin
  cmp #172
  bcc LinkGray
  cmp #181
  bcc LinkCross
  lda #0
  sta ObjectMetasprite
  rts
LinkFlash:
  lda MmDeathAge
  lsr
  lsr
  and #1
  clc
  adc #RG_POSE_DIEFLASH1
  jmp Pose
LinkWait:
  lda #RG_POSE_DIE1
  jmp Pose
LinkSpin:
  lda MmDeathAge
  sec
  sbc #59
  asl
  ldx #0
LinkSpinDivide:
  cmp #9
  bcc LinkSpinReady
  sbc #9
  inx
  jmp LinkSpinDivide
LinkSpinReady:
  txa
  and #3
  clc
  adc #RG_POSE_DIE1
  jmp Pose
LinkGray:
  lda #RG_POSE_DIEGRAY
  jmp Pose
LinkCross:
  lda #RG_POSE_DIECROSS1
  ldx MmDeathAge
  cpx #176
  jcc Pose
  lda #RG_POSE_DIECROSS2
  jmp Pose
RotatingDeath:
  lda MmDeathAge
  lsr
  lsr
  lsr
  and #3
  clc
  adc #RG_POSE_DIE1
  jmp Pose
Normal:
  lda GuestHurtTicks
  beq Unhurt
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne HurtSimon
  ;2.02 requests the missing label"walk" when not standing. Its actual
  ; CustomMovieClip lookup clamps that missing frame to stand(frame1).
  lda #RG_POSE_STAND
  jmp Pose
HurtSimon:
  cmp #CHARACTER_SIMON
  bne Unhurt
  lda #RG_POSE_HURT
  jmp Pose
Unhurt:
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne NativeRosterVisual
  lda CrossoverBehaviorVersion
  bne NativeRosterVisual
  farcall EasyLinkVisual
  jmp Pose
NativeRosterVisual:
  inc RgClock
  lda #RG_POSE_STAND
  sta RgPose
  lda Player_State
  cmp #3
  bne NotVine
  lda RgClock
  lsr
  lsr
  lsr
  and #1
  clc
  adc #RG_POSE_CLIMB1
  jmp Pose
NotVine:
  lda RgAttack
  beq Movement
  lda RgAttackAge
  ldx SelectedCharacter
  cpx #CHARACTER_LINK
  beq LinkAttack
  ldx #RG_POSE_ATTACK1
  cmp #7
  bcc AttackPose
  inx
  cmp #14
  bcc AttackPose
  inx
  jmp AttackPose
LinkAttack:
  ldx #RG_POSE_ATTACK1
  cmp #9
  bcc AttackPose
  inx
  cmp #11
  bcc AttackPose
  inx
AttackPose:
  txa
  ldx RgAttackKind
  beq :+
    clc
    adc #RG_POSE_THROW1-RG_POSE_ATTACK1
  :
  ldx RgCrouch
  jeq Pose
  clc
  adc #RG_POSE_CROUCHATTACK1-RG_POSE_ATTACK1
  jmp Pose
Movement:
  lda RgCrouch
  beq NotCrouch
  lda #RG_POSE_CROUCH
  jmp Pose
NotCrouch:
  lda Player_State
  beq Ground
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne NotLink
  lda RgThrust
  beq Jump
  cmp #1
  beq DownThrust
  lda #RG_POSE_UPTHRUST
  jmp Pose
DownThrust:
  lda #RG_POSE_DOWNTHRUST
  jmp Pose
NotLink:
  cmp #CHARACTER_BILL
  bne Jump
  lda RgShootPose
  bne BillAim
  lda SavedJoypadBits
  and #$0c
  bne BillAim
  lda RgClock
  lsr
  lsr
  and #3
  clc
  adc #RG_POSE_JUMP1
  jmp Pose
Jump:
  lda #RG_POSE_JUMP1
  jmp Pose
Ground:
  lda Player_X_Speed
  beq BillAim
  lda RgClock
  ldx SelectedCharacter
  cpx #CHARACTER_LINK
  beq LinkWalk
  ldx #0
WalkDivide:
  cmp #7
  bcc WalkIndex
  sbc #7
  inx
  jmp WalkDivide
WalkIndex:
  txa
WalkMod:
  cmp #3
  bcc WalkReady
  sbc #3
  jmp WalkMod
WalkReady:
  clc
  adc #RG_POSE_WALK1
  sta RgPose
  jmp BillAim
LinkWalk:
  lsr
  lsr
  lsr
  and #1
  clc
  adc #RG_POSE_WALK1
  sta RgPose
BillAim:
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bne LoadPose
  lda SavedJoypadBits
  and #$0c
  beq LoadPose
  ldx #RG_POSE_UPSTAND
  and #Up_Dir
  beq AimDown
  lda SavedJoypadBits
  and #3
  beq AimReady
  ldx #RG_POSE_DIAGUP
  bne AimReady
AimDown:
  ldx #RG_POSE_DIAGDOWN
AimReady:
  txa
  jmp Pose
LoadPose:
  lda RgPose
Pose:
  sta RgPose
  jmp RosterPose
.endproc

.proc RosterPose
  jsr RosterGraphicsBank
  jsr GuestVisualStatus
  tax
  lda RgPose
AddPower:
  cpx #0
  beq Index
  clc
  adc #ROSTER_POSE_COUNT
  dex
  jmp AddPower
Index:
  tax
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  beq Link
  cmp #CHARACTER_SIMON
  jeq Simon
  lda BillVariant
  beq Bill
  lda RgLANCEBanks,x
  sta SmChrBank
  lda PlayerFacingDir
  cmp #1
  bne LanceLeft
  lda RgLANCERightLo,x
  sta SmPosePtr
  lda RgLANCERightHi,x
  jmp Pointer
LanceLeft:
  lda RgLANCELeftLo,x
  sta SmPosePtr
  lda RgLANCELeftHi,x
  jmp Pointer
Bill:
  lda RgPose
  cmp #RG_POSE_WALK2
  bne BillOriginal
  farcall OrdinaryLowPressurePose
  bcs Pointer
BillOriginal:
  lda RgBILLBanks,x
  sta SmChrBank
  lda PlayerFacingDir
  cmp #1
  bne BillLeft
  lda RgBILLRightLo,x
  sta SmPosePtr
  lda RgBILLRightHi,x
  jmp Pointer
BillLeft:
  lda RgBILLLeftLo,x
  sta SmPosePtr
  lda RgBILLLeftHi,x
  jmp Pointer
Link:
  lda RgLINKBanks,x
  sta SmChrBank
  lda PlayerFacingDir
  cmp #1
  bne LinkLeft
  lda RgLINKRightLo,x
  sta SmPosePtr
  lda RgLINKRightHi,x
  jmp Pointer
LinkLeft:
  lda RgLINKLeftLo,x
  sta SmPosePtr
  lda RgLINKLeftHi,x
  jmp Pointer
Simon:
  lda RgSIMONBanks,x
  sta SmChrBank
  lda PlayerFacingDir
  cmp #1
  bne SimonLeft
  lda RgSIMONRightLo,x
  sta SmPosePtr
  lda RgSIMONRightHi,x
  jmp Pointer
SimonLeft:
  lda RgSIMONLeftLo,x
  sta SmPosePtr
  lda RgSIMONLeftHi,x
Pointer:
  sta SmPosePtr+1
  lda Player_Rel_XPos
  sta Player_Pos_ForScroll
  lda #METASPRITE_SAMUS_BODY
  sta ObjectMetasprite
  rts
.endproc

.proc RosterDeathUpdate
  lda MmDeathPit
  bne Pit
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne Corpse
  lda CrossoverBehaviorVersion
  bne NativeLinkDeathTick
  farcall EasyLinkDeathTick
  rts
NativeLinkDeathTick:
  inc MmDeathAge
  lda MmDeathAge
  cmp #59
  bne :+
    lda #DeathMusic
    sta EventMusicQueue
  :
  lda MmDeathAge
  cmp #219                     ; 40 animation ticks at 75ms, then 650ms.
  bcc Done
  jmp Finish
Corpse:
  jmp RosterCorpseUpdate
Pit:
  inc MmDeathAge
  lda #150
  ldx MmDeathPit
  beq Normal
  ldx SelectedCharacter
  cpx #CHARACTER_LINK
  bne Check
  lda #192
  bne Check
Normal:
  ldx SelectedCharacter
  cpx #CHARACTER_LINK
  bne :+
    lda #189
  :
  cpx #CHARACTER_SIMON
  bne Check
    lda #102
Check:
  cmp MmDeathAge
  bne Done
Finish:
  lda #6
  sta GameEngineSubroutine
  lda #0
  sta TimerControl
Done:
  rts
.endproc
.proc RosterCorpseUpdate
  inc RgDeathTotal
  bne :+
    inc RgDeathTotal+1
  :
  lda RgDeathTotal+1
  jne Motion
  lda RgDeathTotal
  cmp #1
  bne Motion
  lda #0
  sta MmVX
  sta MmVY
  lda #1
  sta Player_State
  lda #$40
  sta MmVX+1
  lda #1
  sta MmVX+2
  lda PlayerFacingDir
  cmp #2
  beq :+
    farcall MegaManMovement::NegateX
  :
  lda #$80
  sta MmVY+1
  lda #$fd
  sta MmVY+2
  lda SelectedCharacter
  cmp #CHARACTER_SIMON
  bne RyuLaunch
  lda #$55
  sta MmVY
  sta MmVY+1
  lda #$fe
  sta MmVY+2
  jmp Motion
RyuLaunch:
  cmp #CHARACTER_RYU
  bne Motion
  lda #$ab
  sta MmVY
  lda #$ca
  sta MmVY+1
  lda #$fc                      ; DIE_VERT_BOOST=385 /120.
  sta MmVY+2
  lda #$c7
  sta XgGravity
  lda #$31
  sta XgGravity+1
Motion:
  lda RgDeathLanded
  jne Landed
  farcall MegaManMovement::Horizontal
  lda MmVY+2
  jmi CheckTimeout
  lda Player_Y_HighPos
  cmp #1
  jne CheckTimeout
  lda Player_X_Position
  clc
  adc #8
  sta RgTempX
  lda Player_PageLoc
  adc #0
  sta RgTempPage
  lda Player_Y_Position
  clc
  adc #32
  sta RgTempY
  farcall ExpandedMapCell
  bcc CheckTimeout
  lda RgTempY
  and #$f0
  sec
  sbc #32
  sta Player_Y_Position
  lda #0
  sta MmVX
  sta MmVX+1
  sta MmVX+2
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  lda #1
  sta RgDeathLanded
  lda #90                       ; Bill waits 1500ms after landing.
  ldx SelectedCharacter
  cpx #CHARACTER_SIMON
  bne :+
    lda #130                    ; Four 115ms kneel frames, then 1700ms.
    pha
    lda #DeathMusic
    sta EventMusicQueue
    pla
  :
  cpx #CHARACTER_RYU
  bne :+
    lda #DeathMusic
    sta EventMusicQueue
    lda #228                    ; 3800ms after landing.
  :
  sta RgDeathDelay
  rts
Landed:
  dec RgDeathDelay
  jeq RosterDeathUpdate::Finish
CheckTimeout:
  lda RgDeathTotal+1
  cmp #1
  bcc Done
  lda RgDeathTotal
  cmp #104                      ; 6000ms fallback if the corpse never lands.
  jcs RosterDeathUpdate::Finish
Done:
  rts
.endproc
.popseg

