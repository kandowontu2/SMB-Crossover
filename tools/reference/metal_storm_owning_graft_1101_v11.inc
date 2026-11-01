; Private owning-composition proposal. CHR is granted; ROM/RAM are NOT granted.
; Called only after complete C2/C3 authentication by the ROM gate. R0..R7 are
; foreground03..0A; native NMI00..02 are never borrowed. No menu ingress here.
.macro Ms11EmitUpdateEntry
Ms11UpdateGate:
 jsr Ms8GateAuth
 rts
.endmacro

.macro Ms11SelectUpdateBeforeReady
 tsx
 lda $010a,x
 cmp #<(Ms11UpdateGate+2)
 beq Ms11GateUpdateCall
.endmacro

.macro Ms11EmitUpdateCall
Ms11GateUpdateCall:
 jsr Ms11RenderUpdate
 bcs Ms8GateAccepted
 bcc Ms8GateBad
.endmacro

.macro Ms11EmitUpdate
; A/X = actual host-area right-bound low/high on the first accepted call.
; Existing source constructor supplies the original actor slots/activation,
; gravity reset, fractions and animation mask. No captured donor RAM image.
; Native scene8 and normal YHigh1 are required by the outer/source guards.
; Source-owned clock/input ordering and epoch guard remain in MsHostStep.
; Caller camera follows this single source world-delta application.
; All AXYP except result C, foreground R0..R7 and five SMC operands retained.
Ms11RenderUpdate:
 jsr MsRSave
 lda $c800
 cmp #$a7
 beq Ms11UpdateStep
 ; Gate stack keeps the original caller registers across authentication.
 ; Its9 saved bytes plus this child JSR put originalA at+10, X at+9.
 ; MsRSave captures the volatile transport registers, not these arguments.
 tsx
 lda $010a,x
 pha
 lda $0109,x
 tax
 pla
 MsRFar MsHostSetBounds,3
 MsRFar MsNativeConstruct,3
 bcc Ms11UpdateRejected
Ms11UpdateStep:
 MsRFar MsHostStep,3
 bcc Ms11UpdateRejected
 MsRFar MsNativeApplyDelta,3
 jsr MsRRestore
 sec
 rts
Ms11UpdateRejected:
 jsr MsRRestore
 clc
 rts
Ms11UpdateEnd:
.endmacro
