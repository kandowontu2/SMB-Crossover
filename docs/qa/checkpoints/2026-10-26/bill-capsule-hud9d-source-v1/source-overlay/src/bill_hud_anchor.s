; Bill and Lance share character3. Their24px capsule belongs in the
; free name-row gap; all other characters retain their original anchor.
; Genuine private ABI: returns A=x,Y=y; preserves X and all input P.
; Actual HUD caller's Y is dead before RemainingDraw::ArtPointer TAY.
.pushseg
.segment "SPECIAL_ROSTER"
.proc BillHudAnchor
  php
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  beq Bill
  lda #192
  ldy #24
  plp
  rts
Bill:
  lda #112
  ldy #16
  plp
  rts
.endproc
.assert BillHudAnchor = $bfae, error, "Bill HUD append moved"
.assert *-BillHudAnchor = 20, error, "Bill HUD helper size changed"
.popseg
