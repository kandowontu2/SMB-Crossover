; Runs only after the existing compact worker has verified the complete
; two-row stage at C2:D000..D7FF. The outer common cold caller holds SEI,
; forced blank, both invalid headers, and saved R0..R7. A3 is mapped.
; R5/R6 ($08/$09) must survive for its subsequent immutable-cookie commit.
.setcpu "6502"
.segment "DECODE"
Src = $03
Dst = $05
Back = $07
Bits = $c038
Flags = $c039
Distance = $c03a
Encoded = $c03b
Length = $c03c

DecodeJay:
 lda $08
 pha
 lda $09
 pha
 lda #<PackedData
 sta Src
 lda #>PackedData
 sta Src+1
 lda #0
 sta Bits
 sta Dst
 lda #$a0
 sta Dst+1
NextToken:
 lda Dst+1
 cmp #>DecodedEnd
 bne More
 lda Dst
 cmp #<DecodedEnd
 bne More
 jmp Complete
EarlyFailed:
 jmp Failed
More:
 lda Bits
 bne HaveFlags
 jsr ReadByte
 bcc EarlyFailed
 sta Flags
 lda #8
 sta Bits
HaveFlags:
 dec Bits
 lsr Flags
 bcs Match
 jsr ReadByte
 bcc EarlyFailed
 jsr WriteByte
 bcc EarlyFailed
 jmp NextToken

Match:
 jsr ReadByte
 bcc EarlyFailed
 sta Distance
 jsr ReadByte
 bcc EarlyFailed
 sta Encoded
 and #15
 clc
 adc #3
 sta Length
 lda Encoded
 and #$f0
 ora Distance
 beq EarlyFailed
 lda Encoded
 lsr A
 lsr A
 lsr A
 lsr A
 sta Encoded
 lda Dst
 sec
 sbc Distance
 sta Back
 lda Dst+1
 sbc Encoded
 cmp #$a0
 bcc EarlyFailed
 cmp #$c0
 bcs EarlyFailed
 sta Back+1
MatchByte:
 ldy #0
 lda (Back),y
 jsr WriteByte
 bcc EarlyFailed
 inc Back
 bne NextMatch
 inc Back+1
NextMatch:
 dec Length
 bne MatchByte
 jmp NextToken

Complete:
 lda Src
 cmp #<PackedEnd
 bne Failed
 lda Src+1
 cmp #>PackedEnd
 bne Failed
 sec
 bcs Return
Failed:
 clc
Return:
 pla
 sta $09
 pla
 sta $08
 rts

ReadByte:
 lda Src+1
 cmp #>PackedEnd
 bne ReadNext
 lda Src
 cmp #<PackedEnd
 beq ReadFail
ReadNext:
 ldy #0
 lda (Src),y
 inc Src
 bne ReadDone
 inc Src+1
ReadDone:
 sec
 rts
ReadFail:
 clc
 rts

WriteByte:
 pha
 lda Dst+1
 cmp #>DecodedEnd
 bne WriteNext
 lda Dst
 cmp #<DecodedEnd
 beq WriteFull
WriteNext:
 pla
 ldy #0
 sta (Dst),y
 cmp (Dst),y
 bne ReadFail
 inc Dst
 bne WriteDone
 inc Dst+1
WriteDone:
 sec
 rts
WriteFull:
 pla
 clc
 rts
PackedData:
