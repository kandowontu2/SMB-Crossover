; Stateless exact unused-OAM metadata tail. MAIN still chooses the real
; visible family and clears every unused attribute's transient bit4.
.setcpu "6502"
.segment "TAIL"
FfMuxUnusedTail:
Loop:
 lda Sprite_Attributes,x
 and #$ef
 sta Sprite_Attributes,x
 inx
 inx
 inx
 inx
 cpx RgOamRotation
 bne Loop
 rts
.segment "STUB"
FfMuxUnusedTailStub:
 jsr FfMuxUnusedTail
 jmp FfMuxOriginalPacketCall
