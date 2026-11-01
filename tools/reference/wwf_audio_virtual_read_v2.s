; Original stream pointers live in bank1's private scratch. Borrow only the
; host's two scoped pointer bytes for the actual read, preserving X/Y/P.
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
 lda R0
 pha
 lda R1
 pha
 lda WfAudioScratch+1,x
 cmp #$e8
 bcc WfAudioReadLow
 lda WfAudioScratch,x
 clc
 adc #.lobyte(WfAudioHighData-$e84e)
 sta R0
 lda WfAudioScratch+1,x
 adc #.hibyte(WfAudioHighData-$e84e)
 sta R1
 jmp WfAudioReadMapped
WfAudioReadLow:
 lda WfAudioScratch,x
 clc
 adc #.lobyte(WfAudioLowData-$8018)
 sta R0
 lda WfAudioScratch+1,x
 adc #.hibyte(WfAudioLowData-$8018)
 sta R1
WfAudioReadMapped:
 lda (R0),y
 sta WfAudioScratch+9
 pla
 sta R1
 pla
 sta R0
 pla
 tax
 plp
 lda WfAudioScratch+9
 rts
