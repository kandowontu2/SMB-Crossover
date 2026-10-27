.pushseg
.segment "KIRBY_CORE"
.proc KbLegacyExpandedCollisionAdder
  ldy #6
  cmp #CHARACTER_SCROOGE
  beq Scrooge
  cmp #CHARACTER_LUIGI
  jeq Luigi
  cmp #CHARACTER_PIT
  beq Medium
  cmp #CHARACTER_BASS
  jeq BassTerrainAdder
  cmp #CHARACTER_SOPHIA
  beq Medium
  lda GuestHurtTicks
  beq Crouch
  iny
  sec
  rts
Medium:
  ldy #3
Crouch:
  lda RgCrouch
  beq Yes
Short:
  ldy #8
Yes:
  sec
  rts
Luigi:
  clc
  rts
Scrooge:
  ldy #10
  sec
  rts
  .res 57-(*-::KbLegacyExpandedCollisionAdder),$ea
  .assert *-KbLegacyExpandedCollisionAdder=57,error,"Original adder span"
.endproc
.proc KbLegacyExpandedCollisionBox
  cmp #CHARACTER_SCROOGE
  beq Scrooge
  cmp #CHARACTER_LUIGI
  beq Done
  ldy #15
  cmp #CHARACTER_PIT
  beq Medium
  cmp #CHARACTER_BASS
  jeq BassTerrainBox
  cmp #CHARACTER_SOPHIA
  beq Medium
  lda GuestHurtTicks
  beq Crouch
  iny
  rts
Medium:
  ldy #12
Crouch:
  lda RgCrouch
  beq Done
Short:
  ldy #17
Done:
  rts
Scrooge:
  ldy #19
  lda RgCrouch
  beq Done
  iny
  rts
  .res 55-(*-::KbLegacyExpandedCollisionBox),$ea
  .assert *-KbLegacyExpandedCollisionBox=55,error,"Original box span"
.endproc
.proc KbAdderDispatch
 cmp #CHARACTER_KIRBY
 beq Kirby
 jmp KbLegacyExpandedCollisionAdder
Kirby:
 ldy #9
 lda RgCrouch
 beq :+
 ldy #8
 :sec
 rts
.endproc
.proc KbBoxDispatch
 cmp #CHARACTER_KIRBY
 beq Kirby
 jmp KbLegacyExpandedCollisionBox
Kirby:
 ldy #18
 lda RgCrouch
 beq :+
 ldy #17
 :rts
.endproc
.popseg
