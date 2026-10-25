; Expanded-only SMB spring/stomp adaptation. Original families keep their
; original dispatch. New platform profiles use installed Mario400/950 spring
; and300 stomp policy, translated to each owner's actual velocity format.
X5BounceOwner=$5ff0
X5BounceLo=$5ff1
X5BounceHi=$5ff2
X5BounceArea=$5ff3
X5BounceLife=$5ff4
X5BounceKey=$5ff5
X5Cv3PriorHurt=$5cc3
.export X5BounceOwner,X5BounceLo,X5BounceHi,X5BounceArea,X5BounceLife,X5BounceKey
.pushseg
.segment "SRAM"
X5CameraBefore: .res 1
X5FootDescending: .res 1
.popseg
.pushseg
.segment "X5_BOUNCE"

.proc X5EasyFootBox
  php
  pha
  lda #0
  sta X5FootDescending
  ; The walking hot path needs no family dispatch or cross-bank contact
  ; correction. Keep that work on descending-foot frames only.
  lda Player_State
  cmp #2
  bne Done
  lda Player_Y_Speed
  beq Done
  bmi Done
  lda CrossoverBehaviorVersion
  bne Done
  jsr X5BounceProfile
  bcc Done
  lda GameEngineSubroutine
  cmp #8
  bne Done
  lda #1
  sta X5FootDescending
  ; Native compact/rolling hurtboxes can end above the host's terrain feet.
  ; Easy adds the normal SMB stomp sole while descending, without changing
  ; the source's Hard-mode hurtbox or upward collision shape.
  lda Player_Rel_YPos
  clc
  adc #31
  cmp BoundingBox_LR_Corner+1
  bcc Done
  sta BoundingBox_LR_Corner+1
Done:
  pla
  plp
  rts
.endproc
.proc X5EasyBodyContact
  php
  pha
  lda X5FootDescending
  beq Done
  lda CrossoverBehaviorVersion
  bne Done
  lda Player_Y_Speed
  bne Done
  lda Player_State
  bne Done
  ; A fast source step may reach the floor before enemy collision runs.
  ; Retain that update's descending contact for the normal stomp resolver.
  lda Enemy_ID,x
  cmp #Spiny
  beq Done
  cmp #PiranhaPlant
  beq Done
  cmp #Podoboo
  beq Done
  lda Enemy_Y_Position,x
  cmp Player_Y_Position
  bcc Done
  lda #1
  sta Player_Y_Speed
Done:
  pla
  plp
  rts
.endproc

; C=1 only for a new platforming profile/alternate. Vic is handled separately.
.proc X5BounceProfile
  lda SelectedCharacter
  cmp #4
  bne Cv3
  lda Z2Variant
  beq No
  sec
  rts
Cv3:
  cmp #5
  bne NewFamily
  lda Cv3Variant
  beq No
  cmp #4
  bcs No
  sec
  rts
NewFamily:
  cmp #13
  bcc No
  cmp #20
  bcs No
  cmp #18
  beq No
  sec
  rts
No:
  clc
  rts
.endproc

.proc X5SpringDispatch
  php
  pha
  jsr X5BounceProfile
  bcs New
  lda SelectedCharacter
  cmp #18
  beq Flying
  cmp #20
  bcs Return
  pla
  plp
  farcall MegaManSpringVelocityModes,jmp
New:
  phx
  phy
  farcall MarioSourceSpring
  jsr X5PublishImpulse
  ply
  plx
Return:
  pla
  plp
  rts
Flying:
  ; Gradius movement owns flight; do not index a platforming spring table.
  lda #0
  sta Player_Y_Speed
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  jmp Return
.endproc

.proc X5StompDispatch
  php
  pha
  jsr X5BounceProfile
  bcs New
  lda SelectedCharacter
  cmp #18
  beq Flying
  cmp #20
  bcs Return
  pla
  plp
  farcall MegaManBounceVelocityModes,jmp
New:
  phx
  phy
  farcall MarioSourceBounce
  lda #1
  sta Player_State
  jsr X5PublishImpulse
  ply
  plx
Return:
  pla
  plp
  rts
Flying:
  lda #0
  sta Player_Y_Speed
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  jmp Return
.endproc

.proc X5PublishImpulse
  lda SelectedCharacter
  cmp #4
  jeq Zelda
  cmp #5
  jeq Cv3
  cmp #13
  jeq Kirby
  cmp #14
  jeq Chip
  cmp #16
  jeq Mike
  cmp #17
  jeq Mario3
  cmp #19
  jeq Turtle
  rts                            ; Mac uses the shared MarioSource state.
Zelda:
  lda MmVY+2
  sta Z2NativeVY
  lda #0
  sta Z2NativeGravityFraction
  lda #1
  sta Z2NativeAir
  rts
Kirby:
  lda #0
  sta KbFloat
  sta KbFloatAge
  sta KbJumpPhase
  rts
Cv3:
  jsr X5RememberImpulse
  lda MmVY+1
  sta Cv3VyLo
  lda MmVY+2
  sta Cv3VyHi
  lda #0
  sta Cv3JumpIndex               ; Stable original terminal row while overridden.
  sta Cv3JumpDelay
  lda #1
  sta Cv3JumpActive
  sta Cv3JumpPhase
  lda Cv3VxHi
  sta Cv3AirVX
  rts
Chip:
  jsr X5RememberImpulse
  ; Rescue Rangers uses upward-positive Q8.8; retain real input/cooldowns.
  lda #0
  sec
  sbc MmVY+1
  sta CdVYLo
  lda #0
  sbc MmVY+2
  sta CdVYHi
  lda MmVY+2
  sta CdLastExportVY
  rts
Mike:
  jsr X5RememberImpulse
  lda #0
  sta JnJump                     ; Its existing ballistic/fall path accepts VY<0.
  sta JnFallFrac
  lda MmVY+2
  sta JnVY
  rts
Mario3:
  ; Signed Q4 fits [-8,+7.9375]. Never import native -12 (wraps to+4).
  lda MmVY+1
  .repeat 4
    lsr
  .endrepeat
  sta M3Scratch
  lda MmVY+2
  .repeat 4
    asl
  .endrepeat
  ora M3Scratch
  sta M3Native::Player_YVel
  lda MmVY+2
  sta M3LastVY
  lda #1
  sta M3Native::Player_InAir
  rts
Turtle:
  lda MmVY+1
  sta TnVYLo
  lda MmVY+2
  sta TnVYHi
  sta TnLastVy
  lda #8
  sta TnJumpStage
  rts
.endproc

.proc X5RememberImpulse
  lda SelectedCharacter
  sta X5BounceOwner
  lda MmVY+1
  sta X5BounceLo
  lda MmVY+2
  sta X5BounceHi
  lda AreaPointer
  sta X5BounceArea
  lda NumberofLives
  sta X5BounceLife
  lda WorldNumber
  asl
  asl
  ora LevelNumber
  sta X5BounceKey
  rts
.endproc
.proc X5ClearImpulse
  lda #0
  ldx #5
Loop:
  sta X5BounceOwner,x
  dex
  bpl Loop
  rts
.endproc

; Existing resident UI farcall retarget only. Clear stale ownership even while
; the owner's movement is not running. Never write an inactive profile overlay.
.proc X5BounceUiDispatch
  php
  pha
  phx
  phy
  jsr X5BounceLifecycle
  ply
  plx
  pla
  plp
::X5OwnUiCall:
  jmp X5OwnInventoryUi
  .res 15,$ea
.endproc
.proc X5BounceLifecycle
  lda X5BounceOwner
  jeq Done
  cmp SelectedCharacter
  jne Clear
  cmp #5
  bne :+
  lda Cv3Variant
  jeq Clear
  cmp #4
  jcs Clear
  :
  lda OperMode
  cmp #1
  jne Clear
  lda OperMode_Task
  cmp #3
  jne Clear
  lda GameEngineSubroutine
  cmp #8
  jne Clear
  lda MmDeathFlag
  jne Clear
  lda AreaPointer
  cmp X5BounceArea
  jne Clear
  lda NumberofLives
  cmp X5BounceLife
  jne Clear
  lda WorldNumber
  asl
  asl
  ora LevelNumber
  cmp X5BounceKey
  jne Clear
  lda Player_State
  jeq Clear
  lda Player_Y_Speed
  jmi Done
  lda X5BounceHi
  jpl Done
  ; Native ceiling owns a nonnegative speed while our launch was still rising.
  lda X5BounceOwner
  cmp #5
  beq Cv3Ceiling
  cmp #14
  beq ChipCeiling
  cmp #16
  bne Clear
  lda Player_Y_Speed
  sta JnVY
  lda #0
  sta JnJump
  sta JnFallFrac
  jmp Clear
ChipCeiling:
  lda CdVYHi
  bmi Clear                      ; Ordinary post-apex fall; do not reverse it.
  lda #0
  sta CdVYLo
  sta CdVYHi
  jmp Clear
Cv3Ceiling:
  lda #1
  sta Cv3JumpPhase
  sta Cv3JumpActive
  lda #12
  ldx Cv3Variant
  cpx #1
  bne :+
    lda #56
  :
  sta Cv3JumpIndex
  lda #0
  sta Cv3JumpDelay
  sta Cv3VyLo
  sta Cv3VyHi
Clear:
  jmp X5ClearImpulse
Done:
  rts
.endproc

; Existing player movement farcall retarget. Mike's own jump table must not
; overwrite a spring launch, and a native ceiling may stop its ballistic path.
.proc X5BounceMovementDispatch
  lda SelectedCharacter
  cmp #16
  bne Native
  lda X5BounceOwner
  cmp #16
  bne Native
  lda Player_State
  beq Native
  lda JnVY
  bne Sync
  lda Player_Y_HighPos
  cmp #1
  bne Sync
  lda Player_Y_Position
  cmp #16
  bne Sync
  lda Player_Y_Speed
  bpl Sync
  ; JnMovement's top clamp zeroes ownVY after its last native export. Do not
  ; re-import that stale negative export and pin him to the HUD forever.
  lda #0
  sta Player_Y_Speed
  sta MmVY+2
  jsr X5ClearImpulse
  jmp Native
Sync:
  lda Player_Y_Speed
  cmp JnVY
  beq Native
  sta JnVY
  lda #0
  sta JnJump
  sta JnFallFrac
Native:
  jmp X5NewMovementFinish
  .res 15,$ea
.endproc

; Replace only CV3's existing18B Horizontal farcall. Its original per-jump
; trajectory still runs safely, but this temporary SMB impulse owns VY until
; ground/ceiling/life/area cleanup. Source input/attack timers remain untouched.
.proc X5BounceCv3Horizontal
  php
  pha
  phx
  phy
  lda SelectedCharacter
  cmp #5
  bne Native
  lda X5BounceOwner
  cmp #5
  bne Native
  lda Cv3Temp
  beq Ground
  clc
  lda X5BounceLo
  adc #$40                      ; Explicit SMB ballistic gravity1/4px/update².
  sta X5BounceLo
  lda X5BounceHi
  adc #0
  sta X5BounceHi
  bmi Copy
  ldy #6
  ldx Cv3Variant
  cpx #1
  bne :+
    iny
  :
  sty Cv3Temp2
  cmp Cv3Temp2
  bcc Copy
  sty X5BounceHi
  lda #0
  sta X5BounceLo
Copy:
  lda X5BounceLo
  sta Cv3VyLo
  sta MmVY+1
  lda X5BounceHi
  sta Cv3VyHi
  sta MmVY+2
  lda #0
  sta MmVY
  jmp Native
Ground:
  jsr X5ClearImpulse
Native:
  ply
  plx
  pla
  plp
  jmp X5Cv3HorizontalFinish
  .res 15,$ea
.endproc

; This affects only the old short-jump release check, not real input memory.
; It lets a physical SMB spring/stomp finish while A is actually released.
.proc X5ChipReleaseInput
  lda SelectedCharacter
  cmp #14
  bne Native
  lda X5BounceOwner
  cmp #14
  bne Native
  lda #A_Button
  rts
Native:
  lda SavedJoypadBits
  and #A_Button
  rts
.endproc
.popseg

; Complete ordinary CV3 camera publication in cold bank86. The old wrapper
; remains exactly its old size; no resident or existing entry address moves.
.pushseg
.segment "X5_BOUNCE"
.proc X5Cv3HorizontalFinish
  ; Explicit SMB accommodation: retain source table index/cadence/art, but
  ; double ordinary Sypha/Alucard trajectory displacement. The original
  ; source kernel and tables are unchanged. Bounce, bat/climb and the full
  ; recoil sequence retain their existing independently owned velocities.
  php
  pha
  phx
  lda SelectedCharacter
  cmp #5
  bne Restore
  lda Cv3Variant
  cmp #2
  bcc Restore
  cmp #4
  bcs Restore
  lda X5Cv3PriorHurt
  sta Cv3Temp3
  lda Cv3HurtAge
  sta X5Cv3PriorHurt
  ora Cv3Temp3
  bne Restore
  lda Cv3Temp
  beq Restore
  lda Cv3Bat
  ora Cv3Climb
  bne Restore
  lda X5BounceOwner
  cmp #5
  beq Restore
  asl Cv3VxLo
  rol Cv3VxHi
  lda Cv3VxLo
  sta MmVX+1
  lda Cv3VxHi
  sta MmVX+2
  lda Cv3Variant
  cmp #2
  beq Restore                 ; Sypha owns a smooth fractional traversal arc.
  asl Cv3VyLo
  rol Cv3VyHi
  lda Cv3VyLo
  sta MmVY+1
  lda Cv3VyHi
  sta MmVY+2
Restore:
  plx
  pla
  plp
  farcall MegaManMovement::Horizontal
  php
  pha
  lda SelectedCharacter
  cmp #5
  bne Done
  lda Cv3Variant
  beq Done
  cmp #4
  bcs Done
  lda MmOldX
  sec
  sbc ScreenLeft_X_Pos
  sta Player_Pos_ForScroll
Done:
  pla
  plp
  rts
.endproc
.popseg

; New platform families publish their actual relative position before the
; native ScrollHandler consumes it. Preserve the movement return ABI.
.pushseg
.segment "X5_BOUNCE"
.proc X5NewMovementFinish
  pha
  lda Player_X_Position
  sta X5CameraBefore
  pla
::X5OwnMovementCall:
  jsr X5OwnMovement
  .res 15,$ea
  php
  pha
  lda SelectedCharacter
  cmp #13
  bcc Done
  cmp #20
  bcs Done
  cmp #18
  beq CurrentPosition          ; Vic advances his own autoscrolling camera.
  ; Match native Mario's pre-step camera cache. A post-step cache alternates
  ; across the follow threshold, producing uneven camera steps at steady speed.
  lda X5CameraBefore
  jmp Relative
CurrentPosition:
  lda Player_X_Position
Relative:
  sec
  sbc ScreenLeft_X_Pos
  sta Player_Pos_ForScroll
Done:
  pla
  plp
  rts
.endproc
.proc X5Cv3IcePlatform
  ; The72px trajectory can descend10/12px per update. Keep the genuine
  ; frozen-enemy support response but admit a crossed8px top surface using
  ; the player's already sampled pre-move foot, instead of treating it as
  ; a side collision after tunnelling through its old current-only band.
  lda SelectedCharacter
  cmp #5
  bne Native
  lda Cv3Variant
  cmp #2
  bne Native
  lda Player_Y_HighPos
  cmp #1
  bne Native
  lda Player_Y_Speed
  bmi Native
  lda Enemy_Y_HighPos,x
  cmp #1
  bne Native
  lda Enemy_Y_Position,x
  clc
  adc #8
  sta AvTmp2
  lda Cv3OldFoot
  cmp AvTmp2
  bcc Cross
  bne Native
Cross:
  lda Player_Y_Position
  clc
  adc #32
  cmp AvTmp2
  bcc Native
  lda Player_X_Position
  sec
  sbc Enemy_X_Position,x
  sta AvTmp
  lda Player_PageLoc
  sbc Enemy_PageLoc,x
  sta Cv3Temp3
  lda AvTmp
  clc
  adc #15
  sta AvTmp
  lda Cv3Temp3
  adc #0
  bne Native
  lda AvTmp
  cmp #31
  bcs Native
  lda AvTmp2
  sec
  sbc #32
  sta Player_Y_Position
Native:
  farcall RemainingIcePlatform,jmp
.endproc
.popseg

; Cold19B tail in Chip's existing motion bank; all old profile PCs stay fixed.
.pushseg
.segment "CD_BOUNCE_BRIDGE"
.proc X5ChipReleaseBridge
  farcall X5ChipReleaseInput
  rts
.endproc
.assert *-X5ChipReleaseBridge=19,error,"Approved cold19B release trampoline"
.popseg

; The spring/stomp ownership lifecycle still runs at the original outer
; entry. Only skip unrelated alternate-specific UI dispatch for profiles
; whose original path ends at InventoryUiTick. Mac15 and vehicles18 keep
; their own HUD handlers; every other identity retains the old entry.
.pushseg
.segment "X5_BOUNCE"
.proc X5OwnInventoryUi
 php
 pha
 phx
 phy
 jsr X5NativeStatusFlush
 ply
 ldx SelectedCharacter
 cpx #13
 bcc Legacy
 cpx #15
 beq Legacy
 cpx #18
 beq Legacy
 cpx #20
 bcs Legacy
 plx
 pla
 plp
 jmp X5NativeInventoryUiLeaf
; The SMB3 P-bar owns its font throughout the update, including a lag NMI
; between this generic input leaf and M3Hud. Other native leaves still hide
; the legacy inventory font. Reuse this previously unreachable15-byte tail.
HudRead:
 cpx #17
 bne OrdinaryHud
 lda #0
 clc
 rts
OrdinaryHud:
 lda InvHudActive
 clc
 rts
 .res 2,$ea
Legacy:
 plx
 pla
 plp
 farcall RlUiDispatch,jmp
.endproc
.export X5OwnInventoryUi
.popseg

; Preserve the surrounding bounce lifecycle and pre-step camera sample.
; Avoid only the redundant trip through the Little Mac exact-ID gate.
.pushseg
.segment "X5_BOUNCE"
.proc X5OwnMovement
 php
 pha
 lda SelectedCharacter
 cmp #19
 bne Legacy
 pla
 plp
 farcall TnMovement,jmp
Legacy:
 pla
 plp
 farcall LmMovementGate,jmp
.endproc
.export X5OwnMovement
.popseg

; Both native numeric printers share the84-byte queue with terrain and
; character HUDs. A blocked field is coalesced to its latest native digits.
.pushseg
.segment "X5_BOUNCE"
.proc X5NativeStatusReserve
  ; Input Y=2*slot, with the caller's slot still on its own stack.
  ; Keep Y and all R0..R7 intact: R0 owns the second packed request.
  lda OperMode
  cmp #1
  bne Fits
  tya
  lsr
  tax
  lda SelectedCharacter
  cmp #4
  bne Capacity
  lda Z2Variant
  beq Capacity
  cpx #1
  bcc Capacity
  cpx #5
  bcc Suppressed              ; score and coins overlap the spell/EXP row
Capacity:
  lda VRAM_Buffer1_Offset
  clc
  adc Lengths,x
  bcs Deferred
  cmp #81                    ; last terminator <=83, before Buffer2 offset
  bcc Fits
Deferred:
  lda Bits,x
  ora NativeStatusPending
  sta NativeStatusPending
Suppressed:
  lda #0
  rts
Fits:
  lda #1
  rts
Lengths:.byte 6,6,6,2,2,3
Bits:.byte 1,2,4,8,16,32
.endproc

.proc X5NativeStatusFlush
  lda OperMode
  cmp #1
  bne Clear
  lda NativeStatusPending
  beq Done
  lda OperMode_Task
  cmp #3
  bne Done
  lda GameEngineSubroutine
  cmp #8
  bne Done
  lda GamePauseStatus
  and #1
  bne Done
  lda R0
  pha
  lda #0
  sta NativeStatusCursor
Next:
  ldx NativeStatusCursor
  lda X5NativeStatusReserve::Bits,x
  and NativeStatusPending
  beq Advance
  eor NativeStatusPending
  sta NativeStatusPending
  txa
  sec
  sbc #1
  and #$0f
  ora #$50                   ; high5 increments to6: truly invalid slot
  farcall HudUpdateNumberLocal
Advance:
  inc NativeStatusCursor
  lda NativeStatusCursor
  cmp #6
  bcc Next
  pla
  sta R0
Done:
  rts
Clear:
  lda #0
  sta NativeStatusPending
  rts
.endproc
.popseg

.pushseg
.segment "X5_BOUNCE"
.proc X5NativeInventoryUiLeaf
  lda GuestHurtTicks
  beq :+
    lda #0
    sta InvFresh
    lda GuestHurtKind
    cmp #CHARACTER_LINK
    beq HurtPhysicalHistory
    cmp #CHARACTER_SIMON
    beq HurtPhysicalHistory
    cmp #CHARACTER_RYU
    beq HurtPhysicalHistory
    lda #0
    sta InvPrevious
    rts                       ; Source disableInput includes weapon selection.
HurtPhysicalHistory:
    lda SavedJoypad1Bits
    sta InvPrevious            ; Held Select is no synthetic press on recovery.
    rts
  :
  lda SavedJoypad1Bits
  eor InvPrevious
  and SavedJoypad1Bits
  sta InvFresh
  lda SavedJoypad1Bits
  sta InvPrevious
  ldx SelectedCharacter
  clc
  jsr X5OwnInventoryUi::HudRead
  beq Done
  lda #0
  sta InvHudActive
  inc ReloadCHRBank
  inc InvDirty
  lda #0
Done:rts
.endproc

.popseg
