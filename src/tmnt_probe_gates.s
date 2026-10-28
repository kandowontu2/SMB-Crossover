; Replace the outer head/side trip with the same exact-ID admissions in the
; already required turtle bank. Other non-Mac profiles keep their original
; next dispatch. Mac retains the complete original terrain implementation.
.pushseg
.segment "TMNT_COMBAT"
.macro TnProbeGate Name,Own,Mac,Other
.if ::MAPPER_MMC5 .and .xmatch(Name,TnFastSideGate)
.proc Name
 ; The only compiled callers use the standard farcall, whose preserved
 ; SafecallA is the incoming A. No intervening calls precede the reload.
 ; Native turtle/Mac leaves load A before consuming it; keep original P.
 php
 lda SelectedCharacter
 cmp #19
 bne CheckMac
 plp
 jmp Own
CheckMac:
 cmp #15
 beq IsMac
 lda SafecallA_SMC+1
 plp
 farcall Other,jmp
IsMac:
 plp
 jmp Mac
 .res 1,$ea
 .assert *-Name=43,error,"Original side-gate span"
.endproc
.else
.proc Name
 php
 pha
 lda SelectedCharacter
 cmp #19
 bne CheckMac
 pla
 plp
 jmp Own
CheckMac:
 cmp #15
 beq IsMac
 pla
 plp
 farcall Other,jmp
IsMac:
 pla
 plp
 jmp Mac
.endproc
.endif
.endmacro
TnProbeGate TnFastSideGate,TnSideDispatch,TnMacSideProbe,NrSide
.proc TnFastHeadGate
 php
 pha
 lda SelectedCharacter
 cmp #19
 bne CheckMac
 pla
 plp
 jmp TnHeadDispatch
CheckMac:
 cmp #15
 beq IsMac
 ; Transfer the existing saved A/P to the CV3 selector. The turtle and
 ; Mac branches are byte/cycle exact; other guests add only this JMP and
 ; a comparison before their original bank call.
 cmp #CHARACTER_BASS
 beq Bass
 jmp Z2HeadAdmission
Bass:jmp BassHeadAdmission
 .res 10,$ea
IsMac:
 pla
 plp
 jmp TnMacHeadProbe
.endproc
.export TnFastSideGate,TnFastHeadGate
.include "tmnt_mac_probes.inc"
.popseg
