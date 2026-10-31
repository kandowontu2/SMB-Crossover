; PROPOSAL ONLY: external ROM authentication BEFORE any rawA2 opcode.
; Placement is not allocated by this file. Parent owns shared dispatch.
.setcpu "6502"
.import SelectedCharacter,FmGroups,CurrentBankC
.import FarCallCommon,SafecallA_SMC,FarcallJmpTarget_SMC,BtCheck
.export CfOrBtCheck,CfExternalCookie,CfExternalGuardEnd
.segment "CF_ROM_GUARD"
CfOrBtCheck:
 php
 pha
 lda SelectedCharacter
 cmp #31
 beq CfExternalCheck
 ; Exact genuine BtCheck ingress ABI for original raw33 and all its
 ; foreign rejections. No alias to RAM/another family's private scratch.
 pla
 plp
 sta SafecallA_SMC+1
 lda #<BtCheck
 sta FarcallJmpTarget_SMC+1
 lda #>BtCheck
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(BtCheck)|$80)
 jmp FarCallCommon
CfExternalCheck:
 txa
 pha
 lda CurrentBankC
 pha
 lda #2
 sta CurrentBankC
 sta $5116
 ldx #15
CfExternalByte:
 cpx #2
 beq CfExternalNext
 lda $dfe0,x
 cmp CfExternalCookie,x
 bne CfExternalNo
CfExternalNext:
 dex
 bpl CfExternalByte
 lda FmGroups
 lsr
 lsr
 lsr
 and #3
 cmp $dfe2
 bne CfExternalNo
 tsx
 lda $0104,x
 ora #1
 bne CfExternalSet
CfExternalNo:
 tsx
 lda $0104,x
 and #$fe
CfExternalSet:
 sta $0104,x
 pla
 sta CurrentBankC
 sta $5116
 pla
 tax
 pla
 plp
 rts
CfExternalCookie:
 ; Builder includes the exact same final ROM cookie used by the loader.
 ; Source/variant byte2 is dynamic and compared separately above.
.incbin "cf-cookie.bin"
CfExternalGuardEnd:
