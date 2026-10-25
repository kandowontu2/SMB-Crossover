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
  beq Medium
  cmp #CHARACTER_SOPHIA
  beq Medium
  lda GuestHurtTicks
  beq Crouch
  iny                          ; Ryu's25NESpx recoil head/feet profile.
  sec
  rts
Crouch:
  lda RgCrouch
  beq Yes
Short:
  ldy #8
  bne Yes
Medium:
  ldy #3
  lda RgCrouch
  bne Short
Yes:
  sec
  rts
Luigi:
  clc                          ; Use native PlayerSize/CrouchingFlag adders.
  rts
Scrooge:
  ldy #10
  sec
  rts
.endproc
.proc KbLegacyExpandedCollisionBox
  cmp #CHARACTER_SCROOGE
  beq Scrooge
  cmp #CHARACTER_LUIGI
  beq Done                     ; Preserve native small/big/crouched Y.
  ldy #15
  cmp #CHARACTER_PIT
  beq Medium
  cmp #CHARACTER_BASS
  beq Medium
  cmp #CHARACTER_SOPHIA
  beq Medium
  lda GuestHurtTicks
  beq Crouch
  iny                          ; Ryu source recoil uses the25NESpx box.
  rts
Crouch:
  lda RgCrouch
  beq Done
Short:
  ldy #17
  rts
Medium:
  ldy #12
  lda RgCrouch
  bne Short
  rts
Done:
  rts
Scrooge:
  ldy #19
  lda RgCrouch
  beq Done
  iny
  rts
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
