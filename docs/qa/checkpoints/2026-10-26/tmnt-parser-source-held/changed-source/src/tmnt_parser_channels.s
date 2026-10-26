; Immutable original six-channel register mapping; no music data removed.
.pushseg
.segment "TMNT_DURATION_HELPER"
TnNativeChannelOffsets:
 .byte 0,4,8,12,0,12
.assert TnNativeChannelOffsets>=$a200 && *<=$a300,lderror,"Declared duration-helper FF tail only"
.export TnNativeChannelOffsets
.popseg
