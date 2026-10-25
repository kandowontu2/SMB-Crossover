; Source NSF effects overlay only the voices they use. The native music image
; is restored before its next update, preventing effects from feeding the song.
.include "audio/remaining-source-sfx.inc"
.pushseg
.segment "SRAM"
AvAudioChar: .res 1
AvAudioId: .res 1
AvAudioRequest: .res 1
AvAudioMask: .res 1
AvAudioOldMask: .res 1
AvAudioPtr: .res 2
AvAudioMusic: .res 16
AvAudioSfx: .res 16
.segment "REMAINING_AUDIO"
.proc RemainingAudioSupported
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  bcc No
  cmp #CHARACTER_SIMON+1
  bcc Yes
  cmp #CHARACTER_RYU
  beq Yes
  cmp #CHARACTER_SOPHIA
  beq Yes
No:
  clc
  rts
Yes:
  sec
  rts
.endproc
.proc RemainingAudioBegin

.if ::MAPPER_MMC5 .and ::ENABLE_MMC5_EXPANDED
  ; Audio also advances on lag NMIs. Re-establish only the HUD background
  ; font after the previous scanline IRQ selected the level font. Sprite
  ; CHR and its pending publication remain paired with the committed OAM.
  lda DisableScreenFlag
  bne HudFontDone
  lda InvHudActive
  beq HudFontDone
  lda X5HudChrUpper
  and #3
  sta $5130
  lda InvHudPhysical
  sta $5128
  ; MMC5 captures upper CHR bits when each bank register is written. The
  ; later world-font IRQ expects the ordinary zero upper latch.
  lda #0
  sta $5130
HudFontDone:
.endif
  jsr RemainingAudioSupported
  bcs Check
  lda #0
  sta AvAudioChar
  sta AvAudioId
  sta AvAudioMask
  sta AvAudioOldMask
  sta AvAudioRequest
  rts
Check:
  cmp AvAudioChar
  beq Restore
  sta AvAudioChar
  lda #0
  sta AvAudioId
  sta AvAudioMask
  sta AvAudioOldMask
  sta AvAudioRequest
Restore:
  ; Typed projectile audio replaces the generic attack cue in the common mixer.
  lda AvAudioRequest
  beq :+
    lda Square1SoundQueue
    and #$ff-Sfx_Fireball
    sta Square1SoundQueue
  :
  lda AvAudioOldMask
  beq Done
  ldx #15
Loop:
  lda AvAudioMusic,x
  sta GuestNativeApu,x
  dex
  bpl Loop
Done:
  rts
.endproc
.proc RemainingAudioTick
  jsr RemainingAudioSupported
  jcc Done
  lda GamePauseStatus
  and #1
  jne Done
  lda OperMode
  jeq Done
  lda AvAudioId
  ora AvAudioRequest
  ora AvAudioOldMask
  jeq Done
  lda R0
  pha
  lda R1
  pha
  ldx #15
Save:
  lda GuestNativeApu,x
  sta AvAudioMusic,x
  dex
  bpl Save
  lda AvAudioRequest
  beq Decode
  cmp #AV_SFX_LINKTAKEDAMAGE
  beq Dmc
  cmp #AV_SFX_SIMONTAKEDAMAGE
  beq Dmc
  sta AvAudioId
  tax
  dex
  lda SophiaAvSfxLo,x
  sta AvAudioPtr
  lda SophiaAvSfxHi,x
  sta AvAudioPtr+1
  lda SophiaAvSfxMasks,x
  sta AvAudioMask
  lda #0
  sta AvAudioRequest
  beq Decode
Dmc:
  jsr RemainingDmcStart
  lda #0
  sta AvAudioRequest
  sta AvAudioId
  sta AvAudioMask
  beq Mix
Decode:
  lda AvAudioId
  jeq Mix
  lda AvAudioPtr
  sta R0
  lda AvAudioPtr+1
  sta R1
Read:
  jsr Byte
  cmp #254
  beq FrameDone
  cmp #255
  beq End
  tax
  jsr Byte
  sta AvAudioSfx,x
  jmp Read
End:
  lda #0
  sta AvAudioId
  sta AvAudioMask
FrameDone:
  lda R0
  sta AvAudioPtr
  lda R1
  sta AvAudioPtr+1
Mix:
  ldx #15
Register:
  txa
  lsr
  lsr
  tay
  lda Bits,y
  and AvAudioMask
  beq Released
  lda AvAudioSfx,x
  sta GuestNativeApu,x
  jmp Dirty
Released:
  lda Bits,y
  and AvAudioOldMask
  beq Next
Dirty:
  lda #1
  sta GuestNativeDirty,x
Next:
  dex
  bpl Register
  lda AvAudioMask
  sta AvAudioOldMask
  ora GuestNativeEnable
  jsr GuestNativeStatusSTA
::RemainingAudioFrameReady:
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
Bits: .byte 1,2,4,8
.endproc

; Pure source DMC injury cues coexist with all four music voices. The shared
; status writer polls real hardware completion before preserving enablebit4,
; preventing an ended sample from restarting on a later music status write.
.proc RemainingDmcStart
  sec
  sbc #AV_SFX_LINKTAKEDAMAGE
  tax
  lda GuestCombinedEnable
  and #15
  sta $4015
.if ::ENABLE_MMC5_EXPANDED
  jsr Cv3DmcInjuryRate
  .res 2,$ea                   ; old five-byte rate/store span
.else
  lda #15                       ; Exact NTSC source rate, no IRQ or loop.
  sta $4010
.endif
  lda #0
  sta $4011
  lda Addresses,x
  sta $4012
  lda Lengths,x
  sta $4013
  lda #2                        ; Shared DMC owner, retained by nonBass begin.
  sta BassDmcActive
  lda GuestCombinedEnable
  ora #$10
  sta GuestCombinedEnable
  sta $4015
::RemainingDmcStarted:
  rts
Addresses:
  .byte (AvDmcLinkTakeDamage-$c000)/64,(AvDmcSimonTakeDamage-$c000)/64
Lengths:
  .byte (AvDmcLinkTakeDamageEnd-AvDmcLinkTakeDamage-1)/16,(AvDmcSimonTakeDamageEnd-AvDmcSimonTakeDamage-1)/16
.endproc
.popseg
