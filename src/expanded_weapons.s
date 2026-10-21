.pushseg
.segment "EXPANDED_EX"
.proc PitFlightUpdate
  lda Player_State
  bne Air
  lda #60
  sta XgPitFuel
Stop:
  lda #0
  sta XgPitFlight
  sta XgPitBlocked
  rts
Air:
  cmp #3
  beq Stop
  lda PlayerStatus
  cmp #2
  bne Stop
  lda MmUnderwater
  bne Stop
  lda A_B_Buttons
  and #A_Button
  beq Stop
  lda SavedJoypadBits
  and #Down_Dir
  bne Stop
  lda XgPitFuel
  beq Stop
  lda XgPitFlight
  beq Done
  dec XgPitFuel
  lda #0
  sta MmVY
  sta XgGravity
  sta XgGravity+1
  sta MmFrictionYActive
  ; Sweep the next two-pixel head step. SMB normally stops a jump by
  ; changing its speed; continuous thrust must not overwrite that response
  ; every update and gradually push the head through the ceiling.
  lda Player_Y_Position
  clc
  adc #6
  sta RgTempY
  ldy #2
  jsr HeadCell
  bcs Roof
  ldy #13
  jsr HeadCell
  bcs Roof
  lda #0
  sta XgPitBlocked
  lda #$80
  sta MmVY+1
  lda #$fe                     ; Controlled 1.5 px/update lift, normal collision.
  sta MmVY+2
Done:
  rts
HeadCell:
  tya
  clc
  adc Player_X_Position
  sta RgTempX
  lda Player_PageLoc
  adc #0
  sta RgTempPage
  jmp ExpandedMapCell
Roof:
  lda #0
  sta MmVY
  sta MmVY+1
  sta MmVY+2
  sta MmYFraction
  sta MmYFraction+1
  lda XgPitBlocked
  bne Done
  inc XgPitBlocked
  lda #Sfx_Bump
  sta Square1SoundQueue
  rts
.endproc
.proc ExpandedWeapons
  lda SelectedCharacter
  cmp #CHARACTER_SCROOGE
  bne :+
    farcall ScroogeWeapons
    rts
  :
  lda #0
  sta Fireball_State
  sta Fireball_State+1
  sta FireballMetasprite
  sta FireballMetasprite+1
  lda TimerControl
  jne Done
  lda GameEngineSubroutine
  cmp #8
  jne Done
SophiaCandidatesReady:
  lda SavedJoypadBits
  eor RgPreviousButtons
  and SavedJoypadBits
  sta RgWeaponButtons
  lda SavedJoypadBits
  sta RgPreviousButtons
  lda RgCooldown
  beq :+
    dec RgCooldown
  :
  lda RgShootPose
  beq :+
    dec RgShootPose
  :
  inc MmWorldTime
  bne :+
    inc MmWorldTime+1
  :
  ldx #5
Timers:
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  beq FlashDone                 ; LSR ticks before Remaining/Expanded weapons.
  lda MmEnemyFlash,x
  beq :+
    dec MmEnemyFlash,x
  :
FlashDone:
  dex
  jpl Timers
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  bne HurtInputReady
  lda GuestHurtTicks
  beq HurtInputReady
  lda #0                        ; Track raw history above, suppress new actions.
  sta RgWeaponButtons
  jmp Shots                     ; Jump Slash body contact remains independent.
HurtInputReady:
  lda RgAttack
  jeq NewAttack
  dec RgAttack
  inc RgAttackAge
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  bne PitMelee
  lda RgAttackKind
  beq RyuSword
  lda RgAttackAge
  cmp #3                       ; throw-2, first 45ms source animation tick.
  bne ExistingAttackDone
  farcall AvRyuRelease
  jmp Shots
RyuSword:
  ; Source checkState clears checkAtkRect in ST_CLIMB/ST_VINE. Keep the
  ; existing animation timer above advancing while suppressing sword geometry.
  lda XgWall
  bne ExistingAttackDone
  lda Player_State
  cmp #3
  beq ExistingAttackDone
  lda RgAttackAge
  cmp #3
  bcc ExistingAttackDone
  cmp #9                       ; attack-2 and attack-3 carry the hit rectangle.
  bcs ExistingAttackDone
  jsr Melee
ExistingAttackDone:
  jmp Shots
PitMelee:
  lda RgAttackAge
  cmp #4
  jcc Shots
  cmp #9
  jcs Shots
  jsr Melee
  jmp Shots
NewAttack:
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  jne Pit
  ; Both source primary and Special return immediately in ST_VINE.
  lda Player_State
  cmp #3
  beq ExistingAttackDone
  lda RgWeaponButtons
  and #Select_Button
  jne RyuThrow
  lda SavedJoypadBits
  and #Up_Dir
  jeq Sword
  lda RgWeaponButtons
  and #B_Button
  jne RyuThrow
Sword:
  ; Only primary is rejected on a wall. Select/Up+B already dispatch above
  ; to the separately permitted source wall subweapon/throw path.
  lda XgWall
  bne ExistingAttackDone
  lda InvSelected+CHARACTER_RYU
  cmp #5
  bne :+
  lda Player_State
  beq :+
  lda RgWeaponButtons
  and #B_Button
  beq :+
    farcall AvRyuSpecial
    jmp Shots
  :
  lda RgWeaponButtons
  and #B_Button
  jeq Shots
  jsr BeginMelee
  jmp Shots
RyuThrow:
  farcall AvRyuSpecial
  jmp Shots
Pit:
  cmp #CHARACTER_PIT
  jne CheckFire
  lda RgWeaponButtons
  and #Select_Button
  jeq CheckFire
  jsr BeginMelee
  jmp Shots
CheckFire:
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  jeq Automatic
  cmp #CHARACTER_SOPHIA
  beq SophiaFresh
  lda RgWeaponButtons
  and #B_Button
  jeq Shots
  jne Fire
SophiaFresh:
  lda RgWeaponButtons
  and #B_Button
  jeq Shots
  jmp Fire
Automatic:
  lda InvSelected+CHARACTER_BASS
  jne Shots
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  bne :+
    lda SavedJoypadBits
    and #B_Button
    bne BassFireHeld
    lda #0
    sta XgBassFirePhase
    jmp Shots
BassFireHeld:
    lda RgWeaponButtons
    and #B_Button
    beq Fire
    lda #0
    sta RgCooldown
    sta XgBassFirePhase
    jmp Fire
  :
  lda SavedJoypadBits
  and #B_Button | Select_Button
  jeq Shots
Fire:
  jsr FireShot
Shots:
  ; Fresh input uses the live raw latch, which may change after the parsed
  ; movement buttons. Test the actual post-input pool so new cannon shots
  ; receive this batch's candidates without changing input/latch semantics.
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne ShotPoolReady
  ldx #9
SophiaCheckPool:
  lda RgShotType,x
  bne SophiaActiveCandidates
  dex
  bpl SophiaCheckPool
  bmi ShotPoolReady
SophiaActiveCandidates:
  farcall GuestPrepareEnemies
ShotPoolReady:
  ldx #9
Loop:
  stx RgSlot
  lda RgShotType,x
  jeq Next
  cmp #9
  jcs Next
  cmp #6
  bne ActiveShot
  lda RgShotImpact,x
  beq ActiveShot
  bmi ActiveShot
  dec RgShotImpact,x
  jne Next
  lda #0
  sta RgShotType,x
  jmp Next
ActiveShot:
  lda RgShotType,x
  inc RgShotAge,x
  cmp #2
  bne :+
    lda RgShotAge,x
    cmp #3
    jcc Next                  ; Original Rygar has a short throw windup.
  :
  jsr MoveShot
  ldx RgSlot
  lda RgShotType,x
  jeq Next
  cmp #3
  jeq Next                    ; Luigi's fireball uses native-style terrain.
  lda RgShotImpact,x
  jmi Next                    ; Source armor deflection disables hit tests.
  jsr Bridge
  farcall MegaManWeapons::Blocks
  lda MmBulletType
  jne Enemies
  ldx RgSlot
  lda RgShotType,x
  cmp #2
  beq ReturnShot
  cmp #8
  jne Kill
ReturnShot:
  cmp #2
  bne :+
    lda #1
    sta XgDiskReturning
    jmp Enemies
  :
  lda #60
  sta RgShotAge,x              ; A blocked Diskarmor returns to its owner.
  jmp Enemies
Kill:
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne ClearShot
  jsr SophiaImpact
  jmp Next
ClearShot:
  lda #0
  sta RgShotType,x
  jmp Next
Enemies:
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne CheckEnemies
  lda RgEnemiesPresent
  jeq Next                    ; No enemy can be hit during this update.
CheckEnemies:
  ldx RgSlot
  lda #0
  sta RgShotHitsNow,x
  jsr Bridge
  farcall MegaManWeapons::Enemies
  ldx RgSlot
  lda RgShotType,x
  cmp #8
  bne :+
    lda RgShotHitsNow,x
    sta RgShotHits,x
  :
  lda MmBulletType
  jne Next
  ldx RgSlot
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne ClearShot
  jsr SophiaImpact
  jmp Next
Next:
  ldx RgSlot
  dex
  jpl Loop
Done:
::ExpandedWeaponsFinish:
  rts
BeginMelee:
  lda #12
  ldx SelectedCharacter
  cpx #CHARACTER_RYU
  bne :+
    lda #14                     ; Five visible 45ms phases, then the end label.
  :
  sta RgAttack
  lda #0
  sta RgAttackKind
  sta RgAttackAge
  sta RgMeleeHits
  jsr ClearMeleeMap
  lda #Sfx_Fireball
  sta Square1SoundQueue
  rts
ClearMeleeMap:
  lda #0
  ldx #0
ClearMap:
  sta RgMeleeBlocks,x
  sta RgMeleeBlocks+160,x
  inx
  jne ClearMap
  rts
FireShot:
  ; Sophia's inventory-owned missiles are spawned by RemainingWeapons.
  ; B always uses her cannon, including when Select is pressed together.
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  bne :+
    lda XgDash
    jne Return
  :
  lda RgCooldown
  jne Return
  lda Player_State
  cmp #3
  jeq Return
  lda SelectedCharacter
  sec
  sbc #CHARACTER_PIT
  tax
  lda Types,x
  sta RgSpawnType
  lda SelectedCharacter
  cmp #CHARACTER_LUIGI
  jne Count
  lda RgCrouch
  jne Return
  lda PlayerStatus
  cmp #2
  jne Return
Count:
  lda #0
  sta RgCount
  ldx #9
CountLoop:
  lda RgShotType,x
  beq :+
    ldy SelectedCharacter
    cpy #CHARACTER_SOPHIA
    bne CountActive
    cmp #6                     ; Missiles have their own independent limits.
    bne :+
    lda RgShotImpact,x
    beq CountActive
    bpl :+                     ; The source explosion is no longer a bullet.
CountActive:
    inc RgCount
  :
  dex
  jpl CountLoop
  lda SelectedCharacter
  cmp #CHARACTER_RYGAR
  jne Many
  lda RgCount
  jne Return
  jsr ClearMeleeMap
Many:
  ldx #4
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  bne :+
    lda PlayerStatus
    bne Limit
    ldx #3
    bne Limit
  :
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  jeq Two
  cmp #CHARACTER_RYU
  bne :+
    ldx #1
    jmp Limit
  :
  cmp #CHARACTER_SOPHIA
  bne :+
    ldx #3
    jmp Limit
  :
  cmp #CHARACTER_LUIGI
  jne Limit
Two:
  ldx #2
Limit:
  cpx RgCount
  bcc PoolFull
  beq PoolFull
  jmp FindShotSlot
PoolFull:
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  bne Return
  jsr BassCadence
  rts
FindShotSlot:
  ldx #9
Find:
  lda RgShotType,x
  jeq Found
  dex
  jpl Find
Return:
  rts
Found:
  stx RgSlot
  lda RgSpawnType
  sta RgShotType,x
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  bne :+
  lda InvSelected+CHARACTER_RYU
  cmp #3
  bne :+
    lda #8
    sta RgShotType,x
  :
Init:
  lda #0
  sta RgShotAge,x
  sta RgShotHits,x
  sta RgShotImpact,x
  sta RgShotFracX,x
  sta RgShotFracY,x
  sta RgShotVXLo,x
  sta RgShotVYLo,x
  sta RgShotVYHi,x
  sta XgShotAim,x
  lda SelectedCharacter
  cmp #CHARACTER_RYGAR
  bne :+
    lda #20
    sta XgDiskReach
    lda #0
    sta XgDiskReturning
  :
  lda PlayerFacingDir
  sta RgShotDir,x
  lda Player_X_Position
  clc
  adc #8
  sta RgShotX,x
  lda Player_PageLoc
  adc #0
  sta RgShotPage,x
  lda #18
  ldy RgCrouch
  beq :+
    lda #25
  :
  ldy SelectedCharacter
  cpy #CHARACTER_LUIGI
  bne :+
    lda #18
  :
  clc
  adc Player_Y_Position
  sta RgShotY,x
  lda Player_Y_HighPos
  adc #0
  sta RgShotYHigh,x
  lda #3
  sta RgShotVXHi,x
  lda RgShotDir,x
  cmp #1
  jeq Aim
  lda #$fd
  sta RgShotVXHi,x
Aim:
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  bne :+
    jsr BassAim
    jmp Finish
  :
  cmp #CHARACTER_RYGAR
  jeq Finish
  cmp #CHARACTER_SOPHIA
  bne :+
    farcall RemainingPower      ; Freeze the acquired tier at actual creation.
    sta RgAttackPower
    sta SsMode,x              ; Source cannon type is fixed at creation.
    jsr SophiaShotOrigin
    jsr SophiaCannonVelocity
    jmp Finish
  :
  cmp #CHARACTER_RYU
  bne :+
    lda #0
    sta RgShotVXLo,x
    lda #5
    sta RgShotVXHi,x
    jsr SignShotX
    farcall RyuProjectileSpawn
    jmp Finish
  :
  cmp #CHARACTER_LUIGI
  jne CheckAim
  lda Player_X_Position
  clc
  adc #13
  sta RgShotX,x
  lda Player_PageLoc
  adc #0
  sta RgShotPage,x
  lda PlayerFacingDir
  cmp #1
  beq :+
    sec
    lda RgShotX,x
    sbc #10
    sta RgShotX,x
    lda RgShotPage,x
    sbc #0
    sta RgShotPage,x
  :
  lda Player_Y_Position
  clc
  adc #11
  sta RgShotY,x
  lda #$f5
  sta RgShotVXLo,x
  lda #3
  sta RgShotVXHi,x
  jsr SignShotX
  lda #$80
  sta RgShotVYLo,x
  lda #2
  sta RgShotVYHi,x
  jmp Finish
CheckAim:
  lda #$2b
  sta RgShotVXLo,x
  lda #4
  sta RgShotVXHi,x
  jsr SignShotX
  lda SavedJoypadBits
  and #Up_Dir
  jeq Down
  lda #4
  sta XgShotAim,x
  lda RgShotVXLo,x
  sta RgShotVYLo,x
  lda RgShotVXHi,x
  sta RgShotVYHi,x
  lda RgShotDir,x
  cmp #2
  beq :+
    jsr NegateShotY
  :
  lda SavedJoypadBits
  and #3
  jeq Vertical
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  jne Finish
Vertical:
  lda #0
  sta RgShotVXLo,x
  sta RgShotVXHi,x
  jmp Finish
Down:
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  jne Finish
  lda SavedJoypadBits
  and #Down_Dir
  jeq Finish
  lda SavedJoypadBits
  and #3
  jeq Finish                  ; Bass has seven directions; no straight down.
  lda #3
  sta RgShotVYHi,x
Finish:
  lda #8
  sta RgShootPose
  sta RgCooldown
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  beq FreshCadence
  cmp #CHARACTER_LUIGI
  beq FreshCadence
  cmp #CHARACTER_SOPHIA
  beq FreshCadence
  cmp #CHARACTER_BASS
  bne FireSound
    jsr BassCadence
  jmp FireSound
FreshCadence:
  ; These source pressAtkBtn handlers gate only on a fresh press and pool size.
  ; The shooting-pose timer does not prevent another shot.
  lda #0
  sta RgCooldown
FireSound:
  lda #Sfx_Fireball
  sta Square1SoundQueue
  rts
Types: .byte 1,2,3,4,5,6
SignShotX:
  lda RgShotDir,x
  cmp #1
  beq SignShotDone
  sec
  lda #0
  sbc RgShotVXLo,x
  sta RgShotVXLo,x
  lda #0
  sbc RgShotVXHi,x
  sta RgShotVXHi,x
SignShotDone:
  rts
NegateShotY:
  sec
  lda #0
  sbc RgShotVYLo,x
  sta RgShotVYLo,x
  lda #0
  sbc RgShotVYHi,x
  sta RgShotVYHi,x
  rts
BassCadence:
  ; 75 ms is 4.5 updates, including attempts while the shot pool is full.
  lda XgBassFirePhase
  eor #1
  sta XgBassFirePhase
  clc
  adc #4
  sta RgCooldown
  lda #12
  sta RgShootPose
  rts
BassAim:
  ; Crossover 2: 580 Flash px/s, diagonals at 75%, seven directions.
  lda #$d5
  sta RgShotVXLo,x
  lda #4
  sta RgShotVXHi,x
  lda #0
  sta XgShotAim,x
  lda SavedJoypadBits
  and #Up_Dir
  beq BassDown
  lda SavedJoypadBits
  and #3
  beq BassUp
  lda #1
  sta XgShotAim,x
  jsr BassDiagonal
  jmp BassUpVelocity
BassUp:
  lda #3
  sta XgShotAim,x
  lda #0
  sta RgShotVXLo,x
  sta RgShotVXHi,x
  lda #$d5
  sta RgShotVYLo,x
  lda #4
  sta RgShotVYHi,x
  jmp BassUpVelocity
BassDown:
  lda SavedJoypadBits
  and #Down_Dir
  beq BassMuzzle
  lda #2
  sta XgShotAim,x
  jsr BassDiagonal
  jmp BassMuzzle
BassUpVelocity:
  sec
  lda #0
  sbc RgShotVYLo,x
  sta RgShotVYLo,x
  lda #0
  sbc RgShotVYHi,x
  sta RgShotVYHi,x
BassMuzzle:
  ldy XgShotAim,x
  lda BassMuzzleX,y
  sta RgTemp
  lda Player_X_Position
  clc
  adc #8
  sta RgShotX,x
  lda Player_PageLoc
  adc #0
  sta RgShotPage,x
  lda RgShotDir,x
  cmp #1
  beq BassMuzzleRight
  sec
  lda RgShotX,x
  sbc RgTemp
  sta RgShotX,x
  lda RgShotPage,x
  sbc #0
  sta RgShotPage,x
  sec
  lda #0
  sbc RgShotVXLo,x
  sta RgShotVXLo,x
  lda #0
  sbc RgShotVXHi,x
  sta RgShotVXHi,x
  jmp BassMuzzleY
BassMuzzleRight:
  clc
  lda RgShotX,x
  adc RgTemp
  sta RgShotX,x
  lda RgShotPage,x
  adc #0
  sta RgShotPage,x
BassMuzzleY:
  lda #18                       ; Ground/air y = feet - 13.5 / 17.5.
  ldy Player_State
  beq :+
    lda #14
  :
  ldy XgShotAim,x
  clc
  adc BassMuzzleYOffsets,y
  clc
  adc Player_Y_Position
  sta RgShotY,x
  lda Player_Y_HighPos
  adc #0
  sta RgShotYHigh,x
  lda #$80
  sta RgShotFracY,x
  rts
BassDiagonal:
  lda #$a0
  sta RgShotVXLo,x
  sta RgShotVYLo,x
  lda #3
  sta RgShotVXHi,x
  sta RgShotVYHi,x
  rts
BassMuzzleX: .byte 19,16,16,5
BassMuzzleYOffsets: .byte 0,-7,7,-10
MoveShot:
  ldx RgSlot
  lda RgShotImpact,x
  jmi Integrate
  lda RgShotType,x
  cmp #1
  bne :+
    lda PlayerStatus
    bne :+
    lda RgShotAge,x
    cmp #13
    jcs MoveKill                 ; 100 Flash pixels at 500px/s: 12 updates.
  :
  lda RgShotType,x
  cmp #2
  jeq Diskarmor
  cmp #8
  bne :+
    farcall RyuWindmillMotion
    ldx RgSlot
    lda RgShotType,x
    jeq MoveDone
    jmp Integrate
  :
  lda RgShotAge,x
  cmp #150
  jcs MoveKill
Missile:
  lda RgShotType,x
  cmp #7
  jne Fireball
  lda PlayerStatus
  cmp #2
  jne Integrate
  jsr HomeEnemy
  jmp Integrate
Fireball:
  cmp #3
  jne Integrate
  clc
  lda RgShotVYLo,x
  adc #48
  sta RgShotVYLo,x
  lda RgShotVYHi,x
  adc #0
  sta RgShotVYHi,x
  bmi Integrate
  cmp #2
  bcc Integrate
  bne CapFireball
  lda RgShotVYLo,x
  cmp #$80
  bcc Integrate
CapFireball:
  lda #$80
  sta RgShotVYLo,x
  lda #2
  sta RgShotVYHi,x
Integrate:
  clc
  lda RgShotFracX,x
  adc RgShotVXLo,x
  sta RgShotFracX,x
  lda RgShotX,x
  adc RgShotVXHi,x
  sta RgShotX,x
  lda #0
  ldy RgShotVXHi,x
  bpl :+
    lda #$ff
  :
  adc RgShotPage,x
  sta RgShotPage,x
  clc
  lda RgShotFracY,x
  adc RgShotVYLo,x
  sta RgShotFracY,x
  lda RgShotY,x
  adc RgShotVYHi,x
  sta RgShotY,x
  lda #0
  ldy RgShotVYHi,x
  bpl :+
    lda #$ff
  :
  adc RgShotYHigh,x
  sta RgShotYHigh,x
  lda RgShotType,x
  cmp #3
  jne Bounds
  jsr LuigiTerrain
  ldx RgSlot
  lda RgShotType,x
  jeq MoveDone
  jsr Bridge
  farcall MegaManWeapons::Enemies
  lda MmBulletType
  jne Bounds
  ldx RgSlot
  jmp MoveKill
Bounds:
  ldx RgSlot
  lda RgShotType,x
  cmp #4
  bne :+
    lda RgShotYHigh,x
    cmp #1
    jne MoveKill                ; Bass's upward/reflected shots leave the pool.
  :
  lda RgShotType,x
  cmp #8                       ; Source windmill updates beyond the viewport.
  jeq MoveDone
  lda RgShotYHigh,x
  cmp #2
  jcs MoveKill
  cmp #1
  jne XBounds
  lda RgShotY,x
  cmp #240
  jcs MoveKill
XBounds:
  lda RgShotX,x
  sec
  sbc ScreenLeft_X_Pos
  lda RgShotPage,x
  sbc ScreenLeft_PageLoc
  jeq MoveDone
  cmp #$ff
  jne MoveKill
  lda RgShotType,x
  cmp #2
  jeq MoveDone
MoveKill:
  lda #0
  sta RgShotType,x
MoveDone:
  rts
Diskarmor:
  ; Original NES OAM: center offsets 24,28,32,36,40,36,32,28,24,20.
  ; Retraction is four pixels/update, with one short chain tail. The two
  ; longer reaches are this port's mushroom/flower adaptation.
  lda #2
  sta RgShootPose
  lda XgDiskReturning
  jne RetractDisk
  lda XgDiskReach
  clc
  adc #4
  sta XgDiskReach
  ldy PlayerStatus
  cmp DiskReach,y
  jcc PositionDisk
  lda DiskReach,y
  sta XgDiskReach
  lda #1
  sta XgDiskReturning
  jmp PositionDisk
RetractDisk:
  lda XgDiskReach
  sec
  sbc #4
  sta XgDiskReach
  cmp #20
  jcc CatchDisk
PositionDisk:
  lda Player_X_Position
  clc
  adc #8
  sta RgShotX,x
  lda Player_PageLoc
  adc #0
  sta RgShotPage,x
  lda RgShotDir,x
  cmp #2
  jeq DiskLeft
  lda RgShotX,x
  clc
  adc XgDiskReach
  sta RgShotX,x
  lda RgShotPage,x
  adc #0
  sta RgShotPage,x
  jmp DiskHeight
DiskLeft:
  ; The native mirrored pose offsets the weapon anchor by two pixels.
  clc
  lda RgShotX,x
  adc #2
  sta RgShotX,x
  lda RgShotPage,x
  adc #0
  sta RgShotPage,x
  lda RgShotX,x
  sec
  sbc XgDiskReach
  sta RgShotX,x
  lda RgShotPage,x
  sbc #0
  sta RgShotPage,x
DiskHeight:
  lda #8
  ldy RgCrouch
  beq :+
    lda #15
  :
  clc
  adc Player_Y_Position
  sta RgShotY,x
  lda Player_Y_HighPos
  adc #0
  sta RgShotYHigh,x
  jmp Bounds
CatchDisk:
  lda #0
  sta XgDiskReach
  sta RgShotType,x
  sta RgShootPose
  rts
DiskReach: .byte 40,64,88
Home:
  lda Player_X_Position
  clc
  adc #8
  sta RgTempX
  lda Player_PageLoc
  adc #0
  sta RgTempPage
  lda Player_Y_Position
  clc
  adc #18
  sta RgTempY
  lda RgShotX,x
  sec
  sbc RgTempX
  clc
  adc #6
  cmp #13
  jcs HomeToPoint
  lda RgShotPage,x
  cmp RgTempPage
  jne HomeToPoint
  lda RgShotY,x
  sec
  sbc RgTempY
  clc
  adc #8
  cmp #17
  jcs HomeToPoint
  lda #0
  sta RgShotType,x
  rts
HomeEnemy:
  ldy #5
FindEnemy:
  lda Enemy_Flag,y
  jeq NextEnemy
  lda Enemy_ID,y
  cmp #$15
  jcs NextEnemy
  lda Enemy_X_Position,y
  clc
  adc #8
  sta RgTempX
  lda Enemy_PageLoc,y
  adc #0
  sta RgTempPage
  lda Enemy_Y_Position,y
  clc
  adc #8
  sta RgTempY
  jmp HomeToPoint
NextEnemy:
  dey
  jpl FindEnemy
  rts
HomeToPoint:
  lda #3
  sta RgShotVXHi,x
  lda RgTempX
  sec
  sbc RgShotX,x
  lda RgTempPage
  sbc RgShotPage,x
  bpl :+
    lda #$fd
    sta RgShotVXHi,x
  :
  lda #0
  sta RgShotVYHi,x
  lda RgTempY
  sec
  sbc RgShotY,x
  clc
  adc #4
  cmp #9
  jcc HomeDone
  lda #2
  ldy RgTempY
  pha
  tya
  cmp RgShotY,x
  pla
  bcs :+
    lda #$fe
  :
  sta RgShotVYHi,x
HomeDone:
  rts
LuigiTerrain:
  lda RgShotX,x
  sta RgTempX
  lda RgShotPage,x
  sta RgTempPage
  lda RgShotY,x
  clc
  adc #4
  sta RgTempY
  jsr MapCell
  jcc Side
  lda RgShotVYHi,x
  jmi Side
  lda #$fd
  sta RgShotVYHi,x
  lda #$c0
  sta RgShotVYLo,x
  lda RgTempY
  and #$f0
  sec
  sbc #5
  sta RgShotY,x
Side:
  lda RgShotY,x
  sta RgTempY
  lda RgShotX,x
  clc
  adc #4
  ldy RgShotDir,x
  cpy #1
  beq :+
    sec
    sbc #8
  :
  sta RgTempX
  jsr MapCell
  jcc TerrainDone
  lda #0
  sta RgShotType,x
TerrainDone:
  rts
MapCell:
::ExpandedMapCell:
  lda RgTempY
  cmp #32
  jcc Empty
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
  jeq Page0
  lda R0
  clc
  adc #208
  sta R0
  lda #>Block_Buffer_1
  adc #0
  jmp ReadCell
Page0:
  lda #>Block_Buffer_1
ReadCell:
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
  jeq Empty
  cmp #$23
  jeq Empty
  cmp #$26
  jeq Empty
  cmp #$c2
  jeq Empty
  sec
  rts
Empty:
  clc
  rts
Bridge:
  ldx RgSlot
  lda RgShotX,x
  sta MmBulletX
  lda RgShotPage,x
  sta MmBulletPage
  lda RgShotY,x
  sta MmBulletY
  lda RgShotDir,x
  sta MmBulletDir
  lda RgShotType,x
  cmp #1
  bne :+
    lda #26
    clc
    adc PlayerStatus
    jmp Type
  :
  cmp #6
  bne :+
    lda SsMode,x
    cmp #2
    bne NotCrusher
    lda #76
    jne Type
NotCrusher:
    clc
    adc #36
    jne Type
  :
  cmp #4
  bne :+
    lda #31
    jmp Type
  :
  tay
  lda DamageTypes-1,y
Type:
  sta MmBulletType
  lda #0
  sta MmSlot
  tax
  rts
DamageTypes: .byte 26,29,30,31,34,36,35,39
Melee:
  farcall RemainingPower
  ; Test the returned tier before loading the collision ID. Restoring A=32
  ; from the stack previously made the unextended sword use the wave hitbox.
  cmp #1
  lda #32
  bcc :+
    lda #33
  :
  ldx SelectedCharacter
  cpx #CHARACTER_PIT
  bne :+
    lda #38
  :
  sta XgMeleeType
  sta MmBulletType
  lda Player_X_Position
  clc
  adc #8
  sta MmBulletX
  lda Player_PageLoc
  adc #0
  sta MmBulletPage
  ; Source Ryu rectangles, scaled from Flash pixels by 1/2. The pose's
  ; foot anchor is (playerX+8, playerY+32). Both stances keep the same
  ; near edge; the extension grows outward, rather than toward Ryu.
  lda #20
  ldx XgMeleeType
  cpx #38
  bne :+
    lda #18
    bne MeleeReachReady
  :
  cpx #33
  bne MeleeReachReady
    lda #27
    ldx RgCrouch
    beq MeleeReachReady
      lda #28
MeleeReachReady:
  ldx PlayerFacingDir
  cpx #1
  beq :+
    eor #$ff
    clc
    adc #1
  :
  sta RgTemp
  clc
  adc MmBulletX
  sta MmBulletX
  lda #0
  bit RgTemp
  bpl :+
    lda #$ff
  :
  adc MmBulletPage
  sta MmBulletPage
  lda #10
  ldx XgMeleeType
  cpx #38
  bne :+
    lda #17
    bne MeleeYReady
  :
  cpx #33
  bne :+
    lda #15
  :
  ldx RgCrouch
  beq :+
    clc
    adc #6
    ldx XgMeleeType
    cpx #32
    bne :+
      clc
      adc #1
  :
MeleeYReady:
  clc
  adc Player_Y_Position
  sta MmBulletY
  lda PlayerFacingDir
  sta MmBulletDir
  lda #0
  sta MmSlot
  farcall MegaManWeapons::Blocks
  lda XgMeleeType
  sta MmBulletType
  lda #0
  sta MmSlot
  farcall MegaManWeapons::Enemies
  rts
.endproc

.proc ExpandedEnemyHit
  lda MmBulletType
  cmp #29
  jeq Disk
  cmp #39
  jeq Windmill
  cmp #41
  jeq Disk
  cmp #32
  jeq Melee
  cmp #33
  jeq Melee
  cmp #38
  jeq Melee
Hit:
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  beq :+                       ; Ryu DEFAULT_PROPS has FLASH, never STOP.
    lda #12
    sta RgEnemyStun,x
  :
  clc
  rts
Melee:
  lda Bits,x
  and RgMeleeHits
  jne Skip
  lda Bits,x
  ora RgMeleeHits
  sta RgMeleeHits
  jmp Hit
Disk:
  lda Bits,x
  ldy RgSlot
  and RgShotHits,y
  jne Skip
  lda Bits,x
  ora RgShotHits,y
  sta RgShotHits,y
  jmp Hit
Windmill:
  lda Bits,x
  ldy RgSlot
  ora RgShotHitsNow,y
  sta RgShotHitsNow,y
  lda Bits,x
  and RgShotHits,y
  jne Skip
  jmp Hit
Skip:
  sec
  rts
Bits: .byte 1,2,4,8,16,32
.endproc

.segment "EXPANDED_EX"
.proc SophiaShotOrigin
  ; Source setDir(), in half-resolution NES coordinates. XgWall retains
  ; the contact side (1=right,2=left); XgJumpUsed retains tangent facing.
  lda #0
  sta RgShotFracX,x
  sta RgShotFracY,x
  lda PlayerFacingDir
  sta RgShotDir,x
  lda #0
  ldy PlayerFacingDir
  cpy #2
  bne :+
    lda #$40
  :
  sta XgShotAim,x
  lda XgWall
  jne Wall
  lda XgCeiling
  jeq Ground
  lda SavedJoypadBits
  and #Down_Dir
  jeq Horizontal
  lda #4
  sta RgShotDir,x
  lda XgShotAim,x
  ora #24
  sta XgShotAim,x
  lda #32
  sta RgTempY
  jmp UpX
Ground:
  lda SavedJoypadBits
  and #Up_Dir
  jeq Horizontal
  lda #3
  sta RgShotDir,x
  lda XgShotAim,x
  ora #8
  sta XgShotAim,x
  lda #7
  sta RgTempY
UpX:
  lda #4
  ldy PlayerFacingDir
  cpy #1
  jeq SetX
  lda #12
  jne SetX
Horizontal:
  lda #$80                    ; HORZ_Y_OFS=25 Flash pixels is 12.5 NES pixels.
  sta RgShotFracY,x
  lda #19
  sta RgTempY
  lda #14
  ldy PlayerFacingDir
  cpy #1
  jeq SetX
  lda #2
  jne SetX
Wall:
  lda XgWall
  eor #3
  sta RgTemp
  lda SavedJoypadBits
  and #3
  cmp RgTemp
  jeq Away
  lda #$48                  ; Clockwise source rotation of the mirrored sprite.
  sta XgShotAim,x
  lda #3
  ldy XgJumpUsed
  cpy #1
  bne :+
    lda #24
    sta XgShotAim,x
    lda #4
  :
  sta RgShotDir,x
  lda #12
  ldy RgShotDir,x
  cpy #4
  bne :+
    lda #24
  :
  sta RgTempY
  lda #$80
  sta RgShotFracX,x
  lda #1
  ldy XgWall
  cpy #1
  beq SetX
  lda #14
  bne SetX
Away:
  lda RgTemp
  sta RgShotDir,x
  lda #18
  sta RgTempY
  lda XgWall
  cmp #1
  bne AwayRight
  lda #$40
  ldy XgJumpUsed
  cpy #1
  bne :+
    lda #16
  :
  sta XgShotAim,x
  lda #$f5                  ; Nx - UP_Y_OFS/2, outside the right-hand wall.
  bne SetX
AwayRight:
  lda #$50
  ldy XgJumpUsed
  cpy #1
  bne :+
    lda #0
  :
  sta XgShotAim,x
  lda #27
SetX:
  ldy #0
  cmp #$80
  bcc :+
    dey
  :
  clc
  adc Player_X_Position
  sta RgShotX,x
  tya
  adc Player_PageLoc
  sta RgShotPage,x
  lda RgTempY
  clc
  adc Player_Y_Position
  sta RgShotY,x
  lda Player_Y_HighPos
  adc #0
  sta RgShotYHigh,x
  rts
.endproc
.proc SophiaCannonVelocity
  lda #0
  sta RgShotVXLo,x
  sta RgShotVXHi,x
  sta RgShotVYLo,x
  sta RgShotVYHi,x
  lda RgShotDir,x
  cmp #3
  bcc Horizontal
  lda #$c0                    ; SPEED450/120; missile cap425/120 is separate.
  sta RgShotVYLo,x
  lda #3
  sta RgShotVYHi,x
  lda RgShotDir,x
  cmp #3
  bne Done
  jmp ExpandedWeapons::NegateShotY
Horizontal:
  lda #$c0
  sta RgShotVXLo,x
  lda #3
  sta RgShotVXHi,x
  jmp ExpandedWeapons::SignShotX
Done:
  rts
.endproc
.proc ExpandedWeaponPointer
  jsr ExpandedGraphicsBank
  ldx RgSlot
  lda RgShotAge,x
  lsr
  ldy SelectedCharacter
  cpy #CHARACTER_RYU
  beq :+
  cpy #CHARACTER_SOPHIA
  beq :+
  lsr
  :
  and #3
  clc
  adc XgShotAim,x
  tay
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  jne NotSophiaArt
    lda RgShotImpact,x
    beq SophiaProjectileArt
    bmi SophiaProjectileArt
    sta RgTemp
    lda #10
    sec
    sbc RgTemp
    lsr
    clc
    adc #48                    ; Source bullet explosion, including blank frame2.
    tay
    lda SelectedCharacter
    jmp NotSophiaArt
SophiaProjectileArt:
    lda RgShotType,x
    cmp #44
    bcs SophiaMissileArt
    tya
    and #3
    tay
    lda SsMode,x
    beq SophiaArtReady
    cmp #1
    bne SophiaCrusherArt
    ldy #4                    ; Source frame8 is Hyper.
    bne SophiaArtReady
SophiaCrusherArt:
    tya
    cmp #3
    bcc SophiaCrusherFrame
      lda #2                  ; Source crusherEnd repeats its last visible frame.
SophiaCrusherFrame:
    clc
    adc #5                    ; Source frames9/10/11 are Crusher.
    tay
SophiaArtReady:
    lda XgShotAim,x
    and #$18
    sta RgTemp
    tya
    clc
    adc RgTemp
    tay
SophiaOrientationReady:
    lda SelectedCharacter
    jmp NotSophiaArt
SophiaMissileArt:
    cmp #45
    bne SophiaMissilePhaseStart
    ; The source homing missile turns with its velocity. Resolve the native
    ; cardinal pose here, only when its committed OAM will actually draw.
    lda RgShotVXHi,x
    bpl :+
      eor #$ff
      clc
      adc #1
    :
    sta RgTemp
    lda RgShotVYHi,x
    bpl :+
      eor #$ff
      clc
      adc #1
    :
    cmp RgTemp
    bcc SophiaHomeHorizontal
    lda #8
    ldy RgShotVYHi,x
    bmi SophiaHomeAimReady
    lda #24
    bne SophiaHomeAimReady
SophiaHomeHorizontal:
    lda #0
    ldy RgShotVXHi,x
    bpl SophiaHomeAimReady
    lda #$40
SophiaHomeAimReady:
    sta XgShotAim,x
SophiaMissilePhaseStart:
    lda XgShotAim,x
    and #$18
    lsr
    lsr
    lsr
    tay
    lda RgShotType,x
    cmp #45
    bne SophiaMissileFlame
    lda SsMode,x
    bmi SophiaMissileUnlit
SophiaMissileFlame:
    lda RgShotAge,x
    and #2                    ; Source fast timer=1000/30ms, two NES frames.
    bne SophiaMissileUnlit
    lda SophiaMissileTurns,y
    clc
    adc #32
    tay
    lda SelectedCharacter
    jmp NotSophiaArt
SophiaMissileUnlit:
    tya
    clc
    adc #44
    tay
    lda SelectedCharacter
NotSophiaArt:
  cmp #CHARACTER_PIT
  bne :+
    lda PlayerStatus
    clc
    adc XgShotAim,x
    tay
  :
  lda RgShotType,x
  cmp #8
  bne :+
    tya
    clc
    adc #4
    tay
    lda RgShotType,x
  :
  cmp #7
  bne :+
    ldy #8
  :
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  jeq Pit
  cmp #CHARACTER_RYGAR
  jeq Rygar
  cmp #CHARACTER_LUIGI
  jeq Luigi
  cmp #CHARACTER_BASS
  jeq Bass
  cmp #CHARACTER_RYU
  jeq Ryu
  lda XgShotAim,x
  and #$40
  bne SophiaLeft
  lda XgSOPHIAWeaponLo,y
  sta R0
  lda XgSOPHIAWeaponHi,y
  jmp Pointer
SophiaLeft:
  lda XgSOPHIAWeaponLeftLo,y
  sta R0
  lda XgSOPHIAWeaponLeftHi,y
  jmp Pointer
Pit:
  lda RgShotDir,x
  cmp #2
  beq PitLeft
  lda XgPITWeaponLo,y
  sta R0
  lda XgPITWeaponHi,y
  jmp Pointer
PitLeft:
  lda XgPITWeaponLeftLo,y
  sta R0
  lda XgPITWeaponLeftHi,y
  jmp Pointer
Rygar:
  lda RgShotDir,x
  cmp #2
  beq RygarLeft
  lda XgRYGARWeaponLo,y
  sta R0
  lda XgRYGARWeaponHi,y
  jmp Pointer
RygarLeft:
  lda XgRYGARWeaponLeftLo,y
  sta R0
  lda XgRYGARWeaponLeftHi,y
  jmp Pointer
Luigi:
  lda XgLUIGIWeaponLo,y
  sta R0
  lda XgLUIGIWeaponHi,y
  jmp Pointer
Bass:
  lda XgBASSWeaponLo,y
  sta R0
  lda XgBASSWeaponHi,y
  jmp Pointer
Ryu:
  ; Source RyuProjectile changes velocity, never scaleX: both launch directions
  ; retain the same shuriken/windmill spin. Mirroring reverses its chiral poses.
  lda XgRYUWeaponLo,y
  sta R0
  lda XgRYUWeaponHi,y
Pointer:
  sta R1
  rts
SophiaMissileTurns: .byte 0,3,6,9
.endproc
.proc SophiaImpact
  lda #10                     ; Five source fast-timer frames, two NES frames each.
  sta RgShotImpact,x
  lda #0
  sta XgShotAim,x
  lda AvAudioRequest
  cmp #19                     ; Preserve source enemy-hit/kill sounds this update.
  bcs Done
  lda #18                     ; AV_SFX_SOPHIABULLETEXPLODE, appended source stream.
  sta AvAudioRequest
Done:
  rts
.endproc
.segment "METASPRITE"
.proc ExpandedDrawShots
  lda MmDeathFlag
  beq :+
    lda SelectedCharacter
    cmp #CHARACTER_BASS
    jne Done
    jmp MegaManDrawDeath
  :
  inc RgDrawFirst
  lda RgDrawFirst
  cmp #10
  bcc :+
    lda #0
    sta RgDrawFirst
  :
  tax
  lda #10
  sta RgDrawRemaining
Loop:
  stx RgSlot
  lda RgShotType,x
  jeq Next
  cmp #9
  bcc NativeShot
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  jne Next
  lda RgShotType,x
  cmp #44
  jcc Next
  cmp #46
  jcs Next
NativeShot:
  cmp #2
  bne :+
    lda RgShotAge,x
    cmp #3
    jcc Next
  :
  farcall ExpandedWeaponPointer
  ldx RgSlot
  lda RgShotX,x
  sec
  sbc ScreenLeft_X_Pos
  sta R4
  lda RgShotPage,x
  sbc ScreenLeft_PageLoc
  sta R5
  lda RgShotY,x
  sta R6
  lda RgShotYHigh,x
  sta R7
  lda #0
  sta R3
  jsr MetaspriteRenderLoop
  lda SelectedCharacter
  cmp #CHARACTER_RYGAR
  bne :+
    jsr Chain
  :
Next:
  dec RgDrawRemaining
  jeq Done
  ldx RgSlot
  inx
  cpx #10
  bcc :+
    ldx #0
  :
  jmp Loop
Done:
  rts
Chain:
  lda XgDiskReach
  sec
  sbc #12
  jcc ChainDone
  cmp #4
  jcc ChainDone
  sta XgChainReach
  ; The original draws one chain sprite, twelve pixels behind disk center.
  lda #1
  sta RgTemp3
  farcall ExpandedChainPointer
Link:
  ldx RgSlot
  lda Player_X_Position
  clc
  adc #8
  sta R4
  lda Player_PageLoc
  adc #0
  sta R5
  lda RgShotDir,x
  cmp #2
  jeq ChainLeft
  lda R4
  clc
  adc XgChainReach
  sta R4
  lda R5
  adc #0
  sta R5
  jmp ChainScreen
ChainLeft:
  clc
  lda R4
  adc #2
  sta R4
  lda R5
  adc #0
  sta R5
  lda R4
  sec
  sbc XgChainReach
  sta R4
  lda R5
  sbc #0
  sta R5
ChainScreen:
  lda R4
  sec
  sbc ScreenLeft_X_Pos
  sta R4
  lda R5
  sbc ScreenLeft_PageLoc
  sta R5
  lda RgShotY,x
  sta R6
  lda RgShotYHigh,x
  sta R7
  lda #0
  sta R3
  jsr MetaspriteRenderLoop
  lda XgChainReach
  sec
  sbc #8
  sta XgChainReach
  jcc ChainDone
  dec RgTemp3
  jeq ChainDone
  cmp #4
  jcs Link
ChainDone:
  rts
.endproc
.popseg
.include "sophia_math.s"
