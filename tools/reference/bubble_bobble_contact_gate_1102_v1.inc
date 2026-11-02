; Private proposal replacing exactly the existing raw25/native body gate.
; The outer real farcall already holds incoming A in SafecallA_SMC.
; Both owned tails branch to the preceding, unchanged JMP FarCallCommon.
.segment "BB_CONTACT_GATE"
.export BbContactGate,BbContactGateEnd
BbContactGate:
 php
 lda SelectedCharacter
 cmp #25
 beq BbContactS2
 cmp #39
 beq BbContactOwn
 lda SafecallA_SMC+1
 plp
 jmp NativeBodyTail
BbContactS2:
 plp
 lda #$15
 sta FarcallJmpTarget_SMC+1
 lda #$bb
 sta FarcallJmpTarget_SMC+2
 lda #$f6
BbContactS2Far:
 bne *-35
 .assert SharedFarJump=BbContactS2Far-35,lderror,"Shared current FarCall tail"
BbContactOwn:
 plp
 ; Incoming A is already in SafecallA_SMC from the real outer farcall.
 lda #<BbBodyVeneer
 sta FarcallJmpTarget_SMC+1
 lda #>BbBodyVeneer
 sta FarcallJmpTarget_SMC+2
 lda #$c1
BbContactOwnFar:
 bne *-50
 .assert SharedFarJump=BbContactOwnFar-50,lderror,"Shared current FarCall tail"
BbContactGateEnd:
