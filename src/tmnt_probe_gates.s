; Replace the outer head/side trip with the same exact-ID admissions in the
; already required turtle bank. Other non-Mac profiles keep their original
; next dispatch. Mac retains the complete original terrain implementation.
.pushseg
.segment "TMNT_COMBAT"
.macro TnProbeGate Name,Own,Mac,Other
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
.endmacro
TnProbeGate TnFastSideGate,TnSideDispatch,TnMacSideProbe,M3SideDispatch
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
 jmp TnCv3HeadGate
 .res 17,$ea
IsMac:
 pla
 plp
 jmp TnMacHeadProbe
.endproc
.export TnFastSideGate,TnFastHeadGate
.include "tmnt_mac_probes.inc"
.popseg
