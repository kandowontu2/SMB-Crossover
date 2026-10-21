; UNAPPLIED proposal: supported Ryu normal-air/climb source wall mechanics.
; Root must assemble/review actual byte count and execute frozen negative/positive
; controls. Full retained attack/corner/current-cache geometry is not claimed.
.pushseg
.segment "SPECIAL_ROSTER"
RyuWallModuleStart:
.proc RyuWallRemember
  php
  pha
  phx
  phy
  lda RyWallResolved
  sta RyWallBlocked
  lda #0
  sta RyWallResolved
  sta RyWallSupported
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  bne Done
  lda Player_State
  cmp #3
  beq Clear
  lda GuestHurtTicks
  bne Clear
  lda Player_Y_HighPos
  cmp #1
  bne Clear
  lda Player_Y_Position
  cmp #176
  bcs Clear
  ; Entry cached the *old* crouch bit before ExpandedMovement reset it. A
  ; retained attack/current-cache geometry is a separate qualified path.
  lda RyWallSide
  bne NormalShape
  lda RyWallOldHeight
  bne Done
  lda RgAttack
  bne Done
NormalShape:
  lda #25
  ldx Player_State
  bne Height
  lda #0
  sta RyWallSide
  lda #27
Height:
  sta RyWallOldHeight
  lda Player_State
  sta RyWallWasGround            ; zero means source lastOnGround=true.
Supported:
  lda #1
  sta RyWallSupported
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
  jmp Done
Clear:
  lda #0
  sta RyWallSide
  sta XgWall
Done:
  ply
  plx
  pla
  plp
  rts
.endproc

; C=1 Ryu attached movement fully prepared; skip ordinary Horizontal.
; C=0 retains ordinary Horizontal, including Sophia's original movement.
.proc RyuSophiaWallBefore
  pha
  phx
  phy
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  beq Sophia
  jmp RyuPlatformBeforeGate
PlatformResume:
  beq LegacyRyu
  lda RyWallSide
  bne Attached
  ; Source previous wallOnRight/Left survives until after movement. Keep a
  ; stopped nonclimbing jump's VY/gravity when its last contact blocks walking.
  lda RyWallBlocked
  and SavedJoypadBits
  and #3
  jeq No
  jmp Yes
Attached:
  lda RyWallSide
  sta XgWall
  sta PlayerFacingDir
  jsr RyuWallAlign
  lda #0
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  sta XgGravity
  sta XgGravity+1
  lda RgAttack
  beq MoveClimb
  lda RgAttackKind
  bne Yes                        ; source climbThrowing returns before movement.
MoveClimb:
  lda SavedJoypadBits
  and #Up_Dir
  beq Down
  lda #17                        ; hTop+10 = nativeY+7+10.
  ldx #0
  jsr RyuWallPoint
  bcc Down
  lda #$ff
  sta MmVY+2
  jmp Yes
Down:
  lda SavedJoypadBits
  and #Down_Dir
  beq Yes
  lda #19                        ; hBot-12.5 = nativeY+19.5.
  ldx #1
  jsr RyuWallPoint
  bcc Yes
  lda #1
  sta MmVY+2
Yes:
  sec
  bcs Return
LegacyRyu:
  ; Preserve existing unsupported retained-frame mechanics explicitly.
  lda XgWallContact
  and SavedJoypadBits
  and #3
  beq No
  lda #1
  sta XgWall
  jmp LegacyVelocity
Sophia:
  lda #5
  farcall InventoryHas
  bcc No
  lda XgWallContact
  and #3
  beq No
  sta XgWall
  sta PlayerFacingDir
LegacyVelocity:
  lda #0
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  sta XgGravity
  sta XgGravity+1
  lda SavedJoypadBits
  and #Up_Dir
  beq LegacyDown
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne :+
    lda #2
    sta XgJumpUsed
  :
  lda #$ff
  sta MmVY+2
LegacyDown:
  lda SavedJoypadBits
  and #Down_Dir
  beq No
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne :+
    lda #1
    sta XgJumpUsed
  :
  lda #1
  sta MmVY+2
No:
  clc
Return:
  ply
  plx
  pla
  rts
.endproc

; Query an anchored source point at nativeY+A+(X?0.5:0), including the
; upper edge of an adjacent tile only for an exactly integer boundary.
.proc RyuWallPoint
  sta RgTempY
  stx RgTemp2
  jsr RyuWallColumn
  clc
  lda Player_Y_Position
  adc RgTempY
  sta RgTempY
  lda MmYFraction+1
  ldx RgTemp2
  beq Integer
  cmp #$80
  bcc Integer
  inc RgTempY
Integer:
  jsr RyuWallMap
  bcs Yes
  lda RgTempY
  and #15
  bne No
  lda MmYFraction
  bne No
  lda MmYFraction+1
  ldx RgTemp2
  beq Exact
  eor #$80
Exact:
  bne No
  dec RgTempY
  jsr RyuWallMap
  rts
Yes:
  sec
  rts
No:
  clc
  rts
.endproc

.proc RyuWallColumn
  lda RyWallEdge
  sta RgTempX
  lda RyWallPage
  sta RgTempPage
  lda RyWallSide
  cmp #2
  bne Done
  sec
  lda RgTempX
  sbc #1
  sta RgTempX
  lda RgTempPage
  sbc #0
  sta RgTempPage
Done:
  rts
.endproc

; Called after shared integration and after the old Contact=0 reset.
; Only definite horizontal crossings are resolved here; diagonal floor/ceiling
; alternatives stay in the existing native pipeline, with no blanket mask.
.proc RyuWallAfterMotion
  php
  pha
  phx
  phy
  jmp RyuPlatformAfterGate
PlatformResume:
  jeq Done
  lda Player_State
  beq Clear
  cmp #3
  beq Clear
  lda XgWallLock
  bne Detach                    ; existing genuine walljump/drop owns its lock.
  lda RyWallSide
  beq NewSide
  jsr RyuWallAlign
  lda RyWallSide
  sta RyWallResolved
  sta XgWallContact
  sta XgWall
  jmp Done
Detach:
  lda #0
  sta RyWallSide
  jmp NewSide                   ; lock suppresses attachment, not body separation.
Clear:
  lda #0
  sta RyWallSide
  sta XgWall
  jmp Done
NewSide:
  lda MmVX+2
  bmi Left
  ora MmVX+1
  ora MmVX
  bne Right
  lda RyWallBlocked
  jeq Done
  cmp #2
  beq Left
Right:
  lda #1
  sta RgTemp3
  ; floor(newRight) = X+14+carry(frac>=.25).
  lda MmXFraction+1
  cmp #$40
  lda Player_X_Position
  adc #14
  sta RgTempX
  lda Player_PageLoc
  adc #0
  sta RgTempPage
  lda RgTempX
  and #$f0
  sta RyWallEdge
  lda RgTempPage
  sta RyWallPage
  ; Old source right must not already be beyond this wall edge.
  lda RyWallOldXFrac
  cmp #$40
  lda RyWallOldX
  adc #14
  sta R2
  lda RyWallOldPage
  adc #0
  cmp RyWallPage
  jcc Vertical
  jne Done
  lda R2
  cmp RyWallEdge
  jcc Vertical
  jne Done
  lda RyWallOldXFine
  jne Done
  lda RyWallOldXFrac
  cmp #$40
  jne Done
  jmp Vertical
Left:
  lda #2
  sta RgTemp3
  ; floor(newLeft)=X+1+carry(frac>=.75); exact zero fraction queries
  ; the tile on the left of the boundary rather than the empty right tile.
  lda MmXFraction+1
  cmp #$c0
  lda Player_X_Position
  adc #1
  sta RgTempX
  lda Player_PageLoc
  adc #0
  sta RgTempPage
  lda MmXFraction
  bne LeftColumn
  lda MmXFraction+1
  cmp #$c0
  bne LeftColumn
  sec
  lda RgTempX
  sbc #1
  sta RgTempX
  lda RgTempPage
  sbc #0
  sta RgTempPage
LeftColumn:
  lda RgTempX
  and #$f0
  clc
  adc #16
  sta RyWallEdge
  lda RgTempPage
  adc #0
  sta RyWallPage
  lda RyWallOldXFrac
  cmp #$c0
  lda RyWallOldX
  adc #1
  sta R2
  lda RyWallOldPage
  adc #0
  cmp RyWallPage
  bcc DoneLeft
  bne Vertical
  lda R2
  cmp RyWallEdge
  bcs Vertical
DoneLeft:
  jmp Done
Vertical:
  lda RgTempX
  and #$f0
  sta RgTempX
  ; Source current body has25px; scan all rows before the foot. Fractional
  ; foot positions include their final row; an exact floor touch does not.
  clc
  lda Player_Y_Position
  adc #31
  sta RyWallScanLast
  lda MmYFraction
  ora MmYFraction+1
  beq :+
    inc RyWallScanLast
  :
  clc
  lda Player_Y_Position
  adc #7
  and #$f0
  sta RyWallScanY
Row:
  lda RyWallScanY
  cmp #208
  jcs Done
  cmp RyWallScanLast
  bcc CheckRow
  beq CheckRow
  jmp Done
CheckRow:
  ; Definite horizontal side only: old bottom>rowTop and old top<rowBottom.
  clc
  lda RyWallOldY
  adc #32
  cmp RyWallScanY
  bcc Next
  bne OldTop
  lda RyWallOldYFine
  ora RyWallOldYFrac
  beq Next
OldTop:
  clc
  lda RyWallScanY
  adc #16
  sta R3
  lda #32
  sec
  sbc RyWallOldHeight
  clc
  adc RyWallOldY
  cmp R3
  bcs Next
  lda RyWallScanY
  sta RgTempY
  jsr RyuWallMap
  bcc Next
  ; Preserve the exact collided tile and wall side before map scratch reuse.
  lda RgTemp3
  sta RyWallResolved
  sta XgWallContact
  jsr RyuWallAlignSide
::RyuWallContactAccepted:
  ; Exported actual-contact receipt; frozen component binds eight actual bytes.
  lda RyWallWasGround
  beq Done                      ; source !lastOnGround requirement.
  lda XgWallLock
  bne Done
  lda SavedJoypadBits
  and RyWallResolved
  beq Done
  jsr RyuWallCanAttach
  bcc Next
  jmp RyuWallAdjustGrab
::RyuWallGrabContinue:
  sta RyWallSide
  sta XgWall
  lda #0
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  sta XgGravity
  sta XgGravity+1
  jmp Done
Next:
  clc
  lda RyWallScanY
  adc #16
  sta RyWallScanY
  jmp Row
Done:
  ply
  plx
  pla
  plp
  rts
.endproc

; Exact13.5px normal/climb body: nativeX+8 +/-6.75.
.proc RyuWallAlign
  lda RyWallSide
  sta RyWallResolved
.endproc
.proc RyuWallAlignSide
  lda RyWallResolved
  cmp #2
  beq Left
  sec
  lda RyWallEdge
  sbc #15
  sta Player_X_Position
  lda RyWallPage
  sbc #0
  sta Player_PageLoc
  lda #$40                      ; Right edge minus14.75.
  bne Fraction
Left:
  sec
  lda RyWallEdge
  sbc #2
  sta Player_X_Position
  lda RyWallPage
  sbc #0
  sta Player_PageLoc
  lda #$c0                      ; Left edge minus1.25.
Fraction:
  sta MmXFraction+1
  lda #0
  sta MmXFraction
  sta MmVX
  sta MmVX+1
  sta MmVX+2
  sta Player_X_Speed
  sta Player_X_Scroll
  lda #16
  sta SideCollisionTimer
  rts
.endproc

.proc RyuWallCanAttach
  ; Top point Y+17 in [tileTop,tileBottom], inclusively.
  clc
  lda RyWallScanY
  adc #16
  sta R3
  clc
  lda Player_Y_Position
  adc #17
  cmp RyWallScanY
  bcc Bottom
  cmp R3
  bcc Yes
  bne Bottom
  lda MmYFraction
  ora MmYFraction+1
  beq Yes
Bottom:
  ; bottom-12.5 >=tileTop and bottom-17.5 <=tileBottom.
  lda MmYFraction+1
  cmp #$80
  lda Player_Y_Position
  adc #19
  cmp RyWallScanY
  bcc No
  sec
  sbc #5
  cmp R3
  bcc Yes
  bne No
  lda MmYFraction
  bne No
  lda MmYFraction+1
  cmp #$80
  bne No
Yes:
  sec
  rts
No:
  clc
  rts
.endproc

.proc RyuWallMap
  lda RgTempY
  cmp #32
  bcc Empty
  cmp #208
  bcs Empty
  and #$f0
  sec
  sbc #32
  sta R0
  lda RgTempX
  lsr
  lsr
  lsr
  lsr
  clc
  adc R0
  sta R0
  lda RgTempPage
  and #1
  beq Page0
  lda R0
  clc
  adc #208
  sta R0
  lda #>Block_Buffer_1
  adc #0
  jmp Pointer
Page0:
  lda #>Block_Buffer_1
Pointer:
  sta R1
  lda R0
  clc
  adc #<Block_Buffer_1
  sta R0
  bcc :+
    inc R1
  :
  ldy #0
  lda (R0),y
  beq Empty
  cmp #$23
  beq Empty
  cmp #$26
  beq Empty
  cmp #$5f
  beq Empty
  cmp #$60
  beq Empty
  cmp #$1c
  beq Empty
  cmp #$6b
  beq Empty
  tay
  jmp RyuWallMapAttribute
::RyuWallMapAttributeContinue:
  and #MTILE_SOLID | MTILE_CLIMB
  cmp #MTILE_SOLID
  bne Empty
  sec
  rts
Empty:
  clc
  rts
.endproc
RyuWallModuleEnd:
.assert RyuWallModuleEnd-RyuWallModuleStart <= 1719, error, "Ryu wall module exceeds reserved SPECIAL_ROSTER budget"
.popseg
