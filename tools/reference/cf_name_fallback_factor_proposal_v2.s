; MEASUREMENT ONLY. Repack the already-owned A67 private selector/fallback.
.setcpu "6502"
.import SelectedCharacter,BwLoad,CfLoadIfCold
.import FarcallJmpTarget_SMC,FarCallCommon
.segment "CF_NAME_FALLBACK_MEASURE"
MeasuredFallback:
 ldx #1
 cmp #45
 beq MeasurementTarget
 ldx #3
 cmp #54
 beq MeasurementTarget
 inx
 cmp #57
 beq MeasurementTarget
 clc
 rts
.assert *-MeasuredFallback=19,error,"15/18/19 genuine ROM fallback19B"
; This LOCAL RTS is only an assembly sizing target. In the real same-object
; source repack all three branches keep actual existing BwResolveROM. The
; measurement tool separately proves those actual linked backward distances.
MeasurementTarget:rts
.segment "CF_LOAD_SELECTOR_MEASURE"
MeasuredSelector:
 lda SelectedCharacter
 cmp #31
 beq CF
 lda #<BwLoad
 ldx #>BwLoad
 ldy #.lobyte(.bank(BwLoad)|$80)
 bne Publish
CF:
 lda #<CfLoadIfCold
 ldx #>CfLoadIfCold
 ldy #.lobyte(.bank(CfLoadIfCold)|$80)
Publish:
 sta FarcallJmpTarget_SMC+1
 stx FarcallJmpTarget_SMC+2
 tya
 jmp FarCallCommon
.assert *-MeasuredSelector=31,error,"Private no-argument selected loader31B"
