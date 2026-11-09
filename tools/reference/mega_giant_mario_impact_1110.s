.setcpu "6502"

.export GiantContact, GiantCrushAsBrick, GiantReadBE, GiantDefeat, GiantBowserDefeat

SelectedCharacter = $6002
MarioVariant = $730a
Enemy_Flag = $10
Enemy_ID = $17
R1 = $04
R2 = $05
R6 = $09
FarNextBank = $0162
FarTarget = $016c
FarMappedEntry = $0161

.segment "CONTACT"
.org $be44
; EColl has already confirmed a native overlap in active play and routed
; power-ups away. Native platform/flag actors have their own collision path.
GiantContact:
    php
    lda SelectedCharacter
    bne StockContact
    lda MarioVariant
    cmp #9
    bne StockContact
    plp
    jsr GiantDefeat
    sec
    rts
StockContact:
    lda #$96
    sta FarTarget
    lda #$af
    sta FarTarget+1
    lda #$ce
    sta FarNextBank
    plp
    pla
    pla
    jmp FarMappedEntry          ; reload original A and use the original frame

GiantDefeat:
    cpy #$2d
    beq $be00
    cpy #$0d
    bne $be3a
    ; Native retirement also clears the renderer's separate metasprite cell.
    ; Keep the donor's defeated-plant identity for the contact result.
    jsr $8d2f
    sty Enemy_ID,x
    lda #2
    jmp $9b1f                  ; native points and smack
.reloc

.segment "BOWSER"
GiantBowserDefeat:
    lda Enemy_Flag,x
    bpl Front
    and #$7f                   ; native rear flag encodes the front slot
    tax
Front:
    stx R1
    jmp $9ab8                  ; native terminal path, after the fireball HP gate

.segment "BLOCK"
; GiantSweep has already classified the real source material and claimed
; its native block slot. Present it to the shatter path as an ordinary brick.
GiantCrushAsBrick:
    ldy R2
    lda #$51
    sta (R6),y
    jmp $9ef5

.segment "AUDIO_VIEW"
; Giant's existing canonical bank90 view. Add one immutable Rogue source
; row without changing any original source read, including the four literal
; bytes BE40..BE43 that separate the two longer reclaimed zero ranges.
    php
    lda $e9
    cmp #$b0
    beq ZeroB0
    cmp #$b1
    beq ZeroB1
    cmp #$b7
    beq ZeroB7
    cmp #$b8
    beq ZeroB8
    cmp #$bc
    beq ZeroBC
    cmp #$be
    bne Original
    jmp GiantReadBE
ZeroBC:
    lda #$3f
    bne CheckAfter
ZeroB0:
    lda #$9d
    bne CheckAfter
ZeroB7:
    lda #$04
CheckAfter:
    cmp $e8
    bcs Original
ReturnZero:
    plp
    lda #0
    rts
ZeroB1:
    lda #$7f
    bne CheckBefore
ZeroB8:
    lda #$8f
CheckBefore:
    cmp $e8
    bcs ReturnZero
Original:
    plp
    lda ($e8),y
    rts

.segment "BE_READ"
GiantReadBE:
    lda $e8
    lsr
    lsr
    cmp #$04
    bcc BEZero
    cmp #$08
    bcc BELiteral
    cmp #$10
    beq BELiteral
    cmp #$20
    bcc BEZero
BELiteral:
    jmp Original
BEZero:
    jmp ReturnZero
NativeDefeat:
    .assert NativeDefeat = $be3a,lderror,"Native defeat branch target"
    jmp $9af5
