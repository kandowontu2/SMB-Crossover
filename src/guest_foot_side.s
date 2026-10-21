; Private unchanged deep-foot branch closure, moved from resident FIXED.
.pushseg
.segment "ROSTER"
.proc RosterGuestFootContactSide
  ; Native SMB uses the last movement direction for a deep foot contact.
  ; A guest can stop with just one foot inside a ledge; that stale direction
  ; would clamp to the far edge and repeat across every tile in the ledge.
  lda SelectedCharacter
  beq Native
  cmp #CHARACTER_LUIGI
  beq Native
  lda R1                         ; Left foot metatile, retained by FootCheck.
  beq Right
  lda R0                         ; Right foot metatile.
  beq Left
  ; A recorded corner may already have both feet in the same tile. Recover
  ; locally toward the adjacent edge instead of carrying a stale direction
  ; through every tile. A partial contact above chooses its actual foot.
  lda Player_X_Position
  and #8
  bne Right
Left:
  lda #2
  bne Store
Native:
  lda Player_MovingDir
  bne Store
Right:
  lda #1
  bne Store
Store:
  sta R0
  rts
.endproc
.popseg
