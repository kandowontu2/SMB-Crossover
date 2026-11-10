; Restore every wrestler's original secondary palette on each owned mux turn.
; The old native-mask table is losslessly packed to fund all helpers/data.
.setcpu "6502"
.segment "MASK"
WfPackedNativeMask:
.byte NATIVE_PACKED
WfMaskValues:.byte 0,2,3,15
; Private EarlyActor leaf. X is the actor index; A is the admitted object ID.
; Y and carry are dead before the following native attribute-mask lookup.
WfReadPackedMask:
 tay
 txa
 pha
 tya
 pha
 lsr
 lsr
 tax
 lda WfPackedNativeMask,x
 tax
 pla
 and #3
 tay
 txa
 cpy #0
 beq MaskReady
MaskShift:
 lsr
 lsr
 dey
 bne MaskShift
MaskReady:
 and #3
 tay
 lda WfMaskValues,y
 sta WfP1Temp
 pla
 tax
 lda WfP1Temp
 rts
; This is reached only inside the already authenticated C2 LateCore path.
WfMakeRoleColors:
 ldx WfOwnerCookie+2
 lda WfRoleColor1,x
 sta WfP1Packet+3
 lda WfRoleColor2,x
 sta WfP1Packet+4
 lda #15
 sta WfP1Packet+5
 rts
; Retire/invalid paths must not trust a private cookie. Match all six source
; palettes instead. The command's $3f15/length3/final$0f checks remain native.
WfMatchRoleColors:
 ldy #5
MatchRole:
 lda VRAM_Buffer1+3,x
 cmp WfRoleColor1,y
 bne NextRole
 lda VRAM_Buffer1+4,x
 cmp WfRoleColor2,y
 beq Matched
NextRole:
 dey
 bpl MatchRole
 clc
 rts
Matched:
 sec
 rts
WfRoleColor1:.byte ROLE_FIRST
WfRoleColor2:.byte ROLE_SECOND
WfRolePaletteEnd:

.segment "EARLY"
 jsr WfReadPackedMask
 nop
.segment "OWN"
 jmp WfMakeRoleColors
.segment "CANCEL"
 jsr WfMatchRoleColors
 bcc CancelNext
