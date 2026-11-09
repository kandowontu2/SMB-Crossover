.setcpu "6502"

FarA = $016a
FarTarget = $016c
FarCall = $015a

.macro Far target, bank, operation
    sta FarA
    lda #<target
    sta FarTarget
    lda #>target
    sta FarTarget+1
    lda #bank
    operation FarCall
.endmacro

.segment "GATE"
    php
    pha
    lda $7309                  ; CrossoverMenuIndex
    cmp #5
    bne Foreign
    lda $6002                  ; selected identity stays native menu raw5
    cmp #5
    bne Foreign
    lda $5fe7                  ; Cv3Variant after the separate Select cycle
    cmp #4
    bne Foreign
    lda $7307                  ; CrossoverMenuState
    cmp #2
    bne Foreign
    lda $0139                  ; NmiDisable, GameLoop publishes FF first
    cmp #$ff
    bne Foreign
    pla
    plp
    jmp DrawPortrait
Foreign:
    pla
    plp
    Far $b979, $cc, jsr        ; actual current FmPending, as at $aad5
    Far $aae7, $c2, jmp        ; original DrawSelectionPreview continuation

.segment "DRAW"
DrawPortrait:
    Far $a325, $84, jsr        ; MoveAllSpritesOffscreen
    lda #<990
    ldx #>990
    ldy #0
    Far $a275, $be, jsr        ; X5SetPhysicalChr, one typed sprite window
    ldx #19
CopyOam:
    lda PortraitOam,x
    sta $0200,x
    dex
    bpl CopyOam
    lda #20
    sta $06de                  ; CurrentOAMOffset
    jmp QueueColors

.segment "COLORS"
QueueColors:
    ldy $04ae                  ; VRAM_Buffer1_Offset, six bytes + terminator
    cpy #78
    bcs Done
    ldx #0
CopyCommand:
    lda PaletteCommand,x
    sta $04af,y
    iny
    inx
    cpx #6
    bne CopyCommand
    sty $04ae
    lda #0
    sta $04af,y
Done:
    rts

; The bounded recipe links donor-derived PortraitOam and PaletteCommand here.
