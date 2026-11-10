; Bits5/6 are prototype selection. Every older boolean consumer receives
; the original byte with only those two newly declared bits removed.
.setcpu "6502"
.segment "MENU_MASK"
.org $b12b
PrototypeContinueValue:
 lda $730b
 and #$9f
 rts
.assert *-PrototypeContinueValue=6,error,"Exact six-byte retired menu tail"

.segment "DK_RESOLVE"
.org $bd28
; Exact61-byte original public envelope. CmHostResolveCharacter ignores
; incoming A: PHP, LDX menu index, native NrMenuCharacter computes its result
; from X. Its unused incoming-A marshal is the three-byte source funding.
DkPrototypeResolve:
 php
 lda $6002
 pha
 lda #$76
 sta $016c
 lda #$be
 sta $016d
 lda #$d1
 jsr $015a
 pla
 cmp #28
 bne NewOwner
 lda $6002
 cmp #28
 bne Done
 lda $730b
 and #$9f
 beq Construct
 jsr $ba5d
 jmp Done
NewOwner:
 lda $6002
 cmp #28
 bne Done
Construct:
 jsr $b9fd
Done:
 plp
 lda $6002
 rts
 .byte $ea
.assert *-DkPrototypeResolve=61,error,"Original DK resolver envelope"

.segment "AR_SELECT"
.org $d1e3
ArPrototypeSelect:
 php
 pha
 lda $6002
 cmp #32
 beq ArOwn
 pla
 plp
 rts
ArOwn:
 pla
 plp
 cmp #32
 bne $d216
 lda $730b
 and #$9f
 beq $d216
 jsr $d254
 lda #0
 sta $5c92
 jmp $d28b
 .byte $ea
; Both original branches now reach the existing D216 constructor directly.
; Retiring the three-byte D205 JMP funds AND9F plus this one trailing NOP.
.assert *-ArPrototypeSelect=37,error,"Original ArHostSelect envelope"

.segment "HU_RESOLVE"
.org $ba97
HuPrototypePacket:
 cmp #28
 bne HuConstruct
 lda $730b
 and #$9f
 beq HuConstruct
 sta $016a
 lda #$5d
 bne HuPacket
HuConstruct:
 sta $016a
 lda #$fd
HuPacket:
 php
 sta $016c
 asl
 bcc HuHigh
 lda #$b9
HuHigh:
 sta $016d
 plp
 lda #$a4
 jsr $015a
; Common farcall packet replaces two copies. 5D<<1=BA (carry0),
; FD<<1=FA (carry1 -> B9). PHP/PLP preserves the original C/V bits.
 .res 48-(*-HuPrototypePacket),$ea
.assert *-HuPrototypePacket=48,error,"Original HuResolve suffix envelope"
