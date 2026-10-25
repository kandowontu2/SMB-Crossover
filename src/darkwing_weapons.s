; Original Duck USA bank6 $8385..$86a1. Gas uses source Q8.8 motion,
; authored sprites, source simultaneous caps/costs. SMB enemy HP uses the
; installed 25-units-per-source-hit convention; terrain stays native SMB.
.pushseg
.segment "DARKWING_CORE"
.proc DwScroogeWeapons
  lda DarkwingVariant
  bne Duck
  farcall ScroogeWeapons,jmp
Duck:
  lda SavedJoypadBits
  sta RgPreviousButtons
  lda TimerControl
  jne Done
  lda GameEngineSubroutine
  cmp #8
  jne Clear
  lda RgShootPose
  beq :+
  dec RgShootPose
:
  ldx #5
Timers:
  lda MmEnemyFlash,x
  beq :+
  dec MmEnemyFlash,x
:
  lda RgEnemyStun,x
  beq :+
  dec RgEnemyStun,x
:
  dex
  bpl Timers
  lda ScFresh
  and #Select_Button
  beq Fire
  lda DwAdaptor
  beq Fire
  lda DwMode
  eor #1
  sta DwMode
Fire:
  lda RgBillBurstDelay
  jne Shots
  lda ScFresh
  and #B_Button
  beq Shots
  jsr DwLaunch
Shots:
  ldx #9
Loop:
  stx RgSlot
  lda RgShotType,x
  beq Next
  jsr DwUpdateShot
Next:
  ldx RgSlot
  dex
  bpl Loop
Done:
  rts
Clear:
  ldx #9
:
  stx RgSlot
  jsr DwEraseShot
  dex
  bpl :-
  rts
.endproc
.proc DwLaunch
  lda #0
  sta RgTemp
  lda DwMode
  and #1
  beq Kind
  lda DwAdaptor
  sta RgTemp
Kind:
  ldy RgTemp
  lda DwGas
  cmp Cost,y
  jcc Done
  lda #0
  sta RgTemp2
  ldx #9
Count:
  lda RgShotType,x
  beq CountNext
  cmp #8
  beq ChargingKind
  tay
  lda Kinds,y
  jmp CompareKind
ChargingKind:
  lda RgShotImpact,x
CompareKind:
  cmp RgTemp
  bne CountNext
  inc RgTemp2
CountNext:
  dex
  bpl Count
  ldy RgTemp
  lda RgTemp2
  cmp Cap,y
  bcs Done
  jsr DwFreeShot
  bcc Done
  lda DwGas
  sec
  sbc Cost,y
  sta DwGas
  jsr DwShotInit
  lda RgTemp
  sta RgShotImpact,x
  beq Basic
  cmp #1
  beq Heavy
  lda #8
  sta RgShotType,x
  lda #$14
  sta XgShotAim,x
  jmp Sound
Basic:
  lda #1
  sta RgShotType,x
  lda #$13
  sta XgShotAim,x
  lda #4
  sta RgShotVXHi,x
  jsr DwFaceVX
  jmp Sound
Heavy:
  lda #3
  sta RgShotType,x
  lda #$16
  sta XgShotAim,x
  lda #$80
  sta RgShotVXLo,x
  lda #$fd
  sta RgShotVYHi,x
  jsr DwFaceVX
Sound:
  lda #16
  sta RgShootPose
  lda #Sfx_Fireball
  sta Square1SoundQueue
Done:
  rts
Cost:.byte 0,2,3,2
Cap:.byte 3,1,2,1
Kinds:.byte $ff,0,$ff,1,1,2,2,3,$ff
.endproc
.proc DwFreeShot
  ldx #9
Loop:
  lda RgShotType,x
  beq Found
  dex
  bpl Loop
  clc
  rts
Found:
  sec
  rts
.endproc
.proc DwShotInit
  lda #0
  sta RgShotAge,x
  sta RgShotHits,x
  sta RgShotHitsNow,x
  sta RgShotFracX,x
  sta RgShotFracY,x
  sta RgShotVXLo,x
  sta RgShotVXHi,x
  sta RgShotVYLo,x
  sta RgShotVYHi,x
  sta SsMode,x
  lda PlayerFacingDir
  sta RgShotDir,x
  lda #23
  ldy RgTemp
  cpy #2
  bcc :+
  lda #30
:
  ldy PlayerFacingDir
  cpy #2
  bne :+
  eor #$ff
  clc
  adc #17                     ; center+8 minus15/22
:
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
  lda #17
  ldy Player_State
  beq Ground
  lda #20
  bne SetY
Ground:
  ldy RgCrouch
  beq SetY
  lda #28
SetY:
  clc
  adc Player_Y_Position
  sta RgShotY,x
  lda Player_Y_HighPos
  adc #0
  sta RgShotYHigh,x
  rts
.endproc
.proc DwFaceVX
  lda RgShotDir,x
  cmp #2
  bne Done
  lda #0
  sec
  sbc RgShotVXLo,x
  sta RgShotVXLo,x
  lda #0
  sbc RgShotVXHi,x
  sta RgShotVXHi,x
Done:
  rts
.endproc
.proc DwUpdateShot
  lda RgShotType,x
  cmp #6
  jeq DwArrowActor
  inc RgShotAge,x
  lda RgShotType,x
  cmp #8
  jeq Charge
  cmp #2
  jeq Impact
  lda RgShotAge,x
  cmp #180
  jcs DwEraseShot
  clc
  lda RgShotFracX,x
  adc RgShotVXLo,x
  sta RgShotFracX,x
  lda RgShotX,x
  adc RgShotVXHi,x
  sta RgShotX,x
  lda RgShotVXHi,x
  bmi :+
  lda #0
  bpl :++
:
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
  lda RgShotVYHi,x
  bmi :+
  lda #0
  bpl :++
:
  lda #$ff
:
  adc RgShotYHigh,x
  sta RgShotYHigh,x
  cmp #1
  jne DwEraseShot
  lda RgShotY,x
  cmp #240
  jcs DwEraseShot
  lda RgShotType,x
  cmp #3
  bne Map
  clc
  lda RgShotVYLo,x
  adc #$40
  sta RgShotVYLo,x
  lda RgShotVYHi,x
  adc #0
  sta RgShotVYHi,x
Map:
  lda RgShotX,x
  sta RgTempX
  lda RgShotPage,x
  sta RgTempPage
  lda RgShotY,x
  sta RgTempY
  lda RgShotType,x
  cmp #5
  bne Probe
  lda #12                      ; originalED19 probes24..26/27..29:±12
  ldy RgShotDir,x
  cpy #1
  beq ArrowProbe
  lda #$f4
ArrowProbe:
  ldy #0
  cmp #$80
  bcc :+
  dey
:
  clc
  adc RgTempX
  sta RgTempX
  tya
  adc RgTempPage
  sta RgTempPage
Probe:
  farcall ExpandedMapCell
  ldx RgSlot
  bcc Enemy
  lda RgShotType,x
  cmp #3
  jeq DwHeavyBurst
  cmp #5
  jeq DwAttachArrow
  cmp #4
  beq Enemy                    ; shockwave remains on source ground
  jmp DwEraseShot
Enemy:
  jmp DwShotEnemies
Impact:
  lda RgShotAge,x
  cmp #15
  jcs DwEraseShot
  rts
Charge:
  lda RgShotAge,x
  cmp #12                      ; authored explosion phases0..3, delay2+1
  jcc Done
  lda RgShotImpact,x
  cmp #2
  bne Thunder
  lda #5
  sta RgShotType,x
  lda #$17
  sta XgShotAim,x
  lda #$99
  sta RgShotVXLo,x
  lda #3
  sta RgShotVXHi,x
  jmp Released
Thunder:
  jsr DwFreeShot
  bcc Done
  stx RgTemp2
  ldy RgSlot
  lda #7
  sta RgShotType,x
  sta RgShotType,y
  lda #$1a
  sta XgShotAim,x
  lda #$19
  sta XgShotAim,y
  lda RgShotX,y
  sta RgShotX,x
  lda RgShotPage,y
  sta RgShotPage,x
  lda RgShotY,y
  sta RgShotY,x
  lda RgShotYHigh,y
  sta RgShotYHigh,x
  lda RgShotDir,y
  sta RgShotDir,x
  lda #3
  sta RgShotImpact,x
  lda #0
  sta RgShotAge,x
  sta RgShotHits,x
  sta RgShotFracX,x
  sta RgShotFracY,x
  lda #$2e
  sta RgShotVXLo,x
  sta RgShotVXLo,y
  sta RgShotVYLo,x
  lda #3
  sta RgShotVXHi,x
  sta RgShotVXHi,y
  sta RgShotVYHi,x
  lda #$d2
  sta RgShotVYLo,y
  lda #$fc
  sta RgShotVYHi,y
  jsr DwFaceVX
  ldx RgSlot
Released:
  lda #0
  sta RgShotAge,x
  jmp DwFaceVX
Done:
  ldx RgSlot
  rts
.endproc
.proc DwShotEnemies
  lda RgShotX,x
  sta MmBulletX
  lda RgShotPage,x
  sta MmBulletPage
  lda RgShotY,x
  sta MmBulletY
  lda RgShotDir,x
  sta MmBulletDir
  lda #1
  ldy RgShotType,x
  cpy #4
  bne :+
  lda #2
:
  cpy #5
  bne :+
  lda #3
:
  sta MmBulletType
  lda #0
  sta MmSlot
  tax
  farcall MegaManWeapons::Enemies
  ldx RgSlot
  lda RgShotType,x
  cmp #4
  bcs Done
  lda MmBulletType
  jeq DwEraseShot
Done:
  rts
.endproc
.proc DwExpandedEnemyHit
  lda SelectedCharacter
  cmp #CHARACTER_SCROOGE
  bne Legacy
  lda DarkwingVariant
  beq Legacy
  lda Bits,x
  ldy RgSlot
  and RgShotHits,y
  bne Skip
  lda Bits,x
  ora RgShotHits,y
  sta RgShotHits,y
  lda #15
  sta RgEnemyStun,x
  clc
  rts
Skip:
  sec
  rts
Legacy:
  farcall ExpandedEnemyHit,jmp
Bits:.byte 1,2,4,8,16,32
.endproc
.proc DwHeavyBurst
  lda #2
  sta RgShotType,x
  lda #$14
  sta XgShotAim,x
  lda #0
  sta RgShotAge,x
  lda RgShotY,x
  and #$f0
  sec
  sbc #1
  sta RgShotY,x
  lda #1
  sta RgTemp3
Spawn:
  jsr DwFreeShot
  bcc Done
  ldy RgSlot
  lda RgShotX,y
  sta RgShotX,x
  lda RgShotPage,y
  sta RgShotPage,x
  lda RgShotY,y
  sta RgShotY,x
  lda #1
  sta RgShotYHigh,x
  sta RgShotImpact,x
  lda #4
  sta RgShotType,x
  lda #$18
  sta XgShotAim,x
  lda RgTemp3
  sta RgShotDir,x
  lda #0
  sta RgShotHits,x
  sta RgShotAge,x
  sta RgShotFracX,x
  sta RgShotFracY,x
  sta RgShotVXLo,x
  sta RgShotVYLo,x
  sta RgShotVYHi,x
  lda #6
  sta RgShotVXHi,x
  jsr DwFaceVX
  inc RgTemp3
  lda RgTemp3
  cmp #3
  bcc Spawn
Done:
  ldx RgSlot
  rts
.endproc
.proc DwEraseShot
  lda RgShotType,x
  cmp #6
  bne Clear
  jsr DwValidateArrow
  bcc Clear
  lda #0
  sta Enemy_Flag,y
  sta EnemyMetasprite,y
Clear:
  lda #0
  sta RgShotType,x
  rts
.endproc

; A native vertical-lift actor supplies collision and player carry. State20
; tags ONLY ID26; helper25/28 tags40/60 are unrelated. No occupied slot is
; replaced. A wall arrow waits (and pauses its lifetime) until a slot is free.
.proc DwAttachArrow
  ; OriginalED85/ED9D resolve the leading±12px probe to a16px tile face.
  lda RgTempX
  and #$f0
  sta RgTempX
  lda RgShotDir,x
  cmp #2
  beq Left
  lda RgTempX
  sec
  sbc #12
  sta RgShotX,x
  lda RgTempPage
  sbc #0
  sta RgShotPage,x
  jmp Ready
Left:
  lda RgTempX
  clc
  adc #28
  sta RgShotX,x
  lda RgTempPage
  adc #0
  sta RgShotPage,x
Ready:
  lda #6
  sta RgShotType,x
  lda #0
  sta RgShotImpact,x
  sta SsMode,x
  lda #255
  sta RgShotAge,x
  jmp DwArrowActor
.endproc
.proc DwValidateArrow
  lda RgShotImpact,x
  beq No
  tay
  dey
  lda Enemy_Flag,y
  cmp #1
  bne No
  lda Enemy_ID,y
  cmp #$26
  bne No
  lda Enemy_State,y
  and #$7f
  sta R0
  txa
  ora #$20
  cmp R0
  bne No
  sec
  rts
No:
  clc
  rts
.endproc
.proc DwArrowActor
  jsr DwValidateArrow
  bcs Owned
  lda RgShotImpact,x
  jne DwEraseShot::Clear
  ldy #5
Find:
  lda Enemy_Flag,y
  beq Create
  dey
  bpl Find
  rts
Create:
  lda #1
  sta Enemy_Flag,y
  sta Enemy_Y_HighPos,y
  lda #$26
  sta Enemy_ID,y
  txa
  ora #$20
  sta Enemy_State,y
  lda #4
  sta Enemy_BoundBoxCtrl,y
  lda #$ff
  sta PlatformCollisionFlag,y
  lda RgShotX,x
  sec
  sbc #12
  sta Enemy_X_Position,y
  lda RgShotPage,x
  sbc #0
  sta Enemy_PageLoc,y
  lda RgShotY,x
  sta Enemy_Y_Position,y
  lda #0
  sta Enemy_YMoveForceFractional,y
  sta Enemy_Y_MoveForce,y
  sta Enemy_Y_Speed,y
  tya
  clc
  adc #1
  sta RgShotImpact,x
Owned:
  lda Enemy_State,y
  bpl CollisionReady
  lda MmVY+2
  bpl RestoreCollision
  lda Player_Y_Position
  clc
  adc #32
  cmp Enemy_Y_Position,y
  bcs CollisionReady
RestoreCollision:
  lda Enemy_State,y
  and #$7f
  sta Enemy_State,y
CollisionReady:
  lda SsMode,x
  bne Fall
  lda RgShotAge,x
  beq StartFall
  dec RgShotAge,x
  lda RgShotAge,x
  cmp #120
  bne Support
  lda #$29
  sta XgShotAim,x
Support:
  lda PlatformCollisionFlag,y
  bmi Done
StartFall:
  lda #1
  sta SsMode,x
  lda #$ff
  sta RgShotVYLo,x
  sta RgShotVYHi,x
Fall:
  lda RgShotVYHi,x
  bmi Move
  lda RgShotX,x
  sta RgTempX
  lda RgShotPage,x
  sta RgTempPage
  lda Enemy_Y_Position,y
  clc
  adc RgShotVYHi,x
  adc #1
  sta RgTempY
  farcall ExpandedMapCell
  ldx RgSlot
  php
  jsr DwValidateArrow
  plp
  bcc Move
  ; Let the source arrow fall through scenery without dragging a native
  ; rider through a solid floor after that frame's terrain resolution.
  lda Enemy_State,y
  ora #$80
  sta Enemy_State,y
Move:
  lda RgShotVYLo,x
  sta Enemy_Y_MoveForce,y
  lda RgShotVYHi,x
  sta Enemy_Y_Speed,y
  clc
  lda RgShotVYLo,x
  adc #$40
  sta RgShotVYLo,x
  lda RgShotVYHi,x
  adc #0
  cmp #8
  bcc :+
  lda #8
:
  sta RgShotVYHi,x
  lda Enemy_Y_Position,y
  cmp #232
  bcc Done
  jmp DwEraseShot
Done:
  rts
.endproc

.proc DwDrawShots
  lda DarkwingVariant
  bne Duck
  farcall RosterDrawShots,jmp
Duck:
  jsr DwPublishBody
  lda #<DW_WEAPON_CHR
  ldx #>DW_WEAPON_CHR
  farcall X5SetSpecialChr
  lda #<(DW_WEAPON_CHR+1)
  ldx #>(DW_WEAPON_CHR+1)
  ldy #5
  farcall X5SetPhysicalChr
  BankPRGC #.bank(DarkwingArtBegin)
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
  beq Next
  cmp #6
  bne Sprite
  jsr DwValidateArrow
  bcc Sprite
  lda Enemy_Y_Position,y
  sta RgShotY,x
  lda #0
  sta EnemyMetasprite,y
Sprite:
  lda XgShotAim,x
  jsr DwWeaponPointer
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
  farcall MetaspriteRenderLoop
Next:
  dec RgDrawRemaining
  beq Pickups
  ldx RgSlot
  inx
  cpx #10
  bcc :+
  ldx #0
:
  jmp Loop
Pickups:
  jmp DwDrawPickups
.endproc
.proc DwWeaponPointer
  tay
  lda RgShotAge,x
  cmp #128
  bcc :+
  lda #0                      ; attached lifetime is not an animation age
:
  sta RgTemp
  lda DwAnimationDelay,y
  clc
  adc #1
  sta RgTemp2
  lda #0
  sta RgTemp3
Divide:
  lda RgTemp
  cmp RgTemp2
  bcc Modulo
  sec
  sbc RgTemp2
  sta RgTemp
  inc RgTemp3
  bne Divide
Modulo:
  lda DwAnimationLast,y
  clc
  adc #1
  sta RgTemp2
  lda RgTemp3
Reduce:
  cmp RgTemp2
  bcc Phase
  sec
  sbc RgTemp2
  jmp Reduce
Phase:
  clc
  adc DwWeaponBase,y
  tay
  lda RgShotDir,x
  cmp #2
  beq Left
  lda DwWeaponRLo,y
  sta R0
  lda DwWeaponRHi,y
  sta R1
  rts
Left:
  lda DwWeaponLLo,y
  sta R0
  lda DwWeaponLHi,y
  sta R1
  rts
.endproc
.popseg
