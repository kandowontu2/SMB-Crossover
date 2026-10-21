; Frame-quantized register writes from the exact NSF tracks in 2.02 MusicInfo.
; Source effects own their actual voices; the MM10 music decoder keeps running.
.include "audio/bass-source-sfx.inc"
.pushseg
.segment "BASS_DPCM"
BassWaterDpcm:
  .incbin "audio/bass/water-shield.dmc"
BassWaterDpcmEnd:
.segment "XG_BASS_GFX"
.proc BassSourceAudioTick
  lda GamePauseStatus
  and #1
  jne Done
  lda OperMode
  jeq Done
  lda R0
  pha
  lda R1
  pha
  lda BassDmcActive
  beq CheckKill
  lda $4015
  and #$10
  bne CheckKill
  jsr StopDmc
CheckKill:
  lda BassSourceKill
  beq Request
  jsr StopDmc
  lda #0
  sta BassSourceKill
  sta BassSourceId
Request:
  lda BassAudioRequest
  cmp #$ff
  beq Decode
  cmp #$f1
  jeq Stop
  cmp #66
  bne :+
    jsr StartDmc
    jmp Decode
  :
  ldx #BASS_SFX_COUNT-1
Find:
  cmp BassSfxRequests,x
  beq Found
  dex
  bpl Find
  jmp Decode
Found:
  lda BassSourceId
  beq Start
  lda BassSfxPriorities,x
  cmp BassSourcePriority
  bcc Decode
Start:
  txa
  clc
  adc #1
  sta BassSourceId
  lda BassSfxPriorities,x
  sta BassSourcePriority
  lda BassSfxLo,x
  sta BassSourcePtr
  lda BassSfxHi,x
  sta BassSourcePtr+1
Decode:
  lda #0
.if ::MAPPER_MMC5
ClearDirty:
  ; Preserve the descending writes and final X/N/Z of the original loop.
  .repeat 16,I
    sta BassAudioSavedDirty+15-I
  .endrepeat
  ldx #$ff
.else
  ldx #15
ClearDirty:
  sta BassAudioSavedDirty,x
  dex
  bpl ClearDirty
.endif
  lda BassSourceId
  beq Stop
  tax
  dex
  lda BassSfxMasks,x
  sta BassAudioMask
  lda BassSourcePtr
  sta R0
  lda BassSourcePtr+1
  sta R1
Read:
  jsr Byte
  cmp #254
  beq FrameDone
  cmp #255
  beq Stop
  cmp #252
  beq Loop
  tax
  jsr Byte
  sta BassAudioSfxApu,x
  lda #1
  sta BassAudioSavedDirty,x
  bne Read
Loop:
  jsr Byte
  pha
  jsr Byte
  sta R1
  pla
  sta R0
  jmp Read
FrameDone:
  lda R0
  sta BassSourcePtr
  lda R1
  sta BassSourcePtr+1
  jmp Mix
Stop:
  lda #0
  sta BassSourceId
  sta BassAudioMask
Mix:
::BassSourceFrameReady:
  lda BassAudioMask
  ora BassAudioPreviousMask
  beq MixStatus                 ; Pure music already owns the complete image.
  ldx #15
Register:
  txa
  lsr
  lsr
  tay
  lda Bits,y
  and BassAudioMask
  beq Music
  lda BassAudioSfxApu,x
  sta GuestNativeApu,x
  lda BassAudioSavedDirty,x
  sta GuestNativeDirty,x
  lda Bits,y
  and BassAudioPreviousMask
  bne Next
  lda #1
  sta GuestNativeDirty,x
  bne Next
Music:
  lda Bits,y
  and BassAudioPreviousMask
  beq Next
  lda #1                       ; Reload a released voice's length counter.
  sta GuestNativeDirty,x
Next:
  dex
  bpl Register
MixStatus:
  ldx #$ff                      ; Same final register state as the mixing loop.
  lda BassAudioMask
  sta BassAudioPreviousMask
  ora XgAudioStatus
  jsr GuestNativeStatusSTA
::BassSourceMixFinish:
  pla
  sta R1
  pla
  sta R0
Done:
  rts
Byte:
  ldy #0
  lda (R0),y
  inc R0
  bne :+
    inc R1
  :
  rts
StartDmc:
  lda GuestCombinedEnable
  and #15
  sta $4015
  lda #14                       ; No DMC IRQ, no looping.
  sta $4010
  lda #64
  sta $4011
  lda #((BassWaterDpcm-$c000)/64)
  sta $4012
  lda #((BassWaterDpcmEnd-BassWaterDpcm-1)/16)
  sta $4013
  lda #1
  sta BassDmcActive
  lda GuestCombinedEnable
  ora #$10
  sta GuestCombinedEnable
  sta $4015
  rts
StopDmc:
  lda #0
  sta BassDmcActive
  sta $4011
  lda GuestCombinedEnable
  and #15
  sta GuestCombinedEnable
  sta $4015
  rts
Bits: .byte 1,2,4,8
.endproc
.popseg
