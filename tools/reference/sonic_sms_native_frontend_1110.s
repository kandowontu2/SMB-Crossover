; Uses only deduplicated hint literals and the original name farcall packet.
.setcpu "6502"
.export SonicNameGate,SonicNamePacket,SonicNativeColors
.segment "NAME_GATE"
.org $ac7d
SonicNameGate:
    php
    lda $6002
    bne Original
    lda $730a
    cmp #10
    bne Original
    lda #0
    sta $016a
    plp
    lda #<SONIC_NAME_ENTRY    ; source-funded shared direct VRAM writer in A97
    ldx #>SONIC_NAME_ENTRY
    ldy #$e1                 ; physical97; no borrowed C window
    bne Publish
Original:
    plp
    lda #$0e                 ; unchanged GiantMenuName $BF:A80E
    ldx #$a8
    ldy #$bf
Publish:
    jmp SonicNamePacket
.segment "NAME_PACKET"
.org $acc0
    sta $016a                ; same public incoming-A publication
    jmp SonicNameGate
SonicNamePacket:
    sta $016c
    stx $016d
    sty $0162
    jmp $015d                ; exact FarCallCommon after NextBank store
.segment "COLORS"
.org $baa4
SonicNativeColors:
    sta $016a
    lda #$3d
    sta $016c
    lda #$a0
    sta $016d
    lda #$ce
    jsr $015a                ; genuine X5GetPlayerColors, all native lifecycle
    php
    pha
    lda $6002
    bne Done
    txa
    pha
    tya
    pha
    lda $730a
    ldy #0
    cmp #5
    beq Copy
    ldy #3
    cmp #6
    beq Copy
    ldy #6
    cmp #10
    bne PopRegisters
Copy:
    ldx $04ae
    lda #2
    sta $03
Loop:
    lda Palette,y
    sta $04ac,x              ; last native P0 packet's opaque entries
    inx
    iny
    dec $03
    bpl Loop
PopRegisters:
    pla
    tay
    pla
    tax
Done:
    pla
    plp
    rts
Palette:
    .byte $16,$30,$27         ; existing Toad
    .byte $16,$30,$27         ; existing Peach
    .byte $16,$12,$30         ; Sonic: red, blue, white
