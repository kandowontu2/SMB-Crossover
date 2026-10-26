.pushseg
.segment "TMNT_SAMUS_AUDIO_COLD"
.proc SamusAudioCold
  lda CurrentBank
  pha
  lda OperMode
  jne Running
  jsr GuestNativeStatusSTA
  jmp Exit
Running:
  lda EventMusicQueue
  ora AreaMusicQueue
  and #Silence
  beq :+
    lda #1
    sta SmAudioSilenced
    jmp Mute
  :
  lda #0
  sta SmAudioRestart
  sta SmAudioFlag
  sta SmAudioMulti
  lda AreaMusicQueue
  beq Event
  lda #0
  sta SmAudioSilenced
  lda #.bank(MetroidAudio1)
  ldy #1
  ldx AreaMusicQueue
  cpx #2
  bne :+
    lda #.bank(MetroidAudio2)
    ldy #8
  :
  cpx #4
  bne :+
    lda #.bank(MetroidAudio4)
    ldy #$10
  :
  cpx #8
  bne :+
    lda #.bank(MetroidAudio1)
    ldy #$40
  :
  sta SmAudioBank
  sty SmAudioFlag
  cpx #PipeIntroMusic
  bne :+
    lda #0
    sta SmAudioFlag
    lda #$80
    sta SmAudioMulti
  :
  inc SmAudioRestart
Event:
  lda EventMusicQueue
  beq Pause
  ldx #0
  stx SmAudioSilenced
  cmp #1
  beq Death
  cmp #$40
  beq Pause                      ; Hurry cue is queued as a native beep below.
  lda #.bank(MetroidAudio1)
  sta SmAudioBank
  lda #$40                       ; Metroid item fanfare for clearing an area.
  sta SmAudioMulti
  inc SmAudioRestart
  jmp Pause
Death:
  lda SmSfx
  ora #64
  sta SmSfx
Pause:
  lda SmAudioSilenced
  bne Mute
  lda GamePauseStatus
  and #1
  beq Unpaused
  sta SmAudioPaused
Mute:
  lda #0
  jsr GuestNativeStatusSTA
  jmp Exit
Unpaused:
  lda SmAudioBank
.if ::MAPPER_MMC5
  ora #MMC5_PRG_ROM
.endif
  BankPRGA a
.if ::MAPPER_MMC5
  ; The MMC5 fixed bank has room for direct copies. Same descending byte
  ; order and exhausted X/flags as the indexed loop, with less NMI work.
 .repeat 12, I
  lda $e0+11-I
  sta SmAudioCpuZp+11-I
  lda SmAudioZp+11-I
  sta $e0+11-I
 .endrepeat
  ldx #$ff
.else
  ldx #11
Save:
  lda $e0,x
  sta SmAudioCpuZp,x
  lda SmAudioZp,x
  sta $e0,x
  dex
  bpl Save
.endif
  lda $1e
  pha
  lda $2e
  pha
  lda #0
  sta $1e
  lda FrameCounter
  sta $2e
  lda #$0f
  jsr GuestNativeStatusSTA
  lda SmAudioCurrent
  cmp SmAudioBank
  bne Init
  lda SmAudioRestart
  beq Effects
Init:
  jsr $b404
  lda SmAudioBank
  sta SmAudioCurrent
  lda #1
  sta SmAudioRam+$2c
  lda SmAudioMulti
  beq :+
    lda #0
    sta SmAudioRam+$2c
  :
  lda SmAudioFlag
  sta SmAudioRam+$85
  lda SmAudioMulti
  sta SmAudioRam+$84
Effects:
  lda #0
  ldx PlayerStatus
  beq :+
    lda #$80
  :
  sta SmAudioRam+$1f
  lda Square1SoundQueue
  and #Sfx_Fireball
  beq :+
    lda #$10
    cpx #2
    bne FireFlag
      lda #1
FireFlag:
    ora SmAudioRam+$81
    sta SmAudioRam+$81
  :
  lda SmSfx
  and #1
  beq :+
    lda SmAudioRam+$81
    ora #2
    sta SmAudioRam+$81
  :
  lda SmSfx
  and #2
  beq :+
    lda SmAudioRam+$83
    ora #2
    sta SmAudioRam+$83
  :
  lda SmSfx
  and #4
  beq :+
    lda SmAudioRam+$83
    ora #1
    sta SmAudioRam+$83
  :
  lda SmSfx
  and #8
  beq :+
    lda SmAudioRam+$80
    ora #$10
    sta SmAudioRam+$80
  :
  lda Square1SoundQueue
  and #Sfx_EnemySmack|Sfx_EnemyStomp
  beq :+
    lda SmAudioRam+$81
    ora #4
    sta SmAudioRam+$81
  :
  lda SmSfx
  and #64
  beq :+
    lda #$80
    sta SmAudioRam+$83
  :
  lda Square1SoundQueue
  and #Sfx_PipeDown_Injury
  beq :+
    lda #4
    sta SmAudioRam+$84
  :
  lda SmSfx
  and #16
  beq :+
    lda SmAudioRam+$80
    ora #8                       ; Native Metroid noise-channel walking cue.
    sta SmAudioRam+$80
  :
  lda SmSfx
  and #32                      ; Source Metroid NSF24, bypass common world Bump.
  beq :+
    lda SmAudioRam+$81
    ora #$20
    sta SmAudioRam+$81
  :
  lda EventMusicQueue
  and #$40
  beq :+
    lda SmAudioRam+$83
    ora #8
    sta SmAudioRam+$83
  :
  jsr $b3b4
  pla
  sta $2e
  pla
  sta $1e
.if ::MAPPER_MMC5
 .repeat 12, I
  lda $e0+11-I
  sta SmAudioZp+11-I
  lda SmAudioCpuZp+11-I
  sta $e0+11-I
 .endrepeat
  ldx #$ff
.else
  ldx #11
Restore:
  lda $e0,x
  sta SmAudioZp,x
  lda SmAudioCpuZp,x
  sta $e0,x
  dex
  bpl Restore
.endif
  lda #0
  sta SmAudioPaused
Exit:
  lda #0
  sta SmSfx
  sta Square1SoundQueue
  sta Square2SoundQueue
  sta NoiseSoundQueue
  sta PauseSoundQueue
  sta AreaMusicQueue
  sta EventMusicQueue
  jmp SamusAudioFixedReturn
.endproc
.export SamusAudioCold
.popseg
