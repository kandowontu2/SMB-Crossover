; Same original channel selection, carry and final A/N/Z/V/D/I.
; X!=0 never changes A before PLA; ORA#0 supplies those exact original N/Z.
; The complete original X=0 branch retains its PHA/PLA and conditional carry.
.pushseg
.segment "TMNT_DURATION_HELPER"
.proc TnSourceChannelOwner
 cpx #0
 beq Zero
 ldx a:TnAudioRam+$93
 clc
 ora #0
 rts
Zero:
 pha
 lda a:TnAudioRam+$0e
 beq Clear
 sec
 pla
 rts
Clear:
 clc
 pla
 rts
.endproc
.assert TnSourceChannelOwner=$a2e0,lderror,"Verified last32B writer slack"
.assert *<=$a300,lderror,"Keep genuine duration products and note stream"
.export TnSourceChannelOwner
.popseg
