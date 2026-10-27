; Gradius controller/weapon programs use their original screen coordinates.
; SMB world contact, capsule delivery and level exits are explicit adapters.
VvLife=$5d0c
VvHurt=$5d0d
VvDeathAge=$5d0e
VvClock=$5d0f
VvSlot=$5d10
VvEnemySlot=$5d11
VvSavedObject=$5d12
VvTemp=$5d13
VvTempY=$5d14
VvTempPage=$5d15
VvRectY=$5d16
VvRectX=$5d17
VvRectPage=$5d18
VvDrawFirst=$5d19
VvDrawCount=$5d1a
VvPose=$5d1b
VvKills=$5d1c
VvTemp2=$5d1d
VvNeedEntry=$5d1e
VvCapY=$5d2c
VvCapActive=$5d30
VvCapAge=$5d34
VvCapFraction=$5d38
VvCapX=$5d4c
VvCapPage=$5d6c
.export VvLife,VvHurt,VvClock,VvCapActive,VvCapX,VvCapPage,VvCapY,VvNeedEntry
.pushseg
.segment "VIC_WORLD"
.proc VvIsActive
 lda SelectedCharacter
 cmp #18
 beq Yes
 clc
 rts
Yes:sec
 rts
.endproc
.proc VvEnsure
 lda VvInitialized
 cmp #$76
 bne NewLife
 lda VvLife
 cmp NumberofLives
 beq Entry
 ; A1UP/score bonus must not look like a lost life and erase equipment.
 lda NumberofLives
 cmp VvLife
 bcc NewLife
 sta VvLife
 jmp Entry
NewLife:
.if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5
 jsr PnHudNewLife
.else
 lda #0
 tax
.endif
Clear:sta $5d00,x
 inx
 bne Clear
 lda #$76
 sta VvInitialized
 lda #20
 sta VvAutoFire
 lda #1
 sta VvAlive
 sta VvNeedEntry
 sta VvHudDirty
 lda NumberofLives
 sta VvLife
Entry:
 lda VvNeedEntry
 beq Done
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 clc
 adc #8
 cmp #16
 bcs :+
 lda #16
:sta VvObjX
 lda Player_Y_Position
 sec
 sbc #24
 cmp #193
 bcc :+
 lda #160
:sta VvObjY
 ldy VvVariant
 beq GradiusEntry
 lda #0
 sta VvPrevious
 rts
GradiusEntry:
 lda #1
 sta VvObjAnim
 lda #0
 sta VvNeedEntry
 sta VvPrevious
 ldx #23
Ring:
 lda VvObjX
 sta VvRingX,x
 lda VvObjY
 sta VvRingY,x
 dex
 bpl Ring
Done:rts
.endproc
.proc VvReset
 jsr VvIsActive
 bcc Done
 lda VvVariant
 beq :+
 jsr PnReset
 jmp Cleanup
:
 lda #0
 ldx #11
Clear:
 sta VvObjAnim,x
 sta VvObjTimer,x
 sta VvObjSub,x
 dex
 bpl Clear
 ldx #3
Caps:sta VvCapActive,x
 dex
 bpl Caps
Cleanup:
 lda #0
.if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5
 jsr PnHudCancelLife
.else
 sta InvHudActive
.endif
 sta DisableCollisionDet
 lda #1
 sta VvNeedEntry
 sta VvHudDirty
Done:rts
.endproc
.proc VvMovement
 jsr VvEnsure
 lda Player_X_Position
 sta MmOldX
 lda SavedJoypadBits
 eor VvPrevious
 and SavedJoypadBits
 sta VvFresh
 lda SavedJoypadBits
 sta VvPrevious
 sta VvHeld
 inc VvClock
 lda VvHurt
 beq :+
 dec VvHurt
:
 lda VvVariant
 beq Gradius
 jsr PnMovement
 jmp MotionReady
Gradius:
 farcall VvNativeMotion
 farcall VvBuyUpgrade
MotionReady:
 lda #1
 sta DisableCollisionDet
 sta PlayerSize
 sta Player_Y_HighPos
 sta Player_State
 sta PlayerFacingDir
 lda #0
 sta PlayerStatus
 sta Player_X_Speed
 sta Player_Y_Speed
 sta Player_X_Scroll
 sta Player_XSpeedAbsolute
 sta MmSliding
 sta SmBall
 sta RgCrouch
 sta CrouchingFlag
 sta MmOnVine
 sta MmUnderwater
 sta GuestHurtTicks
 sta GuestHurtKind
 jsr VvExportPosition
 ; The native ship's terrain query uses its own position, not its large art.
 lda Player_X_Position
 clc
 adc #8
 sta VvRectX
 lda Player_PageLoc
 adc #0
 sta VvRectPage
 lda VvObjY
 clc
 adc #32
 jsr VvReadCell
 cmp #$24
 beq Flag
 cmp #$25
 beq Flag
 cmp #$c5
 beq Axe
 cmp #$c2
 beq Coin
 cmp #$c3
 beq Coin
 cmp #$6c
 beq SidePipe
 cmp #$1f
 beq SidePipe
 cmp #$1c
 beq SidePipe
 cmp #$6b
 beq SidePipe
 cmp #$10
 beq PipeTop
 cmp #$11
 beq PipeTop
Solid:
 tay
 lda MTileAttribute,y
 and #MTILE_SOLID
 jeq Done
 .if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
 lda CheatInvincible
 and #1
 beq CheatSolidDeath
 rts
CheatSolidDeath:
 ldx #0
 jmp KillPlayer
 .else
 lda CheatInvincible
 jne Done
 ldx #0
 jmp KillPlayer
 .endif
Flag:
 lda #0
 sta DisableCollisionDet
 jmp FlagpoleCollision
Axe:
 lda #0
 sta DisableCollisionDet
 jmp HandleAxeMetatile
Coin:
 lda #Sfx_CoinGrab
 sta Square2SoundQueue
 jmp HandleCoinMetatile
SidePipe:
 lda #0
 sta DisableCollisionDet
 sta Player_State
 jmp PipeDwnS
PipeTop:
 pha
 lda SavedJoypadBits
 and #Down_Dir
 beq NotEntering
 lda VvRectX
 sec
 sbc #3
 sta VvRectX
 lda VvRectPage
 sbc #0
 sta VvRectPage
 lda VvObjY
 clc
 adc #32
 jsr VvReadCell
 cmp #$10
 bne NotEntering
 lda VvRectX
 clc
 adc #6
 sta VvRectX
 lda VvRectPage
 adc #0
 sta VvRectPage
 lda VvObjY
 clc
 adc #32
 jsr VvReadCell
 cmp #$11
 bne NotEntering
 pla
 lda #0
 sta DisableCollisionDet
 sta Player_State
 lda #$11
 sta R0
 lda #$10
 sta R1
 jmp HandlePipeEntry
NotEntering:
 pla
 jmp Solid
Done:rts
.endproc
.proc VvExportPosition
 lda VvObjX
 sec
 sbc #8
 clc
 adc ScreenLeft_X_Pos
 sta Player_X_Position
 lda ScreenLeft_PageLoc
 adc #0
 sta Player_PageLoc
 lda VvObjY
 clc
 adc #24
 sta Player_Y_Position
 rts
.endproc
.proc VvReadCell
 cmp #32
 bcc Empty
 cmp #240
 bcs Empty
 and #$f0
 sec
 sbc #32
 sta R2
 lda VvRectX
 lsr
 lsr
 lsr
 lsr
 sta VvTemp
 lda VvRectPage
 and #1
 asl
 asl
 asl
 asl
 ora VvTemp
 jsr GetBlockBufferAddr
 ldy R2
 lda (R6),y
 rts
Empty:lda #0
 rts
.endproc
.proc VvScrollGate
 jsr VvIsActive
 bcc Legacy
 lda GameEngineSubroutine
 cmp #5
 beq ExitWalk
 cmp #8
 bne Legacy
 lda MmDeathFlag
 bne Zero
 lda ScrollLock
 bne Zero
 ldy #1
 farcall ScrollScreen
 inc Player_X_Position
 bne Zero
 inc Player_PageLoc
Zero:
 lda #0
 sta Platform_X_Scroll
 sta Player_X_Scroll
 lda ScrollLock
 beq Done
 sta ScrollAmount
 lda #0
 sta ScrollAmount
Done:rts
ExitWalk:
 ; A free-flying ship may grab the pole near the screen's right edge.
 ; Native end walking must have space to leave its base before the original
 ; Y>=174 path releases ScrollLock and queues the level-clear music.
 lda ScrollLock
 pha
 lda #0
 sta ScrollLock
 farcall ScrollHandler
 pla
 sta ScrollLock
 rts
Legacy:farcall ScrollHandler,jmp
.endproc
.proc VvWeapons
 lda VvVariant
 beq :+
 jmp PnWeapons
:
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda MmDeathFlag
 ora TimerControl
 jne Done
 lda ObjectOffset
 sta VvSavedObject
 farcall VvNativeWeapons
 jsr VvSoundEvents
 lda #11
 sta VvSlot
Loop:
 ldx VvSlot
 lda VvObjAnim,x
 beq Next
 lda VvObjX,x
 sec
 sbc #8
 clc
 adc ScreenLeft_X_Pos
 sta VvRectX
 lda ScreenLeft_PageLoc
 adc #0
 sta VvRectPage
 lda VvObjY,x
 clc
 adc #32
 sta VvRectY
 jsr VvShotBlocks
 ldx VvSlot
 lda VvObjAnim,x
 beq Next
 jsr VvShotEnemies
Next:dec VvSlot
 lda VvSlot
 cmp #3
 bcs Loop
 jsr VvCapsules
 lda VvSavedObject
 sta ObjectOffset
Done:rts
.endproc
.proc VvShotBlocks
 lda VvRectX
 sta MmBulletX
 lda VvRectPage
 sta MmBulletPage
 lda VvRectY
 sta MmBulletY
 lda #1
 sta MmBulletDir
 lda #3
 sta MmBulletType
 ldx #0
 stx MmSlot
 farcall MegaManWeapons::Blocks
 lda MmBulletType
 bne Clear
 ldx VvSlot
 lda #0
 sta VvObjAnim,x
Clear:
 lda #0
 sta MmBulletType
 rts
.endproc
.proc VvShotEnemies
 ldx #5
Loop:
 lda Enemy_Flag,x
 jeq Next
 jmi Next
 lda Enemy_State,x
 and #$20
 jne Next
 lda Enemy_ID,x
 cmp #Bowser
 beq Check
 cmp #$15
 jcs Next
 cmp #Podoboo
 jeq Next
Check:
 lda Enemy_X_Position,x
 sec
 sbc VvRectX
 sta R0
 lda Enemy_PageLoc,x
 sbc VvRectPage
 sta R1
 lda R0
 clc
 adc #12
 sta R0
 lda R1
 adc #0
 jne Next
 lda R0
 cmp #25
 jcs Next
 lda Enemy_Y_Position,x
 sec
 sbc VvRectY
 clc
 adc #12
 cmp #25
 jcs Next
 stx VvEnemySlot
 stx ObjectOffset
 lda Enemy_ID,x
 cmp #Bowser
 beq Boss
 jsr VvDropForEnemy
 ldx VvEnemySlot
 jsr ShellOrBlockDefeat
 jmp Consumed
Boss:stx R1
 jsr HandleEnemyFBallCol
Consumed:
 ldx VvSlot
 lda #0
 sta VvObjAnim,x
 rts
Next:dex
 jpl Loop
 rts
.endproc
.proc VvDropForEnemy
 ; SMB acquisition policy: every third ordinary defeated enemy drops a
 ; physical capsule; no native enemy/platform slot is commandeered.
 inc VvKills
 lda VvKills
 cmp #3
 bcc Done
 lda #0
 sta VvKills
 ldy #3
Find:lda VvCapActive,y
 beq Free
 dey
 bpl Find
 rts
Free:
 lda #1
 sta VvCapActive,y
 lda #0
 sta VvCapAge,y
 sta VvCapFraction,y
 lda Enemy_X_Position,x
 sta VvCapX,y
 lda Enemy_PageLoc,x
 sta VvCapPage,y
 lda Enemy_Y_Position,x
 sta VvCapY,y
Done:rts
.endproc
.proc VvCapsules
 lda #3
 sta VvSlot
Loop:
 ldx VvSlot
 lda VvCapActive,x
 beq Next
 inc VvCapAge,x
 ; Original capsules drift half a screen pixel left per active update.
 lda VvCapFraction,x
 sec
 sbc #128
 sta VvCapFraction,x
 lda VvCapX,x
 sbc #0
 sta VvCapX,x
 lda VvCapPage,x
 sbc #0
 sta VvCapPage,x
 lda VvCapX,x
 clc
 adc ScrollAmount
 sta VvCapX,x
 lda VvCapPage,x
 adc #0
 sta VvCapPage,x
 ; Original free capsules leave through the left screen edge.
 lda VvCapX,x
 cmp ScreenLeft_X_Pos
 lda VvCapPage,x
 sbc ScreenLeft_PageLoc
 bmi Erase
 lda Player_X_Position
 sec
 sbc VvCapX,x
 sta R0
 lda Player_PageLoc
 sbc VvCapPage,x
 sta R1
 lda R0
 clc
 adc #12
 sta R0
 lda R1
 adc #0
 bne Next
 lda R0
 cmp #25
 bcs Next
 lda Player_Y_Position
 clc
 adc #8
 sec
 sbc VvCapY,x
 clc
 adc #12
 cmp #25
 bcs Next
 phx
 jsr VvTake
 plx
Erase:lda #0
 sta VvCapActive,x
Next:dec VvSlot
 jpl Loop
 rts
.endproc
.proc VvTake
 lda VvVariant
 beq :+
 jmp PnTake
:
 lda PlayerScoreDisplay+5
 sta VvScoreDigit
 farcall VvTakeCapsule
 jmp VvSoundEvents
.endproc
.proc VvSoundEvents
 lda VvSfxEvent
 beq Bonus
 cmp #14
 bne Pickup
 lda #Sfx_PowerUpGrab
 bne Sound
Pickup:
 cmp #13
 bne Shot
 lda #Sfx_CoinGrab
 bne Sound
Shot:
 lda #Sfx_Fireball
 sta Square1SoundQueue
 lda #0
 sta VvSfxEvent
 jmp Bonus
Sound:sta Square2SoundQueue
 lda #0
 sta VvSfxEvent
Bonus:
 lda VvScoreBonus
 beq Done
 lda #0
 sta VvScoreBonus
 lda #5
 sta DigitModifier+PlayerScoreLastIndex-2
 farcall AddToScore
Done:rts
.endproc
.proc VvBody
 lda VvVariant
 beq :+
 jmp PnBody
:
 lda #0
 sta GuestBodyStompAllowed    ; ship contact always uses shield/injury semantics
 lda #1
 sta GuestBodyNoStomp
 lda VvHurt
 bne Protected
 lda VvShield
 beq Ordinary
 dec VvShield
 lda #1
 sta VvHudDirty
 lda #8
 sta VvHurt
 lda Enemy_ID,x
 cmp #$15
 bcs Protected
 cmp #Podoboo
 beq Protected
 stx ObjectOffset
 jsr ShellOrBlockDefeat
Protected:sec
 rts
Ordinary:clc
 rts
.endproc
.proc VvInjury
 lda VvVariant
 beq :+
 jmp PnInjury
:
 lda VvShield
 beq Fatal
 dec VvShield
 lda #1
 sta VvHudDirty
 lda #8
 sta VvHurt
 lda #4
 sta InjuryTimer
 sec
 rts
Fatal:ldx #0
 jmp KillPlayer
.endproc
.proc VvDeathStart
 lda #0
 sta VvAlive
 sta VvDeathAge
.if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5
 jsr PnHudCancelLife
::VvDeathHudCancelled:
.else
 sta InvHudActive
.endif
 sta DisableCollisionDet
 lda #$ff
 sta VvLife
 lda VvVariant
 beq :+
 jsr PnDeathStart
:
 rts
.endproc
.proc VvDeathUpdate
 lda VvVariant
 beq :+
 jsr PnDeathUpdate
:
 inc VvDeathAge
 lda VvDeathAge
 cmp #120
 bcc Done
 lda #6
 sta GameEngineSubroutine
 lda #0
 sta TimerControl
Done:rts
.endproc
.popseg
