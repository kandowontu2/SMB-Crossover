; Source Coin is Pickup, never a Ground. Keep native coin attributes intact.
; Tail entry from RyuWallMap after TAY; A/Y both contain the cell ID.
; No allocation, new stack frame, or native/Sophia collision changes.
.pushseg
.segment "SPECIAL_ROSTER"
.proc RyuWallMapAttribute
  cpy #$c2
  beq Empty
  cpy #$c3
  beq Empty
  lda MTileAttribute,y
  jmp RyuWallMapAttributeContinue
Empty:
  clc
  rts
.endproc
.assert *-RyuWallMapAttribute = 16, error, "Ryu coin-only wall filter must stay16bytes"
.popseg
