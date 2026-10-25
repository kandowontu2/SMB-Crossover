; Native APU drivers for the music in the pinned hosted build.
.pushseg
.segment "SRAM"
.align 256
MmAudioRamStart:
Mm2AudioRam: .res 128
Mm3AudioRam: .res 128
MmAudioZp:
Mm3AudioZp: .res $36
Mm2AudioZp: .res $36
MmAudioCpuZp: .res $36
MmAudioCurrentSong: .res 1
MmAudioDesiredSong: .res 1
MmAudioAreaSong: .res 1
MmAudioEngine: .res 1
MmAudioStart: .res 1
MmAudioPaused: .res 1
MmAudioHurryTimer: .res 1
MmAudioSfx: .res 1
MmAudioShotType: .res 1
MmAudioChargeAge: .res 1
MmAudioSfxMask: .res 1
MmAudioLastMask: .res 1
MmAudioLastGround: .res 1

; Explicit new semantics inside previously unused MM512B slab padding.
MmRushLandRequest: .res 1
MmRushLandIndex: .res 1
MmRushLandActive: .res 1
MmRushLandPreviousMask: .res 1
MmRushLandMusic: .res 16
MmRushLandImage: .res 16
MmRushLandDirty: .res 16
.res $200 - (* - MmAudioRamStart)
MmAudioRamEnd:
.include "audio/megaman2/imported.s"
.include "build/generated/guest-audio/megaman3.inc"

.segment "FIXED"
.proc MegaManAudioInit
  lda #0
  ldx #0
Loop:
  sta MmAudioRamStart,x
  sta MmAudioRamStart+256,x
  inx
  bne Loop
  lda #$ff
  sta MmAudioCurrentSong
  rts
.endproc

.proc MegaManAudioUpdate
 .if ::ENABLE_MMC5_EXPANDED
  lda #.bank(ProtoNmiAudioCore) | MMC5_PRG_ROM
  sta MMC5_PRG_BANK_A
  jsr ProtoNmiAudioCore
  sta MMC5_PRG_BANK_A
  jmp CrossoverGraphicsBank
  .byte $ea,$ea
  .assert *-MegaManAudioUpdate=16,error,"Audio resident span unchanged"
 .else
  BankPRGC #.bank(MegaManAudioNativeUpdate)
  jsr MegaManAudioNativeUpdate
  jmp CrossoverGraphicsBank
 .endif
.endproc
.segment "GUEST_GFX"
.proc MegaManAudioNativeUpdate
  lda CurrentBank
  pha
  lda #0
  sta MmAudioStart
  sta MmAudioSfx
  lda OperMode
  bne :+
    jsr GuestNativeStatusSTA
    jmp Exit
  :
  lda EventMusicQueue
  beq Area
  ldy #0
  asl
  bcs SetEvent
  ldy #8
  asl
  bcs Hurry
  ldy #6
  asl
  bcs SetEvent
  ldy #7
  asl
  bcs SetEvent
  ldy #6
  asl
  bcs SetEvent
  asl
  bcs SetEvent
  ldy #7
  asl
  bcs SetEvent
  ldy #10
  bne SetEvent
Hurry:
  lda #166
  sta MmAudioHurryTimer
SetEvent:
  sty MmAudioDesiredSong
  inc MmAudioStart
  jmp Pause
Area:
  lda AreaMusicQueue
  beq Timer
  ldy #0
  asl
  bcs SetArea
  ldy #5
  asl
  bcs SetArea
  ldy #9
  asl
  bcs SetArea
  ldy #1
  asl
  bcs SetArea
  ldy #4
  asl
  bcs SetArea
  ldy #2
  asl
  bcs SetArea
  ldy #3
  asl
  bcs SetArea
  ldy #1
SetArea:
  sty MmAudioDesiredSong
  sty MmAudioAreaSong
  inc MmAudioStart
Timer:
  lda GamePauseStatus
  and #1
  bne Pause
  lda MmAudioHurryTimer
  beq Pause
  dec MmAudioHurryTimer
  bne Pause
    lda MmAudioAreaSong
    sta MmAudioDesiredSong
    inc MmAudioStart
Pause:
  lda GamePauseStatus
  and #1
  beq Unpaused
    sta MmAudioPaused
    lda #0
    jsr GuestNativeStatusSTA
    jmp Exit
Unpaused:
  lda MmAudioDesiredSong
  cmp MmAudioCurrentSong
  bne Start
  lda MmAudioStart
  beq Continue
Start:
  lda MmAudioDesiredSong
  sta MmAudioCurrentSong
  lda #1
  sta MmAudioStart
  lda #0
  ldx #$35
ClearZp:
  sta Mm3AudioZp,x
  sta Mm2AudioZp,x
  dex
  bpl ClearZp
  ldx #127
ClearRam:
  sta Mm2AudioRam,x
  sta Mm3AudioRam,x
  dex
  bpl ClearRam
Continue:
  lda #2
  ldx MmAudioCurrentSong
  cpx #2
  bcs :+
    lda #3
  :
  sta MmAudioEngine
  BankPRGA #.bank(::Mm3::_nmi_audio_processing)
SaveZp:
  ; These drivers keep state in zero page. Swap it around each NMI so SMB's
  ; main-thread state is restored byte for byte, even inside collision code.
  lda $41
  pha
  lda #0
  sta $41
  ; Direct swaps retain every byte and its order while saving the indexing
  ; and loop overhead on every hardware frame, including lag NMIs.
 .repeat $36, I
  lda $c0+I
  sta MmAudioCpuZp+I
 .if I < $1d
  ; MM3 owns C0..DC. Its saved DD..F5 bytes are never consumed or
  ; modified by the driver; MM2 separately owns E0..F5 below.
  lda Mm3AudioZp+I
  sta $c0+I
 .endif
 .endrepeat
  ldx #$36
  cpx #$36
  lda #$0f
  jsr MegaManRushLandBeginStatus
Driver3:
  lda MmAudioStart
  beq Resume3
    lda #$f0
    jsr ::Mm3::_nmi_audio_track_queue
    lda MmAudioCurrentSong
    cmp #1
    bne Resume3
    lda #0
    jsr ::Mm3::_nmi_audio_track_queue
Resume3:
  lda MmAudioPaused
  beq :+
    jsr ::Mm3::_init_channel_pointers_common
  :
  jsr Effects
  jsr Charge
  ldy MmAudioSfx
  beq Process3
  lda Effects3-1,y
  jsr ::Mm3::_nmi_audio_track_queue
Process3:
  lda SsAudioRequest
  beq :+
    sec
    sbc #1
    jsr ::Mm3::_nmi_audio_track_queue
    lda #0
    sta SsAudioRequest
  :
  jsr ::Mm3::_nmi_audio_processing
  lda ::Mm3::zsfx_channel
  and #$0f
  sta MmAudioSfxMask
 .repeat $36, I
 .if ($35-I) < $1d
  lda $f5-I
  sta Mm3AudioZp+$35-I
 .endif
 .endrepeat
  ldx #$ff
  lda MmAudioEngine
  cmp #2
  jne RestoreCpu
  ; MM3 owns the active effect channels. Restore MM2's high frequency
  ; registers when a channel returns to music, even if its note is unchanged.
  lda MmAudioSfxMask
  cmp MmAudioLastMask
  bne Invalidate2
  lda MmAudioPaused
  beq Load2
Invalidate2:
  lda #$ff
  sta Mm2AudioRam+$1c
  sta Mm2AudioRam+$3b
  sta Mm2AudioRam+$5a
  sta Mm2AudioRam+$79
Load2:
  lda MmAudioSfxMask
  sta MmAudioLastMask
  BankPRGA #.bank(::Mm2::_nmi_audio_processing)
 .repeat $16, I
  lda Mm2AudioZp+$35-I
  sta $f5-I
 .endrepeat
  ldx #$ff
  jsr ::Mm2::_nmi_audio_processing
  lda MmAudioStart
  beq Save2
  ldx MmAudioCurrentSong
  lda Tracks2,x
  jsr ::Mm2::_nmi_audio_track_queue
Save2:
 .repeat $16, I
  lda $f5-I
  sta Mm2AudioZp+$35-I
 .endrepeat
  ldx #$ff
RestoreCpu:
  lda MmAudioEngine
  cmp #2
  bne RestoreMm3Cpu
 .repeat $16, I
  lda MmAudioCpuZp+$35-I
  sta $f5-I
 .endrepeat
RestoreMm3Cpu:
 .repeat $1d, I
  lda MmAudioCpuZp+$1c-I
  sta $dc-I
 .endrepeat
  ldx #$ff
  pla
  sta $41
  jsr MegaManRushLandEnd
  nop
  nop
Exit:
  lda #0
  sta Square1SoundQueue
  sta Square2SoundQueue
  sta NoiseSoundQueue
  sta PauseSoundQueue
  sta AreaMusicQueue
  sta EventMusicQueue
  pla
  BankPRGA a
  rts
Effects:
  lda Player_State
  beq Land
  lda #0
  sta MmAudioLastGround
  beq WeaponEffects
Land:
  lda MmAudioLastGround
  bne WeaponEffects
  lda #1
  sta MmAudioLastGround
  lda GameEngineSubroutine
  cmp #8
  bne WeaponEffects
  lda #9
  sta MmAudioSfx
WeaponEffects:
  lda Square1SoundQueue
  and #Sfx_Fireball
  beq :+
    lda #1
    sta MmAudioSfx
    lda MmAudioShotType
    cmp #1
    beq :+
    cmp #4
    beq :+
      lda #7
      sta MmAudioSfx
  :
  lda Square1SoundQueue
  and #Sfx_EnemySmack|Sfx_EnemyStomp
  beq :+
    lda #2
    sta MmAudioSfx
  :
  lda Square1SoundQueue
  and #Sfx_PipeDown_Injury
  beq :+
    lda #3
    sta MmAudioSfx
  :
  lda Square2SoundQueue
  and #Sfx_ExtraLife
  beq :+
    lda #4
    sta MmAudioSfx
  :
  lda EventMusicQueue
  and #1
  beq :+
    lda #8
    sta MmAudioSfx
  :
  rts
Charge:
  lda MmChargeFrames
  cmp #33
  bcs Charging
  lda MmAudioChargeAge
  beq ChargeDone
  lda #0
  sta MmAudioChargeAge
  ; A release must stop both a rising tone and an indefinitely looping tone.
  lda ::Mm3::zsfx_priority
  cmp #8
  bcs ChargeDone
    lda #$f1
    jmp ::Mm3::_nmi_audio_track_queue
Charging:
  lda MmAudioChargeAge
  bne ChargeTimer
  lda MmAudioSfx
  bne ChargeDone
    lda #5
    sta MmAudioSfx
ChargeTimer:
  lda MmAudioChargeAge
  cmp #76
  bcs ChargeLoop
  inc MmAudioChargeAge
  bne ChargeDone
ChargeLoop:
  lda ::Mm3::zsfx_priority
  beq StartLoop
  lda MmAudioChargeAge
  cmp #76
  bne ChargeDone
StartLoop:
  lda MmAudioSfx
  bne ChargeDone
    lda #6
    sta MmAudioSfx
    lda #77
    sta MmAudioChargeAge
ChargeDone:
  rts
Tracks2:
  .byte $ff,0,0,7,11,13,21,15,23,10,65
Effects3:
  .byte 21,24,22,20,57,58,59,23,19
 .if ::MAPPER_MMC3
  ; Keep every foreign function/address literal. Unreachable tail padding
  ; occupies only bytes removed from this private audio closure.
  .res 258, $ea
 .endif
.endproc

; Preserve registers and flags exactly as a native STA would. The MM2 driver
; still advances every music envelope while a channel belongs to an effect.
.segment "FIXED"
.macro MmFilteredWrite Address
  php
  pha
  tya
  pha
  txa
  lsr
  lsr
  tay
  lda MmAudioChannelBits,y
  and MmAudioSfxMask
  bne :+
    pla
    tay
    pla
    .if Address=$4000
.if ::MAPPER_MMC5
      sta GuestNativeApu+$00,x
      inc GuestNativeDirty+$00,x
.else
      jsr GuestNativeStoreSTA00X
.endif
    .else
.if ::MAPPER_MMC5
      sta GuestNativeApu+$01,x
      inc GuestNativeDirty+$01,x
.else
      jsr GuestNativeStoreSTA01X
.endif
    .endif
    plp
    rts
  :
  pla
  tay
  pla
  plp
  rts
.endmacro
.proc MegaManAudioWrite0
  MmFilteredWrite $4000
.endproc
.proc MegaManAudioWrite1
  MmFilteredWrite $4001
.endproc
.proc MegaManAudioStatus
  php
  pha
  ora MmAudioSfxMask
  jsr GuestNativeStatusSTA
  pla
  plp
  rts
.endproc
MmAudioChannelBits: .byte 1,2,4,8
.popseg

