; Lance Bean: Crossover 2.02 Bill003 source skin.
.pushseg
.segment "BILL_GFX"
RgLANCE_STANDLeft:
  .byte 48
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $40, -2, 7
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, -2, -1
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $40, -2, -9
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c0, 14, 7
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 14, -1
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c0, 30, 7
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $80, 30, -1
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $42, -1, 6
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $02, -1, -2
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $42, -1, -10
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $42, 15, 6
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $02, 15, -2
RgLANCE_STANDRight:
  .byte 48
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, -2, 1
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $40, -2, 9
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, -2, 17
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $80, 14, 1
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $40, 14, 9
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $80, 30, 1
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c0, 30, 9
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $02, -1, 2
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $42, -1, 10
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $02, -1, 18
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $02, 15, 2
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $42, 15, 10
RgLANCE_WALK1Left:
  .byte 48
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $40, -2, 10
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c0, -2, 2
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, -2, -6
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $40, 14, 10
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $40, 14, 2
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $80, 14, -6
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c0, 30, 10
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $42, -1, 9
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $02, -1, 1
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $82, -1, -7
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $42, 15, 9
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $82, 15, 1
RgLANCE_WALK1Right:
  .byte 48
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, -2, -2
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $80, -2, 6
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $40, -2, 14
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 14, -2
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 14, 6
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c0, 14, 14
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $80, 30, -2
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $02, -1, -1
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $42, -1, 7
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c2, -1, 15
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $02, 15, -1
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c2, 15, 7
RgLANCE_WALK2Left:
  .byte 44
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, 0, 10
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 0, 2
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 0, -6
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $80, 16, 10
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c0, 16, 2
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 16, -6
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $42, 0, 5
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $42, 0, -3
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c2, 16, 13
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c2, 16, 5
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $02, 16, -3
RgLANCE_WALK2Right:
  .byte 44
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 0, -2
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 0, 6
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 0, 14
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c0, 16, -2
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $80, 16, 6
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $40, 16, 14
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $02, 0, 3
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $02, 0, 11
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $82, 16, -5
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $82, 16, 3
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $42, 16, 11
RgLANCE_WALK3Left:
  .byte 44
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $40, -3, 6
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $40, -3, -2
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 13, 6
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $80, 13, -2
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c0, 29, 6
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $80, 29, -2
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $42, -17, -2
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $42, -1, 6
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $82, -1, -2
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $42, 15, 6
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $02, 15, -2
RgLANCE_WALK3Right:
  .byte 44
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, -3, 2
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, -3, 10
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $40, 13, 2
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c0, 13, 10
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $80, 29, 2
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c0, 29, 10
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $02, -17, 10
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $02, -1, 2
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c2, -1, 10
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $02, 15, 2
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $42, 15, 10
RgLANCE_JUMP1Left:
  .byte 24
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $80, 16, 10
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $80, 16, 2
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 16, -6
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c2, 17, 9
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c2, 17, 1
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $02, 17, -7
RgLANCE_JUMP1Right:
  .byte 24
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c0, 16, -2
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c0, 16, 6
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $40, 16, 14
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $82, 17, -1
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $82, 17, 7
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $42, 17, 15
RgLANCE_JUMP2Left:
  .byte 28
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c0, 14, 8
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 14, 0
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c0, 30, 8
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $80, 30, 0
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $02, 2, 6
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $82, 18, 6
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $82, 18, -2
RgLANCE_JUMP2Right:
  .byte 28
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $80, 14, 0
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 14, 8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $80, 30, 0
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c0, 30, 8
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $42, 2, 2
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c2, 18, 2
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c2, 18, 10
RgLANCE_JUMP3Left:
  .byte 24
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c0, 16, 10
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $00, 16, 2
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $80, 16, -6
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c2, 18, 9
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $82, 18, 1
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $82, 18, -7
RgLANCE_JUMP3Right:
  .byte 24
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $80, 16, -2
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $40, 16, 6
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c0, 16, 14
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $82, 18, -1
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c2, 18, 7
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c2, 18, 15
RgLANCE_JUMP4Left:
  .byte 28
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $40, 14, 8
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 14, 0
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 30, 8
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $80, 30, 0
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $42, 15, 8
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $82, 15, 0
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $82, 31, 0
RgLANCE_JUMP4Right:
  .byte 28
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 14, 0
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 14, 8
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 30, 0
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c0, 30, 8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $02, 15, 0
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c2, 15, 8
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c2, 31, 8
RgLANCE_CROUCHLeft:
  .byte 40
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $40, 16, 17
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 16, 9
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $40, 16, 1
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $40, 16, -7
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $80, 16, -15
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $80, 32, 1
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $82, 17, 16
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $42, 17, 8
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $02, 17, 0
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $42, 17, -8
RgLANCE_CROUCHRight:
  .byte 40
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, 16, -9
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $40, 16, -1
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 16, 7
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 16, 15
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c0, 16, 23
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c0, 32, 7
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c2, 17, -8
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $02, 17, 0
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $42, 17, 8
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $02, 17, 16
RgLANCE_ATTACK1Left:
  .byte 48
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $40, -1, 7
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $80, -1, -1
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, -1, -9
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c0, 15, 7
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 15, -1
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 31, 7
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 31, -1
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $42, 0, 6
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $02, 0, -2
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $42, 0, -10
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c2, 16, 6
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $82, 16, -2
RgLANCE_ATTACK1Right:
  .byte 48
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, -1, 1
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c0, -1, 9
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, -1, 17
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $80, 15, 1
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $40, 15, 9
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 31, 1
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 31, 9
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $02, 0, 2
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $42, 0, 10
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $02, 0, 18
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $82, 16, 2
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c2, 16, 10
RgLANCE_CLIMB1Left:
  .byte 48
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $40, -4, 14
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $40, -4, 6
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, -4, -2
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 12, 6
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $80, 12, -2
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $80, 28, 6
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $42, -3, 9
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $02, -3, 1
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $02, -3, -7
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c2, 13, 9
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $c2, 13, 1
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c2, 29, 9
RgLANCE_CLIMB1Right:
  .byte 48
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, -4, -6
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, -4, 2
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $40, -4, 10
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $40, 12, 2
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c0, 12, 10
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c0, 28, 2
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $02, -3, -1
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $42, -3, 7
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $42, -3, 15
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $82, 13, -1
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $82, 13, 7
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $82, 29, -1
RgLANCE_CLIMB2Left:
  .byte 48
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, -6, 12
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $40, -6, 4
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, -6, -4
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c0, 10, 12
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 10, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c0, 26, 4
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $42, -4, 11
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $82, -4, 3
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $02, -4, -5
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c2, 12, 11
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $82, 12, 3
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c2, 28, 3
RgLANCE_CLIMB2Right:
  .byte 48
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, -6, -4
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, -6, 4
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $40, -6, 12
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $80, 10, -4
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, 10, 4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $80, 26, 4
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $02, -4, -3
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c2, -4, 5
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $42, -4, 13
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $82, 12, -3
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c2, 12, 5
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $82, 28, 5
RgLANCE_UPSTANDLeft:
  .byte 40
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, -16, -1
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $40, 0, 7
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $80, 0, -1
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c0, 16, 7
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 16, -1
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $02, -16, -2
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $42, 0, 6
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $82, 0, -2
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c2, 16, 6
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $82, 16, -2
RgLANCE_UPSTANDRight:
  .byte 40
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $40, -16, 9
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 0, 1
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c0, 0, 9
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $80, 16, 1
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $40, 16, 9
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $42, -16, 10
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $02, 0, 2
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $c2, 0, 10
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $82, 16, 2
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c2, 16, 10
RgLANCE_DIAGUPLeft:
  .byte 48
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $40, -3, 6
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $80, -3, -2
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $80, -3, -10
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 13, 6
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $80, 13, -2
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c0, 29, 6
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $80, 29, -2
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $42, -17, -3
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $42, -1, 5
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $82, -1, -3
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $42, 15, 5
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $02, 15, -3
RgLANCE_DIAGUPRight:
  .byte 48
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, -3, 2
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c0, -3, 10
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c0, -3, 18
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $40, 13, 2
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c0, 13, 10
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $80, 29, 2
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c0, 29, 10
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $02, -17, 11
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $02, -1, 3
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c2, -1, 11
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $02, 15, 3
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $42, 15, 11
RgLANCE_DIAGDOWNLeft:
  .byte 52
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $40, -4, 7
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, -4, -1
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, 12, 7
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $80, 12, -1
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 12, -9
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 28, 7
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 28, -1
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $42, -7, 11
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $42, -7, 3
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $42, 9, 3
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c2, 9, -5
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c2, 25, 11
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $82, 25, 3
RgLANCE_DIAGDOWNRight:
  .byte 52
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, -4, 1
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, -4, 9
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 12, 1
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c0, 12, 9
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 12, 17
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 28, 1
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 28, 9
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $02, -7, -3
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $02, -7, 5
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $02, 9, 5
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $82, 9, 13
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $82, 25, -3
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c2, 25, 5
RgLANCE_UPWALK1Left:
  .byte 44
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, -16, -1
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 0, 7
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $80, 0, -1
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $40, 16, 15
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 16, 7
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $80, 16, -1
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $42, -15, 1
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c2, 1, 9
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $42, 1, 1
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $82, 17, 9
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $82, 17, 1
RgLANCE_UPWALK1Right:
  .byte 44
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $40, -16, 9
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 0, 1
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c0, 0, 9
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 16, -7
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 16, 1
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c0, 16, 9
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $02, -15, 7
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $82, 1, -1
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $02, 1, 7
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c2, 17, -1
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c2, 17, 7
RgLANCE_UPWALK2Left:
  .byte 60
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $40, -16, 2
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, -16, -6
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $40, 0, 10
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $80, 0, 2
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $80, 0, -6
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $80, 16, 10
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c0, 16, 2
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $00, 16, -6
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $42, -19, 1
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $42, -3, 9
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $82, -3, 1
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $82, 13, 9
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $02, 13, 1
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c2, 29, 1
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $82, 29, -7
RgLANCE_UPWALK2Right:
  .byte 60
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, -16, 6
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $40, -16, 14
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 0, -2
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c0, 0, 6
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c0, 0, 14
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c0, 16, -2
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $80, 16, 6
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $40, 16, 14
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $02, -19, 7
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $02, -3, -1
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $c2, -3, 7
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c2, 13, -1
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $42, 13, 7
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $82, 29, 7
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c2, 29, 15
RgLANCE_DIAGUPWALK1Left:
  .byte 52
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, -11, 5
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, -11, -3
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $00, 5, 5
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 5, -3
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 21, 13
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $80, 21, 5
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $80, 21, -3
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $42, -2, 9
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $02, -2, 1
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $82, -2, -7
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $42, 14, 9
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $82, 14, 1
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $82, 30, 9
RgLANCE_DIAGUPWALK1Right:
  .byte 52
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, -11, 3
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, -11, 11
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $40, 5, 3
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 5, 11
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 21, -5
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c0, 21, 3
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c0, 21, 11
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $02, -2, -1
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $42, -2, 7
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c2, -2, 15
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $02, 14, -1
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c2, 14, 7
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c2, 30, -1
RgLANCE_DIAGUPWALK2Left:
  .byte 48
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $40, -3, 5
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $80, -3, -3
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c0, 13, 13
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c0, 13, 5
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 13, -3
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $80, 29, -3
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $02, -7, 3
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $42, -7, -5
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $82, 9, 11
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c2, 9, 3
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $c2, 25, 3
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $82, 25, -5
RgLANCE_DIAGUPWALK2Right:
  .byte 48
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, -3, 3
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c0, -3, 11
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $80, 13, -5
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $80, 13, 3
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $40, 13, 11
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c0, 29, 11
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $42, -7, 5
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $02, -7, 13
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c2, 9, -3
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $82, 9, 5
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $82, 25, 5
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c2, 25, 13
RgLANCE_DIAGDOWNWALK1Left:
  .byte 56
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $40, -10, 10
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, -10, 2
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c0, 6, 10
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $40, 6, 2
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $80, 6, -6
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c0, 22, 10
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c0, 22, 2
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $42, -2, 9
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $02, -2, 1
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $02, -2, -7
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $42, 14, 9
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $82, 14, 1
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c2, 14, -7
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $82, 30, 9
RgLANCE_DIAGDOWNWALK1Right:
  .byte 56
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, -10, -2
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $40, -10, 6
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $80, 6, -2
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 6, 6
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c0, 6, 14
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $80, 22, -2
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $80, 22, 6
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $02, -2, -1
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $42, -2, 7
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $42, -2, 15
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $02, 14, -1
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c2, 14, 7
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $82, 14, 15
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c2, 30, -1
RgLANCE_DIAGDOWNWALK2Left:
  .byte 60
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $40, -3, 10
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, -3, 2
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, -3, -6
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $80, 13, 10
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c0, 13, 2
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 13, -6
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 29, 2
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 29, -6
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $42, -4, 9
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $02, -4, 1
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $82, 12, 9
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c2, 12, 1
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c2, 12, -7
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c2, 28, 1
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $82, 28, -7
RgLANCE_DIAGDOWNWALK2Right:
  .byte 60
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, -3, -2
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $40, -3, 6
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, -3, 14
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c0, 13, -2
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $80, 13, 6
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 13, 14
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 29, 6
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 29, 14
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $02, -4, -1
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $42, -4, 7
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c2, 12, -1
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $82, 12, 7
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $82, 12, 15
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $82, 28, 7
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $c2, 28, 15
RgLANCE_HURTLeft:
  .byte 28
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $80, 14, 12
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 14, 4
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $80, 14, -4
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c0, 30, 12
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $42, 15, 11
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $82, 15, 3
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $82, 15, -5
RgLANCE_HURTRight:
  .byte 28
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c0, 14, -4
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 14, 4
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c0, 14, 12
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $80, 30, -4
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $02, 15, -3
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c2, 15, 5
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c2, 15, 13
RgLANCE_DIE3Left:
  .byte 36
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $c0, 22, 17
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c0, 22, 9
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $80, 22, 1
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $c0, 22, -7
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $80, 22, -15
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c2, 23, 16
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $82, 23, 8
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $c2, 23, 0
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $82, 23, -8
RgLANCE_DIE3Right:
  .byte 36
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $80, 22, -9
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $80, 22, -1
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c0, 22, 7
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $80, 22, 15
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c0, 22, 23
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $82, 23, -8
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c2, 23, 0
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $82, 23, 8
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c2, 23, 16
RgLANCE_CROUCHATTACK1Left:
  .byte 40
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $40, 17, 17
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 17, 9
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $40, 17, 1
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $40, 17, -7
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $80, 17, -15
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $80, 33, 1
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $82, 18, 16
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $42, 18, 8
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $02, 18, 0
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $42, 18, -8
RgLANCE_CROUCHATTACK1Right:
  .byte 40
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $00, 17, -9
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $40, 17, -1
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 17, 7
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 17, 15
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c0, 17, 23
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c0, 33, 7
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c2, 18, -8
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $02, 18, 0
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $42, 18, 8
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $02, 18, 16
RgLANCELeftLo:
 .byte <RgLANCE_STANDLeft,<RgLANCE_WALK1Left,<RgLANCE_WALK2Left,<RgLANCE_WALK3Left,<RgLANCE_JUMP1Left,<RgLANCE_JUMP2Left,<RgLANCE_JUMP3Left,<RgLANCE_JUMP4Left,<RgLANCE_CROUCHLeft,<RgLANCE_ATTACK1Left,<RgLANCE_ATTACK1Left,<RgLANCE_ATTACK1Left,<RgLANCE_STANDLeft,<RgLANCE_STANDLeft,<RgLANCE_STANDLeft,<RgLANCE_CLIMB1Left,<RgLANCE_CLIMB2Left,<RgLANCE_UPSTANDLeft,<RgLANCE_DIAGUPLeft,<RgLANCE_DIAGDOWNLeft,<RgLANCE_UPWALK1Left,<RgLANCE_UPWALK2Left,<RgLANCE_UPSTANDLeft,<RgLANCE_DIAGUPWALK1Left,<RgLANCE_DIAGUPWALK2Left,<RgLANCE_DIAGUPLeft,<RgLANCE_DIAGDOWNWALK1Left,<RgLANCE_DIAGDOWNWALK2Left,<RgLANCE_DIAGDOWNLeft,<RgLANCE_STANDLeft,<RgLANCE_UPSTANDLeft,<RgLANCE_HURTLeft,<RgLANCE_HURTLeft,<RgLANCE_HURTLeft,<RgLANCE_DIE3Left,<RgLANCE_DIE3Left,<RgLANCE_STANDLeft,<RgLANCE_CROUCHATTACK1Left,<RgLANCE_CROUCHATTACK1Left,<RgLANCE_CROUCHATTACK1Left,<RgLANCE_CROUCHATTACK1Left,<RgLANCE_CROUCHATTACK1Left,<RgLANCE_CROUCHATTACK1Left,<RgLANCE_HURTLeft,<RgLANCE_HURTLeft,<RgLANCE_HURTLeft,<RgLANCE_HURTLeft,<RgLANCE_HURTLeft,<RgLANCE_STANDLeft,<RgLANCE_WALK1Left,<RgLANCE_WALK2Left,<RgLANCE_WALK3Left,<RgLANCE_JUMP1Left,<RgLANCE_JUMP2Left,<RgLANCE_JUMP3Left,<RgLANCE_JUMP4Left,<RgLANCE_CROUCHLeft,<RgLANCE_ATTACK1Left,<RgLANCE_ATTACK1Left,<RgLANCE_ATTACK1Left,<RgLANCE_STANDLeft,<RgLANCE_STANDLeft,<RgLANCE_STANDLeft,<RgLANCE_CLIMB1Left,<RgLANCE_CLIMB2Left,<RgLANCE_UPSTANDLeft,<RgLANCE_DIAGUPLeft,<RgLANCE_DIAGDOWNLeft,<RgLANCE_UPWALK1Left,<RgLANCE_UPWALK2Left,<RgLANCE_UPSTANDLeft,<RgLANCE_DIAGUPWALK1Left,<RgLANCE_DIAGUPWALK2Left,<RgLANCE_DIAGUPLeft,<RgLANCE_DIAGDOWNWALK1Left,<RgLANCE_DIAGDOWNWALK2Left,<RgLANCE_DIAGDOWNLeft,<RgLANCE_STANDLeft,<RgLANCE_UPSTANDLeft,<RgLANCE_HURTLeft,<RgLANCE_HURTLeft,<RgLANCE_HURTLeft,<RgLANCE_DIE3Left,<RgLANCE_DIE3Left,<RgLANCE_STANDLeft,<RgLANCE_CROUCHATTACK1Left,<RgLANCE_CROUCHATTACK1Left,<RgLANCE_CROUCHATTACK1Left,<RgLANCE_CROUCHATTACK1Left,<RgLANCE_CROUCHATTACK1Left,<RgLANCE_CROUCHATTACK1Left,<RgLANCE_HURTLeft,<RgLANCE_HURTLeft,<RgLANCE_HURTLeft,<RgLANCE_HURTLeft,<RgLANCE_HURTLeft,<RgLANCE_STANDLeft,<RgLANCE_WALK1Left,<RgLANCE_WALK2Left,<RgLANCE_WALK3Left,<RgLANCE_JUMP1Left,<RgLANCE_JUMP2Left,<RgLANCE_JUMP3Left,<RgLANCE_JUMP4Left,<RgLANCE_CROUCHLeft,<RgLANCE_ATTACK1Left,<RgLANCE_ATTACK1Left,<RgLANCE_ATTACK1Left,<RgLANCE_STANDLeft,<RgLANCE_STANDLeft,<RgLANCE_STANDLeft,<RgLANCE_CLIMB1Left,<RgLANCE_CLIMB2Left,<RgLANCE_UPSTANDLeft,<RgLANCE_DIAGUPLeft,<RgLANCE_DIAGDOWNLeft,<RgLANCE_UPWALK1Left,<RgLANCE_UPWALK2Left,<RgLANCE_UPSTANDLeft,<RgLANCE_DIAGUPWALK1Left,<RgLANCE_DIAGUPWALK2Left,<RgLANCE_DIAGUPLeft,<RgLANCE_DIAGDOWNWALK1Left,<RgLANCE_DIAGDOWNWALK2Left,<RgLANCE_DIAGDOWNLeft,<RgLANCE_STANDLeft,<RgLANCE_UPSTANDLeft,<RgLANCE_HURTLeft,<RgLANCE_HURTLeft,<RgLANCE_HURTLeft,<RgLANCE_DIE3Left,<RgLANCE_DIE3Left,<RgLANCE_STANDLeft,<RgLANCE_CROUCHATTACK1Left,<RgLANCE_CROUCHATTACK1Left,<RgLANCE_CROUCHATTACK1Left,<RgLANCE_CROUCHATTACK1Left,<RgLANCE_CROUCHATTACK1Left,<RgLANCE_CROUCHATTACK1Left,<RgLANCE_HURTLeft,<RgLANCE_HURTLeft,<RgLANCE_HURTLeft,<RgLANCE_HURTLeft,<RgLANCE_HURTLeft
RgLANCELeftHi:
 .byte >RgLANCE_STANDLeft,>RgLANCE_WALK1Left,>RgLANCE_WALK2Left,>RgLANCE_WALK3Left,>RgLANCE_JUMP1Left,>RgLANCE_JUMP2Left,>RgLANCE_JUMP3Left,>RgLANCE_JUMP4Left,>RgLANCE_CROUCHLeft,>RgLANCE_ATTACK1Left,>RgLANCE_ATTACK1Left,>RgLANCE_ATTACK1Left,>RgLANCE_STANDLeft,>RgLANCE_STANDLeft,>RgLANCE_STANDLeft,>RgLANCE_CLIMB1Left,>RgLANCE_CLIMB2Left,>RgLANCE_UPSTANDLeft,>RgLANCE_DIAGUPLeft,>RgLANCE_DIAGDOWNLeft,>RgLANCE_UPWALK1Left,>RgLANCE_UPWALK2Left,>RgLANCE_UPSTANDLeft,>RgLANCE_DIAGUPWALK1Left,>RgLANCE_DIAGUPWALK2Left,>RgLANCE_DIAGUPLeft,>RgLANCE_DIAGDOWNWALK1Left,>RgLANCE_DIAGDOWNWALK2Left,>RgLANCE_DIAGDOWNLeft,>RgLANCE_STANDLeft,>RgLANCE_UPSTANDLeft,>RgLANCE_HURTLeft,>RgLANCE_HURTLeft,>RgLANCE_HURTLeft,>RgLANCE_DIE3Left,>RgLANCE_DIE3Left,>RgLANCE_STANDLeft,>RgLANCE_CROUCHATTACK1Left,>RgLANCE_CROUCHATTACK1Left,>RgLANCE_CROUCHATTACK1Left,>RgLANCE_CROUCHATTACK1Left,>RgLANCE_CROUCHATTACK1Left,>RgLANCE_CROUCHATTACK1Left,>RgLANCE_HURTLeft,>RgLANCE_HURTLeft,>RgLANCE_HURTLeft,>RgLANCE_HURTLeft,>RgLANCE_HURTLeft,>RgLANCE_STANDLeft,>RgLANCE_WALK1Left,>RgLANCE_WALK2Left,>RgLANCE_WALK3Left,>RgLANCE_JUMP1Left,>RgLANCE_JUMP2Left,>RgLANCE_JUMP3Left,>RgLANCE_JUMP4Left,>RgLANCE_CROUCHLeft,>RgLANCE_ATTACK1Left,>RgLANCE_ATTACK1Left,>RgLANCE_ATTACK1Left,>RgLANCE_STANDLeft,>RgLANCE_STANDLeft,>RgLANCE_STANDLeft,>RgLANCE_CLIMB1Left,>RgLANCE_CLIMB2Left,>RgLANCE_UPSTANDLeft,>RgLANCE_DIAGUPLeft,>RgLANCE_DIAGDOWNLeft,>RgLANCE_UPWALK1Left,>RgLANCE_UPWALK2Left,>RgLANCE_UPSTANDLeft,>RgLANCE_DIAGUPWALK1Left,>RgLANCE_DIAGUPWALK2Left,>RgLANCE_DIAGUPLeft,>RgLANCE_DIAGDOWNWALK1Left,>RgLANCE_DIAGDOWNWALK2Left,>RgLANCE_DIAGDOWNLeft,>RgLANCE_STANDLeft,>RgLANCE_UPSTANDLeft,>RgLANCE_HURTLeft,>RgLANCE_HURTLeft,>RgLANCE_HURTLeft,>RgLANCE_DIE3Left,>RgLANCE_DIE3Left,>RgLANCE_STANDLeft,>RgLANCE_CROUCHATTACK1Left,>RgLANCE_CROUCHATTACK1Left,>RgLANCE_CROUCHATTACK1Left,>RgLANCE_CROUCHATTACK1Left,>RgLANCE_CROUCHATTACK1Left,>RgLANCE_CROUCHATTACK1Left,>RgLANCE_HURTLeft,>RgLANCE_HURTLeft,>RgLANCE_HURTLeft,>RgLANCE_HURTLeft,>RgLANCE_HURTLeft,>RgLANCE_STANDLeft,>RgLANCE_WALK1Left,>RgLANCE_WALK2Left,>RgLANCE_WALK3Left,>RgLANCE_JUMP1Left,>RgLANCE_JUMP2Left,>RgLANCE_JUMP3Left,>RgLANCE_JUMP4Left,>RgLANCE_CROUCHLeft,>RgLANCE_ATTACK1Left,>RgLANCE_ATTACK1Left,>RgLANCE_ATTACK1Left,>RgLANCE_STANDLeft,>RgLANCE_STANDLeft,>RgLANCE_STANDLeft,>RgLANCE_CLIMB1Left,>RgLANCE_CLIMB2Left,>RgLANCE_UPSTANDLeft,>RgLANCE_DIAGUPLeft,>RgLANCE_DIAGDOWNLeft,>RgLANCE_UPWALK1Left,>RgLANCE_UPWALK2Left,>RgLANCE_UPSTANDLeft,>RgLANCE_DIAGUPWALK1Left,>RgLANCE_DIAGUPWALK2Left,>RgLANCE_DIAGUPLeft,>RgLANCE_DIAGDOWNWALK1Left,>RgLANCE_DIAGDOWNWALK2Left,>RgLANCE_DIAGDOWNLeft,>RgLANCE_STANDLeft,>RgLANCE_UPSTANDLeft,>RgLANCE_HURTLeft,>RgLANCE_HURTLeft,>RgLANCE_HURTLeft,>RgLANCE_DIE3Left,>RgLANCE_DIE3Left,>RgLANCE_STANDLeft,>RgLANCE_CROUCHATTACK1Left,>RgLANCE_CROUCHATTACK1Left,>RgLANCE_CROUCHATTACK1Left,>RgLANCE_CROUCHATTACK1Left,>RgLANCE_CROUCHATTACK1Left,>RgLANCE_CROUCHATTACK1Left,>RgLANCE_HURTLeft,>RgLANCE_HURTLeft,>RgLANCE_HURTLeft,>RgLANCE_HURTLeft,>RgLANCE_HURTLeft
RgLANCERightLo:
 .byte <RgLANCE_STANDRight,<RgLANCE_WALK1Right,<RgLANCE_WALK2Right,<RgLANCE_WALK3Right,<RgLANCE_JUMP1Right,<RgLANCE_JUMP2Right,<RgLANCE_JUMP3Right,<RgLANCE_JUMP4Right,<RgLANCE_CROUCHRight,<RgLANCE_ATTACK1Right,<RgLANCE_ATTACK1Right,<RgLANCE_ATTACK1Right,<RgLANCE_STANDRight,<RgLANCE_STANDRight,<RgLANCE_STANDRight,<RgLANCE_CLIMB1Right,<RgLANCE_CLIMB2Right,<RgLANCE_UPSTANDRight,<RgLANCE_DIAGUPRight,<RgLANCE_DIAGDOWNRight,<RgLANCE_UPWALK1Right,<RgLANCE_UPWALK2Right,<RgLANCE_UPSTANDRight,<RgLANCE_DIAGUPWALK1Right,<RgLANCE_DIAGUPWALK2Right,<RgLANCE_DIAGUPRight,<RgLANCE_DIAGDOWNWALK1Right,<RgLANCE_DIAGDOWNWALK2Right,<RgLANCE_DIAGDOWNRight,<RgLANCE_STANDRight,<RgLANCE_UPSTANDRight,<RgLANCE_HURTRight,<RgLANCE_HURTRight,<RgLANCE_HURTRight,<RgLANCE_DIE3Right,<RgLANCE_DIE3Right,<RgLANCE_STANDRight,<RgLANCE_CROUCHATTACK1Right,<RgLANCE_CROUCHATTACK1Right,<RgLANCE_CROUCHATTACK1Right,<RgLANCE_CROUCHATTACK1Right,<RgLANCE_CROUCHATTACK1Right,<RgLANCE_CROUCHATTACK1Right,<RgLANCE_HURTRight,<RgLANCE_HURTRight,<RgLANCE_HURTRight,<RgLANCE_HURTRight,<RgLANCE_HURTRight,<RgLANCE_STANDRight,<RgLANCE_WALK1Right,<RgLANCE_WALK2Right,<RgLANCE_WALK3Right,<RgLANCE_JUMP1Right,<RgLANCE_JUMP2Right,<RgLANCE_JUMP3Right,<RgLANCE_JUMP4Right,<RgLANCE_CROUCHRight,<RgLANCE_ATTACK1Right,<RgLANCE_ATTACK1Right,<RgLANCE_ATTACK1Right,<RgLANCE_STANDRight,<RgLANCE_STANDRight,<RgLANCE_STANDRight,<RgLANCE_CLIMB1Right,<RgLANCE_CLIMB2Right,<RgLANCE_UPSTANDRight,<RgLANCE_DIAGUPRight,<RgLANCE_DIAGDOWNRight,<RgLANCE_UPWALK1Right,<RgLANCE_UPWALK2Right,<RgLANCE_UPSTANDRight,<RgLANCE_DIAGUPWALK1Right,<RgLANCE_DIAGUPWALK2Right,<RgLANCE_DIAGUPRight,<RgLANCE_DIAGDOWNWALK1Right,<RgLANCE_DIAGDOWNWALK2Right,<RgLANCE_DIAGDOWNRight,<RgLANCE_STANDRight,<RgLANCE_UPSTANDRight,<RgLANCE_HURTRight,<RgLANCE_HURTRight,<RgLANCE_HURTRight,<RgLANCE_DIE3Right,<RgLANCE_DIE3Right,<RgLANCE_STANDRight,<RgLANCE_CROUCHATTACK1Right,<RgLANCE_CROUCHATTACK1Right,<RgLANCE_CROUCHATTACK1Right,<RgLANCE_CROUCHATTACK1Right,<RgLANCE_CROUCHATTACK1Right,<RgLANCE_CROUCHATTACK1Right,<RgLANCE_HURTRight,<RgLANCE_HURTRight,<RgLANCE_HURTRight,<RgLANCE_HURTRight,<RgLANCE_HURTRight,<RgLANCE_STANDRight,<RgLANCE_WALK1Right,<RgLANCE_WALK2Right,<RgLANCE_WALK3Right,<RgLANCE_JUMP1Right,<RgLANCE_JUMP2Right,<RgLANCE_JUMP3Right,<RgLANCE_JUMP4Right,<RgLANCE_CROUCHRight,<RgLANCE_ATTACK1Right,<RgLANCE_ATTACK1Right,<RgLANCE_ATTACK1Right,<RgLANCE_STANDRight,<RgLANCE_STANDRight,<RgLANCE_STANDRight,<RgLANCE_CLIMB1Right,<RgLANCE_CLIMB2Right,<RgLANCE_UPSTANDRight,<RgLANCE_DIAGUPRight,<RgLANCE_DIAGDOWNRight,<RgLANCE_UPWALK1Right,<RgLANCE_UPWALK2Right,<RgLANCE_UPSTANDRight,<RgLANCE_DIAGUPWALK1Right,<RgLANCE_DIAGUPWALK2Right,<RgLANCE_DIAGUPRight,<RgLANCE_DIAGDOWNWALK1Right,<RgLANCE_DIAGDOWNWALK2Right,<RgLANCE_DIAGDOWNRight,<RgLANCE_STANDRight,<RgLANCE_UPSTANDRight,<RgLANCE_HURTRight,<RgLANCE_HURTRight,<RgLANCE_HURTRight,<RgLANCE_DIE3Right,<RgLANCE_DIE3Right,<RgLANCE_STANDRight,<RgLANCE_CROUCHATTACK1Right,<RgLANCE_CROUCHATTACK1Right,<RgLANCE_CROUCHATTACK1Right,<RgLANCE_CROUCHATTACK1Right,<RgLANCE_CROUCHATTACK1Right,<RgLANCE_CROUCHATTACK1Right,<RgLANCE_HURTRight,<RgLANCE_HURTRight,<RgLANCE_HURTRight,<RgLANCE_HURTRight,<RgLANCE_HURTRight
RgLANCERightHi:
 .byte >RgLANCE_STANDRight,>RgLANCE_WALK1Right,>RgLANCE_WALK2Right,>RgLANCE_WALK3Right,>RgLANCE_JUMP1Right,>RgLANCE_JUMP2Right,>RgLANCE_JUMP3Right,>RgLANCE_JUMP4Right,>RgLANCE_CROUCHRight,>RgLANCE_ATTACK1Right,>RgLANCE_ATTACK1Right,>RgLANCE_ATTACK1Right,>RgLANCE_STANDRight,>RgLANCE_STANDRight,>RgLANCE_STANDRight,>RgLANCE_CLIMB1Right,>RgLANCE_CLIMB2Right,>RgLANCE_UPSTANDRight,>RgLANCE_DIAGUPRight,>RgLANCE_DIAGDOWNRight,>RgLANCE_UPWALK1Right,>RgLANCE_UPWALK2Right,>RgLANCE_UPSTANDRight,>RgLANCE_DIAGUPWALK1Right,>RgLANCE_DIAGUPWALK2Right,>RgLANCE_DIAGUPRight,>RgLANCE_DIAGDOWNWALK1Right,>RgLANCE_DIAGDOWNWALK2Right,>RgLANCE_DIAGDOWNRight,>RgLANCE_STANDRight,>RgLANCE_UPSTANDRight,>RgLANCE_HURTRight,>RgLANCE_HURTRight,>RgLANCE_HURTRight,>RgLANCE_DIE3Right,>RgLANCE_DIE3Right,>RgLANCE_STANDRight,>RgLANCE_CROUCHATTACK1Right,>RgLANCE_CROUCHATTACK1Right,>RgLANCE_CROUCHATTACK1Right,>RgLANCE_CROUCHATTACK1Right,>RgLANCE_CROUCHATTACK1Right,>RgLANCE_CROUCHATTACK1Right,>RgLANCE_HURTRight,>RgLANCE_HURTRight,>RgLANCE_HURTRight,>RgLANCE_HURTRight,>RgLANCE_HURTRight,>RgLANCE_STANDRight,>RgLANCE_WALK1Right,>RgLANCE_WALK2Right,>RgLANCE_WALK3Right,>RgLANCE_JUMP1Right,>RgLANCE_JUMP2Right,>RgLANCE_JUMP3Right,>RgLANCE_JUMP4Right,>RgLANCE_CROUCHRight,>RgLANCE_ATTACK1Right,>RgLANCE_ATTACK1Right,>RgLANCE_ATTACK1Right,>RgLANCE_STANDRight,>RgLANCE_STANDRight,>RgLANCE_STANDRight,>RgLANCE_CLIMB1Right,>RgLANCE_CLIMB2Right,>RgLANCE_UPSTANDRight,>RgLANCE_DIAGUPRight,>RgLANCE_DIAGDOWNRight,>RgLANCE_UPWALK1Right,>RgLANCE_UPWALK2Right,>RgLANCE_UPSTANDRight,>RgLANCE_DIAGUPWALK1Right,>RgLANCE_DIAGUPWALK2Right,>RgLANCE_DIAGUPRight,>RgLANCE_DIAGDOWNWALK1Right,>RgLANCE_DIAGDOWNWALK2Right,>RgLANCE_DIAGDOWNRight,>RgLANCE_STANDRight,>RgLANCE_UPSTANDRight,>RgLANCE_HURTRight,>RgLANCE_HURTRight,>RgLANCE_HURTRight,>RgLANCE_DIE3Right,>RgLANCE_DIE3Right,>RgLANCE_STANDRight,>RgLANCE_CROUCHATTACK1Right,>RgLANCE_CROUCHATTACK1Right,>RgLANCE_CROUCHATTACK1Right,>RgLANCE_CROUCHATTACK1Right,>RgLANCE_CROUCHATTACK1Right,>RgLANCE_CROUCHATTACK1Right,>RgLANCE_HURTRight,>RgLANCE_HURTRight,>RgLANCE_HURTRight,>RgLANCE_HURTRight,>RgLANCE_HURTRight,>RgLANCE_STANDRight,>RgLANCE_WALK1Right,>RgLANCE_WALK2Right,>RgLANCE_WALK3Right,>RgLANCE_JUMP1Right,>RgLANCE_JUMP2Right,>RgLANCE_JUMP3Right,>RgLANCE_JUMP4Right,>RgLANCE_CROUCHRight,>RgLANCE_ATTACK1Right,>RgLANCE_ATTACK1Right,>RgLANCE_ATTACK1Right,>RgLANCE_STANDRight,>RgLANCE_STANDRight,>RgLANCE_STANDRight,>RgLANCE_CLIMB1Right,>RgLANCE_CLIMB2Right,>RgLANCE_UPSTANDRight,>RgLANCE_DIAGUPRight,>RgLANCE_DIAGDOWNRight,>RgLANCE_UPWALK1Right,>RgLANCE_UPWALK2Right,>RgLANCE_UPSTANDRight,>RgLANCE_DIAGUPWALK1Right,>RgLANCE_DIAGUPWALK2Right,>RgLANCE_DIAGUPRight,>RgLANCE_DIAGDOWNWALK1Right,>RgLANCE_DIAGDOWNWALK2Right,>RgLANCE_DIAGDOWNRight,>RgLANCE_STANDRight,>RgLANCE_UPSTANDRight,>RgLANCE_HURTRight,>RgLANCE_HURTRight,>RgLANCE_HURTRight,>RgLANCE_DIE3Right,>RgLANCE_DIE3Right,>RgLANCE_STANDRight,>RgLANCE_CROUCHATTACK1Right,>RgLANCE_CROUCHATTACK1Right,>RgLANCE_CROUCHATTACK1Right,>RgLANCE_CROUCHATTACK1Right,>RgLANCE_CROUCHATTACK1Right,>RgLANCE_CROUCHATTACK1Right,>RgLANCE_HURTRight,>RgLANCE_HURTRight,>RgLANCE_HURTRight,>RgLANCE_HURTRight,>RgLANCE_HURTRight
RgLANCEBanks:
 .byte 117,122,118,126,124,123,125,123,119,122,122,122,117,117,117,125,119,124,126,127,124,118,124,116,127,126,116,117,127,117,124,125,125,125,123,123,117,119,119,119,119,119,119,125,125,125,125,125,117,122,118,126,124,123,125,123,119,122,122,122,117,117,117,125,119,124,126,127,124,118,124,116,127,126,116,117,127,117,124,125,125,125,123,123,117,119,119,119,119,119,119,125,125,125,125,125,117,122,118,126,124,123,125,123,119,122,122,122,117,117,117,125,119,124,126,127,124,118,124,116,127,126,116,117,127,117,124,125,125,125,123,123,117,119,119,119,119,119,119,125,125,125,125,125
.popseg
