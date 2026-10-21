; Normal unrotated Sophia ground consumers. Source HRect113=19x15.5.
; The existing Ryu prior-position cache is character-owned: Sophia publishes
; it before integration; every Ryu consumer is SelectedCharacter-gated.
; Corner calcAxis order, complete foot span and rotated anchors remain separate.
.pushseg
.segment "LEGACY_COLD"
SophiaSourceTerrainStart:
.proc SophiaTerrainValid
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne No
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
  lda RgTempPage
  and #1
  lsr
  ora R5
  ror
  lsr
  lsr
  lsr
  jsr GetBlockBufferAddr
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
  jsr SophiaTerrainQuery
  beq Next
  tax
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
  jsr SophiaPriorXOverlapsCell
  bcc Empty
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
  lda #4
  sta R4                       ; source has no native origin-nibble head gap.
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
  bcc Loop
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
  jsr SophiaTerrainQuery
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
