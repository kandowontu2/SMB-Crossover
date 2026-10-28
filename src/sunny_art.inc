; Exact Super Sunny World RC1 supplied-ROM pixels; Matt Hughson / Kenneth Fejer.
; Native8x8 records repacked losslessly to host8x16; +12Y anchor translation.
.pushseg
.segment "SUNNY_ART"
SunnyArtBegin:
SunnyFrame0R:
 .byte 8
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 16, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 16, 8
SunnyFrame0L:
 .byte 8
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, 16, 8
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, 16, 0
SunnyFrame1R:
 .byte 8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 17, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 17, 8
SunnyFrame1L:
 .byte 8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $40, 17, 8
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $40, 17, 0
SunnyFrame2R:
 .byte 8
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 16, 1
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $00, 16, 9
SunnyFrame2L:
 .byte 8
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $40, 16, 7
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $40, 16, -1
SunnyFrame3R:
 .byte 8
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, 16, 0
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 16, 8
SunnyFrame3L:
 .byte 8
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $40, 16, 8
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $40, 16, 0
SunnyFrame4R:
 .byte 8
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 16, 0
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 16, 8
SunnyFrame4L:
 .byte 8
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $40, 16, 8
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $40, 16, 0
SunnyFrame5R:
 .byte 8
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 16, 0
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 16, 8
SunnyFrame5L:
 .byte 8
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $40, 16, 8
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $40, 16, 0
SunnyFrame6R:
 .byte 8
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 16, 2
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 16, 10
SunnyFrame6L:
 .byte 8
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $40, 16, 6
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $40, 16, -2
SunnyFrame7R:
 .byte 8
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 16, 0
 .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 16, 8
SunnyFrame7L:
 .byte 8
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $40, 16, 8
 .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $40, 16, 0
SunnyFrame8R:
 .byte 8
 .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 16, 0
 .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 16, 8
SunnyFrame8L:
 .byte 8
 .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 16, 8
 .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $40, 16, 0
SunnyFrame9R:
 .byte 4
 .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, -1, -12
SunnyFrame9L:
 .byte 4
 .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $40, -1, 20
SunnyFrame10R:
 .byte 8
 .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 16, 0
 .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 16, 8
SunnyFrame10L:
 .byte 8
 .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 16, 8
 .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, 16, 0
SunnyFrame11R:
 .byte 8
 .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 16, 0
 .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 16, 8
SunnyFrame11L:
 .byte 8
 .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, 16, 8
 .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $40, 16, 0
SunnyFrame12R:
 .byte 8
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, 16, 0
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 16, 8
SunnyFrame12L:
 .byte 8
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $40, 16, 8
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $40, 16, 0
SunnyFrame13R:
 .byte 8
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 16, 0
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 16, 8
SunnyFrame13L:
 .byte 8
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $40, 16, 8
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $40, 16, 0
SunnyFrame14R:
 .byte 8
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 16, 0
 .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 16, 8
SunnyFrame14L:
 .byte 8
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $40, 16, 8
 .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $40, 16, 0
SunnyFrame15R:
 .byte 8
 .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 16, 1
 .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 16, 9
SunnyFrame15L:
 .byte 8
 .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $40, 16, 7
 .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $40, 16, -1
SunnyFrame16R:
 .byte 8
 .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $00, 16, 2
 .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $00, 16, 10
SunnyFrame16L:
 .byte 8
 .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $40, 16, 6
 .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $40, 16, -2
SunnyFrame17R:
 .byte 16
 .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $00, 9, 0
 .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 9, 8
 .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $00, 25, 0
 .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $00, 25, 8
SunnyFrame17L:
 .byte 16
 .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $40, 9, 8
 .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $40, 9, 0
 .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $40, 25, 8
 .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $40, 25, 0
SunnyFrame18R:
 .byte 16
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 10, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 10, 8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 26, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 26, 8
SunnyFrame18L:
 .byte 16
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, 10, 8
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, 10, 0
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $40, 26, 8
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $40, 26, 0
SunnyFrame19R:
 .byte 16
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 9, 0
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $00, 9, 8
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, 25, 0
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 25, 8
SunnyFrame19L:
 .byte 16
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $40, 9, 8
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $40, 9, 0
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $40, 25, 8
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $40, 25, 0
SunnyFrame20R:
 .byte 16
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 9, 0
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 9, 8
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 25, 0
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 25, 8
SunnyFrame20L:
 .byte 16
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $40, 9, 8
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $40, 9, 0
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $40, 25, 8
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $40, 25, 0
SunnyFrame21R:
 .byte 16
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 8, 0
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 8, 8
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 24, 0
 .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 24, 8
SunnyFrame21L:
 .byte 16
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $40, 8, 8
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $40, 8, 0
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $40, 24, 8
 .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $40, 24, 0
SunnyFrame22R:
 .byte 16
 .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 9, 0
 .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 9, 8
 .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 25, 0
 .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 25, 8
SunnyFrame22L:
 .byte 16
 .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 9, 8
 .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $40, 9, 0
 .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $40, 25, 8
 .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 25, 0
SunnyFrame23R:
 .byte 16
 .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 8, 0
 .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 8, 8
 .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 24, 0
 .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 24, 8
SunnyFrame23L:
 .byte 16
 .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, 8, 8
 .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, 8, 0
 .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $40, 24, 8
 .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $40, 24, 0
SunnyFrame24R:
 .byte 16
 .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 10, 0
 .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $00, 10, 8
 .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $00, 26, 0
 .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $00, 26, 8
SunnyFrame24L:
 .byte 16
 .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $40, 10, 8
 .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $40, 10, 0
 .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $40, 26, 8
 .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $40, 26, 0
SunnyFrame25R:
 .byte 16
 .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 9, 0
 .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $00, 9, 8
 .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $00, 25, 0
 .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $00, 25, 8
SunnyFrame25L:
 .byte 16
 .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $40, 9, 8
 .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $40, 9, 0
 .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $40, 25, 8
 .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $40, 25, 0
SunnyFrame26R:
 .byte 8
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 16, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 16, 8
SunnyFrame26L:
 .byte 8
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, 16, 8
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, 16, 0
SunnyFrame27R:
 .byte 16
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 9, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 9, 8
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 25, 0
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $00, 25, 8
SunnyFrame27L:
 .byte 16
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $40, 9, 8
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $40, 9, 0
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $40, 25, 8
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $40, 25, 0
SunnyFrame28R:
 .byte 16
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, 8, 0
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 8, 8
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 24, 0
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 24, 8
SunnyFrame28L:
 .byte 16
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $40, 8, 8
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $40, 8, 0
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $40, 24, 8
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $40, 24, 0
SunnyFrame29R:
 .byte 16
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 9, 0
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 9, 8
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 25, 0
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 25, 8
SunnyFrame29L:
 .byte 16
 .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $40, 9, 8
 .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $40, 9, 0
 .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $40, 25, 8
 .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $40, 25, 0
SunnyFrame30R:
 .byte 16
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 9, 0
 .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 9, 8
 .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 25, 0
 .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 25, 8
SunnyFrame30L:
 .byte 16
 .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $40, 9, 8
 .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $40, 9, 0
 .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 25, 8
 .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $40, 25, 0
SunnyFrame31R:
 .byte 16
 .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 8, 0
 .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 8, 8
 .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 24, 0
 .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 24, 8
SunnyFrame31L:
 .byte 16
 .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $40, 8, 8
 .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 8, 0
 .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, 24, 8
 .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, 24, 0
SunnyFrame32R:
 .byte 16
 .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 8, 0
 .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 8, 8
 .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 24, 0
 .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $00, 24, 8
SunnyFrame32L:
 .byte 16
 .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $40, 8, 8
 .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $40, 8, 0
 .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $40, 24, 8
 .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $40, 24, 0
SunnyFrame33R:
 .byte 20
 .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $00, 12, -3
 .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $00, 12, 5
 .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 12, 13
 .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $00, 28, -3
 .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $00, 28, 5
SunnyFrame33L:
 .byte 20
 .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $40, 12, 11
 .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $40, 12, 3
 .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $40, 12, -5
 .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $40, 28, 11
 .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $40, 28, 3
SunnyFrame34R:
 .byte 20
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 12, -3
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 12, 5
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 12, 13
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 28, -3
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 28, 5
SunnyFrame34L:
 .byte 20
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, 12, 11
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, 12, 3
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $40, 12, -5
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $40, 28, 11
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $40, 28, 3
SunnyRLo:
 .byte <SunnyFrame0R,<SunnyFrame1R,<SunnyFrame2R,<SunnyFrame3R,<SunnyFrame4R,<SunnyFrame5R,<SunnyFrame6R,<SunnyFrame7R,<SunnyFrame8R,<SunnyFrame9R,<SunnyFrame10R,<SunnyFrame11R,<SunnyFrame12R,<SunnyFrame13R,<SunnyFrame14R,<SunnyFrame15R,<SunnyFrame16R,<SunnyFrame17R,<SunnyFrame18R,<SunnyFrame19R,<SunnyFrame20R,<SunnyFrame21R,<SunnyFrame22R,<SunnyFrame23R,<SunnyFrame24R,<SunnyFrame25R,<SunnyFrame26R,<SunnyFrame27R,<SunnyFrame28R,<SunnyFrame29R,<SunnyFrame30R,<SunnyFrame31R,<SunnyFrame32R,<SunnyFrame33R,<SunnyFrame34R
SunnyRHi:
 .byte >SunnyFrame0R,>SunnyFrame1R,>SunnyFrame2R,>SunnyFrame3R,>SunnyFrame4R,>SunnyFrame5R,>SunnyFrame6R,>SunnyFrame7R,>SunnyFrame8R,>SunnyFrame9R,>SunnyFrame10R,>SunnyFrame11R,>SunnyFrame12R,>SunnyFrame13R,>SunnyFrame14R,>SunnyFrame15R,>SunnyFrame16R,>SunnyFrame17R,>SunnyFrame18R,>SunnyFrame19R,>SunnyFrame20R,>SunnyFrame21R,>SunnyFrame22R,>SunnyFrame23R,>SunnyFrame24R,>SunnyFrame25R,>SunnyFrame26R,>SunnyFrame27R,>SunnyFrame28R,>SunnyFrame29R,>SunnyFrame30R,>SunnyFrame31R,>SunnyFrame32R,>SunnyFrame33R,>SunnyFrame34R
SunnyLLo:
 .byte <SunnyFrame0L,<SunnyFrame1L,<SunnyFrame2L,<SunnyFrame3L,<SunnyFrame4L,<SunnyFrame5L,<SunnyFrame6L,<SunnyFrame7L,<SunnyFrame8L,<SunnyFrame9L,<SunnyFrame10L,<SunnyFrame11L,<SunnyFrame12L,<SunnyFrame13L,<SunnyFrame14L,<SunnyFrame15L,<SunnyFrame16L,<SunnyFrame17L,<SunnyFrame18L,<SunnyFrame19L,<SunnyFrame20L,<SunnyFrame21L,<SunnyFrame22L,<SunnyFrame23L,<SunnyFrame24L,<SunnyFrame25L,<SunnyFrame26L,<SunnyFrame27L,<SunnyFrame28L,<SunnyFrame29L,<SunnyFrame30L,<SunnyFrame31L,<SunnyFrame32L,<SunnyFrame33L,<SunnyFrame34L
SunnyLHi:
 .byte >SunnyFrame0L,>SunnyFrame1L,>SunnyFrame2L,>SunnyFrame3L,>SunnyFrame4L,>SunnyFrame5L,>SunnyFrame6L,>SunnyFrame7L,>SunnyFrame8L,>SunnyFrame9L,>SunnyFrame10L,>SunnyFrame11L,>SunnyFrame12L,>SunnyFrame13L,>SunnyFrame14L,>SunnyFrame15L,>SunnyFrame16L,>SunnyFrame17L,>SunnyFrame18L,>SunnyFrame19L,>SunnyFrame20L,>SunnyFrame21L,>SunnyFrame22L,>SunnyFrame23L,>SunnyFrame24L,>SunnyFrame25L,>SunnyFrame26L,>SunnyFrame27L,>SunnyFrame28L,>SunnyFrame29L,>SunnyFrame30L,>SunnyFrame31L,>SunnyFrame32L,>SunnyFrame33L,>SunnyFrame34L
SunnyChrLow:
 .byte 212,212,212,212,212,212,212,212,212,212,212,212,212,212,212,212,212,212,213,213,213,213,213,213,213,213,214,214,214,214,214,214,214,214,215
SunnySemanticSmall:
 .byte 0,3,4,3,2,5,5,10,12,13,12,15,16,6,8,0,0
SunnySemanticBig:
 .byte 17,20,21,22,19,23,24,33,27,28,29,31,32,25,30,17,17
SunnyArtEnd:
.assert SunnyArtEnd-SunnyArtBegin<=$1200,error,"Sunny C94 CE00..DFFF overflow"
.popseg
