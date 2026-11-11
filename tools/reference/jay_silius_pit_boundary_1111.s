; Enter after the native terrain gate has accepted identity, Main, input
; direction and foreground context. X contains the rejected query's reason.
; Below the last SMB buffer row, the actor must continue into native death.
.setcpu "6502"
.segment "HANDOFF"

LowerTerrainGuard:
 stx TileStatus
 cpx #3
 bne RejectOutsideFloor
 lda TileQueryY
 cmp #15
 bcc RejectOutsideFloor
 cmp #$80
 bcs RejectOutsideFloor
 lda #0
 sta TileStatus
 jmp EncodeTileClass
RejectOutsideFloor:
 jmp LegacyTileReject
