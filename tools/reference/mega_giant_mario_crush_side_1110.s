.setcpu "6502"
.export GiantReadRogue33, GiantSideNative

SelectedCharacter = $6002
MarioVariant = $730a
OperMode = $0771
GameEngineSubroutine = $0f

.segment "GIANT_SIDE"

; C97 has already mapped PRG33 and set Y=0. Restore the original
; authored byte and full incoming carry/overflow across the relocated read.
GiantReadRogue33:
    php
    ldy $e8
    cpy #$24
    bcs CanonicalZero
    lda RoguePage6,y
    bcc Publish
CanonicalZero:
    lda #0
Publish:
    ldy #0
    plp
    jmp $c438

RoguePage6:
    .byte $56,$94,$68,$56,$5e,$56,$98,$50,$56,$5e,$56,$94
    .byte $68,$56,$5e,$56,$94,$50,$56,$5e,$56,$98,$68,$56
    .byte $5e,$56,$98,$6e,$72,$6e,$6a,$98,$6e,$6a,$68,$64
    .assert *-RoguePage6 = $24,error,"All nonzero authored bytes"

; Reached only from the native side-query tail after all current guest
; routes. Floors, native head response and interactive structural tiles
; remain with the original owner. The Giant sweep still owns cell removal
; and its normal VRAM/debris admission, including pending $23.
GiantSideNative:
    php
    pha
    lda SelectedCharacter
    bne Stock
    lda MarioVariant
    cmp #9
    bne Stock
    lda OperMode
    cmp #1
    bne Stock
    lda GameEngineSubroutine
    cmp #8
    bne Stock
    pla
    plp
    jsr $958b
    beq Return
    php
    cmp #$23
    beq Pending
    cmp #$c2
    beq Keep
    cmp #$c3
    beq Keep
    cmp #$c5
    beq Keep
    cmp #$5f
    beq Keep
    cmp #$60
    beq Keep
    cmp #$6c
    beq Keep
    cmp #$1f
    beq Keep
    pha
    and #$c0
    asl
    rol
    rol
    tax
    pla
    cmp SolidLimits,x
    ldx #0                      ; the original side getter always returns X=0
    bcs Keep
Pending:
    plp
    lda #0
Return:
    rts
Keep:
    plp
    rts
Stock:
    pla
    plp
    jmp $958b
SolidLimits:
    .byte $24,$6d,$8a,$c6
