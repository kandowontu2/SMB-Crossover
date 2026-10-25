.proc ProtoNativeAudioUpdate
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
  lda ProtoAudioState
  bne ProtoAreaReady
  lda #1
  sta ProtoAudioState
  lda #0
  sta MmAudioDesiredSong
ProtoAreaReady:
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
  lda #3
  sta MmAudioEngine
  BankPRGA #.bank(ProtoMm3::_nmi_audio_processing)
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
  jsr ProtoRushLandBeginStatus
Driver3:
  lda MmAudioStart
  beq Resume3
    lda #$f0
    jsr ::Mm3::_nmi_audio_track_queue
    ldx MmAudioCurrentSong
    lda ProtoTracks,x
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
  lda ProtoAudioState
  cmp #1
  bne ProtoIntroChecked
  lda MmAudioCurrentSong
  bne ProtoIntroInterrupted
  lda #0
  ldx #7
ProtoIntroPointerLoop:
  ora Mm3AudioRam+$50,x
  dex
  bpl ProtoIntroPointerLoop
  cmp #0
  bne ProtoIntroChecked
  lda MmAudioAreaSong
  sta MmAudioDesiredSong
ProtoIntroInterrupted:
  lda #2
  sta ProtoAudioState
ProtoIntroChecked:
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
  jsr ProtoRushLandEnd
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
ProtoTracks:
  .byte 1,2,3,3,2,3,3,1,2,1,$f0
.endproc

.proc ProtoRushLandBeginStatus
  ; Exact one-call context: X=$36,C=1,Y unchanged,A=$0F before old status STA.
  lda MmRushLandPreviousMask
  beq Status
  ldx #15
RestoreMusic:
  lda MmRushLandMusic,x
  sta GuestNativeApu,x
  dex
  bpl RestoreMusic
  ldx #$36
  cpx #$36
Status:
  lda #$0f
  jmp GuestNativeStatusSTA
.endproc
.proc ProtoRushLandEnd
  lda MmRushLandRequest
  ora MmRushLandActive
  ora MmRushLandPreviousMask
  bne Live
Quiet:
  ; Exact displaced5B output: A=0,N=0,Z=1; all other registers/flags retained.
  lda #0
  sta MmAudioPaused
  rts
Live:
  php
  txa
  pha
  tya
  pha
  lda CurrentBank
  pha
  BankPRGA #.bank(BassSfxLand)
  jsr Decode
  pla
  BankPRGA a
  pla
  tay
  pla
  tax
  plp
  jmp Quiet
Decode:
  ldx #15
SaveMusic:
  lda GuestNativeApu,x
  sta MmRushLandMusic,x
  lda #0
  sta MmRushLandDirty,x
  dex
  bpl SaveMusic
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  jne Cancel
  lda CrossoverBehaviorVersion
  cmp #1
  jne Cancel
  lda MmDeathFlag
  jne Cancel
  ; Preserve the existing native higher-priority hurt/life/defeat owners.
  lda MmAudioSfx
  cmp #2
  beq Cancel
  cmp #3
  beq Cancel
  cmp #4
  beq Cancel
  cmp #8
  beq Cancel
  lda MmRushLandRequest
  beq Continue
  lda #0
  sta MmRushLandRequest
  sta MmRushLandIndex
  lda #1
  sta MmRushLandActive
Continue:
  lda MmRushLandActive
  beq Release
  ldy MmRushLandIndex
Read:
  lda BassSfxLand,y
  iny
  cmp #254
  beq FrameDone
  cmp #255
  beq Cancel
  tax
  lda BassSfxLand,y
  iny
  sta MmRushLandImage,x
  lda #1
  sta MmRushLandDirty,x
  bne Read
FrameDone:
  sty MmRushLandIndex
  ldx #15
Mix:
  txa
  and #$0c
  cmp #4
  beq Owned
  cmp #12
  bne Next
Owned:
  lda MmRushLandImage,x
  sta GuestNativeApu,x
  lda MmRushLandDirty,x
  sta GuestNativeDirty,x
  lda MmRushLandPreviousMask
  bne Next
  lda #1
  sta GuestNativeDirty,x
Next:
  dex
  bpl Mix
  lda #10
  sta MmRushLandPreviousMask
  rts
Cancel:
  lda #0
  sta MmRushLandRequest
  sta MmRushLandActive
Release:
  lda MmRushLandPreviousMask
  beq Done
  ldx #15
ReleaseLoop:
  txa
  and #$0c
  cmp #4
  beq Reload
  cmp #12
  bne NextRelease
Reload:
  lda #1
  sta GuestNativeDirty,x
NextRelease:
  dex
  bpl ReleaseLoop
  lda #0
  sta MmRushLandPreviousMask
Done:
  rts
.endproc
