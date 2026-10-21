; Pinned Crossover2.02 Link/Simon/Ryu takeDamageStart/End. The common injury
; owner dispatches only active source hurt profiles; native/no-hurt paths stay
; outside this bank. All exported helpers preserve X/Y/ObjectOffset.
; Units: world coordinates in NES pixels, velocities signed Q8.16 per update.
.pushseg
.segment "SPECIAL_ROSTER"

; Capture before InventoryHurt removes active upgrades and the common start
; clears friction. A is the context token, carried on the caller's stack.
.proc LsrHurtPrepare
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne Ryu
    lda LsrHurtFlags
    and #8                       ; Source jumped survives water's native state2.
    sta RgTemp
    lda Player_State
    bne :+
      sta RgTemp
    :
    lda MmFrictionYActive
    bne LinkToken
    ; BTN_MNGR.relPlyrBtns also calls Link.relJmpBtn when A was held.
    ; That arms retained friction even though hurt bypasses checkState.
    lda A_B_Buttons
    and #A_Button
    beq LinkToken
    lda MmJumpReleased
    bne ZeroLink
    lda #1
LinkToken:
    and #1
    ora RgTemp
    rts
ZeroLink:
    lda #0
    beq LinkToken
Ryu:
  cmp #CHARACTER_RYU
  bne Zero
    lda #0
    sta RgTemp
    lda Player_State
    beq RyuSlash
    lda XgWall
    bne RyuJumped                 ; damageBoost calls detachFromWall first.
    lda XgJumpUsed
    beq RyuSlash
RyuJumped:
    lda #8
    sta RgTemp
RyuSlash:
    lda AvSlash                  ; Source Jump Slash survives takeDamageStart.
    and #1
    ora RgTemp
    rts
Zero:
  lda #0
  rts
.endproc

.proc LsrHurtStart
  sta LsrHurtFlags               ; PHX/PHY are TXA/TYA macros on the6502.
  phx
  phy
  lda LsrHurtFlags
  pha                            ; Context does not consume another SRAM byte.
  and #8                         ; The token's jump bit is not a friction/slash.
  sta LsrHurtFlags
  lda #0
  sta RgCrouch
  sta CrouchingFlag
  sta MmSliding
  sta MmOnVine
  sta MmLastXSpeed
  sta RgAttack
  sta RgAttackAge
  sta RgAttackKind
  sta RgThrust
  sta RgThrustReset
  sta LinkThrustPrev
  sta LinkThrustNow
  sta LinkThrustReceipt
  sta RgShootPose
  sta PlayerSize
  ldx ObjectOffset
  ; nx is the common center coordinate: equal origins recoil right. Facing
  ; is toward the attacker, independently of the previous movement/facing.
  ldy #1                         ; Recoil right; contacted wall mask1.
  lda Enemy_PageLoc,x
  cmp Player_PageLoc
  bcc Direction
  bne RecoilLeft
  lda Enemy_X_Position,x
  cmp Player_X_Position
  bcc Direction
  beq Direction
RecoilLeft:
  iny
Direction:
  tya
  ora LsrHurtFlags
  sta LsrHurtFlags
  tya
  eor #3
  sta PlayerFacingDir
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  jeq Link
  pla
  and #1
  ldx SelectedCharacter
  cpx #CHARACTER_RYU
  bne Simon
  sta AvSlash
  lda #0
  sta XgWall
  jmp RyuPlatformInjuryGate
PlatformResume:
  sta RyWallResolved
  sta XgWallContact
  sta XgWallLock
  sta XgCeiling
  sta XgRise
  lda #$ab                       ; -385 /120, exact rounded negative Q16.
  sta MmVY
  lda #$ca
  sta MmVY+1
  lda #$fc
  sta MmVY+2
  lda #AV_SFX_RYUTAKEDAMAGE
  bne Hop
Simon:
  lda LsrHurtFlags
  ora #8                         ; Simon.damageBoost always sets jumped=true.
  sta LsrHurtFlags
  lda #0
  sta MmVY
  lda #$80                       ; -300 /120.
  sta MmVY+1
  lda #$fd
  sta MmVY+2
  lda #AV_SFX_SIMONTAKEDAMAGE
Hop:
  sta AvAudioRequest
  lda MmVY+2
  sta Player_Y_Speed
  lda #1
  sta GuestHurtTicks              ; Landing-controlled lock, not a fixed timer.
  sta Player_State
  lda #0
  sta MmVX
  lda #$40                       ; +150 /120, or its exact two's complement.
  sta MmVX+1
  lda #1
  sta MmVX+2
  cpy #1
  jeq Started
  lda #$c0
  sta MmVX+1
  lda #$fe
  sta MmVX+2
  jmp Started
Link:
  pla
  and #1
  beq NoFriction
  lda LsrHurtFlags
  ora #4
  sta LsrHurtFlags
  lda #1
  sta MmJumpReleased             ; Source relJmpBtn accompanies armed friction.
NoFriction:
  lda #72                        ;1200ms is fallback; checkState ends by distance.
  sta GuestHurtTicks
  lda MmXFraction
  sta LsrHurtEndX
  lda MmXFraction+1
  sta LsrHurtEndX+1
  cpy #1
  bne LinkLeft
  lda Player_X_Position
  clc
  adc #32                        ;64 Flashpx, retaining the exact fraction.
  sta LsrHurtEndX+2
  lda Player_PageLoc
  adc #0
  sta LsrHurtEndX+3
  lda #$ab
  sta MmVX
  lda #$2a
  sta MmVX+1
  lda #4
  sta MmVX+2
  bne LinkSound
LinkLeft:
  lda Player_X_Position
  sec
  sbc #32
  sta LsrHurtEndX+2
  lda Player_PageLoc
  sbc #0
  sta LsrHurtEndX+3
  lda #$55
  sta MmVX
  lda #$d5
  sta MmVX+1
  lda #$fb
  sta MmVX+2
LinkSound:
  lda #AV_SFX_LINKTAKEDAMAGE
  sta AvAudioRequest
Started:
  lda MmVX+1
  lsr
  lsr
  lsr
  lsr
  sta RgTemp
  lda MmVX+2
  asl
  asl
  asl
  asl
  ora RgTemp
  sta Player_X_Speed
  sta MmLastXSpeed
::LsrHurtStarted:
  ply
  plx
::LsrHurtStartReturned:
  rts
.endproc

; Source Link.checkState tests strict overshoot BEFORE movePlayer/gravity.
; Equality at the exact endpoint is still hurt for that update.
.proc LsrHurtTick
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  jne Locked
  dec GuestHurtTicks
  jeq Ended
  lda LsrHurtFlags
  and #1
  beq Left
  sec                            ; endpoint-current: borrow means strict >.
  lda LsrHurtEndX
  sbc MmXFraction
  lda LsrHurtEndX+1
  sbc MmXFraction+1
  lda LsrHurtEndX+2
  sbc Player_X_Position
  lda LsrHurtEndX+3
  sbc Player_PageLoc
  bcs Locked
  bcc Clamp
Left:
  sec                            ; current-endpoint: borrow means strict <.
  lda MmXFraction
  sbc LsrHurtEndX
  lda MmXFraction+1
  sbc LsrHurtEndX+1
  lda Player_X_Position
  sbc LsrHurtEndX+2
  lda Player_PageLoc
  sbc LsrHurtEndX+3
  bcs Locked
Clamp:
  lda LsrHurtEndX
  sta MmXFraction
  lda LsrHurtEndX+1
  sta MmXFraction+1
  lda LsrHurtEndX+2
  sta Player_X_Position
  lda LsrHurtEndX+3
  sta Player_PageLoc
Ended:
  sec
  rts
Locked:
  clc
  rts
.endproc

.proc LsrHurtMovement
  phx
  phy
  lda ObjectOffset
  pha
  lda #0
  sta MmFrictionYActive          ; Link saves this, but source hurt bypasses it.
  sta PlayerSize
  sta CrouchingFlag
  sta RgCrouch
  sta MmUnderwater
  lda Player_X_Position
  sta MmOldX
  lda Player_State
  bne Air
  lda #0                        ; Terrain stays live; integrate grounded X only.
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  sta MmYFraction
  sta MmYFraction+1
  beq Water
Air:
  lda Player_Y_Speed              ; Adopt actual native ceiling/landing stops.
  cmp MmVY+2
  beq Water
  sta MmVY+2
  lda #0
  sta MmVY
  sta MmVY+1
Water:
  jsr LsrHurtWater
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  jne OtherGravity
  lda #$ab                       ; Link terminal800/120; water-room500/120.
  sta RgFallCap
  lda #$aa
  sta RgFallCap+1
  lda #6
  sta RgFallCap+2
  lda SwimmingFlag
  beq GroundWater
  lda #$2a
  sta RgFallCap+1
  lda #4
  sta RgFallCap+2
GroundWater:
  lda MmUnderwater
  beq Integrate
  lda Player_State
  bne Integrate
  lda #0                         ; Common vxMaxGroundWater90 /120.
  sta MmVX
  lda #$c0
  sta MmVX+1
  lda #0
  sta MmVX+2
  lda LsrHurtFlags
  and #2
  beq Integrate
  lda #$40
  sta MmVX+1
  lda #$ff
  sta MmVX+2
  bne Integrate
OtherGravity:
  ; Simon's shared gravity dispatcher ignores XgGravity, and GuestFall
  ; branches straight to Vertical for Simon before reading RgFallCap.
  lda #$c7                       ; Ryu1400/7200, water500/7200.
  sta XgGravity
  lda #$31
  ldx MmUnderwater
  beq :+
    lda #$11
  :
  sta XgGravity+1
  lda #$55
  sta RgFallCap
  lda #$d5
  sta RgFallCap+1
  lda #5
  sta RgFallCap+2
Integrate:
  ; Prepared hurt geometry must not be replaced by normal/state-dependent
  ; water boxes. Shared IntegrateX still performs source gravity/fall caps.
  farcall MegaManMovement::IntegrateX
::LsrHurtIntegrated:
  pla
  sta ObjectOffset
  ply
  plx
::LsrHurtMovementReturned:
  rts
.endproc

; HRect is fixed at15NESpx for Link,25 for Simon/Ryu. Source condition is
; strictly hTop>waterTop, including the retained Q16 fractional coordinate.
.proc LsrHurtWater
  lda SwimmingFlag
  beq Done
  lda Player_Y_HighPos
  bmi Done
  cmp #1
  bcc Done
  bne Wet
  ldx #25
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne :+
    ldx #15
  :
  txa
  cmp Player_Y_Position
  bcc Wet
  bne Done
  lda MmYFraction
  ora MmYFraction+1
  beq Done
Wet:
  inc MmUnderwater
Done:
  rts
.endproc

; Runs after real terrain/platform collision, before enemy contact. Link only
; ends on the wall matching recoil; Simon/Ryu end on actual support, including
; platforms. A native opposite-side wall bit never cancels Link's recoil.
.proc LsrHurtAfterCollision
  ; Character.groundAbove assigns100Flashpx/s only while jumped=true.
  ; Native NYSpd reports1; translate that real ceiling receipt after collision
  ; so the following source update does not inherit a fabricated1px velocity.
  lda MmVY+2
  bpl Sides
  lda Player_Y_Speed
  cmp #1
  bne Sides
  lda #Sfx_Bump                   ; Character.groundAbove's common ceiling cue.
  ora Square1SoundQueue
  sta Square1SoundQueue
  lda LsrHurtFlags
  and #8
  beq RetainY
  lda #$55                       ;100 /120, rounded signed Q16.
  sta MmVY
  lda #$d5
  sta MmVY+1
  lda #0
  sta MmVY+2
RetainY:
  lda MmVY+2
  sta Player_Y_Speed
Sides:
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne Landing
  lda LsrHurtFlags
  and #3
  and Player_CollisionBits
  bne Locked
  jsr ZeroX
  jmp Ended
Locked:
  clc
  rts
Landing:
  lda LsrHurtFlags
  and #3
  and Player_CollisionBits
  bne CheckGround
  jsr ZeroX                      ; Character.groundOnSide stops into-wall vx.
CheckGround:
  lda Player_State
  bne Locked
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  bne Ended
  lda #0
  sta AvSlash
  sta AvFlip
  sta AvFlipClock
  sta RgAttack
  sta RgAttackAge
  sta RgShootPose
  sta XgWall
  sta XgWallContact
  sta XgJumpUsed
  lda #AV_SFX_RYUJUMP             ; Source landOnGround always plays this cue.
  sta AvAudioRequest
Ended:
  sec
  rts
ZeroX:
  lda #0
  sta MmVX
  sta MmVX+1
  sta MmVX+2
  sta Player_X_Speed
  sta MmLastXSpeed
  rts
.endproc

.proc LsrHurtEnd
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne Done
  lda LsrHurtFlags
  and #4
  lsr
  lsr
  sta MmFrictionYActive          ; Resume retained released-jump friction.
Done:
  rts
.endproc

; Common injury owner advances GuestFlickerPhase modulo6 once per unpaused
; logic update for Link. Each two-update step is the source30Hz flash timer.
; Flash.flashCtr starts1,2,0, so palette output rows are2,3,1. Only Link's
; private body colors are replaced; sprite2/3/world palettes stay untouched.
.proc LsrHurtPalette
  phx
  phy
  lda GuestFlickerPhase
  lsr
  sta RgTemp
  asl
  clc
  adc RgTemp
  tay
  ldx VRAM_Buffer1_Offset
  cpx #$40
  bcs Done
  lda #$3f
  sta VRAM_Buffer1,x
  lda #$11
  sta VRAM_Buffer1+1,x
  lda #3
  sta VRAM_Buffer1+2,x
  lda Colors,y
  sta VRAM_Buffer1+3,x
  lda Colors+1,y
  sta VRAM_Buffer1+4,x
  lda Colors+2,y
  sta VRAM_Buffer1+5,x
  txa
  clc
  adc #6
  tax
  stx VRAM_Buffer1_Offset
  lda #0
  sta VRAM_Buffer1,x
Done:
  ply
  plx
  rts
Colors:
  ; Raw palette PNG row2, x51..53 /75..77 /27..29. NES colors use the
  ; same closest-color convention as the packed body; phase is quantized
  ; to logic updates (global Flash-timer phase is not a per-hit reset).
  .byte $16,$30,$27, $01,$30,$21, $30,$16,$0c
.endproc
.popseg
