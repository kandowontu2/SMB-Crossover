; Audited source placements using native platform25/28, collision and carry.
.pushseg
.segment "CROSSOVER_HELPERS"
.include "crossover_helper_data.inc"

; Preserve the original area-loader result, including its native scratch.
.proc HpLoadArea
  farcall GetAreaDataAddrs
  php
  pha
  txa
  pha
  tya
  pha
  .repeat 8,I
    lda R0+I
    pha
  .endrepeat
  jsr HpConfigure
  .repeat 8,I
    pla
    sta R0+7-I
  .endrepeat
  pla
  tay
  pla
  tax
  pla
  plp
  rts
.endproc

.proc HpConfigure
  ; A stale slot is never erased just because its old ownership entry remains.
  ldx #2
Release:
  stx HpSlot
  jsr HpReleaseActor
  ldx HpSlot
  dex
  bpl Release
  lda #0
  ldx #HpRamEnd-HpRamStart-1
Clear:
  sta HpRamStart,x
  dex
  cpx #$ff
  bne Clear
  lda WorldNumber
  asl
  asl
  ora LevelNumber
  sta HpKey
  lda AreaPointer
  sta HpArea
  jsr HpIdentityKey
  sta HpCharacter
  lda CrossoverBehaviorVersion
  sta HpMode
  lda #1
  sta HpValid
  ldy #0
Record:
  sty HpLoop
  lda HpDataKey,y
  cmp HpKey
  bne Next
  lda HpDataArea,y
  cmp HpArea
  bne Next
  ldx SelectedCharacter          ; Cache is packed; admission always uses raw ID.
  cpx #20
  bcs Next
  lda HpMode
  bne Hard
  lda HpDataEasyGate,y
  bne Gate
  beq Next
Hard:
  lda HpDataHardGate,y
Gate:
  beq Next
  cmp #4
  bne Mask
  cpx #6                       ; Hosted original-six unfiltered source tag.
  bcs Next
  bcc Admit
Mask:
  sta HpTemp2
  tya
  pha
  txa
  tay
  jsr HpGetCharacterMask
  and HpTemp2
  sta HpTemp3
  pla
  tay
  lda HpTemp3
  beq Next
Admit:
  ldx HpCount
  cpx #3
  bcs Next                      ; Proven max3; never overflow allocated state.
  tya
  sta HpRecord,x
  lda HpDataXLo,y
  sta HpXLo,x
  sta HpPreviousXLo,x
  lda HpDataXHi,y
  sta HpXHi,x
  sta HpPreviousXHi,x
  lda HpDataY,y
  sta HpY,x
  sta HpPreviousY,x
  lda HpDataWidth,y
  sta HpWidth,x
  lda HpDataAxis,y
  sta HpKind,x
  inc HpCount
Next:
  ldy HpLoop
  iny
  cpy #HELPER_RECORDS
  jne Record
  rts
.endproc

; Y=family ID, A=H/V accommodation mask; preserve X/Y for authored cells.
.proc HpGetCharacterMask
  cpy #20
  bcs None
.if ::ENABLE_MMC5_EXPANDED
  cpy #5
  bne Table
  lda Cv3Variant
  beq Table
  lda #3                       ; Grant/Sypha/Alucard custom H+V; Simon retains H.
  rts
.endif
Table:
  lda HpCharacterMasks,y
  rts
None:
  lda #0
  rts
.endproc
; Cache the actual CV3 alternate as well as its family. No additional RAM.
.proc HpIdentityKey
.if ::ENABLE_MMC5_EXPANDED
  lda SelectedCharacter
  cmp #5
  bne Native
  lda Cv3Variant
  and #3
  .repeat 5
    asl
  .endrepeat
  ora #5
  rts
.endif
Native:
  lda SelectedCharacter
  rts
.endproc

; X=runtime helper index; C=1 only for our still-live primary native actor.
.proc HpFindActor
  lda HpActorSlot,x
  beq Missing
  cmp #7
  bcs Missing
  tay
  dey
  stx HpSlot
  txa
  clc
  adc #1
  cmp HpActorOwner,y
  bne Missing
  lda Enemy_Flag,y
  cmp #1
  bne Missing
  lda Enemy_ID,y
  cmp #$25
  beq Marker
  cmp #$28
  bne Missing
Marker:
  lda Enemy_State,y
  and #$c0
  cmp #$40
  bne Missing
  sec
  rts
Missing:
  clc
  rts
.endproc

.proc HpReleaseActor
  stx HpSlot
  jsr HpFindActor
  bcc Forget
  tya
  tax
  jsr EraseEnemyObject           ; Original native slot/contact teardown.
Forget:
  ldx HpSlot
  lda HpActorSlot,x
  beq Done
  cmp #7
  bcs ForgetSlot
  tay
  dey
  txa
  clc
  adc #1
  cmp HpActorOwner,y
  bne ForgetSlot
  lda #0
  sta HpActorOwner,y
ForgetSlot:
  lda #0
  sta HpActorSlot,x
Done:
  rts
.endproc

.proc HpSpawnAndTrack
  lda HpValid
  beq Configure
  lda AreaPointer
  cmp HpArea
  bne Configure
  jsr HpIdentityKey
  cmp HpCharacter
  bne Configure
  lda CrossoverBehaviorVersion
  cmp HpMode
  beq Configured
Configure:
  jsr HpConfigure
Configured:
  lda TimerControl
  jne Done
  lda #0
  sta HpSlot
Loop:
  ldx HpSlot
  cpx HpCount
  jcs Done
  jsr HpInSourceMargin
  sta HpVisible,x
  bne Present
  jsr HpReleaseActor
  jmp Next
Present:
  jsr HpFindActor
  bcs Next
  ; Native enemy slots have priority. Never overwrite any active actor.
  ldy #5
Free:
  lda Enemy_Flag,y
  beq Found
  dey
  bpl Free
  jmp Next
Found:
  tya
  pha
  tax
  stx ObjectOffset
  ldy HpSlot
  tya
  clc
  adc #1
  sta HpActorOwner,x
  txa
  clc
  adc #1
  sta HpActorSlot,y
  lda HpKind,y
  beq Horizontal
  lda #$25
  bne ID
Horizontal:
  lda #$28
ID:
  sta Enemy_ID,x
  lda #1
  sta Enemy_Flag,x
  sta Enemy_Y_HighPos,x
  jsr HpProjectPosition
  farcall InitEnemyObject         ; Full native initialization and contact reset.
  pla
  tax
  ldy HpSlot
  lda HpWidth,y
  cmp #6
  beq Wide
  lda #5
  bne Box
Wide:
  lda #6
Box:
  sta Enemy_BoundBoxCtrl,x
  lda #$40
  ldy HpSlot
  ldx HpWidth,y
  cpx #2
  bne Tag
  ora #$20
Tag:
  ldx ObjectOffset
  sta Enemy_State,x
  lda #$ff
  sta PlatformCollisionFlag,x
Next:
  inc HpSlot
  jmp Loop
Done:
  rts
.endproc

; Stored center versus native camera-left. Early strict(-56,+296), late
; inclusive[-48,+288]. Return A=0/1, X=runtime index. Phase holds when detached.
.proc HpInSourceMargin
  lda HpXLo,x
  sec
  sbc ScreenLeft_X_Pos
  sta HpTemp
  lda HpXHi,x
  sbc ScreenLeft_PageLoc
  bmi Left
  cmp #1
  bcc Yes
  bne No
  lda HpMode
  bne LateRight
  lda HpTemp
  cmp #40
  bcc Yes
  bcs No
LateRight:
  lda HpTemp
  cmp #33
  bcc Yes
  bcs No
Left:
  cmp #$ff
  bne No
  lda HpMode
  bne LateLeft
  lda HpTemp
  cmp #201
  bcs Yes
  bcc No
LateLeft:
  lda HpTemp
  cmp #208
  bcs Yes
No:
  lda #0
  rts
Yes:
  lda #1
  rts
.endproc

; Actual X=enemy index,Y=runtime index. Source records store the center;
; native platform logic, graphics and bbox all use the left edge.
.proc HpProjectPosition
  lda HpWidth,y
  asl
  asl
  sta HpTemp
  lda HpXLo,y
  sec
  sbc HpTemp
  sta Enemy_X_Position,x
  lda HpXHi,y
  sbc #0
  sta Enemy_PageLoc,x
  lda HpY,y
  sta Enemy_Y_Position,x
  rts
.endproc

.proc HpNativePlatformDispatch
  lda Enemy_ID,x
  cmp #$25
  beq Tag
  cmp #$28
  bne Native
Tag:
  lda Enemy_State,x
  and #$c0
  cmp #$40
  bne Native
  lda HpActorOwner,x
  beq Native
  cmp #4
  bcs Native
  tay
  dey
  txa
  pha
  tya
  tax
  jsr HpFindActor
  pla
  tax
  bcc Native
  jmp HpMoveNativeHelper
Native:
  lda Enemy_ID,x
  sec
  sbc #$24
  jsr JumpEngine
  .word Balance,YMoving,Lift,Lift,XMoving,Drop,Right
Balance: farcall BalancePlatform,jmp
YMoving: farcall YMovingPlatform,jmp
Lift: farcall MoveLargeLiftPlat,jmp
XMoving: farcall XMovingPlatform,jmp
Drop: farcall DropPlatform,jmp
Right: farcall RightPlatform,jmp
.endproc

.proc HpMoveNativeHelper
  stx HpEngine
  lda HpActorOwner,x
  tax
  dex
  stx HpSlot
  jsr HpMotionTick
  ldy HpSlot
  ldx HpEngine
  jsr HpProjectPosition
  lda PlatformCollisionFlag,x
  bmi Done
  lda HpKind,y
  bne Vertical
  lda HpXLo,y
  sec
  sbc HpPreviousXLo,y
  sta R0
  farcall PositionPlayerOnHPlat,jmp
Vertical:
  farcall PositionPlayerOnVPlat,jmp
Done:
  rts
.endproc

; X is an allocated helper slot. Source phase is sampled BEFORE incrementing;
; a stage-detached helper keeps its phase and current position unchanged.
.proc HpMotionTick
  stx HpSlot
  lda HpXLo,x
  sta HpPreviousXLo,x
  lda HpXHi,x
  sta HpPreviousXHi,x
  lda HpY,x
  sta HpPreviousY,x
  lda HpVisible,x
  beq Done
  jsr HpSine
  sta HpOffset
  ldx HpSlot
  ldy HpRecord,x
  lda HpDataXLo,y
  sta HpXLo,x
  lda HpDataXHi,y
  sta HpXHi,x
  lda HpDataY,y
  sta HpY,x
  lda HpDataAxis,y
  bne Vertical
  lda HpDataXLo,y
  clc
  adc HpOffset
  sta HpXLo,x
  lda #0
  bit HpOffset
  bpl :+
    lda #$ff
  :
  adc HpDataXHi,y
  sta HpXHi,x
  clc
  lda HpPhaseLo,x
  adc #$c2
  sta HpPhaseLo,x
  lda HpPhaseMid,x
  adc #$04
  sta HpPhaseMid,x
  lda HpPhaseHi,x
  adc #$01
  sta HpPhaseHi,x
Done:
  rts
Vertical:
  lda HpDataY,y
  clc
  adc HpOffset
  sta HpY,x
  clc
  lda HpPhaseLo,x
  adc #$d7
  sta HpPhaseLo,x
  lda HpPhaseMid,x
  adc #$ad
  sta HpPhaseMid,x
  lda HpPhaseHi,x
  adc #0
  sta HpPhaseHi,x
  rts
.endproc

; 1024 phase bins mirrored into256 samples per positive quadrant. Integer
; outputs explicitly quantize source sine motion to native NES pixel positions.
.proc HpSine
  lda HpPhaseHi,x
  and #$3f
  asl
  asl
  sta HpTemp
  lda HpPhaseMid,x
  .repeat 6
    lsr
  .endrepeat
  ora HpTemp
  sta HpSineIndex
  lda HpPhaseHi,x
  and #$40
  beq :+
    lda HpSineIndex
    eor #$ff
    sta HpSineIndex
  :
  ldy HpRecord,x
  lda HpDataAxis,y
  bne V
  ldy HpSineIndex
  lda HpSineHorizontal,y
  jmp Signed
V:
  ldy HpSineIndex
  lda HpSineVertical,y
Signed:
  sta HpTemp2
  ldx HpSlot
  lda HpPhaseHi,x
  bpl Positive
    lda HpTemp2
    eor #$ff
    clc
    adc #1
    rts
Positive:
  lda HpTemp2
  rts
.endproc
.popseg
.include "native_platform16.s"
.include "native_platform16_v2.s"
.include "native_helper_pause.s"
