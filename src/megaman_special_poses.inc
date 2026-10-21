; Mega Man 2.02 separate source arms.
.pushseg
.segment "XG_LUIGI_GFX"
SsMegaTHROWLeft:
  .byte 32
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, 0, 6
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 0, -2
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $40, 16, 14
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $00, 16, 6
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $40, 16, -2
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $c0, 16, -10
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $82, 14, -2
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $83, 14, -1
SsMegaTHROWRight:
  .byte 32
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 0, 2
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, 0, 10
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 16, -6
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $40, 16, 2
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $00, 16, 10
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $80, 16, 18
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $c2, 14, 10
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c3, 14, 9
SsMegaAIR_THROWLeft:
  .byte 32
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c0, 2, 13
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $40, 2, 5
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $00, 2, -3
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $00, 2, -11
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $80, 18, 5
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $c0, 18, -3
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $82, 8, 2
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $83, 8, 3
SsMegaAIR_THROWRight:
  .byte 32
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $80, 2, -5
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 2, 3
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $40, 2, 11
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $40, 2, 19
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c0, 18, 3
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $80, 18, 11
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c2, 8, 6
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c3, 8, 5
SsMegaFISTLeft:
  .byte 36
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 8, 11
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $40, 8, 3
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $00, 8, -5
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $40, 8, -13
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $80, 24, 11
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $c0, 24, 3
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 24, -5
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $82, 14, -2
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $83, 14, -1
SsMegaFISTRight:
  .byte 36
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 8, -3
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $00, 8, 5
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $40, 8, 13
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $00, 8, 21
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $c0, 24, -3
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $80, 24, 5
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 24, 13
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $c2, 14, 10
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c3, 14, 9
SsMegaAIR_FISTLeft:
  .byte 32
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $c0, 2, 13
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $40, 2, 5
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $00, 2, -3
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $00, 2, -11
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $80, 18, 5
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $c0, 18, -3
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $82, 8, 2
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $83, 8, 3
SsMegaAIR_FISTRight:
  .byte 32
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $80, 2, -5
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 2, 3
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $40, 2, 11
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $40, 2, 19
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c0, 18, 3
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $80, 18, 11
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c2, 8, 6
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $c3, 8, 5
SsMegaCARRYLeft:
  .byte 28
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $40, 2, 6
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $00, 2, -2
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $c0, 18, 14
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $80, 18, 6
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $c0, 18, -2
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $02, 2, 2
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $83, 14, 3
SsMegaCARRYRight:
  .byte 28
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $00, 2, 2
  .byte MetaspriteVramOffset{$34}, {SPRITE_BANK_0}, $40, 2, 10
  .byte MetaspriteVramOffset{$36}, {SPRITE_BANK_0}, $80, 18, -6
  .byte MetaspriteVramOffset{$38}, {SPRITE_BANK_0}, $c0, 18, 2
  .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_0}, $80, 18, 10
  .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_0}, $42, 2, 6
  .byte MetaspriteVramOffset{$3e}, {SPRITE_BANK_0}, $c3, 14, 5
SsMegaCARRY_STEPLeft:
  .byte 28
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $40, 2, 6
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 2, -2
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $c0, 18, 14
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $80, 18, 6
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $80, 18, -2
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $02, 2, 2
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $83, 14, 3
SsMegaCARRY_STEPRight:
  .byte 28
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $00, 2, 2
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, 2, 10
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $80, 18, -6
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c0, 18, 2
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c0, 18, 10
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $42, 2, 6
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $c3, 14, 5
SsMegaCARRY_WALK1Left:
  .byte 32
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $40, 9, 12
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $40, 9, 4
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $00, 9, -4
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $c0, 25, 12
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $c0, 25, 4
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $80, 25, -4
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $82, 16, 1
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $83, 16, 2
SsMegaCARRY_WALK1Right:
  .byte 32
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $00, 9, -4
  .byte MetaspriteVramOffset{$10}, {SPRITE_BANK_0}, $00, 9, 4
  .byte MetaspriteVramOffset{$12}, {SPRITE_BANK_0}, $40, 9, 12
  .byte MetaspriteVramOffset{$14}, {SPRITE_BANK_0}, $80, 25, -4
  .byte MetaspriteVramOffset{$16}, {SPRITE_BANK_0}, $80, 25, 4
  .byte MetaspriteVramOffset{$18}, {SPRITE_BANK_0}, $c0, 25, 12
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $c2, 16, 7
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c3, 16, 6
SsMegaCARRY_WALK2Left:
  .byte 28
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $40, 7, 9
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $40, 7, 1
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $80, 7, -7
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $c0, 23, 9
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $80, 23, 1
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $82, 14, 1
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $83, 14, 2
SsMegaCARRY_WALK2Right:
  .byte 28
  .byte MetaspriteVramOffset{$1e}, {SPRITE_BANK_0}, $00, 7, -1
  .byte MetaspriteVramOffset{$20}, {SPRITE_BANK_0}, $00, 7, 7
  .byte MetaspriteVramOffset{$22}, {SPRITE_BANK_0}, $c0, 7, 15
  .byte MetaspriteVramOffset{$24}, {SPRITE_BANK_0}, $80, 23, -1
  .byte MetaspriteVramOffset{$26}, {SPRITE_BANK_0}, $c0, 23, 7
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $c2, 14, 7
  .byte MetaspriteVramOffset{$1c}, {SPRITE_BANK_0}, $c3, 14, 6
SsMegaCARRY_WALK3Left:
  .byte 28
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $40, 1, 5
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $00, 1, -3
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $c0, 17, 13
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $c0, 17, 5
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $80, 17, -3
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $82, 16, 1
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $c3, 16, 2
SsMegaCARRY_WALK3Right:
  .byte 28
  .byte MetaspriteVramOffset{$28}, {SPRITE_BANK_0}, $00, 1, 3
  .byte MetaspriteVramOffset{$2a}, {SPRITE_BANK_0}, $40, 1, 11
  .byte MetaspriteVramOffset{$2c}, {SPRITE_BANK_0}, $80, 17, -5
  .byte MetaspriteVramOffset{$2e}, {SPRITE_BANK_0}, $80, 17, 3
  .byte MetaspriteVramOffset{$30}, {SPRITE_BANK_0}, $c0, 17, 11
  .byte MetaspriteVramOffset{$1a}, {SPRITE_BANK_0}, $c2, 16, 7
  .byte MetaspriteVramOffset{$32}, {SPRITE_BANK_0}, $83, 16, 6
SsMegaCARRY_JUMPLeft:
  .byte 32
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $c0, 2, 13
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $40, 2, 5
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $40, 2, -3
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $80, 2, -11
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $80, 18, 5
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $c0, 18, -3
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $82, 8, 2
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $83, 8, 3
SsMegaCARRY_JUMPRight:
  .byte 32
  .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $80, 2, -5
  .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $00, 2, 3
  .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $00, 2, 11
  .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c0, 2, 19
  .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c0, 18, 3
  .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $80, 18, 11
  .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $c2, 8, 6
  .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_0}, $c3, 8, 5
SsMegaLeftLo:
 .byte <SsMegaTHROWLeft,<SsMegaAIR_THROWLeft,<SsMegaFISTLeft,<SsMegaAIR_FISTLeft,<SsMegaCARRYLeft,<SsMegaCARRY_STEPLeft,<SsMegaCARRY_WALK1Left,<SsMegaCARRY_WALK2Left,<SsMegaCARRY_WALK3Left,<SsMegaCARRY_JUMPLeft
SsMegaLeftHi:
 .byte >SsMegaTHROWLeft,>SsMegaAIR_THROWLeft,>SsMegaFISTLeft,>SsMegaAIR_FISTLeft,>SsMegaCARRYLeft,>SsMegaCARRY_STEPLeft,>SsMegaCARRY_WALK1Left,>SsMegaCARRY_WALK2Left,>SsMegaCARRY_WALK3Left,>SsMegaCARRY_JUMPLeft
SsMegaRightLo:
 .byte <SsMegaTHROWRight,<SsMegaAIR_THROWRight,<SsMegaFISTRight,<SsMegaAIR_FISTRight,<SsMegaCARRYRight,<SsMegaCARRY_STEPRight,<SsMegaCARRY_WALK1Right,<SsMegaCARRY_WALK2Right,<SsMegaCARRY_WALK3Right,<SsMegaCARRY_JUMPRight
SsMegaRightHi:
 .byte >SsMegaTHROWRight,>SsMegaAIR_THROWRight,>SsMegaFISTRight,>SsMegaAIR_FISTRight,>SsMegaCARRYRight,>SsMegaCARRY_STEPRight,>SsMegaCARRY_WALK1Right,>SsMegaCARRY_WALK2Right,>SsMegaCARRY_WALK3Right,>SsMegaCARRY_JUMPRight
SsMegaBanks:
 .byte 170,170,170,170,170,171,171,171,171,172
.popseg
