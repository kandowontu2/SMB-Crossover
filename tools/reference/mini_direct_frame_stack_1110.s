; Retain the authenticated Mini service contract and both map sequences.
; X and Y now remain live through the header walk and result restoration.
.setcpu "6502"
.segment "DIRECT"

MapC = $80c2
CurrentBankC = $7da1
FarTarget = $016c
NextBank = $0162
ReturnA = $0179

MiniDirectWorker:
    lda CurrentBankC
    pha
    php                         ; FarCall reloads A and N/Z from SafeCallA.
    lda FarTarget
    sec
    sbc #$20
    sta FarTarget
    lda #$a0
    sta FarTarget+1
    lda $0f
    cmp #8
    bne @cold
    lda #2
    jsr MapC
    lda $c300
    cmp #2
    bne @cold
@header:
    lda $dfe0
    cmp #$a7
    bne @cold
    lda $dfe1
    cmp #41
    bne @cold
    lda CurrentBankC
    eor #1                      ; C2 state to C3 code, then back to C2.
    jsr MapC
    lsr a
    bcs @header                 ; The mapped value was 3 on the first pass.
    lda #3
    bne @call
@cold:
    lda FarTarget
    clc
    adc #$8c
    sta FarTarget
    lda #$b0
    sta FarTarget+1
    lda #$c1
@call:
    sta NextBank
    plp
    jsr $015d
    pla
    jsr MapC
    lda ReturnA                 ; Match the inner FarCall return's A/N/Z.
    rts

MiniDirectWorkerEnd:
.res 128-(*-MiniDirectWorker),$ea
.export MiniDirectWorker,MiniDirectWorkerEnd
