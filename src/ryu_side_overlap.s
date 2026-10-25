; Ryu2.02 normal25: source previous-interior Ground hit has no side response.
; This is not general calcAxis, a stuck-state port, or unsupported-pose parity.
.pushseg
.segment "RYU_SIDE_COLD"
RyuSourceSideAdmissionStart:
.proc RyuSourceSideAdmission
  RP_Save
  cpy RyWallResolved
  jeq Yes                       ; retain the old exact-side source receipt.
  lda RyWallSide
  beq PreviousInterior
  lda Player_State
  jne Yes                       ; explicit ST_CLIMB ignores groundOnSide.
  jmp No                        ; actual landing restores native side handling.
PreviousInterior:
  ; Native normal-row side and deep-foot producers both reach this gate.
  lda Local_eb
  cmp #51
  beq Form
  cmp #54
  jcc No
  cmp #58
  jcs No
Form:
  lda OperMode
  cmp #1
  jne No
  lda GameEngineSubroutine
  cmp #8
  jne No
  lda RyuSourceBodyProfile
  cmp #25
  jne No
  lda RyWallOldHeight
  cmp #25
  jne No
  lda RyWallSupported
  jeq No
  lda RyWallWasGround
  jeq No
  cmp #3
  jcs No
  lda Player_State
  jeq No
  cmp #3
  jcs No
  lda RgAttack
  ora RgCrouch
  ora CrouchingFlag
  ora GuestHurtTicks
  ora GuestPowerupActive
  ora MmDeathFlag
  ora MmUnderwater
  ora SwimmingFlag
  ora RyPlatformSlot
  ora XgWall
  ora AvSlash
  jne No
  lda Player_Y_HighPos
  cmp #1
  jne No
  lda AreaType
  jeq No
  lda Player_Y_Position
  cmp #192
  jcs No
  lda RyWallOldY
  cmp #192
  jcs No
  lda Player_PageLoc
  cmp #$ff
  jeq No
  lda RyWallOldPage
  cmp #$ff
  jeq No
  lda R2
  cmp #$d0
  jcs No
  ; Actual query tile/pointer is retained. Only visible solid Ground families;
  ; transient bump23, hidden, Spring, coins and axe have distinct contracts.
  ldy R3
  lda MTileAttribute,y
  and #MTILE_SOLID|MTILE_CLIMB
  cmp #MTILE_SOLID
  jne No
  cpy #$23
  jeq No
  cpy #$5f
  jeq No
  cpy #$60
  jeq No
  cpy #$66
  jeq No
  cpy #$67
  jeq No
  cpy #$68
  jeq No
  cpy #$c2
  jeq No
  cpy #$c3
  jeq No
  cpy #$c5
  jeq No
  ; Native query adders are positive1/14 (side), or13 (last foot query).
  ; R5 is their actual integer worldpoint; comparison recovers its page carry.
  lda Player_X_Position
  cmp R5
  lda Player_PageLoc
  adc #0
  sta RgTempPage
  lda R5
  and #$f0
  sta RgTempX
  clc
  adc #16
  sta R6                         ; cell right (16bit); left inRgTempX/Page.
  lda RgTempPage
  adc #0
  sta R7
  lda R2
  clc
  adc #32
  sta RgTempY                    ; ground top; native row validity checked.
  clc
  adc #16
  sta RgTemp3                    ; ground bottom.
  ; Current inclusive Y overlap: top<=bottom and bottom>=top.
  lda Player_Y_Position
  clc
  adc #7
  cmp RgTemp3
  bcc CurrentBottom
  jne No
  lda MmYFraction
  ora MmYFraction+1
  jne No
CurrentBottom:
  lda Player_Y_Position
  clc
  adc #32
  cmp RgTempY
  jcc No
  ; Previous STRICT Y interior excludes all direct-above/below/corner paths.
  lda RyWallOldY
  clc
  adc #7
  cmp RgTemp3
  jcs No
  lda RyWallOldY
  clc
  adc #32
  cmp RgTempY
  bne PreviousBottomDifferent
  lda RyWallOldYFine
  ora RyWallOldYFrac
  jeq No
  jmp CurrentRight
PreviousBottomDifferent:
  jcc No
CurrentRight:
  ; floor(current hRight)=PX+14+[fx>=.25] must be >=cell.left.
  lda MmXFraction+1
  cmp #$40
  lda Player_X_Position
  adc #14
  sta R0
  lda Player_PageLoc
  adc #0
  sta R1
  jsr CompareLeft
  jcc No
  ; ceil(current hLeft)=PX+2+[fx>.75] must be <=cell.right.
  lda MmXFraction
  cmp #1
  lda MmXFraction+1
  sbc #$c0
  lda Player_X_Position
  adc #2
  sta R0
  lda Player_PageLoc
  adc #0
  sta R1
  jsr CompareRight
  bcc PreviousRight
  jne No
PreviousRight:
  ; ceil(previous hRight)=oldPX+15+[oldfx>.25] must be >cell.left.
  lda RyWallOldXFine
  cmp #1
  lda RyWallOldXFrac
  sbc #$40
  lda RyWallOldX
  adc #15
  sta R0
  lda RyWallOldPage
  adc #0
  sta R1
  jsr CompareLeft
  jcc No
  jeq No
  ; floor(previous hLeft)=oldPX+1+[oldfx>=.75] must be <cell.right.
  lda RyWallOldXFrac
  cmp #$c0
  lda RyWallOldX
  adc #1
  sta R0
  lda RyWallOldPage
  adc #0
  sta R1
  jsr CompareRight
  jcs No
Yes:
  RP_Restore
  sec
  rts
No:
  RP_Restore
  clc
  rts
CompareLeft:
  lda R1
  cmp RgTempPage
  bne CompareDone
  lda R0
  cmp RgTempX
CompareDone:
  rts
CompareRight:
  lda R1
  cmp R7
  bne RightDone
  lda R0
  cmp R6
RightDone:
  rts
.endproc
RyuSourceSideAdmissionEnd:
.assert RyuSourceSideAdmissionEnd-RyuSourceSideAdmissionStart<=768, error,"Bounded side admission budget"
.popseg

; GO has six extra cold-init bytes for Cheats. Retain its original15-byte
; SAMUS gate and42-byte stomp policy; perform the C-only dispatch in this bank.
.pushseg
.segment "RYU_SIDE_COLD"
.proc RyuSourceSideDispatch
  ; These are the frozen predicate's first source guards, before its costly
  ; scratch save. The sole public caller consumes only carry.
  cpy RyWallResolved
  beq Done
  lda Player_State
  beq Native
  lda RyWallSide
  beq Predicate
  sec
Done:
  rts
Predicate:
  jsr RyuSourceSideAdmission
  bcs Done
Native:
  farcall SamusStopAtWallBanked::NativeGuest
  rts
.endproc
.assert * <= $ba00,error,"Ryu admission and dispatch exceed reserved768bytes"
.popseg
