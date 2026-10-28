; PRIVATE exact-owner hook adapters. ROOT has not admitted Rogue to the menu.
; No shared file is modified: sparse recipe replaces only the original5B
; NrPrepare prologue and keeps its actual continuation/old following PCs.
.pushseg
.segment "NEW_ROSTER_GATE"
.export RdNrPrepare
.proc RdNrPrepare
 php
 pha
 lda SelectedCharacter
 cmp #2
 bne Legacy
 lda RdVariant
 cmp #1
 bne Legacy
 pla
 plp
 farcall RdTxPrepareActor,jmp
Legacy:
 lda SelectedCharacter         ; genuine overwritten original instruction
 jmp RdNrPrepareLegacy         ; original PHP/PHA still live on real stack
.endproc
.assert * <= $ae00,lderror,"Rogue private hooks overlap frozen AUX"
.popseg
