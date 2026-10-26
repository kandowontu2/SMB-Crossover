; Ordinary ownership stores retain A/X/Y/P. Only an active CV3 source
; lane adds stop/restore writes; all existing samples stay in original E127.
.proc Cv3DmcOwnerWrite
 jsr TnDmcOwnerAdmission
 php
 pha
 lda Cv3DmcPriority
 beq Done
 lda GuestCombinedEnable
 and #15
 sta $4015
 lda #$ff
 sta $5117
 lda #0
 sta Cv3DmcPriority
Done:pla
 plp
 rts
.endproc
.assert Cv3DmcOwnerWrite=$fee1,lderror,"Existing Link sample alignment gap"
.assert *=$ff00,lderror,"Preserve original Simon sample start"
