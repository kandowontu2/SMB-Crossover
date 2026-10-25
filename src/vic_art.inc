; Original Gradius USA records; two explicit NES palette approximations.
.pushseg
.segment "VIC_GFX"
VicArtBegin:
VvPose6:
  .byte 8
  .byte $00,$00,$0f,$08
  .byte $02,$02,$0f,$08
VvPose7:
  .byte 8
  .byte $04,$00,$0f,$08
  .byte $04,$00,$0f,$10
VvPose8:
  .byte 8
  .byte $06,$00,$10,$08
  .byte $08,$02,$10,$08
VvPose10:
  .byte 8
  .byte $0a,$00,$08,$08
  .byte $0c,$02,$08,$08
VvPose36:
  .byte 8
  .byte $0e,$00,$08,$10
  .byte $10,$02,$08,$10
VvPose4:
  .byte 16
  .byte $12,$40,$08,$08
  .byte $14,$42,$08,$08
  .byte $12,$00,$08,$00
  .byte $14,$02,$08,$00
VvPose5:
  .byte 16
  .byte $16,$40,$08,$08
  .byte $18,$42,$08,$08
  .byte $16,$00,$08,$00
  .byte $18,$02,$08,$00
VvPose16:
  .byte 16
  .byte $1a,$00,$08,$08
  .byte $1c,$02,$08,$08
  .byte $1a,$c0,$08,$10
  .byte $1c,$c2,$08,$10
VvPose17:
  .byte 16
  .byte $1a,$80,$08,$08
  .byte $1c,$82,$08,$08
  .byte $1a,$40,$08,$10
  .byte $1c,$42,$08,$10
VvPose18:
  .byte 16
  .byte $1e,$80,$08,$08
  .byte $1c,$82,$08,$08
  .byte $1e,$40,$08,$10
  .byte $1c,$42,$08,$10
VvPose1:
  .byte 32
  .byte $20,$00,$08,$10
  .byte $22,$02,$08,$10
  .byte $24,$00,$08,$08
  .byte $26,$02,$08,$08
  .byte $28,$00,$08,$00
  .byte $2a,$02,$08,$00
  .byte $2c,$00,$00,$fc
  .byte $2e,$02,$00,$fc
VvPose2:
  .byte 32
  .byte $20,$00,$05,$10
  .byte $22,$02,$05,$10
  .byte $24,$00,$05,$08
  .byte $26,$02,$05,$08
  .byte $28,$00,$05,$00
  .byte $2a,$02,$05,$00
  .byte $2c,$00,$01,$fc
  .byte $2e,$02,$01,$fc
VvPose3:
  .byte 28
  .byte $20,$00,$0c,$10
  .byte $22,$02,$0c,$10
  .byte $24,$00,$0c,$08
  .byte $26,$00,$0c,$00
  .byte $28,$02,$0c,$00
  .byte $2a,$00,$02,$fc
  .byte $2c,$02,$02,$fc
VvPose45:
  .byte 24
  .byte $00,$00,$08,$00
  .byte $02,$00,$08,$08
  .byte $04,$02,$08,$08
  .byte $02,$c0,$07,$10
  .byte $04,$c2,$07,$10
  .byte $00,$c0,$07,$18
VvPose46:
  .byte 32
  .byte $00,$00,$08,$00
  .byte $02,$02,$08,$00
  .byte $04,$00,$08,$08
  .byte $06,$02,$08,$08
  .byte $04,$c0,$07,$10
  .byte $06,$c2,$07,$10
  .byte $00,$c0,$07,$18
  .byte $02,$c2,$07,$18
VvPose47:
  .byte 24
  .byte $00,$00,$08,$00
  .byte $02,$00,$08,$08
  .byte $04,$02,$08,$08
  .byte $02,$c0,$07,$10
  .byte $04,$c2,$07,$10
  .byte $00,$c0,$07,$18
VvPose48:
  .byte 16
  .byte $00,$00,$08,$08
  .byte $02,$02,$08,$08
  .byte $04,$00,$08,$10
  .byte $06,$02,$08,$10
.popseg
