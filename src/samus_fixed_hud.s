; HUD-only fixed page20/pairs6,7; original world capsule untouched.
; SPECIAL_ROSTER is mapped in A. The renderer needs the same physical record
; at its genuine C-window alias, because farcall maps A to METASPRITE.
.pushseg
.segment "SPECIAL_ROSTER"
.proc SamusFixedMissileHud
 sta AvDrawDirection
 lda AvDrawArt
 cmp #AV_ART_SAMUSPICKUP7
 bne Native
 lda #<(SamusFixedHudRecord+$2000)
 sta R0
 lda #>(SamusFixedHudRecord+$2000)
 sta R1
 BankPRGC #.bank(SamusFixedHudRecord)
 jmp RemainingDraw::FixedHudRender
Native:
 jmp BillCapsuleHudAnchor
.endproc
SamusFixedHudRecord:
 .byte 8
 .byte $4d,$c2,-4,-5
 .byte $4f,$c2,-4,3
; Only Bill/Lance use the free upper HUD gap. The existing Samus
; helper/record keep their addresses. Draw reloads A, and all live
; outputs/flags are qualified through the complete RemainingDraw caller.
.proc BillCapsuleHudAnchor
 lda SelectedCharacter
 cmp #CHARACTER_BILL
 bne Original
 lda #120
 sta R4
 lda #16
 sta R6
Original:
 jmp RemainingDraw::Draw
.endproc
.assert SamusFixedMissileHud=$bfae,error,"Verified existing bank61 tail"
.assert *-SamusFixedMissileHud<=82,error,"Verified tail capacity"
.assert .bank(SamusFixedHudRecord)=61,error,"C alias must map physical61"
.popseg
