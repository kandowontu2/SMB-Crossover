; Interim current native-piece envelope, not Flash bitmap/phase equivalence.
; A-only leaf: no RAM/scratch/X/Y writes. C1 rejects definite disjointness.
.pushseg
.segment "SOPHIA_BODY_COLD"
EasyLinkFirebarStart:
.proc EasyLinkFirebarDisjoint
  lda CrossoverBehaviorVersion
  jne Native
  lda OperMode
  cmp #1
  jne Native
  lda GameEngineSubroutine
  cmp #8
  jne Native
  lda Player_State
  jne Native
  lda RgBillBurst
  cmp #2
  jcc Native
  cmp #5
  jcs Native
  lda RgAttack
  ora RgCrouch
  ora CrouchingFlag
  ora GuestHurtTicks
  ora GuestLegacyHurt
  ora GuestPowerupActive
  ora MmUnderwater
  ora SwimmingFlag
  ora MmYFraction
  ora MmYFraction+1
  jne Native
  lda AreaType
  jeq Native
  lda Player_Y_HighPos
  cmp #1
  jne Native
  lda Player_Y_Position
  cmp #208
  jcs Native
  clc
  adc #17
  cmp BoundingBox_UL_Corner+1
  jne Native
  cmp LinkLastBoxes+1
  jne Native
  clc
  adc #15
  cmp BoundingBox_UL_Corner+3
  jne Native
  cmp LinkLastBoxes+3
  jne Native
  ; Conservative whole8x16 container incl hardware Y+1 and spare pixel:
  ; source/native current-piece envelope [R7-3,R7+13]. No pixel widening.
  lda R7
  cmp #3
  bcc Native
  cmp #243
  bcs Native
  clc
  adc #13
  cmp BoundingBox_UL_Corner+1
  bcc Disjoint
  lda R7
  sec
  sbc #3
  cmp BoundingBox_UL_Corner+3
  bcc Native
  beq Native
Disjoint:
  sec
  rts
Native:
  clc
  rts
.endproc
EasyLinkFirebarEnd:
.popseg
