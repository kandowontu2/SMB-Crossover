; Included in the banked guest-audio segment, MMC5 only. The original NES
; voices remain with the character driver. Shared world tones use $5000/$5004;
; brick shatter still borrows NES noise because MMC5 has no noise generator.
.proc GuestExpansionFlush
  lda GuestMixMask
  and #3
  sta $5015
  ; Preserve the descending image writes without indexed loop bookkeeping.
 .repeat 8, I
  lda GuestFxApu+7-I
  sta GuestExpansionApu+7-I
 .endrepeat
  lda GuestMixMask
  and #1
  beq Output

  ; MMC5 has no sweep registers. Keep a private pulse-1 timer and implement
  ; the NES divider/negate behavior in software, at two half clocks per NMI.
  ; The phase within the video frame is quantized to this 60 Hz update.
  lda GuestFxDirty+2
  beq :+
    lda GuestFxApu+2
    sta GuestSweepPeriod
  :
  lda GuestFxDirty+3
  beq :+
    lda GuestFxApu+3
    and #7
    sta GuestSweepPeriod+1
  :
  lda GuestFxDirty+1
  beq :+
    lda GuestFxApu+1
    sta GuestSweepControl
    lda #1
    sta GuestSweepReload
  :
  lda #2
  sta GuestSweepTicks
Clock:
  jsr GuestExpansionSweepClock
  dec GuestSweepTicks
  bne Clock
  lda GuestSweepPeriod
  sta GuestExpansionApu+2
  lda GuestFxApu+3
  and #$f8
  ora GuestSweepPeriod+1
  sta GuestExpansionApu+3
  jsr GuestExpansionSweepTarget
  bcs Output
  lda GuestExpansionApu
  and #$c0
  ora #$30                       ; MMC5 does not implement NES sweep muting.
  sta GuestExpansionApu
Output:
  ; Fixed register/channel offsets also make silent channels cheap. Keep the
  ; original ascending hardware writes and dirty/ownership retriggers.
 .repeat 8, I
 .scope
 .if I <> 1 && I <> 5             ; $5001/$5005 are unimplemented.
 .if ::ENABLE_MMC5_EXPANDED
 .if I = 0
  lda #1
  and GuestMixMask
  beq ::X5ExpansionOutputChannel2
 .elseif I = 4
::X5ExpansionOutputChannel2:
  lda #2
  and GuestMixMask
  beq ::X5ExpansionOutputDone
 .endif
  lda GuestExpansionApu+I
 .else
  lda #(1 << (I / 4))
  and GuestMixMask
  beq Next
  lda GuestExpansionApu+I
 .endif
  cmp GuestExpansionLast+I
  bne Write
  lda #(1 << (I / 4))
  and GuestMixChanged
  bne Write
  lda GuestFxDirty+I
  beq Next
Write:
  lda GuestExpansionApu+I
  sta $5000+I
  sta GuestExpansionLast+I
Next:
 .endif
 .endscope
 .endrepeat
 .if ::ENABLE_MMC5_EXPANDED
::X5ExpansionOutputDone:
 .endif
  ; Match the old exhausted loop's A/X/Y and all flags, including carry.
  ldx #8
  ldy #1
  cpx #8
  rts
  ; Unreachable capacity retains every following real function entry.
 .if ::ENABLE_MMC5_EXPANDED
  .res 371-(*-::GuestExpansionFlush),$ea
 .endif
.endproc

.proc GuestExpansionSweepClock
  jsr GuestExpansionSweepTarget
  bcc Divider
  lda GuestSweepDivider
  bne Divider
  lda GuestSweepControl
  bpl Divider                    ; Sweep disabled.
  and #7
  beq Divider                    ; Zero shift never updates the timer.
  lda GuestSweepDelta
  sta GuestSweepPeriod
  lda GuestSweepDelta+1
  sta GuestSweepPeriod+1
Divider:
  lda GuestSweepDivider
  beq Reload
  lda GuestSweepReload
  bne Reload
  dec GuestSweepDivider
  rts
Reload:
  lda GuestSweepControl
  lsr
  lsr
  lsr
  lsr
  and #7
  sta GuestSweepDivider
  lda #0
  sta GuestSweepReload
  rts
.endproc

; Carry set if the native sweep gate would allow output; Delta is the target.
.proc GuestExpansionSweepTarget
  lda GuestSweepPeriod
  sta GuestSweepDelta
  lda GuestSweepPeriod+1
  sta GuestSweepDelta+1
  bne ShiftCount
  lda GuestSweepPeriod
  cmp #8
  bcc Muted
ShiftCount:
  lda GuestSweepControl
  and #7
  tay
  beq Direction
Shift:
  lsr GuestSweepDelta+1
  ror GuestSweepDelta
  dey
  bne Shift
Direction:
  lda GuestSweepControl
  and #8
  bne Negate
  clc
  lda GuestSweepPeriod
  adc GuestSweepDelta
  sta GuestSweepDelta
  lda GuestSweepPeriod+1
  adc GuestSweepDelta+1
  sta GuestSweepDelta+1
  jmp Range
Negate:
  clc                            ; Pulse 1 uses one's complement: minus 1.
  lda GuestSweepPeriod
  sbc GuestSweepDelta
  sta GuestSweepDelta
  lda GuestSweepPeriod+1
  sbc GuestSweepDelta+1
  sta GuestSweepDelta+1
Range:
  lda GuestSweepDelta+1
  cmp #8
  bcs Muted
  sec
  rts
Muted:
  clc
  rts
.endproc
