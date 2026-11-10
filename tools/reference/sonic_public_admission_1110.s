; Explicit raw37..43 public envelope and fail-closed Sonic native getters.
; Only source-qualified current selector/auth/demo leases are used.
.setcpu "6502"
.segment "SELECTOR"
PrFamily:
 lda $016d
 cmp #$aa
 beq PrSh
 lda $6002
 sec
 sbc #37
 cmp #7
 bcc PrOdd
 lda $016c
 jmp $b031
PrOdd:
 cmp #4
 beq $a738
 jsr $aee2
 bcc LocalNo
 lda $016d
 cmp #$b0
 bne LocalNo
 lda $016c
 sec
 sbc #$8c
 bcc LocalNo
 cmp #114
 bcs LocalNo
 sta $016c
 lda $6002
 cmp #38
 beq PrPrince
 bcc Mini
 cmp #43
 beq Sonic
 lda #$a0
 bne Publish
Mini:
 lda #$a5
 bne Publish
Sonic:
 lda #$d1
Publish:
 jmp $ab12
LocalNo:
 jmp $ab4f
PrSh:
 ; Full ShCheckCode still rejects every non36 owner before header access.
 lda $016c
 sec
 sbc #$88
 bcc LocalNo
 cmp #111
 bcs LocalNo
 sta $016c
 jsr $a800
 bcc LocalNo
 lda #$a0
 jmp $ab12
PrPrince:
 lda $016c
 sta $0179
 lda #$1e
 sta $016c
 lda #$df
 jmp $ab12
RejectCall:
 jsr $015a
 jmp $ab58
.segment "SH_AUTH"
 ; Both actual importing frames already save AXYP and consume only C.
 lda $6002
 cmp #36
 bne ShNo
 ldx #7
 jmp $aeed
ShNo:
 clc
 rts
RejectHigh:
 lda #$bc
 sta $016d
 lda #$89
 bne RejectCall
.segment "REJECT"
 lda #$54
 sta $016c
 jmp RejectHigh
 nop
.segment "NATIVE_REJECT"
 ; Standard nested FarCall has five bytes below the saved Co frame.
 ; This ROM helper is safe even when either private header is corrupt.
 tsx
 lda $010f,x
 and #$fe
 sta $010f,x
 lda $6002
 cmp #43
 bne RejectDone
 lda #0
 sta $010d,x
 sta $010e,x
 lda $0108,x
 cmp #$f5
 bne RejectDone
 inc $010c,x
RejectDone:
 rts
