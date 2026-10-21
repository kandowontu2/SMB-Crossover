; Generated from the pinned hosted Samus sprites; see docs/reference/samus.json.
.pushseg
.segment "SAMUS_GFX"
SmP0_STANDLeft:
  .byte 44
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $40, 0, 8
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 0, 0
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 0, -8
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $40, 16, 8
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $80, 16, 0
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $07, -16, 1
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $47, 0, 9
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $47, 0, 1
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $07, 0, -7
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $47, 16, 9
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $47, 16, 1
SmP0_STANDRight:
  .byte 44
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 0, 0
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $40, 0, 8
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $40, 0, 16
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 16, 0
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $c0, 16, 8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $47, -16, 7
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $07, 0, -1
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $07, 0, 7
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $47, 0, 15
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $07, 16, -1
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $07, 16, 7
SmP0_SHOOTLeft:
  .byte 44
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $40, 0, 8
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 0, 0
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 0, -8
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $40, 16, 8
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $80, 16, 0
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $07, -16, 1
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $47, 0, 9
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $47, 0, 1
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $07, 0, -7
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $47, 16, 9
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $47, 16, 1
SmP0_SHOOTRight:
  .byte 44
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 0, 0
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $40, 0, 8
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $40, 0, 16
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 16, 0
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $c0, 16, 8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $47, -16, 7
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $07, 0, -1
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $07, 0, 7
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $47, 0, 15
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $07, 16, -1
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $07, 16, 7
SmP0_WALK1Left:
  .byte 36
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $40, 1, 8
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $80, 1, 0
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c0, 17, 8
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $80, 17, 0
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $47, 0, 9
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c7, 0, 1
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $87, 0, -7
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $87, 16, 9
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $87, 16, 1
SmP0_WALK1Right:
  .byte 36
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 1, 0
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c0, 1, 8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $80, 17, 0
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c0, 17, 8
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $07, 0, -1
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $87, 0, 7
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c7, 0, 15
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c7, 16, -1
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $c7, 16, 7
SmP0_WALK2Left:
  .byte 48
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $40, 0, 6
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 0, -2
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $40, 16, 14
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $80, 16, 6
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $80, 16, -2
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $47, -1, 11
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c7, -1, 3
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $07, -1, -5
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $47, 15, 11
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c7, 15, 3
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $87, 15, -5
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $87, 31, 11
SmP0_WALK2Right:
  .byte 48
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 0, 2
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $40, 0, 10
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 16, -6
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $c0, 16, 2
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c0, 16, 10
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $07, -1, -3
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $87, -1, 5
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $47, -1, 13
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $07, 15, -3
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $87, 15, 5
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c7, 15, 13
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c7, 31, -3
SmP0_WALK3Left:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, 0, 8
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $80, 0, 0
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $c0, 16, 16
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c0, 16, 8
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 16, 0
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $47, -1, 9
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $07, -1, 1
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $87, -1, -7
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c7, 15, 17
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c7, 15, 9
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c7, 15, 1
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $87, 31, 1
SmP0_WALK3Right:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 0, 0
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $c0, 0, 8
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $80, 16, -8
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $80, 16, 0
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $40, 16, 8
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $07, -1, -1
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $47, -1, 7
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c7, -1, 15
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $87, 15, -9
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $87, 15, -1
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $87, 15, 7
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c7, 31, 7
SmP0_WALKSHOOT1Left:
  .byte 40
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $40, 1, 8
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $80, 1, 0
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 1, -8
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c0, 17, 8
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $80, 17, 0
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $47, 0, 9
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $87, 0, 1
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $07, 0, -7
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $87, 16, 9
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $87, 16, 1
SmP0_WALKSHOOT1Right:
  .byte 40
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 1, 0
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c0, 1, 8
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $40, 1, 16
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $80, 17, 0
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c0, 17, 8
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $07, 0, -1
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c7, 0, 7
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $47, 0, 15
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c7, 16, -1
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c7, 16, 7
SmP0_WALKSHOOT2Left:
  .byte 48
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $40, 1, 10
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 1, 2
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $80, 1, -6
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $80, 17, 10
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $c0, 17, 2
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $80, 17, -6
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $47, 0, 11
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c7, 0, 3
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $07, 0, -5
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $47, 16, 11
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c7, 16, 3
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $87, 16, -5
SmP0_WALKSHOOT2Right:
  .byte 48
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 1, -2
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $40, 1, 6
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c0, 1, 14
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c0, 17, -2
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $80, 17, 6
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c0, 17, 14
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $07, 0, -3
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $87, 0, 5
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $47, 0, 13
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $07, 16, -3
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $87, 16, 5
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c7, 16, 13
SmP0_WALKSHOOT3Left:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, 1, 6
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $80, 1, -2
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 1, -10
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c0, 17, 14
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c0, 17, 6
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $00, 17, -2
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $47, 0, 7
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $87, 0, -1
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $07, 0, -9
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c7, 16, 15
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c7, 16, 7
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $07, 16, -1
SmP0_WALKSHOOT3Right:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 1, 2
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $c0, 1, 10
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $40, 1, 18
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $80, 17, -6
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $80, 17, 2
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $40, 17, 10
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $07, 0, 1
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c7, 0, 9
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $47, 0, 17
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $87, 16, -7
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $87, 16, 1
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $47, 16, 9
SmP0_UPSTANDLeft:
  .byte 44
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, -16, 1
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $c0, 0, 9
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $80, 0, 1
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $40, 16, 9
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c0, 16, 1
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $47, -7, 9
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $07, -7, 1
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c7, 9, 9
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c7, 9, 1
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c7, 25, 9
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c7, 25, 1
SmP0_UPSTANDRight:
  .byte 44
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, -16, 7
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $80, 0, -1
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $c0, 0, 7
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 16, -1
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $80, 16, 7
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $07, -7, -1
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $47, -7, 7
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $87, 9, -1
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $87, 9, 7
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $87, 25, -1
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $87, 25, 7
SmP0_UPSHOOTLeft:
  .byte 44
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, -16, 1
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $c0, 0, 9
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 0, 1
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $40, 16, 9
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c0, 16, 1
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $47, -5, 9
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $07, -5, 1
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $47, 11, 9
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $47, 11, 1
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c7, 27, 9
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c7, 27, 1
SmP0_UPSHOOTRight:
  .byte 44
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $40, -16, 7
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $80, 0, -1
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $40, 0, 7
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 16, -1
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $80, 16, 7
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $07, -5, -1
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $47, -5, 7
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $07, 11, -1
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $07, 11, 7
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $87, 27, -1
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $87, 27, 7
SmP0_UPWALK1Left:
  .byte 40
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, -6, 8
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, -6, 0
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $40, 10, 8
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 10, 0
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c0, 26, 8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $07, -16, 3
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c7, 0, 11
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $47, 0, 3
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $47, 16, 11
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $87, 16, 3
SmP0_UPWALK1Right:
  .byte 40
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, -6, 0
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $40, -6, 8
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 10, 0
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 10, 8
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $80, 26, 0
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $47, -16, 5
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $87, 0, -3
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $07, 0, 5
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $07, 16, -3
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c7, 16, 5
SmP0_UPWALK2Left:
  .byte 52
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, -6, 10
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, -6, 2
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $40, 10, 10
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c0, 10, 2
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 10, -6
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $80, 26, 10
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $47, -9, 8
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $07, -9, 0
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $07, 7, 8
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $07, 7, 0
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c7, 23, 16
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $87, 23, 8
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c7, 23, 0
SmP0_UPWALK2Right:
  .byte 52
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, -6, -2
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, -6, 6
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 10, -2
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $80, 10, 6
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $40, 10, 14
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $c0, 26, -2
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $07, -9, 0
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $47, -9, 8
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $47, 7, 0
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $47, 7, 8
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $87, 23, -8
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c7, 23, 0
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $87, 23, 8
SmP0_UPWALK3Left:
  .byte 52
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, -6, 10
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, -6, 2
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $40, 10, 18
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c0, 10, 10
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 10, 2
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $c0, 26, 2
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $47, -7, 8
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $07, -7, 0
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $47, 9, 16
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $07, 9, 8
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $07, 9, 0
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c7, 25, 8
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $87, 25, 0
SmP0_UPWALK3Right:
  .byte 52
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, -6, -2
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, -6, 6
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 10, -10
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $80, 10, -2
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $40, 10, 6
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $80, 26, 6
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $07, -7, 0
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $47, -7, 8
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $07, 9, -8
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $47, 9, 0
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $47, 9, 8
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $87, 25, 0
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c7, 25, 8
SmP0_UPWALKSHOOT1Left:
  .byte 40
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, -4, 8
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, -4, 0
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $40, 12, 8
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $80, 12, 0
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c0, 28, 8
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $07, -16, 3
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $c7, 0, 11
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $47, 0, 3
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $47, 16, 11
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $87, 16, 3
SmP0_UPWALKSHOOT1Right:
  .byte 40
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, -4, 0
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, -4, 8
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 12, 0
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c0, 12, 8
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $80, 28, 0
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $47, -16, 5
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $87, 0, -3
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $07, 0, 5
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $07, 16, -3
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c7, 16, 5
SmP0_UPWALKSHOOT2Left:
  .byte 48
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $40, -4, 10
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, -4, 2
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $40, 12, 10
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c0, 12, 2
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 12, -6
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $80, 28, 10
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $47, -5, 11
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c7, -5, 3
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $47, 11, 11
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $47, 11, 3
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $07, 11, -5
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $87, 27, 11
SmP0_UPWALKSHOOT2Right:
  .byte 48
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, -4, -2
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $40, -4, 6
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 12, -2
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $80, 12, 6
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 12, 14
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c0, 28, -2
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $07, -5, -3
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $87, -5, 5
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $07, 11, -3
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $07, 11, 5
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $47, 11, 13
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c7, 27, -3
SmP0_UPWALKSHOOT3Left:
  .byte 52
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, -4, 10
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, -4, 2
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $40, 12, 18
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c0, 12, 10
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 12, 2
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $c0, 28, 2
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $47, -5, 8
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $07, -5, 0
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $47, 11, 16
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c7, 11, 8
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $07, 11, 0
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c7, 27, 8
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $87, 27, 0
SmP0_UPWALKSHOOT3Right:
  .byte 52
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, -4, -2
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, -4, 6
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 12, -10
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $80, 12, -2
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $40, 12, 6
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $80, 28, 6
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $07, -5, 0
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $47, -5, 8
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $07, 11, -8
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $87, 11, 0
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $47, 11, 8
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $87, 27, 0
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c7, 27, 8
SmP0_JUMPLeft:
  .byte 40
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $40, 5, 5
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $80, 5, -3
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c0, 21, 13
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $c0, 21, 5
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $80, 21, -3
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $47, 4, 6
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $07, 4, -2
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c7, 20, 14
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c7, 20, 6
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $87, 20, -2
SmP0_JUMPRight:
  .byte 40
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 5, 3
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c0, 5, 11
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $80, 21, -5
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $80, 21, 3
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c0, 21, 11
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $07, 4, 2
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $47, 4, 10
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $87, 20, -6
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $87, 20, 2
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c7, 20, 10
SmP0_JUMPSHOOTLeft:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, 6, 11
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, 6, 3
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 6, -5
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c0, 22, 11
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c0, 22, 3
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $80, 22, -5
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $47, 5, 7
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $07, 5, -1
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $07, 5, -9
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c7, 21, 15
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c7, 21, 7
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $87, 21, -1
SmP0_JUMPSHOOTRight:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 6, -3
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 6, 5
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $40, 6, 13
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $80, 22, -3
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $80, 22, 5
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $c0, 22, 13
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $07, 5, 1
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $47, 5, 9
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $47, 5, 17
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $87, 21, -7
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $87, 21, 1
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c7, 21, 9
SmP0_UPJUMPLeft:
  .byte 44
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, -1, 11
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, -1, 3
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c0, 15, 11
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 15, 3
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 15, -5
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $47, -2, 8
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $07, -2, 0
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $47, 14, 16
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $07, 14, 8
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $07, 14, 0
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c7, 30, 0
SmP0_UPJUMPRight:
  .byte 44
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, -1, -3
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, -1, 5
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $80, 15, -3
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 15, 5
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $40, 15, 13
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $07, -2, 0
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $47, -2, 8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $07, 14, -8
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $47, 14, 0
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $47, 14, 8
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $87, 30, 8
SmP0_UPJUMPSHOOTLeft:
  .byte 40
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, 1, 11
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 1, 3
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 17, 11
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 17, 3
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 17, -5
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $47, 0, 8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $07, 0, 0
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $47, 16, 16
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c7, 16, 8
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $07, 16, 0
SmP0_UPJUMPSHOOTRight:
  .byte 40
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 1, -3
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, 1, 5
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 17, -3
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 17, 5
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $40, 17, 13
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $07, 0, 0
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $47, 0, 8
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $07, 16, -8
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $87, 16, 0
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $47, 16, 8
SmP0_FLIP1Left:
  .byte 28
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c0, 12, 10
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $80, 12, 2
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 12, -6
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c7, 11, 11
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $07, 11, 3
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $07, 11, -5
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $87, 27, 3
SmP0_FLIP1Right:
  .byte 28
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $80, 12, -2
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c0, 12, 6
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $40, 12, 14
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $87, 11, -3
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $47, 11, 5
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $47, 11, 13
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c7, 27, 5
SmP0_FLIP2Left:
  .byte 32
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $40, 8, 7
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $00, 8, -1
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c0, 24, 7
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $80, 24, -1
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $87, 7, 8
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c7, 7, 0
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c7, 23, 8
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $87, 23, 0
SmP0_FLIP2Right:
  .byte 32
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 8, 1
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $40, 8, 9
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $80, 24, 1
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c0, 24, 9
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c7, 7, 0
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $87, 7, 8
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $87, 23, 0
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $c7, 23, 8
SmP0_FLIP3Left:
  .byte 28
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c0, 12, 10
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $80, 12, 2
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $80, 12, -6
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $47, 11, 11
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $07, 11, 3
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $07, 11, -5
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $87, 27, 3
SmP0_FLIP3Right:
  .byte 28
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $80, 12, -2
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c0, 12, 6
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c0, 12, 14
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $07, 11, -3
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $47, 11, 5
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $47, 11, 13
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $c7, 27, 5
SmP0_FLIP4Left:
  .byte 32
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $40, 8, 7
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $00, 8, -1
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c0, 24, 7
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $80, 24, -1
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $47, 7, 8
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c7, 7, 0
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c7, 23, 8
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $87, 23, 0
SmP0_FLIP4Right:
  .byte 32
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 8, 1
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $40, 8, 9
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $80, 24, 1
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c0, 24, 9
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $07, 7, 0
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $87, 7, 8
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $87, 23, 0
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $c7, 23, 8
SmP0_SLIDELeft = SmP0_JUMPSHOOTLeft
SmP0_SLIDERight = SmP0_JUMPSHOOTRight
SmP0_CLIMB1Left:
  .byte 56
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, -15, -2
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $c0, 1, 14
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $40, 1, 6
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 1, -2
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $80, 17, 6
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $00, 17, -2
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $47, -3, 13
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $87, -3, 5
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $87, -3, -3
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c7, 13, 13
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $07, 13, 5
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $07, 13, -3
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c7, 29, 5
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $87, 29, -3
SmP0_CLIMB1Right:
  .byte 56
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, -15, 10
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $80, 1, -6
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 1, 2
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $40, 1, 10
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c0, 17, 2
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $40, 17, 10
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $07, -3, -5
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c7, -3, 3
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c7, -3, 11
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $87, 13, -5
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $47, 13, 3
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $47, 13, 11
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $87, 29, 3
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $c7, 29, 11
SmP0_CLIMB2Left:
  .byte 56
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c0, -1, 9
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, -1, 1
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, -1, -7
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $40, 15, 9
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 15, 1
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $80, 31, 9
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c7, -2, 10
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $07, -2, 2
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $07, -2, -6
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $47, 14, 10
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $47, 14, 2
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $87, 14, -6
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c7, 30, 10
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c7, 30, 2
SmP0_CLIMB2Right:
  .byte 56
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $80, -1, -1
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $40, -1, 7
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, -1, 15
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 15, -1
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $40, 15, 7
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c0, 31, -1
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $87, -2, -2
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $47, -2, 6
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $47, -2, 14
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $07, 14, -2
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $07, 14, 6
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c7, 14, 14
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $87, 30, -2
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $87, 30, 6
SmP0_BALL1Left:
  .byte 16
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c0, 19, 6
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $80, 19, -2
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c7, 18, 7
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $87, 18, -1
SmP0_BALL1Right:
  .byte 16
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $80, 19, 2
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c0, 19, 10
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $87, 18, 1
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $c7, 18, 9
SmP0_BALL2Left:
  .byte 16
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c0, 20, 7
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $80, 20, -1
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c7, 19, 8
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $87, 19, 0
SmP0_BALL2Right:
  .byte 16
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $80, 20, 1
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c0, 20, 9
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $87, 19, 0
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c7, 19, 8
SmP0_BALL3Left = SmP0_BALL1Left
SmP0_BALL3Right = SmP0_BALL1Right
SmP0_BALL4Left = SmP0_BALL2Left
SmP0_BALL4Right = SmP0_BALL2Right
SmP1_STANDLeft = SmP0_STANDLeft
SmP1_STANDRight = SmP0_STANDRight
SmP1_SHOOTLeft = SmP0_SHOOTLeft
SmP1_SHOOTRight = SmP0_SHOOTRight
SmP1_WALK1Left = SmP0_WALK1Left
SmP1_WALK1Right = SmP0_WALK1Right
SmP1_WALK2Left = SmP0_WALK2Left
SmP1_WALK2Right = SmP0_WALK2Right
SmP1_WALK3Left = SmP0_WALK3Left
SmP1_WALK3Right = SmP0_WALK3Right
SmP1_WALKSHOOT1Left = SmP0_WALKSHOOT1Left
SmP1_WALKSHOOT1Right = SmP0_WALKSHOOT1Right
SmP1_WALKSHOOT2Left = SmP0_WALKSHOOT2Left
SmP1_WALKSHOOT2Right = SmP0_WALKSHOOT2Right
SmP1_WALKSHOOT3Left = SmP0_WALKSHOOT3Left
SmP1_WALKSHOOT3Right = SmP0_WALKSHOOT3Right
SmP1_UPSTANDLeft = SmP0_UPSTANDLeft
SmP1_UPSTANDRight = SmP0_UPSTANDRight
SmP1_UPSHOOTLeft = SmP0_UPSHOOTLeft
SmP1_UPSHOOTRight = SmP0_UPSHOOTRight
SmP1_UPWALK1Left = SmP0_UPWALK1Left
SmP1_UPWALK1Right = SmP0_UPWALK1Right
SmP1_UPWALK2Left = SmP0_UPWALK2Left
SmP1_UPWALK2Right = SmP0_UPWALK2Right
SmP1_UPWALK3Left = SmP0_UPWALK3Left
SmP1_UPWALK3Right = SmP0_UPWALK3Right
SmP1_UPWALKSHOOT1Left = SmP0_UPWALKSHOOT1Left
SmP1_UPWALKSHOOT1Right = SmP0_UPWALKSHOOT1Right
SmP1_UPWALKSHOOT2Left = SmP0_UPWALKSHOOT2Left
SmP1_UPWALKSHOOT2Right = SmP0_UPWALKSHOOT2Right
SmP1_UPWALKSHOOT3Left = SmP0_UPWALKSHOOT3Left
SmP1_UPWALKSHOOT3Right = SmP0_UPWALKSHOOT3Right
SmP1_JUMPLeft = SmP0_JUMPLeft
SmP1_JUMPRight = SmP0_JUMPRight
SmP1_JUMPSHOOTLeft = SmP0_JUMPSHOOTLeft
SmP1_JUMPSHOOTRight = SmP0_JUMPSHOOTRight
SmP1_UPJUMPLeft = SmP0_UPJUMPLeft
SmP1_UPJUMPRight = SmP0_UPJUMPRight
SmP1_UPJUMPSHOOTLeft = SmP0_UPJUMPSHOOTLeft
SmP1_UPJUMPSHOOTRight = SmP0_UPJUMPSHOOTRight
SmP1_FLIP1Left = SmP0_FLIP1Left
SmP1_FLIP1Right = SmP0_FLIP1Right
SmP1_FLIP2Left = SmP0_FLIP2Left
SmP1_FLIP2Right = SmP0_FLIP2Right
SmP1_FLIP3Left = SmP0_FLIP3Left
SmP1_FLIP3Right = SmP0_FLIP3Right
SmP1_FLIP4Left = SmP0_FLIP4Left
SmP1_FLIP4Right = SmP0_FLIP4Right
SmP1_SLIDELeft = SmP0_JUMPSHOOTLeft
SmP1_SLIDERight = SmP0_JUMPSHOOTRight
SmP1_CLIMB1Left = SmP0_CLIMB1Left
SmP1_CLIMB1Right = SmP0_CLIMB1Right
SmP1_CLIMB2Left = SmP0_CLIMB2Left
SmP1_CLIMB2Right = SmP0_CLIMB2Right
SmP1_BALL1Left = SmP0_BALL1Left
SmP1_BALL1Right = SmP0_BALL1Right
SmP1_BALL2Left = SmP0_BALL2Left
SmP1_BALL2Right = SmP0_BALL2Right
SmP1_BALL3Left = SmP0_BALL1Left
SmP1_BALL3Right = SmP0_BALL1Right
SmP1_BALL4Left = SmP0_BALL2Left
SmP1_BALL4Right = SmP0_BALL2Right
SmP2_STANDLeft:
  .byte 48
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $40, 0, 6
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 0, -2
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 0, -10
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $40, 16, 6
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 16, -2
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $47, -1, 7
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $07, -1, -1
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $07, -1, -9
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $47, 15, 7
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $07, 15, -1
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c7, 31, 7
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $87, 31, -1
SmP2_STANDRight:
  .byte 48
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 0, 2
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $40, 0, 10
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $40, 0, 18
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 16, 2
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 16, 10
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $07, -1, 1
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $47, -1, 9
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $47, -1, 17
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $07, 15, 1
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $47, 15, 9
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $87, 31, 1
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c7, 31, 9
SmP2_SHOOTLeft:
  .byte 40
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $40, 0, 6
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 0, -2
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $40, 16, 6
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 16, -2
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $47, -16, 5
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $07, 0, 5
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $87, 0, -3
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $47, 16, 13
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c7, 16, 5
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $07, 16, -3
SmP2_SHOOTRight:
  .byte 40
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 0, 2
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $40, 0, 10
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 16, 2
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 16, 10
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $07, -16, 3
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $47, 0, 3
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c7, 0, 11
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $07, 16, -5
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $87, 16, 3
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $47, 16, 11
SmP2_WALK1Left:
  .byte 36
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $40, 1, 8
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $40, 1, 0
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $80, 17, 8
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $80, 17, 0
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $47, 0, 9
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c7, 0, 1
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $87, 0, -7
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $47, 16, 9
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $87, 16, 1
SmP2_WALK1Right:
  .byte 36
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 1, 0
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 1, 8
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c0, 17, 0
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $c0, 17, 8
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $07, 0, -1
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $87, 0, 7
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $c7, 0, 15
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $07, 16, -1
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c7, 16, 7
SmP2_WALK2Left:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, 0, 8
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 0, 0
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $40, 16, 16
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $80, 16, 8
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c0, 16, 0
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $c7, -1, 11
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $47, -1, 3
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $07, -1, -5
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $47, 15, 11
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c7, 15, 3
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $87, 15, -5
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c7, 31, 11
SmP2_WALK2Right:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 0, 0
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, 0, 8
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 16, -8
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c0, 16, 0
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $80, 16, 8
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $87, -1, -3
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $07, -1, 5
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $47, -1, 13
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $07, 15, -3
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $87, 15, 5
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c7, 15, 13
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $87, 31, -3
SmP2_WALK3Left:
  .byte 48
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $40, 0, 7
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 0, -1
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c0, 16, 15
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c0, 16, 7
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 16, -1
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $07, -1, 10
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $47, -1, 2
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $87, -1, -6
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c7, 15, 18
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c7, 15, 10
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $07, 15, 2
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $87, 31, 2
SmP2_WALK3Right:
  .byte 48
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 0, 1
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $40, 0, 9
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $80, 16, -7
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $80, 16, 1
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 16, 9
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $47, -1, -2
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $07, -1, 6
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c7, -1, 14
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $87, 15, -10
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $87, 15, -2
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $47, 15, 6
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c7, 31, 6
SmP2_WALKSHOOT1Left:
  .byte 40
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $40, 1, 8
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $40, 1, 0
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 1, -8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $80, 17, 8
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $80, 17, 0
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $47, 0, 9
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $87, 0, 1
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $87, 0, -7
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $47, 16, 9
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $87, 16, 1
SmP2_WALKSHOOT1Right:
  .byte 40
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 1, 0
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $00, 1, 8
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $40, 1, 16
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c0, 17, 0
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c0, 17, 8
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $07, 0, -1
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c7, 0, 7
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c7, 0, 15
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $07, 16, -1
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c7, 16, 7
SmP2_WALKSHOOT2Left:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, 1, 10
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, 1, 2
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 1, -6
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $80, 17, 10
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c0, 17, 2
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $80, 17, -6
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $47, 0, 11
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $47, 0, 3
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $87, 0, -5
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $47, 16, 11
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c7, 16, 3
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $87, 16, -5
SmP2_WALKSHOOT2Right:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 1, -2
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 1, 6
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $40, 1, 14
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c0, 17, -2
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $80, 17, 6
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $c0, 17, 14
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $07, 0, -3
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $07, 0, 5
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c7, 0, 13
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $07, 16, -3
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $87, 16, 5
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c7, 16, 13
SmP2_WALKSHOOT3Left:
  .byte 48
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $40, 1, 8
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $40, 1, 0
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 1, -8
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c0, 17, 16
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $c0, 17, 8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $80, 17, 0
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $47, 0, 9
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $87, 0, 1
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $87, 0, -7
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c7, 16, 17
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c7, 16, 9
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $07, 16, 1
SmP2_WALKSHOOT3Right:
  .byte 48
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 1, 0
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 1, 8
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $40, 1, 16
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $80, 17, -8
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $80, 17, 0
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c0, 17, 8
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $07, 0, -1
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c7, 0, 7
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c7, 0, 15
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $87, 16, -9
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $87, 16, -1
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $47, 16, 7
SmP2_UPSTANDLeft:
  .byte 44
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, -16, 1
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, 0, 9
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 0, 1
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $40, 16, 9
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 16, 1
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $47, -6, 8
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $07, -6, 0
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c7, 10, 8
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $07, 10, 0
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c7, 26, 8
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c7, 26, 0
SmP2_UPSTANDRight:
  .byte 44
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, -16, 7
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 0, -1
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $40, 0, 7
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 16, -1
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $40, 16, 7
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $07, -6, 0
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $47, -6, 8
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $87, 10, 0
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $47, 10, 8
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $87, 26, 0
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $87, 26, 8
SmP2_UPSHOOTLeft:
  .byte 44
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, -16, 1
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, 0, 9
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 0, 1
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $40, 16, 9
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 16, 1
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $47, -4, 8
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $07, -4, 0
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c7, 12, 8
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $07, 12, 0
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c7, 28, 8
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c7, 28, 0
SmP2_UPSHOOTRight:
  .byte 44
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $40, -16, 7
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 0, -1
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $40, 0, 7
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 16, -1
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $40, 16, 7
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $07, -4, 0
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $47, -4, 8
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $87, 12, 0
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $47, 12, 8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $87, 28, 0
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $87, 28, 8
SmP2_UPWALK1Left:
  .byte 36
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, -5, 7
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, -5, -1
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $80, 11, 7
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 27, 7
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $47, -6, 8
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $07, -6, 0
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $07, 10, 8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $87, 10, 0
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $87, 26, 8
SmP2_UPWALK1Right:
  .byte 36
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, -5, 1
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, -5, 9
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c0, 11, 1
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 27, 1
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $07, -6, 0
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $47, -6, 8
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $47, 10, 0
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c7, 10, 8
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c7, 26, 0
SmP2_UPWALK2Left:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, -5, 10
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, -5, 2
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $40, 11, 10
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c0, 11, 2
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 11, -6
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $80, 27, 10
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $47, -6, 11
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $07, -6, 3
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $47, 10, 11
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c7, 10, 3
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $07, 10, -5
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $87, 26, 11
SmP2_UPWALK2Right:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, -5, -2
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, -5, 6
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 11, -2
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $80, 11, 6
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $40, 11, 14
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $c0, 27, -2
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $07, -6, -3
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $47, -6, 5
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $07, 10, -3
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $87, 10, 5
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $47, 10, 13
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c7, 26, -3
SmP2_UPWALK3Left:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, -5, 10
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, -5, 2
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $40, 11, 18
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $40, 11, 10
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $00, 11, 2
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $80, 27, 2
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $47, -6, 11
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $07, -6, 3
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $47, 10, 19
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c7, 10, 11
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $07, 10, 3
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $87, 26, 3
SmP2_UPWALK3Right:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, -5, -2
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, -5, 6
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 11, -10
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 11, -2
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $40, 11, 6
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c0, 27, 6
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $07, -6, -3
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $47, -6, 5
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $07, 10, -11
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $87, 10, -3
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $47, 10, 5
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c7, 26, 5
SmP2_UPWALKSHOOT1Left:
  .byte 36
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, -3, 7
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, -3, -1
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $80, 13, 7
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $80, 29, 7
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $47, -4, 8
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $07, -4, 0
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $87, 12, 8
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $87, 12, 0
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $87, 28, 8
SmP2_UPWALKSHOOT1Right:
  .byte 36
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, -3, 1
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, -3, 9
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $c0, 13, 1
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c0, 29, 1
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $07, -4, 0
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $47, -4, 8
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $c7, 12, 0
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c7, 12, 8
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c7, 28, 0
SmP2_UPWALKSHOOT2Left:
  .byte 48
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, -3, 10
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, -3, 2
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $40, 13, 10
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 13, 2
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 13, -6
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $80, 29, 10
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $47, -4, 11
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $07, -4, 3
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $47, 12, 11
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c7, 12, 3
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $07, 12, -5
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $87, 28, 11
SmP2_UPWALKSHOOT2Right:
  .byte 48
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, -3, -2
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, -3, 6
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 13, -2
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 13, 6
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $40, 13, 14
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c0, 29, -2
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $07, -4, -3
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $47, -4, 5
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $07, 12, -3
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $87, 12, 5
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $47, 12, 13
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $c7, 28, -3
SmP2_UPWALKSHOOT3Left:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, -3, 10
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, -3, 2
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $c0, 13, 18
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c0, 13, 10
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $80, 13, 2
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $80, 29, 2
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $47, -4, 11
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $07, -4, 3
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $47, 12, 19
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c7, 12, 11
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $07, 12, 3
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $87, 28, 3
SmP2_UPWALKSHOOT3Right:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, -3, -2
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, -3, 6
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $80, 13, -10
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $80, 13, -2
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c0, 13, 6
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $c0, 29, 6
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $07, -4, -3
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $47, -4, 5
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $07, 12, -11
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $87, 12, -3
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $47, 12, 5
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c7, 28, 5
SmP2_JUMPLeft:
  .byte 44
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 7, 9
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, 7, 1
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $80, 7, -7
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 23, 9
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 23, 1
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $47, 6, 10
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $47, 6, 2
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $87, 6, -6
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c7, 22, 10
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c7, 22, 2
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $87, 22, -6
SmP2_JUMPRight:
  .byte 44
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 7, -1
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 7, 7
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c0, 7, 15
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 23, -1
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 23, 7
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $07, 6, -2
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $07, 6, 6
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c7, 6, 14
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $87, 22, -2
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $87, 22, 6
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c7, 22, 14
SmP2_JUMPSHOOTLeft:
  .byte 44
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, 7, 9
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, 7, 1
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $80, 7, -7
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c0, 23, 9
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c0, 23, 1
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $47, 6, 10
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $47, 6, 2
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $87, 6, -6
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c7, 22, 10
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c7, 22, 2
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $87, 22, -6
SmP2_JUMPSHOOTRight:
  .byte 44
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 7, -1
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 7, 7
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $c0, 7, 15
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $80, 23, -1
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $80, 23, 7
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $07, 6, -2
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $07, 6, 6
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c7, 6, 14
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $87, 22, -2
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $87, 22, 6
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c7, 22, 14
SmP2_UPJUMPLeft:
  .byte 36
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $40, 1, 9
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 1, 1
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c0, 17, 9
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c0, 17, 1
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $47, 0, 10
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $07, 0, 2
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c7, 16, 10
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $c7, 16, 2
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $07, 16, -6
SmP2_UPJUMPRight:
  .byte 36
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 1, -1
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $40, 1, 7
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $80, 17, -1
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $80, 17, 7
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $07, 0, -2
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $47, 0, 6
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $87, 16, -2
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $87, 16, 6
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $47, 16, 14
SmP2_UPJUMPSHOOTLeft:
  .byte 36
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $40, 3, 9
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 3, 1
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c0, 19, 9
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c0, 19, 1
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $47, 2, 10
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $07, 2, 2
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c7, 18, 10
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c7, 18, 2
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $07, 18, -6
SmP2_UPJUMPSHOOTRight:
  .byte 36
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 3, -1
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 3, 7
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $80, 19, -1
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $80, 19, 7
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $07, 2, -2
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $47, 2, 6
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $87, 18, -2
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $87, 18, 6
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $47, 18, 14
SmP2_FLIP1Left:
  .byte 24
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c0, 12, 10
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $80, 12, 2
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $80, 12, -6
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c7, 11, 11
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c7, 11, 3
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $07, 11, -5
SmP2_FLIP1Right:
  .byte 24
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $80, 12, -2
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c0, 12, 6
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c0, 12, 14
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $87, 11, -3
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $87, 11, 5
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $47, 11, 13
SmP2_FLIP2Left:
  .byte 32
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 10, 7
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $80, 10, -1
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c0, 26, 7
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $80, 26, -1
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $47, 9, 8
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $07, 9, 0
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c7, 25, 8
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $87, 25, 0
SmP2_FLIP2Right:
  .byte 32
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 10, 1
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c0, 10, 9
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $80, 26, 1
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c0, 26, 9
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $07, 9, 0
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $47, 9, 8
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $87, 25, 0
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $c7, 25, 8
SmP2_FLIP3Left:
  .byte 24
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $c0, 13, 10
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $80, 13, 2
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $80, 13, -6
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c7, 12, 11
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $07, 12, 3
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $07, 12, -5
SmP2_FLIP3Right:
  .byte 24
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $80, 13, -2
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $c0, 13, 6
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $c0, 13, 14
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $87, 12, -3
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $47, 12, 5
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $47, 12, 13
SmP2_FLIP4Left:
  .byte 32
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $40, 10, 7
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 10, -1
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c0, 26, 7
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $80, 26, -1
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $47, 9, 8
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $07, 9, 0
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c7, 25, 8
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $87, 25, 0
SmP2_FLIP4Right:
  .byte 32
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 10, 1
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 10, 9
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $80, 26, 1
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c0, 26, 9
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $07, 9, 0
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $47, 9, 8
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $87, 25, 0
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c7, 25, 8
SmP2_SLIDELeft = SmP2_JUMPSHOOTLeft
SmP2_SLIDERight = SmP2_JUMPSHOOTRight
SmP2_CLIMB1Left:
  .byte 36
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 1, 6
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 1, -2
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $80, 17, 6
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 17, -2
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $47, 0, 7
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $87, 0, -1
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $87, 16, 7
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $07, 16, -1
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $87, 32, -1
SmP2_CLIMB1Right:
  .byte 36
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, 1, 2
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, 1, 10
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $c0, 17, 2
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $40, 17, 10
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $07, 0, 1
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $c7, 0, 9
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $c7, 16, 1
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $47, 16, 9
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c7, 32, 9
SmP2_CLIMB2Left:
  .byte 36
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 2, 7
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 2, -1
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c0, 18, 7
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $80, 18, -1
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $47, 1, 8
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $07, 1, 0
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $47, 17, 8
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $87, 17, 0
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c7, 33, 8
SmP2_CLIMB2Right:
  .byte 36
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $40, 2, 1
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $40, 2, 9
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $80, 18, 1
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c0, 18, 9
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $07, 1, 0
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $47, 1, 8
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $07, 17, 0
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $c7, 17, 8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $87, 33, 0
SmP2_BALL1Left:
  .byte 16
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $c0, 19, 6
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $80, 19, -2
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c7, 18, 7
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $87, 18, -1
SmP2_BALL1Right:
  .byte 16
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $80, 19, 2
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c0, 19, 10
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $87, 18, 1
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c7, 18, 9
SmP2_BALL2Left:
  .byte 16
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c0, 20, 7
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $80, 20, -1
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c7, 19, 8
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $87, 19, 0
SmP2_BALL2Right:
  .byte 16
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $80, 20, 1
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c0, 20, 9
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $87, 19, 0
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $c7, 19, 8
SmP2_BALL3Left:
  .byte 16
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c0, 19, 6
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $80, 19, -2
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $c7, 18, 7
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $87, 18, -1
SmP2_BALL3Right:
  .byte 16
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $80, 19, 2
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c0, 19, 10
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $87, 18, 1
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c7, 18, 9
SmP2_BALL4Left:
  .byte 16
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c0, 20, 7
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $80, 20, -1
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c7, 19, 8
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $87, 19, 0
SmP2_BALL4Right:
  .byte 16
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $80, 20, 1
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c0, 20, 9
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $87, 19, 0
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c7, 19, 8
SmP0_CROUCHLeft:
  .byte 44
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $40, 8, 9
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 8, 1
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 8, -7
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $80, 24, 9
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c0, 24, 1
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $47, 7, 10
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c7, 7, 2
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $07, 7, -6
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c7, 23, 10
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c7, 23, 2
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $87, 23, -6
SmP0_CROUCHRight:
  .byte 44
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 8, -1
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $40, 8, 7
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $40, 8, 15
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c0, 24, -1
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $80, 24, 7
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $07, 7, -2
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $87, 7, 6
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $47, 7, 14
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $87, 23, -2
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $87, 23, 6
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c7, 23, 14
SmP0_CROUCHSHOOTLeft:
  .byte 44
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $40, 8, 9
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 8, 1
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 8, -7
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $80, 24, 9
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c0, 24, 1
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $47, 7, 10
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c7, 7, 2
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $07, 7, -6
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c7, 23, 10
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c7, 23, 2
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $87, 23, -6
SmP0_CROUCHSHOOTRight:
  .byte 44
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 8, -1
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $40, 8, 7
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $40, 8, 15
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c0, 24, -1
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $80, 24, 7
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $07, 7, -2
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $87, 7, 6
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $47, 7, 14
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $87, 23, -2
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $87, 23, 6
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c7, 23, 14
SmP1_CROUCHLeft = SmP0_CROUCHLeft
SmP1_CROUCHRight = SmP0_CROUCHRight
SmP1_CROUCHSHOOTLeft = SmP0_CROUCHSHOOTLeft
SmP1_CROUCHSHOOTRight = SmP0_CROUCHSHOOTRight
SmP2_CROUCHLeft:
  .byte 44
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, 7, 8
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 7, 0
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 7, -8
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c0, 23, 8
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c0, 23, 0
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $47, 6, 9
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $07, 6, 1
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $07, 6, -7
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c7, 22, 9
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $87, 22, 1
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $87, 22, -7
SmP2_CROUCHRight:
  .byte 44
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 7, 0
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, 7, 8
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $40, 7, 16
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $80, 23, 0
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $80, 23, 8
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $07, 6, -1
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $47, 6, 7
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $47, 6, 15
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $87, 22, -1
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c7, 22, 7
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c7, 22, 15
SmP2_CROUCHSHOOTLeft:
  .byte 40
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, 7, 8
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 7, 0
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 7, -8
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c0, 23, 8
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c0, 23, 0
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $47, 6, 4
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $07, 6, -4
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c7, 22, 12
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c7, 22, 4
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $87, 22, -4
SmP2_CROUCHSHOOTRight:
  .byte 40
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 7, 0
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, 7, 8
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $40, 7, 16
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $80, 23, 0
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $80, 23, 8
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $07, 6, 4
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $47, 6, 12
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $87, 22, -4
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $87, 22, 4
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c7, 22, 12
SamusPoseBanks:
  .byte $9a,$9a,$94,$93,$94,$9e,$94,$95,$9b,$9b,$9e,$92,$92,$9f,$95,$93,$9f,$96,$9b,$9f,$a2,$92,$93,$95,$96,$91,$91,$91,$9a,$a0,$a1,$9a,$9a,$94,$93,$94,$9e,$94,$95,$9b,$9b,$9e,$92,$92,$9f,$95,$93,$9f,$96,$9b,$9f,$a2,$92,$93,$95,$96,$91,$91,$91,$9a,$a0,$a1,$96,$96,$a0,$97,$97,$98,$98,$98,$9c,$9c,$a0,$99,$99,$a1,$99,$9a,$9c,$9d,$a1,$a1,$9d,$97,$80,$a2,$9d,$a2,$a2,$80,$80,$80,$80
.segment "SAMUS"
SamusPoseLeftLo:
  .byte <SmP0_STANDLeft,<SmP0_SHOOTLeft,<SmP0_WALK1Left,<SmP0_WALK2Left,<SmP0_WALK3Left,<SmP0_WALKSHOOT1Left,<SmP0_WALKSHOOT2Left,<SmP0_WALKSHOOT3Left,<SmP0_UPSTANDLeft,<SmP0_UPSHOOTLeft,<SmP0_UPWALK1Left,<SmP0_UPWALK2Left,<SmP0_UPWALK3Left,<SmP0_UPWALKSHOOT1Left,<SmP0_UPWALKSHOOT2Left,<SmP0_UPWALKSHOOT3Left,<SmP0_JUMPLeft,<SmP0_JUMPSHOOTLeft,<SmP0_UPJUMPLeft,<SmP0_UPJUMPSHOOTLeft,<SmP0_FLIP1Left,<SmP0_FLIP2Left,<SmP0_FLIP3Left,<SmP0_FLIP4Left,<SmP0_SLIDELeft,<SmP0_CLIMB1Left,<SmP0_CLIMB2Left,<SmP0_BALL1Left,<SmP0_BALL2Left,<SmP0_BALL3Left,<SmP0_BALL4Left,<SmP1_STANDLeft,<SmP1_SHOOTLeft,<SmP1_WALK1Left,<SmP1_WALK2Left,<SmP1_WALK3Left,<SmP1_WALKSHOOT1Left,<SmP1_WALKSHOOT2Left,<SmP1_WALKSHOOT3Left,<SmP1_UPSTANDLeft,<SmP1_UPSHOOTLeft,<SmP1_UPWALK1Left,<SmP1_UPWALK2Left,<SmP1_UPWALK3Left,<SmP1_UPWALKSHOOT1Left,<SmP1_UPWALKSHOOT2Left,<SmP1_UPWALKSHOOT3Left,<SmP1_JUMPLeft,<SmP1_JUMPSHOOTLeft,<SmP1_UPJUMPLeft,<SmP1_UPJUMPSHOOTLeft,<SmP1_FLIP1Left,<SmP1_FLIP2Left,<SmP1_FLIP3Left,<SmP1_FLIP4Left,<SmP1_SLIDELeft,<SmP1_CLIMB1Left,<SmP1_CLIMB2Left,<SmP1_BALL1Left,<SmP1_BALL2Left,<SmP1_BALL3Left,<SmP1_BALL4Left,<SmP2_STANDLeft,<SmP2_SHOOTLeft,<SmP2_WALK1Left,<SmP2_WALK2Left,<SmP2_WALK3Left,<SmP2_WALKSHOOT1Left,<SmP2_WALKSHOOT2Left,<SmP2_WALKSHOOT3Left,<SmP2_UPSTANDLeft,<SmP2_UPSHOOTLeft,<SmP2_UPWALK1Left,<SmP2_UPWALK2Left,<SmP2_UPWALK3Left,<SmP2_UPWALKSHOOT1Left,<SmP2_UPWALKSHOOT2Left,<SmP2_UPWALKSHOOT3Left,<SmP2_JUMPLeft,<SmP2_JUMPSHOOTLeft,<SmP2_UPJUMPLeft,<SmP2_UPJUMPSHOOTLeft,<SmP2_FLIP1Left,<SmP2_FLIP2Left,<SmP2_FLIP3Left,<SmP2_FLIP4Left,<SmP2_SLIDELeft,<SmP2_CLIMB1Left,<SmP2_CLIMB2Left,<SmP2_BALL1Left,<SmP2_BALL2Left,<SmP2_BALL3Left,<SmP2_BALL4Left
SamusPoseLeftHi:
  .byte >SmP0_STANDLeft,>SmP0_SHOOTLeft,>SmP0_WALK1Left,>SmP0_WALK2Left,>SmP0_WALK3Left,>SmP0_WALKSHOOT1Left,>SmP0_WALKSHOOT2Left,>SmP0_WALKSHOOT3Left,>SmP0_UPSTANDLeft,>SmP0_UPSHOOTLeft,>SmP0_UPWALK1Left,>SmP0_UPWALK2Left,>SmP0_UPWALK3Left,>SmP0_UPWALKSHOOT1Left,>SmP0_UPWALKSHOOT2Left,>SmP0_UPWALKSHOOT3Left,>SmP0_JUMPLeft,>SmP0_JUMPSHOOTLeft,>SmP0_UPJUMPLeft,>SmP0_UPJUMPSHOOTLeft,>SmP0_FLIP1Left,>SmP0_FLIP2Left,>SmP0_FLIP3Left,>SmP0_FLIP4Left,>SmP0_SLIDELeft,>SmP0_CLIMB1Left,>SmP0_CLIMB2Left,>SmP0_BALL1Left,>SmP0_BALL2Left,>SmP0_BALL3Left,>SmP0_BALL4Left,>SmP1_STANDLeft,>SmP1_SHOOTLeft,>SmP1_WALK1Left,>SmP1_WALK2Left,>SmP1_WALK3Left,>SmP1_WALKSHOOT1Left,>SmP1_WALKSHOOT2Left,>SmP1_WALKSHOOT3Left,>SmP1_UPSTANDLeft,>SmP1_UPSHOOTLeft,>SmP1_UPWALK1Left,>SmP1_UPWALK2Left,>SmP1_UPWALK3Left,>SmP1_UPWALKSHOOT1Left,>SmP1_UPWALKSHOOT2Left,>SmP1_UPWALKSHOOT3Left,>SmP1_JUMPLeft,>SmP1_JUMPSHOOTLeft,>SmP1_UPJUMPLeft,>SmP1_UPJUMPSHOOTLeft,>SmP1_FLIP1Left,>SmP1_FLIP2Left,>SmP1_FLIP3Left,>SmP1_FLIP4Left,>SmP1_SLIDELeft,>SmP1_CLIMB1Left,>SmP1_CLIMB2Left,>SmP1_BALL1Left,>SmP1_BALL2Left,>SmP1_BALL3Left,>SmP1_BALL4Left,>SmP2_STANDLeft,>SmP2_SHOOTLeft,>SmP2_WALK1Left,>SmP2_WALK2Left,>SmP2_WALK3Left,>SmP2_WALKSHOOT1Left,>SmP2_WALKSHOOT2Left,>SmP2_WALKSHOOT3Left,>SmP2_UPSTANDLeft,>SmP2_UPSHOOTLeft,>SmP2_UPWALK1Left,>SmP2_UPWALK2Left,>SmP2_UPWALK3Left,>SmP2_UPWALKSHOOT1Left,>SmP2_UPWALKSHOOT2Left,>SmP2_UPWALKSHOOT3Left,>SmP2_JUMPLeft,>SmP2_JUMPSHOOTLeft,>SmP2_UPJUMPLeft,>SmP2_UPJUMPSHOOTLeft,>SmP2_FLIP1Left,>SmP2_FLIP2Left,>SmP2_FLIP3Left,>SmP2_FLIP4Left,>SmP2_SLIDELeft,>SmP2_CLIMB1Left,>SmP2_CLIMB2Left,>SmP2_BALL1Left,>SmP2_BALL2Left,>SmP2_BALL3Left,>SmP2_BALL4Left
SamusPoseRightLo:
  .byte <SmP0_STANDRight,<SmP0_SHOOTRight,<SmP0_WALK1Right,<SmP0_WALK2Right,<SmP0_WALK3Right,<SmP0_WALKSHOOT1Right,<SmP0_WALKSHOOT2Right,<SmP0_WALKSHOOT3Right,<SmP0_UPSTANDRight,<SmP0_UPSHOOTRight,<SmP0_UPWALK1Right,<SmP0_UPWALK2Right,<SmP0_UPWALK3Right,<SmP0_UPWALKSHOOT1Right,<SmP0_UPWALKSHOOT2Right,<SmP0_UPWALKSHOOT3Right,<SmP0_JUMPRight,<SmP0_JUMPSHOOTRight,<SmP0_UPJUMPRight,<SmP0_UPJUMPSHOOTRight,<SmP0_FLIP1Right,<SmP0_FLIP2Right,<SmP0_FLIP3Right,<SmP0_FLIP4Right,<SmP0_SLIDERight,<SmP0_CLIMB1Right,<SmP0_CLIMB2Right,<SmP0_BALL1Right,<SmP0_BALL2Right,<SmP0_BALL3Right,<SmP0_BALL4Right,<SmP1_STANDRight,<SmP1_SHOOTRight,<SmP1_WALK1Right,<SmP1_WALK2Right,<SmP1_WALK3Right,<SmP1_WALKSHOOT1Right,<SmP1_WALKSHOOT2Right,<SmP1_WALKSHOOT3Right,<SmP1_UPSTANDRight,<SmP1_UPSHOOTRight,<SmP1_UPWALK1Right,<SmP1_UPWALK2Right,<SmP1_UPWALK3Right,<SmP1_UPWALKSHOOT1Right,<SmP1_UPWALKSHOOT2Right,<SmP1_UPWALKSHOOT3Right,<SmP1_JUMPRight,<SmP1_JUMPSHOOTRight,<SmP1_UPJUMPRight,<SmP1_UPJUMPSHOOTRight,<SmP1_FLIP1Right,<SmP1_FLIP2Right,<SmP1_FLIP3Right,<SmP1_FLIP4Right,<SmP1_SLIDERight,<SmP1_CLIMB1Right,<SmP1_CLIMB2Right,<SmP1_BALL1Right,<SmP1_BALL2Right,<SmP1_BALL3Right,<SmP1_BALL4Right,<SmP2_STANDRight,<SmP2_SHOOTRight,<SmP2_WALK1Right,<SmP2_WALK2Right,<SmP2_WALK3Right,<SmP2_WALKSHOOT1Right,<SmP2_WALKSHOOT2Right,<SmP2_WALKSHOOT3Right,<SmP2_UPSTANDRight,<SmP2_UPSHOOTRight,<SmP2_UPWALK1Right,<SmP2_UPWALK2Right,<SmP2_UPWALK3Right,<SmP2_UPWALKSHOOT1Right,<SmP2_UPWALKSHOOT2Right,<SmP2_UPWALKSHOOT3Right,<SmP2_JUMPRight,<SmP2_JUMPSHOOTRight,<SmP2_UPJUMPRight,<SmP2_UPJUMPSHOOTRight,<SmP2_FLIP1Right,<SmP2_FLIP2Right,<SmP2_FLIP3Right,<SmP2_FLIP4Right,<SmP2_SLIDERight,<SmP2_CLIMB1Right,<SmP2_CLIMB2Right,<SmP2_BALL1Right,<SmP2_BALL2Right,<SmP2_BALL3Right,<SmP2_BALL4Right
SamusPoseRightHi:
  .byte >SmP0_STANDRight,>SmP0_SHOOTRight,>SmP0_WALK1Right,>SmP0_WALK2Right,>SmP0_WALK3Right,>SmP0_WALKSHOOT1Right,>SmP0_WALKSHOOT2Right,>SmP0_WALKSHOOT3Right,>SmP0_UPSTANDRight,>SmP0_UPSHOOTRight,>SmP0_UPWALK1Right,>SmP0_UPWALK2Right,>SmP0_UPWALK3Right,>SmP0_UPWALKSHOOT1Right,>SmP0_UPWALKSHOOT2Right,>SmP0_UPWALKSHOOT3Right,>SmP0_JUMPRight,>SmP0_JUMPSHOOTRight,>SmP0_UPJUMPRight,>SmP0_UPJUMPSHOOTRight,>SmP0_FLIP1Right,>SmP0_FLIP2Right,>SmP0_FLIP3Right,>SmP0_FLIP4Right,>SmP0_SLIDERight,>SmP0_CLIMB1Right,>SmP0_CLIMB2Right,>SmP0_BALL1Right,>SmP0_BALL2Right,>SmP0_BALL3Right,>SmP0_BALL4Right,>SmP1_STANDRight,>SmP1_SHOOTRight,>SmP1_WALK1Right,>SmP1_WALK2Right,>SmP1_WALK3Right,>SmP1_WALKSHOOT1Right,>SmP1_WALKSHOOT2Right,>SmP1_WALKSHOOT3Right,>SmP1_UPSTANDRight,>SmP1_UPSHOOTRight,>SmP1_UPWALK1Right,>SmP1_UPWALK2Right,>SmP1_UPWALK3Right,>SmP1_UPWALKSHOOT1Right,>SmP1_UPWALKSHOOT2Right,>SmP1_UPWALKSHOOT3Right,>SmP1_JUMPRight,>SmP1_JUMPSHOOTRight,>SmP1_UPJUMPRight,>SmP1_UPJUMPSHOOTRight,>SmP1_FLIP1Right,>SmP1_FLIP2Right,>SmP1_FLIP3Right,>SmP1_FLIP4Right,>SmP1_SLIDERight,>SmP1_CLIMB1Right,>SmP1_CLIMB2Right,>SmP1_BALL1Right,>SmP1_BALL2Right,>SmP1_BALL3Right,>SmP1_BALL4Right,>SmP2_STANDRight,>SmP2_SHOOTRight,>SmP2_WALK1Right,>SmP2_WALK2Right,>SmP2_WALK3Right,>SmP2_WALKSHOOT1Right,>SmP2_WALKSHOOT2Right,>SmP2_WALKSHOOT3Right,>SmP2_UPSTANDRight,>SmP2_UPSHOOTRight,>SmP2_UPWALK1Right,>SmP2_UPWALK2Right,>SmP2_UPWALK3Right,>SmP2_UPWALKSHOOT1Right,>SmP2_UPWALKSHOOT2Right,>SmP2_UPWALKSHOOT3Right,>SmP2_JUMPRight,>SmP2_JUMPSHOOTRight,>SmP2_UPJUMPRight,>SmP2_UPJUMPSHOOTRight,>SmP2_FLIP1Right,>SmP2_FLIP2Right,>SmP2_FLIP3Right,>SmP2_FLIP4Right,>SmP2_SLIDERight,>SmP2_CLIMB1Right,>SmP2_CLIMB2Right,>SmP2_BALL1Right,>SmP2_BALL2Right,>SmP2_BALL3Right,>SmP2_BALL4Right
SamusCrouchBanks:
  .byte $9d,$9d,$9d,$9d,$9e,$a0
SamusCrouchLeftLo:
  .byte <SmP0_CROUCHLeft,<SmP0_CROUCHSHOOTLeft,<SmP1_CROUCHLeft,<SmP1_CROUCHSHOOTLeft,<SmP2_CROUCHLeft,<SmP2_CROUCHSHOOTLeft
SamusCrouchLeftHi:
  .byte >SmP0_CROUCHLeft,>SmP0_CROUCHSHOOTLeft,>SmP1_CROUCHLeft,>SmP1_CROUCHSHOOTLeft,>SmP2_CROUCHLeft,>SmP2_CROUCHSHOOTLeft
SamusCrouchRightLo:
  .byte <SmP0_CROUCHRight,<SmP0_CROUCHSHOOTRight,<SmP1_CROUCHRight,<SmP1_CROUCHSHOOTRight,<SmP2_CROUCHRight,<SmP2_CROUCHSHOOTRight
SamusCrouchRightHi:
  .byte >SmP0_CROUCHRight,>SmP0_CROUCHSHOOTRight,>SmP1_CROUCHRight,>SmP1_CROUCHSHOOTRight,>SmP2_CROUCHRight,>SmP2_CROUCHSHOOTRight
.segment "SAMUS_GFX"
MetaspriteData "SAMUS_BODY", SmP0_STANDLeft, SmP0_STANDRight
MetaspriteData "SAMUS_BEAM_1", SmSAMUS_BEAM_1Left, SmSAMUS_BEAM_1Right
SmSAMUS_BEAM_1Left:
  .byte 4
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_4}, $80, -3, -6
SmSAMUS_BEAM_1Right:
  .byte 4
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_4}, $c0, -3, -2
MetaspriteData "SAMUS_BEAM_1_UP", SmSAMUS_BEAM_1_UPLeft, SmSAMUS_BEAM_1_UPRight
SmSAMUS_BEAM_1_UPLeft:
  .byte 4
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_4}, $80, -2, -5
SmSAMUS_BEAM_1_UPRight:
  .byte 4
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_4}, $c0, -2, -3
MetaspriteData "SAMUS_BEAM_2", SmSAMUS_BEAM_2Left, SmSAMUS_BEAM_2Right
SmSAMUS_BEAM_2Left:
  .byte 4
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_4}, $80, -4, -4
SmSAMUS_BEAM_2Right:
  .byte 4
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_4}, $c0, -4, -4
MetaspriteData "SAMUS_BEAM_2_UP", SmSAMUS_BEAM_2_UPLeft, SmSAMUS_BEAM_2_UPRight
SmSAMUS_BEAM_2_UPLeft:
  .byte 4
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_4}, $c0, -3, -4
SmSAMUS_BEAM_2_UPRight:
  .byte 4
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_4}, $80, -3, -4
MetaspriteData "SAMUS_BEAM_3", SmSAMUS_BEAM_3Left, SmSAMUS_BEAM_3Right
SmSAMUS_BEAM_3Left = SmSAMUS_BEAM_1Left
SmSAMUS_BEAM_3Right = SmSAMUS_BEAM_1Right
MetaspriteData "SAMUS_BEAM_3_UP", SmSAMUS_BEAM_3_UPLeft, SmSAMUS_BEAM_3_UPRight
SmSAMUS_BEAM_3_UPLeft = SmSAMUS_BEAM_1_UPLeft
SmSAMUS_BEAM_3_UPRight = SmSAMUS_BEAM_1_UPRight
MetaspriteData "SAMUS_BEAM_4", SmSAMUS_BEAM_4Left, SmSAMUS_BEAM_4Right
SmSAMUS_BEAM_4Left = SmSAMUS_BEAM_2Left
SmSAMUS_BEAM_4Right = SmSAMUS_BEAM_2Right
MetaspriteData "SAMUS_BEAM_4_UP", SmSAMUS_BEAM_4_UPLeft, SmSAMUS_BEAM_4_UPRight
SmSAMUS_BEAM_4_UPLeft = SmSAMUS_BEAM_2_UPLeft
SmSAMUS_BEAM_4_UPRight = SmSAMUS_BEAM_2_UPRight
MetaspriteData "SAMUS_BEAM_5", SmSAMUS_BEAM_5Left, SmSAMUS_BEAM_5Right
SmSAMUS_BEAM_5Left:
  .byte 8
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_4}, $c0, -4, -4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_4}, $83, -3, -5
SmSAMUS_BEAM_5Right:
  .byte 8
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_4}, $80, -4, -4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_4}, $c3, -3, -3
MetaspriteData "SAMUS_BEAM_5_UP", SmSAMUS_BEAM_5_UPLeft, SmSAMUS_BEAM_5_UPRight
SmSAMUS_BEAM_5_UPLeft = SmSAMUS_BEAM_5Left
SmSAMUS_BEAM_5_UPRight = SmSAMUS_BEAM_5Right
MetaspriteData "SAMUS_BEAM_6", SmSAMUS_BEAM_6Left, SmSAMUS_BEAM_6Right
SmSAMUS_BEAM_6Left:
  .byte 4
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_4}, $80, -4, -4
SmSAMUS_BEAM_6Right:
  .byte 4
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_4}, $c0, -4, -4
MetaspriteData "SAMUS_BEAM_6_UP", SmSAMUS_BEAM_6_UPLeft, SmSAMUS_BEAM_6_UPRight
SmSAMUS_BEAM_6_UPLeft:
  .byte 4
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_4}, $c0, -3, -4
SmSAMUS_BEAM_6_UPRight:
  .byte 4
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_4}, $80, -3, -4
MetaspriteData "SAMUS_BOMB_1", SmSAMUS_BOMB_1Left, SmSAMUS_BOMB_1Right
SmSAMUS_BOMB_1Left:
  .byte 8
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_4}, $80, -4, -4
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_4}, $83, -2, -6
SmSAMUS_BOMB_1Right:
  .byte 8
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_4}, $c0, -4, -4
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_4}, $c3, -2, -2
MetaspriteData "SAMUS_BOMB_2", SmSAMUS_BOMB_2Left, SmSAMUS_BOMB_2Right
SmSAMUS_BOMB_2Left:
  .byte 8
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_4}, $80, -4, -4
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_4}, $83, -2, -6
SmSAMUS_BOMB_2Right:
  .byte 8
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_4}, $c0, -4, -4
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_4}, $c3, -2, -2
MetaspriteData "SAMUS_BOMB_3", SmSAMUS_BOMB_3Left, SmSAMUS_BOMB_3Right
SmSAMUS_BOMB_3Left:
  .byte 8
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_4}, $c0, -5, -3
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_4}, $80, -5, -11
SmSAMUS_BOMB_3Right:
  .byte 8
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_4}, $80, -5, -5
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_4}, $c0, -5, 3
MetaspriteData "SAMUS_BOMB_4", SmSAMUS_BOMB_4Left, SmSAMUS_BOMB_4Right
SmSAMUS_BOMB_4Left:
  .byte 8
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_4}, $40, -8, 0
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_4}, $00, -8, -8
SmSAMUS_BOMB_4Right:
  .byte 8
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_4}, $00, -8, -8
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_4}, $40, -8, 0
MetaspriteData "SAMUS_BOMB_5", SmSAMUS_BOMB_5Left, SmSAMUS_BOMB_5Right
SmSAMUS_BOMB_5Left:
  .byte 32
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_4}, $40, -16, 8
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_4}, $80, -16, 0
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_4}, $c0, -16, -8
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_4}, $00, -16, -16
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_4}, $c0, 0, 8
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_4}, $00, 0, 0
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_4}, $40, 0, -8
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_4}, $80, 0, -16
SmSAMUS_BOMB_5Right:
  .byte 32
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_4}, $00, -16, -16
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_4}, $c0, -16, -8
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_4}, $80, -16, 0
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_4}, $40, -16, 8
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_4}, $80, 0, -16
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_4}, $40, 0, -8
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_4}, $00, 0, 0
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_4}, $c0, 0, 8
MetaspriteData "SAMUS_BOMB_6", SmSAMUS_BOMB_6Left, SmSAMUS_BOMB_6Right
SmSAMUS_BOMB_6Left = SmSAMUS_BOMB_5Left
SmSAMUS_BOMB_6Right = SmSAMUS_BOMB_5Right
SamusWeaponFamilies:
 .byte 0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1
SmGuts0_0Right:
  .byte 4
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $c0, -4, -4
SmGuts0_1Right:
  .byte 4
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $c0, -4, -4
SmGuts0_2Right:
  .byte 4
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $80, -4, -4
SmGuts0_3Right:
  .byte 4
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c0, -4, -3
SmGuts0_4Right:
  .byte 4
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c0, -4, -4
SmGuts0_5Right:
  .byte 4
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $c0, -4, -4
SmGuts1_0Right = SmGuts0_0Right
SmGuts1_1Right = SmGuts0_1Right
SmGuts1_2Right = SmGuts0_2Right
SmGuts1_3Right = SmGuts0_3Right
SmGuts1_4Right:
  .byte 4
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $80, -4, -4
SmGuts1_5Right = SmGuts0_5Right
SmGuts2_0Right:
  .byte 4
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $80, -4, -4
SmGuts2_1Right:
  .byte 4
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $80, -4, -4
SmGuts2_2Right:
  .byte 4
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $c0, -4, -4
SmGuts2_3Right:
  .byte 4
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $80, -4, -3
SmGuts2_4Right = SmGuts0_4Right
SmGuts2_5Right:
  .byte 4
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $80, -4, -4
SmGuts3_0Right = SmGuts2_0Right
SmGuts3_1Right = SmGuts2_1Right
SmGuts3_2Right = SmGuts2_2Right
SmGuts3_3Right = SmGuts0_3Right
SmGuts3_4Right = SmGuts1_4Right
SmGuts3_5Right = SmGuts2_5Right
SamusGutsLo:
  .byte <SmGuts0_0Right,<SmGuts0_1Right,<SmGuts0_2Right,<SmGuts0_3Right,<SmGuts0_4Right,<SmGuts0_5Right,<SmGuts1_0Right,<SmGuts1_1Right,<SmGuts1_2Right,<SmGuts1_3Right,<SmGuts1_4Right,<SmGuts1_5Right,<SmGuts2_0Right,<SmGuts2_1Right,<SmGuts2_2Right,<SmGuts2_3Right,<SmGuts2_4Right,<SmGuts2_5Right,<SmGuts3_0Right,<SmGuts3_1Right,<SmGuts3_2Right,<SmGuts3_3Right,<SmGuts3_4Right,<SmGuts3_5Right
SamusGutsHi:
  .byte >SmGuts0_0Right,>SmGuts0_1Right,>SmGuts0_2Right,>SmGuts0_3Right,>SmGuts0_4Right,>SmGuts0_5Right,>SmGuts1_0Right,>SmGuts1_1Right,>SmGuts1_2Right,>SmGuts1_3Right,>SmGuts1_4Right,>SmGuts1_5Right,>SmGuts2_0Right,>SmGuts2_1Right,>SmGuts2_2Right,>SmGuts2_3Right,>SmGuts2_4Right,>SmGuts2_5Right,>SmGuts3_0Right,>SmGuts3_1Right,>SmGuts3_2Right,>SmGuts3_3Right,>SmGuts3_4Right,>SmGuts3_5Right
.popseg
SAMUS_CHR_FIRST = $91
SAMUS_CHR_DEATH = $a3
SAMUS_CHR_END = $a7
SAMUS_POSE_COUNT = 31
SAMUS_MAX_SPRITES = 14
SM_POSE_STAND = 0
SM_POSE_SHOOT = 1
SM_POSE_WALK1 = 2
SM_POSE_WALK2 = 3
SM_POSE_WALK3 = 4
SM_POSE_WALKSHOOT1 = 5
SM_POSE_WALKSHOOT2 = 6
SM_POSE_WALKSHOOT3 = 7
SM_POSE_UPSTAND = 8
SM_POSE_UPSHOOT = 9
SM_POSE_UPWALK1 = 10
SM_POSE_UPWALK2 = 11
SM_POSE_UPWALK3 = 12
SM_POSE_UPWALKSHOOT1 = 13
SM_POSE_UPWALKSHOOT2 = 14
SM_POSE_UPWALKSHOOT3 = 15
SM_POSE_JUMP = 16
SM_POSE_JUMPSHOOT = 17
SM_POSE_UPJUMP = 18
SM_POSE_UPJUMPSHOOT = 19
SM_POSE_FLIP1 = 20
SM_POSE_FLIP2 = 21
SM_POSE_FLIP3 = 22
SM_POSE_FLIP4 = 23
SM_POSE_SLIDE = 24
SM_POSE_CLIMB1 = 25
SM_POSE_CLIMB2 = 26
SM_POSE_BALL1 = 27
SM_POSE_BALL2 = 28
SM_POSE_BALL3 = 29
SM_POSE_BALL4 = 30
SM_POSE_CROUCH = 31
SM_POSE_CROUCHSHOOT = 32
