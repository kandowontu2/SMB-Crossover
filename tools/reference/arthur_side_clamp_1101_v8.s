; Arthur source probes remain host X+[0,16]. Exact 215-byte owner successor.
; NativeGuest is also a genuine Ryu entry with arbitrary A; gate the selected byte.
; CMP #32 establishes C=1 for Arthur's SBC#1 / ADC#15 separation.
.segment "SAMUS"
.proc SamusStopAtWallBanked
  ldy R0
  cmp #CHARACTER_PIT
  bcc SideDispatch
  cmp #CHARACTER_RYU
  bne NativeGuest
  jmp SamusRyuWallHandled
NativeGuest:
  sty XgWallContact
SideDispatch:
  lda SelectedCharacter
  cpy #1
  bne Left
  cmp #32
  beq ArthurRight
  lda #14
  bne Probe
Left:
  cmp #CHARACTER_SAMUS
  beq LeftProbe
  lda Player_X_Speed
  cmp #1
  bpl Away
  lda SelectedCharacter
  cmp #32
  beq ArthurLeft
LeftProbe:
  lda #1
Probe:
  ; The two unchanged foreign probe constructions share their arithmetic.
  clc
  adc Player_X_Position
  sta SmTempX
  tay
  lda Player_PageLoc
  adc #0
  sta SmTempPage
  pha
  tya
  and #$f0
  ldy R0
  dey
  bne LeftClamp
  sec
  sbc #15
  sta Player_X_Position
  pla
  sbc #0
  jmp Page
LeftClamp:
  ora #15
  sta Player_X_Position
  pla
  jmp Page
ArthurLeft:
  lda Player_X_Position
  and #$f0
  adc #15
  sta Player_X_Position
  lda Player_PageLoc
  adc #0
  jmp Page
Away:
  sec
  rts
ArthurRight:
  lda Player_X_Position
  and #$f0
  sbc #1
  sta Player_X_Position
  lda Player_PageLoc
  sbc #0
Page:
  sta Player_PageLoc
  ldy #$10
  sty SideCollisionTimer
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  beq HurtWallReceipt
  lda GuestHurtTicks
  beq :+
HurtWallReceipt:
  lda R0
  eor #$ff
  and Player_CollisionBits
  sta Player_CollisionBits
:
  lda SelectedCharacter
  cmp #CHARACTER_SAMUS
  bne OtherWallVelocity
  ldy R0
  cpy #2
  beq SamusLeftVelocity
  lda MmVX+2
  bmi KeepSamusVelocity
  ora MmVX+1
  ora MmVX
  bne StopAllVelocity
KeepSamusVelocity:
  lda #0
  sta MmXFraction
  sta MmXFraction+1
  sta Player_X_Scroll
  sec
  rts
SamusLeftVelocity:
  lda MmVX+2
  bpl KeepSamusVelocity
  ; Negative A cannot equal the positive CHARACTER_SIMON constant below.
OtherWallVelocity:
  cmp #CHARACTER_SIMON
  beq ClearWallRemainder
StopAllVelocity:
  lda #0
  sta MmVX
  sta MmVX+1
  sta MmVX+2
ClearWallRemainder:
  lda #0
  sta Player_X_Speed
  beq KeepSamusVelocity

End:
.endproc
