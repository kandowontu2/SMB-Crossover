; Native music/weapon drivers and the original SMB world effects advance
; separately. Mix their register images after both updates, borrowing only
; channels with an active world effect. Timer-high dirty flags preserve note
; retriggers and restore music immediately when an effect releases a channel.
.pushseg
.segment "SRAM"
GuestNativeApu: .res 16
GuestFxApu: .res 24
GuestNativeDirty: .res 16
GuestFxDirty: .res 16
GuestApuLast: .res 16
GuestAudioCharacter: .res 1
GuestWorldQueues: .res 3
GuestMixMask: .res 1
GuestMixPreviousMask: .res 1
GuestMixChanged: .res 1
GuestMixChannel: .res 1
GuestMixRegister: .res 1
GuestMixValue: .res 1
GuestMixOwner: .res 1
GuestNativeEnable: .res 1
GuestCombinedEnable: .res 1
.if ::MAPPER_MMC5
GuestExpansionApu: .res 8
GuestExpansionLast: .res 8
GuestSweepPeriod: .res 2
GuestSweepDelta: .res 2
GuestSweepControl: .res 1
GuestSweepDivider: .res 1
GuestSweepReload: .res 1
GuestSweepTicks: .res 1
.endif
.include "build/generated/guest-audio/writers.inc"
.segment "FIXED"
GuestMetroidStoreIndirectY:
  ; Replaces STA ($e0),Y / INY in the pinned native LoadSFXRegisters loop.
  ; $e0 is the channel's $00/$04/$08/$0c APU offset. Preserve A/X and the
  ; original carry; leave Y and N/Z exactly as the displaced INY would.
  sta GuestMixValue
  php
  txa
  pha
  tya
  clc
  adc $e0
  tax
  lda GuestMixValue
  sta GuestNativeApu,x
  inc GuestNativeDirty,x
  pla
  tax
  lda GuestMixValue
  plp
  iny
  rts
GuestNativeStatusSTA:
  sta GuestNativeEnable
  php
  pha
  lda GuestNativeEnable
  jsr GuestDmcStatus
  sta GuestNativeEnable
  lda GuestMixMask
.if ::MAPPER_MMC5
  and #8                         ; Pulse world effects live on the cartridge.
.endif
  ora GuestNativeEnable
  sta GuestCombinedEnable
  sta $4015
  pla
  plp
  rts
GuestDmcStatus:
  ; Re-enabling a completed DMC restarts its sample. Poll before every
  ; status write, including music's earlier write in this same NMI.
  pha
  lda BassDmcActive
  beq DmcOff
  lda $4015
  and #$10
  beq DmcEnded
  pla
  ora #$10
  rts
DmcEnded:
.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
  jsr TnDmcEndedGate
  .res 5,$ea ; original eight-byte completion span
.else
  lda #0
  sta BassDmcActive
  sta $4011
.endif
DmcOff:
  pla
  and #15
  rts
; Imported drivers use STA for their status writes.
.segment "GUEST_AUDIO"
.include "build/generated/guest-audio/shared-sfx.inc"
.proc GuestAudioBegin
  lda SelectedCharacter
.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
  cmp #CHARACTER_PIT
  bcs :+
.else
  cmp #CHARACTER_BASS
  beq :+
.endif
    jsr BassAudioBegin
  :
  lda SelectedCharacter
  cmp GuestAudioCharacter
  beq Queues
  sta GuestAudioCharacter
  lda #0
  jsr MegaManRushLandCharacterReset
  sta BassAudioPreviousMask
  sta BassAudioLastDeath
  sta BassAudioLastGround
.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
  jsr Cv3DmcResetOwner
.else
  sta BassDmcActive
.endif
  sta $4011
  sta GuestMixMask
  sta GuestMixPreviousMask
  sta GuestNativeEnable
  sta GuestCombinedEnable
.if ::MAPPER_MMC5
  sta $5010                      ; No PCM read mode or expansion audio IRQ.
  sta $5015
  sta GuestSweepDivider
  sta GuestSweepReload
  sta GuestSweepControl
.endif
  sta Square1SoundBuffer
  sta Square2SoundBuffer
  sta NoiseSoundBuffer
  sta PauseSoundBuffer
  ldx #15
Clear:
  sta GuestNativeApu,x
  sta GuestFxApu,x
  sta BassAudioSfxApu,x
  sta GuestNativeDirty,x
  sta GuestFxDirty,x
  dex
  bpl Clear
  lda #$ff
  ldx #15
Invalidate:
  sta GuestApuLast,x
  dex
  bpl Invalidate
Queues:
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  bcc NativeQueues
  ; Added guests use the common jump, stomp, shot, injury and pickup effects
  ; as well as world cues. Luigi takes the complete vanilla audio path.
  lda Square1SoundQueue
  sta GuestWorldQueues
  lda Square2SoundQueue
  sta GuestWorldQueues+1
  lda NoiseSoundQueue
  sta GuestWorldQueues+2
.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
  jmp BassAudioBegin
  nop
.else
  jsr BassAudioBegin
  rts
.endif
NativeQueues:
  lda Square1SoundQueue
  and #Sfx_Bump|Sfx_Flagpole
  sta GuestWorldQueues
  ldx #Sfx_CoinGrab|Sfx_GrowPowerUp|Sfx_GrowVine|Sfx_Blast|Sfx_TimerTick
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  bne FilterSquare2
  ; The hosted mushroom/flower/star cue is shared. Metroid's native driver
  ; has no handler for SMB's pickup or extra-life queue bits and clears
  ; them on exit, so these must reach the shared mixer before that happens.
  ldx #Sfx_CoinGrab|Sfx_GrowPowerUp|Sfx_GrowVine|Sfx_Blast|Sfx_TimerTick|Sfx_PowerUpGrab|Sfx_ExtraLife
FilterSquare2:
  txa
  and Square2SoundQueue
  sta GuestWorldQueues+1
  lda NoiseSoundQueue
  and #Sfx_BrickShatter
  sta GuestWorldQueues+2
  ; Common cues play once through the shared driver. Keep weapon and other
  ; character effects available to the original sound engines.
  lda Square1SoundQueue
  and #$ff-(Sfx_Bump|Sfx_Flagpole)
  sta Square1SoundQueue
  lda Square2SoundQueue
  eor GuestWorldQueues+1         ; Remove exactly the bits captured above.
  sta Square2SoundQueue
  lda NoiseSoundQueue
  and #$ff-Sfx_BrickShatter
  sta NoiseSoundQueue
  rts
.endproc
.proc GuestAudioFinish
  lda OperMode
  beq Silent
  lda GamePauseStatus
  and #1
  beq Tick
Silent:
  lda #0
.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
  jsr Cv3DmcResetOwner
.else
  sta BassDmcActive
.endif
  sta $4011
  sta $4015
  sta GuestMixMask
  sta GuestCombinedEnable
  sta Square1SoundBuffer
  sta Square2SoundBuffer
  sta NoiseSoundBuffer
.if ::MAPPER_MMC5
  sta $5015
.endif
  ; Disabling $4015 clears the length counters. Re-enable alone cannot
  ; resume a held note: reload the saved registers on the next active update.
  lda #$ff
  ldx #15
Invalidate:
  sta GuestApuLast,x
  dex
  bpl Invalidate
  rts
Tick:
  lda GuestWorldQueues
  sta Square1SoundQueue
  lda GuestWorldQueues+1
  sta Square2SoundQueue
  lda GuestWorldQueues+2
  sta NoiseSoundQueue
  jsr GuestSharedSfx::SFXSoundEngine
  lda #0
  sta GuestMixMask
  lda Square1SoundBuffer
  beq :+
    lda #1
    sta GuestMixMask
  :
  lda Square2SoundBuffer
  beq :+
    lda GuestMixMask
    ora #2
    sta GuestMixMask
  :
  lda NoiseSoundBuffer
  beq :+
    lda GuestMixMask
    ora #8
    sta GuestMixMask
  :
  lda GuestMixMask
  eor GuestMixPreviousMask
  sta GuestMixChanged
  lda GuestMixMask
  sta GuestMixPreviousMask
.if ::MAPPER_MMC5
  and #8
.endif
  ora GuestNativeEnable
  jsr GuestDmcStatus
  cmp GuestCombinedEnable
  beq :+
    sta GuestCombinedEnable
    sta $4015
  :
.if ::MAPPER_MMC5
.if ::ENABLE_MMC5_EXPANDED
  jsr TnExpansionSweepGate
.else
  jsr GuestExpansionFlush
.endif
.endif
  lda GuestMixMask
.if ::ENABLE_MMC5_EXPANDED
::X5NativeNoiseSpan:
  jsr X5NativeNoiseMask
.else
  ora GuestMixChanged
.endif
  bne MixedChannels
  jmp GuestAudioNativeFlush
MixedChannels:
  ; Compile-time channel/register offsets remove the indexed loop bookkeeping
  ; while preserving the original ordered writes and ownership transitions.
 .repeat 4, C
  .scope
  .if ::MAPPER_MMC5 && C < 2
   lda #0                       ; World pulses use the expansion channels.
  .else
   lda GuestMixMask
   and #(1 << C)
  .endif
   sta GuestMixOwner
  .repeat 4, R
   .scope
   I = C * 4 + R
   .if I <> 9 && I <> 13
 .if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5 && C < 2
    ; This channel's genuine owner store above is unconditionally zero.
    lda GuestNativeApu+I
 .else
    lda GuestMixOwner
    beq Native
    lda GuestFxApu+I
    jmp Value
Native:
    lda GuestNativeApu+I
 .endif
Value:
    sta GuestMixValue
    cmp GuestApuLast+I
    bne Write
 .if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5 && C < 2
    ; The deleted mix-change AND#0 is constant; only native dirtiness lives.
    lda GuestNativeDirty+I
 .else
    lda GuestMixChanged
   .if ::MAPPER_MMC5
    and #((1 << C) & 8)
   .else
    and #(1 << C)
   .endif
    bne Write
    lda GuestMixOwner
    beq NativeDirty
    lda GuestFxDirty+I
    jmp Dirty
NativeDirty:
    lda GuestNativeDirty+I
 .endif
Dirty:
    beq NextRegister
Write:
    lda GuestMixValue
    sta $4000+I
    sta GuestApuLast+I
NextRegister:
   .endif
    lda #0
    sta GuestNativeDirty+I
    sta GuestFxDirty+I
   .endscope
  .endrepeat
  .endscope
 .endrepeat
  lda #16
  sta GuestMixRegister
  lda #4
  sta GuestMixChannel
  ldx #15
  ldy #3
  cmp #4
  rts

.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
::TnExpansionSweepGate:
.scope TnSweepInlineGate
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 bne Original
 lda BassDmcActive
 beq Idle
 cmp #4                       ; original TMNT E-window owner4 only
 bne Original
 beq CheckMask
Idle:
 lda $4015                    ; unowned active DMC takes literal original
 and #$10
 bne Original
CheckMask:
 lda GuestMixMask
 and #1
 beq Original
 jmp TnExpansionSweepCall
Original:
 jmp GuestExpansionFlush
.endscope
.assert *-::TnExpansionSweepGate=38,lderror,"Real relocated38B gate"
 .res 1089-(*-::GuestAudioFinish),$ea
.endif
.endproc

; With no shared effect or ownership transition, the native register image
; already contains the complete mix. Direct register stores avoid repeating
; channel selection, unused-register checks and owner/dirty dispatch 16 times.
; Keep the original ascending write order and all length-counter retriggers.
.proc GuestAudioNativeFlush
 .repeat 16, I
  .scope
  .if I <> 9 && I <> 13
   lda GuestNativeApu+I
   cmp GuestApuLast+I
   bne WriteNative
   ldx GuestNativeDirty+I
   beq NativeDone
WriteNative:
   sta $4000+I
   sta GuestApuLast+I
NativeDone:
  .endif
 .if !::MAPPER_MMC5
  lda #0
  sta GuestNativeDirty+I
  sta GuestFxDirty+I
 .endif
  .endscope
 .endrepeat
.if ::MAPPER_MMC5
  ; Each register only reads its own dirty byte. Clear the consumed image
  ; together after the ordered hardware writes, loading zero once.
  lda #0
 .repeat 16, I
  sta GuestNativeDirty+I
  sta GuestFxDirty+I
 .endrepeat
.endif
  lda #0
  sta GuestMixOwner
  lda GuestNativeApu+15
  sta GuestMixValue
  lda #16
  sta GuestMixRegister
  lda #4
  sta GuestMixChannel
  ldx #15
  ldy #3
  cmp #4
  rts
.endproc
.if ::MAPPER_MMC5
.include "mmc5_sfx.s"
.endif
.popseg

.if ::ENABLE_MMC5_EXPANDED
.pushseg
.segment "X5_AUDIO_MIX"
; Pulse effects are already flushed on the separate MMC5 voices.
; Only native-noise ownership/change needs the ordinary APU owner loop.
.proc X5NativeNoiseMask
 ora GuestMixChanged
 and #8
 rts
.endproc
.export X5NativeNoiseMask
.popseg
.endif
