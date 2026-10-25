; Preserve the surrounding bounce lifecycle and pre-step camera sample.
; Avoid only the redundant trip through the Little Mac exact-ID gate.
.pushseg
.segment "X5_BOUNCE"
.proc X5OwnMovement
 php
 pha
 lda SelectedCharacter
 cmp #19
 bne Legacy
 pla
 plp
 farcall TnMovement,jmp
Legacy:
 pla
 plp
 farcall LmMovementGate,jmp
.endproc
.export X5OwnMovement
.popseg
