.setcpu "6502"

; Called in the linked test at native85:B087 in place of CheckCodeHeader.
; The real ROM location for this trial body is still unassigned.
.segment "TRIAL"
ConstantService:
    jsr $b8f0
    bcc Return
    cpx #$28
    bne Return
    tsx
    ; Live nested FarCall frame: owner bank, original return PC, service
    ; offset, five SMC bytes, original C bank, then Y, X, A and P.
    lda $0106,x
    cmp #$c1
    bne OtherService
    lda $0107,x
    cmp #$3c
    bne OtherService
    lda $0108,x
    cmp #$a7
    bne OtherService
    lda $0109,x
    cmp #$1b
    beq ConstantResult
    cmp #$66
    beq ConstantResult
    cmp #$24
    beq Adder
    cmp #$27
    bne OtherService
    lda #1
    bne WriteY
Adder:
    lda #2
WriteY:
    sta $0110,x
ConstantResult:
    ; FarCall reloads the original A after the service. Copy its N/Z,
    ; keep the other original status bits and set the service's carry.
    ; The shortcut consumes the old service-offset byte.
    lda $0112,x
    php
    pla
    and #$82
    sta $0109,x
    lda $0113,x
    and #$7d
    ora #1
    ora $0109,x
    sta $0113,x
    ; Resume through the real TXS at AB4B with the service offset already
    ; consumed. The ordinary epilogue restores the SMC bytes and original C.
    lda #$4a
    sta $0107,x
    lda #$ab
    sta $0108,x
    txa
    clc
    adc #9
    tax
    sec
Return:
    rts
OtherService:
    ldx #$28
    sec
    rts

; An alternative interception point is the four public service entries.
; Test this separately from the late return above. Keep the normal full
; dispatcher as the fallback and reuse the existing epoch/header check.
.segment "EARLY_TRIAL"
FastEntry:
    php
    pha
    lda $6002
    cmp #40
    bne Legacy
    txa
    pha
    jsr FastAuthenticate
    pla
    tax
    bcc Legacy
    lda $016c
    cmp #$b0
    beq AnswerTwo
    cmp #$b3
    bne FastFinish
    ldy #1
    bne FastFinish
AnswerTwo:
    ldy #2
FastFinish:
    pla
    plp
    ora #0
    sec
FastReturn:
    rts

Legacy:
    lda $016c
    cmp #$b0
    beq UsualBox
    cmp #$b3
    beq UsualBox
    pla
    plp
    jmp $af9d
UsualBox:
    pla
    plp
    jmp $a7e4

FastAuthenticate:
    lda $0162
    pha
    lda $016c
    pha
    lda $016d
    pha
    lda $0179
    pha
    lda #$dc
    sta $016c
    lda #$a8
    sta $016d
    lda #$d5
    jsr $015a
    pla
    sta $0179
    pla
    sta $016d
    pla
    sta $016c
    pla
    sta $0162
    rts
