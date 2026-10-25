; Authentic source masks remapped to existing SMB sprite palettes.
; Odd8x16 tile IDs select the $1000 window4 published by X5SetSpecialChr.
; No per-item enemy palette changes; body pages524..543 remain byte-exact.
.pushseg
.segment "M3_GFX"
M3WorldArtBegin:
M3Item0:
 .byte 16,1,2,0,248,3,3,0,248,1,66,0,0,3,67,0,0
M3Item1:
 .byte 16,1,2,0,248,3,3,0,248,1,66,0,0,3,67,0,0
M3Item2:
 .byte 24,5,1,0,248,7,2,0,248,9,3,0,248,5,65,0,0,7,66,0,0,9,67,0,0
M3Item3:
 .byte 16,11,1,0,248,13,3,0,248,15,1,0,0,17,3,0,0
M3Item4:
 .byte 16,19,1,0,248,21,3,0,248,19,65,0,0,21,67,0,0
M3Item5:
 .byte 16,23,2,0,248,25,3,0,248,23,66,0,0,25,67,0,0
M3Item6:
 .byte 16,27,2,0,248,29,3,0,248,27,66,0,0,29,67,0,0
M3Fire0:
 .byte 4,31,2,0,0
M3Fire1:
 .byte 4,33,2,0,0
M3Fire2:
 .byte 4,31,194,0,0
M3Fire3:
 .byte 4,33,194,0,0
M3Hammer0:
 .byte 8,35,2,0,6,37,3,0,6
M3Hammer1:
 .byte 8,35,130,6,6,37,131,6,6
M3Hammer2:
 .byte 8,35,194,6,0,37,195,6,0
M3Hammer3:
 .byte 8,35,66,0,0,37,67,0,0
M3Poof0:
 .byte 8,39,2,0,0,39,194,0,8
M3Poof1:
 .byte 8,41,2,0,0,41,194,0,8
M3Poof2:
 .byte 8,43,2,0,0,43,194,0,8
M3Poof3:
 .byte 8,45,2,0,0,45,194,0,8
M3WorldPtrLo:
.lobytes M3Item0,M3Item1,M3Item2,M3Item3,M3Item4,M3Item5,M3Item6,M3Fire0,M3Fire1,M3Fire2,M3Fire3,M3Hammer0,M3Hammer1,M3Hammer2,M3Hammer3,M3Poof0,M3Poof1,M3Poof2,M3Poof3
M3WorldPtrHi:
.hibytes M3Item0,M3Item1,M3Item2,M3Item3,M3Item4,M3Item5,M3Item6,M3Fire0,M3Fire1,M3Fire2,M3Fire3,M3Hammer0,M3Hammer1,M3Hammer2,M3Hammer3,M3Poof0,M3Poof1,M3Poof2,M3Poof3
.popseg
