; Foreground InitScreen hook. Preserve same-life state on warm scene changes;
; retire Shinobi headers before any foreign scene chain can reuse its RAM.
.export ShScene
.segment "SHINOBI_RESIDENT"
ShScene:
 php
 pha
 txa
 pha
 lda SelectedCharacter
 cmp #36
 beq ShSceneOwn
 pla
 tax
 pla
 plp
 jsr ShRetire
 ShRomFar ShPriorScene,149
 rts
ShSceneOwn:
 jsr ShLoad
 bcc ShSceneDone
 jsr ShChr
 ldx CurrentBankC
 lda #2
 sta CurrentBankC
 sta $5116
 lda $c800
 stx CurrentBankC
 stx $5116
 cmp #$a7
 beq ShSceneDone
 ; The source constructor is service15, under the normal authenticated
 ; farcall dispatcher. It independently enforces the forced-blank boundary.
 ShRomFar ShConstructVeneer,193
ShSceneDone:
 pla
 tax
 pla
 plp
 rts
ShConstructVeneer=ShServiceVeneers+45
