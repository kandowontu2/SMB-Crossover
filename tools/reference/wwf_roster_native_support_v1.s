; Native integration helpers. No new global/ZP allocation.
.setcpu "6502"
.macpack longbranch
.import SelectedCharacter,OperMode,CrossoverMenuState,FmGroups,CurrentBank,CurrentBankC
.import GmFamilyNmiGate,FixedAudioRestore,ArNmiPhysicalCWrite,GamePauseStatus
.import GuestAudioBegin,GuestAudioFinish,GuestNativeEnable
.import AreaMusicQueue,EventMusicQueue,Square1SoundQueue,Square2SoundQueue,NoiseSoundQueue,PauseSoundQueue
.import NextBank_SMC,SafereturnA_SMC,SafecallA_SMC,FarcallJmpTarget_SMC,FarCallCommon
.import WfHostReady,WfState,WfCueClass,WfCueValue,WfCuePending
.export WfAudioSavedP,WfAudioSavedSmc,WfAudioNativeEntry
.import WfAudio_E22E,WfAudio_E249,WfAudio_E4DE,WfAudioScratch
.import WfAuthCookie,WfColdIdentity,WfAtomicRti
.export WfAudioProbe,WfAudioFinishC,WfQueueAudioCue
.macro AudioFar Target
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(Target)|$80)
 jsr FarCallCommon
.endmacro
.macro SmcImage Restore
 .repeat 5,I
  .if Restore
   lda WfAudioSavedSmc+I
  .endif
  .if I=0
   .if Restore
    sta NextBank_SMC+1
   .else
    lda NextBank_SMC+1
   .endif
  .elseif I=1
   .if Restore
    sta SafecallA_SMC+1
   .else
    lda SafecallA_SMC+1
   .endif
  .elseif I=2
   .if Restore
    sta FarcallJmpTarget_SMC+1
   .else
    lda FarcallJmpTarget_SMC+1
   .endif
  .elseif I=3
   .if Restore
    sta FarcallJmpTarget_SMC+2
   .else
    lda FarcallJmpTarget_SMC+2
   .endif
  .else
   .if Restore
    sta SafereturnA_SMC+1
   .else
    lda SafereturnA_SMC+1
   .endif
  .endif
  .if !Restore
   sta WfAudioSavedSmc+I
  .endif
 .endrepeat
.endmacro

.segment "WF_RUNTIME_A"
; Fixed AudioUpdate maps A96 only. No RAM opcode is admitted until the same
; complete ROM-cookie comparison used by Main and the ready check succeed.
WfAudioProbe:
 php
 sei
 txa
 pha
 tya
 pha
 lda CurrentBankC
 pha
 jsr WfColdIdentity
 bcc ProbeForeign
 lda OperMode
 cmp #1
 bne ProbeForeign
 lda CrossoverMenuState
 cmp #8
 beq ProbeForeign
 jsr WfAuthCookie
 bcc ProbeForeign
 lda WfHostReady
 cmp #$a7
 bne ProbeForeign
 lda #>(WfAudioAcquiredC-1)
 pha
 lda #<(WfAudioAcquiredC-1)
 pha
 lda #3
 sta CurrentBankC
 jmp ArNmiPhysicalCWrite
ProbeForeign:
 lda #>(WfAudioForeignC-1)
 pha
 lda #<(WfAudioForeignC-1)
 pha
 lda #$e0
 jmp ArNmiPhysicalCWrite

.segment "WF_AUDIO_C3"
; Full cache verification has completed before this C-view raw3 entry.
WfAudioAcquiredC:
 lda #1
 sta CurrentBank
 sta $5115
 SmcImage 0
 AudioFar GuestAudioBegin
 tsx
 lda $0104,x                 ; original P is below saved X/Y/C
 sta WfAudioSavedP
 lda #>(WfAudioNativeEntry-1)
 pha
 lda #<(WfAudioNativeEntry-1)
 pha
 lda #2
 sta CurrentBankC
 jmp ArNmiPhysicalCWrite      ; fixed code maps C2 before entering A1
WfAudioFinishC:
 AudioFar GuestAudioFinish
 lda #0
 sta AreaMusicQueue
 sta EventMusicQueue
 sta Square1SoundQueue
 sta Square2SoundQueue
 sta NoiseSoundQueue
 sta PauseSoundQueue
 SmcImage 1
 sei
 tsx
 lda $0105,x                ; AudioUpdate's original software A owner
 sta CurrentBank            ; fixed restore changes hardware only
 lda #$bf
 sta $5115
 lda #>(WfAudioDoneC-1)
 pha
 lda #<(WfAudioDoneC-1)
 pha
 lda #$e0
 jmp ArNmiPhysicalCWrite

.segment "WF_ROM_C"
; The fixed RTI performs the P/PC return atomically after the actual old C
; mapping is restored. Thus IRQ never sees a stale software bank shadow.
.macro EmitAudioReturn Target
 pla
 sta CurrentBankC
 tsx
 lda $0101,x
 tay
 lda $0103,x
 sta $0101,x
 lda $0102,x
 pha
 lda #<Target
 sta $0102,x
 lda #>Target
 sta $0103,x
 pla
 tax
 lda #>(WfAtomicRti-1)
 pha
 lda #<(WfAtomicRti-1)
 pha
 lda CurrentBankC
 jmp ArNmiPhysicalCWrite
.endmacro
WfAudioForeignC:
 lda #$bf
 sta $5115
 EmitAudioReturn GmFamilyNmiGate
WfAudioDoneC:
 EmitAudioReturn FixedAudioRestore

.segment "WF_A1_INACTIVE"
WfAudioNativeEntry:
 lda WfAudioSavedP
 pha
 plp                         ; IRQ may run while source music continues
 lda GamePauseStatus
 and #1
 bne AudioReturn
 lda WfAudioScratch+3        ; zero only in this freshly loaded audio image
 bne HaveAudioImage
 jsr WfAudio_E22E
 lda #15
 sta GuestNativeEnable       ; donor boot enabled these four APU channels
HaveAudioImage:
 lda WfState+$500
 ora WfState+$504
 ora WfState+$508
 ora WfState+$50c
 bne AudioTick
 ldx WfState+$2b
 lda OriginalThemes,x
 sta WfAudioScratch+1
 jsr WfAudio_E249
AudioTick:
 jsr WfAudio_E4DE
AudioReturn:
 lda #3
 sta CurrentBankC
 sta $5116
 jmp WfAudioFinishC
OriginalThemes:.byte 6,7,4,2,5,1
WfAudioSavedSmc:.res 5,0
WfAudioSavedP:.res 1,0

.segment "WF_ROSTER_CUES"
; All source actor cold/frame calls own A3 and C2. Preserve the original
; channel-specific enqueue semantics instead of dropping different channels.
WfQueueAudioCue:
 lda WfCueClass
 ldy #$10
 cmp #9
 beq QueueSourceCue
 ldy #$18
 cmp #15
 beq QueueSourceCue
 ldy #$1c
QueueSourceCue:
 lda WfCueValue
 cmp WfState+$500,y
 beq CueDone
 sta WfState+$563,y
 sta WfState+$500,y
CueDone:
 inc WfCuePending
 rts
