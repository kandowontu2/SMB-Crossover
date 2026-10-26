; MMC5-only native TMNT music. No persistent multiplier operand owner.
; AudioUpdate selects either char1 Proto or char19 TMNT inside one NMI; IRQ
; touches neither product register. Both users write their operands before reads.
; Preserve original E2/E4/E5, final-ADC V, D/I/X/Y, C=0 and final A/N/Z.
.proc TnFastProduct
 and #15
 beq Zero
 cmp #2
 bcc One
 sta $5205
 lda a:TnAudioRam+4,x
 sta $5206
 lda $5205
 sta z:TnAudioZp+4
 ; Reproduce the ORIGINAL last repeated-add ADC overflow, including wrap.
 sec
 sbc a:TnAudioRam+4,x
 clc
 adc a:TnAudioRam+4,x
 lda $5206
 sta z:TnAudioZp+5
 lda #$ff
 sta z:TnAudioZp+2
 lda z:TnAudioZp+4
 jmp $acd9                  ; Authentic four ASL/ROL pairs and final LDA/RTS.
One:
 lda a:TnAudioRam+4,x
 sta z:TnAudioZp+4
 lsr a
 lsr a
 lsr a
 lsr a
 sta z:TnAudioZp+5
 lda #$ff
 sta z:TnAudioZp+2
 clv                        ; Original last ADC is coefficient + zero.
 clc
 lda z:TnAudioZp+5
 rts
Zero:
 lda #0
 sta z:TnAudioZp+4
 sta z:TnAudioZp+5
 lda #$ff
 sta z:TnAudioZp+2
 clc                        ; Incoming V remains live for the zero case.
 lda #0
 rts
.endproc
.assert TnFastProduct=$a125,lderror,"Verified unused native writer tail"
.assert *<=$a200,lderror,"Retain original duration helper and all later PCs"
.export TnFastProduct
