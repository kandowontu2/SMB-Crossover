; Same publication as SpecialPublishChr, for its two bank-local draw callers.
; The mapper trampoline normally reloads the returned A, replacing N/Z from
; CMP/INC. ORA #0 retains that public flag result without a mapper round trip.
.macro GuestPublishChrLocal
 .local Changed, Done
  lda SsChrActive
  cmp SsLastChrActive
  bne Changed
  lda SsChrPhysical
  cmp SsLastChrPhysical
  beq Done
Changed:
  lda SsChrActive
  sta SsLastChrActive
  lda SsChrPhysical
  sta SsLastChrPhysical
  inc ReloadCHRBank
Done:
  ora #0
.endmacro
