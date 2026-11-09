.setcpu "6502"

Selected = $6002
SavedA = $016a
TargetLo = $016c
TargetHi = $016d
NextBank = $0162
FarCall = $015a
NativeBox = $9f4e
MiniBoxService = $b0bc

.segment "BOX93"
BoxDispatch:
    php
    pha
    tya
    pha
    ldy #0
    lda Selected
    cmp #19
    beq @typed
    iny
    cmp #41
    beq @typed
    iny
    jsr $a00c                 ; Original Little Mac ownership check.
    bcs @mac
@typed:
    lda @lo,y
    sta TargetLo
    lda @hi,y
    sta TargetHi
    lda @bank,y
    sta NextBank
    pla
    tay
    pla
    sta SavedA
    plp
    jsr FarCall+3
    jmp @foot
@lo:   .byte $1b, <MiniBoxStage, $c8
@hi:   .byte $ac, >MiniBoxStage, $ad
@bank: .byte $d9, $d6, $da
    .assert *=$a743, lderror, "Little Mac body entry"
@mac:
    pla
    tay
    pla
    plp
    jsr NativeBox
    jsr $ab4a
    lda $0571
    tay
    clc
    adc $ab5d,x
    sta $0658
    tya
    clc
    adc $ab63,x
    sta $065a
    lda $057c
    tay
    clc
    adc $ab69,x
    sta $0659
    tya
    clc
    adc #32
    sta $065b
    ldx #0
    ldy #0
    .assert *=$a776, lderror, "Existing Easy foot call"
@foot:
    sta SavedA
    lda #0
    sta TargetLo
    lda #$a0
    sta TargetHi
    lda #$d6
    jmp FarCall

.segment "STAGE86"
MiniBoxStage:
    ; Enter only from the raw 41 table slot with the original saved A.
    lda #<MiniBoxService
    sta TargetLo
    lda #>MiniBoxService
    sta TargetHi
    jmp MiniBoxCall
    .res 15-(*-MiniBoxStage), $ea

.segment "CALL86"
MiniBoxCall:
    ; Keep the incumbent service's complete epoch and cookie admission.
    lda #$c1
    jsr FarCall
    bcs @done
    jmp NativeBox             ; The original row 16 rejection continuation.
@done:
    rts
    .res 15-(*-MiniBoxCall), $ea
