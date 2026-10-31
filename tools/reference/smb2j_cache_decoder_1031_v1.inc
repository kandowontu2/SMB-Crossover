; Actual6502 LZSS decoder. Caller supplies a buffered PPUDATA stream and maps
; its exclusive8KiB destination at A000. R0..R7 are imported host scratch,
; never literal00..07. This leaf does not publish a cookie or change mappings.
; Return C=1 only after exactly8192 verified stores; C=0 on invalid distance,
; output overrun or failed RAM readback. Wrapper/auth/forced-blank are separate.
.proc J2DecodeCache
 lda #0
 sta R0
 sta R5
 lda #$a0
 sta R1
 ldy #0
J2Next:
 lda R1
 cmp #$c0
 beq J2Complete
 lda R5
 bne J2FlagReady
 lda PPUDATA
 sta R4
 lda #8
 sta R5
J2FlagReady:
 dec R5
 lsr R4
 bcc J2Match
 lda PPUDATA
 jsr J2Put
 bcc J2Bad
 jmp J2Next
J2Match:
 lda PPUDATA
 tax
 lda PPUDATA
 tay
 txa
 eor #$ff
 clc
 adc R0
 sta R2
 tya
 and #$0f
 eor #$ff
 adc R1
 sta R3
 cmp #$a0
 bcc J2Bad
 tya
 lsr
 lsr
 lsr
 lsr
 clc
 adc #3
 sta R6
 lda #0
 sta R7
 lda R6
 cmp #18
 bne J2CopyReady
 lda PPUDATA
 clc
 adc #18
 sta R6
 lda #0
 adc #0
 sta R7
J2CopyReady:
 ldy #0
J2Copy:
 lda (R2),y
 jsr J2Put
 bcc J2Bad
 inc R2
 bne J2SourceAdvanced
 inc R3
J2SourceAdvanced:
 lda R6
 bne J2DecLength
 dec R7
J2DecLength:
 dec R6
 lda R6
 ora R7
 bne J2Copy
 jmp J2Next
J2Complete:
 sec
 rts
J2Bad:
 clc
 rts
J2Put:
 pha
 lda R1
 cmp #$c0
 bcs J2Overrun
 pla
 sta (R0),y
 cmp (R0),y
 bne J2Bad
 inc R0
 bne J2Stored
 inc R1
J2Stored:
 sec
 rts
J2Overrun:
 pla
 clc
 rts
.endproc
