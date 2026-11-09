.setcpu "6502"

; Current c8 DrawAllMetasprites LegacyTailClear. The byte popped from the
; stack can be anything: (n >> 1) + (n >> 2) + bit1(n) + $2c <= $eb.
; The old ADC #0 therefore always publishes high $a3 and clears C/V.
; Keep C from the low addition and complete A/V in the fixed-bank prefix.
.segment "WORLD"
.export LegacyTailClear, WorldFirebarAdmission, LegacyWorldDraw
LegacyTailClear:
    pla
    lsr
    sta $0b
    lsr
    adc $0b
    adc #$2c
    sta $0b
    lda #$a3
    sta $0c
    jmp $85b2

LegacyWorldDraw:
    jmp $ba23
    nop

; The same four shuffled slot-zero callers still enter at $a261.
; Old fast set $04..07/$24..27 remains valid, and every ID below the
; native firebar minimum is safe. All other IDs use the original gate,
; including the separate small-lift renderer for $2b/$2c.
WorldFirebarAdmission:
    ldx #6
Scan:
    lda $16,x
    cmp #$1b
    bcc Next
    and #$dc
    eor #$04
    bne LegacyWorldDraw
Next:
    dex
    bne Scan
    jmp $bea4
    nop

.segment "FIXED"
    lda #$f8
    clv
    ; Fall through to the unmodified $85b5 legacy clear continuation.

; Current c8 RlOriginalFullShotBank scan. Keep the actual shared CHR bank
; publication and every active projectile type. Skip comparisons for an
; empty slot; the final comparison against CurrentCHRBank defines carry.
.segment "SHOT"
.org $bc9a
    beq $bcae
    cmp #3
    beq Blue
    cmp #6
    bne $bcae
    lda #$78
    bne Found
Blue:
    lda #$70
Found:
    clv
    ; Fall through to the original STA MmFireBank at $bcab.
