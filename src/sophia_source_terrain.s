; Normal unrotated Sophia ground consumers. Source HRect113=19x15.5.
; The existing Ryu prior-position cache is character-owned: Sophia publishes
; it before integration; every Ryu consumer is SelectedCharacter-gated.
; Corner calcAxis order, complete foot span and rotated anchors remain separate.
.pushseg
.segment "SOPHIA_TERRAIN_COLD"
SophiaSourceTerrainStart:
.proc SophiaTerrainValid
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne No
CharacterKnown:
  lda OperMode
  cmp #1
  bne No
  lda GameEngineSubroutine
  cmp #8
  bne No
  lda Player_State
  cmp #3
  bcs No
  lda XgWall
  ora XgCeiling
  ora MmDeathFlag
  ora GuestHurtTicks
  ora GuestPowerupActive
  bne No
  lda Player_Y_HighPos
  cmp #1
  bne No
  lda Player_Y_Position
  cmp #224
  bcs No
  sec
  rts
No:
  clc
  rts
.endproc

; RgTempX/Page/Y is an actual world point. Return the native tile/pointer ABI
; without temporarily relocating the player or publishing a fake body.
.proc SophiaTerrainQuery
  lda RgTempX
  sta R5
  ; Same native low/high table and final carry semantics, without
  ; packing page/column and immediately unpacking them in a callee.
  lda RgTempPage
  and #1
  tay
  lda BlockBufferAddr+2,y
  sta R7
  lda R5
  lsr
  lsr
  lsr
  lsr
  clc
  adc BlockBufferAddr,y
  sta R6
  lda RgTempY
  and #$f0
  sec
  sbc #$20
  sta R2
  tay
  lda (R6),y
  sta R3
  ldy SmTemp
  lda Player_X_Position
  and #15
  sta R4
  ldx #0
  lda R3
  rts
.endproc

; A=0 center,1 left,2 right. Inclusive closed source bounds are sampled with
; ceil(left)-1 and floor(right), with the center covering a possible third cell.
.proc SophiaTerrainXPoint
  cmp #1
  beq Left
  cmp #2
  beq Right
  lda #8
  bne Add
Left:
  lda Player_X_Position
  sec
  sbc #2
  sta RgTempX
  lda Player_PageLoc
  sbc #0
  sta RgTempPage
  lda MmXFraction+1
  cmp #$80
  bcc Done
  bne Extra
  lda MmXFraction
  beq Done
Extra:
  inc RgTempX
  bne Done
  inc RgTempPage
Done:
  rts
Right:
  lda MmXFraction+1
  cmp #$80
  lda #17
  bcc Add
  lda #18
Add:
  clc
  adc Player_X_Position
  sta RgTempX
  lda Player_PageLoc
  adc #0
  sta RgTempPage
  rts
.endproc

.proc SophiaPriorXOverlapsCell
  lda RgTempX
  and #$f0
  sta SmHeadX
  lda RyWallOldXFrac
  cmp #$80
  lda RyWallOldX
  adc #17
  sta SmTempX
  lda RyWallOldPage
  adc #0
  cmp RgTempPage
  bcc No
  bne Left
  lda SmTempX
  cmp SmHeadX
  bcc No
Left:
  lda RyWallOldX
  sta SmTempX
  lda RyWallOldPage
  sta SmTempPage
  lda RyWallOldXFrac
  cmp #$80
  bcc Minus
  bne Right
  lda RyWallOldXFine
  bne Right
Minus:
  sec
  lda SmTempX
  sbc #1
  sta SmTempX
  lda SmTempPage
  sbc #0
  sta SmTempPage
Right:
  clc
  lda SmHeadX
  adc #16
  sta SmHeadX
  lda RgTempPage
  adc #0
  sta SmHeadPage
  lda SmTempPage
  cmp SmHeadPage
  bcc Yes
  bne No
  lda SmTempX
  cmp SmHeadX
  bcc Yes
  bne No
Yes:
  sec
  rts
No:
  clc
  rts
.endproc

; Sophia.checkState: hover always has BRICK_NONE; underwater has it
; outside jumpRise (classic is false in the represented source mode). This
; gate returns the native admission nibble, without changing tile or velocity.
.proc SophiaSourceBrickEffectGate
  lda XgHoverActive
  bne None
  lda MmUnderwater
  beq Bounce
  lda XgRise
  beq None
Bounce:
  lda #4
  rts
None:
  lda #0
  rts
.endproc

.proc SophiaSourceHeadProbe
  lda #0
  sta SmCeilingHit
  jsr SophiaTerrainValid
  jcc Native
  sty SmTemp
  ; ceil(top)-1 = PY+16 through yf==.5, otherwise PY+17.
  lda Player_Y_Position
  clc
  adc #16
  sta RgTempY
  lda MmYFraction+1
  cmp #$80
  bcc QueryReady
  bne ExtraY
  lda MmYFraction
  beq QueryReady
ExtraY:
  inc RgTempY
QueryReady:
  lda RgTempY
  cmp #32
  jcc Empty
  cmp #240
  jcs Empty
  lda #0
  sta SmClearance
Loop:
  lda SmClearance
  jsr SophiaTerrainXPoint
  jsr SophiaTerrainBoundedQuery
  jeq Next
  cmp #$c2
  jeq ReturnTile
  cmp #$c3
  jeq ReturnTile
  cmp #$5f
  beq Hidden
  cmp #$60
  bne Solid
Hidden:
  jsr SophiaSourceBrickEffectGate
  beq Next
Solid:
  ldx R3
  lda MTileAttribute,x
  and #MTILE_SOLID|MTILE_CLIMB
  cmp #MTILE_SOLID
  bne ReturnTile                ; coin/vine has its native separate dispatch.
  lda Player_Y_Speed
  jpl Empty
  lda RyWallSupported
  jeq Empty
  ; Unambiguous direct-below source axis. Corner calcAxis remains separate.
  lda R2
  clc
  adc #48
  sta RgTemp2                  ; actual queried ground bottom.
  lda RyWallOldY
  clc
  adc #16
  cmp RgTemp2
  bcc PriorFraction
  bne Separate
  jmp Separate
PriorFraction:
  ; Prior top may round up only at a half-pixel integer crossing.
  clc
  adc #1
  cmp RgTemp2
  bne Empty
  lda RyWallOldYFrac
  cmp #$80
  bcc Empty
Separate:
  jsr SophiaHeadSourceAxis
  bcc Next
  lda RgTemp2
  sec
  sbc #17
  sta SmTempY
  sta Player_Y_Position
  lda #0
  sta MmYFraction
  lda #$80
  sta MmYFraction+1
  lda #$80
  sta SmCeilingHit
  ; The real query remains in R3/R6/R7. R4 only gates native block
  ; effects: BRICK_NONE skips them while retaining canonical solid contact.
  jsr SophiaSourceBrickEffectGate
  sta R4
ReturnTile:
  lda SmCeilingHit
  bmi ReturnQuery
  lda Player_Y_Position
  and #15
  sta R4
ReturnQuery:
  ldx #0
  ldy SmTemp
  lda R3
  rts
Next:
  inc SmClearance
  lda SmClearance
  cmp #3
  jcc Loop
Empty:
  ldx #0
  ldy SmTemp
  lda #0
  rts
Native:
  jmp BlockBufferColli_Head
.endproc

.proc SophiaSourceSideProbe
  jsr SophiaTerrainValid
  jcc Native
  sty SmTemp
  ; Interior top/bottom rows cover this <16px body without mistaking a
  ; floor or ceiling touch for a horizontal penetration.
  tya
  and #1                       ; native rows33/35 upper,34/36 lower.
  beq Lower
  lda MmYFraction+1
  asl
  lda Player_Y_Position
  adc #16
  jmp YReady
Lower:
  lda MmYFraction
  ora MmYFraction+1
  cmp #1
  lda Player_Y_Position
  adc #31
YReady:
  sta RgTempY
  cmp #32
  bcc Empty
  cmp #240
  bcs Empty
  lda #1
  ldy R0
  cpy #1
  bne Point
  lda #2
Point:
  jsr SophiaTerrainXPoint
  jsr SophiaTerrainBoundedQuery
  beq Done
  lda RgTempX
  and #$f0
  sta SmHeadX
  lda RgTempPage
  sta SmHeadPage
  lda R3
Done:
  rts
Empty:
  lda #0
  rts
Native:
  jmp BlockBufferColli_Side
.endproc

.proc SophiaSourceWall
  jsr SophiaTerrainValid
  jcc Native
  lda R0
  sta XgWallContact
  cmp #1
  beq Right
  ; G.right+9.5 minus the native8px center = G.left+17.5.
  clc
  lda SmHeadX
  adc #17
  sta Player_X_Position
  lda SmHeadPage
  adc #0
  sta Player_PageLoc
  lda MmVX+2
  bpl KeepVelocity
  bmi StopVelocity
Right:
  sec
  lda SmHeadX
  sbc #18
  sta Player_X_Position
  lda SmHeadPage
  sbc #0
  sta Player_PageLoc
  lda MmVX+2
  bmi KeepVelocity
StopVelocity:
  lda #0
  sta MmVX
  sta MmVX+1
  sta MmVX+2
  sta Player_X_Speed
KeepVelocity:
  lda #0
  sta MmXFraction
  sta Player_X_Scroll
  lda #$80
  sta MmXFraction+1
  lda #16
  sta SideCollisionTimer
  sec
  rts
Native:
  lda SelectedCharacter
  farcall SamusStopAtWallBanked, jmp
.endproc
; Exact flat Sophia foot span, current visible ordinary16px ground only.
; Same INY/two-result ABI as BlockBufferColli_Feet. Ambiguous previous
; corners and special terrain retain the original native foot query.
.proc SophiaFeetPriorStrictX
  lda RgTempX
  and #$f0
  sta SmHeadX
  lda RyWallOldXFrac
  cmp #$80
  lda RyWallOldX
  adc #17
  sta SmTempX
  lda RyWallOldPage
  adc #0
  cmp RgTempPage
  jcc No
  bne Left
  lda SmTempX
  cmp SmHeadX
  bcc No
  bne Left
  ; floor(priorRight)==cellLeft: equality is strict only with fraction.
  lda RyWallOldXFine
  bne Left
  lda RyWallOldXFrac
  cmp #$80
  beq No
Left:
  lda RyWallOldX
  sta SmTempX
  lda RyWallOldPage
  sta SmTempPage
  lda RyWallOldXFrac
  cmp #$80
  bcc Minus
  bne Right
  lda RyWallOldXFine
  bne Right
Minus:
  sec
  lda SmTempX
  sbc #1
  sta SmTempX
  lda SmTempPage
  sbc #0
  sta SmTempPage
Right:
  clc
  lda SmHeadX
  adc #16
  sta SmHeadX
  lda RgTempPage
  adc #0
  sta SmHeadPage
  lda SmTempPage
  cmp SmHeadPage
  bcc Yes
  bne No
  lda SmTempX
  cmp SmHeadX
  bcc Yes
  bne No
  ; ceil(priorLeft)==cellRight: a fractional left lies strictly below it.
  lda RyWallOldXFine
  bne Yes
  lda RyWallOldXFrac
  cmp #$80
  beq No
Yes:
  sec
  rts
No:
  clc
  rts
.endproc

.proc SophiaSourceFeet
  jsr SophiaTerrainValid::CharacterKnown
  jcc Original
  ; Only the real flat first-foot epoch may establish the fast pair.
  ; With current n=X&15 in3..13, the two original foot cells cover the
  ; entire19px source span for every fraction. Prior integer displacement
  ; in[-2,+4] puts both query points strictly inside the previous body.
  cpy #30
  jne Slow
  lda RyWallWasGround
  jne Slow
  lda RyWallSupported
  cmp #1
  jne Slow
  lda MmYFraction
  ora MmYFraction+1
  ora MmVY
  ora MmVY+1
  ora MmVY+2
  ora Player_Y_Speed
  ora Player_Y_MoveForce
  ora XgRise
  ora XgHoverActive
  jne Slow
  lda Player_Y_Position
  and #15
  jne Slow
  lda RyWallOldY
  cmp Player_Y_Position
  jne Slow
  lda RyWallOldYFine
  ora RyWallOldYFrac
  jne Slow
  lda Player_X_Position
  and #15
  sec
  sbc #3
  cmp #11
  jcs Slow
  sec
  lda Player_X_Position
  sbc RyWallOldX
  sta SmTempX
  lda Player_PageLoc
  sbc RyWallOldPage
  bcs Forward
  cmp #$ff
  jne Slow
  lda SmTempX
  cmp #$fe
  jcc Slow
  bcs FastQuery
Forward:
  jne Slow
  lda SmTempX
  cmp #5
  jcs Slow
FastQuery:
  jsr BlockBufferColli_Feet
  cmp #$54
  beq FastLand
  cmp #$61
  beq FastLand
  cmp #$62
  beq FastLand
  dey                         ; Restore original input epoch for exact slow path.
  jmp Slow
FastLand:
  lda #0
  sta Player_State            ; All vertical source/native fields were proven0.
  lda #1
  sta MmJumpReleased
  lda #$80
  sta SmClearance             ; Only this same caller's second foot consumes it.
  lda R3
  rts
Slow:
  iny
  sty SmTemp
  lda Player_Y_Position
  clc
  adc #32                    ; floor(source bottom), exact at integral ground.
  sta RgTempY
  cmp #32
  jcc Native
  cmp #240
  jcs Native
  tya
  and #1
  bne Left
  lda #2
  bne Point
Left:
  lda #1
Point:
  sta SmClearance
Query:
  jsr SophiaTerrainXPoint
  jsr SophiaTerrainBoundedQuery
  jeq Center
  cmp #$5f                   ; Hidden, SpringObj, pickups, vine, axe are
  jeq Native                 ; separately defined source interactions.
  cmp #$60
  jeq Native
  cmp #$67
  jeq Native
  cmp #$68
  jeq Native
  cmp #$c2
  jeq Native
  cmp #$c3
  jeq Native
  cmp #$c5
  jeq Native
  tax
  lda MTileAttribute,x
  and #MTILE_SOLID|MTILE_CLIMB
  cmp #MTILE_SOLID
  jne Native
  lda MmVY+2
  jmi Native
  lda RyWallSupported
  jeq Native
  lda R2
  clc
  adc #32
  sta RgTemp2                ; Actual queried ordinary ground top.
  lda RyWallOldY
  clc
  adc #32
  cmp RgTemp2
  bcc StrictX
  jne Native
  lda RyWallOldYFine
  ora RyWallOldYFrac
  jne Native
StrictX:
  jsr SophiaFeetPriorStrictX
  jcc Native
  ; Source groundBelow is resolved before any side queries/body projection.
  lda RgTemp2
  sec
  sbc #32
  sta Player_Y_Position
  lda #0
  sta MmYFraction
  sta MmYFraction+1
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  sta Player_Y_Speed
  sta Player_Y_MoveForce
  sta Player_State
  sta XgRise
  sta XgHoverActive
  lda #1
  sta MmJumpReleased
  lda RyWallWasGround
  beq Return
  lda #AV_SFX_SOPHIALAND
  sta AvAudioRequest
  lda #0
  sta RyWallWasGround         ; Two actual feet produce only one new landing.
Return:
  lda #0
  sta R4                     ; Native landing band follows canonical PY.
  ldy SmTemp
  ldx #0
  lda R3
  rts
Center:
  lda SmClearance
  beq Native
  lda #0
  sta SmClearance
  jmp Query                  ; Center fills the possible third column.
Native:
  ldy SmTemp
  dey
Original:
  jmp BlockBufferColli_Feet
.endproc

SophiaSourceTerrainEnd:

.segment "SOPHIA_BODY_COLD"
.proc SophiaSourceAfterTerrain
  lda XgWall
  ora XgCeiling
  beq CheckCeiling
  lda #0
  sta RyWallSupported
  sta RgDoubleJump
CheckCeiling:
  lda SmCeilingHit
  bpl Done
  lda #0
  sta SmCeilingHit
  sta MmYFraction
  sta XgRise
  lda #$80
  sta MmYFraction+1
  lda SmTempY
  sta Player_Y_Position
  lda XgHoverActive
  ora MmUnderwater
  bne Keep
  lda Square1SoundQueue
  ora #Sfx_Bump
  sta Square1SoundQueue
  lda RgDoubleJump
  beq Keep
  lda #$55
  sta MmVY
  lda #$d5
  sta MmVY+1
  lda #0
  sta MmVY+2
Keep:
  lda MmVY+2
  sta Player_Y_Speed
Done:
  rts
.endproc
.popseg

; Source HitTester.checkLastHitPoints direct-below normal-flat branch.
; Strict prior horizontal interior is a direct head contact. Either prior
; horizontal corner uses calcAxis(false,rightCorner): zero vx chooses the
; side, zero vy chooses the head, otherwise verticalPen<=horizontalPen.
; The native terrain pass resolves that final axis without Flash's deferred
; Ground-list scheduling. Input is the actual queried cell and source caches.
; Preserve R2/R3/R4/R6/R7, SmTemp, RgTemp2 and query X/page for native effects.
.pushseg
.segment "SOPHIA_TERRAIN_COLD"
.proc SophiaHeadSourceAxis
  lda RgTempX
  and #$f0
  sta SmHeadX
  lda RgTempPage
  sta SmHeadPage

  ; floor(priorRight) = oldX+17+carry(xf>=.5).
  lda RyWallOldXFrac
  cmp #$80
  lda RyWallOldX
  adc #17
  sta SmTempX
  lda RyWallOldPage
  adc #0
  cmp SmHeadPage
  jcc CornerRight
  bne CheckLeft
  lda SmTempX
  cmp SmHeadX
  jcc CornerRight
  bne CheckLeft
  lda RyWallOldXFrac
  eor #$80
  ora RyWallOldXFine
  jeq CornerRight             ; exact right==left remains a corner.

CheckLeft:
  ; floor(priorLeft) = oldX-2+carry(xf>=.5).
  lda RyWallOldXFrac
  cmp #$80
  lda RyWallOldX
  sbc #1
  sta SmTempX
  lda RyWallOldPage
  sbc #0
  sta SmTempPage
  jcc Yes                     ; signed priorLeft<0 at world origin.
  clc
  lda SmHeadX
  adc #16
  sta SmHeadX
  lda SmHeadPage
  adc #0
  sta SmHeadPage
  lda SmTempPage
  cmp SmHeadPage
  jcc Yes
  bne CornerLeft
  lda SmTempX
  cmp SmHeadX
  jcc Yes
CornerLeft:
  ldx #0
  beq Corner
CornerRight:
  ldx #1
Corner:
  lda MmVX
  ora MmVX+1
  ora MmVX+2
  jeq No                     ; source vx==0 selects the side, not the head.
  lda MmVY
  ora MmVY+1
  ora MmVY+2
  jeq Yes                    ; with nonzero vx and zero vy, head wins.

  ; V = cellBottom - (PY+16.5+yf), exact unsigned Q8.16 depth.
  lda RgTemp2
  sec
  sbc Player_Y_Position
  sec
  sbc #17
  sta SmTempY
  sec
  lda #0
  sbc MmYFraction
  sta SmTempX
  lda #$80
  sbc MmYFraction+1
  sta SmTempPage
  lda SmTempY
  sbc #0
  sta SmTempY
  cpx #0
  beq LeftDepth

  ; H = PX+17.5+xf - cellLeft.
  lda RgTempX
  and #$f0
  sta RgTempY
  lda MmXFraction
  sta SmHeadX
  clc
  lda MmXFraction+1
  adc #$80
  sta SmHeadPage
  lda Player_X_Position
  adc #17
  sec
  sbc RgTempY
  sta RgTempY
  jmp Compare
LeftDepth:
  ; H = cellRight - (PX-1.5+xf).
  lda RgTempX
  and #$f0
  sec
  sbc Player_X_Position
  clc
  adc #17
  sta RgTempY
  sec
  lda #0
  sbc MmXFraction
  sta SmHeadX
  lda #$80
  sbc MmXFraction+1
  sta SmHeadPage
  lda RgTempY
  sbc #0
  sta RgTempY
Compare:
  lda SmTempY
  cmp RgTempY
  bcc Yes
  bne No
  lda SmTempPage
  cmp SmHeadPage
  bcc Yes
  bne No
  lda SmTempX
  cmp SmHeadX
  bcc Yes
  bne No
Yes:
  sec
  rts
No:
  lda Player_Y_Position
  clc
  adc #16
  sta RgTempY
  lda MmYFraction+1
  cmp #$80
  bcc QueryRestored
  bne QueryExtra
  lda MmYFraction
  beq QueryRestored
QueryExtra:
  inc RgTempY
QueryRestored:
  clc
  rts
.endproc
.popseg

; A negative left body sample at the level origin has no source Ground.
; Retain native empty-query AXY/R2/R4/pointer ABI, but do not expose a tile
; from pageFF's two-page-buffer alias. No clipping on ordinary positive pages.
.pushseg
.segment "SOPHIA_TERRAIN_COLD"
.proc SophiaTerrainBoundedQuery
  lda RgTempPage
  cmp #$ff
  bne Native
  lda Player_PageLoc
  bne Native
  jsr SophiaTerrainQuery
  lda #0
  sta R3
  rts
Native:
  jmp SophiaTerrainQuery
.endproc
.popseg
