; Guard only the provably empty BOTH-groups case. Every nonzero flag or
; private stamp resumes literal original loops and their original visible work.
; No RAM borrow or foreground hardware math. Icon/ammo code supplies final ABI.
.if ::MAPPER_MMC5
.pushseg
.segment "TMNT_CORE"
.proc TnSkipEmptyEquipmentScans
 ldx TnDrawSlot
 dex
 bmi CheckEmpty
 jmp ::TnDrawEquipment::Shot
CheckEmpty:
 lda TnDropKind
 ora TnDropKind+1
 ora TnDropKind+2
 ora TnDropKind+3
 bne Original
 lda TnPickupStamp
 ora TnPickupStamp+1
 ora TnPickupStamp+2
 ora TnPickupStamp+3
 ora TnPickupStamp+4
 ora TnPickupStamp+5
 bne Original
 lda #0
 sta TnDrawSlot
 ldx #$ff
 jmp TnEquipmentIconResume
Original:
 jmp TnEquipmentScansResume
.endproc
.assert TnSkipEmptyEquipmentScans=$b020,lderror,"Append within unallocated TMNT_CORE tail"
.export TnSkipEmptyEquipmentScans,TnEquipmentScansResume,TnEquipmentIconResume
.popseg
.endif
