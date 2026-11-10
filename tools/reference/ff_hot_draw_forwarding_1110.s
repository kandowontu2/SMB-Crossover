; Same private HotRender frontend: fold identical legacy rows1/2, then
; use row2 for the same public full-cookie FF draw service. No new state.
.setcpu "6502"
.segment "HOT"
FfHotDrawFrontend:
 php
 pha
 txa
 pha
 tya
 pha
 ldx #12
 lda SelectedCharacter
 cmp #CharacterBass
 bne Classify
 lda RlVariant
 bne Pick
Classify:
 lda SelectedCharacter
 cmp #20
 bcs Default
 cmp #15
 bcs Middle
 cmp #10
 bne Low
 lda FmAlts
 and #$44
 cmp #$40
 beq Default
Low:
 ldx #13
 bne Pick
Middle:
 tax
 bne Pick
Default:
 ldx #20
 cmp #22
 bne Pick
 ldx #14
Pick:
 lda TargetLo-12,x
 sta FarcallJmpTarget_SMC+1
 lda TargetHi-12,x
 sta FarcallJmpTarget_SMC+2
 lda TargetBank-12,x
 sta NextBank_SMC+1
 pla
 tay
 pla
 tax
 pla
 sta SafecallA_SMC+1
 plp
 jmp FarCallCommon+3
TargetLo:
 .byte Lo0,Lo1,FfRowLo,Lo3,Lo4,Lo5,Lo6,Lo7,Lo8
TargetHi:
 .byte Hi0,Hi1,FfRowHi,Hi3,Hi4,Hi5,Hi6,Hi7,Hi8
TargetBank:
 .byte Bank0,Bank1,190,Bank3,Bank4,Bank5,Bank6,Bank7,Bank8
