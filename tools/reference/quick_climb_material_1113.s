; SMB climbables are handled by the retained native BG/climbing consumer.
; Source geometry, source motion and ordinary/base solidity stay unchanged.
; Existing valid-row SBC has C=1. The mask restores it and all caller flags;
; BCS skips the original HostEmpty LDA#0 without changing the five-byte site.
.segment "WORLD_HOOK"
 jsr QmNativeClimbMaterial
 bcs HostMaterial

; Explicitly inside the existing seven-page Quick code copy/allocation.
; Original native callback finishes with LDA#3C, so its final N/Z also match.
.segment "CLIMB_MASK"
QmNativeClimbMaterial:
 php
 and #3
 cmp #1
 beq MaterialReady
 lda #0
MaterialReady:
 plp
 rts
