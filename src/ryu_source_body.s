; Private source-current body projection, pinned Ryu symbol106/HRect14.
; These integer endpoints implement inclusive contact against native integer
; actor boxes, using the port's Q16 anchors. Native enemy geometry is separate.
.pushseg
.segment "SRAM"
RyuSourceBodyProfile: .res 1       ; 0 unknown,16 crouch15.75,25 air,27 stand.
.assert RyuSourceBodyProfile=GuestBodyStompAllowed+1, error, "Body cache must append after old SRAM"
.assert * <= $8000, error, "Source body cache exceeds SRAM"

.segment "COLLISION"


.segment "SOPHIA_BODY_COLD"
RyuSourceBodyModuleStart:
.proc RyuSourceBodyBox
  php
  pha
  phx
  phy
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  jne Done
  lda GameEngineSubroutine
  cmp #8
  jne Invalid
  lda Player_Y_HighPos
  cmp #1
  jne Invalid
  lda Player_Y_Position
  cmp #224
  jcs Invalid
  lda Player_PageLoc
  cmp #$ff
  bne Coherent
  lda Player_X_Position
  cmp #241
  jcs Invalid
Coherent:
  ; Native terrain can relocate the body after its first bbox build. Until
  ; that distinct source world-resolution path is ported, leave it literal.
  lda Player_X_Position
  sec
  sbc ScreenLeft_X_Pos
  cmp #241
  jcs Invalid
  clc
  adc #1
  cmp BoundingBox_UL_Corner
  jne Invalid
  lda Player_Y_Position
  clc
  adc #32
  cmp BoundingBox_LR_Corner+1
  jne Invalid

  lda GuestHurtTicks
  jne Air
  lda MmDeathFlag
  jne Air
  lda XgWall
  ora RyPlatformSlot
  jne Air
  lda Player_State
  cmp #3
  jeq Air                         ; source pole/vine frames64..66.
  lda RgAttack
  beq Ordinary
  ; Actual accepted fresh ground jump replaces ST_ATTACK with ST_JUMP.
  lda RyWallWasGround
  bne Retained
  lda XgFresh
  and #A_Button
  beq Retained
  lda XgJumpUsed
  jne Air
Retained:
  ; Ryu landOnGround begins idle and finishes the old attack. That gameplay
  ; cancellation remains owned elsewhere; use its source body after landing.
  lda Player_State
  bne Cached
  lda RyWallWasGround
  bne Stand
Cached:
  lda RyuSourceBodyProfile
  cmp #16
  beq Shape
  cmp #25
  beq Shape
  cmp #27
  beq Shape
  jmp Invalid                     ; no invented attack-origin/cache receipt.
Ordinary:
  lda RgCrouch
  bne Crouch
  lda Player_State
  beq Stand
  ; Source checkState sees last onGround before movement/terrain. Walking
  ; off retains this update's27 frame; the next air update has oldState!=0.
  lda RyWallWasGround
  bne Air
  lda XgJumpUsed
  bne Air
Stand:
  lda #27
  bne Shape
Crouch:
  lda #16
  bne Shape
Air:
  lda #25
Shape:
  sta RyuSourceBodyProfile
  tay
  ; hLeft = PX+1.25+fx, hRight=PX+14.75+fx. Integral native target
  ; endpoints overlap iff ceil(hLeft)<=targetRight and floor(hRight)>=left.
  lda Player_X_Position
  sec
  sbc ScreenLeft_X_Pos
  clc
  adc #2
  sta BoundingBox_UL_Corner
  lda MmXFraction+1
  cmp #$c0
  bcc Right
  bne LeftExtra
  lda MmXFraction
  beq Right
LeftExtra:
  inc BoundingBox_UL_Corner
Right:
  lda Player_X_Position
  sec
  sbc ScreenLeft_X_Pos
  clc
  adc #14
  sta BoundingBox_LR_Corner
  lda MmXFraction+1
  cmp #$40
  bcc Top
  inc BoundingBox_LR_Corner
Top:
  cpy #16
  beq Short
  lda Player_Y_Position
  clc
  cpy #27
  beq Tall
  adc #7
  bne TopReady
Tall:
  clc
  adc #5
TopReady:
  sta BoundingBox_UL_Corner+1
  lda MmYFraction
  ora MmYFraction+1
  beq Done
  inc BoundingBox_UL_Corner+1
  bne Done
Short:
  lda Player_Y_Position
  clc
  adc #17
  sta BoundingBox_UL_Corner+1
  lda MmYFraction+1
  cmp #$c0
  bcc Done
  bne ShortExtra
  lda MmYFraction
  beq Done
ShortExtra:
  inc BoundingBox_UL_Corner+1
  bne Done
Invalid:
  lda #0
  sta RyuSourceBodyProfile
Done:
  ply
  plx
  pla
  plp
  rts
.endproc
RyuSourceBodyModuleEnd:
; The native right-side CLC/SBC discards exact integer edge equality. Preserve
; its conservative horizontal broadphase only when the *true* current source
; rectangles overlap. Vertical endpoints remain source-current throughout.
.proc RyuSourceBodyPlatformBasic
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  bne No
  cpx #6
  bcs No
  lda Enemy_Flag,x
  cmp #1
  bne No
  lda Enemy_ID,x
  cmp #$28
  bne No
  lda Enemy_BoundBoxCtrl,x
  cmp #5
  bne No
  lda Enemy_State,x
  bne No
  lda Enemy_Y_HighPos,x
  cmp #1
  bne No
  lda Enemy_PageLoc,x
  cmp #$ff
  bne Yes
  lda Enemy_X_Position,x
  cmp #224
  bcs No
Yes:
  sec
  rts
No:
  clc
  rts
.endproc
.proc RyuSourceBodyPlatformOverlap
  jsr RyuSourceBodyPlatformBasic
  jcc No
  lda RyuSourceBodyProfile
  cmp #25
  jne No
  lda GuestHurtTicks
  ora RgCrouch
  ora RgAttack
  jne No
  lda Player_Y_HighPos
  cmp #1
  jne No
  lda Player_Y_Position
  cmp #224
  jcs No
  ; Inclusive current source25 against the independently bound32x8 actor.
  lda Enemy_Y_Position,x
  clc
  adc #8
  jcs No
  sta R4
  lda Player_Y_Position
  clc
  adc #7
  cmp R4
  bcc Bottom
  jne No
  lda MmYFraction
  ora MmYFraction+1
  bne No
Bottom:
  lda Player_Y_Position
  clc
  adc #32
  cmp Enemy_Y_Position,x
  bcc No
  ; Current rightQ16 >= actor leftQ8.
  lda MmXFraction
  sta R0
  clc
  lda MmXFraction+1
  adc #$c0
  sta R1
  lda Player_X_Position
  adc #14
  sta R2
  lda Player_PageLoc
  adc #0
  sta R3
  cmp Enemy_PageLoc,x
  bcc No
  bne Left
  lda R2
  cmp Enemy_X_Position,x
  bcc No
  bne Left
  lda R1
  cmp Enemy_X_MoveForce,x
  bcc No
Left:
  ; Current leftQ16 <= actor rightQ8.
  clc
  lda Enemy_X_Position,x
  adc #32
  sta R4
  lda Enemy_PageLoc,x
  adc #0
  sta R5
  clc
  lda MmXFraction+1
  adc #$40
  sta R1
  lda Player_X_Position
  adc #1
  sta R2
  lda Player_PageLoc
  adc #0
  cmp R5
  bcc Yes
  bne No
  lda R2
  cmp R4
  bcc Yes
  bne No
  lda R1
  cmp Enemy_X_MoveForce,x
  bcc Yes
  bne No
  lda R0
  bne No
Yes:
  sec
  rts
No:
  clc
  rts
.endproc
.if ::ENABLE_MMC5_EXPANDED
.proc Z2LegacyPlatformPrepare
.else
.proc RyuSourceBodyPlatformPrepare
.endif
  RP_Save
  jsr RyuSourceBodyPlatformOverlap
  bcc Done
  ; Only X is padded. Never restore the obsolete31px vertical envelope.
  lda Player_X_Position
  sec
  sbc ScreenLeft_X_Pos
  cmp #240
  bcs Done                       ; no temporary screen-edge wrap.
  sta BoundingBox_UL_Corner
  clc
  adc #16
  sta BoundingBox_LR_Corner
Done:
  RP_Restore
  rts
.endproc
.if ::ENABLE_MMC5_EXPANDED
.proc Z2LegacyPlatformFinish
.else
.proc RyuSourceBodyPlatformFinish
.endif
  RP_Save
  jsr RyuSourceBodyPlatformBasic
  bcc Done
  lda RyuSourceBodyProfile
  beq Done
  ; Rebuild after the actual native/source response, including attachment's
  ; fractional new location. No old rectangle can leak into a later enemy.
  jsr RelativePlayerPosition
  ldx #0
  jsr BoundingBoxCore
  jsr RyuSourceBodyBox
Done:
  RP_Restore
  rts
.endproc

.popseg
