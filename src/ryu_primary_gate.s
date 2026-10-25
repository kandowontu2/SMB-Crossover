; Source2.02 Ryu.pressAtkBtn rejects primary while Jump Slash remains live.
.pushseg
.segment "EXPANDED_EX"
.proc RyuPrimaryBlocked
  lda XgWall
  ora AvSlash
  rts
.endproc
.popseg
