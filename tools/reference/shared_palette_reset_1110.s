.setcpu "6502"
.segment "WORKER"
.export PaletteResetDispatch, PaletteResetEnd

PaletteResetDispatch:
    ; The sole resident caller stores the zero StarInvincibleTimer in
    ; SafecallA before entering the farcall. No route changes that value.
    lda $6002
    eor #$18
    beq Dragon
    eor #$1a
    beq Rogue
    eor #$1b
    beq Smb2
Native:
    lda #$4c
    sta $016c
    lda #$a5
    sta $016d
    lda #$81
    bne Transfer
Dragon:
    lda #$4f
    sta $016c
    lda #$bf
    sta $016d
    lda #$d6
    bne Transfer
Rogue:
    lda $5fee
    eor #1
    bne Native
    lda #$d3
    sta $016c
    lda #$bc
    sta $016d
    lda #$f9
    bne Transfer
Smb2:
    ; Raw 25 still checks its ready, save ownership and pause gates.
    lda #$21
    sta $016c
    lda #$aa
    sta $016d
    lda #$bf
Transfer:
    sta $0162
    pla
    pla
    jmp $0161
PaletteResetEnd:
