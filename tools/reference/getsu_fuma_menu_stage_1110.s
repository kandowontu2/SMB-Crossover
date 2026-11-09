.setcpu "6502"

FarA = $016a
FarTarget = $016c
FarCall = $015a
Sprite = $0200
Cursor = $04ae
Buffer = $04af

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
.export GfMenuPreview, GfMenuDraw, GfMenuColors, GfMenuName, GfMenuNameTail
GfMenuPreview:
    php
    pha
    lda $7309
    cmp #5
    bne Foreign
    lda $6002
    cmp #5
    bne Foreign
    lda $5fe7
    cmp #4
    bne Foreign
    lda $7307
    cmp #2
    bne Foreign
    lda $0139
    cmp #$ff
    bne Foreign
    pla
    plp
    jmp DrawPortrait
Foreign:
    pla
    plp
    Far $b979, $cc, jsr
    Far $aae7, $c2, jmp

.segment "DRAW"
GfMenuDraw:
DrawPortrait:
    ldx #0
    lda #$f8
Hide:
    sta Sprite,x
    inx
    inx
    inx
    inx
    bne Hide
    ; Exact effects of X5SetPhysicalChr for window0 and physical990.
    lda #<990
    sta $0147
    lda #$83
    sta $73e0
    lda #1
    sta $73ee
    sta $0146
    ldx #19
CopyOam:
    lda PortraitOam,x
    sta Sprite,x
    dex
    bpl CopyOam
    lda #20
    sta $06de
    jmp QueueColors

; The original writer just queued " SIMON BELMONT  ". Its outer space
; cells already match the new name. Replace indices 1..13 in that record.
RewriteName:
    ldx Cursor
    ldy #12
CopyName:
    dex
    lda NameCells,y
    sta Buffer-2,x
    dey
    bpl CopyName
    rts
NameCells:
    .byte $24,$24,$10,$0e,$1d,$1c,$1e,$24,$0f,$1e,$16,$0a,$24

.segment "COLORS"
GfMenuColors:
QueueColors:
    ldy Cursor
    cpy #78
    bcs Done
    ldx #6
CopyColors:
    lda PaletteReverse-1,x
    sta Buffer,y
    iny
    dex
    bne CopyColors
    sty Cursor
    txa
    sta Buffer,y
Done:
    rts

.segment "NAME"
GfMenuName:
    jsr NativeName
    php
    pha
    lda $6002
    cmp #5
    bne NameForeign
    lda $5fe7
    cmp #4
    bne NameForeign
    pla
    plp
    jmp RewriteName
NameForeign:
    pla
    plp
    rts

.segment "NAME_TAIL"
GfMenuNameTail:
NativeName:
    ; The original ACC0 farcall already published FarA. None of the
    ; extra dispatch instructions clobber that operand before this tail.
    lda #<$b720
    sta FarTarget
    lda #>$b720
    sta FarTarget+1
    lda #$cf
    jmp FarCall

; The bounded linker appends the exact portrait and reverse palette data
; to COLORS before linking NAME immediately after it in the same source span.
