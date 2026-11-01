; Preserve original stream pointers while reading relocated source data.
; Only the genuine driver's0..8 scratch is changed, then restored as by LDA.
; The outer native audio adapter must save those bytes for the host.
WfAudioRead4:
 php
 txa
 pha
 ldx #4
 bne WfAudioReadCommon
WfAudioRead7:
 php
 txa
 pha
 ldx #7
WfAudioReadCommon:
 lda $00,x
 pha
 lda $01,x
 pha
 tya
 clc
 adc $00,x
 sta $00,x
 lda $01,x
 adc #0
 sta $01,x
 cmp #$e8
 bcc WfAudioReadLow
 lda $00,x
 clc
 adc #.lobyte(WfAudioHighData-$e84e)
 sta $00,x
 lda $01,x
 adc #.hibyte(WfAudioHighData-$e84e)
 sta $01,x
 jmp WfAudioReadMapped
WfAudioReadLow:
 lda $00,x
 clc
 adc #.lobyte(WfAudioLowData-$8018)
 sta $00,x
 lda $01,x
 adc #.hibyte(WfAudioLowData-$8018)
 sta $01,x
WfAudioReadMapped:
 lda ($00,x)
 sta WfAudioReadByte
 pla
 sta $01,x
 pla
 sta $00,x
 pla
 tax
 plp
 lda WfAudioReadByte
 rts
