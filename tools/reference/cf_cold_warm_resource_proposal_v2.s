; MEASUREMENT ONLY. Two currently ungranted spans; no host/cart allocation.
.setcpu "6502"
.import SelectedCharacter,CfRetire,CfOrBtCheck,CfLoaderProposal,BtServiceVeneers
.import SafecallA_SMC,FarcallJmpTarget_SMC,FarCallCommon
.export CfSceneRetireForeign,CfSceneRetireForeignEnd
.export CfLoadIfCold,CfLoadIfColdEnd
.segment "CF_SCENE_RETIRE_PROPOSAL"
CfSceneRetireForeign:
 php
 pha
 lda SelectedCharacter
 cmp #31
 beq Own
 pla
 plp
 jmp CfRetire                    ; same genuine ROM69
Own:
 pla
 plp
 rts
CfSceneRetireForeignEnd:
.assert CfSceneRetireForeignEnd-CfSceneRetireForeign=17,error,"Measured17B"
.segment "CF_WARM_LOAD_PROPOSAL"
CfLoadIfCold:
 sta SafecallA_SMC+1
 lda #<CfOrBtCheck
 sta FarcallJmpTarget_SMC+1
 lda #>CfOrBtCheck
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(CfOrBtCheck)|$80)
 jsr FarCallCommon
 bcs Ensure
 jsr CfLoaderProposal             ; actual verifiedcopy C1 only
 bcc Done
Ensure:
 ; Genuine shared row15 runs its actual ROM guard before any A2 opcode.
 ; Bowser's existing direct constructor remains separate and unchanged.
 lda #<(BtServiceVeneers+45)
 sta FarcallJmpTarget_SMC+1
 lda #>(BtServiceVeneers+45)
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(BtServiceVeneers)|$80)
 jsr FarCallCommon
 clc                             ; completed CF path: skip Bowser constructor
Done:
 rts
CfLoadIfColdEnd:
.assert CfLoadIfColdEnd-CfLoadIfCold=45,error,"Measured45B"
