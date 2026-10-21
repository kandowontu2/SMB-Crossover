; Original Link ATK_VEC and 300ms Down-thrust timer. Hard is untouched.
; Cold helpers use PLAYER space freed by the separately owned MM relocation.
.pushseg
.segment "PLAYER"
.proc EasyLinkCycle
  lda CrossoverBehaviorVersion
  bne Done
  lda GuestHurtTicks
  bne Done
  farcall EasyLinkFrameCycle
  ; Original relUpBtn/relDwnBtn clear ATK_VEC, even during a sword swing.
  lda SavedJoypadBits
  eor #$ff
  and RgPreviousButtons
  and #Up_Dir|Down_Dir
  bne Reset
  lda Player_State
  bne Timer
  lda RgThrustReset
  bne Reset
Timer:
  lda RgCooldown
  cmp #1
  bne Sword
  lda RgThrustReset
  cmp #1
  beq Reset
Sword:
  lda RgAttackKind
  bne Done
  lda RgAttack
  beq Done
  lda RgAttackAge
  cmp #8                         ; This completed update reaches150ms age9.
  bne Done
Reset:
  jsr EasyLinkResetVector
Done:
  rts
.endproc

; X=actual enemy, RgTemp3=its canonical bit, C=1 skips the old vector hit.
.proc EasyLinkThrustHit
  lda RgMeleeHits
  and RgTemp3
  bne Seen
  lda RgMeleeHits
  ora RgTemp3
  sta RgMeleeHits
  farcall LinkThrustResponse
  lda RgThrust
  cmp #1
  bne New
  lda #18                       ; CustomTimer300ms at60 completed updates.
  sta RgCooldown
  lda Enemy_Y_Position,x
  clc
  adc #8
  farcall LinkClampThrustFeet
New:
  clc
  rts
Seen:
  sec
  rts
.endproc
.proc EasyLinkBounce
  lda #0                        ; Character.BOUNCE_PWR300 /120 =2.5NES.
  sta MmVY
  lda #$80
  sta MmVY+1
  lda #$fd
  sta MmVY+2
  sta Player_Y_Speed
  lda #1
  sta Player_State
  lda #8
  sta LsrHurtFlags
  rts
.endproc

; Old Enemy.stun is an unconditional3000ms animation/timer stop, distinct
; from2.02 STOP property resistance. Source confirmedHitProj owns eligibility.
.proc EasyLinkBoomStop
  lda #180
  sta RgEnemyStun,x
  lda #0
  sta MmEnemyFlash,x
  lda EnemyMetasprite,x
  bne :+
    lda #$ff
  :
  sta LsrFrozenPose,x
  lda EnemyIntervalTimer,x
  sta LsrIntervalTimer,x
  cpx #5
  bcs :+
    lda EnemyFrameTimer,x
    sta LsrFrameTimer,x
  :
  lda #Sfx_EnemySmack
  sta Square1SoundQueue
::EasyLinkBoomStopFinish:
  rts
.endproc

; Old LinkBoomerang.setDir reads the WHOLE display clip before throwStart.
; XML690 gives stand16/jump15/downStart16/downEnd27/upStart26/upEnd28.
; RgThrustReset is the previous checkState pose, so a newly held direction
; chooses START, a retained direction END. Both tiers share all these bounds.
; The output pool is8.8; quantize source Q16 position by dropping its low byte.
.proc EasyLinkBoomOrigin
  lda CrossoverBehaviorVersion
  jeq Easy
  rts
Easy:
  ldx RgSlot
  ldy #0                        ; Whole clip16 by default.
  lda RgBillBurst
  cmp #3
  beq Short
  cmp #17
  bne :+
Short:
    ldy #1                     ; walkStart/jump15.
    bne Height
  :
  cmp #19
  bne :+
    ldy #2                     ; downEnd27.
    bne Height
  :
  cmp #20
  bne :+
    ldy #3                     ; upStart26.
    bne Height
  :
  cmp #21
  bne Height
  ldy #4                       ; upEnd28.
Height:
  sty RgAim                     ; Local index0..4; no persistent pose alias.
  lda Player_X_Position
  clc
  adc #8
  sta RgShotX,x
  lda Player_PageLoc
  adc #0
  sta RgShotPage,x
  lda MmXFraction+1
  sta RgShotFracX,x
  lda SavedJoypadBits
  and #Up_Dir|Down_Dir
  beq Facing
  lda SavedJoypadBits
  and #3
  beq YOrigin                   ; Pure Up/Down uses exact nx, no half-width.
  and #Right_Dir
  bne Right
  beq Left
Facing:
  lda PlayerFacingDir
  cmp #1
  bne Left
Right:
  lda #1
  sta RgShotDir,x
  lda RgShotFracX,x
  clc
  adc #$c0                      ; hWidth13.5 /2 =6.75NES.
  sta RgShotFracX,x
  lda RgShotX,x
  adc #6
  sta RgShotX,x
  lda RgShotPage,x
  adc #0
  sta RgShotPage,x
  jmp YOrigin
Left:
  lda #2
  sta RgShotDir,x
  lda RgShotFracX,x
  sec
  sbc #$c0
  sta RgShotFracX,x
  lda RgShotX,x
  sbc #6
  sta RgShotX,x
  lda RgShotPage,x
  sbc #0
  sta RgShotPage,x
YOrigin:
  ldy RgAim
  lda SavedJoypadBits
  and #Up_Dir
  bne UpOffset
  lda SavedJoypadBits
  and #Down_Dir
  beq HorizontalOffset
  lda SavedJoypadBits
  and #3
  beq FootOffset
  tya
  clc
  adc #10
  tay
  bne Subtract
FootOffset:
  ldy #15
  bne Subtract
HorizontalOffset:
  tya
  clc
  adc #5
  tay
UpOffset:
Subtract:
  lda MmYFraction
  sec
  sbc OffsetLo,y
  lda MmYFraction+1
  sbc OffsetMid,y
  sta RgShotFracY,x
  lda Player_Y_Position
  sbc OffsetHi,y
  clc
  adc #32
  sta RgShotY,x
  ; setDir gives Up priority and Right priority when opposite buttons coexist.
  ; Air movement can retain the old facing, so projectile sign is independent.
  lda RgShotVXLo,x
  ora RgShotVXHi,x
  beq VerticalSign
  lda RgShotDir,x
  cmp #1
  beq WantRight
  lda RgShotVXHi,x
  bmi VerticalSign
  bpl ReverseX
WantRight:
  lda RgShotVXHi,x
  bpl VerticalSign
ReverseX:
  farcall LinkBoomerangSpawn::NegateX
VerticalSign:
  lda SavedJoypadBits
  and #Up_Dir
  beq Finished
  lda RgShotVYHi,x
  bmi Finished
  farcall LinkBoomerangSpawn::NegateY
Finished:
::EasyLinkBoomOriginFinish:
  rts
OffsetLo: .byte $00,$00,$00,$00,$00,$33,$00,$66,$33,$9a,$66,$00,$cd,$66,$33,$00
OffsetMid: .byte $00,$00,$00,$00,$00,$33,$80,$e6,$33,$99,$66,$00,$cc,$66,$33,$00
OffsetHi: .byte $10,$0f,$1b,$1a,$1c,$0b,$0a,$12,$12,$13,$06,$06,$0a,$0a,$0b,$00
.endproc
.proc LsrEffectsBoomerang
  phy
  lda Enemy_ID,x
  cmp #Podoboo
  beq Done
  cmp #$15
  bcc Apply
  cmp #BulletBill_CannonVar
  beq Apply
  cmp #Bowser
  bne Done
Apply:
  lda CrossoverBehaviorVersion
  bne HardBoom
  jsr EasyLinkBoomStop
  jmp Done
HardBoom:
  lda #180
  ldy #0
  farcall LsrEffectsApplyStop
  lda #Sfx_EnemySmack
  sta Square1SoundQueue
Done:
  ply
  rts
.endproc
.proc LinkPrepareContacts
  phx
  phy
  ldx #27
Copy:
  lda BoundingBox_UL_Corner,x
  sta LinkLastBoxes,x
  dex
  bpl Copy
  lda LinkThrustNow
  sta LinkThrustPrev
  lda #0
  sta LinkThrustNow
  sta LinkThrustReceipt
  sta LinkLastValid
  ldx #5
Ids:
  lda Enemy_ID,x
  sta LinkLastIds,x
  lda Enemy_Flag,x
  beq Next
  bpl Onscreen
  lda Enemy_ID,x
  cmp #Bowser
  bne Next                       ; Bowser rear has its own real contact side.
Onscreen:
  lda EnemyOffscrBitsMasked,x
  bne Next
  txa
  asl
  asl
  clc
  adc #4
  tay
  lda LinkLastBoxes+1,y
  cmp LinkLastBoxes+3,y
  bcs Next                       ; Wrapped/offscreen boxes are not a side proof.
  lda LinkLastValid
  ora Bits,x
  sta LinkLastValid
Next:
  dex
  bpl Ids
  lda CrossoverBehaviorVersion
  beq Done
  lda RgThrustReset
  beq Done
  ldx #7
RollBlocks:
  lda RgMeleeBlocks+8,x
  sta RgMeleeBlocks,x
  lda #$ff
  sta RgMeleeBlocks+8,x
  dex
  bpl RollBlocks
Done:
  ply
  plx
  rts
Bits: .byte 1,2,4,8,16,32
.endproc

; ATK_VEC covers Ground and Enemy alike. Reset the complete existing block
; map only at source release/landing/150ms attack or300ms Down timer events.
.proc EasyLinkResetVector
  lda #0
  sta RgMeleeHits
  lda #<RgMeleeBlocks
  sta R0
  lda #>RgMeleeBlocks
  sta R1
  lda #0
  ldy #0
Page:
  sta (R0),y
  iny
  bne Page
  inc R1
  ldy #0
Tail:
  sta (R0),y
  iny
  cpy #160
  bcc Tail
  rts
.endproc
.proc EasyLinkThrustBlock
  lda R3
  jsr BlockBumpedChk
  bcs Attackable
  lda R3
  cmp #$51
  beq Attackable
  cmp #$52
  bne New
  clc
  lda R6
  adc #<(MmSolidTerrain-Block_Buffer_1)
  sta M0
  lda R7
  adc #>(MmSolidTerrain-Block_Buffer_1)
  sta M1
  ldy R2
  lda (M0),y
  bne New
Attackable:
  farcall RosterBlockSeen::Map
  lda (M0),y
  bne Seen
  lda #1
  sta (M0),y
  farcall LinkThrustResponse
  lda RgThrust
  cmp #1
  bne New
  lda MmProbeY
  and #$f0
  farcall LinkClampThrustFeet
New:
  ldx MmSlot
  clc
  rts
Seen:
  ldx MmSlot
  sec
  rts
.endproc

.proc LinkDeferredThrust
  lda CrossoverBehaviorVersion
  beq Done                       ; Easy already resolved the sword first.
  lda TimerControl
  bne Done
  lda GameEngineSubroutine
  cmp #8
  bne Done
  lda RgThrust
  beq Done
  lda LinkThrustReceipt
  ora #$80                       ; High bit selects enemy-only MeleeBridge.
  sta LinkThrustReceipt
  farcall RosterWeapons::MeleeBridge
  lda LinkThrustReceipt
  and #$7f
  sta LinkThrustReceipt
Done:
::LinkDeferredThrustFinish:
  rts
.endproc
.proc LinkClearThrustBlocks
  lda CrossoverBehaviorVersion
  bne Hard
  jsr EasyLinkResetVector
  rts
Hard:
  ldx #15
  lda #$ff
Loop:
  sta RgMeleeBlocks,x
  dex
  bpl Loop
  rts
.endproc
; Original HitTester.animObjHitTest: after the prior sword stops an enemy,
; checkLastHitPoints uses previous PLAYER but CURRENT stunned ENEMY bounds.
; Only this canonical slot's four enemy-cache fields are substituted.
.proc EasyLinkStunnedSide
  lda CrossoverBehaviorVersion
  bne Done
  lda RgEnemyStun,x
  beq Done
  phx
  phy
  txa
  asl
  asl
  clc
  adc #7
  tay
  ldx #3
Copy:
  lda BoundingBox_UL_Corner,y
  sta LinkLastBoxes,y
  dey
  dex
  bpl Copy
  ply
  plx
Done:
  rts
.endproc

.popseg
