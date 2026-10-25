; Replace only shared entry8C75..8C88, then rejoin original STA length/CPX2.
; Base1's repeated addition equals A=count+1; that final ADC also reproduces
; original C/V for every count, including overflow. N/Z are overwritten by
; the original CPX2. Preserve the entry Z test, including its zero branch.
.pushseg
.segment "TMNT_NATIVE_AUDIO_WRITERS"
; Native driver uses offsets00..AD. B0 belonged to the removed ZP-copy slab
; and is private to this driver while its history page is active.
TnDurationY=TnAudioRam+$b0
.export TnDurationY
.proc TnNativeDuration
 sta TnAudioZp+2
 beq Zero
 lda TnAudioRam+$10,x
 cmp #1
 bne NotOne
 lda TnAudioZp+2
 clc
 adc #1
 pha
 lda #0
 sta TnAudioZp+2
 pla
 rts
NotOne:
 cmp #7
 bne Repeat
 sty TnDurationY
 ldy TnAudioZp+2
 lda #0
 sta TnAudioZp+2
 lda TnSevenProduct,y
 ldy TnDurationY
 clc
 adc #7
 rts
Repeat:
 clc
 adc TnAudioRam+$10,x
 dec TnAudioZp+2
 bne Repeat
 rts
Zero:
 lda TnAudioRam+$10,x
 rts
.endproc
.export TnNativeDuration
TnSevenProduct:
.repeat 256,I
 .byte (I*7)&$ff
.endrepeat
.popseg
