; UNADOPTED shared-hook sizing. Original59B slot; this exact worker fits57B plus2B padding.
; New CF path is externally full16-cookie authenticated through actual B0206.
.setcpu "6502"
.import SelectedCharacter,SmFreezeRenderState,FfMuxNativeROM,FfMuxNativeTail
.import SamusFreezeRenderFinish,BtServiceVeneers,FarCallCommon
.import SafecallA_SMC,FarcallJmpTarget_SMC
.export CfSharedDrawSelect,CfSharedDrawSelectEnd
.macro CFP_FAR target,mode
 sta SafecallA_SMC+1
 lda #<target
 sta FarcallJmpTarget_SMC+1
 lda #>target
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(target)|$80)
 jmp FarCallCommon
.endmacro
.segment "CF_SHARED_DRAW_FACTOR_PROPOSAL"
CfSharedDrawSelect:
 lda SelectedCharacter
 eor #31                 ; compare equality WITHOUT changing callerCarry
 beq CF
 ; EXACT original decision/input, including stale state on every foreign.
 lda SmFreezeRenderState
 beq Native
 ; True same-bank native tail body, zero-byte label after its old PLA/PLP.
 ; Same18B SMC/actualnative farcall, same caller return depth; +3CPU vsinline.
 jsr FfMuxNativeTail
 CFP_FAR SamusFreezeRenderFinish,jmp
Native:
 jmp FfMuxNativeROM
CF:
 ; Original path already discarded incomingA and delivered this realstateA.
 ; Preserve it while deliberately bypassing old SamusFinish under newowner.
 lda SmFreezeRenderState
 CFP_FAR BtServiceVeneers+18,jmp
CfSharedDrawSelectEnd:
.assert CfSharedDrawSelectEnd-CfSharedDrawSelect=57,error,"Measured57B within original59"
