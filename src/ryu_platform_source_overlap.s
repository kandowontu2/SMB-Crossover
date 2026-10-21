; Bounded source current-HRect admission before native large-platform response.
; C=1 native fallback (every unsupported form); C=0 disjoint or source handled.
; Only native normal-4 horizontal platform$28/bbox5 and normal-air Ryu25px.
; Actor position/order remain native. This is not a full source platform solver.
.pushseg
.segment "ROSTER"
RyuPlatformSourceOverlapStart:
.proc RyuPlatformSourceOverlap
  RP_Save
  jsr RyuPlatformActor
  jcc Allow
  ; This authored actor/shape binding is independently proven only in1-4.
  lda WorldNumber
  jne Allow
  lda LevelNumber
  cmp #3
  jne Allow
  lda AreaType
  cmp #3
  jne Allow
  lda SecondaryHardMode
  jne Allow
  lda GuestHurtTicks
  ora RgCrouch
  ora RgAttack
  ora XgWall
  ora RyPlatformSlot
  jne Allow
  lda Player_State
  cmp #1
  jne Allow
  lda RyWallSupported
  jeq Allow
  lda RyWallOldHeight
  cmp #25
  jne Allow
  lda RyWallWasGround
  cmp #1
  jne Allow
  lda Player_Y_HighPos
  cmp #1
  jne Allow
  lda Player_Y_Position
  cmp #176
  jcs Allow
  ; Unsigned16world helper additions must not silently wrap a page255 edge.
  lda Player_PageLoc
  cmp #$ff
  bne ActorPage
  lda Player_X_Position
  cmp #242
  jcs Allow
ActorPage:
  lda RyWallOldPage
  cmp #$ff
  bne ActorCoordinate
  lda RyWallOldX
  cmp #242
  jcs Allow
ActorCoordinate:
  lda Enemy_PageLoc,x
  cmp #$ff
  bne Vertical
  lda Enemy_X_Position,x
  cmp #224
  jcs Allow
Vertical:
  ; Source currentY:[PY+7,PY+32], platformY:[EY,EY+8], inclusive.
  lda Enemy_Y_Position,x
  clc
  adc #8
  sta R4
  lda Player_Y_Position
  clc
  adc #7
  cmp R4
  bcc Bottom
  jne NoHit
  lda MmYFraction
  ora MmYFraction+1
  jne NoHit
Bottom:
  lda Player_Y_Position
  clc
  adc #32
  cmp Enemy_Y_Position,x
  jcc NoHit
  ; Exact currentQ16 X:[PX+1.25,PX+14.75], actorQ8 X:[EX,EX+32].
  ldy #0
  jsr RyuPlatformEdge
  lda #14
  ldy #$c0
  jsr RyuPlatformCurrentPoint
  jsr RyuPlatformCompare
  jmi NoHit
  ldy #32
  jsr RyuPlatformEdge
  lda #1
  ldy #$40
  jsr RyuPlatformCurrentPoint
  jsr RyuPlatformCompare
  cmp #1
  jeq NoHit
  ; Overlap alone is not enough for a direct source underside response.
  ; HitTester358..374: previous top below bottom and previous X overlaps.
  lda Enemy_Y_Position,x
  clc
  adc #8
  sta R4
  lda RyWallOldY
  clc
  adc #7
  cmp R4
  jcc Allow
  ldy #0
  jsr RyuPlatformEdge
  lda #14
  ldy #$c0
  jsr RyuPlatformOldPoint
  jsr RyuPlatformCompare
  cmp #1
  jne Allow                  ; oldRight<=oldLeft is diagonal/outside.
  ldy #32
  jsr RyuPlatformEdge
  lda #1
  ldy #$40
  jsr RyuPlatformOldPoint
  jsr RyuPlatformCompare
  cmp #$ff
  jne Allow                  ; oldLeft>=oldRight is diagonal/outside.
  ; Character.groundAbove: ny=platform.hBot+hHeight. Translate foot32:
  ; canonicalY=(EY+8)+25-32=EY+1; exact integer actorY, no epsilon clamp.
  lda Enemy_Y_Position,x
  clc
  adc #1
  sta Player_Y_Position
  lda #0
  sta MmYFraction
  sta MmYFraction+1
  lda XgJumpUsed
  beq RetainVY
  lda #$55                   ;100Flashpx/s /120NES updates =Q16$00D555.
  sta MmVY
  lda #$d5
  sta MmVY+1
  lda #0
  sta MmVY+2
RetainVY:
  lda MmVY+2                 ; keep mirror coherent; no next-AirSync rounding.
  sta Player_Y_Speed
  lda #Sfx_Bump
  ora Square1SoundQueue
  sta Square1SoundQueue
  ; Normal Ryu groundAbove does NOT reset FLIP_TMR or JumpSlash.
  ; Refresh native relative position/box after the source position correction.
  jsr RyuPlatformBox
  jmp NoHit                  ; source response already handled, skip native.
Allow:
  RP_Restore
  sec
  rts
NoHit:
  RP_Restore
  clc
  rts
.endproc
RyuPlatformSourceOverlapEnd:
.assert RyuPlatformSourceOverlapEnd-RyuPlatformSourceOverlapStart <= 768, error, "Source gate bounded ROSTER budget"
.popseg
