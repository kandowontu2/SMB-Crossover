.setcpu "6502"

Selected = $6002
FarA = $016a
FarTarget = $016c
FarCall = $015a
VramName = $04ba
NativeStatusPacket = $b1df

.segment "GATE"
.export GfStatusGate
GfStatusGate:
    sta FarA
    lda Selected
    eor #42
    beq Own
    jmp NativeStatusPacket
Own:
    jmp GfStatusPacket
    .assert *-GfStatusGate=16,error,"Native UpdateNumber tail"

.segment "PACKET"
; Native ProtoPortrait used to execute the NOPs before reaching the
; neighboring RTS. It may return at the first byte of that padding.
    rts
.export GfStatusPacket
GfStatusPacket:
    sta FarTarget             ; A is exactly zero from the owner comparison.
    lda #>GfStatusText
    sta FarTarget+1
    lda #$a4                  ; Physical PRG36 mapped into the A window.
    jmp FarCall
    .assert <GfStatusText=0,lderror,"Implicit packet low byte"

.segment "TEXT"
.export GfStatusText
GfStatusText:
    php
    cmp #0                    ; Only the seven-cell top status name.
    bne Done
    txa
    pha
    ldx #6
Loop:
    lda Name,x
    sta VramName,x
    dex
    bpl Loop
    pla
    tax
    lda #0
Done:
    plp
    rts
Name:
    .byte $10,$0e,$1d,$1c,$1e,$24,$24 ; GETSU
