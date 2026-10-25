; Static level agent integrates only this block in its reserved42-byte native
; DrawSmallPlatform tail, with OBJECT bank0 mapped by RunLargePlatform.
; Root replaces its existing JSR LargePlatformBoundBox with JSR this routine.
; Never treat small-lift Enemy_State (secondY) as a helper marker.
.proc HpNativePlatformBBoxGate
  lda Enemy_ID,x
  cmp #$25
  beq Tag
  cmp #$28
  bne Native
Tag:
  lda Enemy_State,x
  and #$40
  beq Native
  farcall HpNativePlatformBBoxCold
  rts
Native:
  jmp LargePlatformBoundBox
.endproc
.assert *-HpNativePlatformBBoxGate <=42,error,"Native helper bbox gate exceeds42B"
