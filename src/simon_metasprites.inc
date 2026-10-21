; Generated from the pinned hosted SWF.
.pushseg
.segment "SIMON_GFX"
RgSIMON0_STANDLeft:
  .byte 16
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $40, 2, 8
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $80, 2, 0
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $80, 18, 8
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $c0, 18, 0
RgSIMON0_STANDRight:
  .byte 16
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 2, 0
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c0, 2, 8
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c0, 18, 0
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $80, 18, 8
RgSIMON0_WALK1Left:
  .byte 16
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 1, 6
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $80, 1, -2
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c0, 17, 6
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $80, 17, -2
RgSIMON0_WALK1Right:
  .byte 16
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 1, 2
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c0, 1, 10
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $80, 17, 2
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c0, 17, 10
RgSIMON0_WALK2Left = RgSIMON0_STANDLeft
RgSIMON0_WALK2Right = RgSIMON0_STANDRight
RgSIMON0_WALK3Left = RgSIMON0_WALK1Left
RgSIMON0_WALK3Right = RgSIMON0_WALK1Right
RgSIMON0_JUMP1Left:
  .byte 16
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 9, 8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 9, 0
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c0, 25, 8
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $80, 25, 0
RgSIMON0_JUMP1Right:
  .byte 16
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 9, 0
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $40, 9, 8
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $80, 25, 0
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c0, 25, 8
RgSIMON0_JUMP2Left = RgSIMON0_JUMP1Left
RgSIMON0_JUMP2Right = RgSIMON0_JUMP1Right
RgSIMON0_JUMP3Left = RgSIMON0_JUMP1Left
RgSIMON0_JUMP3Right = RgSIMON0_JUMP1Right
RgSIMON0_JUMP4Left = RgSIMON0_JUMP1Left
RgSIMON0_JUMP4Right = RgSIMON0_JUMP1Right
RgSIMON0_CROUCHLeft = RgSIMON0_JUMP1Left
RgSIMON0_CROUCHRight = RgSIMON0_JUMP1Right
RgSIMON0_ATTACK1Left:
  .byte 32
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 1, 16
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 1, 8
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $80, 17, 8
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c0, 17, 0
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $02, 10, 24
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $82, 26, 24
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $87, 9, 24
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c7, 25, 24
RgSIMON0_ATTACK1Right:
  .byte 32
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 1, -8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $40, 1, 0
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c0, 17, 0
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $80, 17, 8
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $42, 10, -16
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c2, 26, -16
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c7, 9, -16
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $87, 25, -16
RgSIMON0_ATTACK2Left:
  .byte 32
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, 1, 8
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 17, 8
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 17, 0
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $42, -7, 16
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $42, 9, 24
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $47, 1, 24
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $87, 1, 16
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c7, 17, 24
RgSIMON0_ATTACK2Right:
  .byte 32
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 1, 0
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 17, 0
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 17, 8
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $02, -7, -8
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $02, 9, -16
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $07, 1, -16
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c7, 1, -8
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $87, 17, -16
RgSIMON0_ATTACK3Left:
  .byte 44
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $40, 3, 8
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $80, 3, 0
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 3, -8
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $80, 19, 8
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c0, 19, 0
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $42, -2, -28
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c2, 14, -12
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c2, 14, -20
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c7, 8, -13
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $87, 8, -21
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $87, 8, -29
RgSIMON0_ATTACK3Right:
  .byte 44
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $00, 3, 0
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c0, 3, 8
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $40, 3, 16
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c0, 19, 0
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $80, 19, 8
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $02, -2, 36
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $82, 14, 20
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $82, 14, 28
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $87, 8, 21
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c7, 8, 29
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c7, 8, 37
RgSIMON0_THROW1Left:
  .byte 16
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 1, 16
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 1, 8
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $80, 17, 8
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c0, 17, 0
RgSIMON0_THROW1Right:
  .byte 16
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 1, -8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $40, 1, 0
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c0, 17, 0
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $80, 17, 8
RgSIMON0_THROW2Left:
  .byte 12
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 1, 8
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $80, 17, 8
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c0, 17, 0
RgSIMON0_THROW2Right:
  .byte 12
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 1, 0
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c0, 17, 0
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $80, 17, 8
RgSIMON0_THROW3Left:
  .byte 20
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $40, 3, 8
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $80, 3, 0
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 3, -8
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $80, 19, 8
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c0, 19, 0
RgSIMON0_THROW3Right:
  .byte 20
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $00, 3, 0
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c0, 3, 8
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $40, 3, 16
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c0, 19, 0
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $80, 19, 8
RgSIMON0_CLIMB1Left:
  .byte 20
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $c0, 1, 9
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 1, 1
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 1, -7
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c0, 17, 9
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c0, 17, 1
RgSIMON0_CLIMB1Right:
  .byte 20
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $80, 1, -1
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $40, 1, 7
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $40, 1, 15
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $80, 17, -1
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $80, 17, 7
RgSIMON0_CLIMB2Left:
  .byte 20
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $40, 1, 8
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $40, 1, 0
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $80, 1, -8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $40, 17, 8
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $80, 17, 0
RgSIMON0_CLIMB2Right:
  .byte 20
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 1, 0
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 1, 8
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c0, 1, 16
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $00, 17, 0
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c0, 17, 8
RgSIMON0_UPSTANDLeft = RgSIMON0_STANDLeft
RgSIMON0_UPSTANDRight = RgSIMON0_STANDRight
RgSIMON0_DIAGUPLeft = RgSIMON0_STANDLeft
RgSIMON0_DIAGUPRight = RgSIMON0_STANDRight
RgSIMON0_DIAGDOWNLeft = RgSIMON0_STANDLeft
RgSIMON0_DIAGDOWNRight = RgSIMON0_STANDRight
RgSIMON0_UPWALK1Left = RgSIMON0_STANDLeft
RgSIMON0_UPWALK1Right = RgSIMON0_STANDRight
RgSIMON0_UPWALK2Left = RgSIMON0_STANDLeft
RgSIMON0_UPWALK2Right = RgSIMON0_STANDRight
RgSIMON0_UPWALK3Left = RgSIMON0_STANDLeft
RgSIMON0_UPWALK3Right = RgSIMON0_STANDRight
RgSIMON0_DIAGUPWALK1Left = RgSIMON0_STANDLeft
RgSIMON0_DIAGUPWALK1Right = RgSIMON0_STANDRight
RgSIMON0_DIAGUPWALK2Left = RgSIMON0_STANDLeft
RgSIMON0_DIAGUPWALK2Right = RgSIMON0_STANDRight
RgSIMON0_DIAGUPWALK3Left = RgSIMON0_STANDLeft
RgSIMON0_DIAGUPWALK3Right = RgSIMON0_STANDRight
RgSIMON0_DIAGDOWNWALK1Left = RgSIMON0_STANDLeft
RgSIMON0_DIAGDOWNWALK1Right = RgSIMON0_STANDRight
RgSIMON0_DIAGDOWNWALK2Left = RgSIMON0_STANDLeft
RgSIMON0_DIAGDOWNWALK2Right = RgSIMON0_STANDRight
RgSIMON0_DIAGDOWNWALK3Left = RgSIMON0_STANDLeft
RgSIMON0_DIAGDOWNWALK3Right = RgSIMON0_STANDRight
RgSIMON0_DOWNTHRUSTLeft = RgSIMON0_STANDLeft
RgSIMON0_DOWNTHRUSTRight = RgSIMON0_STANDRight
RgSIMON0_UPTHRUSTLeft = RgSIMON0_STANDLeft
RgSIMON0_UPTHRUSTRight = RgSIMON0_STANDRight
RgSIMON0_HURTLeft:
  .byte 16
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $40, 3, 8
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $80, 3, 0
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c0, 19, 8
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $c0, 19, 0
RgSIMON0_HURTRight:
  .byte 16
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 3, 0
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c0, 3, 8
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $80, 19, 0
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $80, 19, 8
RgSIMON0_DIE1Left:
  .byte 16
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $40, 11, 8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $00, 11, 0
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c0, 27, 8
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $80, 27, 0
RgSIMON0_DIE1Right:
  .byte 16
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $00, 11, 0
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $40, 11, 8
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $80, 27, 0
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c0, 27, 8
RgSIMON0_DIE2Left:
  .byte 16
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, 17, 16
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 17, 8
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 17, 0
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 17, -8
RgSIMON0_DIE2Right:
  .byte 16
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 17, -8
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 17, 0
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 17, 8
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $40, 17, 16
RgSIMON0_DIE3Left = RgSIMON0_DIE2Left
RgSIMON0_DIE3Right = RgSIMON0_DIE2Right
RgSIMON0_DIE4Left = RgSIMON0_DIE2Left
RgSIMON0_DIE4Right = RgSIMON0_DIE2Right
RgSIMON0_SLIDELeft = RgSIMON0_THROW3Left
RgSIMON0_SLIDERight = RgSIMON0_THROW3Right
RgSIMON0_CROUCHATTACK1Left:
  .byte 32
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $40, 8, 16
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 8, 8
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c0, 24, 8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $80, 24, 0
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $02, 17, 24
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $82, 33, 24
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c7, 16, 24
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c7, 32, 24
RgSIMON0_CROUCHATTACK1Right:
  .byte 32
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 8, -8
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $40, 8, 0
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $80, 24, 0
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c0, 24, 8
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $42, 17, -16
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c2, 33, -16
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $87, 16, -16
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $87, 32, -16
RgSIMON0_CROUCHATTACK2Left:
  .byte 32
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 8, 8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c0, 24, 8
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $80, 24, 0
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $42, 0, 16
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $42, 16, 24
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $47, 0, 16
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c7, 16, 24
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $87, 16, 16
RgSIMON0_CROUCHATTACK2Right:
  .byte 32
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 8, 0
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $80, 24, 0
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c0, 24, 8
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $02, 0, -8
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $02, 16, -16
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $07, 0, -8
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $87, 16, -16
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c7, 16, -8
RgSIMON0_CROUCHATTACK3Left:
  .byte 44
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 10, 8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 10, 0
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 10, -8
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c0, 26, 8
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $80, 26, 0
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $42, 5, -28
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c2, 21, -12
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c2, 21, -20
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c7, 15, -13
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $87, 15, -21
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $87, 15, -29
RgSIMON0_CROUCHATTACK3Right:
  .byte 44
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 10, 0
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $40, 10, 8
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $40, 10, 16
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $80, 26, 0
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c0, 26, 8
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $02, 5, 36
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $82, 21, 20
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $82, 21, 28
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $87, 15, 21
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c7, 15, 29
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c7, 15, 37
RgSIMON0_CROUCHTHROW1Left:
  .byte 16
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 8, 16
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 8, 8
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 24, 8
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $80, 24, 0
RgSIMON0_CROUCHTHROW1Right:
  .byte 16
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 8, -8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $40, 8, 0
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 24, 0
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c0, 24, 8
RgSIMON0_CROUCHTHROW2Left:
  .byte 12
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 8, 8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c0, 24, 8
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $80, 24, 0
RgSIMON0_CROUCHTHROW2Right:
  .byte 12
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 8, 0
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $80, 24, 0
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c0, 24, 8
RgSIMON0_CROUCHTHROW3Left:
  .byte 20
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 10, 8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 10, 0
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 10, -8
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c0, 26, 8
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $80, 26, 0
RgSIMON0_CROUCHTHROW3Right:
  .byte 20
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 10, 0
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $40, 10, 8
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $40, 10, 16
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $80, 26, 0
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c0, 26, 8
RgSIMON0_DIEFLASH1Left = RgSIMON0_STANDLeft
RgSIMON0_DIEFLASH1Right = RgSIMON0_STANDRight
RgSIMON0_DIEFLASH2Left = RgSIMON0_STANDLeft
RgSIMON0_DIEFLASH2Right = RgSIMON0_STANDRight
RgSIMON0_DIEGRAYLeft = RgSIMON0_STANDLeft
RgSIMON0_DIEGRAYRight = RgSIMON0_STANDRight
RgSIMON0_DIECROSS1Left = RgSIMON0_STANDLeft
RgSIMON0_DIECROSS1Right = RgSIMON0_STANDRight
RgSIMON0_DIECROSS2Left = RgSIMON0_STANDLeft
RgSIMON0_DIECROSS2Right = RgSIMON0_STANDRight
RgSIMON1_STANDLeft = RgSIMON0_STANDLeft
RgSIMON1_STANDRight = RgSIMON0_STANDRight
RgSIMON1_WALK1Left = RgSIMON0_WALK1Left
RgSIMON1_WALK1Right = RgSIMON0_WALK1Right
RgSIMON1_WALK2Left = RgSIMON0_STANDLeft
RgSIMON1_WALK2Right = RgSIMON0_STANDRight
RgSIMON1_WALK3Left = RgSIMON0_WALK1Left
RgSIMON1_WALK3Right = RgSIMON0_WALK1Right
RgSIMON1_JUMP1Left = RgSIMON0_JUMP1Left
RgSIMON1_JUMP1Right = RgSIMON0_JUMP1Right
RgSIMON1_JUMP2Left = RgSIMON0_JUMP1Left
RgSIMON1_JUMP2Right = RgSIMON0_JUMP1Right
RgSIMON1_JUMP3Left = RgSIMON0_JUMP1Left
RgSIMON1_JUMP3Right = RgSIMON0_JUMP1Right
RgSIMON1_JUMP4Left = RgSIMON0_JUMP1Left
RgSIMON1_JUMP4Right = RgSIMON0_JUMP1Right
RgSIMON1_CROUCHLeft = RgSIMON0_JUMP1Left
RgSIMON1_CROUCHRight = RgSIMON0_JUMP1Right
RgSIMON1_ATTACK1Left:
  .byte 32
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, 1, 16
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 1, 8
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 17, 8
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 17, 0
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $02, 10, 24
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c2, 26, 24
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $87, 9, 24
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c7, 25, 24
RgSIMON1_ATTACK1Right:
  .byte 32
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 1, -8
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, 1, 0
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 17, 0
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 17, 8
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $42, 10, -16
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $82, 26, -16
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c7, 9, -16
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $87, 25, -16
RgSIMON1_ATTACK2Left:
  .byte 28
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 1, 8
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $80, 17, 8
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c0, 17, 0
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $42, -7, 16
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c2, 9, 24
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $47, -7, 16
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $47, 9, 24
RgSIMON1_ATTACK2Right:
  .byte 28
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 1, 0
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c0, 17, 0
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $80, 17, 8
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $02, -7, -8
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $82, 9, -16
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $07, -7, -8
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $07, 9, -16
RgSIMON1_ATTACK3Left:
  .byte 72
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 3, 8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $80, 3, 0
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $80, 19, 8
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c0, 19, 0
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c2, 11, -8
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $82, 11, -16
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $82, 11, -24
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $82, 11, -32
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $82, 11, -40
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $82, 11, -48
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $07, -1, -8
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $47, -1, -40
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $07, -1, -48
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $87, 15, -8
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $87, 15, -16
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $87, 15, -24
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $87, 15, -32
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $87, 15, -40
RgSIMON1_ATTACK3Right:
  .byte 72
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 3, 0
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c0, 3, 8
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c0, 19, 0
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $80, 19, 8
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $82, 11, 16
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c2, 11, 24
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c2, 11, 32
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c2, 11, 40
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c2, 11, 48
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c2, 11, 56
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $47, -1, 16
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $07, -1, 48
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $47, -1, 56
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c7, 15, 16
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c7, 15, 24
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c7, 15, 32
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c7, 15, 40
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c7, 15, 48
RgSIMON1_THROW1Left = RgSIMON0_THROW1Left
RgSIMON1_THROW1Right = RgSIMON0_THROW1Right
RgSIMON1_THROW2Left:
  .byte 12
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, 1, 8
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 17, 8
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 17, 0
RgSIMON1_THROW2Right:
  .byte 12
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 1, 0
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 17, 0
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 17, 8
RgSIMON1_THROW3Left = RgSIMON0_THROW3Left
RgSIMON1_THROW3Right = RgSIMON0_THROW3Right
RgSIMON1_CLIMB1Left = RgSIMON0_CLIMB1Left
RgSIMON1_CLIMB1Right = RgSIMON0_CLIMB1Right
RgSIMON1_CLIMB2Left = RgSIMON0_CLIMB2Left
RgSIMON1_CLIMB2Right = RgSIMON0_CLIMB2Right
RgSIMON1_UPSTANDLeft = RgSIMON0_STANDLeft
RgSIMON1_UPSTANDRight = RgSIMON0_STANDRight
RgSIMON1_DIAGUPLeft = RgSIMON0_STANDLeft
RgSIMON1_DIAGUPRight = RgSIMON0_STANDRight
RgSIMON1_DIAGDOWNLeft = RgSIMON0_STANDLeft
RgSIMON1_DIAGDOWNRight = RgSIMON0_STANDRight
RgSIMON1_UPWALK1Left = RgSIMON0_STANDLeft
RgSIMON1_UPWALK1Right = RgSIMON0_STANDRight
RgSIMON1_UPWALK2Left = RgSIMON0_STANDLeft
RgSIMON1_UPWALK2Right = RgSIMON0_STANDRight
RgSIMON1_UPWALK3Left = RgSIMON0_STANDLeft
RgSIMON1_UPWALK3Right = RgSIMON0_STANDRight
RgSIMON1_DIAGUPWALK1Left = RgSIMON0_STANDLeft
RgSIMON1_DIAGUPWALK1Right = RgSIMON0_STANDRight
RgSIMON1_DIAGUPWALK2Left = RgSIMON0_STANDLeft
RgSIMON1_DIAGUPWALK2Right = RgSIMON0_STANDRight
RgSIMON1_DIAGUPWALK3Left = RgSIMON0_STANDLeft
RgSIMON1_DIAGUPWALK3Right = RgSIMON0_STANDRight
RgSIMON1_DIAGDOWNWALK1Left = RgSIMON0_STANDLeft
RgSIMON1_DIAGDOWNWALK1Right = RgSIMON0_STANDRight
RgSIMON1_DIAGDOWNWALK2Left = RgSIMON0_STANDLeft
RgSIMON1_DIAGDOWNWALK2Right = RgSIMON0_STANDRight
RgSIMON1_DIAGDOWNWALK3Left = RgSIMON0_STANDLeft
RgSIMON1_DIAGDOWNWALK3Right = RgSIMON0_STANDRight
RgSIMON1_DOWNTHRUSTLeft = RgSIMON0_STANDLeft
RgSIMON1_DOWNTHRUSTRight = RgSIMON0_STANDRight
RgSIMON1_UPTHRUSTLeft = RgSIMON0_STANDLeft
RgSIMON1_UPTHRUSTRight = RgSIMON0_STANDRight
RgSIMON1_HURTLeft = RgSIMON0_HURTLeft
RgSIMON1_HURTRight = RgSIMON0_HURTRight
RgSIMON1_DIE1Left = RgSIMON0_DIE1Left
RgSIMON1_DIE1Right = RgSIMON0_DIE1Right
RgSIMON1_DIE2Left = RgSIMON0_DIE2Left
RgSIMON1_DIE2Right = RgSIMON0_DIE2Right
RgSIMON1_DIE3Left = RgSIMON0_DIE2Left
RgSIMON1_DIE3Right = RgSIMON0_DIE2Right
RgSIMON1_DIE4Left = RgSIMON0_DIE2Left
RgSIMON1_DIE4Right = RgSIMON0_DIE2Right
RgSIMON1_SLIDELeft = RgSIMON0_THROW3Left
RgSIMON1_SLIDERight = RgSIMON0_THROW3Right
RgSIMON1_CROUCHATTACK1Left:
  .byte 32
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 8, 16
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 8, 8
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 24, 8
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $80, 24, 0
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $82, 17, 24
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $82, 33, 24
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $87, 16, 24
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c7, 32, 24
RgSIMON1_CROUCHATTACK1Right:
  .byte 32
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 8, -8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $40, 8, 0
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 24, 0
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c0, 24, 8
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c2, 17, -16
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c2, 33, -16
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c7, 16, -16
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $87, 32, -16
RgSIMON1_CROUCHATTACK2Left:
  .byte 28
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 8, 8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c0, 24, 8
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $80, 24, 0
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $42, 0, 16
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c2, 16, 24
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $47, 0, 16
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $47, 16, 24
RgSIMON1_CROUCHATTACK2Right:
  .byte 28
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 8, 0
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $80, 24, 0
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c0, 24, 8
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $02, 0, -8
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $82, 16, -16
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $07, 0, -8
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $07, 16, -16
RgSIMON1_CROUCHATTACK3Left:
  .byte 56
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 10, 8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 10, 0
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c0, 26, 8
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $80, 26, 0
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c2, 18, -8
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $82, 18, -16
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $82, 18, -24
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $82, 18, -32
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $82, 18, -40
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $87, 18, -8
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $87, 18, -16
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $87, 18, -24
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $87, 18, -32
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $87, 18, -40
RgSIMON1_CROUCHATTACK3Right:
  .byte 56
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 10, 0
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $40, 10, 8
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $80, 26, 0
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c0, 26, 8
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $82, 18, 16
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c2, 18, 24
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c2, 18, 32
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c2, 18, 40
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c2, 18, 48
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c7, 18, 16
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c7, 18, 24
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c7, 18, 32
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $c7, 18, 40
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c7, 18, 48
RgSIMON1_CROUCHTHROW1Left = RgSIMON0_CROUCHTHROW1Left
RgSIMON1_CROUCHTHROW1Right = RgSIMON0_CROUCHTHROW1Right
RgSIMON1_CROUCHTHROW2Left = RgSIMON0_CROUCHTHROW2Left
RgSIMON1_CROUCHTHROW2Right = RgSIMON0_CROUCHTHROW2Right
RgSIMON1_CROUCHTHROW3Left = RgSIMON0_CROUCHTHROW3Left
RgSIMON1_CROUCHTHROW3Right = RgSIMON0_CROUCHTHROW3Right
RgSIMON1_DIEFLASH1Left = RgSIMON0_STANDLeft
RgSIMON1_DIEFLASH1Right = RgSIMON0_STANDRight
RgSIMON1_DIEFLASH2Left = RgSIMON0_STANDLeft
RgSIMON1_DIEFLASH2Right = RgSIMON0_STANDRight
RgSIMON1_DIEGRAYLeft = RgSIMON0_STANDLeft
RgSIMON1_DIEGRAYRight = RgSIMON0_STANDRight
RgSIMON1_DIECROSS1Left = RgSIMON0_STANDLeft
RgSIMON1_DIECROSS1Right = RgSIMON0_STANDRight
RgSIMON1_DIECROSS2Left = RgSIMON0_STANDLeft
RgSIMON1_DIECROSS2Right = RgSIMON0_STANDRight
RgSIMON2_STANDLeft = RgSIMON0_STANDLeft
RgSIMON2_STANDRight = RgSIMON0_STANDRight
RgSIMON2_WALK1Left = RgSIMON0_WALK1Left
RgSIMON2_WALK1Right = RgSIMON0_WALK1Right
RgSIMON2_WALK2Left = RgSIMON0_STANDLeft
RgSIMON2_WALK2Right = RgSIMON0_STANDRight
RgSIMON2_WALK3Left = RgSIMON0_WALK1Left
RgSIMON2_WALK3Right = RgSIMON0_WALK1Right
RgSIMON2_JUMP1Left = RgSIMON0_JUMP1Left
RgSIMON2_JUMP1Right = RgSIMON0_JUMP1Right
RgSIMON2_JUMP2Left = RgSIMON0_JUMP1Left
RgSIMON2_JUMP2Right = RgSIMON0_JUMP1Right
RgSIMON2_JUMP3Left = RgSIMON0_JUMP1Left
RgSIMON2_JUMP3Right = RgSIMON0_JUMP1Right
RgSIMON2_JUMP4Left = RgSIMON0_JUMP1Left
RgSIMON2_JUMP4Right = RgSIMON0_JUMP1Right
RgSIMON2_CROUCHLeft = RgSIMON0_JUMP1Left
RgSIMON2_CROUCHRight = RgSIMON0_JUMP1Right
RgSIMON2_ATTACK1Left:
  .byte 24
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $40, 1, 24
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 1, 16
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 1, 8
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $00, 17, 24
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $80, 17, 8
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c0, 17, 0
RgSIMON2_ATTACK1Right:
  .byte 24
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $00, 1, -16
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 1, -8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $40, 1, 0
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $40, 17, -16
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c0, 17, 0
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $80, 17, 8
RgSIMON2_ATTACK2Left:
  .byte 24
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $40, 1, 24
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $80, 1, 16
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, 1, 8
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $c0, 17, 24
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 17, 8
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 17, 0
RgSIMON2_ATTACK2Right:
  .byte 24
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $00, 1, -16
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c0, 1, -8
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 1, 0
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $80, 17, -16
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 17, 0
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 17, 8
RgSIMON2_ATTACK3Left:
  .byte 44
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 3, 8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $80, 3, 0
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 3, -8
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $80, 19, 8
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c0, 19, 0
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c2, 8, -13
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c2, 8, -21
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c2, 8, -29
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c2, 8, -37
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c2, 8, -45
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $82, 8, -53
RgSIMON2_ATTACK3Right:
  .byte 44
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 3, 0
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c0, 3, 8
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $40, 3, 16
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c0, 19, 0
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $80, 19, 8
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $82, 8, 21
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $82, 8, 29
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $82, 8, 37
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $82, 8, 45
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $82, 8, 53
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c2, 8, 61
RgSIMON2_THROW1Left = RgSIMON0_THROW1Left
RgSIMON2_THROW1Right = RgSIMON0_THROW1Right
RgSIMON2_THROW2Left = RgSIMON1_THROW2Left
RgSIMON2_THROW2Right = RgSIMON1_THROW2Right
RgSIMON2_THROW3Left = RgSIMON0_THROW3Left
RgSIMON2_THROW3Right = RgSIMON0_THROW3Right
RgSIMON2_CLIMB1Left = RgSIMON0_CLIMB1Left
RgSIMON2_CLIMB1Right = RgSIMON0_CLIMB1Right
RgSIMON2_CLIMB2Left = RgSIMON0_CLIMB2Left
RgSIMON2_CLIMB2Right = RgSIMON0_CLIMB2Right
RgSIMON2_UPSTANDLeft = RgSIMON0_STANDLeft
RgSIMON2_UPSTANDRight = RgSIMON0_STANDRight
RgSIMON2_DIAGUPLeft = RgSIMON0_STANDLeft
RgSIMON2_DIAGUPRight = RgSIMON0_STANDRight
RgSIMON2_DIAGDOWNLeft = RgSIMON0_STANDLeft
RgSIMON2_DIAGDOWNRight = RgSIMON0_STANDRight
RgSIMON2_UPWALK1Left = RgSIMON0_STANDLeft
RgSIMON2_UPWALK1Right = RgSIMON0_STANDRight
RgSIMON2_UPWALK2Left = RgSIMON0_STANDLeft
RgSIMON2_UPWALK2Right = RgSIMON0_STANDRight
RgSIMON2_UPWALK3Left = RgSIMON0_STANDLeft
RgSIMON2_UPWALK3Right = RgSIMON0_STANDRight
RgSIMON2_DIAGUPWALK1Left = RgSIMON0_STANDLeft
RgSIMON2_DIAGUPWALK1Right = RgSIMON0_STANDRight
RgSIMON2_DIAGUPWALK2Left = RgSIMON0_STANDLeft
RgSIMON2_DIAGUPWALK2Right = RgSIMON0_STANDRight
RgSIMON2_DIAGUPWALK3Left = RgSIMON0_STANDLeft
RgSIMON2_DIAGUPWALK3Right = RgSIMON0_STANDRight
RgSIMON2_DIAGDOWNWALK1Left = RgSIMON0_STANDLeft
RgSIMON2_DIAGDOWNWALK1Right = RgSIMON0_STANDRight
RgSIMON2_DIAGDOWNWALK2Left = RgSIMON0_STANDLeft
RgSIMON2_DIAGDOWNWALK2Right = RgSIMON0_STANDRight
RgSIMON2_DIAGDOWNWALK3Left = RgSIMON0_STANDLeft
RgSIMON2_DIAGDOWNWALK3Right = RgSIMON0_STANDRight
RgSIMON2_DOWNTHRUSTLeft = RgSIMON0_STANDLeft
RgSIMON2_DOWNTHRUSTRight = RgSIMON0_STANDRight
RgSIMON2_UPTHRUSTLeft = RgSIMON0_STANDLeft
RgSIMON2_UPTHRUSTRight = RgSIMON0_STANDRight
RgSIMON2_HURTLeft = RgSIMON0_HURTLeft
RgSIMON2_HURTRight = RgSIMON0_HURTRight
RgSIMON2_DIE1Left:
  .byte 28
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 11, 8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 11, 0
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c0, 27, 8
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $80, 27, 0
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $02, 0, 1
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $82, 16, 9
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $02, 16, 1
RgSIMON2_DIE1Right:
  .byte 28
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 11, 0
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $40, 11, 8
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $80, 27, 0
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c0, 27, 8
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $42, 0, 7
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c2, 16, -1
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $42, 16, 7
RgSIMON2_DIE2Left:
  .byte 32
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, 17, 16
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $80, 17, 8
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 17, 0
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 17, -8
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $42, 18, 15
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $82, 18, 7
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $02, 18, -1
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $02, 18, -9
RgSIMON2_DIE2Right:
  .byte 32
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 17, -8
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c0, 17, 0
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 17, 8
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $40, 17, 16
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $02, 18, -7
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c2, 18, 1
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $42, 18, 9
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $42, 18, 17
RgSIMON2_DIE3Left = RgSIMON2_DIE2Left
RgSIMON2_DIE3Right = RgSIMON2_DIE2Right
RgSIMON2_DIE4Left = RgSIMON2_DIE2Left
RgSIMON2_DIE4Right = RgSIMON2_DIE2Right
RgSIMON2_SLIDELeft = RgSIMON0_THROW3Left
RgSIMON2_SLIDERight = RgSIMON0_THROW3Right
RgSIMON2_CROUCHATTACK1Left:
  .byte 24
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $40, 8, 24
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 8, 16
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 8, 8
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $00, 24, 24
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 24, 8
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $80, 24, 0
RgSIMON2_CROUCHATTACK1Right:
  .byte 24
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $00, 8, -16
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 8, -8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $40, 8, 0
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $40, 24, -16
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 24, 0
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c0, 24, 8
RgSIMON2_CROUCHATTACK2Left:
  .byte 20
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 0, 16
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $40, 0, 8
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $40, 16, 24
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 16, 8
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 16, 0
RgSIMON2_CROUCHATTACK2Right:
  .byte 20
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 0, -8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 0, 0
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 16, -16
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 16, 0
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, 16, 8
RgSIMON2_CROUCHATTACK3Left:
  .byte 44
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 10, 8
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 10, 0
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $00, 10, -8
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c0, 26, 8
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $80, 26, 0
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c2, 15, -13
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c2, 15, -21
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c2, 15, -29
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c2, 15, -37
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c2, 15, -45
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $82, 15, -53
RgSIMON2_CROUCHATTACK3Right:
  .byte 44
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 10, 0
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $40, 10, 8
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $40, 10, 16
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $80, 26, 0
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c0, 26, 8
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $82, 15, 21
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $82, 15, 29
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $82, 15, 37
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $82, 15, 45
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $82, 15, 53
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $c2, 15, 61
RgSIMON2_CROUCHTHROW1Left = RgSIMON0_CROUCHTHROW1Left
RgSIMON2_CROUCHTHROW1Right = RgSIMON0_CROUCHTHROW1Right
RgSIMON2_CROUCHTHROW2Left = RgSIMON0_CROUCHTHROW2Left
RgSIMON2_CROUCHTHROW2Right = RgSIMON0_CROUCHTHROW2Right
RgSIMON2_CROUCHTHROW3Left = RgSIMON0_CROUCHTHROW3Left
RgSIMON2_CROUCHTHROW3Right = RgSIMON0_CROUCHTHROW3Right
RgSIMON2_DIEFLASH1Left = RgSIMON0_STANDLeft
RgSIMON2_DIEFLASH1Right = RgSIMON0_STANDRight
RgSIMON2_DIEFLASH2Left = RgSIMON0_STANDLeft
RgSIMON2_DIEFLASH2Right = RgSIMON0_STANDRight
RgSIMON2_DIEGRAYLeft = RgSIMON0_STANDLeft
RgSIMON2_DIEGRAYRight = RgSIMON0_STANDRight
RgSIMON2_DIECROSS1Left = RgSIMON0_STANDLeft
RgSIMON2_DIECROSS1Right = RgSIMON0_STANDRight
RgSIMON2_DIECROSS2Left = RgSIMON0_STANDLeft
RgSIMON2_DIECROSS2Right = RgSIMON0_STANDRight
RgSIMONLeftLo:
  .byte <RgSIMON0_STANDLeft,<RgSIMON0_WALK1Left,<RgSIMON0_WALK2Left,<RgSIMON0_WALK3Left,<RgSIMON0_JUMP1Left,<RgSIMON0_JUMP2Left,<RgSIMON0_JUMP3Left,<RgSIMON0_JUMP4Left,<RgSIMON0_CROUCHLeft,<RgSIMON0_ATTACK1Left,<RgSIMON0_ATTACK2Left,<RgSIMON0_ATTACK3Left,<RgSIMON0_THROW1Left,<RgSIMON0_THROW2Left,<RgSIMON0_THROW3Left,<RgSIMON0_CLIMB1Left,<RgSIMON0_CLIMB2Left,<RgSIMON0_UPSTANDLeft,<RgSIMON0_DIAGUPLeft,<RgSIMON0_DIAGDOWNLeft,<RgSIMON0_UPWALK1Left,<RgSIMON0_UPWALK2Left,<RgSIMON0_UPWALK3Left,<RgSIMON0_DIAGUPWALK1Left,<RgSIMON0_DIAGUPWALK2Left,<RgSIMON0_DIAGUPWALK3Left,<RgSIMON0_DIAGDOWNWALK1Left,<RgSIMON0_DIAGDOWNWALK2Left,<RgSIMON0_DIAGDOWNWALK3Left,<RgSIMON0_DOWNTHRUSTLeft,<RgSIMON0_UPTHRUSTLeft,<RgSIMON0_HURTLeft,<RgSIMON0_DIE1Left,<RgSIMON0_DIE2Left,<RgSIMON0_DIE3Left,<RgSIMON0_DIE4Left,<RgSIMON0_SLIDELeft,<RgSIMON0_CROUCHATTACK1Left,<RgSIMON0_CROUCHATTACK2Left,<RgSIMON0_CROUCHATTACK3Left,<RgSIMON0_CROUCHTHROW1Left,<RgSIMON0_CROUCHTHROW2Left,<RgSIMON0_CROUCHTHROW3Left,<RgSIMON0_DIEFLASH1Left,<RgSIMON0_DIEFLASH2Left,<RgSIMON0_DIEGRAYLeft,<RgSIMON0_DIECROSS1Left,<RgSIMON0_DIECROSS2Left,<RgSIMON1_STANDLeft,<RgSIMON1_WALK1Left,<RgSIMON1_WALK2Left,<RgSIMON1_WALK3Left,<RgSIMON1_JUMP1Left,<RgSIMON1_JUMP2Left,<RgSIMON1_JUMP3Left,<RgSIMON1_JUMP4Left,<RgSIMON1_CROUCHLeft,<RgSIMON1_ATTACK1Left,<RgSIMON1_ATTACK2Left,<RgSIMON1_ATTACK3Left,<RgSIMON1_THROW1Left,<RgSIMON1_THROW2Left,<RgSIMON1_THROW3Left,<RgSIMON1_CLIMB1Left,<RgSIMON1_CLIMB2Left,<RgSIMON1_UPSTANDLeft,<RgSIMON1_DIAGUPLeft,<RgSIMON1_DIAGDOWNLeft,<RgSIMON1_UPWALK1Left,<RgSIMON1_UPWALK2Left,<RgSIMON1_UPWALK3Left,<RgSIMON1_DIAGUPWALK1Left,<RgSIMON1_DIAGUPWALK2Left,<RgSIMON1_DIAGUPWALK3Left,<RgSIMON1_DIAGDOWNWALK1Left,<RgSIMON1_DIAGDOWNWALK2Left,<RgSIMON1_DIAGDOWNWALK3Left,<RgSIMON1_DOWNTHRUSTLeft,<RgSIMON1_UPTHRUSTLeft,<RgSIMON1_HURTLeft,<RgSIMON1_DIE1Left,<RgSIMON1_DIE2Left,<RgSIMON1_DIE3Left,<RgSIMON1_DIE4Left,<RgSIMON1_SLIDELeft,<RgSIMON1_CROUCHATTACK1Left,<RgSIMON1_CROUCHATTACK2Left,<RgSIMON1_CROUCHATTACK3Left,<RgSIMON1_CROUCHTHROW1Left,<RgSIMON1_CROUCHTHROW2Left,<RgSIMON1_CROUCHTHROW3Left,<RgSIMON1_DIEFLASH1Left,<RgSIMON1_DIEFLASH2Left,<RgSIMON1_DIEGRAYLeft,<RgSIMON1_DIECROSS1Left,<RgSIMON1_DIECROSS2Left,<RgSIMON2_STANDLeft,<RgSIMON2_WALK1Left,<RgSIMON2_WALK2Left,<RgSIMON2_WALK3Left,<RgSIMON2_JUMP1Left,<RgSIMON2_JUMP2Left,<RgSIMON2_JUMP3Left,<RgSIMON2_JUMP4Left,<RgSIMON2_CROUCHLeft,<RgSIMON2_ATTACK1Left,<RgSIMON2_ATTACK2Left,<RgSIMON2_ATTACK3Left,<RgSIMON2_THROW1Left,<RgSIMON2_THROW2Left,<RgSIMON2_THROW3Left,<RgSIMON2_CLIMB1Left,<RgSIMON2_CLIMB2Left,<RgSIMON2_UPSTANDLeft,<RgSIMON2_DIAGUPLeft,<RgSIMON2_DIAGDOWNLeft,<RgSIMON2_UPWALK1Left,<RgSIMON2_UPWALK2Left,<RgSIMON2_UPWALK3Left,<RgSIMON2_DIAGUPWALK1Left,<RgSIMON2_DIAGUPWALK2Left,<RgSIMON2_DIAGUPWALK3Left,<RgSIMON2_DIAGDOWNWALK1Left,<RgSIMON2_DIAGDOWNWALK2Left,<RgSIMON2_DIAGDOWNWALK3Left,<RgSIMON2_DOWNTHRUSTLeft,<RgSIMON2_UPTHRUSTLeft,<RgSIMON2_HURTLeft,<RgSIMON2_DIE1Left,<RgSIMON2_DIE2Left,<RgSIMON2_DIE3Left,<RgSIMON2_DIE4Left,<RgSIMON2_SLIDELeft,<RgSIMON2_CROUCHATTACK1Left,<RgSIMON2_CROUCHATTACK2Left,<RgSIMON2_CROUCHATTACK3Left,<RgSIMON2_CROUCHTHROW1Left,<RgSIMON2_CROUCHTHROW2Left,<RgSIMON2_CROUCHTHROW3Left,<RgSIMON2_DIEFLASH1Left,<RgSIMON2_DIEFLASH2Left,<RgSIMON2_DIEGRAYLeft,<RgSIMON2_DIECROSS1Left,<RgSIMON2_DIECROSS2Left
RgSIMONLeftHi:
  .byte >RgSIMON0_STANDLeft,>RgSIMON0_WALK1Left,>RgSIMON0_WALK2Left,>RgSIMON0_WALK3Left,>RgSIMON0_JUMP1Left,>RgSIMON0_JUMP2Left,>RgSIMON0_JUMP3Left,>RgSIMON0_JUMP4Left,>RgSIMON0_CROUCHLeft,>RgSIMON0_ATTACK1Left,>RgSIMON0_ATTACK2Left,>RgSIMON0_ATTACK3Left,>RgSIMON0_THROW1Left,>RgSIMON0_THROW2Left,>RgSIMON0_THROW3Left,>RgSIMON0_CLIMB1Left,>RgSIMON0_CLIMB2Left,>RgSIMON0_UPSTANDLeft,>RgSIMON0_DIAGUPLeft,>RgSIMON0_DIAGDOWNLeft,>RgSIMON0_UPWALK1Left,>RgSIMON0_UPWALK2Left,>RgSIMON0_UPWALK3Left,>RgSIMON0_DIAGUPWALK1Left,>RgSIMON0_DIAGUPWALK2Left,>RgSIMON0_DIAGUPWALK3Left,>RgSIMON0_DIAGDOWNWALK1Left,>RgSIMON0_DIAGDOWNWALK2Left,>RgSIMON0_DIAGDOWNWALK3Left,>RgSIMON0_DOWNTHRUSTLeft,>RgSIMON0_UPTHRUSTLeft,>RgSIMON0_HURTLeft,>RgSIMON0_DIE1Left,>RgSIMON0_DIE2Left,>RgSIMON0_DIE3Left,>RgSIMON0_DIE4Left,>RgSIMON0_SLIDELeft,>RgSIMON0_CROUCHATTACK1Left,>RgSIMON0_CROUCHATTACK2Left,>RgSIMON0_CROUCHATTACK3Left,>RgSIMON0_CROUCHTHROW1Left,>RgSIMON0_CROUCHTHROW2Left,>RgSIMON0_CROUCHTHROW3Left,>RgSIMON0_DIEFLASH1Left,>RgSIMON0_DIEFLASH2Left,>RgSIMON0_DIEGRAYLeft,>RgSIMON0_DIECROSS1Left,>RgSIMON0_DIECROSS2Left,>RgSIMON1_STANDLeft,>RgSIMON1_WALK1Left,>RgSIMON1_WALK2Left,>RgSIMON1_WALK3Left,>RgSIMON1_JUMP1Left,>RgSIMON1_JUMP2Left,>RgSIMON1_JUMP3Left,>RgSIMON1_JUMP4Left,>RgSIMON1_CROUCHLeft,>RgSIMON1_ATTACK1Left,>RgSIMON1_ATTACK2Left,>RgSIMON1_ATTACK3Left,>RgSIMON1_THROW1Left,>RgSIMON1_THROW2Left,>RgSIMON1_THROW3Left,>RgSIMON1_CLIMB1Left,>RgSIMON1_CLIMB2Left,>RgSIMON1_UPSTANDLeft,>RgSIMON1_DIAGUPLeft,>RgSIMON1_DIAGDOWNLeft,>RgSIMON1_UPWALK1Left,>RgSIMON1_UPWALK2Left,>RgSIMON1_UPWALK3Left,>RgSIMON1_DIAGUPWALK1Left,>RgSIMON1_DIAGUPWALK2Left,>RgSIMON1_DIAGUPWALK3Left,>RgSIMON1_DIAGDOWNWALK1Left,>RgSIMON1_DIAGDOWNWALK2Left,>RgSIMON1_DIAGDOWNWALK3Left,>RgSIMON1_DOWNTHRUSTLeft,>RgSIMON1_UPTHRUSTLeft,>RgSIMON1_HURTLeft,>RgSIMON1_DIE1Left,>RgSIMON1_DIE2Left,>RgSIMON1_DIE3Left,>RgSIMON1_DIE4Left,>RgSIMON1_SLIDELeft,>RgSIMON1_CROUCHATTACK1Left,>RgSIMON1_CROUCHATTACK2Left,>RgSIMON1_CROUCHATTACK3Left,>RgSIMON1_CROUCHTHROW1Left,>RgSIMON1_CROUCHTHROW2Left,>RgSIMON1_CROUCHTHROW3Left,>RgSIMON1_DIEFLASH1Left,>RgSIMON1_DIEFLASH2Left,>RgSIMON1_DIEGRAYLeft,>RgSIMON1_DIECROSS1Left,>RgSIMON1_DIECROSS2Left,>RgSIMON2_STANDLeft,>RgSIMON2_WALK1Left,>RgSIMON2_WALK2Left,>RgSIMON2_WALK3Left,>RgSIMON2_JUMP1Left,>RgSIMON2_JUMP2Left,>RgSIMON2_JUMP3Left,>RgSIMON2_JUMP4Left,>RgSIMON2_CROUCHLeft,>RgSIMON2_ATTACK1Left,>RgSIMON2_ATTACK2Left,>RgSIMON2_ATTACK3Left,>RgSIMON2_THROW1Left,>RgSIMON2_THROW2Left,>RgSIMON2_THROW3Left,>RgSIMON2_CLIMB1Left,>RgSIMON2_CLIMB2Left,>RgSIMON2_UPSTANDLeft,>RgSIMON2_DIAGUPLeft,>RgSIMON2_DIAGDOWNLeft,>RgSIMON2_UPWALK1Left,>RgSIMON2_UPWALK2Left,>RgSIMON2_UPWALK3Left,>RgSIMON2_DIAGUPWALK1Left,>RgSIMON2_DIAGUPWALK2Left,>RgSIMON2_DIAGUPWALK3Left,>RgSIMON2_DIAGDOWNWALK1Left,>RgSIMON2_DIAGDOWNWALK2Left,>RgSIMON2_DIAGDOWNWALK3Left,>RgSIMON2_DOWNTHRUSTLeft,>RgSIMON2_UPTHRUSTLeft,>RgSIMON2_HURTLeft,>RgSIMON2_DIE1Left,>RgSIMON2_DIE2Left,>RgSIMON2_DIE3Left,>RgSIMON2_DIE4Left,>RgSIMON2_SLIDELeft,>RgSIMON2_CROUCHATTACK1Left,>RgSIMON2_CROUCHATTACK2Left,>RgSIMON2_CROUCHATTACK3Left,>RgSIMON2_CROUCHTHROW1Left,>RgSIMON2_CROUCHTHROW2Left,>RgSIMON2_CROUCHTHROW3Left,>RgSIMON2_DIEFLASH1Left,>RgSIMON2_DIEFLASH2Left,>RgSIMON2_DIEGRAYLeft,>RgSIMON2_DIECROSS1Left,>RgSIMON2_DIECROSS2Left
RgSIMONRightLo:
  .byte <RgSIMON0_STANDRight,<RgSIMON0_WALK1Right,<RgSIMON0_WALK2Right,<RgSIMON0_WALK3Right,<RgSIMON0_JUMP1Right,<RgSIMON0_JUMP2Right,<RgSIMON0_JUMP3Right,<RgSIMON0_JUMP4Right,<RgSIMON0_CROUCHRight,<RgSIMON0_ATTACK1Right,<RgSIMON0_ATTACK2Right,<RgSIMON0_ATTACK3Right,<RgSIMON0_THROW1Right,<RgSIMON0_THROW2Right,<RgSIMON0_THROW3Right,<RgSIMON0_CLIMB1Right,<RgSIMON0_CLIMB2Right,<RgSIMON0_UPSTANDRight,<RgSIMON0_DIAGUPRight,<RgSIMON0_DIAGDOWNRight,<RgSIMON0_UPWALK1Right,<RgSIMON0_UPWALK2Right,<RgSIMON0_UPWALK3Right,<RgSIMON0_DIAGUPWALK1Right,<RgSIMON0_DIAGUPWALK2Right,<RgSIMON0_DIAGUPWALK3Right,<RgSIMON0_DIAGDOWNWALK1Right,<RgSIMON0_DIAGDOWNWALK2Right,<RgSIMON0_DIAGDOWNWALK3Right,<RgSIMON0_DOWNTHRUSTRight,<RgSIMON0_UPTHRUSTRight,<RgSIMON0_HURTRight,<RgSIMON0_DIE1Right,<RgSIMON0_DIE2Right,<RgSIMON0_DIE3Right,<RgSIMON0_DIE4Right,<RgSIMON0_SLIDERight,<RgSIMON0_CROUCHATTACK1Right,<RgSIMON0_CROUCHATTACK2Right,<RgSIMON0_CROUCHATTACK3Right,<RgSIMON0_CROUCHTHROW1Right,<RgSIMON0_CROUCHTHROW2Right,<RgSIMON0_CROUCHTHROW3Right,<RgSIMON0_DIEFLASH1Right,<RgSIMON0_DIEFLASH2Right,<RgSIMON0_DIEGRAYRight,<RgSIMON0_DIECROSS1Right,<RgSIMON0_DIECROSS2Right,<RgSIMON1_STANDRight,<RgSIMON1_WALK1Right,<RgSIMON1_WALK2Right,<RgSIMON1_WALK3Right,<RgSIMON1_JUMP1Right,<RgSIMON1_JUMP2Right,<RgSIMON1_JUMP3Right,<RgSIMON1_JUMP4Right,<RgSIMON1_CROUCHRight,<RgSIMON1_ATTACK1Right,<RgSIMON1_ATTACK2Right,<RgSIMON1_ATTACK3Right,<RgSIMON1_THROW1Right,<RgSIMON1_THROW2Right,<RgSIMON1_THROW3Right,<RgSIMON1_CLIMB1Right,<RgSIMON1_CLIMB2Right,<RgSIMON1_UPSTANDRight,<RgSIMON1_DIAGUPRight,<RgSIMON1_DIAGDOWNRight,<RgSIMON1_UPWALK1Right,<RgSIMON1_UPWALK2Right,<RgSIMON1_UPWALK3Right,<RgSIMON1_DIAGUPWALK1Right,<RgSIMON1_DIAGUPWALK2Right,<RgSIMON1_DIAGUPWALK3Right,<RgSIMON1_DIAGDOWNWALK1Right,<RgSIMON1_DIAGDOWNWALK2Right,<RgSIMON1_DIAGDOWNWALK3Right,<RgSIMON1_DOWNTHRUSTRight,<RgSIMON1_UPTHRUSTRight,<RgSIMON1_HURTRight,<RgSIMON1_DIE1Right,<RgSIMON1_DIE2Right,<RgSIMON1_DIE3Right,<RgSIMON1_DIE4Right,<RgSIMON1_SLIDERight,<RgSIMON1_CROUCHATTACK1Right,<RgSIMON1_CROUCHATTACK2Right,<RgSIMON1_CROUCHATTACK3Right,<RgSIMON1_CROUCHTHROW1Right,<RgSIMON1_CROUCHTHROW2Right,<RgSIMON1_CROUCHTHROW3Right,<RgSIMON1_DIEFLASH1Right,<RgSIMON1_DIEFLASH2Right,<RgSIMON1_DIEGRAYRight,<RgSIMON1_DIECROSS1Right,<RgSIMON1_DIECROSS2Right,<RgSIMON2_STANDRight,<RgSIMON2_WALK1Right,<RgSIMON2_WALK2Right,<RgSIMON2_WALK3Right,<RgSIMON2_JUMP1Right,<RgSIMON2_JUMP2Right,<RgSIMON2_JUMP3Right,<RgSIMON2_JUMP4Right,<RgSIMON2_CROUCHRight,<RgSIMON2_ATTACK1Right,<RgSIMON2_ATTACK2Right,<RgSIMON2_ATTACK3Right,<RgSIMON2_THROW1Right,<RgSIMON2_THROW2Right,<RgSIMON2_THROW3Right,<RgSIMON2_CLIMB1Right,<RgSIMON2_CLIMB2Right,<RgSIMON2_UPSTANDRight,<RgSIMON2_DIAGUPRight,<RgSIMON2_DIAGDOWNRight,<RgSIMON2_UPWALK1Right,<RgSIMON2_UPWALK2Right,<RgSIMON2_UPWALK3Right,<RgSIMON2_DIAGUPWALK1Right,<RgSIMON2_DIAGUPWALK2Right,<RgSIMON2_DIAGUPWALK3Right,<RgSIMON2_DIAGDOWNWALK1Right,<RgSIMON2_DIAGDOWNWALK2Right,<RgSIMON2_DIAGDOWNWALK3Right,<RgSIMON2_DOWNTHRUSTRight,<RgSIMON2_UPTHRUSTRight,<RgSIMON2_HURTRight,<RgSIMON2_DIE1Right,<RgSIMON2_DIE2Right,<RgSIMON2_DIE3Right,<RgSIMON2_DIE4Right,<RgSIMON2_SLIDERight,<RgSIMON2_CROUCHATTACK1Right,<RgSIMON2_CROUCHATTACK2Right,<RgSIMON2_CROUCHATTACK3Right,<RgSIMON2_CROUCHTHROW1Right,<RgSIMON2_CROUCHTHROW2Right,<RgSIMON2_CROUCHTHROW3Right,<RgSIMON2_DIEFLASH1Right,<RgSIMON2_DIEFLASH2Right,<RgSIMON2_DIEGRAYRight,<RgSIMON2_DIECROSS1Right,<RgSIMON2_DIECROSS2Right
RgSIMONRightHi:
  .byte >RgSIMON0_STANDRight,>RgSIMON0_WALK1Right,>RgSIMON0_WALK2Right,>RgSIMON0_WALK3Right,>RgSIMON0_JUMP1Right,>RgSIMON0_JUMP2Right,>RgSIMON0_JUMP3Right,>RgSIMON0_JUMP4Right,>RgSIMON0_CROUCHRight,>RgSIMON0_ATTACK1Right,>RgSIMON0_ATTACK2Right,>RgSIMON0_ATTACK3Right,>RgSIMON0_THROW1Right,>RgSIMON0_THROW2Right,>RgSIMON0_THROW3Right,>RgSIMON0_CLIMB1Right,>RgSIMON0_CLIMB2Right,>RgSIMON0_UPSTANDRight,>RgSIMON0_DIAGUPRight,>RgSIMON0_DIAGDOWNRight,>RgSIMON0_UPWALK1Right,>RgSIMON0_UPWALK2Right,>RgSIMON0_UPWALK3Right,>RgSIMON0_DIAGUPWALK1Right,>RgSIMON0_DIAGUPWALK2Right,>RgSIMON0_DIAGUPWALK3Right,>RgSIMON0_DIAGDOWNWALK1Right,>RgSIMON0_DIAGDOWNWALK2Right,>RgSIMON0_DIAGDOWNWALK3Right,>RgSIMON0_DOWNTHRUSTRight,>RgSIMON0_UPTHRUSTRight,>RgSIMON0_HURTRight,>RgSIMON0_DIE1Right,>RgSIMON0_DIE2Right,>RgSIMON0_DIE3Right,>RgSIMON0_DIE4Right,>RgSIMON0_SLIDERight,>RgSIMON0_CROUCHATTACK1Right,>RgSIMON0_CROUCHATTACK2Right,>RgSIMON0_CROUCHATTACK3Right,>RgSIMON0_CROUCHTHROW1Right,>RgSIMON0_CROUCHTHROW2Right,>RgSIMON0_CROUCHTHROW3Right,>RgSIMON0_DIEFLASH1Right,>RgSIMON0_DIEFLASH2Right,>RgSIMON0_DIEGRAYRight,>RgSIMON0_DIECROSS1Right,>RgSIMON0_DIECROSS2Right,>RgSIMON1_STANDRight,>RgSIMON1_WALK1Right,>RgSIMON1_WALK2Right,>RgSIMON1_WALK3Right,>RgSIMON1_JUMP1Right,>RgSIMON1_JUMP2Right,>RgSIMON1_JUMP3Right,>RgSIMON1_JUMP4Right,>RgSIMON1_CROUCHRight,>RgSIMON1_ATTACK1Right,>RgSIMON1_ATTACK2Right,>RgSIMON1_ATTACK3Right,>RgSIMON1_THROW1Right,>RgSIMON1_THROW2Right,>RgSIMON1_THROW3Right,>RgSIMON1_CLIMB1Right,>RgSIMON1_CLIMB2Right,>RgSIMON1_UPSTANDRight,>RgSIMON1_DIAGUPRight,>RgSIMON1_DIAGDOWNRight,>RgSIMON1_UPWALK1Right,>RgSIMON1_UPWALK2Right,>RgSIMON1_UPWALK3Right,>RgSIMON1_DIAGUPWALK1Right,>RgSIMON1_DIAGUPWALK2Right,>RgSIMON1_DIAGUPWALK3Right,>RgSIMON1_DIAGDOWNWALK1Right,>RgSIMON1_DIAGDOWNWALK2Right,>RgSIMON1_DIAGDOWNWALK3Right,>RgSIMON1_DOWNTHRUSTRight,>RgSIMON1_UPTHRUSTRight,>RgSIMON1_HURTRight,>RgSIMON1_DIE1Right,>RgSIMON1_DIE2Right,>RgSIMON1_DIE3Right,>RgSIMON1_DIE4Right,>RgSIMON1_SLIDERight,>RgSIMON1_CROUCHATTACK1Right,>RgSIMON1_CROUCHATTACK2Right,>RgSIMON1_CROUCHATTACK3Right,>RgSIMON1_CROUCHTHROW1Right,>RgSIMON1_CROUCHTHROW2Right,>RgSIMON1_CROUCHTHROW3Right,>RgSIMON1_DIEFLASH1Right,>RgSIMON1_DIEFLASH2Right,>RgSIMON1_DIEGRAYRight,>RgSIMON1_DIECROSS1Right,>RgSIMON1_DIECROSS2Right,>RgSIMON2_STANDRight,>RgSIMON2_WALK1Right,>RgSIMON2_WALK2Right,>RgSIMON2_WALK3Right,>RgSIMON2_JUMP1Right,>RgSIMON2_JUMP2Right,>RgSIMON2_JUMP3Right,>RgSIMON2_JUMP4Right,>RgSIMON2_CROUCHRight,>RgSIMON2_ATTACK1Right,>RgSIMON2_ATTACK2Right,>RgSIMON2_ATTACK3Right,>RgSIMON2_THROW1Right,>RgSIMON2_THROW2Right,>RgSIMON2_THROW3Right,>RgSIMON2_CLIMB1Right,>RgSIMON2_CLIMB2Right,>RgSIMON2_UPSTANDRight,>RgSIMON2_DIAGUPRight,>RgSIMON2_DIAGDOWNRight,>RgSIMON2_UPWALK1Right,>RgSIMON2_UPWALK2Right,>RgSIMON2_UPWALK3Right,>RgSIMON2_DIAGUPWALK1Right,>RgSIMON2_DIAGUPWALK2Right,>RgSIMON2_DIAGUPWALK3Right,>RgSIMON2_DIAGDOWNWALK1Right,>RgSIMON2_DIAGDOWNWALK2Right,>RgSIMON2_DIAGDOWNWALK3Right,>RgSIMON2_DOWNTHRUSTRight,>RgSIMON2_UPTHRUSTRight,>RgSIMON2_HURTRight,>RgSIMON2_DIE1Right,>RgSIMON2_DIE2Right,>RgSIMON2_DIE3Right,>RgSIMON2_DIE4Right,>RgSIMON2_SLIDERight,>RgSIMON2_CROUCHATTACK1Right,>RgSIMON2_CROUCHATTACK2Right,>RgSIMON2_CROUCHATTACK3Right,>RgSIMON2_CROUCHTHROW1Right,>RgSIMON2_CROUCHTHROW2Right,>RgSIMON2_CROUCHTHROW3Right,>RgSIMON2_DIEFLASH1Right,>RgSIMON2_DIEFLASH2Right,>RgSIMON2_DIEGRAYRight,>RgSIMON2_DIECROSS1Right,>RgSIMON2_DIECROSS2Right
RgSIMONBanks:
  .byte $38,$38,$3a,$38,$39,$39,$39,$39,$39,$37,$3b,$35,$37,$33,$35,$d2,$3a,$38,$38,$38,$38,$38,$38,$38,$38,$38,$38,$38,$38,$38,$38,$39,$d2,$d2,$d2,$d2,$35,$36,$33,$35,$37,$33,$35,$38,$38,$38,$38,$38,$38,$38,$3a,$38,$39,$39,$39,$39,$39,$39,$33,$34,$37,$3b,$35,$d2,$3a,$38,$38,$38,$38,$38,$38,$38,$38,$38,$38,$38,$38,$38,$38,$39,$d2,$d2,$d2,$d2,$35,$37,$33,$d1,$37,$33,$35,$38,$38,$38,$38,$38,$38,$38,$3a,$38,$39,$39,$39,$39,$39,$37,$3b,$3a,$37,$3b,$35,$d2,$3a,$38,$38,$38,$38,$38,$38,$38,$38,$38,$38,$38,$38,$38,$38,$39,$36,$38,$38,$38,$35,$37,$3b,$d1,$37,$33,$35,$38,$38,$38,$38,$38
RgSIMONAXE1Left:
  .byte 16
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $82, -7, 0
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $42, -7, -8
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $83, -7, 0
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $83, -7, -8
RgSIMONAXE1Right:
  .byte 16
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $c2, -7, -8
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $02, -7, 0
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $c3, -7, -8
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c3, -7, 0
RgSIMONAXE2Left:
  .byte 16
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $02, -6, 0
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $82, -6, -8
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $c3, -7, 0
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $83, -7, -8
RgSIMONAXE2Right:
  .byte 16
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $42, -6, -8
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $c2, -6, 0
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $83, -7, -8
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c3, -7, 0
RgSIMONAXE3Left:
  .byte 16
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c2, -6, 0
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $42, -6, -8
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c3, -7, 0
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $83, -7, -8
RgSIMONAXE3Right:
  .byte 16
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $82, -6, -8
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $02, -6, 0
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $83, -7, -8
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c3, -7, 0
RgSIMONAXE4Left:
  .byte 16
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $82, -7, 0
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $c2, -7, -8
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c3, -7, 0
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c3, -7, -8
RgSIMONAXE4Right:
  .byte 16
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c2, -7, -8
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $82, -7, 0
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $83, -7, -8
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $83, -7, 0
RgSIMONWeaponsLeftLo:
  .byte <RgSIMONAXE1Left,<RgSIMONAXE2Left,<RgSIMONAXE3Left,<RgSIMONAXE4Left
RgSIMONWeaponsLeftHi:
  .byte >RgSIMONAXE1Left,>RgSIMONAXE2Left,>RgSIMONAXE3Left,>RgSIMONAXE4Left
RgSIMONWeaponsRightLo:
  .byte <RgSIMONAXE1Right,<RgSIMONAXE2Right,<RgSIMONAXE3Right,<RgSIMONAXE4Right
RgSIMONWeaponsRightHi:
  .byte >RgSIMONAXE1Right,>RgSIMONAXE2Right,>RgSIMONAXE3Right,>RgSIMONAXE4Right
.popseg
