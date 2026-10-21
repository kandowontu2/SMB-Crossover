; Source-specific Sophia motion. Velocities use the shared Q8.16 integrator.
.pushseg
.segment "EXPANDED_EX"
.proc LuigiDeathMotion
  lda MmDeathPit
  jne Done
  lda MmDeathAge
  cmp #15                       ; 250ms freeze, then the native source arc.
  jcc Done
  bne Move
  lda #0
  sta MmVX
  sta MmVX+1
  sta MmVX+2
  sta MmVY
  lda #$d5
  sta MmVY+1
  lda #$fb                      ; -500 /120.
  sta MmVY+2
  lda #1
  sta Player_State
Move:
  lda #0
  sta MmFrictionYActive
  sta RgFallCap
  lda #$80
  sta RgFallCap+1
  lda #4                        ; DIE_VY_MAX_PSV=540 /120.
  sta RgFallCap+2
  lda #$ab
  sta XgGravity
  lda #$2a                      ; DIE_GRAVITY=1200 /7200.
  sta XgGravity+1
  farcall MegaManMovement::Horizontal
Done:
  rts
.endproc
.proc RyuWallJump
  lda SavedJoypadBits
  and #Down_Dir
  bne Drop
  lda PlayerFacingDir
  eor #3
  and SavedJoypadBits
  and #3
  bne Away
  ; Near the top of a wall the source permits a higher jump onto the ledge.
  lda Player_X_Position
  clc
  adc #21
  sta RgTempX
  lda Player_PageLoc
  adc #0
  sta RgTempPage
  lda PlayerFacingDir
  cmp #1
  beq :+
    sec
    lda RgTempX
    sbc #26
    sta RgTempX
    lda RgTempPage
    sbc #0
    sta RgTempPage
  :
  lda Player_Y_Position
  clc
  adc #3
  sta RgTempY
  jsr ExpandedMapCell
  bcs NoJump
  lda #$ab                       ; CLIMB_TOP_JUMP_PWR=430 /120.
  sta MmVY
  lda #$6a
  sta MmVY+1
  lda #$fc
  sta MmVY+2
  lda #15                        ; CANCEL_GRAPPLE_TMR=250ms.
  bne Launch
Away:
  lda PlayerFacingDir
  eor #3
  sta PlayerFacingDir
  lda #0
  sta MmVY
  lda #$80
  sta MmVY+1
  lda #$fd                       ; CLIMB_JUMP_PWR=300 /120.
  sta MmVY+2
  lda #12
Launch:
  sta XgWallLock
  lda #1
  sta XgJumpUsed                   ; Source detachFromWall sets jumped=true.
  lda #0
  sta XgWall
  sec
  rts
Drop:
  lda #1
  sta XgJumpUsed
  lda #0
  sta XgWall
  lda #15
  sta XgWallLock
NoJump:
  clc
  rts
.endproc
.proc SophiaAbilities
  ; Sophia owns these otherwise dormant Ryu cache cells for this update.
  lda #0
  sta RyWallSupported
  lda Player_State
  sta RyWallWasGround          ; Source pre-integration onGround cache.
  bne AirFlag
  sta RgDoubleJump
AirFlag:
  lda XgRise
  beq Cache
  lda #1
  sta RgDoubleJump
Cache:
  lda Player_X_Position
  sta RyWallOldX
  lda Player_PageLoc
  sta RyWallOldPage
  lda MmXFraction
  sta RyWallOldXFine
  lda MmXFraction+1
  sta RyWallOldXFrac
  lda Player_Y_Position
  sta RyWallOldY
  lda MmYFraction
  sta RyWallOldYFine
  lda MmYFraction+1
  sta RyWallOldYFrac
  lda #1
  sta RyWallSupported
  lda XgCeiling
  ora XgWall
  jne Done
  lda XgHoverActive
  jeq Recharge
  lda Player_State
  jeq Recharge
  lda MmUnderwater
  jne Recharge
  lda XgHover
  jeq Recharge
  inc XgHoverDrain
  lda XgHoverDrain
  cmp #18                       ; 300ms per energy unit.
  bcc Boost
  lda #0
  sta XgHoverDrain
  lda StarInvincibleTimer
  bne Boost
  dec XgHover
Boost:
  lda #0
  sta XgGravity
  sta XgGravity+1
  sta MmFrictionYActive
  sec
  lda MmVY
  sbc #$55                      ; HOVER_BOOST_POWER=40 Flash px/s per update.
  sta MmVY
  lda MmVY+1
  sbc #$55
  sta MmVY+1
  lda MmVY+2
  sbc #0
  sta MmVY+2
  jpl Done
  cmp #$ff
  bcc ClampBoost
  lda MmVY+1
  cmp #$2a
  jcs Done
ClampBoost:
  lda #$ab                      ; -100/120 maximum hover climb speed.
  sta MmVY
  lda #$2a
  sta MmVY+1
  lda #$ff
  sta MmVY+2
  rts
Recharge:
  lda #0
  sta XgHoverActive
  lda XgHover
  cmp #8
  bcs Rise
  inc XgHoverRegen
  lda XgHoverRegen
  cmp #120                      ; 2000ms per energy unit, ground or air.
  bcc Rise
  lda #0
  sta XgHoverRegen
  inc XgHover
Rise:
  lda XgRise
  jeq FreeMotion
  lda #0
  sta XgGravity
  sta XgGravity+1
  sta MmFrictionYActive
  lda XgJumpStart
  sec
  sbc Player_Y_Position
  cmp XgJumpHeight
  jcc Done
  lda XgJumpStart
  sec
  sbc XgJumpHeight
  sta Player_Y_Position
  lda #0
  sta XgRise
  ; Source turns gravity back on without zeroing the upward velocity.
  lda MmUnderwater
  jne Water
  lda #$55
  sta XgGravity
  lda #$25
  sta XgGravity+1
FreeMotion:
  lda MmUnderwater
  jne Water
  lda MmVY+2
  jpl Done
  farcall MegaManMovement::NegateY
  jsr LoadY
  lda MmJumpReleased
  bne :+
    jsr SophiaHeldFriction
    jmp DryStore
  :
  jsr SophiaReleasedFriction
DryStore:
  jsr StoreY
  farcall MegaManMovement::NegateY
Done:
  rts
Water:
  lda #0
  sta XgGravity
  sta XgGravity+1
  sta MmFrictionYActive
  lda Player_State
  jeq Done
  lda SavedJoypadBits
  and #Up_Dir | Down_Dir
  cmp #Up_Dir
  jeq WaterUp
  cmp #Down_Dir
  jeq WaterDown
  lda MmVY+2
  sta MmSign
  bpl :+
    farcall MegaManMovement::NegateY
  :
  jsr LoadY
  lda MmSign
  bpl :+
    jsr SophiaWaterUpFriction
    jmp WaterStore
  :
  farcall MmFrictionX            ; FY_WATER_PSV = 1e-7.
WaterStore:
  jsr StoreY
  lda MmSign
  bpl Drift
  farcall MegaManMovement::NegateY
Drift:
  clc
  lda MmYFraction+1
  adc #$80                      ; WATER_FALL_SPEED = 1 Flash pixel/update.
  sta MmYFraction+1
  lda Player_Y_Position
  adc #0
  sta Player_Y_Position
  lda Player_Y_HighPos
  adc #0
  sta Player_Y_HighPos
  jmp WaterCap
WaterUp:
  sec
  lda MmVY+1
  sbc #$20                      ; AY_WATER = 900 /7200.
  sta MmVY+1
  lda MmVY+2
  sbc #0
  sta MmVY+2
  jmp WaterCap
WaterDown:
  clc
  lda MmVY+1
  adc #$20
  sta MmVY+1
  lda MmVY+2
  adc #0
  sta MmVY+2
WaterCap:
  lda MmVY+2
  sta MmSign
  bpl :+
    farcall MegaManMovement::NegateY
  :
  lda MmVY+2
  cmp #1
  bcc WaterSign
  bne ClampWater
  lda MmVY+1
  cmp #$95
  bcc WaterSign
ClampWater:
  lda #$55                      ; VY_MAX_WATER = 190 /120.
  sta MmVY
  lda #$95
  sta MmVY+1
  lda #1
  sta MmVY+2
WaterSign:
  lda MmSign
  jpl Done
  farcall MegaManMovement::NegateY
  rts
LoadY:
  lda MmVY
  sta MmMul
  lda MmVY+1
  sta MmMul+1
  lda MmVY+2
  sta MmMul+2
  rts
StoreY:
  lda MmMul
  sta MmVY
  lda MmMul+1
  sta MmVY+1
  lda MmMul+2
  sta MmVY+2
  rts
.endproc
MmMultiplyRoutine SophiaReleasedFriction, 42968
MmMultiplyRoutine SophiaHeldFriction, 64783
MmMultiplyRoutine SophiaWaterUpFriction, 60694
.popseg
