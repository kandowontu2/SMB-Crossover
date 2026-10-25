; Exact Proto Man skin003 from pinned Crossover2.02.
.pushseg
.segment "PROTO_GFX"
ProtoArtBegin:
ProtoSTANDLeft:
  .byte 36
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 8, 11
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 8, 3
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 8, -5
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 24, 11
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 24, 3
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 24, -5
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $82, 14, 0
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $83, 16, 11
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c3, 16, 3
ProtoSTANDRight:
  .byte 36
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 8, -3
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, 8, 5
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, 8, 13
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 24, -3
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 24, 5
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 24, 13
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c2, 14, 8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c3, 16, -3
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $83, 16, 5
ProtoWALK1Left:
  .byte 44
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 9, 12
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c0, 9, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 9, -4
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 25, 12
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 25, 4
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 25, -4
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $82, 15, 0
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $43, 1, 16
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $03, 1, 8
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c3, 17, 8
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $83, 17, 0
ProtoWALK1Right:
  .byte 44
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 9, -4
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $80, 9, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, 9, 12
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 25, -4
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 25, 4
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 25, 12
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c2, 15, 8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $03, 1, -8
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $43, 1, 0
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $83, 17, 0
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c3, 17, 8
ProtoWALK2Left:
  .byte 36
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 8, 12
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, 8, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $80, 8, -4
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 24, 12
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 24, 4
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $82, 14, 0
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $83, 15, 12
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c3, 15, 4
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $83, 15, -4
ProtoWALK2Right:
  .byte 36
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 8, -4
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 8, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c0, 8, 12
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 24, -4
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 24, 4
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c2, 14, 8
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c3, 15, -4
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $83, 15, 4
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c3, 15, 12
ProtoWALK3Left:
  .byte 40
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 9, 12
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $80, 9, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 9, -4
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 25, 12
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 25, 4
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 25, -4
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $82, 15, 0
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $03, 1, 12
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c3, 17, 4
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $83, 17, -4
ProtoWALK3Right:
  .byte 40
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 9, -4
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c0, 9, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, 9, 12
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 25, -4
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 25, 4
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 25, 12
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c2, 15, 8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $43, 1, -4
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $83, 17, 4
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c3, 17, 12
ProtoWALK4Left = ProtoWALK2Left
ProtoWALK4Right = ProtoWALK2Right
ProtoSHOOTLeft:
  .byte 36
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 9, 10
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c0, 9, 2
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 9, -6
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 25, 10
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 25, 2
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 25, -6
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $82, 15, -2
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c3, 16, 9
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c3, 16, 1
ProtoSHOOTRight:
  .byte 36
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 9, -2
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $80, 9, 6
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, 9, 14
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 25, -2
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 25, 6
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 25, 14
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c2, 15, 10
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $83, 16, -1
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $83, 16, 7
ProtoWALKSHOOT1Left:
  .byte 44
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 9, 12
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c0, 9, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 9, -4
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 25, 12
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 25, 4
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 25, -4
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $82, 15, 0
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $43, 1, 16
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $03, 1, 8
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $83, 17, 8
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $83, 17, 0
ProtoWALKSHOOT1Right:
  .byte 44
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 9, -4
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $80, 9, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, 9, 12
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 25, -4
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 25, 4
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 25, 12
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c2, 15, 8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $03, 1, -8
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $43, 1, 0
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c3, 17, 0
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c3, 17, 8
ProtoWALKSHOOT2Left:
  .byte 40
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 8, 12
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, 8, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 8, -4
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 24, 12
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 24, 4
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 24, -4
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $82, 14, 0
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c3, 16, 12
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c3, 16, 4
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $83, 16, -4
ProtoWALKSHOOT2Right:
  .byte 40
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 8, -4
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 8, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, 8, 12
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 24, -4
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 24, 4
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 24, 12
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c2, 14, 8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $83, 16, -4
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $83, 16, 4
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c3, 16, 12
ProtoWALKSHOOT3Left:
  .byte 40
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 9, 12
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, 9, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 9, -4
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 25, 12
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 25, 4
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 25, -4
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $82, 15, 0
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c3, 17, 12
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c3, 17, 4
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $83, 17, -4
ProtoWALKSHOOT3Right:
  .byte 40
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 9, -4
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 9, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, 9, 12
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 25, -4
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 25, 4
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 25, 12
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c2, 15, 8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $83, 17, -4
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $83, 17, 4
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c3, 17, 12
ProtoWALKSHOOT4Left = ProtoWALKSHOOT2Left
ProtoWALKSHOOT4Right = ProtoWALKSHOOT2Right
ProtoJUMPLeft:
  .byte 32
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 3, 15
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $80, 3, 7
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 3, -1
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 3, -9
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 19, 7
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 19, -1
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $82, 9, 1
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $83, 11, 2
ProtoJUMPRight:
  .byte 32
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 3, -7
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c0, 3, 1
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, 3, 9
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $40, 3, 17
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 19, 1
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 19, 9
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c2, 9, 7
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c3, 11, 6
ProtoJUMPSHOOTLeft:
  .byte 32
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 3, 10
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 3, 2
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 3, -6
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 19, 10
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 19, 2
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 19, -6
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $82, 9, -1
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $83, 11, 0
ProtoJUMPSHOOTRight:
  .byte 32
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 3, -2
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, 3, 6
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, 3, 14
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 19, -2
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 19, 6
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 19, 14
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c2, 9, 9
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c3, 11, 8
ProtoSLIDELeft:
  .byte 44
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 13, 19
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, 13, 11
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 13, 3
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 13, -5
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 29, 11
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 29, 3
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c0, 29, -5
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $82, 19, 3
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $83, 21, 15
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c3, 21, 7
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $83, 21, -1
ProtoSLIDERight:
  .byte 44
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 13, -11
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 13, -3
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, 13, 5
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $40, 13, 13
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 29, -3
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 29, 5
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $80, 29, 13
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c2, 19, 5
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c3, 21, -7
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $83, 21, 1
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c3, 21, 9
ProtoCLIMB1Left:
  .byte 16
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $40, 3, 8
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $40, 3, 0
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c0, 19, 8
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $80, 19, 0
ProtoCLIMB1Right:
  .byte 16
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 3, 0
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $00, 3, 8
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $80, 19, 0
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $c0, 19, 8
ProtoCLIMB2Left:
  .byte 16
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $00, 3, 7
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 3, -1
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $c0, 19, 7
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $80, 19, -1
ProtoCLIMB2Right:
  .byte 16
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $40, 3, 1
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $40, 3, 9
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $80, 19, 1
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c0, 19, 9
ProtoHURTLeft:
  .byte 40
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $40, 4, 20
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $40, 4, 12
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 4, 4
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 4, -4
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c0, 20, 12
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $80, 20, 4
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $80, 20, -4
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $82, 10, 2
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $03, -4, 13
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $c3, 12, 5
ProtoHURTRight:
  .byte 40
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 4, -12
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 4, -4
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $40, 4, 4
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $40, 4, 12
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $80, 20, -4
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c0, 20, 4
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $c0, 20, 12
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c2, 10, 6
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $43, -4, -5
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $83, 12, 3
ProtoSTEPLeft = ProtoSTANDLeft
ProtoSTEPRight = ProtoSTANDRight
ProtoTHROWLeft:
  .byte 40
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 6, 12
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, 6, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 6, -4
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 22, 12
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 22, 4
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 22, -4
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $80, 22, -12
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $02, 6, -2
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $03, 1, 9
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c3, 17, 1
ProtoTHROWRight:
  .byte 40
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 6, -4
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 6, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, 6, 12
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 22, -4
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 22, 4
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 22, 12
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c0, 22, 20
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $42, 6, 10
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $43, 1, -1
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $83, 17, 7
ProtoAIR_THROWLeft = ProtoJUMPLeft
ProtoAIR_THROWRight = ProtoJUMPRight
ProtoFISTLeft:
  .byte 44
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 9, 12
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $80, 9, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $80, 9, -4
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $40, 9, -12
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 9, -20
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 25, 12
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $80, 25, 4
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $80, 25, -4
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $82, 15, -2
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $03, 1, 9
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c3, 17, 1
ProtoFISTRight:
  .byte 44
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 9, -4
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c0, 9, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c0, 9, 12
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 9, 20
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $40, 9, 28
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 25, -4
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c0, 25, 4
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c0, 25, 12
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c2, 15, 10
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $43, 1, -1
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $83, 17, 7
ProtoAIR_FISTLeft:
  .byte 32
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 3, 15
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $80, 3, 7
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $00, 3, -1
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $40, 3, -9
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 19, 7
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 19, -1
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $82, 9, 1
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $83, 11, 2
ProtoAIR_FISTRight:
  .byte 32
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 3, -7
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c0, 3, 1
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $40, 3, 9
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 3, 17
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 19, 1
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 19, 9
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c2, 9, 7
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c3, 11, 6
ProtoCARRYLeft:
  .byte 36
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 8, 11
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 8, 3
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $80, 8, -5
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 24, 11
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 24, 3
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 24, -5
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $82, 14, 0
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $83, 16, 11
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c3, 16, 3
ProtoCARRYRight:
  .byte 36
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 8, -3
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, 8, 5
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c0, 8, 13
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 24, -3
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 24, 5
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 24, 13
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c2, 14, 8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c3, 16, -3
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $83, 16, 5
ProtoCARRY_STEPLeft:
  .byte 36
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 8, 11
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 8, 3
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $80, 8, -5
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 24, 11
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c0, 24, 3
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $80, 24, -5
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $82, 14, 0
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $83, 16, 11
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c3, 16, 3
ProtoCARRY_STEPRight:
  .byte 36
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 8, -3
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, 8, 5
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c0, 8, 13
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 24, -3
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $80, 24, 5
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c0, 24, 13
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c2, 14, 8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c3, 16, -3
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $83, 16, 5
ProtoCARRY_WALK1Left:
  .byte 36
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 9, 12
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c0, 9, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $80, 9, -4
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 25, 12
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 25, 4
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 25, -4
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $82, 15, 0
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c3, 15, 12
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c3, 15, 4
ProtoCARRY_WALK1Right:
  .byte 36
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 9, -4
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $80, 9, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c0, 9, 12
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 25, -4
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 25, 4
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 25, 12
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c2, 15, 8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $83, 15, -4
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $83, 15, 4
ProtoCARRY_WALK2Left:
  .byte 32
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 7, 12
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, 7, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $80, 7, -4
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 23, 12
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 23, 4
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $82, 14, 0
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $83, 15, 12
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c3, 15, 4
ProtoCARRY_WALK2Right:
  .byte 32
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 7, -4
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 7, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c0, 7, 12
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 23, -4
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 23, 4
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c2, 14, 8
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c3, 15, -4
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $83, 15, 4
ProtoCARRY_WALK3Left:
  .byte 36
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 9, 12
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $80, 9, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $80, 9, -4
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 25, 12
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 25, 4
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 25, -4
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $82, 15, 0
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $03, 1, 12
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c3, 17, 4
ProtoCARRY_WALK3Right:
  .byte 36
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 9, -4
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c0, 9, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c0, 9, 12
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 25, -4
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 25, 4
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 25, 12
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c2, 15, 8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $43, 1, -4
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $83, 17, 4
ProtoCARRY_JUMPLeft:
  .byte 32
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 3, 15
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $80, 3, 7
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $00, 3, -1
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 3, -9
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 19, 7
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $80, 19, -1
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $82, 9, 1
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $83, 11, 2
ProtoCARRY_JUMPRight:
  .byte 32
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 3, -7
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c0, 3, 1
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $40, 3, 9
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $40, 3, 17
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 19, 1
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c0, 19, 9
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c2, 9, 7
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c3, 11, 6
ProtoPoseLeftLo:
 .byte <ProtoSTANDLeft,<ProtoWALK1Left,<ProtoWALK2Left,<ProtoWALK3Left,<ProtoWALK4Left,<ProtoSHOOTLeft,<ProtoWALKSHOOT1Left,<ProtoWALKSHOOT2Left,<ProtoWALKSHOOT3Left,<ProtoWALKSHOOT4Left,<ProtoJUMPLeft,<ProtoJUMPSHOOTLeft,<ProtoSLIDELeft,<ProtoCLIMB1Left,<ProtoCLIMB2Left,<ProtoHURTLeft,<ProtoSTEPLeft,<ProtoTHROWLeft,<ProtoAIR_THROWLeft,<ProtoFISTLeft,<ProtoAIR_FISTLeft,<ProtoCARRYLeft,<ProtoCARRY_STEPLeft,<ProtoCARRY_WALK1Left,<ProtoCARRY_WALK2Left,<ProtoCARRY_WALK3Left,<ProtoCARRY_JUMPLeft
ProtoPoseLeftHi:
 .byte >ProtoSTANDLeft,>ProtoWALK1Left,>ProtoWALK2Left,>ProtoWALK3Left,>ProtoWALK4Left,>ProtoSHOOTLeft,>ProtoWALKSHOOT1Left,>ProtoWALKSHOOT2Left,>ProtoWALKSHOOT3Left,>ProtoWALKSHOOT4Left,>ProtoJUMPLeft,>ProtoJUMPSHOOTLeft,>ProtoSLIDELeft,>ProtoCLIMB1Left,>ProtoCLIMB2Left,>ProtoHURTLeft,>ProtoSTEPLeft,>ProtoTHROWLeft,>ProtoAIR_THROWLeft,>ProtoFISTLeft,>ProtoAIR_FISTLeft,>ProtoCARRYLeft,>ProtoCARRY_STEPLeft,>ProtoCARRY_WALK1Left,>ProtoCARRY_WALK2Left,>ProtoCARRY_WALK3Left,>ProtoCARRY_JUMPLeft
ProtoPoseRightLo:
 .byte <ProtoSTANDRight,<ProtoWALK1Right,<ProtoWALK2Right,<ProtoWALK3Right,<ProtoWALK4Right,<ProtoSHOOTRight,<ProtoWALKSHOOT1Right,<ProtoWALKSHOOT2Right,<ProtoWALKSHOOT3Right,<ProtoWALKSHOOT4Right,<ProtoJUMPRight,<ProtoJUMPSHOOTRight,<ProtoSLIDERight,<ProtoCLIMB1Right,<ProtoCLIMB2Right,<ProtoHURTRight,<ProtoSTEPRight,<ProtoTHROWRight,<ProtoAIR_THROWRight,<ProtoFISTRight,<ProtoAIR_FISTRight,<ProtoCARRYRight,<ProtoCARRY_STEPRight,<ProtoCARRY_WALK1Right,<ProtoCARRY_WALK2Right,<ProtoCARRY_WALK3Right,<ProtoCARRY_JUMPRight
ProtoPoseRightHi:
 .byte >ProtoSTANDRight,>ProtoWALK1Right,>ProtoWALK2Right,>ProtoWALK3Right,>ProtoWALK4Right,>ProtoSHOOTRight,>ProtoWALKSHOOT1Right,>ProtoWALKSHOOT2Right,>ProtoWALKSHOOT3Right,>ProtoWALKSHOOT4Right,>ProtoJUMPRight,>ProtoJUMPSHOOTRight,>ProtoSLIDERight,>ProtoCLIMB1Right,>ProtoCLIMB2Right,>ProtoHURTRight,>ProtoSTEPRight,>ProtoTHROWRight,>ProtoAIR_THROWRight,>ProtoFISTRight,>ProtoAIR_FISTRight,>ProtoCARRYRight,>ProtoCARRY_STEPRight,>ProtoCARRY_WALK1Right,>ProtoCARRY_WALK2Right,>ProtoCARRY_WALK3Right,>ProtoCARRY_JUMPRight
ProtoPoseChrLo:
 .byte .lobyte(PROTO_CHR_FIRST+0),.lobyte(PROTO_CHR_FIRST+1),.lobyte(PROTO_CHR_FIRST+2),.lobyte(PROTO_CHR_FIRST+3),.lobyte(PROTO_CHR_FIRST+2),.lobyte(PROTO_CHR_FIRST+4),.lobyte(PROTO_CHR_FIRST+5),.lobyte(PROTO_CHR_FIRST+6),.lobyte(PROTO_CHR_FIRST+7),.lobyte(PROTO_CHR_FIRST+6),.lobyte(PROTO_CHR_FIRST+8),.lobyte(PROTO_CHR_FIRST+9),.lobyte(PROTO_CHR_FIRST+10),.lobyte(PROTO_CHR_FIRST+0),.lobyte(PROTO_CHR_FIRST+0),.lobyte(PROTO_CHR_FIRST+11),.lobyte(PROTO_CHR_FIRST+12),.lobyte(PROTO_CHR_FIRST+13),.lobyte(PROTO_CHR_FIRST+14),.lobyte(PROTO_CHR_FIRST+15),.lobyte(PROTO_CHR_FIRST+14),.lobyte(PROTO_CHR_FIRST+16),.lobyte(PROTO_CHR_FIRST+16),.lobyte(PROTO_CHR_FIRST+17),.lobyte(PROTO_CHR_FIRST+18),.lobyte(PROTO_CHR_FIRST+19),.lobyte(PROTO_CHR_FIRST+8)
ProtoPoseChrHi:
 .byte .hibyte(PROTO_CHR_FIRST+0),.hibyte(PROTO_CHR_FIRST+1),.hibyte(PROTO_CHR_FIRST+2),.hibyte(PROTO_CHR_FIRST+3),.hibyte(PROTO_CHR_FIRST+2),.hibyte(PROTO_CHR_FIRST+4),.hibyte(PROTO_CHR_FIRST+5),.hibyte(PROTO_CHR_FIRST+6),.hibyte(PROTO_CHR_FIRST+7),.hibyte(PROTO_CHR_FIRST+6),.hibyte(PROTO_CHR_FIRST+8),.hibyte(PROTO_CHR_FIRST+9),.hibyte(PROTO_CHR_FIRST+10),.hibyte(PROTO_CHR_FIRST+0),.hibyte(PROTO_CHR_FIRST+0),.hibyte(PROTO_CHR_FIRST+11),.hibyte(PROTO_CHR_FIRST+12),.hibyte(PROTO_CHR_FIRST+13),.hibyte(PROTO_CHR_FIRST+14),.hibyte(PROTO_CHR_FIRST+15),.hibyte(PROTO_CHR_FIRST+14),.hibyte(PROTO_CHR_FIRST+16),.hibyte(PROTO_CHR_FIRST+16),.hibyte(PROTO_CHR_FIRST+17),.hibyte(PROTO_CHR_FIRST+18),.hibyte(PROTO_CHR_FIRST+19),.hibyte(PROTO_CHR_FIRST+8)
ProtoArtEnd:
.assert ProtoArtEnd <= $D108,error,"Proto art overlaps retained common MegaMan projectile records"
.popseg
