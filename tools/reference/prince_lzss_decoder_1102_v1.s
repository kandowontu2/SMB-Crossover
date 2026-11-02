; Private cold-load cost fixture. No resident/shared bootstrap is modified.
; Caller supplies owned SMC source/destination and exact16-bit output count.
; Eight token flags, low bit first:0 literal;1 backref(distance12,len4+3).
.setcpu "6502"
.segment "DECODER"
.export PpLzDecode,PpLzLoad,PpLzStore,PpLzRemain,PpLzEnd
PpLzDecode:
 lda #0
 sta BitsLeft
Loop:
 lda PpLzRemain
 ora PpLzRemain+1
 beq Done
 lda BitsLeft
 bne FlagReady
 jsr ReadByte
 sta Flags
 lda #8
 sta BitsLeft
FlagReady:
 dec BitsLeft
 lsr Flags
 bcs Match
 jsr ReadByte
 jsr WriteByte
 jmp Loop
Match:
 jsr ReadByte
 sta OffsetLo
 jsr ReadByte
 sta Encoded
 and #15
 clc
 adc #3
 sta MatchLeft
 lda Encoded
 lsr
 lsr
 lsr
 lsr
 sta OffsetHi
 lda PpLzStore+1
 sec
 sbc OffsetLo
 sta Back+1
 lda PpLzStore+2
 sbc OffsetHi
 sta Back+2
Copy:
Back:lda $ffff
 inc Back+1
 bne BackReady
 inc Back+2
BackReady:
 jsr WriteByte
 dec MatchLeft
 bne Copy
 jmp Loop
Done:rts
ReadByte:
PpLzLoad:lda $ffff
 inc PpLzLoad+1
 bne ReadDone
 inc PpLzLoad+2
 ; Metadata's last306 encoded bytes stage temporarily in original-state
 ; C200..C332. A page-aligned fragment break prevents unread-input overlap
 ; without borrowing the ungranted DD32..DFD0 gap. Source state initializes
 ; only after this cold decoder and the common worker have returned.
 pha
 lda PpLzLoad+2
 cmp #$dc
 bne ReadStraight
 lda #0
 sta PpLzLoad+1
 lda #$c2
 sta PpLzLoad+2
ReadStraight:pla
ReadDone:rts
WriteByte:
PpLzStore:sta $ffff
 inc PpLzStore+1
 bne DestReady
 inc PpLzStore+2
DestReady:
 lda PpLzRemain
 bne LowNonzero
 dec PpLzRemain+1
LowNonzero:
 dec PpLzRemain
 rts
BitsLeft:.byte 0
Flags:.byte 0
OffsetLo:.byte 0
OffsetHi:.byte 0
Encoded:.byte 0
MatchLeft:.byte 0
PpLzRemain:.word 0
PpLzEnd:
