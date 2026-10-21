; Original XML690/Link.as animation graph, on completed60Hz source updates.
; RgBillBurst=Link sourceframe, Delay=throw timer bit, Cadence=noAnimThisCycle.
; Those fields are Bill-only outside this explicitly EasyLink closure.
.pushseg
.segment "SPECIAL_EXTRA"
.proc EasyLinkFrameCycle
  inc RgClock
  lda RgClock
  cmp #36
  bcc :+
    lda #0
    sta RgClock
  :
  lda RgAttack
  bne Done
  lda Player_State
  cmp #3
  beq Vine
  cmp #0
  bne Air
  lda MmVX
  ora MmVX+1
  ora MmVX+2
  bne Walk
  lda SavedJoypadBits
  and #3
  bne Walk
  lda #2
  bne Store
Walk:
  lda RgBillBurst
  cmp #3
  beq Done
  cmp #4
  beq Done
  lda #3
  bne Store
Vine:
  lda RgBillBurst
  cmp #23
  beq Done
  cmp #24
  beq Done
  lda #23
  bne Store
Air:
  lda SavedJoypadBits
  and #Up_Dir
  beq Down
  ldx #20
  lda RgBillBurst
  cmp #20
  beq End
  cmp #21
  beq End
  bne Start
Down:
  lda SavedJoypadBits
  and #Down_Dir
  beq Jump
  ldx #18
  lda RgBillBurst
  cmp #18
  beq End
  cmp #19
  bne Start
End:
  inx
Start:
  txa
  bne Store
Jump:
  lda #17
Store:
  sta RgBillBurst
Done:
  rts
.endproc

.proc EasyLinkAnimate
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  jne Done
  lda CrossoverBehaviorVersion
  ora GuestHurtTicks
  jne Done
  ldx RgClock
  lda TickMask,x
  sta RgTemp3
  lda RgAttack
  jeq Locomotion
  lda #31
  sta RgAttack                  ; The source framegraph ends the state.
  lda RgAttackKind
  bne Throw
  lda RgAttackAge
  beq SwordStart
  cmp #9
  bcc Done
  bne SwordTick
  lda #6
  sta RgBillBurst
SwordTick:
  lda RgTemp3
  and #1                       ; ANIM_FAST_TMR=30Hz.
  beq Done
  inc RgBillBurst
  lda RgBillBurst
  cmp #7
  bne SwordFinish
  lda Player_State
  beq Done
  lda #9
  bne Frame
SwordFinish:
  jmp Finish
SwordStart:
  lda #5
  bne Frame
Throw:
  lda RgAttackAge
  bne ThrowTick
  lda #1
  sta RgBillCadence             ; Old pressSpcBtn sets noAnimThisCycle.
  lda #2                       ; Ground50ms timer.
  ldx Player_State
  beq :+
    asl                        ; Air100ms timer; retained after landing.
  :
  sta RgBillBurstDelay
  lda #11
  bne Frame
ThrowTick:
  lda RgTemp3
  and RgBillBurstDelay
  beq Done
  lda RgBillCadence
  beq ThrowAdvance
  dec RgBillCadence
  rts
ThrowAdvance:
  inc RgBillBurst
  lda RgBillBurst
  cmp #14
  beq Finish
  cmp #13
  bne Done
  lda Player_State
  beq Done
Finish:
  lda #0
  sta RgAttack
  lda Player_State
  beq Stand
  lda #17
  bne Frame
Stand:
  lda #2
Frame:
  sta RgBillBurst
Done:
  rts
Locomotion:
  lda RgTemp3
  and #4
  beq Done
  lda RgBillBurst
  cmp #3
  beq Advance
  cmp #4
  beq WalkWrap
  cmp #23
  beq Advance
  cmp #24
  bne Done
  lda #23
  bne Frame
WalkWrap:
  lda #3
  bne Frame
Advance:
  inc RgBillBurst
  rts
TickMask:
  .byte 15,0,1,2,1,8,7,0,1,10,1,0,7,0,9,2,1,0
  .byte 15,0,1,2,1,8,7,0,1,10,1,0,7,0,9,2,1,0
.endproc

; Carry1/A=pose only for EasyLink; foreign/Hard preserve old graphics path.
.proc EasyLinkVisual
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne No
  lda CrossoverBehaviorVersion
  bne No
  ldx RgBillBurst
  lda Poses,x
  sec
  rts
No:
  clc
  rts
Poses:
  .byte RG_POSE_STAND,RG_POSE_STAND,RG_POSE_STAND,RG_POSE_WALK1,RG_POSE_WALK2
  .byte RG_POSE_ATTACK1,RG_POSE_ATTACK2,RG_POSE_ATTACK3,RG_POSE_ATTACK3,RG_POSE_UPSTAND,RG_POSE_JUMP1
  .byte RG_POSE_THROW1,RG_POSE_THROW2,RG_POSE_THROW3,RG_POSE_STAND,RG_POSE_STAND,RG_POSE_STAND
  .byte RG_POSE_JUMP1,RG_POSE_DOWNTHRUST,RG_POSE_DIAGDOWN,RG_POSE_UPTHRUST,RG_POSE_DIAGUP,RG_POSE_STAND
  .byte RG_POSE_CLIMB1,RG_POSE_CLIMB2
.endproc
.popseg
