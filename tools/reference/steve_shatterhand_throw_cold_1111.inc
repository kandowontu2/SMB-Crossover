    ; CHR306 mirrors CHR220's punch tail. The original decoder has returned.
    lda #$32
    ldx #$d8
    jsr SteveLateRow
    bcc SteveLateFailed
