; Source-native running masks; explicitly authored source-pixel SMB composites.
.pushseg
.segment "LM_GFX"
LmArtBegin:
Lp0R:
 .byte 24
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, 0, -16, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, 0, 0, 0
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, 0, 16, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, 0, -16, 8
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, 0, 0, 8
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, 0, 16, 8
Lp0L:
 .byte 24
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, 0, -16, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, 0, 0, 0
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, 0, 16, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, 0, -16, 8
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, 0, 0, 8
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, 0, 16, 8
Lp1R:
 .byte 24
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, 0, -16, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, 0, 0, 0
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, 0, 16, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, 0, -16, 8
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, 0, 0, 8
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, 0, 16, 8
Lp1L:
 .byte 24
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, 0, -16, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, 0, 0, 0
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, 0, 16, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, 0, -16, 8
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, 0, 0, 8
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, 0, 16, 8
Lp2R:
 .byte 24
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, 0, -16, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, 0, 0, 0
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, 0, 16, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, 0, -16, 8
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, 0, 0, 8
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, 0, 16, 8
Lp2L:
 .byte 24
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, 0, -16, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, 0, 0, 0
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, 0, 16, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, 0, -16, 8
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, 0, 0, 8
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, 0, 16, 8
Lp3R:
 .byte 32
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, 0, 0, -8
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, 0, 16, -8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, 0, 0, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, 0, 16, 0
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, 0, 0, 8
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, 0, 16, 8
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, 0, 0, 16
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, 0, 16, 16
Lp3L:
 .byte 32
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, 0, 0, -8
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, 0, 16, -8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, 0, 0, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, 0, 16, 0
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, 0, 0, 8
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, 0, 16, 8
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, 0, 0, 16
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, 0, 16, 16
Lp4R:
 .byte 32
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, 0, -16, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, 0, 0, 0
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, 0, 16, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, 0, -16, 8
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, 0, 0, 8
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, 0, 16, 8
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, 0, 0, 16
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, 0, 0, 24
Lp4L:
 .byte 32
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, 0, 0, -16
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, 0, 0, -8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, 0, -16, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, 0, 0, 0
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, 0, 16, 0
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, 0, -16, 8
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, 0, 0, 8
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, 0, 16, 8
Lp5R:
 .byte 36
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, 0, -16, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, 0, 0, 0
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, 0, 16, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, 0, -32, 8
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, 0, -16, 8
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, 0, 0, 8
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, 0, 16, 8
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, 0, -32, 16
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, 0, -16, 16
Lp5L:
 .byte 36
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, 0, -32, -8
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, 0, -16, -8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, 0, -32, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, 0, -16, 0
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, 0, 0, 0
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, 0, 16, 0
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, 0, -16, 8
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, 0, 0, 8
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, 0, 16, 8
Lp6R:
 .byte 24
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, 0, -16, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, 0, 0, 0
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, 0, 16, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, 0, -16, 8
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, 0, 0, 8
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, 0, 16, 8
Lp6L:
 .byte 24
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, 0, -16, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, 0, 0, 0
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, 0, 16, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, 0, -16, 8
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, 0, 0, 8
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, 0, 16, 8
Lp7R:
 .byte 32
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, 0, 0, -8
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, 0, 16, -8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, 0, 0, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, 0, 16, 0
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, 0, 0, 8
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, 0, 16, 8
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, 0, 0, 16
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, 0, 16, 16
Lp7L:
 .byte 32
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, 0, 0, -8
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, 0, 16, -8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, 0, 0, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, 0, 16, 0
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, 0, 0, 8
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, 0, 16, 8
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, 0, 0, 16
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, 0, 16, 16
Lp8R:
 .byte 36
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, 0, 0, -8
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, 0, 16, -8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, 0, 0, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, 0, 16, 0
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, 0, 0, 8
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, 0, 16, 8
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, 0, 0, 16
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, 0, 16, 16
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, 0, 16, 24
Lp8L:
 .byte 36
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, 0, 16, -16
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, 0, 0, -8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, 0, 16, -8
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, 0, 0, 0
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, 0, 16, 0
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, 0, 0, 8
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, 0, 16, 8
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, 0, 0, 16
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, 0, 16, 16
Lp9R:
 .byte 40
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, 0, 0, -8
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, 0, 16, -8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, 0, 0, 0
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, 0, 16, 0
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, 0, -16, 8
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, 0, 0, 8
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, 0, 16, 8
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, 0, -16, 16
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, 0, 0, 16
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, 0, 16, 16
Lp9L:
 .byte 40
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, 0, -16, -8
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, 0, 0, -8
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, 0, 16, -8
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, 0, -16, 0
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, 0, 0, 0
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, 0, 16, 0
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, 0, 0, 8
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, 0, 16, 8
 .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, 0, 0, 16
 .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, 0, 16, 16
LmPoseRLo:
 .byte <Lp0R,<Lp1R,<Lp2R,<Lp3R,<Lp4R,<Lp5R,<Lp6R,<Lp7R,<Lp8R,<Lp9R
LmPoseRHi:
 .byte >Lp0R,>Lp1R,>Lp2R,>Lp3R,>Lp4R,>Lp5R,>Lp6R,>Lp7R,>Lp8R,>Lp9R
LmChrR:
 .byte 156,158,160,162,164,166,168,170,172,174
LmPoseLLo:
 .byte <Lp0L,<Lp1L,<Lp2L,<Lp3L,<Lp4L,<Lp5L,<Lp6L,<Lp7L,<Lp8L,<Lp9L
LmPoseLHi:
 .byte >Lp0L,>Lp1L,>Lp2L,>Lp3L,>Lp4L,>Lp5L,>Lp6L,>Lp7L,>Lp8L,>Lp9L
LmChrL:
 .byte 157,159,161,163,165,167,169,171,173,175
LmStar:
 .byte 8
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_4}, 2, -6, 0
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_4}, 2, -6, 8
.popseg
