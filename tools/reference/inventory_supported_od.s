  ; These six profiles own their own items and never use the legacy2.02
  ; inventory. Match the old dispatch chain's A=ID, X=ID, C=0 exactly.
  ; Mac15 retains his supported-item path. All other IDs use the old entry.
  php
  pha
  phx
  ldx SelectedCharacter
  cpx #13
  bcc LegacySupported
  cpx #15
  beq LegacySupported
  cpx #20
  bcs LegacySupported
  ; CPX20 left C clear. None of the checks/pops changes V/D/I, so discard
  ; saved P rather than restoring its old carry. TXA supplies final N/Z.
  pla
  pla
  pla
  txa
  rts
LegacySupported:
  plx
  pla
  plp
  farcall RlSupportedDispatch,jmp
