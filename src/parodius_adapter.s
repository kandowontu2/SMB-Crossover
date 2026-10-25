; Owns Vic's inactive actor/history storage while a Parodius alternate plays.
; No new cartridge WRAM. Native physics/gear/weapons remain the source program.
PnCapX=$5db9
PnCapY=$5dbd
PnCapPage=$5dc1
PnCapAge=$5dc5
PnCapActive=$5dc9
PnCapFraction=$5dcd
PnPool=$5dd1
PnInitialized=$5dd2
PnReturn=$5dd3
PnDrawFrame=$5dd4
PnProjectile=$5dd5
PnAutoFireAge=$5dd6
PnMissing=$5dd9
; Padding between the native28-byte arrays is not touched by native actor
; reset/!? routines. Punch[5..27] is unsuitable: its native clear sweeps all28.
.if ::MAPPER_MMC5
PnCapVX=$5cfc
PnCapVXF=$5efc
PnCapHits=$5f38
PnCapChange=$5f3c
PnCapAnim=$5fdc
.else
PnCapVX=RgAudioRam+252
PnCapVXF=MmAudioRamStart+380
PnCapHits=MmAudioRamStart+56
PnCapChange=MmAudioRamStart+60
PnCapAnim=MmAudioRamStart+92
.endif
PnRewardTurn=$5d7d
PnBellStreak=$5d7e
.export PnCapVX,PnCapVXF,PnCapHits,PnCapChange,PnCapAnim,PnRewardTurn,PnBellStreak
.export PnPool,PnMissing,PnCapActive,PnCapX,PnCapY,PnCapPage,PnCapAge,PnCapFraction
.export PnDrawFrame,VvSlot
.pushseg
.segment "VIC_WORLD"
.proc PnEnsure
 lda PnInitialized
 cmp #$50
 beq Position
 lda #0
 tax
Clear:
.if ::MAPPER_MMC5
 sta $5c00,x
 sta $5e00,x
.else
 sta RgAudioRam,x
 sta MmAudioRamStart,x
 sta MmAudioRamStart+256,x
.endif
 inx
 bne Clear
 ldx #223
Persistent:
.if ::MAPPER_MMC5
 sta $5f00,x
.endif
 dex
 cpx #$ff
 bne Persistent
 lda #$50
 sta PnInitialized
 lda #1
 sta PnType
 sta PnDrawFlags
 lda #$80
 sta PnActive
 lda VvVariant
 sta PnSkin
 lda #1
 sta VvNeedEntry
 lda #0
 sta PnMissing
 sta PnBombPaletteReady
 lda #1
 sta PnBombCapturePending
Position:
 lda VvNeedEntry
 beq Done
 lda VvObjX
 sta PnX
 lda VvObjY
 sta PnY
 lda #0
 sta VvNeedEntry
 sta PnXF
 sta PnYF
 ldx #126
History:
 lda PnX
 sta PnHistory,x
 lda PnY
 sta PnHistory+1,x
 dex
 dex
 bpl History
Done:rts
.endproc
.proc PnMovement
 jsr PnEnsure
 ; Match the existing ship controls: A fires, B confirms a bar cell.
 lda VvHeld
 jsr SwapButtons
 sta VvHeld
 lda VvFresh
 jsr SwapButtons
 sta VvFresh
 lda VvHeld
 and #$40
 beq Released
 inc PnAutoFireAge
 lda PnAutoFireAge
 cmp #$40
 bcc Motion
 lda VvFresh
 ora #$40
 sta VvFresh
Released:lda #0
 sta PnAutoFireAge
Motion:
 BankPRGC #.bank(PnAnimationTable)
::PnNativeFrameReady:
 ldx #0
 lda PnBellFlags
 and #2
 beq Normal
 farcall PnNativeBigMotion
 jmp Gear
Normal:farcall PnNativeMotion
Gear:
 ldx #0
 farcall PnNativeGear
 lda VvFresh
 and #$80
 beq Export
 lda #1
 sta VvHudDirty
Export:
 lda PnX
 sta VvObjX
 lda PnY
 sta VvObjY
 rts
SwapButtons:
 pha
 and #$3f
 sta VvTemp
 pla
 pha
 and #$80
 lsr
 ora VvTemp
 sta VvTemp
 pla
 and #$40
 asl
 ora VvTemp
 rts
.endproc
.proc PnReset
 lda #1
 sta VvNeedEntry
 lda #0
 ldx #27
Shots:
 sta PnActive,x
 sta PnFrame,x
 sta PnContact,x
 sta PnHitMask,x
 dex
 bne Shots
 ldx #3
Caps:
 sta PnCapActive,x
 dex
 bpl Caps
 sta PnAutoFireAge
 sta PnBombPaletteReady
 lda #1
 sta PnBombCapturePending
 rts
.endproc
.proc PnWeapons
 lda GameEngineSubroutine
 cmp #8
 jne Done
 lda MmDeathFlag
 ora TimerControl
 jne Done
 lda ObjectOffset
 sta VvSavedObject
 jsr PnWorldContacts
 BankPRGC #.bank(PnAnimationTable)
 farcall PnNativeWeapons
 jsr PnCapsules
 jsr PnSoundEvents
 lda VvSavedObject
 sta ObjectOffset
Done:rts
.endproc
.proc PnTake
 lda #4
 jmp PnTakeKind
.endproc
.proc PnTakeKind
 sta PnContact
 lda PnBellFlags
 and #1
 sta VvTempPage
 lda CurrentBankC
 pha
 BankPRGC #.bank(PnAnimationTable)
 farcall PnNativePickup
 pla
 BankPRGC a
 lda #0
 sta PnContact
 lda PnBellFlags
 and #1
 beq Feedback
 lda VvTempPage
 bne Feedback
 lda #1
 sta PnBombCapturePending
Feedback:
 lda #1
 sta VvHudDirty
 lda #Sfx_CoinGrab
 sta Square2SoundQueue
 rts
.endproc
.proc PnWorldTerrain
 ; Original probe arguments: M0=screen X, R0:R1=screen Y.
 lda M1
 jne Empty
 lda M0
 clc
 adc ScreenLeft_X_Pos
 sta VvRectX
 lda ScreenLeft_PageLoc
 adc #0
 sta VvRectPage
 lda R1
 jne Empty
 lda R0
 clc
 adc #32
 bcs Empty
 sta VvRectY
 jsr VvReadCell
 tay
 lda MTileAttribute,y
 and #MTILE_SOLID
 beq Empty
 jsr PnWorldImpact
 lda #1
 rts
Empty:lda #0
 rts
.endproc
.proc PnWorldImpact
 ; One strict SMB cell transaction, retaining native block/reward animation.
 lda VvRectX
 sta MmBulletX
 lda VvRectPage
 sta MmBulletPage
 lda VvRectY
 sta MmBulletY
 lda #10
 sta MmBulletType
 lda #0
 sta MmSlot
 tax
 farcall MegaManWeapons::BombPoint
 lda #0
 sta MmBulletType
 rts
.endproc
.proc PnWorldContacts
 lda #27
 sta PnProjectile
Actor:
 ldx PnProjectile
 lda #0
 sta PnContact,x
 lda PnActive,x
 bmi Alive
 cpx #27
 bne ClearMask
 lda PnBellFlags
 and #1
 beq ClearMask
 lda PnActive+27
 jne Next
ClearMask:
 lda #0
 sta PnHitMask,x
 jmp Next
Alive:
 lda PnDrawFlags,x
 and #$c0
 jne Next
 lda PnType,x
 cmp #31
 bcc TypeReady
 lda #0
TypeReady:tay
 lda PnContactRadiusX,y
 sta VvTempY
 lda PnContactRadiusY,y
 sta VvTemp
 lda PnX,x
 clc
 adc ScreenLeft_X_Pos
 sta VvRectX
 php
 lda PnDrawFlags,x
 and #$30
 lsr
 lsr
 lsr
 lsr
 tay
 lda PnCoordinateHigh,y
 plp
 adc ScreenLeft_PageLoc
 sta VvRectPage
 lda PnY,x
 clc
 adc #32
 jcs Next
 sta VvRectY
 jsr PnShotPickups
 jcs Next
 lda #5
 sta VvEnemySlot
Enemy:
 ldx VvEnemySlot
 lda Enemy_Flag,x
 jeq EnemyNext
 jmi EnemyNext
 lda Enemy_State,x
 and #$20
 jne EnemyNext
 lda Enemy_ID,x
 cmp #Bowser
 beq Bounds
 cmp #$15
 jcs EnemyNext
 cmp #Podoboo
 jeq EnemyNext
Bounds:
 lda Enemy_BoundBoxCtrl,x
 cmp #12
 bcc BoxReady
 lda #9
BoxReady:asl
 asl
 tay
 ; Original Parodius half extents meet the actual SMB enemy rectangle.
 ; The enemy's engine origin is not its sprite center (notably Goombas).
 lda BoundBoxCtrlData,y
 clc
 adc BoundBoxCtrlData+2,y
 lsr
 clc
 adc Enemy_X_Position,x
 sta R0
 lda Enemy_PageLoc,x
 adc #0
 sta R1
 lda BoundBoxCtrlData+2,y
 sec
 sbc BoundBoxCtrlData,y
 lsr
 clc
 adc VvTempY
 sta R2
 lda R0
 sec
 sbc VvRectX
 sta R0
 lda R1
 sbc VvRectPage
 sta R1
 lda R0
 clc
 adc R2
 sta R0
 lda R1
 adc #0
 jne EnemyNext
 lda R2
 asl
 sta R3
 lda R0
 cmp R3
 jcs EnemyNext
 lda Enemy_Y_HighPos,x
 cmp #1
 jne EnemyNext
 lda BoundBoxCtrlData+1,y
 clc
 adc BoundBoxCtrlData+3,y
 lsr
 clc
 adc Enemy_Y_Position,x
 sta R0
 lda #0
 adc #0
 sta R1
 lda BoundBoxCtrlData+3,y
 sec
 sbc BoundBoxCtrlData+1,y
 lsr
 clc
 adc VvTemp
 sta R2
 lda R0
 sec
 sbc VvRectY
 sta R0
 lda R1
 sbc #0
 sta R1
 lda R0
 clc
 adc R2
 sta R0
 lda R1
 adc #0
 jne EnemyNext
 lda R2
 asl
 sta R3
 lda R0
 cmp R3
 jcs EnemyNext
 ldy PnProjectile
 lda EnemyBits,x
 and PnHitMask,y
 jne EnemyNext
 lda EnemyBits,x
 ora PnHitMask,y
 sta PnHitMask,y
 txa
 sta PnEnemyIndex,y
 lda #1
 sta PnContact,y
 lda #0
 sta PnEnemyType,x
 stx ObjectOffset
 lda Enemy_ID,x
 cmp #Bowser
 beq Boss
 jsr PnDropForEnemy
 ldx VvEnemySlot
 jsr ShellOrBlockDefeat
 jmp EnemyNext
Boss:stx R1
 jsr HandleEnemyFBallCol
EnemyNext:
 dec VvEnemySlot
 jpl Enemy
Next:
 dec PnProjectile
 lda PnProjectile
 cmp #6
 jcs Actor
 rts
EnemyBits:.byte 1,2,4,8,16,32
.endproc
.proc PnDropForEnemy
 inc VvKills
 lda VvKills
 cmp #3
 bcc Done
 lda #0
 sta VvKills
 ldy #3
Find:lda PnCapActive,y
 beq Free
 dey
 bpl Find
 rts
Free:
 inc PnRewardTurn
 lda PnRewardTurn
 and #1
 beq Bell
 lda #4
 bne Kind
Bell:lda #6
Kind:
 sta PnCapActive,y
 lda #4
 sta PnCapHits,y
 lda #0
 sta PnCapAge,y
 sta PnCapFraction,y
 sta PnCapVX,y
 sta PnCapVXF,y
 sta PnCapChange,y
 sta PnCapAnim,y
 lda Enemy_X_Position,x
 sta PnCapX,y
 lda Enemy_PageLoc,x
 sta PnCapPage,y
 lda Enemy_Y_Position,x
 sta PnCapY,y
Done:rts
.endproc
.proc PnCapsules
 lda #3
 sta VvSlot
Loop:
 ldx VvSlot
 lda PnCapActive,x
 jeq Next
 cmp #11
 jcs Floating
 inc PnCapAnim,x
 lda PnCapActive,x
 cmp #6
 ldy #12
 bcc AnimLimit
 ldy #18
AnimLimit:
 tya
 cmp PnCapAnim,x
 bne Moving
 lda #0
 sta PnCapAnim,x
Moving:
 lda PnCapActive,x
 cmp #6
 jcs BellMove
 inc PnCapAge,x
 lda PnCapAge,x
 cmp #240
 jcs Expire
 lda PnCapFraction,x
 sec
 sbc #128
 sta PnCapFraction,x
 lda PnCapX,x
 sbc #0
 sta PnCapX,x
 lda PnCapPage,x
 sbc #0
 sta PnCapPage,x
 lda PnCapX,x
 clc
 adc ScrollAmount
 sta PnCapX,x
 lda PnCapPage,x
 adc #0
 sta PnCapPage,x
 jmp Position
Floating:
 dec PnCapAge,x
 jeq Clear
 lda PnCapX,x
 clc
 adc ScrollAmount
 sta PnCapX,x
 lda PnCapPage,x
 adc #0
 sta PnCapPage,x
 jmp Next
BellMove:
 lda PnCapAge,x
 beq Acceleration
 dec PnCapAge,x
Acceleration:
 ; Original $94F5: accelerate left by1/64px per update, capped at -3.
 lda PnCapVXF,x
 clc
 adc #$fc
 sta PnCapVXF,x
 lda PnCapVX,x
 adc #$ff
 bpl Velocity
 cmp #$fd
 bcs Velocity
 lda #$fd
Velocity:sta PnCapVX,x
 ldy #0
 lda PnCapVX,x
 bpl VelocitySign
 dey
VelocitySign:
 lda PnCapFraction,x
 clc
 adc PnCapVXF,x
 sta PnCapFraction,x
 lda PnCapX,x
 adc PnCapVX,x
 sta PnCapX,x
 tya
 adc PnCapPage,x
 sta PnCapPage,x
 ; Original $A1FB integrates screen-space Bell velocity without subtracting
 ; native camera scroll. Convert that screen delta back into SMB world X.
 lda PnCapX,x
 clc
 adc ScrollAmount
 sta PnCapX,x
 lda PnCapPage,x
 adc #0
 sta PnCapPage,x
Position:
 ; A capsule left behind by autoscrolling must release its physical slot.
 lda PnCapX,x
 clc
 adc #16
 sta R0
 lda PnCapPage,x
 adc #0
 sta R1
 lda R0
 sec
 sbc ScreenLeft_X_Pos
 lda R1
 sbc ScreenLeft_PageLoc
 jmi Expire
 lda Player_X_Position
 sec
 sbc PnCapX,x
 sta R0
 lda Player_PageLoc
 sbc PnCapPage,x
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
 sbc PnCapY,x
 clc
 adc #12
 cmp #25
 bcs Next
 lda PnCapActive,x
 cmp #6
 bne TakeType
 farcall PnGoldBellScore
 lda #6
 jsr PnTakeKind
 jmp Next
TakeType:
 cmp #4
 bcs Typed
 lda #4
Typed:jsr PnTakeKind
 ldx VvSlot
 jmp Clear
Expire:
 lda PnCapActive,x
 cmp #6
 bcc Clear
 lda #0
 sta PnBellStreak
Clear:
 lda #0
 sta PnCapActive,x
Next:dec VvSlot
 jpl Loop
 rts
.endproc
.proc PnSoundEvents
 lda VvSfxEvent
 beq Done
 cmp #$1c
 beq Coin
 cmp #$39
 beq Power
 cmp #$38
 beq Power
 cmp #$22
 beq Power
 cmp #$24
 beq Power
 cmp #$25
 beq Power
 lda #Sfx_Fireball
 sta Square1SoundQueue
 jmp Clear
Coin:lda #Sfx_CoinGrab
 bne Pickup
Power:lda #Sfx_PowerUpGrab
Pickup:
 ldx Square2SoundQueue
 cpx #Sfx_ExtraLife
 beq Clear
 sta Square2SoundQueue
Clear:
 lda #0
 sta VvSfxEvent
Done:rts
.endproc
.proc PnShotPickups
 ldx PnProjectile
 lda PnType,x
 cmp #7                       ; source Red crest cannot recolor a Bell
 jeq NoHit
 lda #3
 sta VvSlot
Caps:
 ldx VvSlot
 lda PnCapActive,x
 cmp #6
 jcc Next
 cmp #11
 jcs Next
 lda PnCapX,x
 clc
 adc #8
 sta R0
 lda PnCapPage,x
 adc #0
 sta R1
 lda VvTempY
 clc
 adc #3
 sta R2
 lda R0
 sec
 sbc VvRectX
 sta R0
 lda R1
 sbc VvRectPage
 sta R1
 lda R0
 clc
 adc R2
 sta R0
 lda R1
 adc #0
 jne Next
 lda R2
 asl
 cmp R0
 jcc Next
 lda VvTemp
 clc
 adc #3
 sta R2
 lda PnCapY,x
 clc
 adc #8
 sec
 sbc VvRectY
 clc
 adc R2
 sta R0
 lda R2
 asl
 cmp R0
 jcc Next
 ldy PnProjectile
 lda PnCapActive,x
 sta PnContact,y
 lda PnCapAge,x
 jne Hit
 lda #4
 sta PnCapAge,x
 dec PnCapHits,x
 bne Bounce
 inc PnCapChange,x
 ldy PnCapChange,x
 cpy #16
 bcs Vanish
 lda PnBellColorSteps,y
 tay
 lda PnBellContactTypes,y
 sta PnCapActive,x
 lda #1
 cpy #0
 bne SaveHits
 lda #4
SaveHits:sta PnCapHits,x
Bounce:
 lda #1                       ; original Bell hit sets velocity +1px/update
 sta PnCapVX,x
 lda #0
 sta PnCapVXF,x
 lda #Sfx_Bump
 sta Square1SoundQueue
Hit:sec
 rts
Vanish:
 lda #0
 sta PnCapActive,x
 sta PnBellStreak
 sec
 rts
Next:
 dec VvSlot
 jpl Caps
NoHit:clc
 rts
.endproc
.proc PnBody
 lda #0
 sta GuestBodyStompAllowed
 lda #1
 sta GuestBodyNoStomp
 lda PnBellFlags
 and #2
 beq Shield
 lda Enemy_ID,x
 cmp #BulletBill_CannonVar
 beq Crush
 cmp #$15
 bcs Protected
 cmp #Podoboo
 beq Protected
Crush:
 stx ObjectOffset
 jsr ShellOrBlockDefeat
 sec
 rts
Shield:
 lda VvHurt
 bne Protected
 lda PnAux
 beq Fatal
 dec PnAux
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
Fatal:clc
 rts
.endproc
.proc PnInjury
 lda PnBellFlags
 and #2
 bne Safe
 lda PnAux
 beq Fatal
 dec PnAux
 lda #8
 sta VvHurt
 lda #4
 sta InjuryTimer
Safe:sec
 rts
Fatal:ldx #0
 jmp KillPlayer
.endproc
.popseg

.pushseg
.segment "VIC_CORE"
.proc PnPublishSkin
 rts
.endproc
.proc PnSoundEvent
 sta VvSfxEvent
 rts
.endproc
.proc PnSourceExit
 rts                         ; SMB owns flagpole/castle/pipe scripting.
.endproc
.proc PnBellSpecials
 farcall PnBellTick,jmp
.endproc
.macro PnWorldCallback Name,Target
.proc Name
 phx
 phy
 lda M0
 pha
 lda M1
 pha
 lda R0
 pha
 lda R1
 pha
 lda R4
 pha
 lda R5
 pha
 lda R6
 pha
 lda R7
 pha
 farcall Target
 sta PnReturn
 pla
 sta R7
 pla
 sta R6
 pla
 sta R5
 pla
 sta R4
 pla
 sta R1
 pla
 sta R0
 pla
 sta M1
 pla
 sta M0
 BankPRGC #.bank(PnAnimationTable)
 ply
 plx
 lda PnReturn
 rts
.endproc
.endmacro
PnWorldCallback PnTerrainQuery,PnWorldTerrain
PnWorldCallback PnTerrainImpact,PnWorldImpact
.popseg
