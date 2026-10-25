; Original RescueRangers USA renderer pixels, losslessly8x8 to8x16.
.pushseg
.segment "CD_GFX"
CdArtBegin:
CdPose0Right:
 .byte 28
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 14, -2
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 14, 6
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 14, 14
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 30, -2
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 30, 6
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $00, 30, 14
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $01, 20, 0
CdPose0Left:
 .byte 24
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 14, -1
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 14, 7
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 14, 15
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 30, -1
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 30, 7
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $01, 20, 10
CdPose1Right:
 .byte 20
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 8, 1
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 8, 9
 .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 24, 1
 .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 24, 9
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $01, 14, 3
CdPose1Left:
 .byte 20
 .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 8, -1
 .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 8, 7
 .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 24, -1
 .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 24, 7
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $01, 14, 7
CdPose2Right:
 .byte 28
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 14, -2
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 14, 6
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 14, 14
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 30, -2
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 30, 6
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $00, 30, 14
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $01, 20, 0
CdPose2Left:
 .byte 24
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 14, -1
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 14, 7
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 14, 15
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 30, -1
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 30, 7
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $01, 20, 10
CdPose3Right:
 .byte 24
 .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 8, 0
 .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 8, 8
 .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 24, 0
 .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 24, 8
 .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $00, 24, 16
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $01, 14, 2
CdPose3Left:
 .byte 24
 .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $00, 8, -2
 .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $00, 8, 6
 .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 8, 14
 .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $00, 24, -2
 .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $00, 24, 6
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $01, 14, 8
CdPose4Right:
 .byte 24
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 8, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 8, 8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 24, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 24, 8
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 24, 16
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $01, 14, 2
CdPose4Left:
 .byte 24
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, 8, -2
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 8, 6
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 8, 14
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 24, -2
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 24, 6
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $01, 14, 8
CdPose5Right:
 .byte 24
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 8, 1
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 8, 9
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 24, 1
 .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 24, 9
 .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 24, 17
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $01, 14, 3
CdPose5Left:
 .byte 24
 .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 8, -2
 .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 8, 6
 .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 8, 14
 .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 24, -2
 .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 24, 6
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $01, 14, 7
CdPose6Right:
 .byte 24
 .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 8, 0
 .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 8, 8
 .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 24, 0
 .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $00, 24, 8
 .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $00, 24, 16
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $01, 14, 2
CdPose6Left:
 .byte 24
 .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $00, 8, -1
 .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 8, 7
 .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 8, 15
 .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $00, 24, -1
 .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $00, 24, 7
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $01, 14, 8
CdPose7Right:
 .byte 24
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 8, 1
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 8, 9
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 24, 1
 .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 24, 9
 .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 24, 17
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $01, 14, 3
CdPose7Left:
 .byte 24
 .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 8, -2
 .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 8, 6
 .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 8, 14
 .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 24, -2
 .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 24, 6
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $01, 14, 7
CdPose8Right:
 .byte 24
 .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 8, 0
 .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 8, 8
 .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 24, 0
 .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 24, 8
 .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $00, 24, 16
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $01, 14, 2
CdPose8Left:
 .byte 24
 .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $00, 8, -2
 .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $00, 8, 6
 .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 8, 14
 .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $00, 24, -2
 .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $00, 24, 6
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $01, 14, 8
CdPose9Right:
 .byte 24
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 8, 1
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 8, 9
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 24, 1
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 24, 9
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 24, 17
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $01, 14, 3
CdPose9Left:
 .byte 24
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, 8, -2
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 8, 6
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 8, 14
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 24, -2
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 24, 6
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $01, 14, 7
CdPose10Right:
 .byte 24
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 8, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 8, 8
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 24, 0
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 24, 8
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 24, 16
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $01, 14, 2
CdPose10Left:
 .byte 24
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, 8, -1
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 8, 7
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 8, 15
 .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 24, -1
 .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 24, 7
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $01, 14, 8
CdPose11Right:
 .byte 24
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 8, 1
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 8, 9
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 24, 1
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 24, 9
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 24, 17
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $01, 14, 3
CdPose11Left:
 .byte 24
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, 8, -2
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 8, 6
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 8, 14
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 24, -2
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 24, 6
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $01, 14, 7
CdPose12Right:
 .byte 28
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 14, -2
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 14, 6
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 14, 14
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 30, -2
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 30, 6
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $00, 30, 14
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $01, 20, 0
CdPose12Left:
 .byte 24
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 14, -1
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 14, 7
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 14, 15
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 30, -1
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 30, 7
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $01, 20, 10
CdPose13Right:
 .byte 24
 .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 14, 0
 .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 14, 8
 .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 14, 16
 .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 30, 0
 .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 30, 8
 .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 30, 16
CdPose13Left:
 .byte 20
 .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 14, -2
 .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 14, 6
 .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $00, 14, 14
 .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $00, 30, -2
 .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $00, 30, 6
CdPose14Right:
 .byte 28
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 8, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 8, 8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 8, 16
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 24, 0
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 24, 8
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $00, 24, 16
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $01, 14, 2
CdPose14Left:
 .byte 24
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 8, -2
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 8, 6
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 8, 14
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 24, -2
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 24, 6
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $01, 14, 8
CdPose15Right:
 .byte 24
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 8, 0
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 8, 8
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 24, 0
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 24, 8
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $00, 24, 16
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $01, 14, 2
CdPose15Left:
 .byte 24
 .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 8, -2
 .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 8, 6
 .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 8, 14
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 24, -2
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 24, 6
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $01, 14, 8
CdPose16Right:
 .byte 20
 .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 8, 1
 .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 8, 9
 .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 24, 1
 .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 24, 9
 .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $01, 14, 3
CdPose16Left:
 .byte 20
 .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 8, -1
 .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 8, 7
 .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $00, 24, -1
 .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $00, 24, 7
 .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $01, 14, 7
CdPose17Right:
 .byte 28
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 0, -9
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 0, -1
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 0, 7
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 16, -9
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 16, -1
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $00, 16, 7
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $01, 14, -7
CdPose17Left:
 .byte 28
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 0, 2
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 0, 10
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 0, 18
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 16, 2
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 16, 10
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 16, 18
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $01, 14, 17
CdPose18Right:
 .byte 20
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 8, 3
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 8, 11
 .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 24, 3
 .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $00, 24, 11
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $01, 14, 5
CdPose18Left:
 .byte 20
 .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $00, 8, -3
 .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $00, 8, 5
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 24, -3
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 24, 5
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $01, 14, 5
CdPose19Right:
 .byte 28
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 0, -9
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 0, -1
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 0, 7
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 16, -9
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 16, -1
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $00, 16, 7
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $01, 14, -7
CdPose19Left:
 .byte 28
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 0, 2
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 0, 10
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 0, 18
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 16, 2
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 16, 10
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 16, 18
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $01, 14, 17
CdPose20Right:
 .byte 20
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 8, 0
 .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 8, 8
 .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 24, 0
 .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 24, 8
 .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $01, 17, 3
CdPose20Left:
 .byte 20
 .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 8, 0
 .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 8, 8
 .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 24, 0
 .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 24, 8
 .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $01, 17, 8
CdPose21Right:
 .byte 28
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 8, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 8, 8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 24, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 24, 8
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 24, 16
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $01, 1, 2
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $01, 17, 2
CdPose21Left:
 .byte 28
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 8, -1
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 8, 7
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 8, 15
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 24, -1
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 24, 7
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $01, 1, 6
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $01, 17, 6
CdPose22Right:
 .byte 28
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 8, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 8, 8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 24, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 24, 8
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 24, 16
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $01, -3, 10
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $01, 13, 2
CdPose22Left:
 .byte 28
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 8, -1
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 8, 7
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 8, 15
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 24, -1
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 24, 7
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $01, -3, -2
 .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $01, 13, 6
CdPose23Right:
 .byte 28
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 8, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 8, 8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 24, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 24, 8
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 24, 16
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $01, -7, 2
 .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $01, 9, 2
CdPose23Left:
 .byte 28
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 8, -1
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 8, 7
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 8, 15
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 24, -1
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 24, 7
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $01, -7, 6
 .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $01, 9, 6
CdPose24Right:
 .byte 32
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 8, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 8, 8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 24, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 24, 8
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 24, 16
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $01, -3, -3
 .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $01, 13, -3
 .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $01, 13, 5
CdPose24Left:
 .byte 32
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 8, -1
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 8, 7
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 8, 15
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 24, -1
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 24, 7
 .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $01, -3, 9
 .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $01, -3, 17
 .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $01, 13, 9
CdPose25Right:
 .byte 16
 .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 16, -2
 .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $00, 16, 6
 .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $00, 16, 14
 .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $01, 20, 0
CdPose25Left:
 .byte 16
 .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 16, -1
 .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $00, 16, 7
 .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $00, 16, 15
 .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $01, 20, 10
CdPose26Right:
 .byte 20
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 9, 1
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 9, 9
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 25, 1
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 25, 9
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $01, 14, 3
CdPose26Left:
 .byte 20
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $00, 9, -1
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, 9, 7
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 25, -1
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 25, 7
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $01, 14, 7
CdPose27Right:
 .byte 16
 .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 16, -2
 .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $00, 16, 6
 .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $00, 16, 14
 .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $01, 20, 0
CdPose27Left:
 .byte 16
 .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 16, -1
 .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $00, 16, 7
 .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $00, 16, 15
 .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $01, 20, 10
CdPose28Right:
 .byte 24
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 8, 0
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 8, 8
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 24, 0
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 24, 8
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 24, 16
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $01, 14, 2
CdPose28Left:
 .byte 24
 .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 8, -2
 .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 8, 6
 .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 8, 14
 .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 24, -2
 .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 24, 6
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $01, 14, 8
CdPose29Right:
 .byte 28
 .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 9, 0
 .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 9, 8
 .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 9, 16
 .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 25, 0
 .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 25, 8
 .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $00, 25, 16
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $01, 14, 2
CdPose29Left:
 .byte 24
 .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $00, 9, -2
 .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $00, 9, 6
 .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 9, 14
 .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $00, 25, -2
 .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $00, 25, 6
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $01, 14, 8
CdPose30Right:
 .byte 24
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 9, 1
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 9, 9
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 9, 17
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 25, 1
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 25, 9
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $01, 14, 3
CdPose30Left:
 .byte 24
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, 9, -2
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 9, 6
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 9, 14
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 25, -2
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 25, 6
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $01, 14, 7
CdPose31Right:
 .byte 28
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 9, 0
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 9, 8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 9, 16
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 25, 0
 .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 25, 8
 .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 25, 16
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $01, 14, 2
CdPose31Left:
 .byte 24
 .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 9, -1
 .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 9, 7
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 9, 15
 .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 25, -1
 .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 25, 7
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $01, 14, 8
CdPose32Right:
 .byte 24
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 9, 1
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 9, 9
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 9, 17
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 25, 1
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 25, 9
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $01, 14, 3
CdPose32Left:
 .byte 24
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, 9, -2
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 9, 6
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 9, 14
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 25, -2
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 25, 6
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $01, 14, 7
CdPose33Right:
 .byte 24
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 8, 0
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 8, 8
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 24, 0
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 24, 8
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 24, 16
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $01, 14, 2
CdPose33Left:
 .byte 24
 .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 8, -2
 .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 8, 6
 .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 8, 14
 .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 24, -2
 .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 24, 6
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $01, 14, 8
CdPose34Right:
 .byte 24
 .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 8, 1
 .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 8, 9
 .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 24, 1
 .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 24, 9
 .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $00, 24, 17
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $01, 14, 3
CdPose34Left:
 .byte 24
 .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $00, 8, -2
 .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $00, 8, 6
 .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 8, 14
 .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $00, 24, -2
 .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $00, 24, 6
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $01, 14, 7
CdPose35Right:
 .byte 24
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 8, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 8, 8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 24, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 24, 8
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 24, 16
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $01, 14, 2
CdPose35Left:
 .byte 24
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, 8, -1
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 8, 7
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 8, 15
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 24, -1
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 24, 7
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $01, 14, 8
CdPose36Right:
 .byte 24
 .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 8, 1
 .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 8, 9
 .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 24, 1
 .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 24, 9
 .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $00, 24, 17
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $01, 14, 3
CdPose36Left:
 .byte 24
 .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $00, 8, -2
 .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $00, 8, 6
 .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 8, 14
 .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $00, 24, -2
 .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $00, 24, 6
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $01, 14, 7
CdPose37Right:
 .byte 16
 .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 16, -2
 .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $00, 16, 6
 .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $00, 16, 14
 .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $01, 20, 0
CdPose37Left:
 .byte 16
 .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 16, -1
 .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $00, 16, 7
 .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $00, 16, 15
 .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $01, 20, 10
CdPose38Right:
 .byte 24
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 14, 0
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 14, 8
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 14, 16
 .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 30, 0
 .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 30, 8
 .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 30, 16
CdPose38Left:
 .byte 20
 .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 14, -2
 .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 14, 6
 .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 14, 14
 .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 30, -2
 .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 30, 6
CdPose39Right:
 .byte 28
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 9, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 9, 8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 9, 16
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 25, 0
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 25, 8
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $00, 25, 16
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $01, 14, 2
CdPose39Left:
 .byte 24
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 9, -2
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 9, 6
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 9, 14
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 25, -2
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 25, 6
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $01, 14, 8
CdPose40Right:
 .byte 24
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 8, 0
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 8, 8
 .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 24, 0
 .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 24, 8
 .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 24, 16
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $01, 14, 2
CdPose40Left:
 .byte 24
 .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 8, -2
 .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 8, 6
 .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 8, 14
 .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 24, -2
 .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 24, 6
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $01, 14, 8
CdPose41Right:
 .byte 20
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 8, 1
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 8, 9
 .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 24, 1
 .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 24, 9
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $01, 14, 3
CdPose41Left:
 .byte 20
 .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $00, 8, -1
 .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $00, 8, 7
 .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $00, 24, -1
 .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 24, 7
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $01, 14, 7
CdPose42Right:
 .byte 24
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 5, -9
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 5, -1
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 5, 7
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 21, -9
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 21, -1
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $01, 14, -7
CdPose42Left:
 .byte 24
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, 5, 2
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 5, 10
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 5, 18
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 21, 10
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 21, 18
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $01, 14, 17
CdPose43Right:
 .byte 20
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 8, 3
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 8, 11
 .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 24, 3
 .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 24, 11
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $01, 14, 5
CdPose43Left:
 .byte 20
 .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $00, 8, -3
 .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $00, 8, 5
 .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 24, -3
 .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 24, 5
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $01, 14, 5
CdPose44Right:
 .byte 24
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 5, -9
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 5, -1
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 5, 7
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 21, -9
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 21, -1
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $01, 14, -7
CdPose44Left:
 .byte 24
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, 5, 2
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 5, 10
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 5, 18
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 21, 10
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 21, 18
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $01, 14, 17
CdPose45Right:
 .byte 20
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 9, 0
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 9, 8
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 25, 0
 .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 25, 8
 .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $01, 17, 3
CdPose45Left:
 .byte 20
 .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 9, 0
 .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 9, 8
 .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 25, 0
 .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 25, 8
 .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $01, 17, 8
CdPose46Right:
 .byte 28
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 9, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 9, 8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 25, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 25, 8
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 25, 16
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $01, 1, 2
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $01, 17, 2
CdPose46Left:
 .byte 28
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 9, -1
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 9, 7
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 9, 15
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 25, -1
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 25, 7
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $01, 1, 6
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $01, 17, 6
CdPose47Right:
 .byte 28
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 9, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 9, 8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 25, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 25, 8
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 25, 16
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $01, -3, 10
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $01, 13, 2
CdPose47Left:
 .byte 28
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 9, -1
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 9, 7
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 9, 15
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 25, -1
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 25, 7
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $01, -3, -2
 .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $01, 13, 6
CdPose48Right:
 .byte 28
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 9, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 9, 8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 25, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 25, 8
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 25, 16
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $01, -7, 2
 .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $01, 9, 2
CdPose48Left:
 .byte 28
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 9, -1
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 9, 7
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 9, 15
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 25, -1
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 25, 7
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $01, -7, 6
 .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $01, 9, 6
CdPose49Right:
 .byte 32
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 9, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 9, 8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 25, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 25, 8
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 25, 16
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $01, -3, -3
 .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $01, 13, -3
 .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $01, 13, 5
CdPose49Left:
 .byte 32
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 9, -1
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 9, 7
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 9, 15
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 25, -1
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 25, 7
 .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $01, -3, 9
 .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $01, -3, 17
 .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $01, 13, 9
CdPose50Right:
 .byte 8
 .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 12, 0
 .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $00, 12, 8
CdPose50Left:
 .byte 8
 .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $00, 12, 0
 .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $00, 12, 8
CdPose51Right:
 .byte 8
 .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $01, 12, 0
 .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $01, 12, 8
CdPose51Left:
 .byte 8
 .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $01, 12, 0
 .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $01, 12, 8
CdPose52Right:
 .byte 8
 .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $00, 12, 0
 .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 12, 8
CdPose52Left:
 .byte 8
 .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $00, 12, 0
 .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $00, 12, 8
CdPose53Right:
 .byte 16
 .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $00, 20, 0
 .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 20, 8
 .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $01, 12, 0
 .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $01, 12, 8
CdPose53Left:
 .byte 16
 .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $00, 20, 0
 .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 20, 8
 .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $01, 12, 0
 .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $01, 12, 8
CdPose54Right:
 .byte 8
 .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 12, 8
 .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $01, 12, 0
CdPose54Left:
 .byte 8
 .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 12, 5
 .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $01, 12, 8
CdPose55Right:
 .byte 24
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 8, -4
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 8, 4
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 8, 12
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 24, -4
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 24, 4
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $00, 24, 12
CdPose55Left:
 .byte 24
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, 8, -4
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 8, 4
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 8, 12
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 24, -4
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 24, 4
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 24, 12
CdPose56Right:
 .byte 12
 .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $00, 12, 12
 .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $01, 12, 0
 .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $01, 12, 8
CdPose56Left:
 .byte 12
 .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $00, 12, 0
 .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $01, 12, 5
 .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $01, 12, 13
CdPose57Right:
 .byte 12
 .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 12, 8
 .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $01, 12, 0
 .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $01, 12, 8
CdPose57Left:
 .byte 12
 .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $00, 12, 0
 .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $01, 12, 5
 .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $01, 12, 13
CdPose58Right:
 .byte 12
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 12, 8
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $01, 12, 0
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $01, 12, 8
CdPose58Left:
 .byte 12
 .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 12, 0
 .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $01, 12, 0
 .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $01, 12, 8
CdPose59Right:
 .byte 12
 .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 12, 8
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $01, 12, 0
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $01, 12, 8
CdPose59Left:
 .byte 12
 .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 12, 0
 .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $01, 12, 0
 .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $01, 12, 8
CdPoseRightLo:
 .byte <CdPose0Right,<CdPose1Right,<CdPose2Right,<CdPose3Right,<CdPose4Right,<CdPose5Right,<CdPose6Right,<CdPose7Right,<CdPose8Right,<CdPose9Right,<CdPose10Right,<CdPose11Right,<CdPose12Right,<CdPose13Right,<CdPose14Right,<CdPose15Right,<CdPose16Right,<CdPose17Right,<CdPose18Right,<CdPose19Right,<CdPose20Right,<CdPose21Right,<CdPose22Right,<CdPose23Right,<CdPose24Right,<CdPose25Right,<CdPose26Right,<CdPose27Right,<CdPose28Right,<CdPose29Right,<CdPose30Right,<CdPose31Right,<CdPose32Right,<CdPose33Right,<CdPose34Right,<CdPose35Right,<CdPose36Right,<CdPose37Right,<CdPose38Right,<CdPose39Right,<CdPose40Right,<CdPose41Right,<CdPose42Right,<CdPose43Right,<CdPose44Right,<CdPose45Right,<CdPose46Right,<CdPose47Right,<CdPose48Right,<CdPose49Right,<CdPose50Right,<CdPose51Right,<CdPose52Right,<CdPose53Right,<CdPose54Right,<CdPose55Right,<CdPose56Right,<CdPose57Right,<CdPose58Right,<CdPose59Right
CdPoseRightHi:
 .byte >CdPose0Right,>CdPose1Right,>CdPose2Right,>CdPose3Right,>CdPose4Right,>CdPose5Right,>CdPose6Right,>CdPose7Right,>CdPose8Right,>CdPose9Right,>CdPose10Right,>CdPose11Right,>CdPose12Right,>CdPose13Right,>CdPose14Right,>CdPose15Right,>CdPose16Right,>CdPose17Right,>CdPose18Right,>CdPose19Right,>CdPose20Right,>CdPose21Right,>CdPose22Right,>CdPose23Right,>CdPose24Right,>CdPose25Right,>CdPose26Right,>CdPose27Right,>CdPose28Right,>CdPose29Right,>CdPose30Right,>CdPose31Right,>CdPose32Right,>CdPose33Right,>CdPose34Right,>CdPose35Right,>CdPose36Right,>CdPose37Right,>CdPose38Right,>CdPose39Right,>CdPose40Right,>CdPose41Right,>CdPose42Right,>CdPose43Right,>CdPose44Right,>CdPose45Right,>CdPose46Right,>CdPose47Right,>CdPose48Right,>CdPose49Right,>CdPose50Right,>CdPose51Right,>CdPose52Right,>CdPose53Right,>CdPose54Right,>CdPose55Right,>CdPose56Right,>CdPose57Right,>CdPose58Right,>CdPose59Right
CdPoseLeftLo:
 .byte <CdPose0Left,<CdPose1Left,<CdPose2Left,<CdPose3Left,<CdPose4Left,<CdPose5Left,<CdPose6Left,<CdPose7Left,<CdPose8Left,<CdPose9Left,<CdPose10Left,<CdPose11Left,<CdPose12Left,<CdPose13Left,<CdPose14Left,<CdPose15Left,<CdPose16Left,<CdPose17Left,<CdPose18Left,<CdPose19Left,<CdPose20Left,<CdPose21Left,<CdPose22Left,<CdPose23Left,<CdPose24Left,<CdPose25Left,<CdPose26Left,<CdPose27Left,<CdPose28Left,<CdPose29Left,<CdPose30Left,<CdPose31Left,<CdPose32Left,<CdPose33Left,<CdPose34Left,<CdPose35Left,<CdPose36Left,<CdPose37Left,<CdPose38Left,<CdPose39Left,<CdPose40Left,<CdPose41Left,<CdPose42Left,<CdPose43Left,<CdPose44Left,<CdPose45Left,<CdPose46Left,<CdPose47Left,<CdPose48Left,<CdPose49Left,<CdPose50Left,<CdPose51Left,<CdPose52Left,<CdPose53Left,<CdPose54Left,<CdPose55Left,<CdPose56Left,<CdPose57Left,<CdPose58Left,<CdPose59Left
CdPoseLeftHi:
 .byte >CdPose0Left,>CdPose1Left,>CdPose2Left,>CdPose3Left,>CdPose4Left,>CdPose5Left,>CdPose6Left,>CdPose7Left,>CdPose8Left,>CdPose9Left,>CdPose10Left,>CdPose11Left,>CdPose12Left,>CdPose13Left,>CdPose14Left,>CdPose15Left,>CdPose16Left,>CdPose17Left,>CdPose18Left,>CdPose19Left,>CdPose20Left,>CdPose21Left,>CdPose22Left,>CdPose23Left,>CdPose24Left,>CdPose25Left,>CdPose26Left,>CdPose27Left,>CdPose28Left,>CdPose29Left,>CdPose30Left,>CdPose31Left,>CdPose32Left,>CdPose33Left,>CdPose34Left,>CdPose35Left,>CdPose36Left,>CdPose37Left,>CdPose38Left,>CdPose39Left,>CdPose40Left,>CdPose41Left,>CdPose42Left,>CdPose43Left,>CdPose44Left,>CdPose45Left,>CdPose46Left,>CdPose47Left,>CdPose48Left,>CdPose49Left,>CdPose50Left,>CdPose51Left,>CdPose52Left,>CdPose53Left,>CdPose54Left,>CdPose55Left,>CdPose56Left,>CdPose57Left,>CdPose58Left,>CdPose59Left
CdPoseChrLo:
 .byte .lobyte(412),.lobyte(412),.lobyte(412),.lobyte(412),.lobyte(413),.lobyte(413),.lobyte(413),.lobyte(413),.lobyte(412),.lobyte(414),.lobyte(414),.lobyte(414),.lobyte(412),.lobyte(414),.lobyte(415),.lobyte(415),.lobyte(415),.lobyte(416),.lobyte(415),.lobyte(416),.lobyte(416),.lobyte(417),.lobyte(417),.lobyte(417),.lobyte(417),.lobyte(416),.lobyte(418),.lobyte(416),.lobyte(418),.lobyte(418),.lobyte(419),.lobyte(419),.lobyte(419),.lobyte(418),.lobyte(419),.lobyte(420),.lobyte(419),.lobyte(416),.lobyte(420),.lobyte(421),.lobyte(421),.lobyte(420),.lobyte(422),.lobyte(421),.lobyte(422),.lobyte(422),.lobyte(423),.lobyte(423),.lobyte(423),.lobyte(423),.lobyte(414),.lobyte(417),.lobyte(417),.lobyte(421),.lobyte(422),.lobyte(424),.lobyte(422),.lobyte(423),.lobyte(424),.lobyte(424)
CdPoseChrHi:
 .byte .hibyte(412),.hibyte(412),.hibyte(412),.hibyte(412),.hibyte(413),.hibyte(413),.hibyte(413),.hibyte(413),.hibyte(412),.hibyte(414),.hibyte(414),.hibyte(414),.hibyte(412),.hibyte(414),.hibyte(415),.hibyte(415),.hibyte(415),.hibyte(416),.hibyte(415),.hibyte(416),.hibyte(416),.hibyte(417),.hibyte(417),.hibyte(417),.hibyte(417),.hibyte(416),.hibyte(418),.hibyte(416),.hibyte(418),.hibyte(418),.hibyte(419),.hibyte(419),.hibyte(419),.hibyte(418),.hibyte(419),.hibyte(420),.hibyte(419),.hibyte(416),.hibyte(420),.hibyte(421),.hibyte(421),.hibyte(420),.hibyte(422),.hibyte(421),.hibyte(422),.hibyte(422),.hibyte(423),.hibyte(423),.hibyte(423),.hibyte(423),.hibyte(414),.hibyte(417),.hibyte(417),.hibyte(421),.hibyte(422),.hibyte(424),.hibyte(422),.hibyte(423),.hibyte(424),.hibyte(424)
CdAnim1:
 .byte 0,1
CdAnim2:
 .byte 2,3
CdAnim3:
 .byte 4,5,6,7
CdAnim4:
 .byte 8,9,10,11
CdAnim5:
 .byte 12
CdAnim6:
 .byte 13
CdAnim7:
 .byte 14
CdAnim8:
 .byte 15
CdAnim9:
 .byte 16,17
CdAnim10:
 .byte 18,19
CdAnim11:
 .byte 20
CdAnim12:
 .byte 21,22,23,24
CdAnim13:
 .byte 25,26
CdAnim14:
 .byte 27,28
CdAnim15:
 .byte 29,30,31,32
CdAnim16:
 .byte 33,34,35,36
CdAnim17:
 .byte 37
CdAnim18:
 .byte 38
CdAnim19:
 .byte 39
CdAnim20:
 .byte 40
CdAnim21:
 .byte 41,42
CdAnim22:
 .byte 43,44
CdAnim23:
 .byte 45
CdAnim24:
 .byte 46,47,48,49
CdAnim34:
 .byte 50
CdAnim35:
 .byte 51
CdAnim36:
 .byte 52
CdAnim37:
 .byte 53,54
CdAnim38:
 .byte 55
CdAnim39:
 .byte 56,57
CdAnim40:
 .byte 58,59
CdAnimFirst:
 .byte 0,0,2,4,8,12,13,14,15,16,18,20,21,25,27,29,33,37,38,39,40,41,43,45,46,0,0,0,0,0,0,0,0,0,50,51,52,53,55,56,58
CdAnimLength:
 .byte 0,2,2,4,4,1,1,1,1,2,2,1,4,2,2,4,4,1,1,1,1,2,2,1,4,0,0,0,0,0,0,0,0,0,1,1,1,2,1,2,2
CdAnimRate:
 .byte 8,6,6,6,6,8,8,8,8,4,4,8,4,6,6,6,6,8,8,8,8,4,4,8,4,8,8,8,8,8,8,8,8,8,8,8,8,8,8,4,4
CdWorldChr=425
.export CdWorldChr
CdBoxWood:
 .byte 8
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_4}, $00, 0, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_4}, $00, 0, 8
CdBoxMetal:
 .byte 8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_4}, $01, 0, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_4}, $01, 0, 8
CdBoxApple:
 .byte 24
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_4}, $00, -4, -4
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_4}, $00, -4, 4
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_4}, $00, -4, 12
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_4}, $00, 12, -4
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_4}, $00, 12, 4
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_4}, $00, 12, 12
.popseg
