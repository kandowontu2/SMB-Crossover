; Playable NPC adaptation. The frozen source motion is split only at its
; original world callback: native terrain runs once between these halves.
.setcpu "6502"
.macpack longbranch
.include "state.inc"
.include "host-imports.inc"
.export BwCacheServices,BwCacheDecline,BwConstruct,BwMovement,BwGraphics
.export BwWeaponTail,BwDrawShots,BwInjury,BwPickup,BwEnsure
.segment "BW_IMAGE"
BwCacheServices:
 .word 0 ; builder replaces this two-byte marker with the real36JMP table
BwCacheDecline:clc
 rts
BwNoop:rts
BwVisible:sec
 rts

.macro BwFar target
 sta SafecallA_SMC+1
 lda #<target
 sta FarcallJmpTarget_SMC+1
 lda #>target
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(target)|$80)
 jsr FarCallCommon
.endmacro

; A/P/X/Y retained for the actual forcedblank scene callback. Persist only
; HP/tier within this selected family's cache, independently for each player.
BwConstruct:
 php
 pha
 txa
 pha
 tya
 pha
 jsr BwSavePlayer
 lda FmAlts
 and #8
 beq BwCtorThree
 lda #1
BwCtorThree:
 sta BwVariant
 lda #0
 ldx #33
BwCtorClear:
 sta BwVel,x
 dex
 bpl BwCtorClear
 ; Fresh clears the source variant too; restore the selected identity last.
 lda FmAlts
 and #8
 beq BwCtorVariant
 lda #1
BwCtorVariant:sta BwVariant
 lda #0
 sta BwPending
 sta BwPrevious
 sta BwShots
 sta BwShots+10
 sta MmDeathFlag
 sta CrouchingFlag
 sta PlayerSize
 lda #$ff
 sta BwPaletteAck
 lda #1
 sta BwFacing
 jsr BwSelectPlayer
 jsr BwImport
 lda #$b7
 sta BwReady
 pla
 tay
 pla
 tax
 pla
 plp
 rts

BwSelectPlayer:
 lda CurrentPlayer
 and #1
 asl
 asl
 tax
 stx BwPlayerKey
 lda BwPersistent+3,x
 cmp #$b7
 bne BwPlayerNew
 lda BwPersistent+2,x
 cmp NumberofLives
 bne BwPlayerNew
 lda BwPersistent,x
 beq BwPlayerNew
 bne BwPlayerLoad
BwPlayerNew:
 lda #34                    ; original SMB3 boss health, playable1-hit damage
 ldy BwVariant
 beq BwPlayerHP
 lda #5                     ; original SMB1 boss health
BwPlayerHP:sta BwPersistent,x
 lda #0
 sta BwPersistent+1,x
 lda NumberofLives
 sta BwPersistent+2,x
 lda #$b7
 sta BwPersistent+3,x
BwPlayerLoad:
 lda BwPersistent,x
 sta BwHP
 lda BwPersistent+1,x
 sta BwTier
 sta PlayerStatus
 rts

BwSavePlayer:
 lda BwReady
 cmp #$b7
 bne BwSaveDone
 ldx BwPlayerKey
 lda BwHP
 sta BwPersistent,x
 lda BwTier
 sta BwPersistent+1,x
BwSaveDone:rts

BwEnsure:
 lda BwReady
 cmp #$b7
 jne BwConstruct
 lda CurrentPlayer
 and #1
 asl
 asl
 cmp BwPlayerKey
 jne BwConstruct
 ldx BwPlayerKey
 lda NumberofLives
 cmp BwPersistent+2,x
 jne BwConstruct
 rts

BwImport:
 lda Player_X_Position
 sta BwPos
 lda Player_PageLoc
 sta BwPage
 lda Player_Y_Position
 sta BwPos+1
 lda Player_Y_HighPos
 sta BwPage+1
 lda Player_State
 beq BwImportGround
 lda #0
 sta BwGrounded
 rts
BwImportGround:
 lda #1
 sta BwGrounded
 rts

BwActive:
 lda OperMode
 cmp #1
 bne BwInactive
 lda GameEngineSubroutine
 cmp #8
 bne BwInactive
 lda GamePauseStatus
 and #1
 ora TimerControl
 bne BwInactive
 lda BwHP
 beq BwInactive
 sec
 rts
BwInactive:clc
 rts

BwMovement:
 jsr BwEnsure
 jsr BwActive
 jcc BwMovementDone
 jsr BwImport
 lda Player_X_Position
 sta BwOldX
 lda Player_Y_Speed
 cmp BwNativeY
 beq BwMoveKeepY
 ldx BwVariant
 bne BwMoveSetY
 asl
 asl
 asl
 asl
BwMoveSetY:sta BwVel+1
 lda #0
 sta BwFrac+1
 sta BwForceY
BwMoveKeepY:
 lda #0
 sta BwPending
 lda SavedJoypadBits
 ldx BwVariant
 bne BwMoveOne
 jsr Bw3Step
 jmp BwExport
BwMoveOne:
 jsr Bw1Step
BwExport:
 lda BwPos
 sta Player_X_Position
 sec
 sbc BwOldX
 sta Player_X_Scroll
 lda BwPage
 sta Player_PageLoc
 lda BwPos+1
 sta Player_Y_Position
 lda BwPage+1
 sta Player_Y_HighPos
 lda BwFacing
 sta PlayerFacingDir
 lda BwVel
 sta Player_X_Speed
 bpl BwAbsX
 eor #$ff
 clc
 adc #1
BwAbsX:sta Player_XSpeedAbsolute
 lda BwVel+1
 ldx BwVariant
 bne BwNativeYSpeed
 cmp #$80
 ror
 cmp #$80
 ror
 cmp #$80
 ror
 cmp #$80
 ror
BwNativeYSpeed:
 sta Player_Y_Speed
 sta BwNativeY
 lda BwGrounded
 bne BwExportGround
 lda #1
 ldx Player_Y_Speed
 bmi BwExportState
 lda #2
 bne BwExportState
BwExportGround:lda #0
BwExportState:sta Player_State
 lda #0
 sta PlayerSize
 sta CrouchingFlag
BwMovementDone:sec
 rts

; Actual ProcFireball_Bubble tail is after PlayerCtrl/native BG collision.
; Import native camera/side/ceiling/ground clamps before the source's original
; gravity/pose continuation. This runs once even when DrawAll skips a frame.
BwWeaponTail:
 jsr BwEnsure
 jsr BwActive
 bcc BwTailDone
 lda BwPending
 beq BwTailShots
 lda #0
 sta BwPending
 jsr BwImport
 lda Player_Y_Speed
 cmp BwNativeY
 beq BwTailKeepSpeed
 ldx BwVariant
 bne BwTailSetY
 asl
 asl
 asl
 asl
BwTailSetY:sta BwVel+1
 lda #0
 sta BwFrac+1
 sta BwForceY
BwTailKeepSpeed:
 jsr BwCoreFinish
BwTailShots:
 lda BwEmit
 beq BwTailAdvance
 jsr BwSpawnFire
 lda #0
 sta BwEmit
BwTailAdvance:
 jsr BwAdvanceFire
 jsr BwSavePlayer
BwTailDone:rts

BwStatus:
 lda BwTier
 tax
 rts
BwInjury:
 jsr BwEnsure
 lda InjuryTimer
 bne BwProtected
 lda BwHP
 beq BwHurtDead
 dec BwHP
 beq BwHurtDead
 lda #90
 sta InjuryTimer
 lda #4
 sta Square1SoundQueue
 jsr BwSavePlayer
BwProtected:sec
 rts
BwHurtDead:
 lda #0
 sta BwHP
 jsr BwSavePlayer
 jsr KillPlayer
 sec
 rts
BwDeathStart:
 lda #0
 sta BwHP
 sta BwPending
 sta BwShots
 sta BwShots+10
 jsr BwSavePlayer
 rts
BwDeath:
 BwFar NativePlayerDeath
 rts
BwBody:
 lda AreaType
 sta GuestBodyStompAllowed
 lda #0
 sta GuestBodyNoStomp
 clc
 rts
BwAdder:ldy #0
 sec
 rts
BwBoxProfile:ldy #0
 rts
BwHead:jsr BlockBufferColli_Head
 rts
BwSide:jsr BlockBufferColli_Side
 rts
BwHeadWithin:
 lda Player_Y_Position
 cmp #32
 rts
BwFullBox:
 ; The WIP uses native big-player16x32 contact geometry. Exact original
 ; artwork extends above it by8/16px; no fictitious boss hitbox is claimed.
 lda Player_Rel_XPos
 clc
 adc #2
 sta BoundingBox_UL_Corner
 clc
 adc #12
 sta BoundingBox_LR_Corner
 lda Player_Rel_YPos
 sta BoundingBox_UL_Corner+1
 clc
 adc #32
 sta BoundingBox_LR_Corner+1
 rts
BwBounce:
 lda #$fc
 sta Player_Y_Speed
 lda #0
 sta Player_Y_MoveForce
 lda #1
 sta Player_State
 sec
 rts
BwPrepare:sec
 rts
BwMature:
 lda Enemy_State,x
 bmi BwMatureYes
 clc
 rts
BwMatureYes:sec
 rts
BwPickup:
 lda PowerUpType,x
 cmp #2
 bcs BwPickupNative
 lda Enemy_State,x
 bpl BwPickupDone
 txa
 pha
 lda BwTier
 sta GuestPowerupOld
 sta GuestPowerupDisplay
 lda PowerUpType,x
 bne BwGrantFlower
 lda BwTier
 bne BwGrantDone
 lda #1
 bne BwGrantTier
BwGrantFlower:lda #2
BwGrantTier:sta BwTier
BwGrantDone:
 lda BwTier
 sta PlayerStatus
 sta GuestPowerupTarget
 lda #34
 ldy BwVariant
 beq BwGrantHP
 lda #5
BwGrantHP:sta BwHP
 jsr BwSavePlayer
 pla
 tax
 jsr EraseEnemyObject
 txa
 pha
 lda #6
 jsr SetupFloateyNumber
 lda #$20
 sta Square2SoundQueue
 BwFar MarioSourceBeginFreeze
 pla
 tax
BwPickupDone:rts
BwPickupNative:
 BwFar MarioSourcePowerupCollision
 rts
BwFullPower:
 lda #2
 sta BwTier
 sta PlayerStatus
 lda #34
 ldx BwVariant
 beq BwFullHP
 lda #5
BwFullHP:sta BwHP
 jsr BwSavePlayer
 rts
BwPowerupTick:
 BwFar GuestPowerupUpdate
 lda BwTier
 sta PlayerStatus
 lda #0
 sta PlayerSize
 rts

BwUi:
 lda StarInvincibleTimer
 beq BwUiNormal
 lda #$ff
 sta BwPaletteAck
 rts
BwUiNormal:
 lda BwPaletteAck
 beq BwUiDone
 BwFar BwColors
 lda #0
 sta BwPaletteAck
BwUiDone:rts

BwGraphics:
 jsr BwEnsure
 lda R0
 pha
 lda R1
 pha
 lda BwVariant
 beq BwGfxThree
 lda BwPose
 and #3
 asl
 tax
 lda Bw1RightPtrs,x
 sta R0
 lda Bw1RightPtrs+1,x
 sta R1
 lda #8
 sta BwDrawY
 lda #8
 sta BwDrawX
 lda #<824
 bne BwGfxPage
BwGfxThree:
 ldx BwPose
 cpx #9
 bcc BwGfxPoseOK
 ldx #0
BwGfxPoseOK:
 lda Bw3PoseLo,x
 sta R0
 lda Bw3PoseHi,x
 sta R1
 lda #16
 sta BwDrawY
 lda #0
 sta BwDrawX
 lda Bw3PosePages,x
 clc
 adc #<825
BwGfxPage:
 sta BwDrawPage
 ldy #0
 lda (R0),y
 sta BwRenderBuffer
 sta BwPartBytes
 iny
BwGfxCopy:
 lda (R0),y
 sta BwRenderBuffer,y
 iny
 cpy BwPartBytes
 bcc BwGfxCopy
 beq BwGfxCopy
 lda #0
 sta BwDrawFlip
 lda PlayerFacingDir
 cmp #1
 beq BwGfxFacingRight
 lda #$40
BwGfxFacingRight:
 ; Original3 unflipped poses faceLEFT; original1 right records faceRIGHT.
 ldx BwVariant
 bne BwGfxHaveFlip
 eor #$40
BwGfxHaveFlip:sta BwDrawFlip
 ldy #2
BwGfxAdjust:
 lda BwRenderBuffer,y
 eor BwDrawFlip
 sta BwRenderBuffer,y
 iny
 lda BwRenderBuffer,y
 sec
 sbc BwDrawY
 sta BwRenderBuffer,y
 iny
 lda BwDrawFlip
 beq BwGfxUnflippedX
 lda #16
 sec
 sbc BwRenderBuffer,y
 jmp BwGfxXOffset
BwGfxUnflippedX:lda BwRenderBuffer,y
BwGfxXOffset:
 sec
 sbc BwDrawX
 sta BwRenderBuffer,y
 iny
 iny
 cpy BwPartBytes
 bcc BwGfxAdjust
 beq BwGfxAdjust
 lda #<(BwRenderBuffer+$2000)
 sta SmPosePtr
 lda #>(BwRenderBuffer+$2000)
 sta SmPosePtr+1
 lda #3
 sta CurrentBankC
 sta $5116
 lda BwDrawPage
 ldx #3
 ldy #0
 BwFar X5SetPhysicalChr
 lda CurrentCHRBank
 sta SmChrBank
 lda Player_SprAttrib
 and #$20
 sta Player_SprAttrib
 lda #.lobyte(METASPRITE_SAMUS_BODY)
 sta ObjectMetasprite
 pla
 sta R1
 pla
 sta R0
 rts

Bw1RightPtrs:.word Bw1OPEN1RIGHT,Bw1OPEN2RIGHT,Bw1CLOSED1RIGHT,Bw1CLOSED2RIGHT

; Two friendly flames. Source3 uses Bowser_FireballXVel[-10,+10] in4.4;
; source1 uses the original40/60 fractional subtraction, mirrored for right.
; Original native SMB flame graphics and P2 are the disclosed common WIP art.
BwSpawnFire:
 ldx #0
 lda BwShots
 beq BwSpawnSlot
 ldx #10
 lda BwShots+10
 bne BwSpawnDone
BwSpawnSlot:
 lda #1
 sta BwShots,x
 lda BwFacing
 sta BwShots+1,x
 lda BwPos
 clc
 adc #16
 sta BwShots+2,x
 lda BwPage
 adc #0
 sta BwShots+3,x
 lda BwPos+1
 sec
 sbc #8
 sta BwShots+4,x
 lda #0
 sta BwShots+5,x
 sta BwShots+6,x
 lda #100
 sta BwShots+7,x
 lda BwShots+4,x
 sta BwShots+8,x
 lda #$08
 sta NoiseSoundQueue
BwSpawnDone:rts

BwAdvanceFire:
 ldx #0
BwFireSlot:
 stx BwShotSlot
 lda BwShots,x
 jeq BwFireNext
 dec BwShots+7,x
 jeq BwFireErase
 lda BwVariant
 bne BwFireOne
 lda BwShots+1,x
 cmp #1
 bne BwFireThreeLeft
 inc BwShots+2,x
 bne BwFireContact
 inc BwShots+3,x
 jmp BwFireContact
BwFireThreeLeft:
 lda BwShots+2,x
 bne BwFireThreeDec
 dec BwShots+3,x
BwFireThreeDec:dec BwShots+2,x
 jmp BwFireContact
BwFireOne:
 lda #$40
 ldy SecondaryHardMode
 beq BwFireForce
 lda #$60
BwFireForce:sta BwTemp
 lda BwShots+1,x
 cmp #1
 bne BwFireOneLeft
 lda BwShots+5,x
 clc
 adc BwTemp
 sta BwShots+5,x
 lda BwShots+2,x
 adc #1
 sta BwShots+2,x
 lda BwShots+3,x
 adc #0
 sta BwShots+3,x
 jmp BwFireContact
BwFireOneLeft:
 lda BwShots+5,x
 sec
 sbc BwTemp
 sta BwShots+5,x
 lda BwShots+2,x
 sbc #1
 sta BwShots+2,x
 lda BwShots+3,x
 sbc #0
 sta BwShots+3,x
BwFireContact:
 jsr BwFireActors
 jmp BwFireNext
BwFireErase:
 lda #0
 sta BwShots,x
BwFireNext:
 ldx BwShotSlot
 txa
 clc
 adc #10
 tax
 cpx #20
 jcc BwFireSlot
 rts

BwFireActors:
 ldy #5
BwFireEnemy:
 lda Enemy_Flag,y
 jeq BwFireEnemyNext
 bmi BwFireEnemyNext
 lda Enemy_State,y
 and #$20
 bne BwFireEnemyNext
 lda Enemy_Y_HighPos,y
 cmp #1
 bne BwFireEnemyNext
 lda Enemy_ID,y
 cmp #$15
 bcc BwFireEligible
 cmp #$2d
 bne BwFireEnemyNext
BwFireEligible:
 lda Enemy_X_Position,y
 sec
 sbc BwShots+2,x
 sta BwTemp
 lda Enemy_PageLoc,y
 sbc BwShots+3,x
 beq BwFireEnemyRight
 cmp #$ff
 bne BwFireEnemyNext
 lda BwTemp
 cmp #$e9
 bcc BwFireEnemyNext
 bcs BwFireEnemyY
BwFireEnemyRight:
 lda BwTemp
 cmp #16
 bcs BwFireEnemyNext
BwFireEnemyY:
 lda Enemy_Y_Position,y
 sec
 sbc BwShots+4,x
 clc
 adc #15
 cmp #31
 bcs BwFireEnemyNext
 tya
 tax
 stx R1
 jsr HandleEnemyFBallCol       ; genuine native immunity/HP/defeat/score/SFX
 ldx BwShotSlot
 lda #0
 sta BwShots,x
 rts
BwFireEnemyNext:dey
 jpl BwFireEnemy
 rts

BwDrawShots:
 lda R0
 pha
 lda R1
 pha
 ldx #0
BwDrawFireLoop:
 stx BwShotSlot
 lda BwShots,x
 beq BwDrawFireNext
 lda BwShots+2,x
 sec
 sbc ScreenLeft_X_Pos
 sta R4
 lda BwShots+3,x
 sbc ScreenLeft_PageLoc
 sta R5
 lda BwShots+4,x
 sta R6
 lda #1
 sta R7
 lda #<(BwFireRecord+$2000)
 sta R0
 lda #>(BwFireRecord+$2000)
 sta R1
 lda FrameCounter
 and #2
 asl
 asl
 asl
 asl
 asl
 asl
 ora #2
 sta R3
 BwFar MetaspriteRenderLoop
BwDrawFireNext:
 ldx BwShotSlot
 txa
 clc
 adc #10
 tax
 cpx #20
 bcc BwDrawFireLoop
 pla
 sta R1
 pla
 sta R0
 rts
BwFireRecord:.byte 12,56,0,0,0,58,0,0,8,60,0,0,16
