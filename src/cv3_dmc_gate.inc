; Executes identically in E127 and its E125 mirror. No shared SMC farcall.
.proc Cv3DmcStartGate
 sta Cv3DmcEntryA
 lda CurrentBankC
 sta Cv3DmcSavedC
 lda #$fd
 sta CurrentBankC
 sta $5116
 lda Cv3DmcEntryA
 jsr Cv3DmcStart
 pha
 php
 lda Cv3DmcSavedC
 sta CurrentBankC
 sta $5116
 plp
 pla
 rts
.endproc
.assert Cv3DmcStartGate=$fe15,lderror,"Existing Bass sample alignment gap"
.assert *<=$fe40,lderror,"Preserve original Link sample start"
