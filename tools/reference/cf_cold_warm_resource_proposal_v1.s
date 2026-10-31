; MEASUREMENT ONLY. Two currently ungranted spans; no host/cart allocation.
.setcpu "6502"
.import SelectedCharacter,CfRetire,CfOrBtCheck,CfLoaderProposal
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
 bcc Cold
 rts                             ; full-cookie/class valid, C1; no copy
Cold:
 jmp CfLoaderProposal             ; same genuine ROM115, original caller frame
CfLoadIfColdEnd:
.assert CfLoadIfColdEnd-CfLoadIfCold=24,error,"Measured24B"
