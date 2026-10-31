; Relocatable sizing proposal ONLY. These workers are not installed.
; Requested replacement of four currently unconsumed own26B kernel gates:
; FwActionTick/FwWeapons/FwEnemyContact/FwForgetEnemy, A62ADDE..<AE46.
.setcpu "6502"
.import SelectedCharacter,FwPaletteTick,DrawAllMetasprites
.import FarCallCommon,SafecallA_SMC,FarcallJmpTarget_SMC
.import FfMuxNativeLate,FfMuxHeartbeat
.export FfMuxNativeROM,FfMuxTickROM,FfMuxProposalEnd
.segment "FF_ROM_HOST"
.macro MP_WORKER target
 sta SafecallA_SMC+1
 lda #<target
 sta FarcallJmpTarget_SMC+1
 lda #>target
 sta FarcallJmpTarget_SMC+2
 jmp FwCallEnter
.endmacro
FfMuxNativeROM:
 php
 pha
 lda SelectedCharacter
 cmp #22
 bne FfMuxRomNative
 jsr FwCheck
 bcc FfMuxRomNative
 pla
 plp
 ; Complete original DrawAll BEFORE capturing its genuine output C bank.
 ; FwCallEnter then preserves that actual publication while filtering OAM.
 sta SafecallA_SMC+1
 lda #<DrawAllMetasprites
 sta FarcallJmpTarget_SMC+1
 lda #>DrawAllMetasprites
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(DrawAllMetasprites)|$80)
 jsr FarCallCommon
 MP_WORKER FfMuxNativeLate
FfMuxRomNative:
 pla
 plp
.export FfMuxNativeTail
FfMuxNativeTail:
 sta SafecallA_SMC+1
 lda #<DrawAllMetasprites
 sta FarcallJmpTarget_SMC+1
 lda #>DrawAllMetasprites
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(DrawAllMetasprites)|$80)
 jmp FarCallCommon
.assert *-FfMuxNativeROM=70,error,"Measured native selector70B"

; Genuine row29 UI runs before the pause branch, including draw-skipped Main.
; Retain body palette service exactly, then only verified selectedFF can enter
; a RAM3 heartbeat that preserves every old result/native scratch output.
FfMuxTickROM:
 jsr FwPaletteTick
 php
 jsr FwCheck
 bcc FfMuxRomCold
 plp
 MP_WORKER FfMuxHeartbeat
FfMuxRomCold:
 plp
 rts
FfMuxProposalEnd:
.assert FfMuxProposalEnd-FfMuxTickROM=28,error,"Measured heartbeat28B"
.assert FfMuxProposalEnd-FfMuxNativeROM=98,error,"98B of granted104B own gate block"

 .res 104-(*-FfMuxNativeROM),$ea
 .assert *-FfMuxNativeROM=104,error,"Explicit retired104B owner span"
