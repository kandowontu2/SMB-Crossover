; PRIVATE motion/BG caller prototype. Never shared admission or native proof.
; Real PLAYER caller owns no live incoming R0..R7 across movement. The narrow
; movement flush therefore deliberately clobbers them; preserved standalone
; RdTxAfterMovement remains separate, including its documented SP192 negative.
.pushseg
.segment "ROGUE_DAWN_HOST"
.export RdTxMovement,RdTxMovementEnd
.proc RdTxMovement
 php
 pha
 jsr RdHostEnabled
 bcs Own
 pla
 plp
 farcall SamusMovement,jmp       ; genuine normal-Samus target, no state alias
Own:
 pla
 plp
 jsr RdTxMovementBegin          ; clear borrowed cells before every admitted step
 lda CurrentBankC
 pha
 BankPRGC #94                  ; frozen ART and genuine callback bridge
 jsr RdHsImportPosition
 jsr RdHsClockBefore
 farcall RdControlStep
 jsr RdHsExportPosition
 jsr RdTxMovementFlush          ; shallow real native owner, BEFORE weapons
 jsr RdHsClockAfter
 pla
 BankPRGC a                    ; restore actual caller's declared C lease
 rts
.endproc
RdTxMovementEnd:
.assert * <= $c000,error,"Approved A95 host capacity"
.popseg
