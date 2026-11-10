.include "scheduler-imports.inc"
.export RdsBoot,RdsMainGate,RdsNmiGate,RdsCommonStart,RdsCommonEnd
.export RdsAudioFrame,RdsFrameStart,RdsFrameEnd
; Existing private512B image, live only under effective audio owner82.
RdsApplied=RgAudioRam+$117
RdsRngDelta=RgAudioRam+$118
RdsContext=RgAudioRam+$119    ; missile/gear/VY/Beam selector: four source reads
RdsTheme=RgAudioRam+$11d
RdsNeedTheme=RgAudioRam+$11e
RdsDacDue=RgAudioRam+$11f
; Sole common publication byte: bits1..2 completed Rogue Mains (0..2),
; bit0 busy; other bits remain zero. Five live cues have no busy rule.
RdsCommit=$5fb6
RdsSmcBackup=RgAudioCpuZp+155

.macro RdsFar Target,Bank,Tail
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #($80|Bank)
 .ifblank Tail
  jsr FarCallCommon
 .else
  jmp FarCallCommon
 .endif
.endmacro
.macro RdsSaveSmc
 lda NextBank_SMC+1
 sta RdsSmcBackup+0
 lda SafecallA_SMC+1
 sta RdsSmcBackup+1
 lda FarcallJmpTarget_SMC+1
 sta RdsSmcBackup+2
 lda FarcallJmpTarget_SMC+2
 sta RdsSmcBackup+3
 lda SafereturnA_SMC+1
 sta RdsSmcBackup+4
.endmacro
.macro RdsRestoreSmc
 lda RdsSmcBackup+0
 sta NextBank_SMC+1
 lda RdsSmcBackup+1
 sta SafecallA_SMC+1
 lda RdsSmcBackup+2
 sta FarcallJmpTarget_SMC+1
 lda RdsSmcBackup+3
 sta FarcallJmpTarget_SMC+2
 lda RdsSmcBackup+4
 sta SafereturnA_SMC+1
.endmacro

.segment "ROGUE_SCHEDULER_COMMON"
RdsCommonStart:

; Real PauseRoutine18B target: inputAFF is begin, A0 is common Main end.
; Boot initial0; EVERY Main brackets context. A Main ending as activeRogue
; atomically increments its completed count. Foreign retirement discards old
; counts while preserving the current busy bit; no cached Main RMW can revive it.
.proc RdsMainGate
 php
 pha
 beq End
 inc RdsCommit             ; every Main marks context busy atomically
BeginReady:
 pla
 plp
 RdsFar HpPauseCold,26,Tail ; genuine native pause exactly once
End:
 jsr IsActive
 bcc ForeignMain
 inc RdsCommit             ; atomic odd->even completed activeRogueMain
 jmp EndReady
ForeignMain:
 lda #0
 sta RdsCommit             ; a retired owner never survives this Main
EndReady:
 pla
 plp
 sta NmiDisable
 rts
.endproc
.proc IsActive
 lda OperMode
 beq No
 lda SelectedCharacter
 cmp #2
 bne No
 lda RdVariant
 cmp #1
 bne No
 sec
 rts
No:clc
 rts
.endproc

; Proposed AudioUpdate first18B:
; LDA CurrentBank/PHA/LDA#BF/STA5115/JMP RdsNmiGate/6EA (12+6B).
; No SMC or software-bank write occurs before this cold entry. Foreign
; branches discard oldA then replay the ORIGINAL prefix and tail into fixed
; F06F/F0D8. SoundTest menu8 never clocks Rogue, including its inner call.
.proc RdsNmiGate
 php
 lda CrossoverMenuState
 cmp #8
 jeq Foreign
 jsr IsActive
 jcc Foreign
 plp
 lda #$bf
 sta CurrentBank          ; real A63 now owns normal farcall continuations
 RdsSaveSmc
 lda GuestAudioCharacter
 cmp #$82
 beq Existing
 lda RdsCommit
 and #1
 jne ColdBusy
 lda #$ff
 sta GuestAudioCharacter
 RdsFar GuestAudioBegin,29 ; true old DMC/mixer owner reset, once
 ; Genuine Begin filters/clears exactly these bits. Restore them before
 ; the single real Frame capture; do not replay a previous frame image.
 lda GuestWorldQueues
 ora Square1SoundQueue
 sta Square1SoundQueue
 lda GuestWorldQueues+1
 ora Square2SoundQueue
 sta Square2SoundQueue
 lda GuestWorldQueues+2
 ora NoiseSoundQueue
 sta NoiseSoundQueue
 RdsFar RdaAudioInit,62    ; source init; private cache is cleared here
 lda #$82
 sta GuestAudioCharacter
 jmp Stable
Existing:
 lda RdsCommit
 and #1
 bne Tick
Stable:
 jsr CommitContext
Tick:
 RdsFar RdsAudioFrame,62
 lda RdsCommit
 and #1
 bne Done
 lda #0
 sta RdsCommit
 sta RdsApplied           ; stable ACK after capture/tick, never cues
Done:
 RdsRestoreSmc
 pla                      ; original foreground software A shadow
 sta CurrentBank
 pha
 jmp FixedAudioRestore    ; authentic fixed PLA/STA5115/RTS
ColdBusy:
 ; Do not interpret another owner's512B image or partial Rogue overlay.
 ; Complete prior-owner reset is deferred until the first stable acquire.
 lda #0
 sta $4015
 sta $5015
 sta $4011
 jmp Done
Foreign:
 plp
 pla                      ; discard manual mapping's saved oldA
 ; Retire only our effective owner. No private image read under foreign.
 php
 pha
 lda RdsCommit
 and #1
 sta RdsCommit             ; retire count/startmark, preserve actualbusy
 lda GuestAudioCharacter
 cmp #$82
 bne ForeignReady
 lda #$ff
 sta GuestAudioCharacter
 lda #0
 sta $4011
 sta $4015
 sta $5015
ForeignReady:
 pla
 plp
 lda OperMode
 beq Vanilla
 lda SelectedCharacter
 beq Vanilla
 cmp #8                   ; actual original LuigiID
 beq Vanilla
 cmp #23                  ; actual original SunnyID
 beq Vanilla
 jmp FixedGuestRemainder
Vanilla:jmp FixedVanillaRemainder
.endproc

.proc CommitContext
 lda RdMissileMode
 sta RdsContext
 lda RdGear
 sta RdsContext+1
 lda RdVY
 sta RdsContext+2
 lda RdBeamSfx
 sta RdsContext+3
 lda GamePauseStatus
 and #1
 beq Normal
 lda #5
 bne ModeReady
Normal:lda #3
ModeReady:sta RdaZpState
 ldx AreaType
 cpx #1
 bne OtherArea
 ldx WorldNumber
 lda WorldTheme,x
 jmp Compare
OtherArea:lda AreaTheme,x
Compare:
 cmp RdsTheme
 bne NewTheme
 ldx AreaMusicQueue
 txa
 and #15                  ; actual native normal ground/water/cave/castle
 beq ThemeDone
 lda RdsTheme
NewTheme:
 sta RdsTheme
 sta RdaZpState+1          ; source23, not future AreaPointer
 lda #1
 sta RdsNeedTheme
ThemeDone:rts
AreaTheme:.byte 4,0,2,5
WorldTheme:.byte 1,0,3,1,0,3,1,0
.endproc
.proc RdsBoot
 lda #0
 sta RdsCommit
 lda #<CrossoverInit
 sta FarcallJmpTarget_SMC+1
 lda #>CrossoverInit
 sta FarcallJmpTarget_SMC+2
 lda #$8a
 jmp FarCallCommon
.endproc
RdsCommonEnd:
.out .sprintf("RDS common bytes=%u",RdsCommonEnd-RdsCommonStart)

.segment "ROGUE_AUDIO_ADAPTER_A62"
RdsFrameStart:
; Proposed replacement of the old RdaAudioTick body, preserving its public
; register envelope and C map. Original borrow leavesXFF: restore exactly
; after the0..2 RNG loop before entering the real49:A770 driver.
.proc RdsAudioFrame
 lda RdsCommit
 and #6
 lsr
 tax
 sec
 sbc RdsApplied
 sta RdsRngDelta
 stx RdsApplied
 ; Exact original RemainingAudioBegin font prefix ONLY. The later source-
 ; effect restore/RemainingAudioTick are deliberately not replayed forRogue.
 lda DisableScreenFlag
 bne FontDone
 lda InvHudActive
 beq FontDone
 lda X5HudChrUpper
 and #3
 sta $5130
 lda InvHudPhysical
 sta $5128
 lda #0
 sta $5130
FontDone:
 lda RdsNeedTheme
 beq NoTheme
 ldx RdsTheme
 lda NormalFlags,x
 sta RdSfx+5
NoTheme:
 lda RdSfx
 and #1
 sta RdsNeedTheme          ; init clears normal request; retry ONLY theme
 lda #$e1
 sta CurrentBankC
 sta $5116
 jsr RdaBorrow
 ldx RdsRngDelta
 beq RngDone
Rng:jsr RdaOriginalRng
 dex
 bne Rng
RngDone:
 ldx #$ff
 jsr RdaNA770
 jsr RdaRelease
 lda RdaFrameControl
 sta $4017                ; genuine source action every tick, not dirty-skipped
 lda RdsNeedTheme
 beq NoDac
 lda RdaDac
 sta $4011
NoDac:
 lda Square1SoundQueue
 and #$42                 ; authenticated Bump02|Flagpole40
 sta GuestWorldQueues
 lda Square2SoundQueue
 and #$7f                 ; real coin/grow/vine/blast/timer/pickup/life bits
 sta GuestWorldQueues+1
 lda NoiseSoundQueue
 and #1                   ; real BrickShatter01; no generic attack substitute
 sta GuestWorldQueues+2
 lda RdaZpState
 cmp #5
 beq Paused
 RdsFar GuestAudioFinishTick,29
 jmp Ack
Paused:
 lda #0
 sta $5015
 sta GuestMixMask
 sta GuestMixPreviousMask
 lda GuestNativeEnable
 and #15
 sta GuestCombinedEnable
 sta $4015
 RdsFar GuestAudioNativeFlush,29
Ack:
 lda #0
 sta Square1SoundQueue
 sta Square2SoundQueue
 sta NoiseSoundQueue
 sta PauseSoundQueue
 sta AreaMusicQueue
 sta EventMusicQueue
 rts
NormalFlags:.byte 16,1,8,64,16,128
.endproc
; Proposed rebind of Reset's existing CrossoverInit target, not an extra hook.
; True initialization first owns5FB6 before NMI is enabled. CrossoverInit's
; real input liveness/caller proof remains mandatory in the eventual union.
RdsFrameEnd:
.out .sprintf("RDS frame bytes=%u",RdsFrameEnd-RdsFrameStart)

.assert RdsCommonEnd-RdsCommonStart<=512,lderror,"Approved common512B exceeded"
