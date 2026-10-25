; Playable NES boss adaptation: native sword poses and phases; no flight.
.export MkWeapons,MkGraphics,MkSetPose,MkMovementInput,MkClampOamPriority,KbOamPriority
.pushseg
.segment "KIRBY_CORE"
.proc KbOamPriority
  ; Exact former resident rotation; cold only on the expanded target.
  lda RgOamUsed
  beq First
  lsr
  lsr
  tax
  lda Steps,x
  clc
  adc RgOamFirst
  bcs Wrap
  cmp RgOamUsed
  bcc Ready
Wrap:
  sec
  sbc RgOamUsed
  jmp Ready
First:
  lda #0
Ready:
  sta RgOamFirst
  ldx SelectedCharacter
  cpx #CHARACTER_KIRBY
  bne Rotation
  ldx KbVariant
  beq Rotation
  jsr MkClampOamPriority
Rotation:
  lda RgOamFirst
  eor #$ff
  clc
  adc #1
  sta RgOamRotation
  rts
Steps:
  .byte 0
  .repeat 63,I
    .scope
      N=I+1
      .if N=1
        .byte 0
      .elseif (N .mod 7)=0
        .if (N .mod 5)=0
          .byte (3 .mod N)*4
        .else
          .byte (5 .mod N)*4
        .endif
      .else
        .byte (7 .mod N)*4
      .endif
    .endscope
  .endrepeat
.endproc
.proc MkClampOamPriority
  ; DrawAll calls only for Meta, before any rotated-ring writes. His only
  ; active pre-body output is the three health sprites (12bytes). Never put
  ; the ring's priority pivot INSIDE his body: that would reorder overlapping
  ; native parts at the63/0 boundary. Skip to the END, retaining guest flicker.
  lda SmPosePtr+1
  cmp #$c0
  bcc Done
  cmp #$e0
  bcs Done
  lda CurrentBankC
  pha
  BankPRGC #.bank(KbArtStart)
  lda SmPosePtr
  sta R0
  lda SmPosePtr+1
  sta R1
  ldy #0
  lda (R0),y
  sta KbTemp
  pla
  BankPRGC a
  lda KbTemp
  beq Done
  cmp #48
  bcs Done
  and #3
  bne Done
  lda #0
  sta KbTemp2
  lda GameEngineSubroutine
  cmp #8
  bne SpanReady
  lda MmDeathFlag
  bne SpanReady
  lda #12
  sta KbTemp2
SpanReady:
  lda KbTemp2
  clc
  adc KbTemp
  sta KbTemp
  lda RgOamFirst
  cmp KbTemp2
  bcc Done
  beq Done
  cmp KbTemp
  bcs Done
  lda KbTemp
  sta RgOamFirst
Done:
  lda RgOamFirst
  rts
.endproc
.proc MkMovementInput
  lda #0
  sta KbCopy
  sta KbMouth
  sta KbFloat
  lda KbAction
  cmp #7
  jne Done
  lda MkCombo
  cmp #3
  jeq Done
  cmp #4
  beq Plunge
  lda Player_State
  bne Done
  lda #0
  sta MmVX
  sta MmVX+1
  sta MmVX+2
  lda MkCombo
  cmp #5
  bne Lunge
  lda #$c0
  ldy #1
  bne SetX
Lunge:
  cmp #2
  bne Done
  lda MkMoveTick
  cmp #10
  bcc Done
  cmp #36
  bcs Done
  lda #$80
  ldy #2
SetX:
  sta MmVX+1
  sty MmVX+2
  lda MkAttackDir
  cmp #2
  bne Done
  sec
  lda #0
  sbc MmVX+1
  sta MmVX+1
  lda #0
  sbc MmVX+2
  sta MmVX+2
  rts
Plunge:
  lda #0
  sta MmVX
  sta MmVX+1
  sta MmVX+2
  sta KbJumpPhase
  lda MkMoveTick
  cmp #32
  bcc Hover
  bne Done
  lda #2
  sta MmVY+2
  lda #0
  sta MmVY
  sta MmVY+1
  rts
Hover:
  lda #0
  sta MmVY
  sta MmVY+1
  sta MmVY+2
Done:rts
.endproc
.proc MkGraphics
  lda Player_SprAttrib
  and #$fc
  sta Player_SprAttrib
  ldx #8
  lda GameEngineSubroutine
  cmp #11
  bne Alive
  ldx #$38
  jmp Facing
Alive:
  lda KbHurtMove
  beq Action
  ldx #$36
  jmp Facing
Action:
  lda KbAction
  cmp #7
  bne NotAttack
  BankPRGC #.bank(KbArtStart)
  ldx MkCombo
  lda MkActionLo,x
  sta R0
  lda MkActionHi,x
  sta R1
  ldy MkMoveTick
  lda (R0),y
  tax
  lda MkCombo
  cmp #3
  bne AttackFacing
  lda MkAttackDir
  cmp #2
  bne SpinPose
  txa
  sta KbTemp
  lda #$83
  sec
  sbc KbTemp
  tax
SpinPose:
  jmp MkSetPose
AttackFacing:
  lda MkAttackDir
  jmp Direction
NotAttack:
  lda RgCrouch
  beq NotCrouch
  ldx #$14
  bne Facing
NotCrouch:
  lda Player_State
  beq Ground
  ; Native jump:32/34/36/38/3A for4/15/9/6/5 updates, then34.
  ; Pose38 is the transient dark cape, not the permanent falling pose.
  ldx #$32
  lda KbJumpAge
  cmp #5
  bcc Facing
  ldx #$34
  cmp #20
  bcc Facing
  ldx #$36
  cmp #29
  bcc Facing
  ldx #$38
  cmp #35
  bcc Facing
  ldx #$3a
  cmp #40
  bcc Facing
  ldx #$34
  bne Facing
Ground:
  lda Player_X_Speed
  beq Facing
  lda KbClock
  lsr
  lsr
  and #7
  tay
  ldx WalkPoses,y
Facing:
  lda PlayerFacingDir
Direction:
  cmp #2
  bne :+
  inx
: jmp MkSetPose
WalkPoses: .byte $10,$12,$10,$0e,$0c,$0a,$0c,$0e
.endproc
.proc MkSetPose
  BankPRGC #.bank(KbArtStart)
  stx KbPose
  lda MkBodyChr,x
  sta SmChrBank
  lda MkBodyLo,x
  sta SmPosePtr
  lda MkBodyHi,x
  sta SmPosePtr+1
  lda #METASPRITE_SAMUS_BODY
  sta ObjectMetasprite
  lda #1
  sta KbPoseChr
  ; KbDrawShots publishes this page when it builds the corresponding OAM.
  rts
.endproc
.segment "KIRBY_ABILITIES"
.proc MkWeapons
  lda TimerControl
  jne Done
  lda GameEngineSubroutine
  cmp #8
  jne Done
  lda MmDeathFlag
  jne Done
  farcall KbInputs
  lda KbAction
  cmp #7
  jne Input
  lda MkCombo
  cmp #4
  bne Age
  lda MkMoveTick
  cmp #32
  bcc Age
  lda Player_State
  bne Age
  lda #6
  sta MkCombo
  lda #0
  sta MkMoveTick
  BankPRGC #.bank(KbArtStart)
  lda MkActionLength+6
  sta KbActionAge
  lda #Sfx_Bump
  sta Square1SoundQueue
  jmp Contact
Age:
  inc MkMoveTick
  lda KbActionAge
  beq EndMove
  dec KbActionAge
  jne Contact
  lda MkCombo
  cmp #4
  bne EndMove
  dec MkMoveTick
  inc KbActionAge
  jmp Contact
EndMove:
  lda #0
  sta KbAction
Input:
  lda KbHurtMove
  jne Done
  lda KbFresh
  and #Select_Button
  beq SwordInput
  lda Player_State
  jne Done
  lda #2
  bne Start
SwordInput:
  lda KbFresh
  and #B_Button
  jeq Done
  lda Player_State
  beq GroundInput
  lda SavedJoypadBits
  and #Down_Dir
  beq Spin
  lda #4
  bne Start
Spin:
  lda #3
  bne Start
GroundInput:
  lda SavedJoypadBits
  and #Up_Dir
  beq ChargeInput
  lda #1
  bne Start
ChargeInput:
  lda SavedJoypadBits
  and #Left_Dir|Right_Dir
  beq FirstSwing
  lda #5
  bne Start
FirstSwing:
  lda #0
Start:
  sta MkCombo
  lda #0
  sta MkMoveTick
  sta MkHitBits
  sta MkBlockHit
  lda PlayerFacingDir
  sta MkAttackDir
  lda #7
  sta KbAction
  BankPRGC #.bank(KbArtStart)
  ldx MkCombo
  lda MkActionLength,x
  sta KbActionAge
  lda #Sfx_Fireball
  sta Square1SoundQueue
Contact:
  lda KbAction
  cmp #7
  bne Done
  farcall MkGraphics
  jsr DamagePhase
  lda MkDamage
  beq Done
  jsr Bounds
  bcc Done
  jsr Blocks
  jsr Enemies
Done:rts
DamagePhase:
  lda #0
  sta MkDamage
  ldx MkCombo
  cpx #6
  beq PhaseDone
  lda MkMoveTick
  cpx #0
  beq SlashPhase
  cpx #1
  beq TriplePhase
  cpx #2
  beq LungePhase
  cpx #4
  beq PlungePhase
  bne Active
SlashPhase:
  cmp #4
  bcc PhaseDone
  cmp #32
  bcs PhaseDone
  bcc Active
TriplePhase:
  cmp #48
  bcs PhaseDone
  bcc Active
LungePhase:
  cmp #10
  bcc PhaseDone
  cmp #58
  bcs PhaseDone
  bcc Active
PlungePhase:
  cmp #32
  bcc PhaseDone
Active:
  inc MkDamage
PhaseDone:rts
Bounds:
  BankPRGC #.bank(KbArtStart)
  ldx KbPose
  lda MkSwordWidth,x
  sta MkRectW
  beq NoBounds
  lda MkSwordHeight,x
  sta MkRectH
  beq NoBounds
  lda MkSwordLeft,x
  sta MkSwordLeftValue
  clc
  adc Player_X_Position
  sta MkRectX
  lda #0
  bit MkSwordLeftValue
  bpl :+
  lda #$ff
: adc Player_PageLoc
  sta MkRectPage
  lda MkSwordTop,x
  sta MkSwordTopValue
  clc
  adc Player_Y_Position
  sta MkRectY
  lda #0
  bit MkSwordTopValue
  bpl :+
  lda #$ff
: adc Player_Y_HighPos
  cmp #1
  bne NoBounds
  sec
  rts
NoBounds:
  clc
  rts
Blocks:
  lda MkBlockHit
  bne BlockDone
  lda MkRectX
  sta MmBulletX
  lda MkRectPage
  sta MmBulletPage
  lda MkAttackDir
  sta MmBulletDir
  cmp #2
  beq BlockY
  lda MkRectW
  sec
  sbc #1
  clc
  adc MkRectX
  sta MmBulletX
  lda MkRectPage
  adc #0
  sta MmBulletPage
BlockY:
  lda MkRectH
  lsr
  clc
  adc MkRectY
  sta MmBulletY
  lda #3
  sta MmBulletType
  ldx #0
  stx MmSlot
  ; A sword tip is a point, not a charged buster's wide rectangle. Reuse the
  ; strict single-cell dispatcher with sword damage, so an adjacent wall
  ; cannot intercept the intended question block or shift its reward.
  farcall MegaManWeapons::BombPoint
  lda MmBulletType
  beq MarkBlock
  lda MmBreakBlock
  beq ClearProxy
MarkBlock:
  inc MkBlockHit
ClearProxy:
  lda #0
  sta MmBulletType
BlockDone:rts
Enemies:
  lda ObjectOffset
  sta KbSavedObject
  ldx #5
Loop:
  stx KbPullSlot
  jsr KbFamilyForEnemy
  bne Eligible
  lda Enemy_Flag,x
  jeq Next
  jmi Next
  lda Enemy_ID,x
  cmp #Bowser
  jne Next
Eligible:
  lda BitMask,x
  and MkHitBits
  jne Next
  lda Enemy_Y_HighPos,x
  cmp #1
  jne Next
  lda Enemy_X_Position,x
  sec
  sbc MkRectX
  sta KbTempX
  lda Enemy_PageLoc,x
  sbc MkRectPage
  sta KbTempPage
Right:
  lda KbTempX
  clc
  adc #15
  sta KbTempX
  lda KbTempPage
  adc #0
  bne Next
  lda MkRectW
  clc
  adc #15
  cmp KbTempX
  bcc Next
  beq Next
  lda Enemy_Y_Position,x
  sec
  sbc MkRectY
  sta KbTempY
  lda #0
  sbc #0
  sta KbTempPage
  lda KbTempY
  clc
  adc #23
  sta KbTempY
  lda KbTempPage
  adc #0
  bne Next
  lda MkRectH
  clc
  adc #23
  cmp KbTempY
  bcc Next
  beq Next
  lda BitMask,x
  ora MkHitBits
  sta MkHitBits
  stx ObjectOffset
  lda Enemy_ID,x
  cmp #Bowser
  bne Defeat
  stx R1
  jsr HandleEnemyFBallCol
  jmp Hit
Defeat:
  jsr ShellOrBlockDefeat
Hit:
  lda #Sfx_EnemySmack
  sta Square1SoundQueue
Next:
  ldx KbPullSlot
  dex
  jpl Loop
  lda KbSavedObject
  sta ObjectOffset
  rts
BitMask:.byte 1,2,4,8,16,32
.endproc
.popseg
