; Authenticated Rogue1.21 pickups. Rawtype0..9, phase=(sourceClock>>1)&3.
; Include after HOST_AUX code, with RdWxAuxStart=$ad60 in physical121.
; Intentional C121 data lease; no permission to replace native world palettes.
RD_ITEM_FIRST_CHR=694
RD_ITEM_FIRST_WINDOW=6
RD_ITEM_LO_C=$de00
RD_ITEM_HI_C=$de28
.pushseg
.segment "ROGUE_DAWN_HOST_AUX"
.assert (*-RdWxAuxStart)<=$10a0,error,"Reserve original item ART tail"
 .res $10a0-(*-RdWxAuxStart),$ff
.export RdItemLoA,RdItemHiA,RD_ITEM_FIRST_CHR,RD_ITEM_FIRST_WINDOW
.export RD_ITEM_LO_C,RD_ITEM_HI_C
RdItemLoA:
 .byte <(RdItemRecord0+$2000),<(RdItemRecord1+$2000),<(RdItemRecord2+$2000),<(RdItemRecord3+$2000),<(RdItemRecord4+$2000),<(RdItemRecord5+$2000),<(RdItemRecord6+$2000),<(RdItemRecord7+$2000),<(RdItemRecord8+$2000),<(RdItemRecord9+$2000),<(RdItemRecord10+$2000),<(RdItemRecord11+$2000),<(RdItemRecord12+$2000),<(RdItemRecord13+$2000),<(RdItemRecord14+$2000),<(RdItemRecord15+$2000),<(RdItemRecord16+$2000),<(RdItemRecord17+$2000),<(RdItemRecord18+$2000),<(RdItemRecord19+$2000),<(RdItemRecord20+$2000),<(RdItemRecord21+$2000),<(RdItemRecord22+$2000),<(RdItemRecord23+$2000),<(RdItemRecord24+$2000),<(RdItemRecord25+$2000),<(RdItemRecord26+$2000),<(RdItemRecord27+$2000),<(RdItemRecord28+$2000),<(RdItemRecord29+$2000),<(RdItemRecord30+$2000),<(RdItemRecord31+$2000),<(RdItemRecord32+$2000),<(RdItemRecord33+$2000),<(RdItemRecord34+$2000),<(RdItemRecord35+$2000),<(RdItemRecord36+$2000),<(RdItemRecord37+$2000),<(RdItemRecord38+$2000),<(RdItemRecord39+$2000)
RdItemHiA:
 .byte >(RdItemRecord0+$2000),>(RdItemRecord1+$2000),>(RdItemRecord2+$2000),>(RdItemRecord3+$2000),>(RdItemRecord4+$2000),>(RdItemRecord5+$2000),>(RdItemRecord6+$2000),>(RdItemRecord7+$2000),>(RdItemRecord8+$2000),>(RdItemRecord9+$2000),>(RdItemRecord10+$2000),>(RdItemRecord11+$2000),>(RdItemRecord12+$2000),>(RdItemRecord13+$2000),>(RdItemRecord14+$2000),>(RdItemRecord15+$2000),>(RdItemRecord16+$2000),>(RdItemRecord17+$2000),>(RdItemRecord18+$2000),>(RdItemRecord19+$2000),>(RdItemRecord20+$2000),>(RdItemRecord21+$2000),>(RdItemRecord22+$2000),>(RdItemRecord23+$2000),>(RdItemRecord24+$2000),>(RdItemRecord25+$2000),>(RdItemRecord26+$2000),>(RdItemRecord27+$2000),>(RdItemRecord28+$2000),>(RdItemRecord29+$2000),>(RdItemRecord30+$2000),>(RdItemRecord31+$2000),>(RdItemRecord32+$2000),>(RdItemRecord33+$2000),>(RdItemRecord34+$2000),>(RdItemRecord35+$2000),>(RdItemRecord36+$2000),>(RdItemRecord37+$2000),>(RdItemRecord38+$2000),>(RdItemRecord39+$2000)
RdItemRecord0:
 .byte $08,$81,$00,$ff,$01,$83,$00,$ff,$09
RdItemRecord1:
 .byte $08,$81,$01,$ff,$01,$83,$01,$ff,$09
RdItemRecord2:
 .byte $08,$81,$02,$ff,$01,$83,$02,$ff,$09
RdItemRecord3:
 .byte $08,$81,$03,$ff,$01,$83,$03,$ff,$09
RdItemRecord4:
 .byte $08,$85,$00,$ff,$00,$87,$00,$ff,$08
RdItemRecord5:
 .byte $08,$85,$01,$ff,$00,$87,$01,$ff,$08
RdItemRecord6:
 .byte $08,$85,$02,$ff,$00,$87,$02,$ff,$08
RdItemRecord7:
 .byte $08,$85,$03,$ff,$00,$87,$03,$ff,$08
RdItemRecord8:
 .byte $08,$89,$00,$ff,$02,$8b,$00,$ff,$0a
RdItemRecord9:
 .byte $10,$8d,$00,$ff,$02,$8f,$00,$ff,$0a,$91,$01,$ff,$02,$93,$01,$ff,$0a
RdItemRecord10:
 .byte $10,$8d,$00,$ff,$02,$8f,$00,$ff,$0a,$91,$02,$ff,$02,$93,$02,$ff,$0a
RdItemRecord11:
 .byte $10,$8d,$00,$ff,$02,$8f,$00,$ff,$0a,$91,$03,$ff,$02,$93,$03,$ff,$0a
RdItemRecord12:
 .byte $08,$95,$00,$00,$00,$97,$00,$00,$08
RdItemRecord13:
 .byte $08,$95,$01,$00,$00,$97,$01,$00,$08
RdItemRecord14:
 .byte $08,$95,$02,$00,$00,$97,$02,$00,$08
RdItemRecord15:
 .byte $08,$95,$03,$00,$00,$97,$03,$00,$08
RdItemRecord16:
 .byte $08,$99,$00,$ff,$03,$9b,$00,$ff,$0b
RdItemRecord17:
 .byte $08,$99,$01,$ff,$03,$9b,$01,$ff,$0b
RdItemRecord18:
 .byte $08,$99,$02,$ff,$03,$9b,$02,$ff,$0b
RdItemRecord19:
 .byte $08,$99,$03,$ff,$03,$9b,$03,$ff,$0b
RdItemRecord20:
 .byte $08,$9d,$00,$ff,$00,$9f,$00,$ff,$08
RdItemRecord21:
 .byte $08,$9d,$01,$ff,$00,$9f,$01,$ff,$08
RdItemRecord22:
 .byte $08,$9d,$02,$ff,$00,$9f,$02,$ff,$08
RdItemRecord23:
 .byte $08,$9d,$03,$ff,$00,$9f,$03,$ff,$08
RdItemRecord24:
 .byte $08,$a1,$00,$ff,$02,$a3,$00,$ff,$0a
RdItemRecord25:
 .byte $10,$a5,$00,$ff,$02,$a7,$00,$ff,$0a,$91,$01,$ff,$02,$93,$01,$ff,$0a
RdItemRecord26:
 .byte $10,$a5,$00,$ff,$02,$a7,$00,$ff,$0a,$91,$02,$ff,$02,$93,$02,$ff,$0a
RdItemRecord27:
 .byte $10,$a5,$00,$ff,$02,$a7,$00,$ff,$0a,$91,$03,$ff,$02,$93,$03,$ff,$0a
RdItemRecord28:
 .byte $10,$91,$00,$ff,$02,$93,$00,$ff,$0a,$a9,$01,$ff,$02,$ab,$01,$ff,$0a
RdItemRecord29:
 .byte $08,$ad,$01,$ff,$02,$af,$01,$ff,$0a
RdItemRecord30:
 .byte $10,$a9,$01,$ff,$02,$ab,$01,$ff,$0a,$91,$02,$ff,$02,$93,$02,$ff,$0a
RdItemRecord31:
 .byte $10,$a9,$01,$ff,$02,$ab,$01,$ff,$0a,$91,$03,$ff,$02,$93,$03,$ff,$0a
RdItemRecord32:
 .byte $08,$b1,$00,$ff,$00,$b3,$00,$ff,$08
RdItemRecord33:
 .byte $08,$b1,$01,$ff,$00,$b3,$01,$ff,$08
RdItemRecord34:
 .byte $08,$b1,$02,$ff,$00,$b3,$02,$ff,$08
RdItemRecord35:
 .byte $08,$b1,$03,$ff,$00,$b3,$03,$ff,$08
RdItemRecord36:
 .byte $08,$b5,$00,$ff,$00,$b7,$00,$ff,$08
RdItemRecord37:
 .byte $08,$b5,$01,$ff,$00,$b7,$01,$ff,$08
RdItemRecord38:
 .byte $08,$b5,$02,$ff,$00,$b7,$02,$ff,$08
RdItemRecord39:
 .byte $08,$b5,$03,$ff,$00,$b7,$03,$ff,$08
RdItemArtEnd:
.assert .loword(RdItemLoA)=$be00,lderror,"C121 mirrored item pointers"
.assert RdItemArtEnd-RdItemLoA<=512,error,"Original item512B tail"
.popseg
