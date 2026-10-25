; Match InventoryDrawPickups::Drops age/parity admission; supplied art is unchanged.
; Appended after existing ROLL_CORE owners to retain all existing code PCs.
.pushseg
.segment "ROLL_CORE"
.proc RlDropVisibleKind
 lda InvDropKind,x
 beq Done
 php
 lda InvDropAgeHi,x
 bne Fade
 lda InvDropAge,x
 cmp #240
 bcc Visible
Fade:
 lda FrameCounter
 and #1
 beq Visible
 plp
 lda #0
 rts
Visible:
 plp
 lda InvDropKind,x
Done:rts
.endproc
.popseg
