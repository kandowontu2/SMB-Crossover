; Complete source13/15/24/21/1E/2F plus retained source1F.
; Same selected-family160B slab;0..35 keep all existing owners.
Cv3FxNoiseID=RgAudioZp+36
Cv3FxPulseID=RgAudioZp+37
Cv3FxOwned=RgAudioZp+38 ;1pulse,8noise,64promote legacy1F,128new request
Cv3FxPulseFrame=RgAudioZp+39
Cv3FxPulseApu=RgAudioZp+40
Cv3FxPulseMusic=RgAudioZp+44
Cv3FxNoisePtr=RgAudioZp+48
Cv3FxPulsePtr=RgAudioZp+50
Cv3FxSavedA=RgAudioZp+52
Cv3FxPendingNoise=RgAudioZp+53 ; independent same-update source requests
Cv3FxPendingPulse=RgAudioZp+54
Cv3FxSourceHigh=RgAudioZp+55 ; original shared source frequency-high image
; Main is the sole head/slot producer; NMI is the sole tail consumer.
; Counters and physical slot indexes are full bytes. Neither reset nor
; an interrupted NMI rewrites producer head. Tail=head discards a cold epoch.
Cv3FxQueueHead=RgAudioZp+56
Cv3FxQueueTail=RgAudioZp+57
Cv3FxQueueOverflow=RgAudioZp+58 ; impossible in the bounded gameplay producer graph
Cv3FxQueue=RgAudioRam+$100 ;256 physical slots, logical capacity64; CV1 upper RAM unused
.pushseg
.segment "CV_AUDIO"
.proc Cv3FxTick
 jsr Cv3DmcBeforeCv1
 lda Cv3FxQueueHead
 cmp Cv3FxQueueTail
 beq Empty
 jsr Cv3FxDrainGate
Empty:lda Cv3NoiseActive
 bmi Steady
 bne Legacy
 lda Cv3FxOwned
 bne Full
 lda AvAudioRequest
 cmp #26
 beq Legacy
 lda #0 ; match old final active load/register flags for ordinary requests
 rts
Legacy:jmp Cv3MusicAndNoiseTick+3 ; unchanged executable legacy body
Full:jmp Cv3FxResidentDispatch
Steady:jmp Cv3FxSteadyTry
 .res 67-(*-::Cv3FxTick),$ea
.endproc
.proc Cv3FxMusicInit
 php
 pha
 lda Cv3NoiseActive
 cmp #1
 bne Cancel ; only genuine legacy1F needs conversion into an owned noise image
 lda Cv3FxOwned
 ora #8
 sta Cv3FxOwned
 lda #$80
 sta Cv3NoiseActive
Cancel:lda Cv3FxQueueHead
 sta Cv3FxQueueTail
 lda #0
 sta Cv3FxNoiseID
 sta Cv3FxPulseID
 sta Cv3FxPendingNoise
 sta Cv3FxPendingPulse
 sta Cv3FxSourceHigh
 jsr Cv3FxClearTyped
Done:pla
 plp
 jmp CvAudioInit
 .res 66-(*-::Cv3FxMusicInit),$ea
.endproc
.proc Cv3FxLegacyNoiseHigh
 lda Cv3FxSourceHigh
 ora #8
 sta Cv3NoiseApu+3
 rts
.endproc

; C28 resident steady source21/1E. The real generic owner handles admission,
; mixed pulse/noise, priority, release and every non-steady state.
.proc Cv3FxResidentDispatch
 php
 pha
 tya
 pha
 lda CurrentBank
 sta Cv3FxSavedA
 lda Cv3FxOwned
 cmp #8
 bne Generic
 lda Cv3FxNoiseID
 beq Generic
 cmp #$21
 beq Pending
 cmp #$1e
 bne Generic
Pending:lda AvAudioRequest
 bne Generic
 lda Cv3FxPendingNoise
 ora Cv3FxPendingPulse
 bne Generic
 jsr Cv3FxResidentNoise
 jmp Restore
Generic:txa ; resident-only work never touches X, so only the fallback saves it
 pha
 lda #.bank(Cv3FxService)|MMC5_PRG_ROM
 sta CurrentBank
 sta $5115
 jsr Cv3FxService
 lda Cv3FxSavedA
 sta CurrentBank
 sta $5115
 pla
 tax
Restore:pla
 tay
 pla
 plp
 rts
.endproc
.proc Cv3FxResidentNoise
 ; Genuine old callable entry/span: pure body plus original normalization.
 jsr Cv3FxResidentBody
 lda #$80
 sta Cv3NoiseActive
 rts
 ; Sole private entry is Tick's BMI path. A is the negative Active byte.
 ; P is saved before checks; a non80 value falls back with exact originalA/P.
::Cv3FxSteadyTry:
 php
 cmp #$80
 bne Slow
 lda Cv3FxOwned
 cmp #8
 bne Slow
 lda Cv3FxNoiseID
 cmp #$21
 beq Pending
 cmp #$1e
 bne Slow
Pending:lda AvAudioRequest
 ora Cv3FxPendingNoise
 ora Cv3FxPendingPulse
 bne Slow
 ; SavedA is dead bank-cache scratch on this C28-only path. Generic always
 ; dominates its bank-restore read with its own CurrentBank write.
 sty Cv3FxSavedA
 jsr Cv3FxResidentBody
 ldy Cv3FxSavedA
 lda #$80 ; inputA proven80; Active remains80; V/C/DI restored byPLP
 plp
 rts
Slow:lda Cv3NoiseActive
 pha
 tya
 pha
 lda CurrentBank
 sta Cv3FxSavedA
 jmp Cv3FxResidentDispatch::Generic
 ; Genuine sole roster-wrapper caller, in the original unreachable tail.
 ; Original public Tick compatibility entry remains byte-exact.
::Cv3FxNativeTick:
 lda Cv3DmcPending
 ora Cv3DmcPriority
 bne NativeDmcWork
 jsr CvAudioPlay ; its first LDA overwrites A/NZ, all other flags unchanged
NativePlayed:
 lda Cv3FxQueueHead
 cmp Cv3FxQueueTail
 beq NativeEmpty
 jsr Cv3FxDrainGate
NativeEmpty:lda Cv3NoiseActive
 beq NativeInactive
 bmi NativeSteady
 jmp Cv3MusicAndNoiseTick::KnownActive
NativeInactive:lda Cv3FxOwned
 bne NativeFull
 lda AvAudioRequest
 cmp #26
 beq NativeLegacyCold
 lda #0
 rts
NativeLegacyCold:jmp Cv3MusicAndNoiseTick+3
NativeFull:jmp Cv3FxResidentDispatch
NativeSteady:jmp Cv3FxSteadyTry
NativeDmcWork:
 jsr Cv3DmcBeforeCv1::Work ; identical nonzero guard already executed
 jmp NativePlayed
 .assert *-::Cv3FxResidentNoise<=149,error,"Old genuine callable span"
 .res 149-(*-::Cv3FxResidentNoise),$ea
.endproc
Cv3FxResidentVolume:.byte 56,56,56,56,56,56,56,56,56,56,48,52,52,52,52,52,52,52,52,52,52,48,50,50,50,50,50,50,50,50,50,50,48,49,49,49,49,49,49,49,49,49,48
Cv3FxResidentPeriod:.byte 15,13,15,10,9,8,7,6,5,4,0,13,12,11,10,9,8,7,6,5,4,0,13,12,11,10,9,8,7,6,5,4,0,13,12,11,10,9,8,7,6,4
.assert *<=$dc00,lderror,"Only recorded original CV1 C28 slack"
.segment "X5_AUDIO_MIX"
.proc Cv3FxOwnerInit
 sta Cv3DmcPending
 lda SelectedCharacter
 cmp #CHARACTER_SIMON
 bne Clear
 lda GamePauseStatus
 and OperMode
 and #1
 bne Done
Clear:lda #0
 sta Cv3NoiseActive
 sta Cv3FxOwned
 sta Cv3FxSourceHigh
 lda Cv3FxQueueHead
 sta Cv3FxQueueTail
Done:rts
 .assert *-::Cv3FxOwnerInit<=38,error,"Retained original callable span"
 .res 38-(*-::Cv3FxOwnerInit),$ea
.endproc
.assert *<=$c000,lderror,"Only remaining38B X5 mixer tail"
.segment "CV3_COMBAT"
.proc Cv3FxSpawn
 sta Cv3ShotType,x
 php
 pha
 tya
 pha
 lda Cv3ShotType,x
 jsr Cv3FxProducer
 pla
 tay
 pla
 plp
 rts
 .assert *-::Cv3FxSpawn<=191,error,"Retained original callable span"
 .res 191-(*-::Cv3FxSpawn),$ea
.endproc
Cv3FxQueueIDs:.byte $1f,$13,$15,$24,$21,$1e,$2f
Cv3FxQueueMasks:.byte 8,8,8,9,9,9,9
.segment "CV3_GRIP"
.proc Cv3FxBatEnter
 php
 tya
 pha
 lda #7
 jsr Cv3FxQueueCommand
 pla
 tay
 plp
 lda #1
 sta Cv3Bat
 rts
 .assert *-::Cv3FxBatEnter<=61,error,"Retained original callable span"
 .res 61-(*-::Cv3FxBatEnter),$ea
.endproc
.proc Cv3FxSceneRequest
 php ; real original Cv3DmcSceneRequest PHP displaced into this prelude
 jsr Cv3FxCancel
 lda #0
 jmp Cv3DmcSceneRequest+3 ; original STA pending and original remaining body
.endproc
.proc Cv3FxCancel
 tya
 pha
 lda #8
 jsr Cv3FxQueueCommand
 pla
 tay
 rts
 .assert *-::Cv3FxCancel<=57,error,"Retained original callable span"
 .res 57-(*-::Cv3FxCancel),$ea
.endproc
.proc Cv3FxDeathDispatch
 php
 pha
 txa
 pha
 tya
 pha
 lda SelectedCharacter
 cmp #CHARACTER_SIMON
 bne Done
 lda Cv3Variant
 beq Done
 cmp #4
 jcs Done
 jsr Cv3FxCancel
Done:pla
 tay
 pla
 tax
 pla
 plp
 farcall RlDeathStartDispatch,jmp
.endproc
.proc Cv3FxService
 lda R0
 pha
 lda R1
 pha
 ; The source update has already run. Capture only its genuinely dirty
 ; owned registers, suppress them in the current FX image, and keep music
 ; advancing at its original cadence underneath each independently owned voice.
 lda Cv3FxOwned
 and #$40
 beq Capture
 ldy Cv3NoiseIndex
 lda Cv3FxLegacyOffsets,y
 clc
 adc #<Cv3Fx1FNoise
 sta Cv3FxNoisePtr
 lda #>Cv3Fx1FNoise
 adc #0
 sta Cv3FxNoisePtr+1
Capture:lda Cv3FxOwned
 and #8
 beq PulseCapture
 lda GuestNativeDirty+12
 beq NC12
 lda GuestNativeApu+12
 sta Cv3NoiseMusicVolume
 lda Cv3NoiseApu
 sta GuestNativeApu+12
 lda #0
 sta GuestNativeDirty+12
NC12:
 lda GuestNativeDirty+14
 beq NC14
 lda GuestNativeApu+14
 sta Cv3NoiseMusicPeriod
 lda Cv3NoiseApu+2
 sta GuestNativeApu+14
 lda #0
 sta GuestNativeDirty+14
NC14:
 lda GuestNativeDirty+15
 beq NC15
 lda GuestNativeApu+15
 sta Cv3NoiseMusicHigh
 lda Cv3NoiseApu+3
 sta GuestNativeApu+15
 lda #0
 sta GuestNativeDirty+15
NC15:
PulseCapture:lda Cv3FxOwned
 and #1
 beq Admit
 lda GuestNativeDirty+0
 beq PC0
 lda GuestNativeApu+0
 sta Cv3FxPulseMusic+0
 lda Cv3FxPulseApu+0
 sta GuestNativeApu+0
 lda #0
 sta GuestNativeDirty+0
PC0:
 lda GuestNativeDirty+1
 beq PC1
 lda GuestNativeApu+1
 sta Cv3FxPulseMusic+1
 lda Cv3FxPulseApu+1
 sta GuestNativeApu+1
 lda #0
 sta GuestNativeDirty+1
PC1:
 lda GuestNativeDirty+2
 beq PC2
 lda GuestNativeApu+2
 sta Cv3FxPulseMusic+2
 lda Cv3FxPulseApu+2
 sta GuestNativeApu+2
 lda #0
 sta GuestNativeDirty+2
PC2:
 lda GuestNativeDirty+3
 beq PC3
 lda GuestNativeApu+3
 sta Cv3FxPulseMusic+3
 lda Cv3FxPulseApu+3
 sta GuestNativeApu+3
 lda #0
 sta GuestNativeDirty+3
PC3:
Admit:lda Cv3FxOwned
 and #9
 sta Cv3FxOwned
 lda AvAudioRequest
 cmp #26
 bcc Pending
 cmp #33
 bcs Pending
 sec
 sbc #26
 tay
 lda Cv3FxPendingNoise
 ora Cv3FxPendingPulse
 bne ClearRequest
 lda Cv3FxMasks,y
 and #8
 beq SeedPulse
 lda Cv3FxIDs,y
 sta Cv3FxPendingNoise
SeedPulse:lda Cv3FxMasks,y
 and #1
 beq ClearRequest
 lda Cv3FxIDs,y
 sta Cv3FxPendingPulse
ClearRequest:
 lda #0
 sta AvAudioRequest
Pending:lda Cv3FxPendingNoise
 beq PulseAlreadyClear
 cmp Cv3FxNoiseID
 bcc PulseAdmission
 jsr FindIndex
 lda Cv3FxOwned
 and #8
 bne NewNoise
 lda GuestNativeApu+12
 sta Cv3NoiseMusicVolume
 lda GuestNativeApu+14
 sta Cv3NoiseMusicPeriod
 lda GuestNativeApu+15
 sta Cv3NoiseMusicHigh
NewNoise:lda Cv3FxPendingNoise
 sta Cv3FxNoiseID
 lda Cv3FxNoiseLo,y
 sta Cv3FxNoisePtr
 lda Cv3FxNoiseHi,y
 sta Cv3FxNoisePtr+1
 lda #0
 sta Cv3NoiseIndex
 lda Cv3FxOwned
 ora #8
 sta Cv3FxOwned
PulseAdmission:lda #0
 sta Cv3FxPendingNoise
PulseAlreadyClear:lda Cv3FxPendingPulse
 beq Pulse
 cmp Cv3FxPulseID
 bcc Noise
 jsr FindIndex
 lda Cv3FxOwned
 and #1
 bne NewPulse
 ldx #3
PM:lda GuestNativeApu,x
 sta Cv3FxPulseMusic,x
 dex
 bpl PM
NewPulse:lda Cv3FxPendingPulse
 sta Cv3FxPulseID
 lda Cv3FxPulseLo,y
 sta Cv3FxPulsePtr
 lda Cv3FxPulseHi,y
 sta Cv3FxPulsePtr+1
 lda #0
 sta Cv3FxPulseFrame
 lda Cv3FxOwned
 ora #1
 sta Cv3FxOwned
Noise:lda #0
 sta Cv3FxPendingPulse
Pulse:lda Cv3FxOwned
 and #1
 beq NoiseTick
 lda Cv3FxPulseID
 beq PulseRelease
 lda Cv3FxPulsePtr
 sta R0
 lda Cv3FxPulsePtr+1
 sta R1
 jsr Decode
 lda R0
 sta Cv3FxPulsePtr
 lda R1
 sta Cv3FxPulsePtr+1
 inc Cv3FxPulseFrame
 ldy #0
 lda (R0),y
 cmp #255
 bne NoiseTick
 lda #0
 sta Cv3FxPulseID
 beq NoiseTick
PulseRelease:ldx #3
PR:lda Cv3FxPulseMusic,x
 sta GuestNativeApu,x
 lda #1
 sta GuestNativeDirty,x
 dex
 bpl PR
 lda Cv3FxOwned
 and #$fe
 sta Cv3FxOwned
NoiseTick:lda Cv3FxOwned
 and #8
 beq Done
 lda Cv3FxNoiseID
 beq NoiseRelease
 lda Cv3FxNoisePtr
 sta R0
 lda Cv3FxNoisePtr+1
 sta R1
 jsr Decode
 lda R0
 sta Cv3FxNoisePtr
 lda R1
 sta Cv3FxNoisePtr+1
 inc Cv3NoiseIndex
 ldy #0
 lda (R0),y
 cmp #255
 bne NoiseRunning
 lda #0
 sta Cv3FxNoiseID ; original priority clears on the final silence frame
NoiseRunning:lda #$80
Done:sta Cv3NoiseActive
Return:pla
 sta R1
 pla
 sta R0
 rts
NoiseRelease:lda Cv3NoiseMusicVolume
 sta GuestNativeApu+12
 lda Cv3NoiseMusicPeriod
 sta GuestNativeApu+14
 lda Cv3NoiseMusicHigh
 sta GuestNativeApu+15
 lda #1
 sta GuestNativeDirty+12
 sta GuestNativeDirty+14
 sta GuestNativeDirty+15
 lda Cv3FxOwned
 and #$f7
 sta Cv3FxOwned
 lda #0
 jmp Done
 .assert *-::Cv3FxService<=598,error,"Original helper boundary"
 .res 598-(*-::Cv3FxService),$ea
FindIndex:ldy #6
Find:cmp Cv3FxIDs,y
 beq Found
 dey
 bpl Find
Found:rts
Decode:jmp (R0) ; every target is a genuine mappedA82 source-frame stub
Read:jsr Peek
 inc R0
 bne ByteDone
 inc R1
ByteDone:rts
Peek:ldy #0
 lda (R0),y
 rts
.endproc
Cv3FxIDs:.byte $1f,$13,$15,$24,$21,$1e,$2f
Cv3FxMasks:.byte 8,8,8,9,9,9,9

; Native frame packets keep original C/F/E or pulse source image-store order.
; Only a currently owned frame dispatches here; outer Cv3FxTick preserves AXY/P.
; Existing R0/R1 borrow is restored by Cv3FxService on every return.
.proc Cv3FxFrameNoiseFull
 sta GuestNativeApu+12
 sta Cv3NoiseApu
 lda #1
 sta GuestNativeDirty+12
 lda Cv3FxSourceHigh
 ora #8
 sta GuestNativeApu+15
 sta Cv3NoiseApu+3
 lda #1
 sta GuestNativeDirty+15
 txa
 sta GuestNativeApu+14
 sta Cv3NoiseApu+2
 lda #1
 sta GuestNativeDirty+14
 ldy #7
 jmp Cv3FxFrameAdvance
.endproc
.proc Cv3FxFrameNoiseVolume
 sta GuestNativeApu+12
 sta Cv3NoiseApu
 lda #1
 sta GuestNativeDirty+12
 ldy #5
 jmp Cv3FxFrameAdvance
.endproc
.proc Cv3FxFramePulseFull
 sta GuestNativeApu
 sta Cv3FxPulseApu
 lda #1
 sta GuestNativeDirty
 tya
 sta GuestNativeApu+3
 sta Cv3FxPulseApu+3
 and #7
 sta Cv3FxSourceHigh
 lda #1
 sta GuestNativeDirty+3
 txa
 sta GuestNativeApu+2
 sta Cv3FxPulseApu+2
 lda #1
 sta GuestNativeDirty+2
 ldy #9
 jmp Cv3FxFrameAdvance
.endproc
.proc Cv3FxFramePulseVolumePeriod
 sta GuestNativeApu
 sta Cv3FxPulseApu
 lda #1
 sta GuestNativeDirty
 txa
 sta GuestNativeApu+2
 sta Cv3FxPulseApu+2
 lda #1
 sta GuestNativeDirty+2
 ldy #7
 jmp Cv3FxFrameAdvance
.endproc
.proc Cv3FxFramePulseVolumeSweep
 sta GuestNativeApu
 sta Cv3FxPulseApu
 lda #1
 sta GuestNativeDirty
 lda #127
 sta GuestNativeApu+1
 sta Cv3FxPulseApu+1
 lda #1
 sta GuestNativeDirty+1
 ldy #5
 jmp Cv3FxFrameAdvance
.endproc
.proc Cv3FxFramePulseSweepFull
 pha
 lda #127
 sta GuestNativeApu+1
 sta Cv3FxPulseApu+1
 lda #1
 sta GuestNativeDirty+1
 pla
 jmp Cv3FxFramePulseFull
.endproc
.proc Cv3FxFramePulseSweepVolumePeriod
 pha
 lda #127
 sta GuestNativeApu+1
 sta Cv3FxPulseApu+1
 lda #1
 sta GuestNativeDirty+1
 pla
 jmp Cv3FxFramePulseVolumePeriod
.endproc
; Quiet packets fall through to the shared pointer commit.
.proc Cv3FxFrameQuiet
 ldy #3
.endproc
.proc Cv3FxFrameAdvance
 tya
 clc
 adc R0
 sta R0
 bcc Done
 inc R1
Done:rts
.endproc
Cv3Fx1FNoise:
Cv3Fx1FNoiseFrame000:
 lda #57
 ldx #7
 jmp Cv3FxFrameNoiseFull
Cv3Fx1FNoiseFrame001:
 jmp Cv3FxFrameQuiet
Cv3Fx1FNoiseFrame002:
 jmp Cv3FxFrameQuiet
Cv3Fx1FNoiseFrame003:
 lda #48
 ldx #0
 jmp Cv3FxFrameNoiseFull
Cv3Fx1FNoiseFrame004:
 jmp Cv3FxFrameQuiet
Cv3Fx1FNoiseFrame005:
 jmp Cv3FxFrameQuiet
Cv3Fx1FNoiseFrame006:
 lda #57
 ldx #8
 jmp Cv3FxFrameNoiseFull
Cv3Fx1FNoiseFrame007:
 jmp Cv3FxFrameQuiet
Cv3Fx1FNoiseFrame008:
 jmp Cv3FxFrameQuiet
Cv3Fx1FNoiseFrame009:
 lda #53
 ldx #15
 jmp Cv3FxFrameNoiseFull
Cv3Fx1FNoiseFrame010:
 jmp Cv3FxFrameQuiet
Cv3Fx1FNoiseFrame011:
 jmp Cv3FxFrameQuiet
Cv3Fx1FNoiseFrame012:
 lda #52
 ldx #1
 jmp Cv3FxFrameNoiseFull
Cv3Fx1FNoiseFrame013:
 jmp Cv3FxFrameQuiet
Cv3Fx1FNoiseFrame014:
 jmp Cv3FxFrameQuiet
Cv3Fx1FNoiseFrame015:
 lda #51
 ldx #10
 jmp Cv3FxFrameNoiseFull
Cv3Fx1FNoiseFrame016:
 jmp Cv3FxFrameQuiet
Cv3Fx1FNoiseFrame017:
 jmp Cv3FxFrameQuiet
Cv3Fx1FNoiseFrame018:
 lda #50
 ldx #5
 jmp Cv3FxFrameNoiseFull
Cv3Fx1FNoiseFrame019:
 jmp Cv3FxFrameQuiet
Cv3Fx1FNoiseFrame020:
 jmp Cv3FxFrameQuiet
Cv3Fx1FNoiseFrame021:
 lda #49
 ldx #8
 jmp Cv3FxFrameNoiseFull
Cv3Fx1FNoiseFrame022:
 jmp Cv3FxFrameQuiet
Cv3Fx1FNoiseFrame023:
 jmp Cv3FxFrameQuiet
Cv3Fx1FNoiseFrame024:
 lda #49
 ldx #11
 jmp Cv3FxFrameNoiseFull
Cv3Fx1FNoiseFrame025:
 jmp Cv3FxFrameQuiet
Cv3Fx1FNoiseFrame026:
 jmp Cv3FxFrameQuiet
Cv3Fx1FNoiseFrame027:
 lda #48
 jmp Cv3FxFrameNoiseVolume
Cv3Fx1FNoiseEnd: .byte $ff
Cv3Fx13Noise:
Cv3Fx13NoiseFrame000:
 lda #52
 ldx #1
 jmp Cv3FxFrameNoiseFull
Cv3Fx13NoiseFrame001:
 lda #55
 ldx #3
 jmp Cv3FxFrameNoiseFull
Cv3Fx13NoiseFrame002:
 lda #59
 ldx #5
 jmp Cv3FxFrameNoiseFull
Cv3Fx13NoiseFrame003:
 lda #61
 ldx #7
 jmp Cv3FxFrameNoiseFull
Cv3Fx13NoiseFrame004:
 lda #51
 ldx #8
 jmp Cv3FxFrameNoiseFull
Cv3Fx13NoiseFrame005:
 jmp Cv3FxFrameQuiet
Cv3Fx13NoiseFrame006:
 lda #60
 ldx #6
 jmp Cv3FxFrameNoiseFull
Cv3Fx13NoiseFrame007:
 jmp Cv3FxFrameQuiet
Cv3Fx13NoiseFrame008:
 lda #50
 ldx #4
 jmp Cv3FxFrameNoiseFull
Cv3Fx13NoiseFrame009:
 jmp Cv3FxFrameQuiet
Cv3Fx13NoiseFrame010:
 lda #60
 ldx #2
 jmp Cv3FxFrameNoiseFull
Cv3Fx13NoiseFrame011:
 jmp Cv3FxFrameQuiet
Cv3Fx13NoiseFrame012:
 lda #48
 jmp Cv3FxFrameNoiseVolume
Cv3Fx13NoiseEnd: .byte $ff
Cv3Fx15Noise:
Cv3Fx15NoiseFrame000:
 lda #49
 ldx #1
 jmp Cv3FxFrameNoiseFull
Cv3Fx15NoiseFrame001:
 lda #51
 ldx #3
 jmp Cv3FxFrameNoiseFull
Cv3Fx15NoiseFrame002:
 lda #54
 ldx #5
 jmp Cv3FxFrameNoiseFull
Cv3Fx15NoiseFrame003:
 lda #57
 ldx #7
 jmp Cv3FxFrameNoiseFull
Cv3Fx15NoiseFrame004:
 lda #49
 ldx #8
 jmp Cv3FxFrameNoiseFull
Cv3Fx15NoiseFrame005:
 jmp Cv3FxFrameQuiet
Cv3Fx15NoiseFrame006:
 lda #58
 ldx #6
 jmp Cv3FxFrameNoiseFull
Cv3Fx15NoiseFrame007:
 jmp Cv3FxFrameQuiet
Cv3Fx15NoiseFrame008:
 lda #49
 ldx #4
 jmp Cv3FxFrameNoiseFull
Cv3Fx15NoiseFrame009:
 jmp Cv3FxFrameQuiet
Cv3Fx15NoiseFrame010:
 lda #58
 ldx #1
 jmp Cv3FxFrameNoiseFull
Cv3Fx15NoiseFrame011:
 jmp Cv3FxFrameQuiet
Cv3Fx15NoiseFrame012:
 lda #48
 ldx #0
 jmp Cv3FxFrameNoiseFull
Cv3Fx15NoiseFrame013:
 jmp Cv3FxFrameQuiet
Cv3Fx15NoiseFrame014:
 lda #48
 ldx #0
 jmp Cv3FxFrameNoiseFull
Cv3Fx15NoiseFrame015:
 jmp Cv3FxFrameQuiet
Cv3Fx15NoiseFrame016:
 lda #48
 jmp Cv3FxFrameNoiseVolume
Cv3Fx15NoiseEnd: .byte $ff
Cv3Fx24Noise:
Cv3Fx24NoiseFrame000:
 lda #48
 ldx #0
 jmp Cv3FxFrameNoiseFull
Cv3Fx24NoiseFrame001:
 lda #58
 ldx #6
 jmp Cv3FxFrameNoiseFull
Cv3Fx24NoiseFrame002:
 lda #59
 ldx #13
 jmp Cv3FxFrameNoiseFull
Cv3Fx24NoiseFrame003:
 lda #59
 ldx #14
 jmp Cv3FxFrameNoiseFull
Cv3Fx24NoiseFrame004:
 lda #59
 ldx #12
 jmp Cv3FxFrameNoiseFull
Cv3Fx24NoiseFrame005:
 lda #48
 jmp Cv3FxFrameNoiseVolume
Cv3Fx24NoiseEnd: .byte $ff
Cv3Fx24Pulse:
Cv3Fx24PulseFrame000:
 lda #187
 ldx #112
 ldy #10
 jmp Cv3FxFramePulseSweepFull
Cv3Fx24PulseFrame001:
 lda #181
 ldx #0
 ldy #11
 jmp Cv3FxFramePulseFull
Cv3Fx24PulseFrame002:
 lda #182
 ldx #0
 ldy #10
 jmp Cv3FxFramePulseFull
Cv3Fx24PulseFrame003:
 lda #183
 ldx #0
 ldy #11
 jmp Cv3FxFramePulseFull
Cv3Fx24PulseFrame004:
 lda #184
 ldx #128
 ldy #9
 jmp Cv3FxFramePulseFull
Cv3Fx24PulseFrame005:
 lda #177
 ldx #0
 ldy #8
 jmp Cv3FxFramePulseFull
Cv3Fx24PulseFrame006:
 lda #182
 ldx #160
 ldy #10
 jmp Cv3FxFramePulseFull
Cv3Fx24PulseFrame007:
 lda #184
 ldx #192
 ldy #9
 jmp Cv3FxFramePulseFull
Cv3Fx24PulseFrame008:
 lda #183
 ldx #26
 ldy #10
 jmp Cv3FxFramePulseFull
Cv3Fx24PulseFrame009:
 lda #184
 ldx #64
 jmp Cv3FxFramePulseVolumePeriod
Cv3Fx24PulseFrame010:
 lda #183
 ldx #106
 jmp Cv3FxFramePulseVolumePeriod
Cv3Fx24PulseFrame011:
 lda #182
 ldx #208
 jmp Cv3FxFramePulseVolumePeriod
Cv3Fx24PulseFrame012:
 lda #181
 ldx #0
 ldy #13
 jmp Cv3FxFramePulseFull
Cv3Fx24PulseFrame013:
 lda #180
 ldx #96
 ldy #14
 jmp Cv3FxFramePulseFull
Cv3Fx24PulseFrame014:
 lda #180
 ldx #0
 ldy #10
 jmp Cv3FxFramePulseFull
Cv3Fx24PulseFrame015:
 lda #179
 ldx #0
 ldy #11
 jmp Cv3FxFramePulseFull
Cv3Fx24PulseFrame016:
 lda #177
 ldx #0
 ldy #8
 jmp Cv3FxFramePulseFull
Cv3Fx24PulseFrame017:
 lda #180
 ldx #64
 ldy #10
 jmp Cv3FxFramePulseFull
Cv3Fx24PulseFrame018:
 lda #178
 ldx #100
 jmp Cv3FxFramePulseVolumePeriod
Cv3Fx24PulseFrame019:
 lda #179
 ldx #208
 jmp Cv3FxFramePulseVolumePeriod
Cv3Fx24PulseFrame020:
 lda #178
 ldx #0
 ldy #13
 jmp Cv3FxFramePulseFull
Cv3Fx24PulseFrame021:
 lda #178
 ldx #0
 ldy #14
 jmp Cv3FxFramePulseFull
Cv3Fx24PulseFrame022:
 lda #177
 ldx #0
 ldy #10
 jmp Cv3FxFramePulseFull
Cv3Fx24PulseFrame023:
 lda #177
 ldx #0
 ldy #11
 jmp Cv3FxFramePulseFull
Cv3Fx24PulseFrame024:
 lda #48
 jmp Cv3FxFramePulseVolumeSweep
Cv3Fx24PulseEnd: .byte $ff
Cv3Fx21Noise:
Cv3Fx21NoiseFrame000:
 lda #56
 ldx #15
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame001:
 lda #56
 ldx #13
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame002:
 lda #56
 ldx #15
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame003:
 lda #56
 ldx #10
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame004:
 lda #56
 ldx #9
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame005:
 lda #56
 ldx #8
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame006:
 lda #56
 ldx #7
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame007:
 lda #56
 ldx #6
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame008:
 lda #56
 ldx #5
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame009:
 lda #56
 ldx #4
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame010:
 lda #48
 ldx #0
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame011:
 lda #52
 ldx #13
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame012:
 lda #52
 ldx #12
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame013:
 lda #52
 ldx #11
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame014:
 lda #52
 ldx #10
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame015:
 lda #52
 ldx #9
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame016:
 lda #52
 ldx #8
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame017:
 lda #52
 ldx #7
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame018:
 lda #52
 ldx #6
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame019:
 lda #52
 ldx #5
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame020:
 lda #52
 ldx #4
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame021:
 lda #48
 ldx #0
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame022:
 lda #50
 ldx #13
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame023:
 lda #50
 ldx #12
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame024:
 lda #50
 ldx #11
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame025:
 lda #50
 ldx #10
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame026:
 lda #50
 ldx #9
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame027:
 lda #50
 ldx #8
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame028:
 lda #50
 ldx #7
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame029:
 lda #50
 ldx #6
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame030:
 lda #50
 ldx #5
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame031:
 lda #50
 ldx #4
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame032:
 lda #48
 ldx #0
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame033:
 lda #49
 ldx #13
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame034:
 lda #49
 ldx #12
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame035:
 lda #49
 ldx #11
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame036:
 lda #49
 ldx #10
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame037:
 lda #49
 ldx #9
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame038:
 lda #49
 ldx #8
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame039:
 lda #49
 ldx #7
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame040:
 lda #49
 ldx #6
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame041:
 lda #49
 ldx #4
 jmp Cv3FxFrameNoiseFull
Cv3Fx21NoiseFrame042:
 lda #48
 jmp Cv3FxFrameNoiseVolume
Cv3Fx21NoiseEnd: .byte $ff
Cv3Fx21Pulse:
Cv3Fx21PulseFrame000:
 lda #48
 jmp Cv3FxFramePulseVolumeSweep
Cv3Fx21PulseEnd: .byte $ff
Cv3Fx2FNoise:
Cv3Fx2FNoiseFrame000:
 lda #48
 ldx #0
 jmp Cv3FxFrameNoiseFull
Cv3Fx2FNoiseFrame001:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame002:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame003:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame004:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame005:
 lda #59
 ldx #13
 jmp Cv3FxFrameNoiseFull
Cv3Fx2FNoiseFrame006:
 lda #59
 ldx #13
 jmp Cv3FxFrameNoiseFull
Cv3Fx2FNoiseFrame007:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame008:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame009:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame010:
 lda #57
 ldx #15
 jmp Cv3FxFrameNoiseFull
Cv3Fx2FNoiseFrame011:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame012:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame013:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame014:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame015:
 lda #56
 ldx #13
 jmp Cv3FxFrameNoiseFull
Cv3Fx2FNoiseFrame016:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame017:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame018:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame019:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame020:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame021:
 lda #54
 ldx #15
 jmp Cv3FxFrameNoiseFull
Cv3Fx2FNoiseFrame022:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame023:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame024:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame025:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame026:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame027:
 lda #53
 ldx #13
 jmp Cv3FxFrameNoiseFull
Cv3Fx2FNoiseFrame028:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame029:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame030:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame031:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame032:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame033:
 lda #52
 ldx #15
 jmp Cv3FxFrameNoiseFull
Cv3Fx2FNoiseFrame034:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame035:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame036:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame037:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame038:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame039:
 lda #51
 ldx #13
 jmp Cv3FxFrameNoiseFull
Cv3Fx2FNoiseFrame040:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame041:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame042:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame043:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame044:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame045:
 lda #50
 ldx #15
 jmp Cv3FxFrameNoiseFull
Cv3Fx2FNoiseFrame046:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame047:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame048:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame049:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame050:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame051:
 lda #49
 ldx #13
 jmp Cv3FxFrameNoiseFull
Cv3Fx2FNoiseFrame052:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame053:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame054:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame055:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame056:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame057:
 lda #49
 ldx #15
 jmp Cv3FxFrameNoiseFull
Cv3Fx2FNoiseFrame058:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame059:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame060:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame061:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame062:
 jmp Cv3FxFrameQuiet
Cv3Fx2FNoiseFrame063:
 lda #48
 jmp Cv3FxFrameNoiseVolume
Cv3Fx2FNoiseEnd: .byte $ff
Cv3Fx2FPulse:
Cv3Fx2FPulseFrame000:
 lda #177
 ldx #83
 ldy #9
 jmp Cv3FxFramePulseSweepFull
Cv3Fx2FPulseFrame001:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame002:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame003:
 lda #178
 ldx #254
 ldy #8
 jmp Cv3FxFramePulseFull
Cv3Fx2FPulseFrame004:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame005:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame006:
 lda #179
 ldx #226
 jmp Cv3FxFramePulseVolumePeriod
Cv3Fx2FPulseFrame007:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame008:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame009:
 lda #180
 ldx #190
 jmp Cv3FxFramePulseVolumePeriod
Cv3Fx2FPulseFrame010:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame011:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame012:
 lda #182
 ldx #169
 jmp Cv3FxFramePulseSweepVolumePeriod
Cv3Fx2FPulseFrame013:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame014:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame015:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame016:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame017:
 lda #182
 ldx #226
 jmp Cv3FxFramePulseVolumePeriod
Cv3Fx2FPulseFrame018:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame019:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame020:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame021:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame022:
 lda #182
 ldx #83
 ldy #9
 jmp Cv3FxFramePulseFull
Cv3Fx2FPulseFrame023:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame024:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame025:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame026:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame027:
 lda #180
 ldx #169
 ldy #8
 jmp Cv3FxFramePulseFull
Cv3Fx2FPulseFrame028:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame029:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame030:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame031:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame032:
 lda #180
 ldx #226
 jmp Cv3FxFramePulseVolumePeriod
Cv3Fx2FPulseFrame033:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame034:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame035:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame036:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame037:
 lda #180
 ldx #83
 ldy #9
 jmp Cv3FxFramePulseFull
Cv3Fx2FPulseFrame038:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame039:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame040:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame041:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame042:
 lda #179
 ldx #169
 ldy #8
 jmp Cv3FxFramePulseFull
Cv3Fx2FPulseFrame043:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame044:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame045:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame046:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame047:
 lda #179
 ldx #226
 jmp Cv3FxFramePulseVolumePeriod
Cv3Fx2FPulseFrame048:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame049:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame050:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame051:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame052:
 lda #179
 ldx #83
 ldy #9
 jmp Cv3FxFramePulseFull
Cv3Fx2FPulseFrame053:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame054:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame055:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame056:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame057:
 lda #178
 ldx #169
 ldy #8
 jmp Cv3FxFramePulseFull
Cv3Fx2FPulseFrame058:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame059:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame060:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame061:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame062:
 lda #178
 ldx #226
 jmp Cv3FxFramePulseVolumePeriod
Cv3Fx2FPulseFrame063:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame064:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame065:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame066:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame067:
 lda #178
 ldx #83
 ldy #9
 jmp Cv3FxFramePulseFull
Cv3Fx2FPulseFrame068:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame069:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame070:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame071:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame072:
 lda #177
 ldx #169
 ldy #8
 jmp Cv3FxFramePulseFull
Cv3Fx2FPulseFrame073:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame074:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame075:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame076:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame077:
 lda #177
 ldx #226
 jmp Cv3FxFramePulseVolumePeriod
Cv3Fx2FPulseFrame078:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame079:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame080:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame081:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame082:
 lda #177
 ldx #83
 ldy #9
 jmp Cv3FxFramePulseFull
Cv3Fx2FPulseFrame083:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame084:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame085:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame086:
 jmp Cv3FxFrameQuiet
Cv3Fx2FPulseFrame087:
 lda #48
 jmp Cv3FxFramePulseVolumeSweep
Cv3Fx2FPulseEnd: .byte $ff
Cv3FxNoiseLo:.byte <Cv3Fx1FNoise,<Cv3Fx13Noise,<Cv3Fx15Noise,<Cv3Fx24Noise,<Cv3Fx21Noise,<Cv3Fx21Noise,<Cv3Fx2FNoise
Cv3FxNoiseHi:.byte >Cv3Fx1FNoise,>Cv3Fx13Noise,>Cv3Fx15Noise,>Cv3Fx24Noise,>Cv3Fx21Noise,>Cv3Fx21Noise,>Cv3Fx2FNoise
Cv3FxPulseLo:.byte 0,0,0,<Cv3Fx24Pulse,<Cv3Fx21Pulse,<Cv3Fx21Pulse,<Cv3Fx2FPulse
Cv3FxPulseHi:.byte 0,0,0,>Cv3Fx24Pulse,>Cv3Fx21Pulse,>Cv3Fx21Pulse,>Cv3Fx2FPulse
Cv3FxLegacyOffsets:.byte 0,7,10,13,20,23,26,33,36,39,46,49,52,59,62,65,72,75,78,85,88,91,98,101,104,111,114,117,122

; NMI is the only consumer. It is never preempted by another audio owner.
; Process all committed commands before advancing either source voice once.
.proc Cv3FxDrain
 lda Cv3FxOwned
 and #8
 bne NoiseKnown
 lda #0
 sta Cv3FxNoiseID
NoiseKnown:lda Cv3FxOwned
 and #1
 bne PulseKnown
 lda #0
 sta Cv3FxPulseID
PulseKnown:lda AvAudioRequest
 cmp #26
 bne Begin
 lda Cv3FxPendingNoise
 cmp #$1f
 bcs Begin
 lda #$1f
 sta Cv3FxPendingNoise
Begin:ldy Cv3FxQueueTail
 cpy Cv3FxQueueHead
 beq Done
Loop:lda Cv3FxQueue,y
 cmp #8
 beq Cancel
 tax
 ; Every authenticated source cue1..7 owns noise. Pulse is table bit0.
 lda Cv3FxRawIDs,x
 cmp Cv3FxPendingNoise
 bcc Pulse
 sta Cv3FxPendingNoise
Pulse:lda Cv3FxRawMasks,x
 lsr
 bcc Consumed
 lda Cv3FxRawIDs,x
 cmp Cv3FxPendingPulse
 bcc Consumed
 sta Cv3FxPendingPulse
 jmp Consumed
Cancel:jsr Cv3FxCancelConsumer
Consumed:iny
 cpy Cv3FxQueueHead
 bne Loop
 sty Cv3FxQueueTail
Done:lda Cv3FxPendingNoise
 ora Cv3FxPendingPulse
 beq Return
 lda Cv3FxPendingPulse
 bne Full
 lda Cv3FxPendingNoise
 cmp #$1f
 bne Full
 lda Cv3FxOwned
 and #9
 bne Full
 ; Paused/muted requests are folded but never ticked or exposed as Av26
 ; to the common decoder. Their original pending priority survives resume.
 lda GamePauseStatus
 and #1
 bne Full
 lda RgAudioSilenced
 bne Full
 lda AvAudioRequest
 beq Legacy
 cmp #26
 bcc DiscardLegacy
 cmp #33
 bcc Legacy
DiscardLegacy:lda #0
 sta Cv3FxPendingNoise
 rts
Legacy:lda #0
 sta Cv3FxPendingNoise
 lda #26
 sta AvAudioRequest
Return:rts
Full:lda Cv3FxOwned
 ora #$80
 sta Cv3FxOwned
 lda Cv3NoiseActive
 cmp #1
 bne Dispatch
 lda Cv3NoiseIndex
 cmp #28
 bcs Dispatch
 lda #$1f
 sta Cv3FxNoiseID
 lda Cv3FxOwned
 ora #$48
 sta Cv3FxOwned
Dispatch:lda #$80
 sta Cv3NoiseActive
 rts
.endproc
.proc Cv3FxCancelConsumer
 lda Cv3NoiseActive
 cmp #1
 bne IDs
 lda Cv3FxOwned
 ora #8
 sta Cv3FxOwned
 lda #$80
 sta Cv3NoiseActive
IDs:lda #0
 sta Cv3FxNoiseID
 sta Cv3FxPulseID
 sta Cv3FxPendingNoise
 sta Cv3FxPendingPulse
 jsr Cv3FxClearTyped
 rts
.endproc
; A=7 bat or8 cancel. Main writes the slot before publishing head LAST.
; Full rejection is only a defensive invalid-domain behavior: it neither
; overwrites committed data nor publishes a partially written command.
.proc Cv3FxQueueCommand
 pha
 cmp #8
 bne Room
 lda Cv3FxQueueHead
 cmp Cv3FxQueueTail
 beq Room
 sec
 sbc #1

 tay
 lda Cv3FxQueue,y
 cmp #8
 beq Duplicate
Room:
 lda Cv3FxQueueHead
 sec
 sbc Cv3FxQueueTail
 cmp #64
 bcs Full
 lda Cv3FxQueueHead

 tay
 pla
 sta Cv3FxQueue,y
 inc Cv3FxQueueHead
 rts
Full:pla
 inc Cv3FxQueueOverflow
 rts
Duplicate:pla
 rts
.endproc
.assert *<=$c000,lderror,"Complete sourceFX inside recorded A82 slack"
.popseg

.segment "CV3_COMBAT"
.proc Cv3FxProducer
 sta Cv3ShotType,x
 cmp #1
 bcc Done
 cmp #7
 bcs Done
 ldy AvAudioRequest
 beq WorldClear
 cpy #26
 bcc Done
 cpy #33
 bcs Done
WorldClear:pha
 lda Cv3FxQueueHead
 sec
 sbc Cv3FxQueueTail
 cmp #64
 bcs Full
 ldy Cv3FxQueueHead
 pla
 sta Cv3FxQueue,y
 inc Cv3FxQueueHead
Done:rts
Full:pla
 inc Cv3FxQueueOverflow
 rts
.endproc
.segment "CV_AUDIO"
.proc Cv3FxDrainGate
 php
 pha
 txa
 pha
 tya
 pha
 lda CurrentBank
 pha
 lda #.bank(Cv3FxDrain)|MMC5_PRG_ROM
 sta CurrentBank
 sta $5115
 jsr Cv3FxDrain
 pla
 sta CurrentBank
 sta $5115
 pla
 tay
 pla
 tax
 pla
 plp
 rts
.endproc
.proc Cv3FxClearTyped
 lda AvAudioRequest
 cmp #26
 bcc Done
 cmp #33
 bcs Done
 lda #0
 sta AvAudioRequest
Done:rts
.endproc

.pushseg
.segment "CV3_COMBAT"
; Sole actual caller has constant1..6 and at most21 outstanding commands after
; the NMI mute consumer/cancel-run proof. Checked public entry remains above.
.proc Cv3FxProducerFast
 sta Cv3ShotType,x
 ldy AvAudioRequest
 beq WorldClear
 cpy #26
 bcc Done
 cpy #33
 bcs Done
WorldClear:ldy Cv3FxQueueHead
 sta Cv3FxQueue,y
 inc Cv3FxQueueHead
Done:rts
.endproc
.segment "CV3_GRIP"
Cv3FxRawIDs:.byte 0,$13,$15,$24,$21,$1e,$1f,$2f
Cv3FxRawMasks:.byte 0,8,8,9,9,9,8,9
.assert *<=$c000,lderror,"Declared remaining A82 source space"
.segment "CV_AUDIO"
.proc Cv3FxMuteGate
 php
 lda Cv3FxQueueHead
 cmp Cv3FxQueueTail
 beq Empty
 jsr Cv3FxDrainGate
Empty:plp
 lda #0
 jmp GuestNativeStatusSTA
.endproc
.proc Cv3FxResidentBody
 ; All-zero dirty state avoids three separate taken branches. If music
 ; wrote fields, cache exact new music values before original source emission.
 lda GuestNativeDirty+12
 ora GuestNativeDirty+14
 ora GuestNativeDirty+15
 beq Ready
 lda GuestNativeDirty+12
 beq P
 lda GuestNativeApu+12
 sta Cv3NoiseMusicVolume
P:lda GuestNativeDirty+14
 beq H
 lda GuestNativeApu+14
 sta Cv3NoiseMusicPeriod
H:lda GuestNativeDirty+15
 beq FinalCheck
 lda GuestNativeApu+15
 sta Cv3NoiseMusicHigh
FinalCheck:ldy Cv3NoiseIndex
 cpy #42
 bne Emit
 ; The final source frame writes volume only. Reproduce the original
 ; pre-emission restoration/clear of any music period/high writes exactly.
 lda GuestNativeDirty+14
 beq FH
 lda Cv3NoiseApu+2
 sta GuestNativeApu+14
 lda #0
 sta GuestNativeDirty+14
FH:lda GuestNativeDirty+15
 beq Emit
 lda Cv3NoiseApu+3
 sta GuestNativeApu+15
 lda #0
 sta GuestNativeDirty+15
 jmp Emit
Ready:ldy Cv3NoiseIndex
Emit:lda Cv3FxResidentVolume,y
 sta GuestNativeApu+12
 sta Cv3NoiseApu
 cpy #42
 beq Final
 lda Cv3FxSourceHigh
 ora #8
 sta GuestNativeApu+15
 sta Cv3NoiseApu+3
 lda Cv3FxResidentPeriod,y
 sta GuestNativeApu+14
 sta Cv3NoiseApu+2
 lda #1
 sta GuestNativeDirty+12
 sta GuestNativeDirty+15
 sta GuestNativeDirty+14
 lda #7
 bne Commit
Final:lda #1
 sta GuestNativeDirty+12
 lda #0
 sta Cv3FxNoiseID
 lda #5
Commit:clc
 adc Cv3FxNoisePtr
 sta Cv3FxNoisePtr
 bcc NoCarry
 inc Cv3FxNoisePtr+1
NoCarry:inc Cv3NoiseIndex
 rts
.endproc
.assert *<=$dc00,lderror,"Declared remaining C28 source space"
.popseg
