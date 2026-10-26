; Private original Rescue Rangers music adapter; no shared farcall/SMC.
.pushseg
ChNativeSavedPointer=XgLzHistory+$a4
ChNativePending=XgLzHistory+$a8
ChNativeResume=XgLzHistory+$a9
ChNativePrivatePointer=XgLzHistory+$aa
.segment "CHIP_NATIVE_SERVICE"
ChNativeService:
  lda RgAudioRequest
  beq Play
  sec
  sbc #1
  jsr ChNativeSourceInit
  rts
Play:
  jmp ChNativeSourcePlay
.assert * <= $ae00,lderror,"Chip service stays before original data"
.segment "CHIP_NATIVE_BRIDGE"
ChNativeMacTail:
  BankPRGA #.bank(LmNativeMusicUpdate)
  jmp LmNativeMusicUpdate
ChNativeBridge:
  lda CurrentBank
  pha
  lda #.bank(ChNativeService)|MMC5_PRG_ROM
  sta CurrentBank
  sta MMC5_PRG_BANK_A
  jsr ChNativeService
  pla
  sta CurrentBank
  sta MMC5_PRG_BANK_A
  rts
.assert * <= $e000,lderror,"Chip bridge stays inside existing C94 tail"
.segment "CHIP_NATIVE_ADAPTER"
.proc ChNativeAudioUpdate
  ; The caller saved its A bank. C94 contains the data/roundtrip bridge.
  BankPRGC #.bank(ChNativeBridge)
  lda SelectedCharacter
  cmp #15
  jeq MacTail
  lda #.bank(ChNativeAudioUpdate)|MMC5_PRG_ROM
  sta CurrentBank
  lda #0
  sta RgAudioRequest
  lda XgAudioCharacter
  cmp #$f8
  beq Initialized
  lda #$f8
  sta XgAudioCharacter
  lda #0
  sta RgAudioSong
  sta RgAudioSilenced
  sta XgAudioEvent
  sta ChNativeResume
  lda #2
  sta ChNativePending
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
  sta ChNativePending
  lda #0
  sta RgAudioSilenced
  sta XgAudioEvent
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
  sta ChNativePending
  lda #0
  sta RgAudioSilenced
  lda #1
  sta XgAudioEvent
Pause:
  lda GamePauseStatus
  and #1
  jne Mute
  lda RgAudioSilenced
  jne Mute
  lda ChNativePending
  sta RgAudioRequest
  beq Resume
  sta RgAudioSong
  inc XgAudioSong
  lda #0
  ldx #$a3
ClearSource:
  sta XgLzHistory,x
  dex
  cpx #$ff
  bne ClearSource
  ldx #3
ClearPrivatePointer:
  sta ChNativePrivatePointer,x
  dex
  bpl ClearPrivatePointer
  ldx #15
ClearImage:
  sta GuestNativeApu,x
  lda #1
  sta GuestNativeDirty,x
  lda #0
  dex
  bpl ClearImage
  sta ChNativePending
Resume:
  lda ChNativeResume
  beq Borrow
  lda #0
  sta ChNativeResume
  ldx #15
  lda #1
RestoreImage:
  sta GuestNativeDirty,x
  dex
  bpl RestoreImage
  lda #15
  jsr GuestNativeStatusSTA
Borrow:
 .macro BorrowPointer Address,Offset
  lda Address
  sta ChNativeSavedPointer+Offset
  lda ChNativePrivatePointer+Offset
  sta Address
 .endmacro
  BorrowPointer ChNativePointer,0
  BorrowPointer ChNativePointer+1,1
  BorrowPointer ChNativeMappedC5,2
  BorrowPointer ChNativeMappedC5+1,3
  ldx #0
  ldy #0
  jsr ChNativeBridge
 .macro RestorePointer Address,Offset
  lda Address
  sta ChNativePrivatePointer+Offset
  lda ChNativeSavedPointer+Offset
  sta Address
 .endmacro
  RestorePointer ChNativePointer,0
  RestorePointer ChNativePointer+1,1
  RestorePointer ChNativeMappedC5,2
  RestorePointer ChNativeMappedC5+1,3
  jmp Queues
Mute:
  lda #1
  sta ChNativeResume
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
MacTail:
  jmp ChNativeMacTail
Areas: .byte 2,4,5,8,12,13,14
Events:.byte 15,16,11,11,16,11,10
.endproc
.popseg
