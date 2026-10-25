; Positive native-family table and3 own projectiles. No actor-slot eviction.
.pushseg
.segment "KIRBY_ABILITIES"
.proc KbFamilyForEnemy
  cpx #6
  jcs No
  lda Enemy_Flag,x
  jeq No
  jmi No                         ; Bowser/controller duplicates never enter mouth
  lda Enemy_State,x
  and #$20
  jne No
  lda Enemy_ID,x
  cmp #Goomba
  jne Other
  lda Enemy_State,x
  cmp #2
  jcs No
  lda #1
  rts
Other:
  tay
  lda Families,y
  rts
No:
  lda #0
  rts
Families:
  .repeat 256,I
   .if I=::Goomba
    .byte 1
   .elseif I=::GreenKoopa
    .byte 2
   .elseif I=::RedKoopa
    .byte 3
   .elseif I=::BuzzyBeetle
    .byte 4
   .elseif I=::HammerBro
    .byte 5
   .elseif I=::Bloober
    .byte 6
   .elseif I=::GreyCheepCheep
    .byte 7
   .elseif I=::RedCheepCheep .or I=::FlyingCheepCheep
    .byte 8
   .elseif I=::GreenParatroopaJump .or I=::RedParatroopa .or I=::GreenParatroopaFly
    .byte 9
   .elseif I=::Lakitu
    .byte 10
   .elseif I=::Spiny
    .byte 11
   .elseif I=::PiranhaPlant
    .byte 12
   .elseif I=::Podoboo
    .byte 13
   .elseif I=::BulletBill_FrenzyVar .or I=::BulletBill_CannonVar
    .byte 14
   .else
    .byte 0
   .endif
  .endrepeat
.endproc
.proc KbWeapons
  lda KbVariant
  beq :+
  jmp MkWeapons
:
  lda TimerControl
  jne Done
  lda GameEngineSubroutine
  cmp #8
  jne Done
  farcall KbInputs
  lda KbActionAge
  jeq Input
  dec KbActionAge
  jne Input
  lda KbAction
  cmp #1
  jeq Input
  lda #0
  sta KbAction
Input:
  lda KbFresh
  and #Select_Button
  jeq NotDiscard
  jsr KbDropCopy
NotDiscard:
  lda MmUnderwater
  jeq LandWeapons
  lda SavedJoypadBits
  and #B_Button
  jeq Update
  lda KbCooldown
  jne Update
  lda #3
  jsr Spawn
  jcc Update
  lda #7
  sta KbShotKind,x
  lda #6
  sta KbAction
  lda #12
  sta KbActionAge
  sta KbCooldown
  lda SavedJoypadBits
  and #Up_Dir|Down_Dir
  jeq WaterSound
  lda #0
  sta KbShotVXHi,x
  lda SavedJoypadBits
  and #Down_Dir
  jeq WaterUp
  lda #3
  jne WaterAim
WaterUp:
  lda #$fd
WaterAim:
  sta KbShotVYHi,x
WaterSound:
  lda #Sfx_Fireball
  sta Square1SoundQueue
  jmp Update
LandWeapons:
  lda KbMouth
  jeq Empty
  lda SavedJoypadBits
  and #Down_Dir
  jne Swallow
  lda KbFresh
  and #B_Button
  jeq Update
  lda #1
  jsr Spawn
  jcc Update                     ; a full pool keeps the held enemy
  lda #0
  sta KbMouth
  lda #2
  sta KbAction
  lda #24
  sta KbActionAge
  lda #Sfx_Fireball
  sta Square1SoundQueue
  jmp Update
Swallow:
  lda KbMouthCopy
  sta KbCopy
  lda #0
  sta KbMouth
  lda #3
  sta KbAction
  lda #24
  sta KbActionAge
  lda #Sfx_PowerUpGrab
  sta Square2SoundQueue
  jmp Update
Empty:
  lda KbFloat
  jeq NotFloat
  lda KbFresh
  and #B_Button
  jeq Update
  lda #2
  jsr Spawn
  jcc Update
  lda #0
  sta KbFloat
  lda #2
  sta KbAction
  lda #24
  sta KbActionAge
  lda #Sfx_Fireball
  sta Square1SoundQueue
  jmp Update
NotFloat:
  lda KbCopy
  jeq Inhale
  lda SavedJoypadBits
  and #B_Button
  jeq CopyOff
  lda KbCooldown
  jne Update
  jsr CopyAttack
  jmp Update
CopyOff:
  lda KbAction
  cmp #4
  jne Update
  lda KbCopy
  cmp #4
  jeq CancelCopy
  cmp #10
  jne Update
CancelCopy:
  lda #0
  sta KbAction
  jeq Update
Inhale:
  lda KbAction
  cmp #5
  jeq Update
  lda SavedJoypadBits
  and #B_Button
  jeq StopInhale
  lda KbAction
  cmp #1
  jeq Pull
  lda #1
  sta KbAction
  lda #8
  sta KbActionAge
  lda #Sfx_Bump
  sta Square1SoundQueue
Pull:
  lda KbActionAge
  jne Update
  jsr Suction
  jmp Update
StopInhale:
  lda KbAction
  cmp #1
  jne Update
  lda #0
  sta KbAction
Update:
  lda KbAction
  cmp #4
  jne NotBite
  lda KbCopy
  cmp #12
  jne NotBite
  jsr BiteContacts
NotBite:
  jsr DropUpdate
  jsr Shots
Done:
  rts
Suction:
  lda ObjectOffset
  sta KbSavedObject
  ldx #5
NextPull:
  stx KbPullSlot
  jsr KbFamilyForEnemy
  jeq PullNext
  sta KbTemp2
  lda Enemy_X_Position,x
  sec
  sbc Player_X_Position
  sta KbTempX
  lda Enemy_PageLoc,x
  sbc Player_PageLoc
  sta KbTempPage
  lda PlayerFacingDir
  cmp #1
  jeq PullRight
  sec
  lda #0
  sbc KbTempX
  sta KbTempX
  lda #0
  sbc KbTempPage
  sta KbTempPage
PullRight:
  lda KbTempPage
  jne PullNext
  lda KbTempX
  cmp #57
  jcs PullNext
  jsr KbInhaleVertical
  jcc PullNext
  lda KbTempX
  cmp #13
  jcc Capture
  lda PlayerFacingDir
  cmp #1
  jne PullLeft
  sec
  lda Enemy_X_Position,x
  sbc #2
  sta Enemy_X_Position,x
  lda Enemy_PageLoc,x
  sbc #0
  sta Enemy_PageLoc,x
  jmp PullY
PullLeft:
  clc
  lda Enemy_X_Position,x
  adc #2
  sta Enemy_X_Position,x
  lda Enemy_PageLoc,x
  adc #0
  sta Enemy_PageLoc,x
PullY:
  lda #0
  sta Enemy_Y_Speed,x
  sta Enemy_Y_MoveForce,x
  jsr KbInhaleTargetY
  cmp Enemy_Y_Position,x
  jeq PullDone
  jcs PullDown
  dec Enemy_Y_Position,x
  jmp PullDone
PullDown:
  inc Enemy_Y_Position,x
PullDone:
  jmp PullReturn
Capture:
  lda Enemy_ID,x
  clc
  adc #1
  sta KbMouth
  lda KbTemp2
  sta KbMouthCopy
  stx ObjectOffset
  lda #1
  jsr SetupFloateyNumber
  ldx KbPullSlot
  jsr EraseEnemyObject
  lda #0
  sta KbAction
  lda #Sfx_CoinGrab
  sta Square2SoundQueue
  jmp PullReturn
PullNext:
  dex
  jpl NextPull
  lda KbDropKind
  jeq PullReturn
  lda KbDropX
  sec
  sbc Player_X_Position
  sta KbTempX
  lda KbDropPage
  sbc Player_PageLoc
  sta KbTempPage
  lda KbTempX
  clc
  adc #16
  sta KbTempX
  lda KbTempPage
  adc #0
  jne PullReturn
  lda KbTempX
  cmp #48
  jcs PullReturn
  lda KbDropY
  sec
  sbc Player_Y_Position
  cmp #48
  jcs PullReturn
  lda KbDropKind
  sta KbMouthCopy
  lda #$ff
  sta KbMouth
  lda #0
  sta KbDropKind
  sta KbAction
PullReturn:
  lda KbSavedObject
  sta ObjectOffset
  rts
CopyAttack:
  lda #4
  sta KbAction
  lda #16
  sta KbActionAge
  lda #20
  sta KbCooldown
  lda KbCopy
  cmp #1
  jeq Body
  cmp #4
  jeq Body
  cmp #9
  jeq Body
  cmp #10
  jeq Body
  cmp #11
  jeq Needles
  cmp #12
  jeq Body
  cmp #14
  jeq Body
  cmp #13
  jne Projectile
  lda #8
  sta KbCooldown
Projectile:
  lda #3
  jsr Spawn
  jcc CopyReturn
  lda KbCopy
  sta KbShotKind,x
  cmp #5
  jne NotHammer
  lda #0
  sta KbShotVYLo,x
  lda #$fd
  sta KbShotVYHi,x
NotHammer:
  cmp #6
  jne NotJet
  lda #0
  sta KbShotVXHi,x
  lda #$fd
  sta KbShotVYHi,x
NotJet:
  lda KbCopy
  cmp #7
  jne NotBubble
  lda #2
  ldy KbShotDir,x
  cpy #2
  bne :+
  lda #$fe
  :sta KbShotVXHi,x
NotBubble:
  lda #Sfx_Fireball
  sta Square1SoundQueue
  rts
Body:
  lda KbCopy
  cmp #4
  jeq ContinuousBody
  cmp #10
  jne BodySound
ContinuousBody:
  lda #2
  sta KbActionAge
  lda #1
  sta KbCooldown
BodySound:
  lda #Sfx_EnemySmack
  sta Square1SoundQueue
CopyReturn:
  rts
Needles:
  ldy #0
NeedleLoop:
  sty KbAttackBits
  lda #3
  jsr Spawn
  jcc CopyReturn
  lda #11
  sta KbShotKind,x
  ldy KbAttackBits
  lda NeedleVX,y
  sta KbShotVXHi,x
  lda NeedleVY,y
  sta KbShotVYHi,x
  iny
  cpy #3
  jcc NeedleLoop
  lda #Sfx_Fireball
  sta Square1SoundQueue
  rts
NeedleVX:.byte $fe,0,2
NeedleVY:.byte $ff,$fd,$ff
Spawn:
  pha
  ldx #0
Find:
  lda KbShotType,x
  jeq Found
  inx
  cpx #3
  jcc Find
  pla
  clc
  rts
Found:
  pla
  sta KbShotType,x
  lda #0
  sta KbShotFX,x
  sta KbShotFY,x
  sta KbShotAge,x
  sta KbShotHits,x
  sta KbShotKind,x
  sta KbShotVXLo,x
  sta KbShotVYLo,x
  sta KbShotVYHi,x
  lda Player_X_Position
  sta KbShotX,x
  lda Player_PageLoc
  sta KbShotPage,x
  lda Player_Y_Position
  clc
  adc #20
  sta KbShotY,x
  lda PlayerFacingDir
  sta KbShotDir,x
  cmp #2
  jeq Left
  lda #4
  sta KbShotVXHi,x
  clc
  lda KbShotX,x
  adc #16
  sta KbShotX,x
  lda KbShotPage,x
  adc #0
  sta KbShotPage,x
  sec
  rts
Left:
  lda #$fc
  sta KbShotVXHi,x
  sec
  rts
Shots:
  ldx #0
Loop:
  stx KbSavedSlot
  lda KbShotType,x
  jeq Next
  inc KbShotAge,x
  lda KbShotAge,x
  cmp #90
  jcs Kill
  lda KbShotType,x
  cmp #2
  jne CopyMotion
  lda KbShotAge,x
  cmp #24
  jcs Kill
  cmp #9
  jcc Move
  cmp #12
  jcc AirOne
  cmp #14
  jcc AirHalf
  cmp #16
  jcc AirThird
  lda #0
  sta KbShotVXHi,x
  sta KbShotVXLo,x
  jmp Move
AirOne:
  lda #1
  sta KbShotVXHi,x
  lda #0
  jeq AirFraction
AirHalf:
  lda #$80
  jne AirSlow
AirThird:
  lda #$55
AirSlow:
  pha
  lda #0
  sta KbShotVXHi,x
  pla
AirFraction:
  sta KbShotVXLo,x
  ldy KbShotDir,x
  cpy #2
  jne Move
  sec
  lda #0
  sbc KbShotVXLo,x
  sta KbShotVXLo,x
  lda #0
  sbc KbShotVXHi,x
  sta KbShotVXHi,x
  jmp Move
CopyMotion:
  lda KbShotKind,x
  cmp #13
  jne NotFire
  lda KbShotAge,x
  cmp #20
  jcs Kill
NotFire:
  lda KbShotKind,x
  cmp #2
  jeq Arc
  cmp #11
  jeq Arc
  cmp #5
  jne NotArc
Arc:
  clc
  lda KbShotVYLo,x
  adc #32
  sta KbShotVYLo,x
  lda KbShotVYHi,x
  adc #0
  sta KbShotVYHi,x
NotArc:
  lda KbShotKind,x
  cmp #3
  jne NotReturn
  lda KbShotAge,x
  cmp #24
  jcc NotReturn
  lda KbShotX,x
  cmp Player_X_Position
  lda KbShotPage,x
  sbc Player_PageLoc
  lda #3
  jcc ReturnSpeed
  lda #$fd
ReturnSpeed:
  sta KbShotVXHi,x
NotReturn:
  lda KbShotKind,x
  cmp #8
  jne Move
  lda KbShotAge,x
  and #8
  jeq WaveDown
  lda #1
  jne Wave
WaveDown:
  ; Start upward from the mouth. The opposite phase drove this16px effect
  ; into the floor within five updates. These same8-update half waves now
  ; stay above the ground without changing their speed, lifetime or CPU cost.
  lda #$ff
Wave:
  sta KbShotVYHi,x
Move:
  clc
  lda KbShotFX,x
  adc KbShotVXLo,x
  sta KbShotFX,x
  lda KbShotX,x
  adc KbShotVXHi,x
  sta KbShotX,x
  lda #0
  ldy KbShotVXHi,x
  bpl :+
  lda #$ff
:
  adc KbShotPage,x
  sta KbShotPage,x
  clc
  lda KbShotFY,x
  adc KbShotVYLo,x
  sta KbShotFY,x
  lda KbShotY,x
  adc KbShotVYHi,x
  sta KbShotY,x
  cmp #32
  jcc Kill
  cmp #232
  jcs Kill
  lda KbShotKind,x
  cmp #2
  jne FloorDone
  jsr ShotFloor
  ldx KbSavedSlot
FloorDone:
  lda KbShotX,x
  sec
  sbc ScreenLeft_X_Pos
  lda KbShotPage,x
  sbc ScreenLeft_PageLoc
  jne Kill
  jsr BlockProxy
  ldx KbSavedSlot
  lda KbShotType,x
  jeq Next
  jsr EnemyContacts
  jmp Next
Kill:
  lda #0
  sta KbShotType,x
Next:
  ldx KbSavedSlot
  inx
  cpx #3
  jcc Loop
  rts
BlockProxy:
  lda KbShotType,x
  cmp #2
  jeq NoBlock                 ; air puff cannot mutate protected level terrain
  lda KbShotX,x
  sta MmBulletX
  lda KbShotPage,x
  sta MmBulletPage
  lda KbShotY,x
  sta MmBulletY
  lda KbShotDir,x
  sta MmBulletDir
  lda #3                     ; established strict brick/question policy
  sta MmBulletType
  ldx #0
  stx MmSlot
  farcall MegaManWeapons::Blocks
  lda MmBulletType
  jne ClearProxy
  ldx KbSavedSlot
  lda #0
  sta KbShotType,x
ClearProxy:
  lda #0
  sta MmBulletType
NoBlock:
  rts
ShotFloor:
  lda KbShotY,x
  clc
  adc #8
  sta KbTempY
  lda KbShotX,x
  clc
  adc #8
  sta KbTempX
  lda KbShotPage,x
  adc #0
  sta KbTempPage
  jsr SolidPoint
  jcc FloorNo
  lda KbShotVYHi,x
  jmi FloorNo
  lda KbTempY
  and #$f0
  sec
  sbc #8
  sta KbShotY,x
  lda #0
  sta KbShotVYHi,x
  sta KbShotVYLo,x
  sta KbShotFY,x
FloorNo:rts
SolidPoint:
  lda KbTempY
  cmp #$20
  jcc EmptyPoint
  cmp #$f0
  jcs EmptyPoint
  and #$f0
  sec
  sbc #$20
  sta R2
  lda KbTempX
  lsr
  lsr
  lsr
  lsr
  sta KbTemp
  lda KbTempPage
  and #1
  asl
  asl
  asl
  asl
  ora KbTemp
  jsr GetBlockBufferAddr
  ldy R2
  lda (R6),y
  tay
  lda MTileAttribute,y
  and #MTILE_SOLID
  jeq EmptyPoint
  sec
  rts
EmptyPoint:
  clc
  rts
EnemyContacts:
  lda ObjectOffset
  sta KbSavedObject
  ldx #5
Enemy:
  stx KbPullSlot
  jsr KbFamilyForEnemy
  jne OrdinaryEnemy
  lda Enemy_Flag,x
  jeq NextEnemy
  jmi NextEnemy
  lda Enemy_ID,x
  cmp #Bowser
  jne NextEnemy
OrdinaryEnemy:
  ldy KbSavedSlot
  lda Enemy_X_Position,x
  sec
  sbc KbShotX,y
  sta KbTempX
  lda Enemy_PageLoc,x
  sbc KbShotPage,y
  sta KbTempPage
  lda KbTempX
  clc
  adc #12
  sta KbTempX
  lda KbTempPage
  adc #0
  jne NextEnemy
  lda KbTempX
  cmp #25
  jcs NextEnemy
  lda Enemy_Y_Position,x
  sec
  sbc KbShotY,y
  clc
  adc #12
  cmp #25
  jcs NextEnemy
  stx ObjectOffset
  lda Enemy_ID,x
  cmp #Bowser
  jne Defeat
  stx R1
  jsr HandleEnemyFBallCol
  jmp Consumed
Defeat:
  jsr ShellOrBlockDefeat
Consumed:
  ldx KbSavedSlot
  lda #0
  sta KbShotType,x
  jmp EnemyDone
NextEnemy:
  dex
  jpl Enemy
EnemyDone:
  lda KbSavedObject
  sta ObjectOffset
  rts
DropUpdate:
  lda KbDropKind
  jeq DropDone
  inc KbDropAge
  jne DropMove
  lda #0
  sta KbDropKind
  jeq DropDone
DropMove:
  lda KbDropAge
  and #1
  jne DropDone
  lda KbDropAge
  and #7
  jne DropVelocity
  lda KbDropVY
  cmp #3
  jeq DropVelocity
  inc KbDropVY
DropVelocity:
  lda KbDropY
  clc
  adc KbDropVY
  sta KbDropY
  cmp #32
  jcc DropKill
  cmp #232
  jcs DropKill
  lda KbDropX
  clc
  adc KbDropDX
  sta KbDropX
  lda KbDropPage
  ldx KbDropDX
  bpl :+
  sbc #0
  jmp DropPage
  :adc #0
DropPage:
  sta KbDropPage
  lda KbDropY
  clc
  adc #8
  sta KbTempY
  lda KbDropX
  sta KbTempX
  lda KbDropPage
  sta KbTempPage
  jsr SolidPoint
  jcc DropDone
  lda KbDropVY
  jmi DropDone
  lda KbTempY
  and #$f0
  sec
  sbc #8
  sta KbDropY
  lda #$fe
  sta KbDropVY
  jne DropDone
DropKill:
  lda #0
  sta KbDropKind
DropDone:
  rts
BiteContacts:
  lda ObjectOffset
  sta KbSavedObject
  ldx #5
BiteLoop:
  stx KbPullSlot
  jsr KbFamilyForEnemy
  jeq BiteNext
  lda Enemy_X_Position,x
  sec
  sbc Player_X_Position
  sta KbTempX
  lda Enemy_PageLoc,x
  sbc Player_PageLoc
  sta KbTempPage
  lda PlayerFacingDir
  cmp #2
  jne BiteRight
  sec
  lda #0
  sbc KbTempX
  sta KbTempX
  lda #0
  sbc KbTempPage
  sta KbTempPage
BiteRight:
  lda KbTempPage
  jne BiteNext
  lda KbTempX
  cmp #41
  jcs BiteNext
  lda Enemy_Y_Position,x
  sec
  sbc Player_Y_Position
  clc
  adc #2
  cmp #37
  jcs BiteNext
  stx ObjectOffset
  jsr ShellOrBlockDefeat
BiteNext:
  ldx KbPullSlot
  dex
  jpl BiteLoop
  lda KbSavedObject
  sta ObjectOffset
  rts
.endproc

.proc KbDropCopy
  lda KbCopy
  jeq Done
  sta KbDropKind
  lda #0
  sta KbCopy
  sta KbDropAge
  lda Player_X_Position
  sta KbDropX
  lda Player_PageLoc
  sta KbDropPage
  lda Player_Y_Position
  clc
  adc #20
  sta KbDropY
  lda #$fe
  sta KbDropVY
  lda #1
  ldx PlayerFacingDir
  cpx #2
  bne :+
  lda #$ff
  :sta KbDropDX
Done:
  rts
.endproc

.proc KbAbilityMove
  lda KbAction
  cmp #4
  jne Done
  lda KbCopy
  cmp #1
  jeq GroundCharge
  cmp #14
  jeq BulletDash
  cmp #4
  jeq Guard
  cmp #9
  jeq HiJump
  cmp #10
  jeq Cloud
  rts
GroundCharge:
  lda Player_State
  jne Done
BulletDash:
  lda KbCopy
  cmp #14
  jne ChargeX
  lda #0
  sta MmVY+1
  sta MmVY+2
ChargeX:
  lda #0
  sta MmVX+1
  lda #3
  sta MmVX+2
  lda PlayerFacingDir
  cmp #2
  jne Done
  lda #$fd
  sta MmVX+2
  rts
Guard:
  lda Player_State
  jne Done
  lda #0
  sta MmVX+1
  sta MmVX+2
  rts
HiJump:
  lda KbActionAge
  cmp #15
  jne Done
  lda #0
  sta MmVY+1
  lda #$fa
  sta MmVY+2
  sta Player_Y_Speed
  lda #1
  sta Player_State
  rts
Cloud:
  lda SavedJoypadBits
  and #B_Button
  jeq Done
  lda #0
  sta MmVY+1
  sta MmVY+2
Done:
  rts
.endproc

.proc KbBodyContact
  lda KbHurt
  jeq NotHurt
  sec
  rts
NotHurt:
  jsr KbFamilyForEnemy
  jeq No
  lda KbVariant
  jne OrdinaryAttack
  lda KbAction
  cmp #1
  jne OrdinaryAttack
  ; Only an edible enemy in front of an active mouth is protected. Back,
  ; startup, released-B, hazard and Meta Knight contacts remain ordinary.
  lda KbActionAge
  jne No
  lda SavedJoypadBits
  and #B_Button
  jeq No
  jsr KbInhaleVertical
  jcc No
  lda Enemy_X_Position,x
  sec
  sbc Player_X_Position
  sta KbTempX
  lda Enemy_PageLoc,x
  sbc Player_PageLoc
  sta KbTempPage
  lda PlayerFacingDir
  cmp #1
  jeq MouthFront
  sec
  lda #0
  sbc KbTempX
  sta KbTempX
  lda #0
  sbc KbTempPage
  sta KbTempPage
MouthFront:
  lda KbTempPage
  jne No
  lda KbTempX
  cmp #57
  jcs No
  sec
  rts
OrdinaryAttack:
  lda KbAction
  cmp #5
  jeq Defeat
  cmp #4
  jne No
  lda KbCopy
  cmp #4
  jne NotGuard
  lda Enemy_ID,x
  cmp #Podoboo
  jeq No
  sec
  rts
NotGuard:
  cmp #1
  jeq Defeat
  cmp #9
  jeq Defeat
  cmp #11
  jeq Defeat
  cmp #12
  jeq Defeat
  cmp #14
  jne No
Defeat:
  phx
  lda ObjectOffset
  pha
  stx ObjectOffset
  jsr ShellOrBlockDefeat
  pla
  sta ObjectOffset
  plx
Protected:
  sec
  rts
No:
  clc
  rts
.endproc
.popseg






.pushseg
.segment "KIRBY_ABILITIES"
.proc KbInhaleTargetY
  ; Native ground enemies share the origin+24 foot even when the artwork
  ; is taller. Kirby's foot is origin+32. Keep their feet level: deriving
  ; this from sprite height would bury tall Koopas four pixels in the floor.
  lda #8
  clc
  adc Player_Y_Position
  rts
.endproc
.proc KbInhaleVertical
  jsr KbInhaleTargetY
  sta KbTempY
  lda Enemy_Y_HighPos,x
  cmp #1
  bne No
  lda Enemy_Y_Position,x
  sec
  sbc KbTempY
  clc
  adc #12
  cmp #25
  bcs No
  sec
  rts
No:
  clc
  rts
.endproc
.popseg
