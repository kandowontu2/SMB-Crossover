.pushseg
.segment "M3_LOGIC"
.proc M3Movement
 jsr M3Ensure
 lda M3Ready
 cmp #$b3
 bne Reset
 lda NumberofLives
 cmp M3Life
 bne Reset
 lda AreaNumber
 cmp M3LastArea
 bne Reset
 lda LevelNumber
 cmp M3LastLevel
 beq Ready
Reset:jsr M3Reset
Ready:
 lda SavedJoypadBits
 eor M3Previous
 and SavedJoypadBits
 sta M3Fresh
 lda SavedJoypadBits
 sta M3Previous
 lda Player_X_Position
 sta M3OldX
 sta MmOldX
 lda Player_Y_Position
 sta M3OldY
 lda M3Growth
 ora M3Poof
 beq Move
 lda #0
 sta Player_X_Speed
 sta Player_X_Scroll
 rts
Move:
 lda Player_State
 cmp #3
 bne Native
 farcall MegaManClimbing,jmp
Native:
 farcall M3Step
 lda Player_Rel_XPos
 sta Player_Pos_ForScroll
 rts
.endproc
.segment "M3_NATIVE"
.proc M3Step
 lda Player_X_Position
 sta M3Native::Player_X
 lda Player_PageLoc
 sta M3Native::Player_XHi
 lda Player_Y_Position
 sta M3Native::Player_Y
 sta M3Native::Player_SpriteY
 lda Player_Y_HighPos
 sta M3Native::Player_YHi
 lda #0
 sta M3Native::Player_AboveTop
 sta M3Native::FloatLevel_PlayerWaterStat
 sta M3Native::Player_IsHolding
 sta M3Native::Player_Kuribo
 sta M3Native::Player_TwisterSpin
 sta M3Native::Level_PipeMove
 sta M3Native::Level_SlopeEn
 sta M3Native::Level_Tile_GndL
 sta MmSliding
 sta MmOnVine
 lda AreaType
 bne Dry
 lda #$40
 sta M3Native::FloatLevel_PlayerWaterStat
 lda #1
 sta M3Native::Player_InWater
 sta MmUnderwater
 jmp WaterReady
Dry:lda #0
 sta M3Native::Player_InWater
 sta MmUnderwater
WaterReady:
 lda SavedJoypadBits
 sta M3Native::Pad_Holding
 lda M3Fresh
 sta M3Native::Pad_Input
 lda FrameCounter
 sta M3Native::Counter_1
 lda StarInvincibleTimer
 sta M3Native::Player_StarInv
 lda M3Native::Counter_Wiggly
 and #$f0
 sec
 sbc #$90
 sta M3Native::Counter_Wiggly
 lda M3Native::Player_TailCount
 beq :+
 dec M3Native::Player_TailCount
:
 lda M3Native::Player_FireCount
 beq :+
 dec M3Native::Player_FireCount
:
 lda M3Native::Player_PMeterCnt
 beq :+
 dec M3Native::Player_PMeterCnt
:
 lda M3Native::Player_TailAttack
 beq :+
 dec M3Native::Player_TailAttack
:
 lda M3Native::Player_QueueSuit
 beq QueueReady
 cmp #$0f
 bcc OrdinaryQueue
 lda M3Form
 cmp #5
 bne ClearQueue
 lda #$c0
 sta M3Native::Player_Statue
 bne ClearQueue
OrdinaryQueue:sec
 sbc #1
 sta M3Form
ClearQueue:lda #0
 sta M3Native::Player_QueueSuit
QueueReady:
 lda Player_X_Speed
 cmp M3LastVX
 beq XReady
 sta M3Native::Player_XVel
 lda #0
 sta M3Native::Player_XVelFrac
XReady:
 lda Player_State
 bne Air
 lda #0
 sta M3Native::Player_InAir
 sta M3Native::Player_YVel
 beq Run
Air:
 lda #1
 sta M3Native::Player_InAir
 lda Player_Y_Speed
 cmp M3LastVY
 beq Run
 asl
 asl
 asl
 asl
 sta M3Native::Player_YVel
Run:
 jsr M3Native::Player_Control
 jsr M3Native::Player_PowerUpdate
 jsr M3Native::Player_SetSpecialFrames
 lda M3Native::Player_X
 sta Player_X_Position
 sec
 sbc M3OldX
 sta Player_X_Scroll
 lda M3Native::Player_XHi
 sta Player_PageLoc
 lda M3Native::Player_Y
 sta Player_Y_Position
 lda M3Native::Player_YHi
 sta Player_Y_HighPos
 lda M3Native::Player_XVel
 sta Player_X_Speed
 sta M3LastVX
 bpl :+
 eor #$ff
 clc
 adc #1
:sta Player_XSpeedAbsolute
 lda M3Native::Player_YVel
 lsr
 lsr
 lsr
 lsr
 cmp #8
 bcc :+
 ora #$f0
:sta Player_Y_Speed
 sta M3LastVY
 sta MmVY+2
 lda M3Native::Player_InAir
 beq Ground
 lda #1
 ldy M3Native::Player_YVel
 bmi :+
 lda #2
:sta Player_State
 bne Body
Ground:lda #0
 sta Player_State
Body:
 lda M3Native::Player_IsDucking
 sta CrouchingFlag
 sta RgCrouch
 lda #0
 ldx M3Form
 bne :+
 lda #1
:sta PlayerSize
 lda M3Form
 beq Status
 cmp #2
 bcc Status
 lda #2
Status:sta PlayerStatus
 lda M3Native::Player_FlipBits
 and #$40
 beq Left
 lda #1
 bne Face
Left:lda #2
Face:sta PlayerFacingDir
 lda M3Native::Sound_QPlayer
 and #$81 ; Native jump/Frog hop; provisional SMB world-effect bridge.
 beq Swim
 lda #Sfx_BigJump
 sta Square1SoundQueue
Swim:lda M3Native::Sound_QPlayer
 and #4
 beq Tail
 lda #Sfx_EnemyStomp
 sta Square1SoundQueue
Tail:lda M3Native::Sound_QLevel1
 cmp #M3Native::SND_LEVELTAILWAG
 bne Poof
 lda #Sfx_Fireball
 sta Square1SoundQueue
Poof:lda M3Native::Sound_QLevel1
 cmp #M3Native::SND_LEVELPOOF
 bne Clear
 lda #24
 sta M3Poof
 lda #Sfx_PipeDown_Injury
 sta Square1SoundQueue
 lda #0
 sta M3Native::Player_SuitLost
Clear:lda #0
 sta M3Native::Sound_QPlayer
 sta M3Native::Sound_QLevel1
 sta M3Native::Sound_QLevel2
 sta MmVX
 sta MmVY
 sta MmVY+1
 lda M3Native::Player_XVel
 asl
 asl
 asl
 asl
 sta MmVX+1
 lda M3Native::Player_XVel
 lsr
 lsr
 lsr
 lsr
 cmp #8
 bcc :+
 ora #$f0
:sta MmVX+2
 rts
.endproc
.popseg
