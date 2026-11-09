.setcpu "6502"
.export GiantLateCheck, GiantMapMaa, GiantMaaTailMux, GiantTailFast, GiantTailFinish, GiantReturnDraw

; MaaOwner returns MarioVariant XOR 2 for raw Mario. The source DrawAll
; enters this nonrotating tail only for the native raw0 family and Luigi.
; EOR leaves the original carry and overflow intact for the stock return.
.segment "CHECK"
.org $bff7
GiantLateCheck:
    eor #$0b
    beq $bf85
    lda #$f8
    rts
.reloc

.segment "MAP"
GiantMapMaa:
    ldy CurrentBankC
    jmp $85c2                  ; common native bank-C publication

.segment "MAA_MUX"
GiantMaaTailMux:
    lda MarioVariant
    eor #2
    bne Giant
    lda #$c4                   ; original MaaDrawNeck A, N/Z and C/V
    jmp $dc0b
Giant:
    lda #$da
    sta $0145
    sta $5115
    jmp GiantTailFast          ; execution here is in the stable C window

.segment "TAIL_FAST"
GiantTailFast:
    tya
    pha                        ; exact incoming C window from GiantMapMaa
    lda M0                     ; original OAMClear entry low byte
    sec
    sbc #$2c
    ldx #0
Index:
    cmp #3
    bcc Ready
    sbc #3
    inx
    inx
    inx
    inx
    bne Index
Ready:
    jmp GiantTailFinish

.segment "TAIL_FINISH"
GiantTailFinish:
    lda #<GiantDrawOwner
    sta $016c
    lda #>GiantDrawOwner
    sta $016d
    lda #$d4
    jsr $015a
    pla
    sta CurrentBankC
    sta $5116
    ; The native fixed mapper return performs RTS. Continue at the stock
    ; F8 return in physical4 only after that bank is actually visible.
    lda #$bf
    pha
    lda #$fa
    pha
    lda #$84
    jmp GiantReturnDraw

.segment "RETURN"
GiantReturnDraw:
    sta $0145                  ; publish from fixed code, even across FF NMI
    jmp $eb3e                  ; native STA $5115 / RTS
