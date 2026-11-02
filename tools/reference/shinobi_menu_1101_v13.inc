.export ShMenuResolve
.segment "SHINOBI_RESIDENT"
ShMenuResolve:
 jsr ShRetire
 ShRomFar ShPriorResolve,157
 php
 lda CrossoverMenuIndex
 cmp #10
 bne ShMenuDone
 lda FmAlts
 and #4
 beq ShMenuDone
 lda #36
 sta SelectedCharacter
ShMenuDone:
 plp
 lda SelectedCharacter
 rts
