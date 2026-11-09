.setcpu "6502"

SelectedCharacter = $6002
SavedA = $016a
TargetLo = $016c
TargetHi = $016d
FarCallCommon = $015a

.macro Tail bank, target
  lda #<target
  sta TargetLo
  lda #>target
  sta TargetHi
  lda #bank
  jmp FarCallCommon
.endmacro

.segment "MINI_TAIL"
.export MiniMovementTail
MiniMovementTail:
  ; Existing Mini row-zero veneer. It performs its ordinary readiness,
  ; live header and engine checks, and retains its native fallback.
  Tail $d4, $b420

.segment "CAMERA"
.export CameraMovementAdmission, CameraMovementEnd
CameraMovementAdmission:
  sta SavedA
  php
  lda SelectedCharacter
  cmp #14
  beq Chip
  cmp #19
  beq Scrooge
  cmp #41
  beq Mini
Legacy:
  plp
  Tail $dd, $a0b0
Scrooge:
  plp
  Tail $d7, $a352
Chip:
  plp
  Tail $d1, $a0b2
Mini:
  plp
  jmp MiniMovementTail
  .res $49 - (* - CameraMovementAdmission), $ea
CameraMovementEnd:
