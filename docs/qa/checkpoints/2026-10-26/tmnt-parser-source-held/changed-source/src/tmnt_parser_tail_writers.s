; Exact original STA replacement body; only adapter JSR/RTS removed.
.pushseg
.segment "TMNT_DURATION_HELPER"
.proc TnTailAC1D
 sta a:GuestNativeApu+2,x
 php
 inc a:GuestNativeDirty+2,x
 plp
 jmp $ac20
.endproc
.export TnTailAC1D
.proc TnTailAC09
 sta a:GuestNativeApu+3,x
 php
 inc a:GuestNativeDirty+3,x
 plp
 jmp $ac0c
.endproc
.export TnTailAC09
.proc TnTailAADD
 sta a:GuestNativeApu+8
 php
 inc a:GuestNativeDirty+8
 plp
 jmp $aae0
.endproc
.export TnTailAADD
.proc TnTailB16C
 sta a:GuestNativeApu+0,x
 php
 inc a:GuestNativeDirty+0,x
 plp
 jmp $b16f
.endproc
.export TnTailB16C
.proc TnTailB171
 sta a:GuestNativeApu+1,x
 php
 inc a:GuestNativeDirty+1,x
 plp
 jmp $b174
.endproc
.export TnTailB171
.proc TnTailAA96
 sta a:GuestNativeApu+0,x
 php
 inc a:GuestNativeDirty+0,x
 plp
 jmp $aa99
.endproc
.export TnTailAA96
.assert TnTailAC1D=$a29e,lderror,"Append only original declared FF"
.assert *<=$a300,lderror,"Keep all original products and stream bytes"
.popseg
