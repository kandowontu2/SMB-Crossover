; Source-composed Bass arms and Pharaoh body layers.
.pushseg
.segment "XG_BASS_GFX"
SsBassPHARAOH_STANDLeft:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $42, 7, 9
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $42, 7, 1
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $82, 7, -7
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c2, 23, 9
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c2, 23, 1
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $82, 23, -7
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $47, 6, 10
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $03, 6, 2
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $87, 6, -6
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $87, 22, 10
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c7, 22, 2
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $87, 22, -6
SsBassPHARAOH_STANDRight:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $02, 7, -1
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $02, 7, 7
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $c2, 7, 15
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $82, 23, -1
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $82, 23, 7
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $c2, 23, 15
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $07, 6, -2
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $43, 6, 6
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c7, 6, 14
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c7, 22, -2
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $87, 22, 6
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c7, 22, 14
SsBassPHARAOH_WALK1Left:
  .byte 44
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $42, 9, 13
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $42, 9, 5
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $82, 9, -3
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c2, 25, 13
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $82, 25, 5
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $47, 8, 14
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c3, 8, 6
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $83, 8, -2
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c7, 24, 14
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c7, 24, 6
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $87, 24, -2
SsBassPHARAOH_WALK1Right:
  .byte 44
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $02, 9, -5
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $02, 9, 3
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c2, 9, 11
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $82, 25, -5
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $c2, 25, 3
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $07, 8, -6
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $83, 8, 2
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c3, 8, 10
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $87, 24, -6
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $87, 24, 2
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c7, 24, 10
SsBassPHARAOH_WALK2Left:
  .byte 36
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $42, 7, 16
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $42, 7, 8
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $82, 7, 0
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $82, 23, 8
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $47, 6, 12
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $03, 6, 4
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $87, 6, -4
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c7, 22, 12
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $87, 22, 4
SsBassPHARAOH_WALK2Right:
  .byte 36
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $02, 7, -8
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $02, 7, 0
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c2, 7, 8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c2, 23, 0
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $07, 6, -4
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $43, 6, 4
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c7, 6, 12
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $87, 22, -4
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $c7, 22, 4
SsBassPHARAOH_WALK3Left:
  .byte 44
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $42, 1, 10
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $42, 1, 2
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $42, 17, 18
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $82, 17, 10
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $82, 17, 2
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $47, 8, 15
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $83, 8, 7
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c3, 8, -1
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c7, 24, 15
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c7, 24, 7
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $87, 24, -1
SsBassPHARAOH_WALK3Right:
  .byte 44
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $02, 1, -2
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $02, 1, 6
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $02, 17, -10
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c2, 17, -2
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c2, 17, 6
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $07, 8, -7
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $c3, 8, 1
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $83, 8, 9
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $87, 24, -7
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $87, 24, 1
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c7, 24, 9
SsBassPHARAOH_JUMPLeft:
  .byte 44
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $42, -1, 11
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $02, -1, 3
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $c2, 15, 11
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c2, 15, 3
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $82, 15, -5
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $47, 0, 17
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $43, 0, 9
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $03, 0, 1
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c7, 16, 9
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $07, 16, 1
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $87, 16, -7
SsBassPHARAOH_JUMPRight:
  .byte 44
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $02, -1, -3
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $42, -1, 5
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $82, 15, -3
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $82, 15, 5
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c2, 15, 13
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $07, 0, -9
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $03, 0, -1
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $43, 0, 7
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $87, 16, -1
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $47, 16, 7
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c7, 16, 15
SsBassPHARAOH_CROUCHLeft = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_CROUCHRight = SsBassPHARAOH_STANDRight
SsBassPHARAOH_ATTACK1Left:
  .byte 44
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $42, -1, 8
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $42, -1, 0
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c2, 15, 16
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c2, 15, 8
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $82, 15, 0
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $47, 6, 10
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $03, 6, 2
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $87, 6, -6
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $87, 22, 10
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c7, 22, 2
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $07, 22, -6
SsBassPHARAOH_ATTACK1Right:
  .byte 44
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $02, -1, 0
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $02, -1, 8
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $82, 15, -8
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $82, 15, 0
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c2, 15, 8
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $07, 6, -2
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $43, 6, 6
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c7, 6, 14
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c7, 22, -2
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $87, 22, 6
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $47, 22, 14
SsBassPHARAOH_ATTACK2Left = SsBassPHARAOH_ATTACK1Left
SsBassPHARAOH_ATTACK2Right = SsBassPHARAOH_ATTACK1Right
SsBassPHARAOH_ATTACK3Left = SsBassPHARAOH_ATTACK1Left
SsBassPHARAOH_ATTACK3Right = SsBassPHARAOH_ATTACK1Right
SsBassPHARAOH_CLIMB1Left:
  .byte 36
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $c2, 4, 8
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $82, 4, 0
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $82, 20, 8
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $82, 20, 0
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $47, 3, 9
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $c7, 3, 1
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $07, 3, -7
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c7, 19, 9
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $87, 19, 1
SsBassPHARAOH_CLIMB1Right:
  .byte 36
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $82, 4, 0
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $c2, 4, 8
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $c2, 20, 0
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c2, 20, 8
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $07, 3, -1
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $87, 3, 7
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $47, 3, 15
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $87, 19, -1
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c7, 19, 7
SsBassPHARAOH_CLIMB2Left:
  .byte 28
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $82, 9, 7
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $82, 9, -1
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $82, 25, -1
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $47, 8, 8
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $07, 8, 0
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $87, 24, 8
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $87, 24, 0
SsBassPHARAOH_CLIMB2Right:
  .byte 28
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c2, 9, 1
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c2, 9, 9
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c2, 25, 9
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $07, 8, 0
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $47, 8, 8
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c7, 24, 0
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c7, 24, 8
SsBassPHARAOH_HURTLeft:
  .byte 36
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $42, 2, 11
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $02, 2, 3
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c2, 18, 11
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c2, 18, 3
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $47, 1, 17
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $43, 1, 9
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $03, 1, 1
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c7, 17, 9
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $87, 17, 1
SsBassPHARAOH_HURTRight:
  .byte 36
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $02, 2, -3
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $42, 2, 5
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $82, 18, -3
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $82, 18, 5
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $07, 1, -9
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $03, 1, -1
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $43, 1, 7
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $87, 17, -1
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c7, 17, 7
SsBassPHARAOH_DIELeft = SsBassPHARAOH_HURTLeft
SsBassPHARAOH_DIERight = SsBassPHARAOH_HURTRight
SsBassPHARAOH_DASHLeft = SsBassPHARAOH_WALK1Left
SsBassPHARAOH_DASHRight = SsBassPHARAOH_WALK1Right
SsBassPHARAOH_UPLeft:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $42, 7, 16
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $02, 7, 8
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $82, 7, 0
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c2, 23, 16
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c2, 23, 8
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $82, 23, 0
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $43, 6, 17
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $43, 6, 9
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $87, 6, 1
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c7, 22, 17
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $87, 22, 9
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $87, 22, 1
SsBassPHARAOH_UPRight:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $02, 7, -8
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $42, 7, 0
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $c2, 7, 8
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $82, 23, -8
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $82, 23, 0
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $c2, 23, 8
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $03, 6, -9
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $03, 6, -1
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c7, 6, 7
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $87, 22, -9
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c7, 22, -1
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c7, 22, 7
SsBassPHARAOH_DIAGUPLeft:
  .byte 56
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $42, 7, 14
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $42, 7, 6
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $82, 7, -2
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $82, 7, -10
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $c2, 23, 14
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c2, 23, 6
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $82, 23, -2
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $47, 6, 15
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $83, 6, 7
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $83, 6, -1
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $87, 6, -9
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $87, 22, 15
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c7, 22, 7
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $87, 22, -1
SsBassPHARAOH_DIAGUPRight:
  .byte 56
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $02, 7, -6
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $02, 7, 2
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c2, 7, 10
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c2, 7, 18
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $82, 23, -6
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $82, 23, 2
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c2, 23, 10
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $07, 6, -7
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c3, 6, 1
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c3, 6, 9
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c7, 6, 17
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c7, 22, -7
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $87, 22, 1
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c7, 22, 9
SsBassPHARAOH_DIAGDOWNLeft:
  .byte 64
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $42, -3, 11
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $42, -3, 3
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $02, -3, -5
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $42, 13, 11
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $42, 13, 3
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $02, 13, -5
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $c2, 29, 19
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $82, 29, 11
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $82, 29, 3
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $47, 5, 15
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $03, 5, 7
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $43, 5, -1
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $87, 21, 15
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $c7, 21, 7
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $87, 21, -1
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $87, 21, -9
SsBassPHARAOH_DIAGDOWNRight:
  .byte 64
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $02, -3, -3
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $02, -3, 5
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $42, -3, 13
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $02, 13, -3
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $02, 13, 5
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $42, 13, 13
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $82, 29, -11
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c2, 29, -3
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c2, 29, 5
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $07, 5, -7
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $43, 5, 1
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $03, 5, 9
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c7, 21, -7
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $87, 21, 1
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c7, 21, 9
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c7, 21, 17
SsBassPHARAOH_THROWLeft = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_THROWRight = SsBassPHARAOH_STANDRight
SsBassPHARAOH_WALLLeft = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_WALLRight = SsBassPHARAOH_STANDRight
SsBassPHARAOH_CEILINGLeft = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_CEILINGRight = SsBassPHARAOH_STANDRight
SsBassPHARAOH_HOVERLeft = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_HOVERRight = SsBassPHARAOH_STANDRight
SsBassPHARAOH_CROUCHSHOOTLeft = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_CROUCHSHOOTRight = SsBassPHARAOH_STANDRight
SsBassPHARAOH_JUMPSHOOTLeft:
  .byte 44
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $42, 2, 11
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $02, 2, 3
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $02, 2, -5
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c2, 18, 11
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c2, 18, 3
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $47, 1, 17
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $43, 1, 9
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $03, 1, 1
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $87, 1, -7
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c7, 17, 9
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $87, 17, 1
SsBassPHARAOH_JUMPSHOOTRight:
  .byte 44
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $02, 2, -3
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $42, 2, 5
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $42, 2, 13
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $82, 18, -3
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $82, 18, 5
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $07, 1, -9
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $03, 1, -1
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $43, 1, 7
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c7, 1, 15
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $87, 17, -1
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c7, 17, 7
SsBassPHARAOH_JUMPUPLeft:
  .byte 48
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $42, 1, 12
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $02, 1, 4
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $82, 1, -4
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c2, 17, 12
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $82, 17, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $82, 17, -4
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $43, 0, 13
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $43, 0, 5
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $87, 0, -3
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c7, 16, 13
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $07, 16, 5
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $87, 16, -3
SsBassPHARAOH_JUMPUPRight:
  .byte 48
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $02, 1, -4
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $42, 1, 4
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c2, 1, 12
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $82, 17, -4
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c2, 17, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c2, 17, 12
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $03, 0, -5
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $03, 0, 3
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c7, 0, 11
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $87, 16, -5
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $47, 16, 3
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c7, 16, 11
SsBassPHARAOH_CROUCHATTACK1Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_CROUCHATTACK1Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_CROUCHATTACK2Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_CROUCHATTACK2Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_CROUCHATTACK3Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_CROUCHATTACK3Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_JUMPATTACK1Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_JUMPATTACK1Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_JUMPATTACK2Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_JUMPATTACK2Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_JUMPATTACK3Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_JUMPATTACK3Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_JUMPDIAGUPLeft:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $42, 1, 13
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $42, 1, 5
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $c2, 1, -3
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $82, 1, -11
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $82, 17, 5
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $82, 17, -3
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $c7, 0, 14
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $83, 0, 6
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $83, 0, -2
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $87, 0, -10
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $07, 16, 6
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c7, 16, -2
SsBassPHARAOH_JUMPDIAGUPRight:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $02, 1, -5
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $02, 1, 3
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $82, 1, 11
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c2, 1, 19
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c2, 17, 3
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $c2, 17, 11
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $87, 0, -6
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c3, 0, 2
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c3, 0, 10
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c7, 0, 18
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $47, 16, 2
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $87, 16, 10
SsBassPHARAOH_JUMPDIAGDOWNLeft:
  .byte 52
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $42, 1, 13
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $42, 1, 5
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $02, 1, -3
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $82, 17, 5
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $82, 17, -3
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $82, 17, -11
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $47, -1, 14
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $03, -1, 6
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $03, -1, -2
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $07, 15, 6
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c7, 15, -2
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $87, 15, -10
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $87, 31, 6
SsBassPHARAOH_JUMPDIAGDOWNRight:
  .byte 52
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $02, 1, -5
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $02, 1, 3
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $42, 1, 11
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c2, 17, 3
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $c2, 17, 11
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c2, 17, 19
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $07, -1, -6
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $43, -1, 2
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $43, -1, 10
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $47, 15, 2
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $87, 15, 10
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c7, 15, 18
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c7, 31, 2
SsBassPHARAOH_HOVERSMALLLeft = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_HOVERSMALLRight = SsBassPHARAOH_STANDRight
SsBassPHARAOH_DEATH1Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_DEATH1Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_DEATH2Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_DEATH2Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_DEATH3Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_DEATH3Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_DEATH4Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_DEATH4Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_RYUSLASH1Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_RYUSLASH1Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_RYUSLASH2Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_RYUSLASH2Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_RYUSLASH3Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_RYUSLASH3Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_RYUSLASH4Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_RYUSLASH4Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_RYUSLASH5Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_RYUSLASH5Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_DUCKSLASH1Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_DUCKSLASH1Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_DUCKSLASH2Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_DUCKSLASH2Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_DUCKSLASH3Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_DUCKSLASH3Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_DUCKSLASH4Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_DUCKSLASH4Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_DUCKSLASH5Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_DUCKSLASH5Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_AIRSLASH1Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_AIRSLASH1Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_AIRSLASH2Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_AIRSLASH2Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_AIRSLASH3Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_AIRSLASH3Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_AIRSLASH4Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_AIRSLASH4Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_AIRSLASH5Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_AIRSLASH5Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_RYUTHROW1Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_RYUTHROW1Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_RYUTHROW2Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_RYUTHROW2Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_RYUTHROW3Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_RYUTHROW3Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_RYUTHROW4Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_RYUTHROW4Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_RYUTHROW5Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_RYUTHROW5Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_DUCKTHROW1Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_DUCKTHROW1Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_DUCKTHROW2Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_DUCKTHROW2Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_DUCKTHROW3Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_DUCKTHROW3Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_DUCKTHROW4Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_DUCKTHROW4Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_DUCKTHROW5Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_DUCKTHROW5Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_AIRTHROW1Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_AIRTHROW1Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_AIRTHROW2Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_AIRTHROW2Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_AIRTHROW3Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_AIRTHROW3Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_AIRTHROW4Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_AIRTHROW4Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_AIRTHROW5Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_AIRTHROW5Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_WALLTHROW1Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_WALLTHROW1Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_WALLTHROW2Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_WALLTHROW2Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_WALLTHROW3Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_WALLTHROW3Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_WALLTHROW4Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_WALLTHROW4Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_WALLTHROW5Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_WALLTHROW5Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_BACKTHROW1Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_BACKTHROW1Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_BACKTHROW2Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_BACKTHROW2Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_BACKTHROW3Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_BACKTHROW3Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_BACKTHROW4Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_BACKTHROW4Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_BACKTHROW5Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_BACKTHROW5Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_WALKSTEPLeft:
  .byte 44
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $42, 0, 9
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $42, 0, 1
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $c2, 16, 17
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $82, 16, 9
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $02, 16, 1
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $47, 6, 15
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $83, 6, 7
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $83, 6, -1
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $87, 22, 15
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c7, 22, 7
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $87, 22, -1
SsBassPHARAOH_WALKSTEPRight:
  .byte 44
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $02, 0, -1
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $02, 0, 7
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $82, 16, -9
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c2, 16, -1
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $42, 16, 7
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $07, 6, -7
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $c3, 6, 1
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c3, 6, 9
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c7, 22, -7
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $87, 22, 1
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c7, 22, 9
SsBassPHARAOH_FLAP1Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_FLAP1Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_FLAP2Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_FLAP2Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_FLAPSHOT1Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_FLAPSHOT1Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_FLAPSHOT2Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_FLAPSHOT2Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_FLAPUP1Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_FLAPUP1Right = SsBassPHARAOH_STANDRight
SsBassPHARAOH_FLAPUP2Left = SsBassPHARAOH_STANDLeft
SsBassPHARAOH_FLAPUP2Right = SsBassPHARAOH_STANDRight
SsBassARM_THROWLeft:
  .byte 60
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $40, 5, 10
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $00, 5, 2
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $40, 5, -6
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $80, 21, 10
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c0, 21, 2
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $80, 21, -6
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $80, 21, -14
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $42, -2, -3
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $82, 14, 5
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $82, 14, -3
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $02, 14, -11
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c2, 30, 13
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $82, 30, 5
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c2, 30, -3
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $43, 5, -2
SsBassARM_THROWRight:
  .byte 60
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 5, -2
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $40, 5, 6
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 5, 14
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c0, 21, -2
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $80, 21, 6
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $c0, 21, 14
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c0, 21, 22
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $02, -2, 11
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c2, 14, 3
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c2, 14, 11
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $42, 14, 19
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $82, 30, -5
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c2, 30, 3
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $82, 30, 11
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $03, 5, 10
SsBassPHARAOH_ARM_THROWLeft:
  .byte 64
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $42, -3, 6
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $42, -3, -2
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $02, -3, -10
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $42, 13, 6
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $42, 13, -2
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $02, 13, -10
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $c2, 29, 14
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $82, 29, 6
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $82, 29, -2
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $47, 5, 10
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $03, 5, 2
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $43, 5, -6
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $87, 21, 10
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $c7, 21, 2
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $87, 21, -6
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $87, 21, -14
SsBassPHARAOH_ARM_THROWRight:
  .byte 64
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $02, -3, 2
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $02, -3, 10
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $42, -3, 18
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $02, 13, 2
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $02, 13, 10
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $42, 13, 18
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $82, 29, -6
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c2, 29, 2
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c2, 29, 10
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $07, 5, -2
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $43, 5, 6
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $03, 5, 14
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c7, 21, -2
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $87, 21, 6
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c7, 21, 14
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c7, 21, 22
SsBassARM_AIR_THROWLeft:
  .byte 40
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $40, 1, 16
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $40, 1, 8
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $40, 1, 0
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $40, 1, -8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c0, 17, 8
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $80, 17, 0
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c2, 2, -1
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $02, 2, -9
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $82, 18, 7
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $02, 18, -1
SsBassARM_AIR_THROWRight:
  .byte 40
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 1, -8
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 1, 0
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 1, 8
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $00, 1, 16
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $80, 17, 0
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c0, 17, 8
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $82, 2, 9
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $42, 2, 17
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c2, 18, 1
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $42, 18, 9
SsBassPHARAOH_ARM_AIR_THROWLeft:
  .byte 44
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $42, 2, 10
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $42, 2, 2
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c2, 2, -6
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c2, 18, 10
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c2, 18, 2
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $47, 1, 16
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $47, 1, 8
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $87, 1, 0
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $47, 1, -8
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c7, 17, 8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $87, 17, 0
SsBassPHARAOH_ARM_AIR_THROWRight:
  .byte 44
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $02, 2, -2
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $02, 2, 6
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $82, 2, 14
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $82, 18, -2
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $82, 18, 6
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $07, 1, -8
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $07, 1, 0
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c7, 1, 8
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $07, 1, 16
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $87, 17, 0
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c7, 17, 8
SsBassARM_FISTLeft:
  .byte 56
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, 1, 10
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 1, 2
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $40, 1, -6
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $80, 17, 10
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c0, 17, 2
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $80, 17, -6
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $80, 17, -14
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $02, 0, 1
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $02, 0, -7
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $82, 16, 9
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c2, 16, 1
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $82, 16, -7
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $82, 16, -15
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $83, 10, -2
SsBassARM_FISTRight:
  .byte 56
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 1, -2
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, 1, 6
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 1, 14
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c0, 17, -2
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $80, 17, 6
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $c0, 17, 14
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $c0, 17, 22
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $42, 0, 7
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $42, 0, 15
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c2, 16, -1
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $82, 16, 7
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c2, 16, 15
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c2, 16, 23
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $c3, 10, 10
SsBassPHARAOH_ARM_FISTLeft:
  .byte 52
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $42, 0, 4
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $42, 0, -4
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $c2, 16, 12
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $82, 16, 4
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $02, 16, -4
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $82, 16, -12
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $47, 1, 10
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $03, 1, 2
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $43, 1, -6
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $87, 17, 10
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c3, 17, 2
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $83, 17, -6
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $87, 17, -14
SsBassPHARAOH_ARM_FISTRight:
  .byte 52
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $02, 0, 4
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $02, 0, 12
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $82, 16, -4
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c2, 16, 4
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $42, 16, 12
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c2, 16, 20
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $07, 1, -2
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $43, 1, 6
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $03, 1, 14
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c7, 17, -2
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $83, 17, 6
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c3, 17, 14
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c7, 17, 22
SsBassARM_AIR_FISTLeft:
  .byte 56
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $c0, 0, 13
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 0, 5
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $80, 0, -3
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 0, -11
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $80, 16, 5
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $c0, 16, -3
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $42, -6, 15
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $42, -6, 7
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $02, -6, -1
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c2, 10, 7
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c2, 10, -1
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $82, 10, -9
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c2, 26, 7
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $83, 4, 3
SsBassARM_AIR_FISTRight:
  .byte 56
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $80, 0, -5
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, 0, 3
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $c0, 0, 11
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $40, 0, 19
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c0, 16, 3
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $80, 16, 11
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $02, -6, -7
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $02, -6, 1
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $42, -6, 9
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $82, 10, 1
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $82, 10, 9
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c2, 10, 17
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $82, 26, 1
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $c3, 4, 5
SsBassPHARAOH_ARM_AIR_FISTLeft:
  .byte 48
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $42, 1, 12
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $42, 1, 4
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $c2, 1, -4
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $02, 1, -12
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $82, 17, 4
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $82, 17, -4
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c7, 0, 13
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $83, 0, 5
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $87, 0, -3
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $07, 0, -11
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $07, 16, 5
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c7, 16, -3
SsBassPHARAOH_ARM_AIR_FISTRight:
  .byte 48
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $02, 1, -4
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $02, 1, 4
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $82, 1, 12
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $42, 1, 20
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c2, 17, 4
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c2, 17, 12
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $87, 0, -5
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c3, 0, 3
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c7, 0, 11
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $47, 0, 19
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $47, 16, 3
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $87, 16, 11
SsBassARM_CARRYLeft:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, 6, 11
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 6, 3
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $80, 6, -5
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $80, 22, 11
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c0, 22, 3
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $80, 22, -5
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $42, 3, 5
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $02, 3, -3
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c2, 19, 13
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c2, 19, 5
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $82, 19, -3
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $83, 10, 3
SsBassARM_CARRYRight:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 6, -3
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, 6, 5
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $c0, 6, 13
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c0, 22, -3
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $80, 22, 5
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $c0, 22, 13
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $02, 3, 3
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $42, 3, 11
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $82, 19, -5
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $82, 19, 3
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c2, 19, 11
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c3, 10, 5
SsBassPHARAOH_ARM_CARRYLeft:
  .byte 48
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $42, 7, 10
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $42, 7, 2
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $82, 7, -6
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c2, 23, 10
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $c2, 23, 2
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $82, 23, -6
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $47, 6, 11
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $03, 6, 3
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $87, 6, -5
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $87, 22, 11
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c7, 22, 3
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $87, 22, -5
SsBassPHARAOH_ARM_CARRYRight:
  .byte 48
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $02, 7, -2
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $02, 7, 6
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c2, 7, 14
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $82, 23, -2
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $82, 23, 6
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c2, 23, 14
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $07, 6, -3
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $43, 6, 5
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c7, 6, 13
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c7, 22, -3
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $87, 22, 5
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c7, 22, 13
SsBassARM_CARRY_STEPLeft:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, 6, 11
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 6, 3
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $80, 6, -5
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $80, 22, 11
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 22, 3
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $80, 22, -5
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $42, 3, 5
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $02, 3, -3
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c2, 19, 13
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c2, 19, 5
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $82, 19, -3
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $83, 10, 3
SsBassARM_CARRY_STEPRight:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 6, -3
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, 6, 5
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $c0, 6, 13
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c0, 22, -3
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 22, 5
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c0, 22, 13
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $02, 3, 3
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $42, 3, 11
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $82, 19, -5
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $82, 19, 3
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c2, 19, 11
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c3, 10, 5
SsBassPHARAOH_ARM_CARRY_STEPLeft:
  .byte 48
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $42, 7, 10
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $42, 7, 2
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $82, 7, -6
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c2, 23, 10
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $82, 23, 2
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $82, 23, -6
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $47, 6, 11
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $03, 6, 3
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $87, 6, -5
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $87, 22, 11
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c7, 22, 3
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $87, 22, -5
SsBassPHARAOH_ARM_CARRY_STEPRight:
  .byte 48
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $02, 7, -2
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $02, 7, 6
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c2, 7, 14
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $82, 23, -2
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c2, 23, 6
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c2, 23, 14
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $07, 6, -3
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $43, 6, 5
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c7, 6, 13
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c7, 22, -3
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $87, 22, 5
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c7, 22, 13
SsBassARM_CARRY_WALK1Left:
  .byte 44
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, 8, 12
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 8, 4
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 8, -4
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c0, 24, 12
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c0, 24, 4
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $80, 24, -4
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $02, 0, -3
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c2, 16, 13
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c2, 16, 5
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $82, 16, -3
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $83, 12, 2
SsBassARM_CARRY_WALK1Right:
  .byte 44
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 8, -4
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, 8, 4
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $40, 8, 12
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $80, 24, -4
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $80, 24, 4
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $c0, 24, 12
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $42, 0, 11
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $82, 16, -5
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $82, 16, 3
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c2, 16, 11
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c3, 12, 6
SsBassPHARAOH_ARM_CARRY_WALK1Left:
  .byte 44
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $42, 9, 11
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $42, 9, 3
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $02, 9, -5
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c2, 25, 11
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $82, 25, 3
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $47, 8, 12
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c3, 8, 4
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $07, 8, -4
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c7, 24, 12
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c7, 24, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $87, 24, -4
SsBassPHARAOH_ARM_CARRY_WALK1Right:
  .byte 44
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $02, 9, -3
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $02, 9, 5
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $42, 9, 13
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $82, 25, -3
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c2, 25, 5
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $07, 8, -4
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $83, 8, 4
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $47, 8, 12
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $87, 24, -4
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $87, 24, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c7, 24, 12
SsBassARM_CARRY_WALK2Left:
  .byte 44
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $40, 6, 10
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 6, 2
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 6, -6
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c0, 22, 10
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $80, 22, 2
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $42, -2, 0
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $02, -2, -8
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c2, 14, 8
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $82, 14, 0
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $c2, 30, 8
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $83, 10, 2
SsBassARM_CARRY_WALK2Right:
  .byte 44
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 6, -2
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $40, 6, 6
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 6, 14
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $80, 22, -2
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c0, 22, 6
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $02, -2, 8
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $42, -2, 16
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $82, 14, 0
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c2, 14, 8
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $82, 30, 0
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c3, 10, 6
SsBassPHARAOH_ARM_CARRY_WALK2Left:
  .byte 36
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $42, 7, 14
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $42, 7, 6
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $02, 7, -2
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $82, 23, 6
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $47, 6, 10
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $03, 6, 2
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $87, 6, -6
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c7, 22, 10
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $87, 22, 2
SsBassPHARAOH_ARM_CARRY_WALK2Right:
  .byte 36
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $02, 7, -6
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $02, 7, 2
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $42, 7, 10
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c2, 23, 2
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $07, 6, -2
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $43, 6, 6
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $c7, 6, 14
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $87, 22, -2
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c7, 22, 6
SsBassARM_CARRY_WALK3Left:
  .byte 44
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $40, 8, 13
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 8, 5
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $80, 8, -3
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c0, 24, 13
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $c0, 24, 5
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $80, 24, -3
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $02, 0, -3
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $c2, 16, 13
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c2, 16, 5
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $82, 16, -3
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c3, 12, 2
SsBassARM_CARRY_WALK3Right:
  .byte 44
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 8, -5
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $40, 8, 3
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c0, 8, 11
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $80, 24, -5
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $80, 24, 3
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c0, 24, 11
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $42, 0, 11
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $82, 16, -5
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $82, 16, 3
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c2, 16, 11
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $83, 12, 6
SsBassPHARAOH_ARM_CARRY_WALK3Left:
  .byte 44
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $42, -1, 7
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $02, -1, -1
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $42, 15, 15
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c2, 15, 7
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $82, 15, -1
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $47, 8, 13
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $83, 8, 5
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $83, 8, -3
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c7, 24, 13
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c7, 24, 5
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $87, 24, -3
SsBassPHARAOH_ARM_CARRY_WALK3Right:
  .byte 44
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $02, -1, 1
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $42, -1, 9
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $02, 15, -7
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $82, 15, 1
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c2, 15, 9
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $07, 8, -5
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c3, 8, 3
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c3, 8, 11
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $87, 24, -5
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $87, 24, 3
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c7, 24, 11
SsBassARM_CARRY_JUMPLeft:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $c0, 0, 13
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 0, 5
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 0, -3
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $80, 0, -11
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $80, 16, 5
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $c0, 16, -3
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $c2, 4, 12
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c2, 4, 4
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $82, 4, -4
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $82, 20, 4
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c2, 20, -4
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $83, 4, 3
SsBassARM_CARRY_JUMPRight:
  .byte 48
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $80, 0, -5
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, 0, 3
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $40, 0, 11
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c0, 0, 19
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c0, 16, 3
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $80, 16, 11
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $82, 4, -4
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $82, 4, 4
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c2, 4, 12
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c2, 20, 4
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $82, 20, 12
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c3, 4, 5
SsBassPHARAOH_ARM_CARRY_JUMPLeft:
  .byte 44
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $42, 1, 12
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $42, 1, 4
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $82, 1, -4
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $82, 17, 4
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $82, 17, -4
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c7, 0, 13
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $83, 0, 5
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $03, 0, -3
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $87, 0, -11
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $87, 16, 5
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c7, 16, -3
SsBassPHARAOH_ARM_CARRY_JUMPRight:
  .byte 44
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $02, 1, -4
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $02, 1, 4
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c2, 1, 12
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c2, 17, 4
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $c2, 17, 12
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $87, 0, -5
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c3, 0, 3
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $43, 0, 11
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c7, 0, 19
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c7, 16, 3
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $87, 16, 11
SsBassLeftLo:
 .byte <SsBassPHARAOH_STANDLeft,<SsBassPHARAOH_WALK1Left,<SsBassPHARAOH_WALK2Left,<SsBassPHARAOH_WALK3Left,<SsBassPHARAOH_JUMPLeft,<SsBassPHARAOH_CROUCHLeft,<SsBassPHARAOH_ATTACK1Left,<SsBassPHARAOH_ATTACK2Left,<SsBassPHARAOH_ATTACK3Left,<SsBassPHARAOH_CLIMB1Left,<SsBassPHARAOH_CLIMB2Left,<SsBassPHARAOH_HURTLeft,<SsBassPHARAOH_DIELeft,<SsBassPHARAOH_DASHLeft,<SsBassPHARAOH_UPLeft,<SsBassPHARAOH_DIAGUPLeft,<SsBassPHARAOH_DIAGDOWNLeft,<SsBassPHARAOH_THROWLeft,<SsBassPHARAOH_WALLLeft,<SsBassPHARAOH_CEILINGLeft,<SsBassPHARAOH_HOVERLeft,<SsBassPHARAOH_CROUCHSHOOTLeft,<SsBassPHARAOH_JUMPSHOOTLeft,<SsBassPHARAOH_JUMPUPLeft,<SsBassPHARAOH_CROUCHATTACK1Left,<SsBassPHARAOH_CROUCHATTACK2Left,<SsBassPHARAOH_CROUCHATTACK3Left,<SsBassPHARAOH_JUMPATTACK1Left,<SsBassPHARAOH_JUMPATTACK2Left,<SsBassPHARAOH_JUMPATTACK3Left,<SsBassPHARAOH_JUMPDIAGUPLeft,<SsBassPHARAOH_JUMPDIAGDOWNLeft,<SsBassPHARAOH_HOVERSMALLLeft,<SsBassPHARAOH_DEATH1Left,<SsBassPHARAOH_DEATH2Left,<SsBassPHARAOH_DEATH3Left,<SsBassPHARAOH_DEATH4Left,<SsBassPHARAOH_RYUSLASH1Left,<SsBassPHARAOH_RYUSLASH2Left,<SsBassPHARAOH_RYUSLASH3Left,<SsBassPHARAOH_RYUSLASH4Left,<SsBassPHARAOH_RYUSLASH5Left,<SsBassPHARAOH_DUCKSLASH1Left,<SsBassPHARAOH_DUCKSLASH2Left,<SsBassPHARAOH_DUCKSLASH3Left,<SsBassPHARAOH_DUCKSLASH4Left,<SsBassPHARAOH_DUCKSLASH5Left,<SsBassPHARAOH_AIRSLASH1Left,<SsBassPHARAOH_AIRSLASH2Left,<SsBassPHARAOH_AIRSLASH3Left,<SsBassPHARAOH_AIRSLASH4Left,<SsBassPHARAOH_AIRSLASH5Left,<SsBassPHARAOH_RYUTHROW1Left,<SsBassPHARAOH_RYUTHROW2Left,<SsBassPHARAOH_RYUTHROW3Left,<SsBassPHARAOH_RYUTHROW4Left,<SsBassPHARAOH_RYUTHROW5Left,<SsBassPHARAOH_DUCKTHROW1Left,<SsBassPHARAOH_DUCKTHROW2Left,<SsBassPHARAOH_DUCKTHROW3Left,<SsBassPHARAOH_DUCKTHROW4Left,<SsBassPHARAOH_DUCKTHROW5Left,<SsBassPHARAOH_AIRTHROW1Left,<SsBassPHARAOH_AIRTHROW2Left,<SsBassPHARAOH_AIRTHROW3Left,<SsBassPHARAOH_AIRTHROW4Left,<SsBassPHARAOH_AIRTHROW5Left,<SsBassPHARAOH_WALLTHROW1Left,<SsBassPHARAOH_WALLTHROW2Left,<SsBassPHARAOH_WALLTHROW3Left,<SsBassPHARAOH_WALLTHROW4Left,<SsBassPHARAOH_WALLTHROW5Left,<SsBassPHARAOH_BACKTHROW1Left,<SsBassPHARAOH_BACKTHROW2Left,<SsBassPHARAOH_BACKTHROW3Left,<SsBassPHARAOH_BACKTHROW4Left,<SsBassPHARAOH_BACKTHROW5Left,<SsBassPHARAOH_WALKSTEPLeft,<SsBassPHARAOH_FLAP1Left,<SsBassPHARAOH_FLAP2Left,<SsBassPHARAOH_FLAPSHOT1Left,<SsBassPHARAOH_FLAPSHOT2Left,<SsBassPHARAOH_FLAPUP1Left,<SsBassPHARAOH_FLAPUP2Left,<SsBassARM_THROWLeft,<SsBassPHARAOH_ARM_THROWLeft,<SsBassARM_AIR_THROWLeft,<SsBassPHARAOH_ARM_AIR_THROWLeft,<SsBassARM_FISTLeft,<SsBassPHARAOH_ARM_FISTLeft,<SsBassARM_AIR_FISTLeft,<SsBassPHARAOH_ARM_AIR_FISTLeft,<SsBassARM_CARRYLeft,<SsBassPHARAOH_ARM_CARRYLeft,<SsBassARM_CARRY_STEPLeft,<SsBassPHARAOH_ARM_CARRY_STEPLeft,<SsBassARM_CARRY_WALK1Left,<SsBassPHARAOH_ARM_CARRY_WALK1Left,<SsBassARM_CARRY_WALK2Left,<SsBassPHARAOH_ARM_CARRY_WALK2Left,<SsBassARM_CARRY_WALK3Left,<SsBassPHARAOH_ARM_CARRY_WALK3Left,<SsBassARM_CARRY_JUMPLeft,<SsBassPHARAOH_ARM_CARRY_JUMPLeft
SsBassLeftHi:
 .byte >SsBassPHARAOH_STANDLeft,>SsBassPHARAOH_WALK1Left,>SsBassPHARAOH_WALK2Left,>SsBassPHARAOH_WALK3Left,>SsBassPHARAOH_JUMPLeft,>SsBassPHARAOH_CROUCHLeft,>SsBassPHARAOH_ATTACK1Left,>SsBassPHARAOH_ATTACK2Left,>SsBassPHARAOH_ATTACK3Left,>SsBassPHARAOH_CLIMB1Left,>SsBassPHARAOH_CLIMB2Left,>SsBassPHARAOH_HURTLeft,>SsBassPHARAOH_DIELeft,>SsBassPHARAOH_DASHLeft,>SsBassPHARAOH_UPLeft,>SsBassPHARAOH_DIAGUPLeft,>SsBassPHARAOH_DIAGDOWNLeft,>SsBassPHARAOH_THROWLeft,>SsBassPHARAOH_WALLLeft,>SsBassPHARAOH_CEILINGLeft,>SsBassPHARAOH_HOVERLeft,>SsBassPHARAOH_CROUCHSHOOTLeft,>SsBassPHARAOH_JUMPSHOOTLeft,>SsBassPHARAOH_JUMPUPLeft,>SsBassPHARAOH_CROUCHATTACK1Left,>SsBassPHARAOH_CROUCHATTACK2Left,>SsBassPHARAOH_CROUCHATTACK3Left,>SsBassPHARAOH_JUMPATTACK1Left,>SsBassPHARAOH_JUMPATTACK2Left,>SsBassPHARAOH_JUMPATTACK3Left,>SsBassPHARAOH_JUMPDIAGUPLeft,>SsBassPHARAOH_JUMPDIAGDOWNLeft,>SsBassPHARAOH_HOVERSMALLLeft,>SsBassPHARAOH_DEATH1Left,>SsBassPHARAOH_DEATH2Left,>SsBassPHARAOH_DEATH3Left,>SsBassPHARAOH_DEATH4Left,>SsBassPHARAOH_RYUSLASH1Left,>SsBassPHARAOH_RYUSLASH2Left,>SsBassPHARAOH_RYUSLASH3Left,>SsBassPHARAOH_RYUSLASH4Left,>SsBassPHARAOH_RYUSLASH5Left,>SsBassPHARAOH_DUCKSLASH1Left,>SsBassPHARAOH_DUCKSLASH2Left,>SsBassPHARAOH_DUCKSLASH3Left,>SsBassPHARAOH_DUCKSLASH4Left,>SsBassPHARAOH_DUCKSLASH5Left,>SsBassPHARAOH_AIRSLASH1Left,>SsBassPHARAOH_AIRSLASH2Left,>SsBassPHARAOH_AIRSLASH3Left,>SsBassPHARAOH_AIRSLASH4Left,>SsBassPHARAOH_AIRSLASH5Left,>SsBassPHARAOH_RYUTHROW1Left,>SsBassPHARAOH_RYUTHROW2Left,>SsBassPHARAOH_RYUTHROW3Left,>SsBassPHARAOH_RYUTHROW4Left,>SsBassPHARAOH_RYUTHROW5Left,>SsBassPHARAOH_DUCKTHROW1Left,>SsBassPHARAOH_DUCKTHROW2Left,>SsBassPHARAOH_DUCKTHROW3Left,>SsBassPHARAOH_DUCKTHROW4Left,>SsBassPHARAOH_DUCKTHROW5Left,>SsBassPHARAOH_AIRTHROW1Left,>SsBassPHARAOH_AIRTHROW2Left,>SsBassPHARAOH_AIRTHROW3Left,>SsBassPHARAOH_AIRTHROW4Left,>SsBassPHARAOH_AIRTHROW5Left,>SsBassPHARAOH_WALLTHROW1Left,>SsBassPHARAOH_WALLTHROW2Left,>SsBassPHARAOH_WALLTHROW3Left,>SsBassPHARAOH_WALLTHROW4Left,>SsBassPHARAOH_WALLTHROW5Left,>SsBassPHARAOH_BACKTHROW1Left,>SsBassPHARAOH_BACKTHROW2Left,>SsBassPHARAOH_BACKTHROW3Left,>SsBassPHARAOH_BACKTHROW4Left,>SsBassPHARAOH_BACKTHROW5Left,>SsBassPHARAOH_WALKSTEPLeft,>SsBassPHARAOH_FLAP1Left,>SsBassPHARAOH_FLAP2Left,>SsBassPHARAOH_FLAPSHOT1Left,>SsBassPHARAOH_FLAPSHOT2Left,>SsBassPHARAOH_FLAPUP1Left,>SsBassPHARAOH_FLAPUP2Left,>SsBassARM_THROWLeft,>SsBassPHARAOH_ARM_THROWLeft,>SsBassARM_AIR_THROWLeft,>SsBassPHARAOH_ARM_AIR_THROWLeft,>SsBassARM_FISTLeft,>SsBassPHARAOH_ARM_FISTLeft,>SsBassARM_AIR_FISTLeft,>SsBassPHARAOH_ARM_AIR_FISTLeft,>SsBassARM_CARRYLeft,>SsBassPHARAOH_ARM_CARRYLeft,>SsBassARM_CARRY_STEPLeft,>SsBassPHARAOH_ARM_CARRY_STEPLeft,>SsBassARM_CARRY_WALK1Left,>SsBassPHARAOH_ARM_CARRY_WALK1Left,>SsBassARM_CARRY_WALK2Left,>SsBassPHARAOH_ARM_CARRY_WALK2Left,>SsBassARM_CARRY_WALK3Left,>SsBassPHARAOH_ARM_CARRY_WALK3Left,>SsBassARM_CARRY_JUMPLeft,>SsBassPHARAOH_ARM_CARRY_JUMPLeft
SsBassRightLo:
 .byte <SsBassPHARAOH_STANDRight,<SsBassPHARAOH_WALK1Right,<SsBassPHARAOH_WALK2Right,<SsBassPHARAOH_WALK3Right,<SsBassPHARAOH_JUMPRight,<SsBassPHARAOH_CROUCHRight,<SsBassPHARAOH_ATTACK1Right,<SsBassPHARAOH_ATTACK2Right,<SsBassPHARAOH_ATTACK3Right,<SsBassPHARAOH_CLIMB1Right,<SsBassPHARAOH_CLIMB2Right,<SsBassPHARAOH_HURTRight,<SsBassPHARAOH_DIERight,<SsBassPHARAOH_DASHRight,<SsBassPHARAOH_UPRight,<SsBassPHARAOH_DIAGUPRight,<SsBassPHARAOH_DIAGDOWNRight,<SsBassPHARAOH_THROWRight,<SsBassPHARAOH_WALLRight,<SsBassPHARAOH_CEILINGRight,<SsBassPHARAOH_HOVERRight,<SsBassPHARAOH_CROUCHSHOOTRight,<SsBassPHARAOH_JUMPSHOOTRight,<SsBassPHARAOH_JUMPUPRight,<SsBassPHARAOH_CROUCHATTACK1Right,<SsBassPHARAOH_CROUCHATTACK2Right,<SsBassPHARAOH_CROUCHATTACK3Right,<SsBassPHARAOH_JUMPATTACK1Right,<SsBassPHARAOH_JUMPATTACK2Right,<SsBassPHARAOH_JUMPATTACK3Right,<SsBassPHARAOH_JUMPDIAGUPRight,<SsBassPHARAOH_JUMPDIAGDOWNRight,<SsBassPHARAOH_HOVERSMALLRight,<SsBassPHARAOH_DEATH1Right,<SsBassPHARAOH_DEATH2Right,<SsBassPHARAOH_DEATH3Right,<SsBassPHARAOH_DEATH4Right,<SsBassPHARAOH_RYUSLASH1Right,<SsBassPHARAOH_RYUSLASH2Right,<SsBassPHARAOH_RYUSLASH3Right,<SsBassPHARAOH_RYUSLASH4Right,<SsBassPHARAOH_RYUSLASH5Right,<SsBassPHARAOH_DUCKSLASH1Right,<SsBassPHARAOH_DUCKSLASH2Right,<SsBassPHARAOH_DUCKSLASH3Right,<SsBassPHARAOH_DUCKSLASH4Right,<SsBassPHARAOH_DUCKSLASH5Right,<SsBassPHARAOH_AIRSLASH1Right,<SsBassPHARAOH_AIRSLASH2Right,<SsBassPHARAOH_AIRSLASH3Right,<SsBassPHARAOH_AIRSLASH4Right,<SsBassPHARAOH_AIRSLASH5Right,<SsBassPHARAOH_RYUTHROW1Right,<SsBassPHARAOH_RYUTHROW2Right,<SsBassPHARAOH_RYUTHROW3Right,<SsBassPHARAOH_RYUTHROW4Right,<SsBassPHARAOH_RYUTHROW5Right,<SsBassPHARAOH_DUCKTHROW1Right,<SsBassPHARAOH_DUCKTHROW2Right,<SsBassPHARAOH_DUCKTHROW3Right,<SsBassPHARAOH_DUCKTHROW4Right,<SsBassPHARAOH_DUCKTHROW5Right,<SsBassPHARAOH_AIRTHROW1Right,<SsBassPHARAOH_AIRTHROW2Right,<SsBassPHARAOH_AIRTHROW3Right,<SsBassPHARAOH_AIRTHROW4Right,<SsBassPHARAOH_AIRTHROW5Right,<SsBassPHARAOH_WALLTHROW1Right,<SsBassPHARAOH_WALLTHROW2Right,<SsBassPHARAOH_WALLTHROW3Right,<SsBassPHARAOH_WALLTHROW4Right,<SsBassPHARAOH_WALLTHROW5Right,<SsBassPHARAOH_BACKTHROW1Right,<SsBassPHARAOH_BACKTHROW2Right,<SsBassPHARAOH_BACKTHROW3Right,<SsBassPHARAOH_BACKTHROW4Right,<SsBassPHARAOH_BACKTHROW5Right,<SsBassPHARAOH_WALKSTEPRight,<SsBassPHARAOH_FLAP1Right,<SsBassPHARAOH_FLAP2Right,<SsBassPHARAOH_FLAPSHOT1Right,<SsBassPHARAOH_FLAPSHOT2Right,<SsBassPHARAOH_FLAPUP1Right,<SsBassPHARAOH_FLAPUP2Right,<SsBassARM_THROWRight,<SsBassPHARAOH_ARM_THROWRight,<SsBassARM_AIR_THROWRight,<SsBassPHARAOH_ARM_AIR_THROWRight,<SsBassARM_FISTRight,<SsBassPHARAOH_ARM_FISTRight,<SsBassARM_AIR_FISTRight,<SsBassPHARAOH_ARM_AIR_FISTRight,<SsBassARM_CARRYRight,<SsBassPHARAOH_ARM_CARRYRight,<SsBassARM_CARRY_STEPRight,<SsBassPHARAOH_ARM_CARRY_STEPRight,<SsBassARM_CARRY_WALK1Right,<SsBassPHARAOH_ARM_CARRY_WALK1Right,<SsBassARM_CARRY_WALK2Right,<SsBassPHARAOH_ARM_CARRY_WALK2Right,<SsBassARM_CARRY_WALK3Right,<SsBassPHARAOH_ARM_CARRY_WALK3Right,<SsBassARM_CARRY_JUMPRight,<SsBassPHARAOH_ARM_CARRY_JUMPRight
SsBassRightHi:
 .byte >SsBassPHARAOH_STANDRight,>SsBassPHARAOH_WALK1Right,>SsBassPHARAOH_WALK2Right,>SsBassPHARAOH_WALK3Right,>SsBassPHARAOH_JUMPRight,>SsBassPHARAOH_CROUCHRight,>SsBassPHARAOH_ATTACK1Right,>SsBassPHARAOH_ATTACK2Right,>SsBassPHARAOH_ATTACK3Right,>SsBassPHARAOH_CLIMB1Right,>SsBassPHARAOH_CLIMB2Right,>SsBassPHARAOH_HURTRight,>SsBassPHARAOH_DIERight,>SsBassPHARAOH_DASHRight,>SsBassPHARAOH_UPRight,>SsBassPHARAOH_DIAGUPRight,>SsBassPHARAOH_DIAGDOWNRight,>SsBassPHARAOH_THROWRight,>SsBassPHARAOH_WALLRight,>SsBassPHARAOH_CEILINGRight,>SsBassPHARAOH_HOVERRight,>SsBassPHARAOH_CROUCHSHOOTRight,>SsBassPHARAOH_JUMPSHOOTRight,>SsBassPHARAOH_JUMPUPRight,>SsBassPHARAOH_CROUCHATTACK1Right,>SsBassPHARAOH_CROUCHATTACK2Right,>SsBassPHARAOH_CROUCHATTACK3Right,>SsBassPHARAOH_JUMPATTACK1Right,>SsBassPHARAOH_JUMPATTACK2Right,>SsBassPHARAOH_JUMPATTACK3Right,>SsBassPHARAOH_JUMPDIAGUPRight,>SsBassPHARAOH_JUMPDIAGDOWNRight,>SsBassPHARAOH_HOVERSMALLRight,>SsBassPHARAOH_DEATH1Right,>SsBassPHARAOH_DEATH2Right,>SsBassPHARAOH_DEATH3Right,>SsBassPHARAOH_DEATH4Right,>SsBassPHARAOH_RYUSLASH1Right,>SsBassPHARAOH_RYUSLASH2Right,>SsBassPHARAOH_RYUSLASH3Right,>SsBassPHARAOH_RYUSLASH4Right,>SsBassPHARAOH_RYUSLASH5Right,>SsBassPHARAOH_DUCKSLASH1Right,>SsBassPHARAOH_DUCKSLASH2Right,>SsBassPHARAOH_DUCKSLASH3Right,>SsBassPHARAOH_DUCKSLASH4Right,>SsBassPHARAOH_DUCKSLASH5Right,>SsBassPHARAOH_AIRSLASH1Right,>SsBassPHARAOH_AIRSLASH2Right,>SsBassPHARAOH_AIRSLASH3Right,>SsBassPHARAOH_AIRSLASH4Right,>SsBassPHARAOH_AIRSLASH5Right,>SsBassPHARAOH_RYUTHROW1Right,>SsBassPHARAOH_RYUTHROW2Right,>SsBassPHARAOH_RYUTHROW3Right,>SsBassPHARAOH_RYUTHROW4Right,>SsBassPHARAOH_RYUTHROW5Right,>SsBassPHARAOH_DUCKTHROW1Right,>SsBassPHARAOH_DUCKTHROW2Right,>SsBassPHARAOH_DUCKTHROW3Right,>SsBassPHARAOH_DUCKTHROW4Right,>SsBassPHARAOH_DUCKTHROW5Right,>SsBassPHARAOH_AIRTHROW1Right,>SsBassPHARAOH_AIRTHROW2Right,>SsBassPHARAOH_AIRTHROW3Right,>SsBassPHARAOH_AIRTHROW4Right,>SsBassPHARAOH_AIRTHROW5Right,>SsBassPHARAOH_WALLTHROW1Right,>SsBassPHARAOH_WALLTHROW2Right,>SsBassPHARAOH_WALLTHROW3Right,>SsBassPHARAOH_WALLTHROW4Right,>SsBassPHARAOH_WALLTHROW5Right,>SsBassPHARAOH_BACKTHROW1Right,>SsBassPHARAOH_BACKTHROW2Right,>SsBassPHARAOH_BACKTHROW3Right,>SsBassPHARAOH_BACKTHROW4Right,>SsBassPHARAOH_BACKTHROW5Right,>SsBassPHARAOH_WALKSTEPRight,>SsBassPHARAOH_FLAP1Right,>SsBassPHARAOH_FLAP2Right,>SsBassPHARAOH_FLAPSHOT1Right,>SsBassPHARAOH_FLAPSHOT2Right,>SsBassPHARAOH_FLAPUP1Right,>SsBassPHARAOH_FLAPUP2Right,>SsBassARM_THROWRight,>SsBassPHARAOH_ARM_THROWRight,>SsBassARM_AIR_THROWRight,>SsBassPHARAOH_ARM_AIR_THROWRight,>SsBassARM_FISTRight,>SsBassPHARAOH_ARM_FISTRight,>SsBassARM_AIR_FISTRight,>SsBassPHARAOH_ARM_AIR_FISTRight,>SsBassARM_CARRYRight,>SsBassPHARAOH_ARM_CARRYRight,>SsBassARM_CARRY_STEPRight,>SsBassPHARAOH_ARM_CARRY_STEPRight,>SsBassARM_CARRY_WALK1Right,>SsBassPHARAOH_ARM_CARRY_WALK1Right,>SsBassARM_CARRY_WALK2Right,>SsBassPHARAOH_ARM_CARRY_WALK2Right,>SsBassARM_CARRY_WALK3Right,>SsBassPHARAOH_ARM_CARRY_WALK3Right,>SsBassARM_CARRY_JUMPRight,>SsBassPHARAOH_ARM_CARRY_JUMPRight
SsBassBanks:
 .byte 244,244,244,245,245,244,245,245,245,246,246,246,246,244,247,247,248,244,244,244,244,244,246,248,244,244,244,244,244,244,249,249,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,244,250,244,244,244,244,244,244,250,251,249,251,252,252,253,253,254,254,254,254,255,255,255,114,114,114,115,115
.popseg
