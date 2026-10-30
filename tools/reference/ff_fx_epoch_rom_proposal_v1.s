; Relocatable sizing proposal ONLY. These workers are not installed.
; Requested replacement of four currently unconsumed own26B kernel gates:
; FwActionTick/FwWeapons/FwEnemyContact/FwForgetEnemy, A62ADDE..<AE46.
.setcpu "6502"
.import SelectedCharacter,FwCheck,FwCallEnter,FwPaletteTick,DrawAllMetasprites
.import FarCallCommon,SafecallA_SMC,FarcallJmpTarget_SMC
.import FfMuxNativeLate,FfMuxHeartbeat
.export FfMuxNativeROM,FfMuxTickROM,FfMuxProposalEnd
.segment "FF_MUX_ROM_PROPOSAL"
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
 bne Native
 jsr FwCheck
 bcc Native
 pla
 plp
 MP_WORKER FfMuxNativeLate
Native:
 pla
 plp
 sta SafecallA_SMC+1
 lda #<DrawAllMetasprites
 sta FarcallJmpTarget_SMC+1
 lda #>DrawAllMetasprites
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(DrawAllMetasprites)|$80)
 jmp FarCallCommon
.assert *-FfMuxNativeROM=52,error,"Measured native selector52B"

; Genuine row29 UI runs before the pause branch, including draw-skipped Main.
; Retain body palette service exactly, then only verified selectedFF can enter
; a RAM3 heartbeat that preserves every old result/native scratch output.
FfMuxTickROM:
 jsr FwPaletteTick
 php
 jsr FwCheck
 bcc Cold
 plp
 MP_WORKER FfMuxHeartbeat
Cold:
 plp
 rts
FfMuxProposalEnd:
.assert FfMuxProposalEnd-FfMuxTickROM=28,error,"Measured heartbeat28B"
.assert FfMuxProposalEnd-FfMuxNativeROM=80,error,"80B of proposed104B own gate block"
