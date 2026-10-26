; Native TMNT music owns the inactive decoder RAM/ZP only for character19.
TnAudioRam=XgLzHistory
TnAudioZp=XgAudioPtr
.assert XgAudioZeroPageEnd-XgAudioPtr=14,error,"Native music owns the inactive fourteen-byte decoder ZP slab"
TnAudioRequest=XgLzHistory+$cc
TnAudioSong=XgLzHistory+$cd
TnAudioSilenced=XgLzHistory+$ce
TnAudioPaused=XgLzHistory+$cf
TnAudioDmcRegs=XgLzHistory+$d0
TnAudioWriterA=XgLzHistory+$d4
TnAudioDacHold=XgLzHistory+$d5
TnAudioVirtualEnable=XgLzHistory+$d6
TnAudioEnableHeld=XgLzHistory+$d7
; This byte is outside the compressed history, which another guest can reuse
; before the last buffered DMC bits have drained. Bass reserves but never reads
; or writes the remaining ten bytes in BassAudioSavedApu.
TnDmcDrain=BassAudioSavedApu+6
TN_RAW_APU=0
.export TnAudioRam,TnAudioZp,TnAudioRequest,TnAudioSong,TnAudioSilenced,TnAudioPaused
.export TnAudioDmcRegs,TnAudioDacHold,TnAudioVirtualEnable,TnAudioEnableHeld
.export TnDmcDrain
.include "tmnt-native.inc"
.pushseg
.segment "TMNT_NATIVE_AUDIO_WRITERS"
.include "tmnt_audio_writers.s"
.include "tmnt_audio_multiply.s"
.include "tmnt_audio_parser.s"
.include "tmnt_parser_math_next.s"
.include "tmnt_parser_channels.s"
.include "tmnt_parser_unrolled.s"
.include "tmnt_parser_tail_writers.s"
.include "tmnt_source_channel_owner.s"
.segment "TMNT_SAMUS_AUDIO_COLD"
.proc TnAudioUpdate
 lda #0
 sta TnAudioRequest
 lda XgAudioCharacter
 cmp #$fd
 beq Initialized
 lda #$fd
 sta XgAudioCharacter
 lda #0
 sta TnAudioSong
 sta TnAudioSilenced
 sta TnAudioPaused
 lda #2
 sta TnAudioRequest
Initialized:
 lda AreaMusicQueue
 ora EventMusicQueue
 and #Silence
 beq Area
 lda #1
 sta TnAudioSilenced
Area:
 lda AreaMusicQueue
 and #$7f
 beq Event
 ldx #0
FindArea:lsr
 bcs AreaFound
 inx
 bne FindArea
AreaFound:
 lda Areas,x
 sta TnAudioRequest
 lda #0
 sta TnAudioSilenced
Event:
 lda EventMusicQueue
 and #$7f
 beq Pause
 ldx #0
FindEvent:lsr
 bcs EventFound
 inx
 bne FindEvent
EventFound:
 lda Events,x
 sta TnAudioRequest
 lda #0
 sta TnAudioSilenced
Pause:
 lda GamePauseStatus
 and #1
 jne Mute
 lda TnAudioSilenced
 jne Mute
 lda TnAudioRequest
 beq Resume
 pha
 lda #0
 ldx #0
ResetState:
 sta TnAudioRam,x
 inx
 cpx #$d8
 bne ResetState
 .repeat 14,I
  sta z:TnAudioZp+I
 .endrepeat
 pla
 sta TnAudioRequest
 sta TnAudioSong
 inc XgAudioSong
 ldx #15
 lda #0
ResetImage:
 sta GuestNativeApu,x
 lda #1
 sta GuestNativeDirty,x
 lda #0
 dex
 bpl ResetImage
Resume:
 lda TnAudioPaused
 beq Borrow
 lda TnAudioDacHold
 sta $4011
 lda TnAudioEnableHeld
 jsr TnSourceSTA15
 lda #0
 sta TnAudioPaused
Borrow:
 lda TnAudioRequest
 beq Play
 jsr TnMusicInitCall
 jmp Restore
Play:jsr TnMusicPlayCall
Restore:
 jmp Queues
Mute:
 lda TnAudioPaused
 bne Muted
 lda GuestNativeEnable
 and #15
 sta TnAudioEnableHeld
 lda BassDmcActive
 eor #4
 bne Hold
 lda #0                        ; Pause cuts an active drum; next beat restarts.
 sta TnAudioDacHold
Hold:lda #1
 sta TnAudioPaused
Muted:
 lda #0
 jsr TnSourceSTA15
 sta $4011
Queues:
 lda #0
 sta AreaMusicQueue
 sta EventMusicQueue
 sta Square1SoundQueue
 sta Square2SoundQueue
 sta NoiseSoundQueue
 jmp TnAudioAdapterReturn
Areas:.byte 2,5,3,10,8,1,11
Events:.byte 15,13,12,12,13,12,6
.endproc
.export TnAudioUpdate
.popseg
