.setcpu "6502"

SelectedCharacter = $6002
TimerControl = $074a
SavedA = $016a
TargetLo = $016c
TargetHi = $016d
FarCallCommon = $015a
LargePlatformCollision = $b453

.segment "POLICY"
.export PlatformCollisionPolicy
PlatformCollisionPolicy:
  lda SelectedCharacter
  cmp #11                       ; Original Link/Ryu owners remain below 11.
  lda TimerControl              ; Keep C and return the actual timer decision.
  rts
  .res 11 - (* - PlatformCollisionPolicy), $ea

.segment "DISPATCH"
.export NativePlatformCollisionDispatch
NativePlatformCollisionDispatch:
  sta SavedA
  php
  jsr PlatformCollisionPolicy
  bcc Full
  bne Full                     ; With motion suppressed, retain the old packet.
  plp
  jmp LargePlatformCollision
Full:
  plp
  lda #$5c
  jsr BodyCallback
  jsr LargePlatformCollision
  sta SavedA
  lda #$83
BodyCallback:
  sta TargetLo
  lda #$bf
  sta TargetHi
  lda #$ba
  ; The sole caller kills A/P before their next use. Actual far transport
  ; still preserves the body service's X/Y and exact SMC return packet.
  jmp FarCallCommon
  .res 44 - (* - NativePlatformCollisionDispatch), $ea
