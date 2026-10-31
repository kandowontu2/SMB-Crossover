; PRIVATE raw25 Main bridge. Frozen original-source leaves are included first.
; No NMI/audio scheduler/menu exposure. No new RAM or global admission flag.
.pushseg
.segment "PARODIUS_BELLS"
.export S2MainGame,S2MainPlayer,S2MainBox,S2MainWorld,S2MainPickup,S2MainEnd
.export S2MainInjury,S2MainStatus,S2MainVisible,S2MainDraw,S2MainPlatform
.export S2MainStomp,S2MainPrepare,S2MainScene,S2MainFresh,S2MainUi
.export S2MainBody,S2MainNativeNoop,S2MainMature,S2MainPalette
.export S2MainSpawn,S2MainErase,S2MainImmunity,S2MainCarryPrelude,S2MainGrow,S2MainEndStar
.export S2MainProjectiles
.export S2MainAdder,S2MainBoxProfile
.export S2MainBegin,S2MainEndCode
S2MainBegin:

.proc S2MainGame
 ; Called only AFTER raw25 gate; cold ownership is initialized by Fresh.
 lda GameEngineSubroutine
 cmp #8
 beq Player
 cmp #11
 beq Death
 farcall GameRoutines,jmp       ; genuine SMB entrance/pipe/vine/flag routines.
Player:jmp S2MainPlayer
Death:
 jsr S2DeathUpdate
 jsr GetPlayerOffscreenBits
 jmp RelativePlayerPosition
.endproc

.proc S2MainPlayer
 jsr S2Ensure                 ; own acquisition before any private mask read.
 lda SavedJoypadBits
 and #$c0
 sta A_B_Buttons
 lda SavedJoypadBits
 and #3
 sta Left_Right_Buttons
 lda SavedJoypadBits
 and #12
 sta Up_Down_Buttons
 lda Player_Rel_XPos
 sta Player_Pos_ForScroll       ; native pre-step camera sample, exactly once.
 lda #0
 sta S2HeadY                   ; host-only cache invalid until real up probe.
 lda Player_Y_Position
 pha                           ; actual pre-Main origin; source scratch may change.
 jsr S2MainOwnerMask
 pha
 jsr S2Movement                ; sole source physics/object/control callback.
 bcc PopDone
 pla
 jsr S2MainReleaseCulled       ; real native erase for a source-retired throw.
 jsr S2MainVelocity
 jsr VvScrollBridge            ; resident native camera/clamp, exactly once.
 jsr GetPlayerOffscreenBits
 jsr RelativePlayerPosition
 jsr S2ImportPosition          ; accept actual camera left/right clamp.
 jsr S2MainWorld               ; native rewards/pipes, no native BG integrator.
 pla
 sta S2HeadPage                ; head/coin scratch consumed; priorY for body pass.
 jsr S2MainBox
 lda Player_Y_HighPos
 cmp #2
 bcc Done
 jsr S2DeathStart              ; source death, host life loss remains engine6.
Done:rts
PopDone:pla
 pla
 rts
.endproc

.proc S2MainOwnerMask
 lda #0
 sta R0
 ldx #2
Loop:lda S2ObjectState,x
 beq Next
 ldy S2ObjectHost0,x
 cpy #6
 bcs Next
 lda Bits,y
 ora R0
 sta R0
Next:dex
 bpl Loop
 lda R0
 rts
Bits:.byte 1,2,4,8,16,32
.endproc
.proc S2MainReleaseCulled
 sta R1
 jsr S2MainOwnerMask
 eor #$ff
 and R1
 sta R1
 ldx #5
Loop:lda S2MainOwnerMask::Bits,x
 and R1
 beq Next
 jsr EraseEnemyObject
Next:dex
 bpl Loop
 rts
.endproc

.proc S2MainVelocity
 ; Source signed Q4 VY remains untouched. Native SMB consumers use integer
 ; speed/sign. A positive fractional fall must still be a descending contact.
 lda S2VY
 beq Store
 bmi Negative
 clc
 adc #15
 .repeat 4
 lsr
 .endrepeat
 bne Store
Negative:
 lda S2VY
 .repeat 4
 cmp #$80
 ror
 .endrepeat
Store:sta Player_Y_Speed
 rts
.endproc

.proc S2MainBox
 ; Original source rectangle is exclusive right/bottom. SMB's collision
 ; loop compares inclusive endpoints, so publish right12/bottom32.
 lda Player_Rel_XPos
 clc
 adc #2
 sta BoundingBox_UL_XPos
 lda Player_Rel_XPos
 clc
 adc #12
 sta BoundingBox_LR_Corner
 lda #11
 ldy S2Duck
 beq :+
 lda #16
:clc
 adc Player_Y_Position
 sta BoundingBox_UL_YPos
 lda Player_Y_Position
 clc
 adc #32
 sta BoundingBox_LR_Corner+1
 ldx #0
 ldy #0
 rts
.endproc

.proc S2MainCell
 ; R4 worldX,R5 page,R6 screenY -> genuine native block pointer R6/7,
 ; R2 row, A tile. Main scratch only. Bounds checked BEFORE any indirect read.
 lda R6
 cmp #32
 bcc Empty
 cmp #240
 bcs Empty
 and #$f0
 sec
 sbc #32
 sta R2
 lda R5
 and #1
 .repeat 4
 asl
 .endrepeat
 sta R0
 lda R4
 .repeat 4
 lsr
 .endrepeat
 ora R0
 jsr GetBlockBufferAddr
 ldy R2
 lda (R6),y
 rts
Empty:lda #0
 rts
.endproc

.proc S2MainWorld
 ; Resolve source-detected head transaction once, retaining the real native
 ; brick/question/coin writer and actor producer. Never repeat BG physics.
 lda S2HeadY
 beq Coins
 lda AreaType
 beq Coins
 lda BlockBounceTimer
 bne Coins
 lda S2HeadY
 sta R6
 lda S2HeadX
 sta R4
 lda S2HeadPage
 sta R5
 jsr S2MainCell
 beq Coins
 tay
 lda MTileAttribute,y
 and #MTILE_BUMP|MTILE_CLIMB
 bne Coins
 tya
 jsr PlayerHeadCollision
 jsr S2MainVelocity            ; real bump does not replace source Q4 motion.
Coins:
 lda S2YPage
 jne Done
 lda #0
 sta S2HeadPage                ; head cache consumed; reuse host-only scratch.
CoinLoop:
 ldx S2HeadPage
 lda CoinY,x
 clc
 adc S2Y
 sta R6
 lda CoinX,x
 clc
 adc S2X
 sta R4
 lda S2Page
 adc #0
 sta R5
 jsr S2MainCell
 jsr CheckForCoinMTiles
 bcc Next
 jsr HandleCoinMetatile        ; actual erase, visible queue, coins/life writer.
 jmp Pipe                     ; source adapter awards at most one per Main.
Next:inc S2HeadPage
 lda S2HeadPage
 cmp #9
 bcc CoinLoop
Pipe:
 lda S2Air
 bne Done
 lda S2Held
 and #4
 beq Done
 lda S2X
 clc
 adc #3
 sta R4
 lda S2Page
 adc #0
 sta R5
 lda S2Y
 clc
 adc #32
 sta R6
 jsr S2MainCell
 pha
 lda S2X
 clc
 adc #12
 sta R4
 lda S2Page
 adc #0
 sta R5
 lda S2Y
 clc
 adc #32
 sta R6
 jsr S2MainCell
 sta R0                       ; native right11,left10 pipe pair.
 pla
 sta R1
 jsr HandlePipeEntry
Done:rts
CoinX:.byte 2,7,12,2,7,12,2,7,12
CoinY:.byte 11,11,11,22,22,22,32,32,32
.endproc

.proc S2MainPickup
 ; Actual physically admitted collector supplies X, no rewards are seeded.
 phx
 jsr S2Pickup
 plx
 bcc Native
 phx
 jsr EraseEnemyObject
 plx
 lda #Sfx_PowerUpGrab
 sta Square2SoundQueue
 lda #6
 jmp SetupFloateyNumber
Native:farcall MarioSourcePowerupCollision,jmp
.endproc

.proc S2MainPrepare
 lda SelectedCharacter
 sta InvPickupOwner,x
 lda #$fc
 sta InvPickup,x
 lda #0
 sta InvRisePhase,x
 sta InvPickupSaveLo,x
 sta InvPickupSaveHi,x
 rts
.endproc

.proc S2MainScene
 jsr S2Ensure
 jsr S2ImportPosition
 rts
.endproc
.proc S2MainFresh
 jmp S2ColdInit                ; before first Ensure/Ready read, at real newgame.
.endproc
.proc S2MainUi
 ; Shared native status fields stay, no legacy inventory row indexed by25.
 lda #0
 sta InvHudActive
 sta InvFresh
 rts
.endproc
.proc S2MainNativeNoop
 clc
 rts
.endproc
.proc S2MainMature
 lda PowerUpType,x
 cmp #2
 bcs Yes
 lda Enemy_State,x
 bpl No
Yes:sec
 rts
No:clc
 rts
.endproc
.proc S2MainAdder
 cmp #25
 beq Own
 farcall RlAdderDispatch,jmp
Own:jmp S2Adder
.endproc
.proc S2MainBoxProfile
 cmp #25
 beq Own
 farcall RlBoxDispatch,jmp
Own:jmp S2Box
.endproc

.proc S2MainBody
 ; Real PlayerCollisionCore has ALREADY admitted this actor overlap.
 ; No coordinate heuristic invents contact. X remains the actual actor.
 phy
 lda AreaType
 sta GuestBodyStompAllowed
 lda CrossoverBehaviorVersion
 sta GuestBodyNoStomp
 beq Ordinary
 lda S2VY
 bmi Ordinary
 cpx #6
 bcs Ordinary
 lda Enemy_Flag,x
 beq Ordinary
 bmi Ordinary
 lda Enemy_State,x
 bne Ordinary
 lda Enemy_ID,x
 cmp #6
 beq Walker
 cmp #2
 bcs Ordinary
Walker:
 txa
 pha
 asl
 asl
 clc
 adc #5                       ; native enemy bbox top:4*(slot+1)+1.
 tay
 lda S2HeadPage               ; actual pre-Main origin, after head/coin consumption.
 clc
 adc #32                      ; inclusive native leading-foot contact plane.
 bcs NoTop
 cmp BoundingBox_UL_Corner,y
 bcc Top
 bne NoTop
Top:
 lda BoundingBox_UL_Corner,y
 sec
 sbc #32
 sta Player_Y_Position
 lda #1
 sbc #0
 sta Player_Y_HighPos
 pla
 tax
 ; Re-lifting a still-live old throw transfers its private ownership. Never
 ; allocate a second record for the same actual native actor.
 lda S2Fresh
 and #$40
 beq Stand
 lda S2State
 ora S2Holding
 ora S2Duck
 bne Stand
 jsr S2EnemyControl
 bcc Stand
 phx
 tya
 tax
 jsr S2ClearObject
 plx
Stand:
 jsr S2StandOnActor
 ply
 sec
 rts
NoTop:pla
 tax
Ordinary:ply
 clc
 rts
.endproc

.proc S2MainInjury
 lda Enemy_Rel_XPos            ; real ForceInjury caller leaves A=raw ownerID.
 jsr S2InjuryStart
 sec                          ; protection is also handled; no vanilla shrink.
 rts
.endproc
.proc S2MainStatus
 lda #1                       ; source HP, not PlayerStatus, owns death choice.
 tax
 rts
.endproc
.proc S2MainVisible
 lda S2Hurt
 beq Show
 lda S2Clock
 and #8
 bne Hide
Show:sec
 rts
Hide:clc
 rts
.endproc

.proc S2MainStomp
 ; Only after a real successful Easy native stomp; import its genuine impulse.
 jsr S2ActorEpochChanged       ; native stomp now owns this actor's state/AI.
 lda Player_Y_Speed
 .repeat 4
 asl
 .endrepeat
 sta S2VY
 lda #0
 sta S2AY
 sta S2YF
 lda #1
 sta S2Air
 sta Player_State
 rts
.endproc

.proc S2MainPlatform
 ; A is the real platform top from PositionPlayerOnVPlat's actual owner.
 ; X is its native actor. Source inclusive foot is origin+32.
 pha
 lda GameEngineSubroutine
 cmp #11
 beq Skip
 lda Enemy_Y_HighPos,x
 cmp #1
 bne Skip
 pla
 sec
 sbc #32
 sta Player_Y_Position
 lda Enemy_Y_HighPos,x
 sbc #0
 sta Player_Y_HighPos
 jsr S2ImportPosition
 lda #0
 sta S2VY
 sta S2AY
 sta S2YF
 sta S2Air
 sta Player_Y_Speed
 sta Player_Y_MoveForce
 sta Player_State
 rts
Skip:pla
 rts
.endproc

.proc S2MainDraw
 ; NrDraw is the PRE-body projectile pass. Do not render body twice or let
 ; vegetable pose overwrite its cached descriptor/reservation.
 lda SmPosePtr
 pha
 lda SmPosePtr+1
 pha
 lda SmChrBank
 pha
 jsr S2DrawObjects
 pla
 sta SmChrBank
 pla
 sta SmPosePtr+1
 pla
 sta SmPosePtr
 rts
.endproc

.proc S2MainEnd
 ; Called at the one GameCore palette tail AFTER world/render work. The
 ; NMI source clock is independent and deliberately NOT advanced here.
 farcall ResetPalStar
 jmp S2HudLate
.endproc
.proc S2MainEndStar
 farcall CyclePlayerPalettePreload
 jmp S2HudLate
.endproc
.proc S2MainEndTimers
 lda GameEngineSubroutine
 cmp #11
 beq Active
 lda TimerControl
 bne Done
Active:jsr S2MainPalette
 jmp S2EndFrame
Done:rts
.endproc

.proc S2MainPalette
OwnStart:
 ; Publish sourceP0's three non-universal colors only. Original source eye
 ; roleP1 is returned by the frozen C80 endpoint, NOT stolen from enemies.
 ; Complete eye-role hardware composition remains explicit host work.
 lda StarInvincibleTimer
 ora VRAM_Buffer_AddrCtrl       ; ROM palette service must precede acknowledgment.
 bne Done
 lda S2NativeCharacter
 cmp S2PaletteAck
 beq Done
 jsr S2PalettePointer
 ldx VRAM_Buffer1_Offset
 cpx #77
 bcs Done
 jsr S2NativePaletteHeader
Loop:lda (R0),y
 sta VRAM_Buffer1+3,x
 inx
 iny
 cpy #4
 bne Loop
 txa
 clc
 adc #3
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 lda S2NativeCharacter
 sta S2PaletteAck              ; acknowledge only a successful complete packet.
Done:rts
 .res 14,$ea
 .assert *-OwnStart=74,error,"Existing source palette public envelope"
.endproc

.proc S2MainSpawn
 php
 pha
 phy
 jsr S2ActorEpochChanged
 ply
 pla
 plp
 farcall CrossoverLevelEnemyInit,jmp
.endproc
.proc S2MainErase
 ; Exact native Ryu erase body follows owner-specific epoch invalidation.
 php
 pha
 phy
 jsr S2ActorEpochChanged
 ply
 pla
 plp
 sta MmEnemyFlash,x
 php
 inx
 cpx RyPlatformSlot
 bne Done
 sta RyPlatformSlot
 sta RyPlatformCancel
 sta XgWall
 inc XgJumpUsed
Done:dex
 plp
 rts
.endproc
.proc S2MainImmunity
 phy
 jsr S2EnemyControl
 bcc No
 lda S2ObjectProjectile,y
 cmp #32
 bcs No
 ply
 sec                          ; original held/self and post-throw grace.
 rts
No:ply
 clc
 rts
.endproc
.proc S2MainCarryPrelude
 ; Original RunNormalEnemies prefix has not run. Native attrs remain exact.
 lda #0
 sta Enemy_SprAttrib,x
 lda Enemy_State,x
 beq Control
 phy
 jsr S2ActorEpochChanged       ; real battle/reset writer now owns native state.
 ply
 clc
 rts
Control:
 phy
 jsr S2EnemyControl
 ply
 bcc Done                     ; ordinary actor resumes the untouched native path.
 farcall NormalEnemyOffscreenBits
 jsr RelativeEnemyPosition
 farcall EnemyGraphicsEngine
 farcall NormalEnemyBoundBox
 sec                          ; source owns carried/thrown terrain/physics.
Done:rts
.endproc
.proc S2MainGrow
 ; Source-derived outline of the actual52-byte A0 rise body. Every exit
 ; tail-farcalls its genuine A0 consumer; no raw cross-window JMP.
 farcall LmRiseGate
 bcs Draw
 lda FrameCounter
 and #3
 bne Check
 dec Enemy_Y_Position,x
 lda Enemy_State,x
 inc Enemy_State,x
 cmp #$11
 bcc Check
 lda #$10
 sta Enemy_X_Speed,x
 lda #$80
 sta Enemy_State,x
 asl
 sta Enemy_SprAttrib,x
 rol
 sta Enemy_MovingDir,x
Check:farcall ChkPUSte,jmp
Draw:farcall RunPUSubs,jmp
.endproc

.proc S2MainProjectiles
 ; Borrow/restore the actual four-byte native fireball collision rectangle.
 ; Source kinematics run once in Movement; this is only the host contact
 ; consumer. A real native rectangle test precedes every defeat/score write.
 lda TimerControl
 ora GamePauseStatus
 jne Done
 ldx #3
Save:lda BoundingBox_UL_Corner+28,x
 pha
 dex
 bpl Save
 ldx #2
Object:
 stx S2Source12
 lda S2ObjectState,x
 jeq NextObject
 lda S2ObjectProjectile,x
 jeq NextObject
 lda S2YPage+1,x
 jne NextObject
 lda S2X+1,x
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda S2Page+1,x
 sbc ScreenLeft_PageLoc
 jne NextObject
 lda R4
 cmp #240
 jcs NextObject               ; same fully-visible admission as native shots.
 ldy S2ObjectHitbox,x
 lda R4
 clc
 adc HitLeft,y
 sta BoundingBox_UL_Corner+28
 clc
 adc HitWidth,y
 sec
 sbc #1
 sta BoundingBox_UL_Corner+30
 lda S2Y+1,x
 clc
 adc HitTop,y
 sta BoundingBox_UL_Corner+29
 clc
 adc HitHeight,y
 sec
 sbc #1
 sta BoundingBox_UL_Corner+31
 ldx #5
Enemy:
 lda Enemy_Flag,x
 beq NextEnemy
 bmi NextEnemy
 lda Enemy_State,x
 and #$20
 bne NextEnemy
 lda Enemy_ID,x
 cmp #$15
 bcs NextEnemy
 cmp #Podoboo
 beq NextEnemy
 jsr S2EnemyControl
 bcs NextEnemy                ; held/other owned throws are not enemy targets.
 jsr GetEnemyOffscreenBits
 jsr RelativeEnemyPosition
 phx
 farcall GetEnemyBoundBox
 plx
 lda EnemyOffscrBitsMasked,x
 bne NextEnemy
 jsr GetEnemyBoundBoxOfs
 phx
 ldx #28
 jsr SprObjectCollisionCore
 plx
 bcc NextEnemy
 phx
 ldx S2Source12
 jsr S2ObjectHit               ; clears ONLY after actual accepted overlap.
 cmp #6
 bcs Vegetable
 tax
 jsr EraseEnemyObject          ; carried actor's genuine native epoch ends.
Vegetable:
 plx
 jsr ShellOrBlockDefeat        ; actual native drop/damage/score/SFX authority.
 jmp NextObject
NextEnemy:dex
 bpl Enemy
NextObject:
 ldx S2Source12
 dex
 jpl Object
 ldx #0
Restore:pla
 sta BoundingBox_UL_Corner+28,x
 inx
 cpx #4
 bcc Restore
Done:rts
 ; Exact originalF099/F0AD/F0C1/F0D5 fields0..3. Active records use0/2.
HitLeft:.byte 2,2,3,0
HitTop:.byte 11,16,3,0
HitWidth:.byte 11,11,9,16
HitHeight:.byte 22,17,13,16
.endproc
S2MainEndCode:
.assert S2MainEndCode<=$c000,lderror,"SMB2 Main needs reviewed additional CORE capacity"
.popseg
