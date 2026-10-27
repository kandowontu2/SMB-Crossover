; Expanded MMC5 title-only sound browser. No gameplay RAM allocation.
; The native platform draw buffer is inactive on this page and is invalidated
; before entering/leaving. Audio never uses the shared foreground farcall SMC.
SoundTestVariantActive=HpDrawBuffer+11
SoundTestSavedVariantLo=HpDrawBuffer+12
SoundTestSavedVariantHi=HpDrawBuffer+13
SoundTestSavedVariantValue=HpDrawBuffer+14
SoundTestHero=HpDrawBuffer+15
SoundTestKind=HpDrawBuffer+16
SoundTestIndex=HpDrawBuffer+17
SoundTestPlaying=HpDrawBuffer+18
SoundTestCommand=HpDrawBuffer+19
SoundTestCueKind=HpDrawBuffer+20
SoundTestCueValue=HpDrawBuffer+21
SoundTestReserved=HpDrawBuffer+22
.export SoundTestHero,SoundTestKind,SoundTestIndex,SoundTestPlaying,SoundTestCommand
.pushseg
.segment "X5_MENU_UI"

.proc SoundTestEnter
 lda #0
 sta HpValid
 ldx #11
Clear:
 sta SoundTestVariantActive,x
 dex
 bpl Clear
 lda #7
 sta CrossoverMenuState
 lda #1
 sta DisableScreenFlag
 rts
.endproc

.proc SoundTestInput
 lda CrossoverMenuPressed
 and #B_Button
 beq Navigate
 lda #0
 sta SoundTestPlaying
 sta SoundTestCommand
 sta HpValid
 jsr SoundTestRestoreVariant
 jsr SoundTestReset
 lda #3
 sta CrossoverOptionsFocus
 sta CrossoverMenuState
 lda #1
 sta DisableScreenFlag
 rts
Navigate:
 lda CrossoverMenuPressed
 and #Up_Dir|Down_Dir
 beq Category
 ldx SoundTestHero
 and #Up_Dir
 beq NextHero
 dex
 bpl HeroReady
 ldx #SoundTestHeroCount-1
 bne HeroReady
NextHero:
 inx
 cpx #SoundTestHeroCount
 bcc HeroReady
 ldx #0
HeroReady:
 stx SoundTestHero
 lda #0
 sta SoundTestIndex
 jmp Stop
Category:
 lda CrossoverMenuPressed
 and #Select_Button
 beq Track
 lda SoundTestKind
 eor #1
 sta SoundTestKind
 lda #0
 sta SoundTestIndex
 jmp Stop
Track:
 lda CrossoverMenuPressed
 and #Left_Dir|Right_Dir
 beq Playback
 jsr Count
 stx R2
 ldx SoundTestIndex
 lda CrossoverMenuPressed
 and #Left_Dir
 beq NextTrack
 dex
 bpl TrackReady
 ldx R2
 dex
 bpl TrackReady
NextTrack:
 inx
 cpx R2
 bcc TrackReady
 ldx #0
TrackReady:
 stx SoundTestIndex
 jmp Stop
Playback:
 lda CrossoverMenuPressed
 and #Start_Button
 jne Stop
 lda CrossoverMenuPressed
 and #A_Button
 jeq Done
 lda #0
 sta SoundTestPlaying
 sta SoundTestCommand
 jsr SoundTestRestoreVariant
 jsr SoundTestReset
 ldx SoundTestHero
 lda SoundTestHeroIds,x
 sta SoundTestReserved
 lda SoundTestVariantHi,x
 beq VariantReady
 sta SoundTestSavedVariantHi
 sta R1
 lda SoundTestVariantLo,x
 sta SoundTestSavedVariantLo
 sta R0
 ldy #0
 lda (R0),y
 sta SoundTestSavedVariantValue
 lda SoundTestVariantValue,x
 sta (R0),y
 lda #1
 sta SoundTestVariantActive
VariantReady:
 lda SoundTestKind
 beq MusicCue
 cmp #1
 bne MusicCue
 lda SoundTestReserved
 cmp #CHARACTER_PIT
 bcc EffectCue
 cmp #CHARACTER_BASS
 beq EffectCue
 cmp #CHARACTER_RYU
 beq EffectCue
 cmp #CHARACTER_SOPHIA
 beq EffectCue
 lda #CHARACTER_PIT
 sta SoundTestReserved
EffectCue:
 lda SelectedCharacter
 pha
 lda SoundTestReserved
 sta SelectedCharacter
 farcall GuestAudioBegin
 pla
 sta SelectedCharacter
 jsr SoundTestEffectPointer
 ldy #0
 lda (R0),y
 sta SoundTestCueKind
 iny
 lda (R0),y
 sta SoundTestCueValue
 jsr SoundTestCue
 jmp Play
MusicCue:
 ldx SoundTestIndex
 lda SoundTestMusicBits,x
 sta SoundTestCueValue
Play:
 lda #1
 sta SoundTestPlaying
 sta SoundTestCommand
 jmp Changed
Stop:
 lda #0
 sta SoundTestPlaying
 sta SoundTestCommand
 jsr SoundTestRestoreVariant
 lda #2
 sta SoundTestCommand
Changed:
 jmp SoundTestQueue
Done:
 rts
Count:
 ldx #SoundTestMusicCount
 lda SoundTestKind
 beq Counted
 ldx SoundTestHero
 lda SoundTestSfxCounts,x
 tax
Counted:rts
.endproc

.proc SoundTestRestoreVariant
 lda SoundTestVariantActive
 beq Done
 lda SoundTestSavedVariantLo
 sta R0
 lda SoundTestSavedVariantHi
 sta R1
 ldy #0
 lda SoundTestSavedVariantValue
 sta (R0),y
 lda #0
 sta SoundTestVariantActive
Done:rts
.endproc

.proc SoundTestBuildPage
 lda PPUSTATUS
 lda #$20
 sta PPUADDR
 lda #0
 sta PPUADDR
 lda #$24
 ldx #4
 ldy #0
Blank:
 sta PPUDATA
 iny
 bne Blank
 dex
 bne Blank
 lda #$23
 sta PPUADDR
 lda #$c0
 sta PPUADDR
 lda #$aa
 ldx #64
Attributes:
 sta PPUDATA
 dex
 bne Attributes
 ldy #0
Next:
 lda Text,y
 beq Done
 sta PPUADDR
 iny
 lda Text,y
 sta PPUADDR
 iny
 lda Text,y
 tax
 iny
Copy:
 lda Text,y
 sta PPUDATA
 iny
 dex
 bne Copy
 beq Next
Done:rts
Text:
 .byte $20,$8b,T0End-T0
T0:.byte "SOUND TEST"
T0End:
 .byte $21,$05,T1End-T1
T1:.byte "CHARACTER"
T1End:
 .byte $21,$e5,T2End-T2
T2:.byte "TRACK"
T2End:
 .byte $22,$85,T3End-T3
T3:.byte "STATUS - "
T3End:
 .byte $22,$e3,H0End-H0
H0:.byte "UP DOWN - CHARACTER"
H0End:
 .byte $23,$03,H1End-H1
H1:.byte "LEFT RIGHT - TRACK"
H1End:
 .byte $23,$23,H2End-H2
H2:.byte "SELECT - MUSIC OR SFX"
H2End:
 .byte $23,$43,H3End-H3
H3:.byte "A - PLAY  START - STOP"
H3End:
 .byte $23,$63,H4End-H4
H4:.byte "B - OPTIONS"
H4End:
 .byte 0
 .assert *-Text<256,error,"Sound test static text uses one Y page"
.endproc

.proc SoundTestQueue
 ldx SoundTestHero
 lda SoundTestNameLo,x
 sta R0
 lda SoundTestNameHi,x
 sta R1
 lda #22
 sta R2
 lda #$21
 sta R3
 lda #$45
 sta R4
 jsr Line
 lda #<MusicType
 sta R0
 lda #>MusicType
 sta R1
 lda SoundTestKind
 beq TypeReady
 lda #<SfxType
 sta R0
 lda #>SfxType
 sta R1
TypeReady:
 lda #12
 sta R2
 lda #$a5
 sta R4
 jsr Line
 lda SoundTestKind
 bne EffectName
 lda #<SoundTestMusicNames
 sta R0
 lda #>SoundTestMusicNames
 sta R1
 ldx SoundTestIndex
MusicOffset:
 cpx #0
 beq NameReady
 clc
 lda R0
 adc #24
 sta R0
 bcc :+
 inc R1
:
 dex
 bne MusicOffset
 beq NameReady
EffectName:
 jsr SoundTestEffectPointer
 clc
 lda R0
 adc #2
 sta R0
 bcc NameReady
 inc R1
NameReady:
 lda #24
 sta R2
 lda #$22
 sta R3
 lda #$24
 sta R4
 jsr Line
 lda #<Stopped
 sta R0
 lda #>Stopped
 sta R1
 lda SoundTestPlaying
 beq StatusReady
 lda #<Playing
 sta R0
 lda #>Playing
 sta R1
StatusReady:
 lda #8
 sta R2
 lda #$8e
 sta R4
 jmp Line
Line:
 ldx VRAM_Buffer1_Offset
 lda R3
 sta VRAM_Buffer1,x
 lda R4
 sta VRAM_Buffer1+1,x
 lda R2
 sta VRAM_Buffer1+2,x
 ldy #0
Bytes:
 lda (R0),y
 sta VRAM_Buffer1+3,x
 inx
 iny
 cpy R2
 bne Bytes
 inx
 inx
 inx
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 rts
MusicType:.byte "TYPE - MUSIC"
SfxType:  .byte "TYPE - SFX  "
Stopped:  .byte "STOPPED "
Playing:  .byte "PLAYING "
.endproc

.proc SoundTestEffectPointer
 ldx SoundTestHero
 lda SoundTestCommonCounts,x
 sta R2
 lda SoundTestIndex
 cmp R2
 bcs Native
 lda SoundTestCommonLo,x
 sta R0
 lda SoundTestCommonHi,x
 sta R1
 ldx SoundTestIndex
 jmp Offset
Native:
 sec
 sbc R2
 pha
 lda SoundTestSfxLo,x
 sta R0
 lda SoundTestSfxHi,x
 sta R1
 pla
 tax
Offset:
 cpx #0
 beq Done
 clc
 lda R0
 adc #26
 sta R0
 bcc :+
 inc R1
:
 dex
 jmp Offset
Done:rts
.endproc

; The original vanilla playback call already owns music bank5 and preserves
; its caller's A mapping. Append in its unused tail; preserve every old song
; address and the original gameplay SoundEngine entry/branch span.
.segment "MUSIC"
.proc SoundTestAudioGate
 lda CrossoverMenuState
 cmp #8
 beq SoundTestAudioTick
 lda #0
 sta SND_MASTERCTRL_REG
 rts
.endproc

; Normal AudioUpdate restores bank5 before returning. NMI uses this direct
; route and never changes the main thread's five live farcall SMC operands.
.proc SoundTestAudioTick
 lda #.bank(SoundTestAudioTick)|MMC5_PRG_ROM
 sta CurrentBank
 lda OperMode
 pha
 lda SelectedCharacter
 pha
 lda GamePauseStatus
 pha
 lda PlayerStatus
 pha
 lda Player_State
 pha
 lda GameEngineSubroutine
 pha
 lda MmDeathFlag
 pha
 lda MmChargeFrames
 pha
 lda #1
 sta OperMode
 sta Player_State
 lda #0
 sta GamePauseStatus
 sta PlayerStatus
 sta GameEngineSubroutine
 sta MmDeathFlag
 sta MmChargeFrames
 ldx SoundTestHero
 lda SoundTestReserved
 sta SelectedCharacter
 lda SoundTestCommand
 beq Continue
 cmp #3
 beq SendEvent
 cmp #1
 bne Stopped
 lda SoundTestKind
 bne Continue
 ldx SoundTestIndex
 lda SoundTestCueValue
 cpx #7
 bcs PrimeEvent
 sta AreaMusicQueue
 jmp Continue
PrimeEvent:
 lda #GroundMusic
 sta AreaMusicQueue
 lda #3
 sta SoundTestCommand
 jmp Tick
SendEvent:
 lda SoundTestCueValue
 sta EventMusicQueue
Continue:
 lda SoundTestPlaying
 beq Stopped
 lda SoundTestKind
 beq Update
 lda SoundTestCueKind
 cmp #8
 bne :+
 lda SoundTestCueValue
 sta PlayerStatus
:
 ; The UI selected the exact shared SFX family for common-only heroes.
 lda SelectedCharacter
 cmp #CHARACTER_PIT
 bcc Update
 sta XgAudioCharacter
 lda #3
 sta XgAudioEvent
Update:
 lda #0
 sta SoundTestCommand
Tick:
 jsr AudioUpdate
 jmp Restore
Stopped:
 lda #0
 sta SoundTestCommand
 sta $4015
 sta $5015
 sta $4011
Restore:
 pla
 sta MmChargeFrames
 pla
 sta MmDeathFlag
 pla
 sta GameEngineSubroutine
 pla
 sta Player_State
 pla
 sta PlayerStatus
 pla
 sta GamePauseStatus
 pla
 sta SelectedCharacter
 pla
 sta OperMode
 rts
.endproc

.assert * <= $c000,error,"Sound audio wrapper exceeds bank5 tail"
.segment "X5_MENU_UI"
.proc SoundTestReset
 lda #0
 sta $4015
 sta $5015
 sta $4011
 sta AreaMusicQueue
 sta EventMusicQueue
 sta Square1SoundQueue
 sta Square2SoundQueue
 sta NoiseSoundQueue
 sta PauseSoundQueue
 sta GuestMixMask
 sta GuestMixPreviousMask
 sta GuestNativeEnable
 sta GuestCombinedEnable
 sta BassDmcActive
 sta BassSourceId
 sta BassSourcePriority
 sta BassSourceKill
 sta BassAudioPreviousMask
 sta BassAudioLastDeath
 sta BassAudioLastGround
 sta AvAudioId
 sta AvAudioMask
 sta AvAudioOldMask
 sta AvAudioRequest
 sta SsAudioRequest
 sta SmSfx
 sta RgSfx
 sta ProtoAudioState
 ldx #15
ClearImages:
 sta GuestNativeApu,x
 sta GuestFxApu,x
 sta XgMusicApu,x
 sta GuestNativeDirty,x
 sta GuestFxDirty,x
 dex
 bpl ClearImages
 ldx #0
ClearRoster:
 sta RgAudioRam,x
 sta RgAudioRam+$100,x
 inx
 bne ClearRoster
 ldx #159
ClearZp:
 sta RgAudioZp,x
 dex
 bpl ClearZp
 jsr AudioInit
 jsr MegaManAudioInit
 jsr SamusAudioInit
 lda #0
 sta MmAudioCurrentSong
 sta MmAudioDesiredSong
 lda #$ff
 sta GuestAudioCharacter
 sta RgAudioCharacter
 sta XgAudioCharacter
 sta BassAudioRequest
 ldx #15
Invalidate:
 sta GuestApuLast,x
 dex
 bpl Invalidate
 ldx #7
InvalidateExpansion:
 sta GuestExpansionLast,x
 dex
 bpl InvalidateExpansion
 rts
.endproc

.proc SoundTestCue
 ldx SoundTestCueKind
 lda SoundTestCueValue
 cpx #1
 beq Square1
 cpx #2
 beq Square2
 cpx #3
 beq Noise
 cpx #4
 beq Typed
 cpx #5
 beq Robot
 cpx #6
 beq Metroid
 cpx #9
 beq Cv3
 ; The primary source wrappers consume their ordinary, real shot requests.
 lda #1
 sta RgSfx
 lda #Sfx_Fireball
Square1:sta Square1SoundQueue
 rts
Square2:sta Square2SoundQueue
 rts
Noise:sta NoiseSoundQueue
 rts
Typed:sta AvAudioRequest
 ldx SoundTestHero
 lda SoundTestHeroIds,x
 sta AvAudioChar
 rts
Robot:sta SsAudioRequest
 rts
Metroid:sta SmSfx
 rts
Cv3:ldy Cv3FxQueueHead
 sta Cv3FxQueue,y
 inc Cv3FxQueueHead
 rts
.endproc

.include "sound_test_tables.inc"
.assert * <= $c000,error,"Sound browser exceeds its existing bank99 A-window tail"
.popseg
