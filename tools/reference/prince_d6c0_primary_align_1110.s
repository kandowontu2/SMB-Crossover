; Typed to original 7:D634 and 7:D6C0. C40B and its other callers stay exact.
.setcpu "6502"
.segment "CODE"
.export PpSavePrimaryAlign,PpRestorePrimaryAlign

WorldAlign = $c40b
RawQuery = $c078
SavedPrimary = $c0a1

PpSavePrimaryAlign:
 jsr WorldAlign
 ldx #2
Save:
 lda RawQuery,x
 sta SavedPrimary,x
 dex
 bpl Save
 rts

PpRestorePrimaryAlign:
 ldx #2
Restore:
 lda SavedPrimary,x
 sta RawQuery,x
 dex
 bpl Restore
 jmp WorldAlign
