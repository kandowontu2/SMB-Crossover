; Append after all old bank7 contributors; old24 streams/tables stay literal.
.include "audio/sophia-land-sfx.inc"

; RemainingAudioTick deliberately keeps its original24 effects unchanged.
; Landing25 alone must not reload sweep/length/phase on silent source updates.
; The genuine21-byte stream is active only at pointer offsets9..20; writes
; occur at offsets9/update1 and19/update7. Full source progression is guarded
; independently. A paused held pointer must not produce another retrigger.
.pushseg
.segment "SOPHIA_LAND_AUDIO"
.assert >(AvSfxSophiaLand+20) = >AvSfxSophiaLand, lderror, "Landing stream low-byte phase guard must stay in one page"
.proc SophiaLandAudioTick
  jsr RemainingAudioTick
  php
  pha
  lda AvAudioId
  cmp #AV_SFX_SOPHIALAND
  bne Done
  lda GamePauseStatus
  and #1
  bne Quiet
  lda AvAudioPtr
  cmp #<(AvSfxSophiaLand+9)
  beq Done
  cmp #<(AvSfxSophiaLand+19)
  beq Done
Quiet:
  lda #0
  sta GuestNativeDirty+4
  sta GuestNativeDirty+5
  sta GuestNativeDirty+6
  sta GuestNativeDirty+7
Done:
  pla
  plp
  rts
.endproc
.popseg
