; MegaManBase effects over Bass's MM10 playlist, from 2.02's source NSFs.
.pushseg
.segment "SRAM"
BassAudioInit: .res 1
BassAudioRequest: .res 1
BassAudioPreviousMask: .res 1
BassAudioMask: .res 1
BassAudioLastGround: .res 1
BassAudioLastDeath: .res 1
BassAudioSavedApu:
BassSourceId: .res 1
BassSourcePtr: .res 2
BassSourcePriority: .res 1
BassSourceKill: .res 1
BassDmcActive: .res 1
.res 10
BassAudioSavedDirty: .res 16
BassAudioSfxApu: .res 16
.segment "GUEST_AUDIO"
.proc BassAudioBegin
  lda SelectedCharacter
  cmp #CHARACTER_BASS
  beq Bass
  lda #0
  sta BassAudioInit
  sta BassAudioPreviousMask
  sta BassAudioLastDeath
  sta BassAudioLastGround
  sta BassSourceId
  lda BassDmcActive
  cmp #2
  bcs OtherDmc
  lda #0
  sta BassDmcActive
OtherDmc:
  rts
Bass:
  lda #$ff
  sta BassAudioRequest
  lda BassAudioPreviousMask
  beq Requests
  ; The music decoder emits only changed registers. Restore the complete
  ; held music image before decoding, rather than leaving yesterday's SFX.
  ldx #15
RestoreMusic:
  lda XgMusicApu,x
  sta GuestNativeApu,x
  dex
  bpl RestoreMusic
Requests:
  lda GuestWorldQueues
  and #Sfx_Fireball
  beq :+
    lda #21
    sta BassAudioRequest
  :
  lda SsAudioRequest
  beq :+
    sec
    sbc #1
    sta BassAudioRequest
    lda #0
    sta SsAudioRequest
  :
  lda GuestWorldQueues
  and #Sfx_EnemySmack
  beq :+
    lda #24
    sta BassAudioRequest
  :
  lda GuestWorldQueues
  and #Sfx_PipeDown_Injury
  beq :+
    lda #22
    sta BassAudioRequest
  :
  lda GuestWorldQueues+1
  and #Sfx_ExtraLife|Sfx_PowerUpGrab
  beq :+
    lda #20
    sta BassAudioRequest
  :
  lda Player_State
  beq Ground
  lda #0
  sta BassAudioLastGround
  beq Death
Ground:
  lda BassAudioLastGround
  bne Death
  lda #1
  sta BassAudioLastGround
  lda GameEngineSubroutine
  cmp #8
  bne Death
  lda BassAudioRequest
  cmp #$ff
  bne Death
  lda #19
  sta BassAudioRequest
Death:
  lda MmDeathFlag
  cmp BassAudioLastDeath
  beq Filter
  sta BassAudioLastDeath
  cmp #0
  beq Filter
  lda #1
  sta BassSourceKill
  lda #23
  sta BassAudioRequest
Filter:
  lda GuestWorldQueues
  and #$ff-(Sfx_Fireball|Sfx_EnemySmack|Sfx_PipeDown_Injury|Sfx_BigJump|Sfx_SmallJump)
  sta GuestWorldQueues
  lda GuestWorldQueues+1
  and #$ff-(Sfx_ExtraLife|Sfx_PowerUpGrab)
  sta GuestWorldQueues+1
  rts
.endproc
.segment "XG_BASS_GFX"
.proc BassNativeAudioTick
  lda CurrentBank
  pha
  BankPRGA #.bank(BassSfxLand)
  jsr BassSourceAudioTick
  pla
  BankPRGA a
  rts
.endproc
.popseg
.include "bass_source_sfx.s"
