.pushseg
.segment "KIRBY_GFX"
KbCopyIconLo:
.byte <KbIcon0,<KbIcon1,<KbIcon2,<KbIcon3,<KbIcon4,<KbIcon5,<KbIcon6,<KbIcon7,<KbIcon8,<KbIcon9,<KbIcon10,<KbIcon11,<KbIcon12,<KbIcon13
KbCopyIconHi:
.byte >KbIcon0,>KbIcon1,>KbIcon2,>KbIcon3,>KbIcon4,>KbIcon5,>KbIcon6,>KbIcon7,>KbIcon8,>KbIcon9,>KbIcon10,>KbIcon11,>KbIcon12,>KbIcon13
KbIcon0:
.byte 8,162,3,0,0,164,3,0,8
KbIcon1:
.byte 8,154,0,0,0,154,64,0,8
KbIcon2:
.byte 8,154,2,0,0,154,66,0,8
KbIcon3:
.byte 8,160,3,0,0,160,67,0,8
KbIcon4:
.byte 16,192,1,0,0,194,1,0,8,224,1,16,0,226,1,16,8
KbIcon5:
.byte 16,218,3,0,0,218,67,0,8,250,3,16,0,250,67,16,8
KbIcon6:
.byte 8,172,0,0,0,174,0,0,8
KbIcon7:
.byte 8,172,2,0,0,174,2,0,8
KbIcon8:
.byte 16,144,0,0,0,146,0,0,8,176,0,16,0,178,0,16,8
KbIcon9:
.byte 16,204,1,0,0,206,1,0,8,236,1,16,0,238,1,16,8
KbIcon10:
.byte 8,136,2,0,0,138,2,0,8
KbIcon11:
.byte 16,220,1,0,0,220,65,0,8,252,1,16,0,252,65,16,8
KbIcon12:
.byte 8,25,2,0,0,25,66,0,8
KbIcon13:
.byte 8,156,3,0,0,158,3,0,8
KbIcon14:
.byte 4,94,3,0,0
KbIcon15:
.byte 8,64,3,0,0,66,3,0,8
KbIcon16:
.byte 8,208,2,0,0,208,194,0,8
KbIcon17:
.byte 8,210,2,0,0,210,194,0,8
KbNativeShotLo:
.byte <KbIcon14,<KbIcon15,<KbIcon16,<KbIcon17
KbNativeShotHi:
.byte >KbIcon14,>KbIcon15,>KbIcon16,>KbIcon17
.popseg
