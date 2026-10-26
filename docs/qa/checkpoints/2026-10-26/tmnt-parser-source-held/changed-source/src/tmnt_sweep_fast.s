; New private C87 run alias. A29 remains mapped for literal fallback
; clock/target calls. Only owner0/4 is admitted; TMNT samples reside in E.
.pushseg
.segment "TN_SWEEP_C87"
.proc TnExpansionFlushFast
 lda GuestMixMask
 and #3
 sta $5015
.repeat 8,I
.if 7-I<>2 && 7-I<>3
 ; Both source-clock routes later overwrite2/3 before any output/reader.
 lda GuestFxApu+7-I
 sta GuestExpansionApu+7-I
.endif
.endrepeat
 ; Gate already proves pulse1. Dirty images, nonzero divider
 ; or reload, and values outside18..2047 retain literal source halfclocks.
 lda GuestSweepControl
 cmp #$99
 jne Original
 lda GuestFxDirty+1
 ora GuestFxDirty+2
 ora GuestFxDirty+3
 jne Original
 lda GuestSweepDivider
 ora GuestSweepReload
 bne Original
 lda GuestSweepPeriod+1
 cmp #8
 bcs Original
 cmp #0
 bne Wide
 lda GuestSweepPeriod
 cmp #18
 bcc Original
 ; CMP18 already proves carry1. Last SBC cannot overflow for P>=18.
 sbc #1
 lsr
 sta GuestSweepPeriod
 sta GuestExpansionApu+2
 sec
 sbc #1
 lsr
 sta GuestSweepDelta
 lda #0
 ; PeriodHi was proved zero and is not modified on this small route.
 sta GuestSweepDelta+1
 sta GuestSweepTicks
 lda GuestFxApu+3
 and #$f8
 sta GuestExpansionApu+3
 jmp Output
Wide:
 ; CMP0 already proves carry1 for every nonzero high byte.
 lda GuestSweepPeriod
 sbc #1
 sta GuestSweepPeriod
 lda GuestSweepPeriod+1
 sbc #0
 lsr
 sta GuestSweepPeriod+1
 ror GuestSweepPeriod
 sec
 lda GuestSweepPeriod
 sbc #1
 sta GuestSweepDelta
 lda GuestSweepPeriod+1
 sbc #0
 lsr
 sta GuestSweepDelta+1
 ror GuestSweepDelta
 lda #0
 sta GuestSweepTicks
 lda GuestSweepPeriod
 sta GuestExpansionApu+2
 lda GuestFxApu+3
 and #$f8
 ora GuestSweepPeriod+1
 sta GuestExpansionApu+3
 jmp Output
Original:
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
.repeat 2,C
.scope
 lda #(1<<C)
 and GuestMixMask
 beq NextChannel
.repeat 4,R
.scope
 I=C*4+R
.if R<>1
 lda GuestExpansionApu+I
 cmp GuestExpansionLast+I
 bne Write
 lda #(1<<C)
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
NextChannel:
.endscope
.endrepeat
 ldx #8
 tay
 ; Private caller consumes only X8/Y=finalA/V/D/I. Its REAL CPX8 owns
 ; every final C/N/Z result after restoring the original C-window bank.
 rts
.endproc
.popseg
