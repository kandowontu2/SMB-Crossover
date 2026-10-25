; Original Gradius music over the common guest/world-effect mixer.
; This family owns the compressed-audio history while Vic Viper is active.
.pushseg
.segment "VG_AUDIO_DISPATCH"
.proc VgAudioDispatch
  lda SelectedCharacter
  cmp #18
  bne Legacy
  lda VvVariant
  bne Legacy
  BankPRGA #.bank(GradiusAudioUpdate)
  jmp GradiusAudioUpdate
Legacy:
  jmp LmNativeMusicGate
.endproc
.assert *-VgAudioDispatch=23,error,"Native audio fits the existing 24-byte C-bank tail"
.segment "VIC_NATIVE_AUDIO"
VgAudioRam = XgLzHistory
VG_RAW_APU = 0

.proc GradiusAudioUpdate
  lda #0
  sta RgAudioRequest
  lda XgAudioCharacter
  cmp #$fe                       ; Separate from all playlist-family indices.
  beq Initialized
  lda #$fe
  sta XgAudioCharacter
  lda #0
  sta RgAudioSong
  sta RgAudioSilenced
  lda #3                         ; Source Beginning of the History.
  sta RgAudioRequest
Initialized:
  lda OperMode
  jeq Mute
  lda AreaMusicQueue
  ora EventMusicQueue
  and #Silence
  beq Area
  lda #1
  sta RgAudioSilenced
Area:
  lda AreaMusicQueue
  and #$7f
  beq Event
  ldx #0
FindArea:
  lsr
  bcs AreaFound
  inx
  bne FindArea
AreaFound:
  lda Areas,x
  sta RgAudioRequest
  lda #0
  sta RgAudioSilenced
Event:
  lda EventMusicQueue
  and #$7f
  beq Pause
  ldx #0
FindEvent:
  lsr
  bcs EventFound
  inx
  bne FindEvent
EventFound:
  lda Events,x
  sta RgAudioRequest
  lda #0
  sta RgAudioSilenced
Pause:
  lda GamePauseStatus
  and #1
  jne Mute
  lda RgAudioSilenced
  jne Mute
  lda GuestNativeEnable
  cmp #15
  beq Enabled
  lda #15
  jsr GuestNativeStatusSTA
Enabled:
  lda RgAudioRequest
  beq SaveCpu
  sta RgAudioSong
  inc XgAudioSong
  lda #0
  ldx #79
ResetState:
  sta VgAudioRam,x
  dex
  bpl ResetState
  ldx #6
ResetPointers:
  sta RgAudioZp,x
  dex
  bpl ResetPointers
  ldx #15
ResetImage:
  sta GuestNativeApu,x
  lda #1
  sta GuestNativeDirty,x
  lda #0
  dex
  bpl ResetImage
SaveCpu:
  ; Only six indirect-pointer bytes need live CPU zero page. Unroll this
  ; tiny transfer so protecting interrupted gameplay costs no indexed scan.
  lda $15
  sta RgAudioCpuZp
 .macro VgBorrow Address,Offset
  lda z:Address
  sta RgAudioCpuZp+Offset
  lda RgAudioZp+Offset
  sta z:Address
 .endmacro
  VgBorrow $dd,1
  VgBorrow $de,2
  VgBorrow $f6,3
  VgBorrow $f7,4
  VgBorrow $fa,5
  VgBorrow $fb,6
  lda #0
  sta $15                        ; Pause is handled without advancing the driver.
  lda RgAudioRequest
  beq Play
  sec
  sbc #1                         ; NSF song numbering is one based.
  ldx #0
  ldy #0
  jsr GradiusNativeInit
  jmp RestoreCpu                 ; First play update follows initialization.
Play:
  jsr GradiusNativePlay
RestoreCpu:
 .macro VgRestore Address,Offset
  lda z:Address
  sta RgAudioZp+Offset
  lda RgAudioCpuZp+Offset
  sta z:Address
 .endmacro
  VgRestore $dd,1
  VgRestore $de,2
  VgRestore $f6,3
  VgRestore $f7,4
  VgRestore $fa,5
  VgRestore $fb,6
  lda RgAudioCpuZp
  sta $15
  jmp Queues
Mute:
  lda #0
  jsr GuestNativeStatusSTA
Queues:
  lda #0
  sta AreaMusicQueue
  sta EventMusicQueue
  sta Square1SoundQueue
  sta Square2SoundQueue
  sta NoiseSoundQueue
  rts
Areas:
  .byte 3,6,4,9,5,1,10
Events:
  .byte 13,13,14,14,13,14,10
.endproc
.macro VgDirectWriter Name,Offset
.proc Name
  sta GuestNativeApu+Offset
  php
  inc GuestNativeDirty+Offset
  plp
  rts
.endproc
.endmacro
VgDirectWriter VgNativeStoreSTA08,8
VgDirectWriter VgNativeStoreSTA09,9
VgDirectWriter VgNativeStoreSTA0c,12
.include "gradius-native.inc"
.popseg
