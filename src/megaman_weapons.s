; Weapon rules from the pinned hosted game. Coordinates are NES pixels.
.pushseg
.segment "SRAM"
MegaManRamStart:
MmDeathFlag: .res 1
MmDeathPit: .res 1
MmDeathAge: .res 1
MmDeathX: .res 1
MmDeathPage: .res 1
MmDeathY: .res 1
MmDeathYHigh: .res 1
MmDeathPart: .res 1
MmDeathDistance: .res 2
MmDeathMetasprite: .res 1
MmChargeFrames: .res 1
MmCharging: .res 1
MmOnVine: .res 1
MmVineExit: .res 1
MmVineX: .res 1
MmVineButtons: .res 1
MmVineLastButtons: .res 1
MmClimbFrame: .res 1
MmClimbTimer: .res 1
MmFlashTick: .res 1
MmFlashPhase: .res 1
MmPaletteIndex: .res 1
MmLastPalette: .res 1
MmBulletType: .res 4
MmBulletX: .res 4
MmBulletPage: .res 4
MmBulletY: .res 4
MmBulletFracLo: .res 4
MmBulletFracHi: .res 4
MmBulletDir: .res 4
MmBulletAge: .res 4
MmEnemyHealthLo: .res 6
MmEnemyHealthHi: .res 6
MmEnemyFlash: .res 6
MmBrickHealth: .res 416
MmCoinHits: .res 416
MmCoinStartLo: .res 416
MmCoinStartHi: .res 416
; Protect the foundation separately from destructible underground masonry.
MmSolidTerrain: .res 416
GuestTerrainColumn: .res 13
MmWorldTime: .res 2
MmCoinElapsed: .res 2
MmBreakBlock: .res 1
MmProbeIndex: .res 1
MmProbeX: .res 1
MmProbePage: .res 1
MmProbeY: .res 1
MmProbeOffset: .res 1
MmBillSkip: .res 1
MmBillEdgeX: .res 2
MmBillEdgePage: .res 2
MmBillEdgeY: .res 2
MmBillRow: .res 2
MmWalkTimer: .res 1
MmWalkFrame: .res 1
MmRenderPose: .res 1
MmWasWalking: .res 1
MmMapOffset: .res 2
MmSlot: .res 1
MmEnemySlot: .res 1
MmDamage: .res 1
MmTemp: .res 1
MmFireBank: .res 1
MmSavedPlayer: .res 8
MmBlockAttack: .res 1
MmVX: .res 3
MmVY: .res 3
MmXFraction: .res 2
MmYFraction: .res 2
MmLastXSpeed: .res 1
MmSliding: .res 1
MmSlideTravel: .res 2
MmSlideStop: .res 1
MmCeiling: .res 1
MmOldX: .res 1
MmMul: .res 3
MmProduct: .res 5
MmSign: .res 1
MmJumpReleased: .res 1
MmFrictionYActive: .res 1
MmUnderwater: .res 1
GuestEnemyMask: .res 1
GuestEnemyX: .res 6
GuestEnemyY: .res 6
GuestEnemyMinY: .res 1
GuestEnemyMaxY: .res 1
GuestEnemyWrapY: .res 1
MmStepTimer: .res 1
MmPreviousDir: .res 1
MegaManRamEnd:

; Always-visible helpers share the resident low bank. Native terrain code
; runs in its existing OBJECT bank, freeing this space for exact DMC samples.
.segment "LOWCODE"
.proc MegaManCollisionAdder
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  bcc :+
    jmp ExpandedCollisionAdder
  :
  cmp #CHARACTER_BILL
  bcs Roster
  cmp #CHARACTER_SAMUS
  beq Samus
  cmp #CHARACTER_MEGAMAN
  beq Guest
  clc
  rts
Guest:
  ldy #3
  lda GuestHurtTicks
  bne HurtProfileReady           ; Source takeDamage retains stand's48Flashpx HRect.
  lda Player_State
  beq :+
    iny
  :
  lda MmSliding
  beq :+
    ldy #5
  :
HurtProfileReady:
  sec
  rts
Samus:
  ldy #6
  lda Player_State
  jmp SamusCrouchTerrainTail
  beq :+
    iny
  :
  lda SmBall
  beq :+
    ldy #8
  :
  sec
  rts
Roster:
  cmp #CHARACTER_BILL
  bne :+
    jsr BillCachedTerrainRow
    rts
  :
  ldy #6
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  bne :+
    ldy #9
    sec
    rts
  :
  lda Player_State
  beq :+
    iny
  :
  lda RgCrouch
  beq :+
    ldy #8
  :
  sec
  rts
.endproc
.proc MegaManCollisionBox
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  bcc :+
    jmp ExpandedCollisionBox
  :
  cmp #CHARACTER_BILL
  bcs Roster
  cmp #CHARACTER_SAMUS
  beq Samus
  cmp #CHARACTER_MEGAMAN
  bne Done
  ldy #12
  lda GuestHurtTicks
  bne Done                       ; Hurt stays24NESpx tall even while airborne.
  lda Player_State
  beq :+
    iny
  :
  lda MmSliding
  beq Done
    ldy #14
Done:
  rts
Samus:
  ldy #15
  lda Player_State
  jmp SamusCrouchBodyTail
  beq :+
    iny
  :
  lda SmBall
  beq Done
  ldy #17
  rts
Roster:
  cmp #CHARACTER_BILL
  bne :+
    lda #0
    jsr BillHotSelect
    rts
  :
  cmp #CHARACTER_LINK
  bne :+
    ldy #18
    rts
  :
  ldy #15
  lda GuestHurtTicks
  beq RosterCrouch
  iny                          ; Simon source recoil uses the25NESpx box.
  rts
RosterCrouch:
  lda RgCrouch
  beq :+
    ldy #17
  :
  rts
.endproc
.proc CrossoverBlockSize
  php
  lda MmBlockAttack
  bne Done
  lda SelectedCharacter
  cmp #CHARACTER_LUIGI
  bne :+
    lda PlayerStatus
    beq SmallHead
    ldy #0
    beq Done
  :
  cmp #CHARACTER_SAMUS
  beq SamusHead
  cmp #CHARACTER_MEGAMAN
  beq MegaManHead
  cmp #CHARACTER_MARIO
  beq Done
  bne SmallHead                 ; Bill/Link/Simon break with weapons, not heads.
MegaManHead:
  lda PlayerStatus
  bne Done
SmallHead:
    ldy #1
Done:
  plp
  rts
SamusHead:
  ; Easy uses the original suit rule;2.02 only bumps while upright.
  lda CrossoverBehaviorVersion
  bne SmallHead
  lda SmBall
  bne SmallHead
  lda PlayerStatus
  cmp #2
  beq SmallHead
  ldy #0
  beq Done
.endproc
.proc MegaManResetBlockHealth
  pha
  lda SelectedCharacter
  bne Guest
    pla
    rts
Guest:
  lda R6
  sec
  sbc #<Block_Buffer_1
  sta M0
  lda R7
  sbc #>Block_Buffer_1
  sta M1
  lda M0
  clc
  adc #<MmBrickHealth
  sta M0
  lda M1
  adc #>MmBrickHealth
  sta M1
  lda #0
  sta (M0),y
  clc
  lda M0
  adc #<416
  sta M0
  lda M1
  adc #>416
  sta M1
  lda #0
  sta (M0),y
  ; X is the parser's row index. Underground terrain ABOVE the bottom two
  ; rows is breakable masonry too, including the bonus room's middle shelf.
  ; Parser provenance alone must not make those $52 bricks indestructible.
  clc
  lda R6
  adc #<(MmSolidTerrain-Block_Buffer_1)
  sta M0
  lda R7
  adc #>(MmSolidTerrain-Block_Buffer_1)
  sta M1
  cpx #11
  bcc NotTerrain
  lda GuestTerrainColumn,x
  beq NotTerrain
  cmp MetatileBuffer,x
  bne NotTerrain
  lda #1
  bne StoreTerrain
NotTerrain:
  lda #0
StoreTerrain:
  sta (M0),y
  pla
  rts
.endproc
.pushseg
.segment "SAMUS"
.proc MegaManResetArea
  lda SelectedCharacter
  beq :+
    jsr MegaManClearState
    jmp SamusClearState
  :
  rts
.endproc

.proc MegaManClearState
  lda #<MegaManRamStart
  sta R0
  lda #>MegaManRamStart
  sta R1
  lda #0
  sta MegaManShotPose
  ldy #0
Loop:
  sta (R0),y
  inc R0
  bne :+
    inc R1
  :
  ldx R1
  cpx #>MegaManRamEnd
  bne Loop
  ldx R0
  cpx #<MegaManRamEnd
  bne Loop
  rts
.endproc

.popseg
.proc MegaManFullShotBank
  lda #0
  sta MmFireBank
  ldx #3
Find:
  lda MmBulletType,x
  cmp #3
  beq Blue
  cmp #6
  bne Next
    lda #8
    bne Found
Blue:
  lda #0
Found:
  clc
  adc #$70
  sta MmFireBank
Next:
  dex
  bpl Find
.if ::MAPPER_MMC5
  lda #CHR_SPRITES+2
  ldx MmFireBank
  beq BankReady
    txa
    ora #1
BankReady:
  cmp CurrentCHRBank+4
  beq Done
    sta CurrentCHRBank+4
.else
  lda AreaType
  asl
  ldx MmFireBank
  beq Original
    txa                           ; All four area BG CHR images are identical.
    bne BankReady
Original:
  asl
  clc
  adc #2
BankReady:
  cmp AreaChrBank+1
  beq Done
    sta AreaChrBank+1
.endif
  inc ReloadCHRBank
Done:
  rts
.endproc

.segment "GUEST"
; Samus/Bill batches share eligibility and native box origins across shots.
; Damage still rechecks mutable flag/death state before applying a hit.
.proc GuestPrepareEnemies
  lda #0
  sta GuestEnemyMask
  sta GuestEnemyMaxY
  sta GuestEnemyWrapY
  lda #$ff
  sta GuestEnemyMinY
  ldx #5
Loop:
  lda Enemy_Flag,x
  beq Next
  bmi Next
  lda Enemy_State,x
  and #$20
  bne Next
  lda Enemy_ID,x
  cmp #$15
  bcc Candidate
  cmp #BulletBill_CannonVar
  beq Candidate
  cmp #Bowser
  bne Next
Candidate:
  cmp #Goomba
  bne :+
    lda Enemy_State,x
    cmp #2
    bcs Next
  :
  lda EnemyOffscrBitsMasked,x
  bne Next
  lda Bits,x
  ora GuestEnemyMask
  sta GuestEnemyMask
  lda Enemy_X_Position,x
  sec
  sbc ScreenLeft_X_Pos
  sta GuestEnemyX,x
  lda Enemy_Y_Position,x
  cmp #232
  bcc :+
    inc GuestEnemyWrapY
  :
  clc
  adc #8
  sta GuestEnemyY,x
  cmp GuestEnemyMinY
  bcs :+
    sta GuestEnemyMinY
  :
  clc
  adc #16
  cmp GuestEnemyMaxY
  bcc :+
    sta GuestEnemyMaxY
  :
Next:
  dex
  bpl Loop
  ; Conservative Bill envelope includes the source HammerBro head. Other
  ; candidate boxes remain unchanged; the precise test uses two rectangles.
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bne :+
    sec
    lda GuestEnemyMinY
    sbc #8
    bcs MinReady
    lda #0
MinReady:
    sta GuestEnemyMinY
  :
  lda GuestEnemyMask
  sta RgEnemiesPresent
  rts
Bits: .byte 1,2,4,8,16,32
.endproc
.macro MmMapPointer Base
  clc
  lda MmMapOffset
  adc #<Base
  sta M0
  lda MmMapOffset+1
  adc #>Base
  sta M1
.endmacro
.pushseg
.segment "LEGACY_COLD"
.proc MegaManCoinBrick
  ; Each hosted coin brick permits fourteen coins, with a six-second window.
  ; Native Mario keeps the base engine's original shared coin-brick timer.
  lda R6
  sec
  sbc #<Block_Buffer_1
  sta MmMapOffset
  lda R7
  sbc #>Block_Buffer_1
  sta MmMapOffset+1
  MmMapPointer MmCoinHits
  ldy R2
  lda (M0),y
  bne Existing
  lda #1
  sta (M0),y
  MmMapPointer MmCoinStartLo
  lda MmWorldTime
  sta (M0),y
  MmMapPointer MmCoinStartHi
  lda MmWorldTime+1
  sta (M0),y
  lda R0
  rts
Existing:
  cmp #14
  bcs LastCoin
  MmMapPointer MmCoinStartLo
  sec
  lda MmWorldTime
  sbc (M0),y
  sta MmCoinElapsed
  php
  MmMapPointer MmCoinStartHi
  plp
  lda MmWorldTime+1
  sbc (M0),y
  cmp #2
  bcs LastCoin
  cmp #1
  bne MoreCoins
  lda MmCoinElapsed
  cmp #104
  bcs LastCoin
MoreCoins:
  MmMapPointer MmCoinHits
  lda (M0),y
  clc
  adc #1
  sta (M0),y
  cmp #14
  bcs LastCoin
  lda R0
  rts
LastCoin:
  MmMapPointer MmCoinHits
  lda #14
  sta (M0),y
  lda #$c4
  rts
.endproc
.popseg

.proc MegaManWeapons
  lda #0
  sta Fireball_State
  sta Fireball_State+1
  sta FireballMetasprite
  sta FireballMetasprite+1
  lda TimerControl
  jne Done
  lda GameEngineSubroutine
  cmp #8
  beq Active
    lda #0
    sta MmChargeFrames
    sta MmCharging
    ldx #3
Clear:
    sta MmBulletType,x
    dex
    bpl Clear
    rts
Active:
  inc MmWorldTime
  bne :+
    inc MmWorldTime+1
  :
  inc MmFlashTick
  lda MmFlashTick
  cmp #2
  bcc :+
    lda #0
    sta MmFlashTick
    inc MmFlashPhase
    lda MmFlashPhase
    cmp #6
    bcc :+
      lda #0
      sta MmFlashPhase
  :
  lda MegaManShotPose
  beq :+
    dec MegaManShotPose
  :
  ldx #5
Flash:
  lda MmEnemyFlash,x
  beq :+
    dec MmEnemyFlash,x
  :
  dex
  bpl Flash
  jsr Buttons
  ldx #3
Update:
  stx MmSlot
  lda MmBulletType,x
  beq Next
  inc MmBulletAge,x
  jsr Move
  lda MmBulletType,x
  beq Next
  jsr Blocks
  ldx MmSlot
  lda MmBulletType,x
  beq Next
  jsr Enemies
Next:
  ldx MmSlot
  dex
  bpl Update
Done:
  rts

Buttons:
  lda CrossoverBehaviorVersion
  beq ClassicButtons
  lda InvSelected+CHARACTER_MEGAMAN
  beq :+
    rts
  :
ClassicButtons:
  lda A_B_Buttons
  and #B_Button
  beq Release
  lda PreviousA_B_Buttons
  and #B_Button
  bne Holding
  lda Player_State
  cmp #3
  jeq Return
  lda CrossoverBehaviorVersion
  beq BeginCharge
  lda CrouchingFlag
  jne Return                  ;2.02 fresh B while sliding starts no charge.
BeginCharge:
  lda PlayerStatus
  beq :+
    lda #1
  :
  sta MmCharging
  lda CrouchingFlag
  bne Holding
  lda Player_State
  cmp #3
  beq Holding
  ldx #3
  ldy #0
Count:
  lda MmBulletType,x
  beq :+
    cmp #3
    beq Holding
    cmp #6
    beq Holding
    iny
  :
  dex
  bpl Count
  cpy #3
  bcs Holding
  lda #1
  jsr PowerType
  jsr Spawn
Holding:
  lda MmCharging
  beq Return
  lda PlayerStatus
  beq ResetCharge
  lda MmChargeFrames
  cmp #87
  bcs Return
  inc MmChargeFrames
Return:
  rts
Release:
  lda MmChargeFrames
  cmp #48                       ; 800 ms at the reference's 60 Hz
  bcc ResetCharge
  lda PlayerStatus
  beq ResetCharge
  lda CrouchingFlag
  bne ResetCharge
  lda #2
  ldy MmChargeFrames
  cpy #87                       ; 1450 ms, full charge
  bcc :+
    lda #3
  :
  jsr PowerType
  jsr Spawn
ResetCharge:
  lda #0
  sta MmChargeFrames
  sta MmCharging
  rts
PowerType:
  ldy PlayerStatus
  cpy #2
  bne :+
    clc
    adc #3
  :
  rts
Spawn:
  sta MmTemp
  ldy Player_Y_HighPos
  cpy #1
  bne Return
  ldx #3
FindSlot:
  lda MmBulletType,x
  beq FoundSlot
  dex
  bpl FindSlot
  rts
FoundSlot:
  lda MmTemp
  sta MmBulletType,x
  lda #0
  sta MmBulletAge,x
  sta MmBulletFracLo,x
  sta MmBulletFracHi,x
  lda PlayerFacingDir
  sta MmBulletDir,x
  cmp #1
  bne SpawnLeft
  lda Player_X_Position
  clc
  adc #27
  sta MmBulletX,x
  lda Player_PageLoc
  adc #0
  bne SpawnPage
  beq SpawnPage
SpawnLeft:
  lda Player_X_Position
  sec
  sbc #11
  sta MmBulletX,x
  lda Player_PageLoc
  sbc #0
SpawnPage:
  sta MmBulletPage,x
  lda #18
  ldy Player_State
  beq :+
    lda #14
  :
  clc
  adc Player_Y_Position
  sta MmBulletY,x
  lda #12
  sta MegaManShotPose
  lda MmTemp
  sta MmAudioShotType
  lda #Sfx_Fireball
  sta Square1SoundQueue
  rts

Move:
  lda MmBulletDir,x
  cmp #1
  bne MoveLeft
  lda CrossoverBehaviorVersion
  beq MoveClassicRight
  clc
  lda MmBulletFracHi,x
  adc #$c0                       ;450/120=$03C000: low byte unchanged.
  sta MmBulletFracHi,x
  jmp MoveRightWhole
MoveClassicRight:
  clc
  lda MmBulletFracLo,x
  adc #$55
  sta MmBulletFracLo,x
  lda MmBulletFracHi,x
  adc #$95
  sta MmBulletFracHi,x
MoveRightWhole:
  lda MmBulletX,x
  adc #3
  sta MmBulletX,x
  lda MmBulletPage,x
  adc #0
  jmp StorePage
MoveLeft:
  lda CrossoverBehaviorVersion
  beq MoveClassicLeft
  sec
  lda MmBulletFracHi,x
  sbc #$c0
  sta MmBulletFracHi,x
  jmp MoveLeftWhole
MoveClassicLeft:
  sec
  lda MmBulletFracLo,x
  sbc #$55
  sta MmBulletFracLo,x
  lda MmBulletFracHi,x
  sbc #$95
  sta MmBulletFracHi,x
MoveLeftWhole:
  lda MmBulletX,x
  sbc #3
  sta MmBulletX,x
  lda MmBulletPage,x
  sbc #0
StorePage:
  sta MmBulletPage,x
  lda MmBulletX,x
  sec
  sbc ScreenLeft_X_Pos
  lda MmBulletPage,x
  sbc ScreenLeft_PageLoc
  jeq MoveDone
Kill:
  lda #0
  sta MmBulletType,x
MoveDone:
  rts

Blocks:
  lda #0
  sta MmProbeIndex
  ldy MmBulletType,x
  cpy #10
  jeq BombPoint
  cpy #11
  bcc Probe
  cpy #14
  jcc BillPrepare
  cpy #36                       ; Sophia normal/hyper/Crusher cannon.
  jeq BillPrepare
  cpy #37
  jeq BillPrepare
  cpy #76
  jeq BillPrepare
  cpy #69                       ; Bill's inventory laser and flare.
  jeq BillPrepare
  cpy #70
  jeq BillPrepare
  cpy #71                       ; Sophia's standard missile also has symmetric corners.
  jeq BillPrepare
  ; Pit's three arrow tiers have symmetric extents. Reuse the distinct-cell
  ; empty-air path; solid cells retain the existing facing/row probe order.
  cpy #26
  bcc Probe
  cpy #29
  bcs Probe
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  jeq BillPrepare
Probe:
  lda #0
  sta MmBreakBlock
  ldy MmBulletType,x
  lda MmProbeIndex
  cmp #4
  bcc ProbeEdges
  cmp #8
  bcc ProbeCenter
  and #1
  beq ProbeMidRight
  lda #$f0
  bne ProbeOffset
ProbeMidRight:
  lda #16
  bne ProbeOffset
ProbeCenter:
  lda #0
  beq ProbeOffset
ProbeEdges:
  and #1
  beq ProbeRight
  lda ShotLeft-1,y
  jmp ProbeOffset
ProbeRight:
  lda ShotRight-1,y
ProbeOffset:
  ldy MmBulletDir,x
  cpy #1
  beq :+
    eor #$ff
    clc
    adc #1
  :
  sta MmProbeOffset
  clc
  adc MmBulletX,x
  sta MmProbeX
  lda #0
  bit MmProbeOffset
  bpl :+
    lda #$ff
  :
  adc MmBulletPage,x
  sta MmProbePage
  ldy MmBulletType,x
  lda MmProbeIndex
  and #2
  beq ProbeTop
  lda ShotBottom-1,y
  jmp ProbeVertical
ProbeTop:
  lda ShotTop-1,y
ProbeVertical:
  clc
  adc MmBulletY,x
  sta MmProbeY
ProbeBounds:
  ; EasyWhipEligible accepts only adjacent Link/Simon IDs under Easy.
  lda SelectedCharacter
  sec
  sbc #CHARACTER_LINK
  cmp #2
  bcs EasyWhipProbeAdmissionDone
  lda CrossoverBehaviorVersion
  bne EasyWhipProbeAdmissionDone
  farcall EasyWhipProbe
EasyWhipProbeAdmissionDone:
  lda MmProbeY
  cmp #$20
  jcc ProbeNext
  cmp #$f0
  jcs ProbeNext
  and #$f0
  sec
  sbc #$20
  sta R2
  lda MmProbeX
  lsr
  lsr
  lsr
  lsr
  sta MmTemp
  lda MmProbePage
  and #1
  asl
  asl
  asl
  asl
  ora MmTemp
  jsr GetBlockBufferAddr
  ldy R2
  lda (R6),y
  jeq ProbeNext
  cmp #$23
  jeq ProbeNext
  cmp #$26
  jeq ProbeNext
  cmp #$c2
  jeq ProbeNext
  cmp #$c3
  jeq ProbeNext
  sta R3
  jsr RosterBlockSeen
  jcs ProbeNext
  lda R3
  jsr BlockBumpedChk
  jcs Activate
  lda R3
  cmp #$51
  beq Brick
  cmp #$52
  jne Terrain
  ; $54 is overworld ground, never a brick. $52 is shared between
  ; underground bricks and terrain, so consult the parser's cell flag.
  clc
  lda R6
  adc #<(MmSolidTerrain-Block_Buffer_1)
  sta M0
  lda R7
  adc #>(MmSolidTerrain-Block_Buffer_1)
  sta M1
  ldy R2
  lda (M0),y
  jne Terrain
Brick:
  ; Translate the exact native block-map address to its parallel health map.
  lda R6
  sec
  sbc #<Block_Buffer_1
  sta M0
  lda R7
  sbc #>Block_Buffer_1
  sta M1
  lda M0
  clc
  adc #<MmBrickHealth
  sta M0
  lda M1
  adc #>MmBrickHealth
  sta M1
  ldy R2
  lda (M0),y
  bne :+
    lda #34                      ; Hosted brick health: two ordinary buster hits.
  :
  ldx MmSlot
  pha
  ldy MmBulletType,x
  lda DamageTable-1,y
  jsr EasyLsrDamage
  sta MmDamage
  pla
  sec
  sbc MmDamage
  bcc DestroyBrick
  beq DestroyBrick
  ldy R2
  sta (M0),y
  jmp Solid
Terrain:
  ldy MmSlot
  lda MmBulletType,y
  ; Bill Flare requests Brick/Enemy, not GroundNonBrick. Brick/question
  ; dispatch already occurred above; keep probing so later corners may hit.
  cmp #69                       ; Source Bill Laser/Flare request Brick/Enemy.
  beq BillPlainGround
  cmp #70
  bne :+
BillPlainGround:
    jmp ProbeNext
  :
  cmp #43
  bcc Solid
  cmp #58
  bcs Solid
  cmp #48                       ; Flame's falling seed collides with terrain.
  jne ProbeNext
Solid:
  ldx MmSlot
  jmp Kill
DestroyBrick:
  lda #1
  sta MmBreakBlock
Activate:
  jsr GuestClaimBlockSlot
  jcc ProbeNext
  jsr RosterMarkBlock
  ; Reuse SMB's item/break dispatch at the contacted map cell. A projectile's
  ; edge can enter another tile or page before its center does. Its bounce
  ; sprite, debris and reward must all use that same cell, not the center.
  ; Restore player coordinates and velocities changed by the native routines.
  lda Player_X_Position
  sta MmSavedPlayer
  lda Player_PageLoc
  sta MmSavedPlayer+1
  lda Player_Y_Position
  sta MmSavedPlayer+2
  lda Player_Y_HighPos
  sta MmSavedPlayer+3
  lda PlayerSize
  sta MmSavedPlayer+4
  lda CrouchingFlag
  sta MmSavedPlayer+5
  lda Player_Y_Speed
  sta MmSavedPlayer+6
  lda MmProbeX
  and #$f0
  sta Player_X_Position
  lda MmProbePage
  sta Player_PageLoc
  lda MmProbeY
  and #$f0
  sta Player_Y_Position
  lda #1
  sta Player_Y_HighPos
  lda #0
  sta PlayerSize
  sta CrouchingFlag
  lda #1
  sta MmBlockAttack
  lda R3
  jsr PlayerHeadCollision
  lda #0
  sta MmBlockAttack
  lda MmSavedPlayer
  sta Player_X_Position
  lda MmSavedPlayer+1
  sta Player_PageLoc
  lda MmSavedPlayer+2
  sta Player_Y_Position
  lda MmSavedPlayer+3
  sta Player_Y_HighPos
  lda MmSavedPlayer+4
  sta PlayerSize
  lda MmSavedPlayer+5
  sta CrouchingFlag
  lda MmSavedPlayer+6
  sta Player_Y_Speed
  ldx MmSlot
  lda MmBreakBlock
  beq ConsumeBlock
  lda MmBulletType,x
  cmp #3
  jeq ProbeNext
  cmp #6
  jeq ProbeNext
  cmp #43                       ; Blade/knuckle/charged Pharaoh pierce a defeat.
  jeq ProbeNext
  cmp #44
  jeq ProbeNext
  cmp #47
  jeq ProbeNext
  cmp #51
  jeq ProbeNext
  cmp #52
  jeq ProbeNext
ConsumeBlock:
  jmp Kill
ProbeNext:
  inc MmProbeIndex
  ldx MmSlot
  lda MmProbeIndex
  cmp #4
  bcs ProbeExtra
  ldy MmBulletType,x
  cpy #11
  bcc OrdinaryProbe
  cpy #14
  jcc BillProbe
  cpy #36
  jeq BillProbe
  cpy #37
  jeq BillProbe
  cpy #76
  jeq BillProbe
  cpy #69
  jeq BillProbe
  cpy #70
  jeq BillProbe
  cpy #71
  jeq BillProbe
OrdinaryProbe:
  jmp Probe
ProbeExtra:
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bcc MoveDone2
  lda MmBulletType,x
  jsr RosterIsMelee
  bcc MoveDone2
  lda MmProbeIndex
  cmp #8
  jcc Probe
  ldy MmBulletType,x
  lda RadiusX-1,y
  farcall EasyWhipProbeRadius
  cmp #17
  bcc MoveDone2
  lda MmProbeIndex
  cmp #12
  jcc Probe
MoveDone2:
  rts

BombPoint:
  ; The Samus bomb bridge already visits each of its nine terrain cells.
  ; Type10 has zero terrain extents: all four generic corners are identical.
  ; Keep the ordinary dispatcher and final probe index, but visit once.
  lda #0
  sta MmBreakBlock
  lda #3
  sta MmProbeIndex
  lda MmBulletX,x
  sta MmProbeX
  lda MmBulletPage,x
  sta MmProbePage
  lda MmBulletY,x
  sta MmProbeY
  jmp ProbeBounds

BillPrepare:
  cpy #69
  beq BillSourceTerrain
  cpy #70
  beq BillSourceTerrain
  cpy #14
  bcs OrdinaryBillEdges
BillSourceTerrain:
  jsr BillSourceBounds
  bcs BillDuplicateEdges
OrdinaryBillEdges:
  ; Bill's bullets and Sophia's cannon have symmetric rectangular bounds.
  ; Calculate each
  ; edge once rather than repeating 16-bit world-coordinate arithmetic for
  ; every corner. BillProbe retains the original facing-dependent order.
  lda RadiusX-1,y
  sta MmDamage
  clc
  adc MmBulletX,x
  sta MmBillEdgeX
  lda MmBulletPage,x
  adc #0
  sta MmBillEdgePage
  sec
  lda MmBulletX,x
  sbc MmDamage
  sta MmBillEdgeX+1
  lda MmBulletPage,x
  sbc #0
  sta MmBillEdgePage+1
  lda RadiusY-1,y               ; Laser69 is wider than it is tall.
  sta MmDamage
  sec
  lda MmBulletY,x
  sbc MmDamage
  sta MmBillEdgeY
  clc
  lda MmBulletY,x
  adc MmDamage
  sta MmBillEdgeY+1
BillDuplicateEdges:
  ; Flag duplicate columns/rows before the probe loop, so repeated corners
  ; skip coordinate conversion and map lookup as well as tile handling.
  lda #0
  sta MmBillSkip
  lda MmBillEdgeX
  eor MmBillEdgeX+1
  and #$f0
  bne :+
    inc MmBillSkip
  :
  lda MmBillEdgeY
  eor MmBillEdgeY+1
  and #$f0
  bne BillRows
  lda MmBillSkip
  ora #2
  sta MmBillSkip
BillRows:
  ldy #1
BillRowLoop:
  lda MmBillEdgeY,y
  cmp #32
  bcc BillRowOutside
  cmp #240
  bcs BillRowOutside
  and #$f0
  sec
  sbc #32
  bcs BillRowStore
BillRowOutside:
  lda #$ff
BillRowStore:
  sta MmBillRow,y
  dey
  bpl BillRowLoop
  ; Most shots are in empty air. Read the distinct map cells directly,
  ; sharing a column pointer between its two rows. Only a potentially
  ; solid cell needs the full block hit/health/reward dispatcher below.
BillEmptyColumn:
  ldy MmProbeIndex
  lda MmBillEdgeX,y
  lsr
  lsr
  lsr
  lsr
  sta MmTemp
  lda MmBillEdgePage,y
  and #1
  asl
  asl
  asl
  asl
  ora MmTemp
  jsr GetBlockBufferAddr
  ldy MmBillRow
  cpy #$ff
  beq BillEmptyBottom
  jsr BillCellEmpty
  bcs BillSolidCell
BillEmptyBottom:
  lda MmBillSkip
  and #2
  bne BillEmptyNext
  ldy MmBillRow+1
  cpy #$ff
  beq BillEmptyNext
  jsr BillCellEmpty
  bcs BillSolidCell
BillEmptyNext:
  lda MmBillSkip
  and #1
  bne BillEmptyDone
  inc MmProbeIndex
  lda MmProbeIndex
  cmp #2
  bcc BillEmptyColumn
BillEmptyDone:
  ldx MmSlot
  rts
BillCellEmpty:
  lda (R6),y
  beq BillCellClear
  cmp #$23
  beq BillCellClear
  cmp #$26
  beq BillCellClear
  cmp #$c2
  beq BillCellClear
  cmp #$c3
  beq BillCellClear
  sec
  rts
BillCellClear:
  clc
  rts
BillSolidCell:
  lda #0
  sta MmProbeIndex
  ldx MmSlot
BillProbe:
  lda MmProbeIndex
  and MmBillSkip
  jne ProbeNext
  lda MmProbeIndex
  and #1
  ldy MmBulletDir,x
  cpy #1
  beq :+
    eor #1
  :
  tay
  lda MmBillEdgeX,y
  sta MmProbeX
  lda MmBillEdgePage,y
  sta MmProbePage
  lda MmProbeIndex
  lsr
  tay
  lda MmBillEdgeY,y
  sta MmProbeY
  ldy MmBulletType,x
  jmp ProbeBounds

Enemies:
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bne OrdinaryEnemyBounds
  ldy MmBulletType,x
  cpy #69
  beq BillSourceEnemy
  cpy #70
  beq BillSourceEnemy
  cpy #11
  bcc OrdinaryEnemyBounds
  cpy #14
  bcs OrdinaryEnemyBounds
BillSourceEnemy:
  jsr BillSourceBounds
  bcc OrdinaryEnemyBounds
  sec
  lda MmBillEdgeX+1
  sbc ScreenLeft_X_Pos
  sta BoundingBox_UL_Corner+28
  sec
  lda MmBillEdgeX
  sbc ScreenLeft_X_Pos
  sta BoundingBox_LR_Corner+28
  lda MmBillEdgeY
  sta BoundingBox_UL_Corner+29
  lda MmBillEdgeY+1
  sta BoundingBox_LR_Corner+29
  jmp EnemyBoundsReady
OrdinaryEnemyBounds:
  ; Native bounding boxes occupy four bytes per enemy, starting at offset 4.
  ; These are the same collision boxes used for Mario's projectiles.
  lda MmBulletX,x
  sec
  sbc ScreenLeft_X_Pos
  sta MmTemp
  ldy MmBulletType,x
  lda RadiusX-1,y
  sta MmDamage
  lda MmTemp
  sec
  sbc MmDamage
  sta BoundingBox_UL_Corner+28
  lda MmTemp
  clc
  adc MmDamage
  sta BoundingBox_LR_Corner+28
  lda RadiusY-1,y
  sta MmDamage
  lda MmBulletY,x
  sec
  sbc MmDamage
  sta BoundingBox_UL_Corner+29
  lda MmBulletY,x
  clc
  adc MmDamage
  sta BoundingBox_LR_Corner+29
EnemyBoundsReady:
  ; EasyWhipEligible accepts only adjacent Link/Simon IDs under Easy.
  lda SelectedCharacter
  sec
  sbc #CHARACTER_LINK
  cmp #2
  bcs EasyWhipEnvelopeAdmissionDone
  lda CrossoverBehaviorVersion
  bne EasyWhipEnvelopeAdmissionDone
  farcall EasyWhipEnvelope
EasyWhipEnvelopeAdmissionDone:
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  beq CachedEnvelope
  cmp #CHARACTER_BILL
  beq CachedEnvelope
  cmp #CHARACTER_SOPHIA
  bne BeginEnemyLoop
CachedEnvelope:
  lda GuestEnemyMask
  beq NoEnemyOverlap
  lda GuestEnemyWrapY
  bne BeginEnemyLoop
  lda BoundingBox_UL_Corner+29
  cmp BoundingBox_LR_Corner+29
  bcs BeginEnemyLoop
  lda GuestEnemyMinY
  cmp BoundingBox_LR_Corner+29
  beq EnvelopeOverlap
  bcc EnvelopeOverlap
NoEnemyOverlap:
  rts
EnvelopeOverlap:
  lda GuestEnemyMaxY
  cmp BoundingBox_UL_Corner+29
  bcc NoEnemyOverlap
BeginEnemyLoop:
  ldx #5
EnemyLoop:
  stx MmEnemySlot
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  beq CachedEnemy
  cmp #CHARACTER_BILL
  beq CachedEnemy
  cmp #CHARACTER_SOPHIA
  beq CachedEnemy
  jmp UncachedEnemy
CachedEnemy:
  lda GuestPrepareEnemies::Bits,x
  and GuestEnemyMask
  jeq NextEnemy
  lda Enemy_Flag,x
  jeq NextEnemy
  jmi NextEnemy
  lda Enemy_State,x
  and #$20
  jne NextEnemy
  lda Enemy_ID,x
  cmp #HammerBro
  bne CachedNativeVertical
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bne CachedNativeVertical
BillBroAdmission:
  farcall BillHammerBroOverlap
BillBroReturn:
  jcc NextEnemy
  jmp EnemyHit
CachedNativeVertical:
  ; The native collision core has special wrap behavior. Preserve that path
  ; at both Y seams rather than treating a wrapped box as an ordinary span.
  lda Enemy_Y_Position,x
  cmp #232
  bcs CachedBounds
  lda BoundingBox_UL_Corner+29
  cmp BoundingBox_LR_Corner+29
  bcs CachedBounds
  lda GuestEnemyY,x
  cmp BoundingBox_LR_Corner+29
  beq CachedVerticalOverlap
  jcs NextEnemy
CachedVerticalOverlap:
  clc
  adc #16
  cmp BoundingBox_UL_Corner+29
  jcc NextEnemy
CachedBounds:
  lda GuestEnemyX,x
  sta BoundingBox_UL_Corner+32
  clc
  adc #16
  sta BoundingBox_LR_Corner+32
  lda GuestEnemyY,x
  sta BoundingBox_UL_Corner+33
  clc
  adc #16
  sta BoundingBox_LR_Corner+33
  jmp CompareEnemy
UncachedEnemy:
  lda Enemy_Flag,x
  jeq NextEnemy
  jmi NextEnemy                    ; Bowser's duplicate cannot be hit twice
  lda Enemy_State,x
  and #$20
  jne NextEnemy
  lda Enemy_ID,x
  cmp #$15
  bcc CheckEnemy
  cmp #BulletBill_CannonVar
  beq CheckEnemy
  cmp #Bowser
  jne NextEnemy
CheckEnemy:
  cmp #Goomba
  bne :+
    lda Enemy_State,x
    cmp #2
    jcs NextEnemy
  :
  lda EnemyOffscrBitsMasked,x
  jne NextEnemy
  ; Bill's bullets cannot wrap vertically (Move clips their centers to
  ; 32..239). Reject clear vertical misses before preparing the general
  ; collision boxes. Retain the native wrap path for enemies at the seam.
  ldy SelectedCharacter
  cpy #CHARACTER_BILL
  bne EnemyBounds
  lda Enemy_Y_Position,x
  cmp #232
  bcs EnemyBounds
  clc
  adc #8
  cmp BoundingBox_LR_Corner+29
  beq BillVerticalOverlap
  bcs NextEnemy
BillVerticalOverlap:
  clc
  adc #16
  cmp BoundingBox_UL_Corner+29
  bcc NextEnemy
EnemyBounds:
  ; Character sword secondary admission, not a projectile/body-box expansion.
  ; Unsupported kinds retain the native proxy below. Integer-source positions
  ; are tested as two separate rectangles, including the facing-dependent notch.
  ; Y already holds SelectedCharacter on both branches and fallthrough.
  cpy #CHARACTER_RYU
  bne NativeEnemyBounds
  ldy MmSlot
  lda MmBulletType,y
  cmp #32
  bne NativeEnemyBounds
  lda Enemy_ID,x
  beq RyuKoopaKind
  cmp #RedKoopa
  bne NativeEnemyBounds
RyuKoopaKind:
  lda Enemy_State,x
  cmp #4
  beq RyuKoopaKnownState
  cmp #2
  bcs NativeEnemyBounds
RyuKoopaKnownState:
  lda PlayerFacingDir
  beq NativeEnemyBounds
  cmp #3
  bcs NativeEnemyBounds
  lda Enemy_MovingDir,x
  beq NativeEnemyBounds
  cmp #3
  bcs NativeEnemyBounds
  jsr RyuKoopaPrimary
  bcc NextEnemy
  jmp EnemyHit
NativeEnemyBounds:
  ; SMB's Goomba hurtbox only covers its lower six pixels. The hosted
  ; buster can hit the whole visible body, including a standing shot.
  lda Enemy_X_Position,x
  sec
  sbc ScreenLeft_X_Pos
  sta BoundingBox_UL_Corner+32
  clc
  adc #16
  sta BoundingBox_LR_Corner+32
  lda Enemy_Y_Position,x
  clc
  adc #8
  sta BoundingBox_UL_Corner+33
  clc
  adc #16
  sta BoundingBox_LR_Corner+33
CompareEnemy:
  ldy #28
  ldx #32
  jsr SprObjectCollisionCore
  bcc NextEnemy
EnemyHit:
  ldx MmEnemySlot
  jsr DamageEnemy
  ldx MmSlot
  lda MmBulletType,x
  jeq MoveDone2
NextEnemy:
  ldx MmEnemySlot
  dex
  jpl EnemyLoop
  rts
DamageEnemy:
  jsr RosterEnemyHit
  jcs KeepShot
  ldy MmSlot
  lda MmBulletType,y
  cmp #10
  bne DamageOnce
  lda BombHitBits,x
  ldy SmSlot
  and SmBombHits,y
  jne KeepShot
  lda BombHitBits,x
  ora SmBombHits,y
  sta SmBombHits,y
DamageOnce:
  lda Enemy_ID,x
  cmp #Podoboo
  jeq Immune
  cmp #BuzzyBeetle
  jeq Armored
  cmp #BulletBill_FrenzyVar
  jeq Armored
  cmp #BulletBill_CannonVar
  jne Susceptible
Armored:
  lda MmBulletType
  cmp #78                       ; Exclude the only $F7-fold collision.
  beq CheckKnuckle
  and #$f7                      ; Fold67/75 and68/76 together; no X/Y writes.
  sbc #66                       ; CMPcarry is0 below78: foldedvalue minus67.
  cmp #2
  bcc Susceptible               ; Normalized0/1:67,68,75,76.
  cmp #3
  beq Susceptible               ; Normalized3:70; original78 already rejected.
CheckKnuckle:
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  beq SharedKnuckle
  cmp #CHARACTER_MEGAMAN
  bne Immune
SharedKnuckle:
  ldy MmSlot
  lda MmBulletType,y
  cmp #44                       ; Knuckle pierce 10 exceeds source armor 5.
  beq Susceptible
Immune:
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  beq SharedDeflect
  cmp #CHARACTER_MEGAMAN
  jne Consume
  lda CrossoverBehaviorVersion
  jeq Consume                 ; Classic armor consumes, never damages.
SharedDeflect:
  farcall BassDeflectProjectile
  jcs KeepShot
  jmp Consume
Susceptible:
  lda MmEnemyHealthLo,x
  ora MmEnemyHealthHi,x
  bne HealthReady
  ldy Enemy_ID,x
  cpy #Bowser
  bne NormalHealth
    lda SelectedCharacter
    cmp #CHARACTER_LUIGI
    bne :+
      lda #<1250                ; MarioBase: five 250-damage fireballs.
      ldy #>1250
      jmp StoreHealth
    :
    cmp #CHARACTER_BASS
    bcs ModernBoss
    cmp #CHARACTER_SIMON+1
    bcs LegacyBoss
ModernBoss:
      lda WorldNumber
      cmp #7
      bcc LegacyBoss
      lda #<1100                ; 2.02's final hammer/fireball Bowser.
      ldy #>1100
      jmp StoreHealth
LegacyBoss:
    lda #<600
    ldy #>600
    pha
    lda WorldNumber
    cmp #5
    pla
    bcc StoreHealth
      lda #<900
      ldy #>900
      bne StoreHealth
NormalHealth:
    lda SelectedCharacter
    cmp #CHARACTER_LUIGI
    bcs ModernHealth
    phy
    phx
    farcall InventorySupported
    plx
    ply
    bcc LegacyHealth
  ModernHealth:
    lda HealthTable202,y
    jmp HealthLoaded
  LegacyHealth:
  lda HealthTable,y
  HealthLoaded:
  ldy #0
StoreHealth:
  sta MmEnemyHealthLo,x
  tya
  sta MmEnemyHealthHi,x
HealthReady:
  ; SourceFREEZE is resolvedbeforepiercing; an existingfreeze thawsfirst.
  jmp :+
  .res 14,$ea                    ; Preserve exactold17B span andlaterPCs.
  :
  lda MmBulletType
  cmp #75
  jeq Defeat
  ldy MmSlot
  lda MmBulletType,y
  tay
  lda DamageTable-1,y
  jsr EasyLsrDamage
  sta MmDamage
  lda MmEnemyHealthLo,x
  sec
  sbc MmDamage
  sta MmEnemyHealthLo,x
  lda MmEnemyHealthHi,x
  sbc #0
  sta MmEnemyHealthHi,x
  bcc Defeat
  ora MmEnemyHealthLo,x
  beq Defeat
  ; Properties follow successful piercing and a surviving damage receipt.
  ; FLASH is visual only; the source contact dictionaries admit new attacks.
  farcall LsrEffectsAcceptedHit
  bcs :+
    lda #2                        ; Other characters retain their own contract.
    sta MmEnemyFlash,x
  :
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne NativeHitSound
  lda #19                         ; AV_SFX_SOPHIAHITENEMY
  sta AvAudioRequest
  jmp Consume
NativeHitSound:
  lda #Sfx_EnemySmack
  sta Square1SoundQueue
Consume:
  ldx MmSlot
  lda MmBulletType,x
  jsr RosterKeepWeapon
  jcs KeepShot
  lda MmBulletType,x
  cmp #10
  jeq KeepShot
  jmp SamusShotEnemyConsume
Defeat:
  farcall LsrEffectsKilled
  stx R1
  lda Enemy_ID,x
  cmp #Bowser
  bne DefeatOther
    lda #1
    sta BowserHitPoints
    lda SelectedCharacter
    cmp #CHARACTER_SOPHIA
    bne NativeBowserDefeat
    farcall SophiaDefeatBowser
    jmp Killed
NativeBowserDefeat:
    jsr HandleEnemyFBallCol
    jmp Killed
DefeatOther:
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne NativeDefeat
  farcall SophiaDefeatEnemy
  jmp Killed
NativeDefeat:
  jsr ShellOrBlockDefeat
Killed:
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne NativeKillSound
  lda #20                         ; AV_SFX_SOPHIAKILLENEMY
  sta AvAudioRequest
  lda #0
  sta Square1SoundQueue
NativeKillSound:
  ldx MmSlot
  lda MmBulletType,x
  cmp #66                       ; Fire Wheel/Dragon pass through defeated targets.
  beq KeepShot
  cmp #67
  beq KeepShot
  cmp #43                       ; Metal Blade passes through a defeated enemy.
  beq KeepShot
  cmp #47                       ; Full Pharaoh Shot has the same source property.
  beq KeepShot
  jsr RosterKeepWeapon
  bcs KeepShot
  lda MmBulletType,x
  cmp #10
  beq KeepShot
  cmp #3
  beq KeepShot
  cmp #6
  jne Consume
KeepShot:
  rts
DamageTable:
  .byte 25,50,75,34,50,100,40,40,40,100,25,30,30,50,75,100
  .byte 50,0,70,75,100,60,50,75,100,25,40,65,100,250,17,75
  .byte 75,75,100,30,40,100,50,34,50,100,50,200,25,50,100,75
  .byte 75,50,100,75,0,50,75,75,75,0,75,0,200,75,15,50
  .byte 75,75,75,100,25,50,100,100,40,75,255
  .byte 50
ShotLeft:
  ; 2.02 Simon leather/morning-star/flame widths: 57/57/87 Flash px.
  ; Ryu normal/wave rectangles: 48x13 and 75(79 crouched)x32 Flash px.
  ; NES half-scale centers and radii round outward to integer pixels.
  .byte -4,-5,-9,-4,-6,-9,-3,-3,-4,0
  .byte -2,-3,-3,-10,-10,-10,-7,-3,-15,-15,-22,-6,-4,-4,-4
  .byte -4,-6,-7,-7,-4,-3,-12,-19,-4,-5,-4,-6,-8
  .byte -7,-3,-3
    .byte -8,-5,-7,-4,-7,-10,-3,-4,-4,-10,-12,-12,-3
    .byte 0,-4,-16
  .byte 0,-4,0,-18,-4,-3,-8,-5,-6,-6,-4,-6,-4,-4,-4,-3,-12,-12
  .byte -6
ShotRight:
  .byte 4,4,7,7,7,7,3,3,4,0
  .byte 2,3,3,10,10,10,7,3,15,15,22,6,4,4,4
  .byte 4,6,7,7,4,3,12,19,4,5,4,6,8
  .byte 7,3,3
    .byte 8,5,7,4,7,10,3,4,4,10,12,12,3
    .byte 16,4,0
  .byte 0,4,0,18,4,3,8,5,6,6,4,6,4,4,4,3,12,12
  .byte 6
ShotTop:
  .byte -3,-4,-7,-5,-6,-9,-3,-3,-4,0
  .byte -2,-3,-3,-4,-4,-5,-3,-3,-4,-4,-5,-6,-10,-10,-10
  .byte -3,-3,-4,-7,-4,-3,-4,-8,-4,-5,-4,-6,-8
  .byte -7,-3,-3
    .byte -8,-5,-7,-4,-7,-10,-3,-16,-4,-10,-6,-8,-3
    .byte -4,0,-4
  .byte 0,-3,0,-22,-2,-4,-12,-6,-6,-6,-3,-2,-4,-4,-4,-3,-12,-12
  .byte -6
ShotBottom:
  .byte 3,4,7,5,6,9,3,3,4,0
  .byte 2,3,3,4,4,5,3,3,4,4,5,6,10,10,10
  .byte 3,3,4,7,4,3,4,8,4,5,4,6,8
  .byte 7,3,3
    .byte 8,5,7,4,7,10,3,0,4,10,6,8,3
    .byte 4,16,4
  .byte 0,3,0,22,2,4,0,6,6,6,3,2,4,4,4,3,12,12
  .byte 6
RadiusX:
  .byte 4,5,8,6,7,8,3,3,4,16
  .byte 2,3,3,10,10,10,7,3,15,15,22,6,4,4,4
  .byte 4,6,7,7,4,3,12,19,4,5,4,6,8
  .byte 7,3,3
    .byte 8,5,7,4,7,10,3,4,4,10,12,12,3
    .byte 8,4,8
  .byte 0,4,0,18,4,3,8,5,6,6,4,6,4,4,4,3,12,12
  .byte 6
RadiusY:
  .byte 3,4,7,5,6,9,3,3,4,16
  .byte 2,3,3,4,4,5,3,3,4,4,5,6,10,10,10
  .byte 3,3,4,7,4,3,4,8,4,5,4,6,8
  .byte 7,3,3
    .byte 8,5,7,4,7,10,3,8,4,10,6,8,3
    .byte 4,8,4
  .byte 0,3,0,22,2,4,12,6,6,6,3,2,4,4,4,3,12,12
  .byte 6
BombHitBits: .byte 1,2,4,8,16,32
HealthTable:
  .byte 125,125,160,125,100,200,100,175,100,100,75,75,255,75,125,125
  .byte 125,200,100,100,50
  ; Inventory characters use 2.02 balance. Enemy indices are SMB native IDs.
  HealthTable202:
    .byte 100,100,100,100,100,200,75,150,100,100,75,75,255,75,100,100
    .byte 100,200,100,100,50

; Source: HitTester.multipleHRectHitTest Character ahRect vs Koopa hRect2;
; KoopaGreen/Red current main/head rectangles, Ryu primary unextended sword.
; Entry X=actual native slot, type32/ID0 or3/state0,1 or4/facings1,2 checked.
; Return C=overlap, X preserved. A/Y and dead MmTemp/MmDamage scratch clobbered.
; No R0..R7, extra stack pushes, persistent state, boxes or hit receipts changed.
; Integer actor positions retain exact source half-pixel rectangle endpoints.
.proc RyuKoopaPrimary
  ; Signed 17-bit world deltas: carry distinguishes true adjacent pages from
  ; the far unsigned wrap aliases. All possible overlaps fit -64..64.
  sec
  lda Enemy_X_Position,x
  sbc Player_X_Position
  sta MmTemp
  lda Enemy_PageLoc,x
  sbc Player_PageLoc
  bcs XPositive
  cmp #$ff
  jne Miss
  lda MmTemp
  cmp #$c0
  jcc Miss
  jmp XReady
XPositive:
  cmp #0
  jne Miss
  lda MmTemp
  cmp #65
  jcs Miss
XReady:
  eor #$80
  sta MmTemp
  sec
  lda Enemy_Y_Position,x
  sbc Player_Y_Position
  sta MmDamage
  lda Enemy_Y_HighPos,x
  sbc Player_Y_HighPos
  bcs YPositive
  cmp #$ff
  jne Miss
  lda MmDamage
  cmp #$c0
  jcc Miss
  jmp YReady
YPositive:
  cmp #0
  jne Miss
  lda MmDamage
  cmp #65
  jcs Miss
YReady:
  eor #$80
  sta MmDamage
  ; Inclusive minimum/exclusive maximum after biasing signed deltas by128.
  ldy #0
  lda RgCrouch
  beq BodyYReady
  iny
BodyYReady:
  lda MmDamage
  cmp BodyYMin,y
  bcc Head
  cmp BodyYMaxEx,y
  bcs Head
  ldy PlayerFacingDir
  dey
  lda MmTemp
  cmp BodyXMin,y
  bcc Head
  cmp BodyXMaxEx,y
  bcc Hit
Head:
  ldy #0
  lda RgCrouch
  beq HeadStance
  iny
HeadStance:
  lda Enemy_State,x
  cmp #4
  bne HeadYReady
  iny
  iny
HeadYReady:
  lda MmDamage
  cmp HeadYMin,y
  bcc Miss
  cmp HeadYMaxEx,y
  bcs Miss
  ; DY is dead after this test; reuse that same temporary for the X index.
  lda PlayerFacingDir
  sec
  sbc #1
  asl
  sta MmDamage
  lda Enemy_MovingDir,x
  sec
  sbc #1
  clc
  adc MmDamage
  tay
  lda Enemy_State,x
  cmp #4
  bne HeadXReady
  iny
  iny
  iny
  iny
HeadXReady:
  lda MmTemp
  cmp HeadXMin,y
  bcc Miss
  cmp HeadXMaxEx,y
  bcs Miss
Hit:
  sec
  rts
Miss:
  clc
  rts
BodyYMin:   .byte 111,117
BodyYMaxEx: .byte 132,139
BodyXMin:   .byte 129,89
BodyXMaxEx: .byte 168,128
HeadYMin:   .byte 125,131,115,121
HeadYMaxEx: .byte 142,149,132,139
HeadXMin:   .byte 129,134,89,94,128,137,88,97
HeadXMaxEx: .byte 163,168,123,128,160,169,120,129
.endproc
.endproc

.segment "METASPRITE"
.proc MegaManDrawShots
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  jne Done
  lda MmDeathFlag
  beq :+
    jmp MegaManDrawDeath
  :
  ldx #3
Loop:
  stx MmSlot
  ldy MmBulletType,x
  beq Next
  lda MmBulletAge,x
  lsr
  sta MmTemp
  lda ShotLengths-1,y
  sta MmDamage
  lda MmTemp
Modulo:
  cmp MmDamage
  bcc PhaseReady
  sbc MmDamage
  jmp Modulo
PhaseReady:
  clc
  adc ShotStarts-1,y
  tay
  lda MmBulletDir,x
  cmp #1
  bne Left
  lda MetaspriteTableRightLo,y
  sta R0
  lda MetaspriteTableRightHi,y
  bne Pointer
Left:
  lda MetaspriteTableLeftLo,y
  sta R0
  lda MetaspriteTableLeftHi,y
Pointer:
  sta R1
  lda MmBulletX,x
  sec
  sbc ScreenLeft_X_Pos
  sta R4
  lda MmBulletPage,x
  sbc ScreenLeft_PageLoc
  sta R5
  lda MmBulletY,x
  sta R6
  lda #1
  sta R7
  lda #0
  sta R3
  jsr MetaspriteRenderLoop
Next:
  ldx MmSlot
  dex
  bpl Loop
Done:
  rts
ShotStarts:
  .byte METASPRITE_MM_BULLET_1, METASPRITE_MM_BULLET_2, METASPRITE_MM_BULLET_6
  .byte METASPRITE_MM_BULLET_10, METASPRITE_MM_BULLET_4, METASPRITE_MM_BULLET_13
ShotLengths:
  .byte 1,2,4,3,2,3
.endproc
.popseg

; Both linked HammerBro HRects, aligned independently by exact native/source
; bitmap silhouettes. Easy pivot EX+5/+11, Hard EX+8; foot always EY+24.
; Only Bill types11..13 use source Q8 rectangles. All foreign weapons retain
; the exact pre-correction proxy and native collision core.
.pushseg
.segment "LEGACY_COLD"
.proc BillHammerBroOverlap
  lda MmBulletType
  cmp #69
  beq Advanced
  cmp #70
  beq Advanced
  jmp LegacyTypes
Advanced:
  ldy CrossoverBehaviorVersion
  beq Legacy
  jmp EnemyValidity
LegacyTypes:
  cmp #11
  bcc Legacy
  cmp #14
  bcs Legacy
EnemyValidity:
  lda Enemy_MovingDir,x
  beq Legacy
  cmp #3
  bcs Legacy
  lda Enemy_Y_HighPos,x
  cmp #1
  bne Legacy
  jmp Source
Legacy:
  lda GuestEnemyX,x
  sta BoundingBox_UL_Corner+32
  clc
  adc #16
  sta BoundingBox_LR_Corner+32
  lda GuestEnemyY,x
  sta BoundingBox_UL_Corner+33
  clc
  adc #16
  sta BoundingBox_LR_Corner+33
  ldy #28
  ldx #32
  jmp SprObjectCollisionCore
Source:
  ldy RgSlot
  sec
  lda RgShotX,y
  sbc Enemy_X_Position,x
  sta R1
  lda RgShotPage,y
  sbc Enemy_PageLoc,x
  beq PositiveX
  cmp #$ff
  jne No
  lda R1
  ; Conservative integer hull cull only. The two-rectangle test below owns
  ; admission. Max source radius2.4; hullX[-2,18], hullY[0,24].
  cmp #251
  jcc No
  jmp XReady
PositiveX:
  lda R1
  cmp #22
  jcs No
XReady:
  sec
  lda RgShotY,y
  sbc Enemy_Y_Position,x
  sta R5
  cmp #27
  bcc YReady
  cmp #253
  jcc No
YReady:
  lda RgShotFracX,y
  sta R0
  lda RgShotFracY,y
  sta R4
  ; Source radius scalar is rounded once to Q8, as in frozen growth.
  lda MmBulletType
  cmp #69
  bne OrdinaryRadius
  ldy RgSlot
  lda RgShotVXLo,y
  ora RgShotVXHi,y
  beq OrdinaryRadius
  lda RgShotVYLo,y
  ora RgShotVYHi,y
  beq OrdinaryRadius
  lda #$1f
  sta RgTemp
  lda #2
  sta RgTemp2
  jmp RadiusReady
OrdinaryRadius:
  lda #0
  ldy MmBulletType
  cpy #13
  bne RadiusIndex
  ldy RgSlot
  lda RgShotAge,y
  cmp #35
  bcc :+
    lda #35
  :
  ldy CrossoverBehaviorVersion
  beq RadiusIndex
  cmp #0
  beq RadiusIndex
  sec
  sbc #1
RadiusIndex:
  tay
  lda GrowthRadiusLo,y
  sta RgTemp
  lda GrowthRadiusHi,y
  sta RgTemp2
RadiusReady:
  sec
  lda R0
  sbc RgTemp
  sta R0
  lda R1
  sbc RgTemp2
  sta R1
  sec
  lda R4
  sbc RgTemp
  sta R4
  lda R5
  sbc RgTemp2
  sta R5
  lda CrossoverBehaviorVersion
  beq Symmetric
  ; Hard cached left/top, but local width/height are exactly3 NES pixels.
  lda R0
  sta R2
  lda R4
  sta R6
  clc
  lda R1
  adc #3
  sta R3
  clc
  lda R5
  adc #3
  sta R7
  jmp RectIndex
Symmetric:
  clc
  lda R0
  adc RgTemp
  sta R2
  lda R1
  adc RgTemp2
  sta R3
  clc
  lda R2
  adc RgTemp
  sta R2
  lda R3
  adc RgTemp2
  sta R3
  clc
  lda R4
  adc RgTemp
  sta R6
  lda R5
  adc RgTemp2
  sta R7
  clc
  lda R6
  adc RgTemp
  sta R6
  lda R7
  adc RgTemp2
  sta R7
RectIndex:
  lda CrossoverBehaviorVersion
  asl
  asl
  sta MmProbeIndex
  lda Enemy_MovingDir,x
  cmp #2
  bne First
  inc MmProbeIndex
  inc MmProbeIndex
First:
  ldy MmProbeIndex
Record:
  ; Both Y limits are integral at the documented Q8 projection precision.
  lda R7
  bmi Next
  cmp Top,y
  bcc Next
  lda R5
  bmi Horizontal
  cmp Bottom,y
  bcc Horizontal
  bne Next
  lda R4
  bne Next
Horizontal:
  sec
  lda R2
  sbc LeftLo,y
  lda R3
  sbc LeftHi,y
  bvc :+
    eor #$80
  :
  bmi Next
  sec
  lda RightLo,y
  sbc R0
  lda RightHi,y
  sbc R1
  bvc :+
    eor #$80
  :
  bmi Next
Hit:
  sec
  rts
Next:
  iny
  tya
  and #1
  bne Record
No:
  clc
  rts
; EasyR primary/head, EasyL primary/head, HardR primary/head, HardL primary/head.
LeftLo:  .byte 128,0,128,0,0,0,0,0
LeftHi:  .byte 0,7,5,0,3,10,3,-2
RightLo: .byte 128,0,128,0,0,0,0,0
RightHi: .byte 10,16,15,9,13,18,13,6
Top:     .byte 6,0,6,0,6,0,6,0
Bottom:  .byte 24,10,24,10,24,10,24,10
.endproc
.assert .bank(GrowthRadiusLo) = .bank(RgBILLWeaponsRightLo), lderror, "Bill mapped C000 scalar/art ABI"
.popseg
