.setcpu "6502"
.segment "STEVE_PACKET_BOOT"

; The native worker authenticated this complete physical row at raw3 A000.
; Map raw1 at C000 and copy the cold code to its D800 alias before calling it.
StevePacketBoot:
    lda #1
    jsr $80c2
    lda #0
    sta $dfe0
    ldy #0
BootCopy:
    lda $a000,y
    sta $d800,y
    lda $a100,y
    sta $d900,y
    lda $a200,y
    sta $da00,y
    lda $a300,y
    sta $db00,y
    iny
    bne BootCopy
    lda #<StevePacketCold
    sta $016c
    lda #>StevePacketCold
    sta $016d
    lda #1
    jmp $015a

.segment "STEVE_PACKET_COLD"
Remaining = $05
RowIndex = $07
InputLow = $0a
StevePacketCold:
    tsx
    stx ColdStack
    ; Restore Jay's source rows and original decoder before mounting Steve.
    ldx #0
    stx ComparePass
DirectNext:
    stx DirectIndex
    lda DirectRows,x
    sta $03
    lda DirectRows+1,x
    sta $04
    lda DirectRows+2,x
    jsr SetC
    lda DirectRows+3,x
    sta RowIndex
    lda DirectRows+4,x
    sta InputLow
    lda DirectRows+5,x
    sta InputHigh
    lda DirectRows+6,x
    sta Remaining
    lda DirectRows+7,x
    sta Remaining+1
DirectPass:
    jsr MapInput
DirectByte:
    lda $2007
    ldy #0
    ldx ComparePass
    bne DirectCompare
    sta ($03),y
DirectCompare:
    cmp ($03),y
    bne ColdBad
    inc $03
    bne :+
    inc $04
:
    jsr DecreaseRemaining
    bne DirectByte
    ldx DirectIndex
    lda ComparePass
    bne DirectDone
    inc ComparePass
    jmp DirectNext
DirectDone:
    lda #0
    sta ComparePass
    txa
    clc
    adc #8
    tax
    cpx #40
    bne DirectNext
    lda #3
    jsr SetC
    lda #0
    ldy #64
:
    sta $d3bf,y
    dey
    bpl :-
    lda #2
    jsr SetC
    lda #$c0
    sta $016c
    lda #$a7
    sta $016d
    lda #3
    jsr $015a
    bcc ColdBad
    lda #0
    sta ComparePass
DecodePass:
    lda #0
    sta RowIndex
    sta BitsLeft
    sta BlockIndex
    sta RingStore+1
    lda #$a8
    sta RingStore+2
    lda #<PacketOffset
    sta InputLow
    lda #>PacketOffset
    sta InputHigh
    jsr MapInput
    ldx #0
Dictionary:
    jsr ReadByte
    sta Dict,x
    inx
    cpx #16
    bne Dictionary
    jsr NextBlock
DecodeToken:
    lda Remaining
    ora Remaining+1
    bne :+
    lda ComparePass
    bne ColdGood
    inc ComparePass
    jmp DecodePass
:
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
    lsr a
    lsr a
    lsr a
    lsr a
    tax
    lda Dict,x
Literal:
    jsr WriteByte
    jmp DecodeToken
Match:
    ldx #8
    jsr ReadBits
    sta OffsetLow
    ldx #8
    jsr ReadBits
    pha
    and #15
    clc
    adc #3
    sta MatchLeft
    pla
    lsr a
    lsr a
    lsr a
    lsr a
    sta OffsetHigh
    lda RingStore+1
    sec
    sbc OffsetLow
    sta Back+1
    lda RingStore+2
    sbc OffsetHigh
    and #15
    ora #$a0
    cmp #$a8
    bcs :+
    adc #$10
:
    sta Back+2
CopyMatch:
Back:
    lda $ffff
    jsr WriteByte
    inc Back+1
    bne :+
    inc Back+2
    lda Back+2
    cmp #$b8
    bne :+
    lda #$a8
    sta Back+2
:
    dec MatchLeft
    bne CopyMatch
    jmp DecodeToken
ColdBad:
    ldx ColdStack
    txs
    lda #1
    jsr SetC
    lda #0
    sta $dfe0
    clc
    bcc ColdReturn
ColdGood:
    lda #1
    jsr SetC
    ldy #15
CommitRaw1:
    lda ExpectedCookie,y
    sta $dfe0,y
    cmp $dfe0,y
    bne ColdBad
    dey
    bpl CommitRaw1
    sec
ColdReturn:
    lda #2
    jsr SetC
    rts
SetC:
    sta CurrentBankC
    sta $5116
    rts

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
    lda $2007
    pha
    inc InputLow
    bne ReadReturn
    inc InputHigh
    lda InputHigh
    cmp #4
    beq InputNextRow
.ifndef STEVE_RECOVERY_RELOCATED
    lda RowIndex
    cmp #8
    bne ReadReturn
    lda InputHigh
    cmp #2
    bne ReadReturn
    inc InputHigh                ; preserve physical CHR307 recovery cells
    bne InputRemap
.else
    bne ReadReturn
.endif
InputNextRow:
    inc RowIndex
    lda #0
    sta InputHigh
.ifdef STEVE_WAVE_ROW
    lda RowIndex
    cmp #9
    bne InputRemap
    lda #WaveArtBytes
    sta InputLow
.endif
InputRemap:
    jsr MapInput
ReadReturn:
    pla
    rts
MapInput:
    txa
    pha
    ldx RowIndex
    lda SourceHigh,x
    sta $5130
    lda SourceLow,x
    sta $5123
    lda #0
    sta $5130
    bit $2002
    lda InputHigh
    ora #$0c
    sta $2006
    lda InputLow
    sta $2006
    lda $2007
    pla
    tax
    rts
WriteByte:
    ldy #0
    ldx ComparePass
    bne CompareByte
    sta ($03),y
CompareByte:
    cmp ($03),y
    bne ColdBad
RingStore:
    sta $a800
    inc RingStore+1
    bne :+
    inc RingStore+2
    lda RingStore+2
    cmp #$b8
    bne :+
    lda #$a8
    sta RingStore+2
:
    inc $03
    bne :+
    inc $04
:
    jsr DecreaseRemaining
    bne WriteDone
    lda BlockIndex
    cmp #BlockTableSize
    beq WriteDone
NextBlock:
    ldx BlockIndex
    lda BlockTable,x
    sta $03
    lda BlockTable+1,x
    sta $04
    lda BlockTable+2,x
    jsr SetC
    lda BlockTable+3,x
    sta Remaining
    lda BlockTable+4,x
    sta Remaining+1
    txa
    clc
    adc #5
    sta BlockIndex
WriteDone:
    rts
DecreaseRemaining:
    lda Remaining
    bne :+
    dec Remaining+1
:
    dec Remaining
    lda Remaining
    ora Remaining+1
    rts

ColdStack: .byte 0
DirectIndex: .byte 0
ComparePass: .byte 0
InputHigh: .byte 0
BlockIndex: .byte 0
BitsLeft: .byte 0
Flags: .byte 0
Value: .byte 0
OffsetLow: .byte 0
OffsetHigh: .byte 0
MatchLeft: .byte 0
Dict: .res 16
DirectRows:
    ; target, raw bank, source-table index, PPU offset, length
    .word $c400
    .byte 3,SourceDirectBase
    .word 0,1024
    .word $c800
    .byte 3,SourceDirectBase+1
    .word 0,1024
    .word $cc00
    .byte 3,SourceDirectBase+2
    .word 0,1024
    .word $d400
    .byte 2,SourceDirectBase+4
    .word 0,1024
    .word $d000
    .byte 3,SourceDirectBase+5
    .word $40,959
SourceLow:
    .byte <371,<375,<379,<336,<338,<167,<304,<306,<307
.ifdef STEVE_WAVE_ROW
    .byte <STEVE_WAVE_ROW
.endif
    .byte <222,<232,<234,<331,<332,<218
SourceHigh:
    .byte >371,>375,>379,>336,>338,>167,>304,>306,>307
.ifdef STEVE_WAVE_ROW
    .byte >STEVE_WAVE_ROW
.endif
    .byte >222,>232,>234,>331,>332,>218
BlockTable:
    .byte BlockTableBytes
ExpectedCookie:
    .byte CookieBytes
StevePacketColdEnd:
