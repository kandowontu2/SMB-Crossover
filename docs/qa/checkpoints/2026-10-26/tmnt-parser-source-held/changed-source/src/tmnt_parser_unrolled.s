; Same six source voices/calls/order and all RAM92/RAM93 stores.
.pushseg
.segment "TMNT_DURATION_HELPER"
.proc TnNativeUnrolled
 jsr $a612
 ldx #0
 ldy #0
.repeat 6,I
 stx a:TnAudioRam+$92
 sty a:TnAudioRam+$93
 lda a:TnAudioRam+$0a,x
 beq :+
 jsr $a671
:
 inx
.if I<5
 .if I=4
  ldy #12
 .else
  ldy #(((I+1)*4)&15)
 .endif
 cpx #5
 tya
.else
 cpx #6
.endif
.endrepeat
 rts
.endproc
.assert TnNativeUnrolled=$a221,lderror,"Append only declaredFF after readonly channel table"
.assert *<=$a300,lderror,"Retain complete original products table and moved source stream"
.export TnNativeUnrolled
.popseg
