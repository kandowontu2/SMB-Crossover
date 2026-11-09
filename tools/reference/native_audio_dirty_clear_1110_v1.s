; MMC5 native-only APU mix, in the original $A92D..$AAB5 extent.
; An unwritten register has an equal image and a zero dirty byte already.
; Consume a dirty byte after the corresponding hardware/shadow write.
.export NativeFlush, NativeFlushEnd
.segment "CODE"
NativeFlush:
 ldy #0
 .repeat 16, I
  .scope
   .if I <> 9 && I <> 13
    lda GuestNativeApu+I
    cmp GuestApuLast+I
    bne WriteNative
    ldx GuestNativeDirty+I
    beq NativeDone
WriteNative:
    sta $4000+I
    sta GuestApuLast+I
    ; Keeping the triangle linear counter in the trailing clear avoids
    ; adding a branch-page penalty to a full native image refresh.
    .if I <> 8
    sty GuestNativeDirty+I
    .endif
NativeDone:
   .endif
  .endscope
 .endrepeat
 lda #0
 .repeat 16, I
  .if I = 8 || I = 9 || I = 13
   sta GuestNativeDirty+I
  .endif
  sta GuestFxDirty+I
 .endrepeat
 sta GuestMixOwner
 lda GuestNativeApu+15
 sta GuestMixValue
 lda #16
 sta GuestMixRegister
 lda #4
 sta GuestMixChannel
 ldx #15
 ldy #3
 cmp #4
 rts
NativeFlushEnd:
