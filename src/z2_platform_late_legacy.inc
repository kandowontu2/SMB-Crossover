.proc Z2LateLegacyFirebarAdmission
  ; No matching ID can produce a firebar. Keep the existing live-owner checks.
  ldx #5
CheckFirebarID:
  lda Enemy_ID,x
  cmp #$1b
  bcc NextFirebarID
  cmp #$23
  bcc DrawFirebars
NextFirebarID:
  dex
  bpl CheckFirebarID
  stx FirebarSlot
  bmi FirebarsReady
DrawFirebars:
  farcall DrawWorldFirebars
FirebarsReady:
  rts
.endproc
