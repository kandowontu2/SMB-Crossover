; These collision queries receive the raw character ID in A. Preserve the
; original Roll selected-alternate override, and retain the old full router
; for mismatched/unsupported input. Actual native profile leaves stay intact.
.pushseg
.segment "HOT_COLLISION_GATE"
.macro HotCollision Name,OwnRoll,Kirby,Chip,Mac,Mike,Mario3,Vic,Turtle,Original
.proc Name
 php
 pha
 lda SelectedCharacter
 cmp #CHARACTER_BASS
 bne NotRoll
 lda RlVariant
 beq NotRoll
 pla
 plp
 farcall OwnRoll,jmp
NotRoll:
 pla
 pha
 cmp SelectedCharacter
 jne Fallback
 cmp #20
 jcs Fallback
 cmp #14
 bcc ToKirby
 beq ToChip
 cmp #15
 beq ToMac
 cmp #16
 beq ToMike
 cmp #17
 beq ToMario3
 cmp #18
 beq ToVic
 ; Only19 remains; its existing native leaf retains its exact flag contract.
 pla
 plp
 farcall Turtle,jmp
ToKirby:
 pla
 plp
 farcall Kirby,jmp
ToChip:
 pla
 plp
 farcall Chip,jmp
ToMac:
 pla
 plp
 ; Both exact-ID Mac leaves are LDY0 and return carry set by CMP15.
 ; Reuse that three-instruction result without another bank round trip.
 ldy #0
 sec
 rts
ToMike:
 pla
 plp
 farcall Mike,jmp
ToMario3:
 pla
 plp
 farcall Mario3,jmp
ToVic:
 pla
 plp
 farcall Vic,jmp
Fallback:
 pla
 plp
 farcall Original,jmp
.endproc
.endmacro
HotCollision HotCollisionAdder,RlAdder,KbAdderDispatch,CdAdderDispatch,LmAdderGate,JnAdderDispatch,M3AdderDispatch,VvAdderDispatch,TnAdderDispatch,RlAdderDispatch
HotCollision HotCollisionBox,RlBox,KbBoxDispatch,CdBoxDispatch,LmBoxGate,JnBoxDispatch,M3BoxDispatch,VvBoxDispatch,TnBoxDispatch,RlBoxDispatch
.popseg
