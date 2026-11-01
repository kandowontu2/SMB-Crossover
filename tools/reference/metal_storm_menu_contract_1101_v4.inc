; Cold ROM fragments only. Never put these consumers behind an unauthenticated
; A3 opcode. The component's8000 arena is a CPU test location, NOT a ROM lease.
.import CrossoverMenuIndex,FmAlts,SelectedCharacter
.export MsMenuResolveLeaf,MsMenuStartFlagsLeaf
.proc MsMenuResolveLeaf
 php
 lda CrossoverMenuIndex
 cmp #11
 bne Done
 lda FmAlts
 and #2
 beq Done
 lda #35
 sta SelectedCharacter
Done:
 plp
 lda SelectedCharacter
 rts
.endproc

; Call AFTER authentic FmStartRetireFlags. Retain only this owner's alt bit;
; raw11 Sophia must retain all its existing start/portrait/vehicle behavior.
.proc MsMenuStartFlagsLeaf
 php
 pha
 lda SelectedCharacter
 cmp #35
 bne :+
 lda FmAlts
 ora #2
 sta FmAlts
:pla
 plp
 rts
.endproc
