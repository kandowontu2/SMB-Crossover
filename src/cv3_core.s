; Original-USA CV3 motion, authored poses and SMB scene adapter. Source
; reference pinned3272648f; original player banks1C/1D byte authenticated.
.pushseg
.segment "CV3_CORE"
.proc Cv3IsActive
  lda SelectedCharacter
  cmp #CHARACTER_SIMON
  jne No
  lda Cv3Variant
  jeq No
  cmp #4
  jcs No
  sec
  rts
No:
  clc
  rts
.endproc
.macro Cv3Gate legacy
.local Live
  php
  pha
  jsr Cv3IsActive
  jcs Live
  pla
  plp
  farcall legacy,jmp
Live:
  pla
  plp
.endmacro
.proc Cv3Ensure
  ldx Cv3Variant
  dex
  lda Cv3Ready,x
  jne Area
  lda #64
  sta Cv3Health,x
  lda #10
  sta Cv3Hearts,x
  lda #0
  sta Cv3Subweapon,x
  sta Cv3Power,x
  lda #1
  sta Cv3Ready,x
Area:
  lda Cv3Variant
  cmp Cv3ActiveVariant
  jne Reset
  lda NumberofLives
  cmp Cv3LastLife
  jne Life
  lda AreaPointer
  cmp Cv3LastArea
  jne Reset
  lda WorldNumber
  cmp Cv3LastWorld
  jeq Done
  jne Reset
Life:
  lda #64
  sta Cv3Health,x
  lda #10
  sta Cv3Hearts,x
  lda #0
  sta Cv3Subweapon,x
  sta Cv3Power,x
Reset:
  jsr Cv3ClearTransient
Done:
  rts
.endproc
.proc Cv3ClearTransient
  lda #0
  ldx #0
Loop:
  sta $5c00,x
  inx
  jne Loop
  lda Cv3Variant
  sta Cv3ActiveVariant
  lda NumberofLives
  sta Cv3LastLife
  lda AreaPointer
  sta Cv3LastArea
  lda WorldNumber
  sta Cv3LastWorld
  lda #1
  sta Cv3Pose
  jsr Cv3CacheBody
  rts
.endproc
.proc Cv3ResetGate
  farcall VvResetDispatch
  jsr Cv3IsActive
  jcc Done
  jmp Cv3ClearTransient
Done:rts
.endproc
.proc Cv3MovementGate
  Cv3Gate Z2MovementGate
  jsr Cv3Ensure
  lda GameEngineSubroutine
  cmp #8
  jne Done
  lda SavedJoypadBits
  eor Cv3Previous
  and SavedJoypadBits
  sta Cv3Fresh
  lda SavedJoypadBits
  sta Cv3Previous
  lda #0
  sta PlayerSize
  sta CrouchingFlag
  sta RgCrouch
  sta MmSliding
  sta MmFrictionYActive
  sta GuestHurtKind
  sta MmUnderwater
  lda #1
  sta GuestHurtVisible
  lda SwimmingFlag
  jeq Timers
  farcall CrossoverWaterCheck
Timers:
  lda Cv3Invul
  jeq InjuryDone
  dec Cv3Invul
  lda #1
  sta InjuryTimer
  lda FrameCounter
  and #4
  jeq InjuryDone
  lda #0
  sta GuestHurtVisible
InjuryDone:
  lda Cv3AttackAge
  jeq Hurt
  dec Cv3AttackAge
Hurt:
  lda Cv3HurtAge
  jeq Ability
  dec Cv3HurtAge
  clc
  lda Cv3VyLo
  adc #$40
  sta Cv3VyLo
  lda Cv3VyHi
  adc #0
  sta Cv3VyHi
  jmp Integrate
Ability:
  jsr Cv3Abilities
  jcs Integrate
  lda Player_State
  jeq Ground
  lda Cv3JumpActive
  jne Air
  jsr Cv3StartFall
  jmp Air
Ground:
  lda Cv3JumpActive
  jeq OrdinaryGround
  lda Cv3JumpPhase
  jne OrdinaryGround
  lda #1
  sta Player_State
  jmp Air
OrdinaryGround:
  lda #0
  sta Cv3JumpActive
  sta Cv3JumpReleased
  sta Cv3JumpPhase
  sta Cv3VyLo
  sta Cv3VyHi
  sta MmYFraction
  sta MmYFraction+1
  lda SavedJoypadBits
  and #Down_Dir
  jeq Jump
  lda #1
  sta RgCrouch
  lda #4
  sta CrouchingFlag
Jump:
  lda Cv3Fresh
  and #A_Button
  jeq GroundWalk
  lda RgCrouch
  jne GroundWalk
  jsr Cv3StartJump
  jmp Air
GroundWalk:
  jsr Cv3GroundVelocity
  jmp Integrate
Air:
  lda Cv3Variant
  cmp #1
  jne FixedAir
  lda SavedJoypadBits
  and #3
  jeq GrantNoDirection
  cmp #2
  jcs GrantLeft
  sta PlayerFacingDir
  lda #1
  jne GrantVX
GrantLeft:
  lda #2
  sta PlayerFacingDir
  lda #$ff
  jne GrantVX
GrantNoDirection:
  lda #0
GrantVX:
  sta Cv3VxHi
  lda #0
  sta Cv3VxLo
  jmp JumpVelocity
FixedAir:
  lda Cv3AirVX
  sta Cv3VxHi
  lda #0
  sta Cv3VxLo
JumpVelocity:
  jsr Cv3JumpVelocity
Integrate:
  lda Cv3VxLo
  sta MmVX+1
  lda Cv3VxHi
  sta MmVX+2
  lda Cv3VyLo
  sta MmVY+1
  lda Cv3VyHi
  sta MmVY+2
  lda #0
  sta MmVX
  sta MmVY
  sta RgGravity
  sta RgGravity+1
  sta XgGravity
  sta XgGravity+1
  sta MmFrictionYActive
  lda #8
  sta RgFallCap+2
  ; Native shared position/camera integrator; gravity is disabled because
  ; CV3's original trajectory table already supplies this update's velocity.
  lda Player_State
  sta Cv3Temp
  lda #0
  sta Player_State
  farcall X5BounceCv3Horizontal
  lda Cv3Temp
  sta Player_State
  jeq Integrated
  clc
  lda MmYFraction+1
  adc Cv3VyLo
  sta MmYFraction+1
  lda Player_Y_Position
  adc Cv3VyHi
  sta Player_Y_Position
  lda #0
  ldx Cv3VyHi
  bpl :+
  lda #$ff
:
  adc Player_Y_HighPos
  sta Player_Y_HighPos
  lda Cv3VyHi
  sta Player_Y_Speed
Integrated:
  jsr Cv3CacheBody
Done:
  rts
.endproc
.proc Cv3GroundVelocity
  lda #0
  sta Cv3VxLo
  sta Cv3VxHi
  lda Cv3AttackAge
  ora RgCrouch
  jne Done
  lda SavedJoypadBits
  and #3
  cmp #1
  jeq Right
  cmp #2
  jne Done
  sta PlayerFacingDir
  lda #$ff
  sta Cv3VxHi
  lda Cv3Variant
  cmp #1
  jne Done
  lda #$c0
  sta Cv3VxLo
  lda #$fe
  sta Cv3VxHi
  rts
Right:
  sta PlayerFacingDir
  lda #1
  sta Cv3VxHi
  lda Cv3Variant
  cmp #1
  jne Done
  lda #$40
  sta Cv3VxLo
Done:rts
.endproc
.proc Cv3StartJump
  lda #1
  sta Player_State
  sta Cv3JumpActive
  lda #2
  sta Cv3JumpDelay
  lda #0
  sta Cv3JumpReleased
  sta Cv3JumpPhase
  lda #9
  ldx Cv3Variant
  cpx #1
  bne :+
  lda #30
:
  sta Cv3JumpIndex
  lda SavedJoypadBits
  and #3
  jeq NoDirection
  cmp #2
  jeq Left
  lda #1
  jne Store
Left:
  lda #$ff
  jne Store
NoDirection:
  lda #0
Store:
  sta Cv3AirVX
  lda #Sfx_BigJump
  sta Square1SoundQueue
  rts
.endproc
.proc Cv3StartFall
  lda #1
  sta Cv3JumpActive
  sta Cv3JumpPhase
  lda #12
  ldx Cv3Variant
  cpx #1
  bne :+
  lda #56
:
  sta Cv3JumpIndex
  lda #0
  sta Cv3AirVX
  rts
.endproc
.proc Cv3JumpVelocity
  lda Cv3JumpDelay
  jeq Live
  dec Cv3JumpDelay
  lda #0
  sta Cv3VyLo
  sta Cv3VyHi
  rts
Live:
  lda Cv3Variant
  cmp #2
  jne OriginalJump
  jmp Cv3SyphaArc
OriginalJump:
  ; A native head bump owns a positive/zero speed while our old table was
  ; still rising. Start the source's falling half instead of re-entering it.
  lda Player_Y_Speed
  jmi Table
  lda Cv3VyHi
  jpl Table
  lda #1
  sta Cv3JumpPhase
Table:
  lda #0
  sta Cv3VyLo
  sta MmYFraction
  sta MmYFraction+1
  lda Cv3Variant
  cmp #1
  jne Fixed
  lda Cv3JumpPhase
  jne GrantDown
  lda SavedJoypadBits
  and #A_Button
  jne GrantUp
  lda #1
  sta Cv3JumpReleased
GrantUp:
  ldy Cv3JumpIndex
  lda Cv3GrantJump,y
  cmp #$81
  jeq Apex
  sta Cv3VyHi
  tya
  clc
  adc #1
  ldx Cv3JumpReleased
  jeq Clamp
  clc
  adc #1
Clamp:
  cmp #57
  jcc Save
  lda #57
Save:
  sta Cv3JumpIndex
  rts
GrantDown:
  ldy Cv3JumpIndex
  lda Cv3GrantJump,y
  cmp #$80
  jeq Terminal
  eor #$ff
  clc
  adc #1
  sta Cv3VyHi
  tya
  sec
  sbc #2
  jpl Save
  lda #0
  jeq Save
Fixed:
  ldy Cv3JumpIndex
  lda Cv3FixedJump,y
  ldx Cv3JumpPhase
  jne FixedDown
  cmp #$81
  jeq Apex
  sta Cv3VyHi
  inc Cv3JumpIndex
  rts
FixedDown:
  cmp #$80
  jeq Terminal
  eor #$ff
  clc
  adc #1
  sta Cv3VyHi
  dec Cv3JumpIndex
  rts
Apex:
  lda #1
  sta Cv3JumpPhase
  dec Cv3JumpIndex
  lda #0
  sta Cv3VyHi
  rts
Terminal:
  lda #7
  ldx Cv3Variant
  cpx #1
  beq :+
  lda #6
:
  sta Cv3VyHi
  rts
.endproc
.proc Cv3CacheBody
  lda #6
  ldx #15
  ldy Cv3Variant
  cpy #1
  jne Compact
  lda #3
  ldx #12
Compact:
  ldy RgCrouch
  jne Small
  ldy Cv3Bat
  cpy #2
  jne Store
Small:
  lda #8
  ldx #17
Store:
  sta Cv3CachedAdder
  stx Cv3CachedBox
  rts
.endproc
.popseg

.pushseg
.segment "CV3_CORE"
.proc Cv3SyphaArc
  lda Cv3JumpPhase
  bne Step
  lda Cv3JumpIndex
  cmp #9
  bne Head
  inc Cv3JumpIndex
  lda #0
  sta Cv3VyLo
  sta MmYFraction+1
  lda #$fa
  sta Cv3VyHi
  rts
Head:
  lda Player_Y_Speed
  bmi Step
  lda Cv3VyHi
  bpl Step
  lda #0
  sta Cv3VyLo
  sta Cv3VyHi
  sta MmYFraction+1
Step:
  clc
  lda Cv3VyLo
  adc #$40
  sta Cv3VyLo
  lda Cv3VyHi
  adc #0
  sta Cv3VyHi
  bmi Done
  lda #1
  sta Cv3JumpPhase
  lda Cv3VyHi
  cmp #6
  bcc Done
  lda #6
  sta Cv3VyHi
  lda #0
  sta Cv3VyLo
Done:
  rts
.endproc
.popseg
