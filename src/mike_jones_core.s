; StarTropics source HP/weapon rules; SMB pickup/level delivery is adapted.
.pushseg
.segment "MIKE_CORE"
.proc JnIsActive
 lda SelectedCharacter
 cmp #CHARACTER_MIKE
 jeq Yes
 clc
 rts
Yes:sec
 rts
.endproc
.proc JnEnsure
 lda JnMaxHearts
 jne Stage
 lda #0
 ldx #15
Clear:sta JnPersistent,x
 dex
 jpl Clear
 lda #3
 sta JnMaxHearts
 lda #6
 sta JnHealth
 lda #1
 sta JnOwnedTier
 lda #$ff
 sta JnStage
Stage:
 lda WorldNumber
 asl
 asl
 clc
 adc LevelNumber
 cmp JnStage
 jeq Ready
 sta JnStage
 jsr JnClearGear
Ready:
 lda JnHealth
 jne ReadyState
 lda MmDeathFlag
 jne ReadyState
 lda JnMaxHearts
 asl
 sta JnHealth
 lda #1
 sta JnUiDirty
ReadyState:
 lda JnReady
 cmp #$4a
 jeq Done
 jmp JnAreaReset
Done:rts
.endproc
.proc JnClearGear
 lda #0
 ldx #9
Clear:sta JnAmmo,x
 dex
 jpl Clear
 sta JnSelected
 lda JnStars
 and #$80
 sta JnStars
 lda #1
 sta JnUiDirty
 rts
.endproc
.proc JnAreaReset
 jsr JnIsActive
 jcc Done
 lda JnHealth
 jne ClearEntry
 lda MmDeathFlag
 jne ClearEntry
 lda JnMaxHearts
 asl
 sta JnHealth
ClearEntry:
 lda #0
 tax
Clear:sta $5c00,x
 inx
 jne Clear
 lda #$4a
 sta JnReady
 lda SavedJoypadBits
 sta JnPrevious
 lda #1
 sta JnUiDirty
Done:rts
.endproc
.proc JnEffectiveTier
 ; Original bank26:A783..A7B7. 0112 is half-heart HP; thresholds0C/16.
 lda JnOwnedTier
 cmp #3
 jcc Two
 ldx JnHealth
 cpx #22
 jcs Done
 lda #2
Two:cmp #2
 jcc Done
 ldx JnHealth
 cpx #12
 jcs Done
 lda #1
Done:jmp JnPublishTier
 nop ; preserve all subsequent resident profile addresses
.endproc
.proc JnInputs
 lda SavedJoypadBits
 eor JnPrevious
 and SavedJoypadBits
 sta JnPressed
 lda SavedJoypadBits
 sta JnPrevious
 lda JnPressed
 and #Select_Button
 jeq Done
 ldx JnSelected
Next:inx
 cpx #11
 bcc :+
 ldx #0
:txa
 jeq Store
 lda JnAmmo-1,x
 jeq Next
Store:stx JnSelected
 lda #1
 sta JnUiDirty
 lda #Sfx_CoinGrab
 sta Square2SoundQueue
Done:rts
.endproc
.proc JnInjury
 lda JnHurt
 jne Protected
 stx JnSavedX
 lda JnHealth
 sec
 sbc #2
 jcc Fatal
 jeq Fatal
 sta JnHealth
 lda #60 ; source-like hurt interval, scaled SMB contact2 half-hearts.
 sta JnHurt
 lda #1
 sta JnUiDirty
 lda #4
 sta InjuryTimer
 lda #0
 sta TimerControl
 sta PlayerChangeSizeFlag
 sta GuestHurtTicks
 sta GuestHurtKind
 lda #Sfx_EnemySmack
 sta Square1SoundQueue
 ldx JnSavedX
Protected:sec
 rts
Fatal:lda #0
 sta JnHealth
 ldx JnSavedX
 jmp KillPlayer
.endproc
.proc JnInjuryStatus
 lda JnHurt
 jne Alive
 lda JnHealth
 cmp #3
 jcs Alive
 lda #0
 sta JnHealth
 rts
Alive:lda #1
 rts
.endproc
.proc JnLifeLost
 jsr JnClearGear
 lda #0
 sta JnHealth
 jmp JnAreaReset::ClearEntry
.endproc
.proc JnDeath
 inc MmDeathAge
 lda MmDeathAge
 cmp #120
 jcc Done
 lda #6
 sta GameEngineSubroutine
 lda #0
 sta TimerControl
Done:rts
.endproc
.proc JnPalette
 ; Source scene palette $3F1D..1F=07,36,21; dedicate only player0.
 ldx VRAM_Buffer1_Offset
 cpx #78 ; Six command bytes plus terminator fit the84-byte buffer.
 jcs Done
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 lda #$07
 sta VRAM_Buffer1+3,x
 lda #$36
 sta VRAM_Buffer1+4,x
 lda #$21
 sta VRAM_Buffer1+5,x
 txa
 clc
 adc #6
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
Done:rts
.endproc
.proc JnGraphics
 lda Player_Rel_XPos
 sta Player_Pos_ForScroll
 lda Player_SprAttrib
 and #$fc
 sta Player_SprAttrib
 lda JnHurt
 jeq Visible
 and #4
 jeq Visible
 lda #0
 sta ObjectMetasprite
 rts
Visible:
 ldx #0
 lda Player_State
 jeq Ground
 ldx #3
Ground:
 lda JnAttack
 jeq Walk
 ldx JnWeapon
 cpx #10
 jne OrdinaryAttack
 ldx #3
 jmp Pose
OrdinaryAttack:
 lda JnAttack
 ldx #4
 cmp #6
 jcc Pose
 ldx #5
 jmp Pose
Walk:
 lda Player_State
 jne Pose
 lda Player_X_Speed
 jeq Pose
 lda JnClock
 lsr
 lsr
 and #3
 tax
 lda WalkFrames,x
 tax
Pose:jmp JnSetPose
WalkFrames:.byte 0,1,2,1
.endproc
.proc JnPortrait
 jsr JnEnsure
 ldx #0
 jsr JnSetPose
 jmp JnPalette
.endproc
.proc JnSetPose
 BankPRGC #.bank(JnArtStart)
 stx JnPose
 lda #<JN_FIRST_CHR
 sta SmChrBank
 sta PlayerChrBank
 lda PlayerFacingDir
 cmp #2
 jeq Left
 lda JnBodyRLo,x
 sta SmPosePtr
 lda JnBodyRHi,x
 jmp Ptr
Left:lda JnBodyLLo,x
 sta SmPosePtr
 lda JnBodyLHi,x
Ptr:sta SmPosePtr+1
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 lda SmChrBank
 ldx #>JN_FIRST_CHR
 ldy #0
 farcall X5SetPhysicalChr,jmp
.endproc
.popseg
