; SIZE/ABI PROPOSAL ONLY. Not installed or linked into any source candidate.
.setcpu "6502"
.import SelectedCharacter,BwBtResolve,BtCacheServices,BtColdPortrait,BtColdColors
.import FarCallCommon,FarcallJmpTarget_SMC,SafecallA_SMC,NextBank_SMC
.export BwServiceVeneers,BtServiceVeneers,BtServiceUnavailable,BtRouter
.segment "BT_ROM_ROUTER"
BwServiceVeneers:
BtServiceVeneers:
.repeat 36
 jmp BtRouter
.endrepeat
BtServiceUnavailable:clc
 rts
BtRouter:
 php
 pha
 txa
 pha
 tya
 pha
 ; Equivalent13B owner gate: exactly27/31/33, no native flags consumed.
 lda SelectedCharacter
 cmp #33
 beq Owner
 and #$fb
 cmp #27
 bne Bad
Owner:
 ; No nested call or write of any SMC byte precedes this capture. The
 ; genuine incoming SFC target remains B020+3*service; all33SMC is saved
 ; by both actual vector paths. There is NO own rowJSR return to consume.
 lda FarcallJmpTarget_SMC+1
 sec
 sbc #<BtServiceVeneers
 ; Original nativeAXYP is already saved. X is only resolver service temp.
 tax
 lda SelectedCharacter
 cmp #33
 bne Default
 txa
 cmp #51
 beq Portrait
 cmp #78
 bne Default
 lda #<BtColdColors
 bne Cold
Portrait:
 lda #<BtColdPortrait
Cold:
 sta FarcallJmpTarget_SMC+1
 lda #>BtColdPortrait
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(BtColdPortrait)|$80)
 bne Target
Default:
 txa
 sta SafecallA_SMC+1
 lda #<BwBtResolve
 sta FarcallJmpTarget_SMC+1
 lda #>BwBtResolve
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(BwBtResolve)|$80)
 jsr FarCallCommon
 bcc Bad
Target:
 sta NextBank_SMC+1
 pla
 tay
 pla
 tax
 pla
 sta SafecallA_SMC+1
 plp
 jmp FarCallCommon+3
Bad:
 pla
 tay
 pla
 tax
 pla
 sta SafecallA_SMC+1
 pla
 and #$fe
 pha
 lda SafecallA_SMC+1
 plp
 rts
.assert *-BtServiceVeneers=223,error,"Measured223/224 only"
.assert >BtColdPortrait=>BtColdColors,lderror,"True owned cold targets share high"
.assert .bank(BtColdPortrait)=.bank(BtColdColors),lderror,"True owned cold targets share bank"
.assert .lobyte(BtColdColors)<>0,lderror,"Literal cold branch always"
.assert .lobyte(.bank(BtColdPortrait)|$80)<>0,lderror,"ROM raw bank nonzero"
.assert >BtServiceVeneers=>(BtServiceVeneers+107),lderror,"All36 low offsets same page"
.assert .lobyte(BtCacheServices)=0,lderror,"Actual A000 cache API"
