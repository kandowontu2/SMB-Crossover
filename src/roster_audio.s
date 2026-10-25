; Native Contra, Zelda and Castlevania APU drivers. Shared private state is
; reset when changing character. C000 holds the wrapper while A000 plays audio.
.pushseg
.segment "SRAM"
RgAudioRam: .res $200
RgContraRam = RgAudioRam
RgZeldaRam = RgAudioRam
RgAudioZp: .res 160
RgAudioCpuZp: .res 160
RgAudioCharacter: .res 1
RgAudioSong: .res 1
RgAudioSilenced: .res 1
RgAudioRequest: .res 1
RgSfx: .res 1
.include "build/generated/guest-audio/contra.inc"
.include "build/generated/guest-audio/zelda.inc"
.include "build/generated/guest-audio/castlevania.inc"
.segment "FIXED"
.proc RosterAudioUpdate
  lda CurrentBank
  pha
  lda SelectedCharacter
  sec
  sbc #CHARACTER_BILL
  asl
  clc
  adc #$17
  pha
.if ::MAPPER_MMC5
  ora #MMC5_PRG_ROM
.endif
  BankPRGA a
  pla
  clc
  adc #1
.if ::MAPPER_MMC5
  ora #MMC5_PRG_ROM
.endif
  BankPRGC a
  jsr $dc00
  pla
  BankPRGA a
  jsr CrossoverGraphicsBank
  rts
.endproc

.macro NativeRosterWrapper Kind
.local Wrapper, ZpAddresses, ZpCount
.if Kind=2
  ZpCount=24
.else
  ZpCount=17
.endif
.proc Wrapper
  lda SelectedCharacter
  cmp RgAudioCharacter
  beq AlreadyInit
  sta RgAudioCharacter
  lda #0
  sta RgAudioSong
  sta RgAudioSilenced
  ldx #0
ClearRam:
  sta RgAudioRam,x
  sta RgAudioRam+$100,x
  inx
  bne ClearRam
  ldx #ZpCount-1
ClearZp:
  sta RgAudioZp,x
  dex
  cpx #$ff
  bne ClearZp
AlreadyInit:
  ldy #ZpCount-1
Save:
  ldx ZpAddresses,y
  lda $00,x
  sta RgAudioCpuZp,y
  lda RgAudioZp,y
  sta $00,x
  dey
  cpy #$ff
  bne Save
  lda #0
  sta RgAudioRequest
.if Kind=2
  sta $22                       ; Castlevania pause flag
.elseif Kind=0
  sta $25                       ; Contra pause flag
.else
  sta $e0                       ; Zelda pause flag; engine overwrites its pointer
.endif
  lda OperMode
  jeq Mute
  lda GamePauseStatus
  and #1
  jne Mute
  lda AreaMusicQueue
  ora EventMusicQueue
  and #Silence
  beq Music
  lda #1
  sta RgAudioSilenced
Music:
  lda AreaMusicQueue
  and #$7f
  beq Event
  lda #0
  sta RgAudioSilenced
  ldx #0
  lda AreaMusicQueue
MusicIndex:
  lsr
  bcs FoundArea
  inx
  bne MusicIndex
FoundArea:
  lda Areas,x
  sta RgAudioRequest
Event:
  lda EventMusicQueue
  and #$7f
  beq PlayMusic
  lda #0
  sta RgAudioSilenced
  lda EventMusicQueue
  ldx #0
EventIndex:
  lsr
  bcs FoundEvent
  inx
  bne EventIndex
FoundEvent:
  lda Events,x
  beq PlayMusic
  sta RgAudioRequest
PlayMusic:
  lda RgAudioSilenced
  jne Mute
  lda #$0f
  jsr GuestNativeStatusSTA
  lda RgAudioRequest
  beq Effects
  sta RgAudioSong
.if Kind=0
  jsr ContraNative::init_pulse_and_noise_channels
  lda RgAudioRequest
  jsr ContraNative::init_sound_code_vars
.elseif Kind=1
  sta ZeldaNative::musicRequest
.else
  jsr CvAudioInit
.endif
Effects:
  lda RgSfx
  and #1
  beq OtherEffects
.if Kind=0
  ldx PlayerStatus
  lda Shots,x
  jsr ContraNative::init_sound_code_vars
.elseif Kind=1
  lda #1
  sta ZeldaNative::soundEffectRequest
.else
  lda #$0b
  jsr CvAudioInit
.endif
OtherEffects:
  lda Square1SoundQueue
  and #Sfx_EnemySmack|Sfx_EnemyStomp
  beq Pickup
.if Kind=0
  lda #$19
  jsr ContraNative::init_sound_code_vars
.elseif Kind=1
  lda #$10
  sta ZeldaNative::soundEffectRequest
.else
  lda #$0d
  jsr CvAudioInit
.endif
Pickup:
  lda Square2SoundQueue
  and #Sfx_PowerUpGrab|Sfx_ExtraLife
  beq Tick
.if Kind=0
  lda #$1f
  jsr ContraNative::init_sound_code_vars
.elseif Kind=1
  lda #$10
  sta ZeldaNative::musicEffectRequest
.else
  lda #$16
  jsr CvAudioInit
.endif
Tick:
.if Kind=0
  jsr ContraNative::handle_sound_slots
.elseif Kind=1
  jsr ZeldaNative::process_audio
.else
.if ::ENABLE_MMC5_EXPANDED
  jsr Cv3MusicAndNoiseTick
.else
  jsr CvAudioPlay
.endif
.endif
  jmp Restore
Mute:
  lda #0
  jsr GuestNativeStatusSTA
Restore:
.if Kind=2 .and ::ENABLE_MMC5_EXPANDED
  jsr Cv3RestoreAudioZp
  jmp AudioRestored
  .res 14,$ea ; old20-byte loop footprint: no original following PC moves
.else
  ldy #ZpCount-1
Load:
  ldx ZpAddresses,y
  lda $00,x
  sta RgAudioZp,y
  lda RgAudioCpuZp,y
  sta $00,x
  dey
  cpy #$ff
  bne Load
.endif
AudioRestored:
  lda #0
  sta RgSfx
  sta Square1SoundQueue
  sta Square2SoundQueue
  sta NoiseSoundQueue
  sta PauseSoundQueue
  sta EventMusicQueue
  sta AreaMusicQueue
  rts
.if Kind=0
Areas: .byte $2a,$36,$3e,$3a,$32,$26,$36
Events:.byte $1c,$4e,$4a,$46,$4e,$46,0
Shots: .byte $0a,$0c,$12
.elseif Kind=1
Areas: .byte 1,$80,$20,$20,1,8,4
Events:.byte $10,$40,4,4,$40,4,0
.else
Areas: .byte $2a,$30,$33,$3c,$30,$27,$42
Events:.byte $4e,$51,$4b,$48,$51,$48,$3f
.endif
.endproc
ZpAddresses:
.if Kind=0
.repeat 16,I
  .byte $e0+I
.endrepeat
.byte $25
.elseif Kind=1
.byte $00,$01,$02,$03,$04,$05
.repeat 10,I
  .byte $66+I
.endrepeat
.byte $e0
.else
.byte $ba,$bb,$bc,$bd,$be,$bf
.repeat 16,I
  .byte $e0+I
.endrepeat
.byte $22,$60
.endif
.endmacro
.segment "CONTRA_WRAP"
NativeRosterWrapper 0
.segment "ZELDA_WRAP"
NativeRosterWrapper 1
.segment "CV_WRAP"
NativeRosterWrapper 2
.popseg
