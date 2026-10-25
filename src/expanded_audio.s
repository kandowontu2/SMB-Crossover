.pushseg
.segment "ZEROPAGE"
; The decoder owns these bytes only during expanded-character audio. Native
; drivers for other characters restore borrowed CPU zero page, and a change
; of character restarts the decoder before using its history state.
XgLzFlags: .res 1
XgLzBits: .res 1
XgLzRemaining: .res 1
XgLzPosition: .res 2
XgLzCopy: .res 2
XgLzDistance: .res 2
XgLzValue: .res 1
XgLzSavedX: .res 1
XgLzSavedY: .res 1
XgAudioZeroPageEnd:
.assert XgLzFlags = XgAudioPtr+2, error, "Persistent audio zero page must be contiguous"
.segment "SRAM"
XgMusicApu: .res 16
XgAudioPreviousSfx: .res 1
XgAudioBase: .res 1
XgAudioSelection: .res 1
XgAudioEventSelection: .res 1
XgAudioStatus: .res 1
XgAudioDepth: .res 1
XgAudioStackLo: .res 32
XgAudioStackHi: .res 32
XgAudioStackBank: .res 32
.include "crossover_helper_ram.s"
.align $100
XgLzHistory: .res 2048
.segment "LOWCODE"
.proc ExpandedAudioUpdate
  lda CurrentBank
  pha
  BankPRGC #.bank(ExpandedAudioTick)
.if ::ENABLE_MMC5_EXPANDED
  jsr VgAudioDispatch
.else
  jsr ExpandedAudioTick
.endif
::ExpandedAudioDecoded:
.if ::ENABLE_MMC5_EXPANDED
  jsr KbAudioFamily
.else
  lda SelectedCharacter
.endif
  cmp #CHARACTER_BASS
  bne :+
    BankPRGC #.bank(BassNativeAudioTick)
    jsr BassNativeAudioTick
  :
  pla
  BankPRGA a
  jsr CrossoverGraphicsBank
  rts
.endproc
.include "expanded_music.inc"
.segment "XG_AUDIO"
.proc ExpandedAudioTick
.if ::ENABLE_MMC5_EXPANDED
  jsr KbAudioFamily
.else
  lda SelectedCharacter
.endif
  cmp XgAudioCharacter
  bne Init
  lda AreaMusicQueue
  and #$7f
  beq Pause
Init:
.if ::ENABLE_MMC5_EXPANDED
  jsr KbAudioFamily
.else
  lda SelectedCharacter
.endif
  sta XgAudioCharacter
  lda #0
  sta XgAudioDelay
  sta XgAudioEvent
  sta XgAudioPreviousSfx
  sta XgAudioDepth
  jsr ResetLz
  ldx #15
Clear:
  sta XgMusicApu,x
  sta GuestNativeApu,x
  dex
  bpl Clear
  lda #15
  sta XgAudioStatus
.if ::ENABLE_MMC5_EXPANDED
  jsr KbAudioFamily
.else
  lda SelectedCharacter
.endif
  sec
  sbc #CHARACTER_PIT
  sta XgAudioBase
  asl
  asl
  asl
  sec
  sbc XgAudioBase
  sta XgAudioBase
  ldx #0
  lda AreaMusicQueue
  and #$7f
  beq AreaIndex
FindArea:
  lsr
  bcs AreaIndex
  inx
  bne FindArea
AreaIndex:
  txa
  clc
  adc XgAudioBase
  sta XgAudioSelection
  jsr Restart
Pause:
  lda GamePauseStatus
  and #1
  jne Done
  lda AreaMusicQueue
  ora EventMusicQueue
  and #Silence
  beq IncomingEvent
  lda #3
  sta XgAudioEvent
IncomingEvent:
  lda EventMusicQueue
  and #$7f
  beq EventState
  ldx #0
FindEvent:
  lsr
  bcs SetEvent
  inx
  bne FindEvent
SetEvent:
  txa
  clc
  adc XgAudioBase
  tax
  stx XgAudioEventSelection
  lda XgEventBanks,x
  sta XgAudioBank
  lda XgEventLo,x
  sta XgAudioPtr
  lda XgEventHi,x
  sta XgAudioPtr+1
  lda #0
  sta XgAudioDelay
  sta XgAudioDepth
  jsr ResetLz
  jsr ClearImage
  lda #15
  sta XgAudioStatus
  lda #1
  sta XgAudioEvent
  lda EventMusicQueue
  and #TimeRunningOutMusic
  beq EventState
  lda #4                         ; Hurry selects its own looping source song.
  sta XgAudioEvent
EventState:
  lda XgAudioEvent
  cmp #2
  bcc Enabled
  cmp #4
  beq Enabled
  lda #0
  jsr GuestNativeStatusSTA
  jmp ClearQueues
Enabled:
  lda XgAudioStatus
  jsr GuestNativeStatusSTA
Advance:
  lda XgAudioBank
.if ::MAPPER_MMC5
  ora #MMC5_PRG_ROM
.endif
  BankPRGA a
  lda XgAudioDelay
  beq CodecCommands
  dec XgAudioDelay
  jmp ClearQueues
CodecCommands:
.if ::ENABLE_MMC5_EXPANDED
  lda XgAudioCharacter
  cmp #13
  bcc Commands
  jmp MaskFrame
.endif
Commands:
  jsr Byte
  cmp #$ff
  beq Loop
  cmp #$fe
  jeq ClearQueues
  cmp #$1f
  jeq ReturnMacro
  cmp #$1c
  jeq LoopMusic
  cmp #$20
  jcs Macro
  cmp #$1d
  bne Register
  jsr Byte
  sec
  sbc #1
  sta XgAudioDelay
  jmp ClearQueues
Loop:
  lda XgAudioEvent
  beq LoopMusic
  cmp #4
  beq LoopEvent
  lda #2
  sta XgAudioEvent
  lda #0
  jsr GuestNativeStatusSTA
  jmp ClearQueues
LoopMusic:
  jsr ResetLz
  ldx XgAudioSelection
  lda XgLoopBanks,x
  sta XgAudioBank
  lda XgLoopLo,x
  sta XgAudioPtr
  lda XgLoopHi,x
  sta XgAudioPtr+1
  jsr MapAudioBank
  jmp CodecCommands
LoopEvent:
  jsr ResetLz
  ldx XgAudioEventSelection
  lda XgEventLoopBanks,x
  sta XgAudioBank
  lda XgEventLoopLo,x
  sta XgAudioPtr
  lda XgEventLoopHi,x
  sta XgAudioPtr+1
  jsr MapAudioBank
  jmp CodecCommands
Register:
  tax
  jsr Byte
  cpx #21
  bne Store
  and #15
  sta XgAudioStatus
  jsr GuestNativeStatusSTA
  jmp Commands
Store:
  sta XgMusicApu,x
  sta GuestNativeApu,x
  inc GuestNativeDirty,x
  jmp Commands
.if ::ENABLE_MMC5_EXPANDED
MaskFrame:
  ; Dedicated frame masks need one dispatch per frame, with no macro stack.
  ; Reuse three bytes of that inactive stack rather than growing audio RAM.
  jsr Byte
  cmp #$ff
  jeq Loop
  cmp #$fe
  jeq LoopMusic
  cmp #$80
  bcc EmptyFrames
  cmp #$82
  jcs StopCorruptStream
  sta XgAudioStackLo+2
  jsr Byte
  sta XgAudioStackLo
  jsr Byte
  sta XgAudioStackLo+1
  ldx #0
MaskRegister:
  lsr XgAudioStackLo+1
  ror XgAudioStackLo
  bcc MaskNext
  jsr Byte
  sta XgMusicApu,x
  sta GuestNativeApu,x
  inc GuestNativeDirty,x
MaskNext:
  inx
  cpx #16
  bne MaskRegister
  lda XgAudioStackLo+2
  and #1
  jeq ClearQueues
  jsr Byte
  and #15
  sta XgAudioStatus
  jsr GuestNativeStatusSTA
  jmp ClearQueues
EmptyFrames:
  sec
  sbc #1
  sta XgAudioDelay
  jmp ClearQueues
.endif
ClearQueues:
  lda #0
  sta AreaMusicQueue
  sta EventMusicQueue
  sta Square1SoundQueue
  sta Square2SoundQueue
  sta NoiseSoundQueue
Done:
  rts
Restart:
  jsr ResetLz
  ldx XgAudioSelection
  lda XgAreaBanks,x
  sta XgAudioBank
  lda XgAreaLo,x
  sta XgAudioPtr
  lda XgAreaHi,x
  sta XgAudioPtr+1
  jsr MapAudioBank
  inc XgAudioSong
  rts
Macro:
  sec
  sbc #$20
  tay
  ldx XgAudioDepth
  cpx #32
  jcs StopCorruptStream
  lda XgAudioPtr
  sta XgAudioStackLo,x
  lda XgAudioPtr+1
  sta XgAudioStackHi,x
  lda XgAudioBank
  sta XgAudioStackBank,x
  inc XgAudioDepth
  lda XgMacroLo,y
  sta XgAudioPtr
  lda XgMacroHi,y
  sta XgAudioPtr+1
  lda #.bank(XgMacroLo)
  sta XgAudioBank
  jsr MapAudioBank
  jmp Commands
ReturnMacro:
  lda XgAudioDepth
  beq StopCorruptStream
  dec XgAudioDepth
  ldx XgAudioDepth
  lda XgAudioStackLo,x
  sta XgAudioPtr
  lda XgAudioStackHi,x
  sta XgAudioPtr+1
  lda XgAudioStackBank,x
  sta XgAudioBank
  jsr MapAudioBank
  jmp Commands
StopCorruptStream:
  lda #3
  sta XgAudioEvent
  jmp ClearQueues
MapAudioBank:
  lda XgAudioBank
.if ::MAPPER_MMC5
  ora #MMC5_PRG_ROM
.endif
  BankPRGA a
  rts
ClearImage:
  ldx #15
  lda #0
ClearImageLoop:
  sta XgMusicApu,x
  sta GuestNativeApu,x
  lda #1
  sta GuestNativeDirty,x
  lda #0
  dex
  bpl ClearImageLoop
  rts
Byte:
  stx XgLzSavedX
  sty XgLzSavedY
  lda XgAudioDepth
  bne Uncompressed
  jsr LzByte
  jmp ByteResult
Uncompressed:
  jsr RawByte
ByteResult:
  sta XgLzValue
  ldx XgLzSavedX
  ldy XgLzSavedY
  lda XgLzValue
  rts
ResetLz:
  lda #0
  sta XgLzBits
  sta XgLzRemaining
  sta XgLzPosition
  lda #>XgLzHistory
  sta XgLzPosition+1
  lda #0                        ; Callers also use ResetLz to clear A.
  rts
LzByte:
  lda XgLzRemaining
  bne CopyLz
  lda XgLzBits
  bne LzToken
  jsr RawByte
  sta XgLzFlags
  lda #8
  sta XgLzBits
LzToken:
  dec XgLzBits
  lsr XgLzFlags
  bcs LzMatch
  jsr RawByte
  jmp WriteHistory
LzMatch:
  jsr RawByte
  sta XgLzDistance
  jsr RawByte
  pha
  and #7
  sta XgLzDistance+1
  pla
  lsr
  lsr
  lsr
  clc
  adc #3
  sta XgLzRemaining
  clc                           ; pos - (encoded distance + 1).
  lda XgLzPosition
  sbc XgLzDistance
  sta XgLzCopy
  lda XgLzPosition+1
  sbc XgLzDistance+1
  cmp #>XgLzHistory
  bcs :+
    clc
    adc #8
  :
  sta XgLzCopy+1
CopyLz:
  ldy #0
  lda (XgLzCopy),y
  tax
  inc XgLzCopy
  bne :+
    inc XgLzCopy+1
    lda XgLzCopy+1
    cmp #>XgLzHistory+8
    bne :+
      lda #>XgLzHistory
      sta XgLzCopy+1
  :
  dec XgLzRemaining
  txa
WriteHistory:
  ldy #0
  sta (XgLzPosition),y
  tax
  inc XgLzPosition
  bne :+
    inc XgLzPosition+1
    lda XgLzPosition+1
    cmp #>XgLzHistory+8
    bne :+
      lda #>XgLzHistory
      sta XgLzPosition+1
  :
  txa
  rts
RawByte:
  ldy #0
  lda (XgAudioPtr),y
  pha
  inc XgAudioPtr
  bne EndByte
  inc XgAudioPtr+1
  lda XgAudioPtr+1
  cmp #$c0
  bne EndByte
  lda #$a0
  sta XgAudioPtr+1
  inc XgAudioBank
  lda XgAudioBank
.if ::MAPPER_MMC5
  ora #MMC5_PRG_ROM
.endif
  BankPRGA a
EndByte:
  pla
  rts
.endproc
.popseg

.if ::ENABLE_MMC5_EXPANDED
.pushseg
.segment "XG_AUDIO"
.proc KbAudioFamily
  lda SelectedCharacter
  cmp #CHARACTER_KIRBY
  bne :+
  lda KbVariant
  beq Kirby
  lda #14
  rts
Kirby:
  lda #13
  rts
: lda SelectedCharacter
  cmp #CHARACTER_TMNT
  bne :+
  lda #CHARACTER_RYGAR
  rts
: cmp #CHARACTER_KIRBY
  bcc Done
  lda #CHARACTER_PIT
Done:rts
.endproc
.popseg
.endif
