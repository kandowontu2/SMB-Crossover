; The two intermediate clocks only consume Delta when the timer is eligible
; for an update. GuestExpansionFlush recomputes Delta after both clocks.
SweepClock:
  lda GuestSweepDivider
  bne Divider
  lda GuestSweepControl
  bpl ReloadControl
  and #7
  beq Reload
  jsr GuestExpansionSweepTarget
  bcc Reload
  lda GuestSweepDelta
  sta GuestSweepPeriod
  lda GuestSweepDelta+1
  sta GuestSweepPeriod+1
Reload:
  lda GuestSweepControl
ReloadControl:
  lsr
  lsr
  lsr
  lsr
  and #7
  sta GuestSweepDivider
  lda #0
  sta GuestSweepReload
  rts
Divider:
  lda GuestSweepReload
  bne Reload
  dec GuestSweepDivider
  rts
