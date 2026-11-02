; Private lossless cold decoder.16 literal dictionary bytes, then LSB-first
; tokens:0,literal-kind,(4-bit index or8-bit raw);1,12-bit distance+len4.
; Same exact3..18-byte overlapping LZ backreferences as the qualified codec.
.setcpu "6502"
.segment "DECODER"
.export PpLdDecode,PpLdLoad,PpLdStore,PpLdRemain,PpLdEnd
PpLdDecode:
 ldx #0
Dictionary:
 jsr ReadByte
 sta Dict,x
 inx
 cpx #16
 bne Dictionary
 lda #0
 sta BitsLeft
Loop:
 lda PpLdRemain
 ora PpLdRemain+1
 beq Done
 jsr ReadBit
 bcs Match
 jsr ReadBit
 bcs Indexed
 ldx #8
 jsr ReadBits
 jmp Literal
Indexed:
 ldx #4
 jsr ReadBits
 lsr
 lsr
 lsr
 lsr
 tax
 lda Dict,x
Literal:
 jsr WriteByte
 jmp Loop
Match:
 ldx #8
 jsr ReadBits
 sta OffsetLo
 ldx #8
 jsr ReadBits
 pha
 and #15
 clc
 adc #3
 sta MatchLeft
 pla
 lsr
 lsr
 lsr
 lsr
 sta OffsetHi
 lda PpLdStore+1
 sec
 sbc OffsetLo
 sta Back+1
 lda PpLdStore+2
 sbc OffsetHi
 sta Back+2
Copy:
Back:lda $ffff
 inc Back+1
 bne :+
 inc Back+2
:
 jsr WriteByte
 dec MatchLeft
 bne Copy
 jmp Loop
Done:rts
ReadBits:
 jsr ReadBit
 ror Value
 dex
 bne ReadBits
 lda Value
 rts
ReadBit:
 lda BitsLeft
 bne :+
 jsr ReadByte
 sta Flags
 lda #8
 sta BitsLeft
:
 dec BitsLeft
 lsr Flags
 rts
ReadByte:
PpLdLoad:lda $ffff
 inc PpLdLoad+1
 bne ReadDone
 inc PpLdLoad+2
 pha
 lda PpLdLoad+2
 cmp #$dc
 bne :+
 lda #0
 sta PpLdLoad+1
 lda #$c2
 sta PpLdLoad+2
:
 pla
ReadDone:rts
WriteByte:
PpLdStore:sta $ffff
 inc PpLdStore+1
 bne :+
 inc PpLdStore+2
:
 lda PpLdRemain
 bne :+
 dec PpLdRemain+1
:
 dec PpLdRemain
 rts
BitsLeft:.byte 0
Flags:.byte 0
Value:.byte 0
OffsetLo:.byte 0
OffsetHi:.byte 0
MatchLeft:.byte 0
PpLdRemain:.word 0
Dict:.res 16
PpLdEnd:
