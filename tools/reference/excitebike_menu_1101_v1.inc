; Retain the real Sh/native resolver and its output ABI. Only slot29 with
; FmAlts bit16 clear becomes raw37. The existing pending portrait/name remains24.
.export ExMenuResolve,ExMenuDone,ExReset
.segment "EX_MENU_GATE"
ExMenuResolve:
 jsr ExPriorMenuResolve
 jmp ExMenuBody
.segment "EX_MENU_BODY"
ExMenuBody:
 php
 lda FmAlts
 and #16
 asl                       ; bit32 lies outside every native slot0..31.
 ora CrossoverMenuIndex
 cmp #29
ExMenuBranch:
 ; ca65 requires the relative operand in this segment; ld65 checks the
 ; exact cross-fragment destination instead of widening the two-byte branch.
 bne *+120
 .assert ExMenuDone=ExMenuBranch+120,lderror,"Ex menu branch destination"
 lda #37
 sta SelectedCharacter
ExMenuTail:
 bne *+113                  ; LDA#37 remains nonzero through its STA.
 .assert ExMenuDone=ExMenuTail+113,lderror,"Ex menu tail destination"
.segment "EX_MENU_DONE"
ExMenuDone:
 plp
 lda SelectedCharacter
 rts
ExReset:
 jsr ExRetire              ; ROM-only: no opcode follows revoked RAM headers.
 sec
 rts
