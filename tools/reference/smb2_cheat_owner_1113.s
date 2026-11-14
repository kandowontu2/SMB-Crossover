; Exact private grant smb2-cheat-owner-1113. No new RAM or stack writes.
; The real gate saved R0..R7 in reverse order. Zero-page indexed wrapping
; pops the same eight bytes into3..10 in the same order, saving two bytes.
.setcpu "6502"
.segment "OWNER_RESTORE"
OwnerRestore:
 ldx #$f8
OwnerPop:
 pla
 sta $0b,x
 inx
 bne OwnerPop
 pla
 tay
 pla
 tax
 pla
 plp
 lda GuestHurtKind
 beq OwnerNative
 ; Original injury tail, byte-for-byte and with the same live stack.
 sta SafeA
 lda #$c9
 sta TargetLo
 lda #$b7
 sta TargetHi
 lda #$8a
 jmp FarCallCommon
OwnerNative:
 ; The preceding LDA/BEQ proves A0/Z1/N0. EOR preserves C and V.
 lda SelectedCharacter
 eor #25
 beq OwnerSMB2
 lda #0
 sta SafeA
 jmp OwnerForeignTail
OwnerSMB2:
 lda #0
 jmp ExistingSMB2Tail
.segment "OWNER_FOREIGN"
OwnerForeignTail:
 ; Original81:A021 destination; do not use the recursive A14D policy.
 lda #$21
 sta TargetLo
 lda #$a0
 sta TargetHi
 lda #$81
 jmp FarCallCommon
