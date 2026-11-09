.setcpu "6502"

MainGate = $8356
FarCallCommon = $015a

.segment "END_MAIN"
  ; A=0 from PauseSkip. The caller returns straight from MainGate.
  jmp MainGate

.segment "MAIN_GATE"
  ; The fixed shim's original return immediately returned to its caller.
  ; FarCallCommon still pushes its own mapper and target return frames.
  jmp FarCallCommon
  nop
