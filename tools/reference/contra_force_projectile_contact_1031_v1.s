; Actual CF radius comparator adapted to a static native target rectangle.
; Dx/Dy are signed16 in R2/R3; R0/R1 are inclusive raw-OAM target bounds;
; R4 is the genuine source half extent. R5/R6 cache source X/Y radii.
; Original strict |delta| < sum(radii) becomes 0 < d+r-left <= 2r+right-left.
.setcpu "6502"
.import CfCallA,CfTarget,CfTargetBank,CfEnemySlot
.importzp R0,R1,R2,R3,R4,R5,R6,R7,Enemy_ID,Enemy_State
.export CfContactAxis,CfContactAxisEnd,CfContactAxisGate,CfNativeTargetTop,CfNativeTargetTopEnd
.segment "CF_CONTACT_AXIS"
CfContactAxis:
 ldx CfEnemySlot
 lda Enemy_ID,x
 cmp #6
 bne Axis
 lda Enemy_State,x
 cmp #2
 bcs No                    ; stomp-squished Goomba is already dead
Axis:
 lda R1
 sec
 sbc R0
 clc
 adc R4
 clc
 adc R4
 sta R1
 lda #0
 adc #0
 sta R7
 lda R2
 clc
 adc R4
 sta R2
 lda R3
 adc #0
 sta R3
 lda R2
 sec
 sbc R0
 sta R2
 lda R3
 sbc #0
 sta R3
 ora R2
 beq No
 lda R3
 cmp R7
 bcc Yes
 bne No
 lda R2
 cmp R1
 bcc Yes
 beq Yes
No:clc
 rts
Yes:sec
 rts
CfContactAxisEnd:
.assert CfContactAxisEnd-CfContactAxis<=84,error,"existing84B A1 tail"
.segment "CF_CONTACT_GATE"
CfContactAxisGate:
 php
 pha
 lda #<CfContactAxis
 sta CfTarget
 lda #>CfContactAxis
 sta CfTarget+1
 lda #.lobyte(.bank(CfContactAxis))
 sta CfTargetBank
 pla
 plp
 jmp CfCallA
.segment "CF_CONTACT_TARGET"
; Encoded top+1 from genuine native living-pose raw-OAM cells. Hardware
; adds1 to BOTH source and target display Y; retain original coordinate units.
; Left0/right15/bottom23. Zero preserves hazards and rejects no-op IDs.
CfNativeTargetTop:
 .byte 1,1,0,1,0,1,9,1,0,0,9,9,0,1,1,1,1,1,9,0,9
CfNativeTargetTopEnd:
.assert CfNativeTargetTopEnd-CfNativeTargetTop=21,error,"typed ordinary21"
