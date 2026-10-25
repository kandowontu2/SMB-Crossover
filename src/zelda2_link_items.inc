; Original itemtile table prg7:EE7F..EEAC; native beam32/flame84 prg0:98E0.
.pushseg
.segment "Z2_GFX"
Z2ItemMAGIC:
 .byte 8
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_4}, $01, 0, -8
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_4}, $41, 0, 0
Z2ItemSWORD:
 .byte 4
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_4}, $01, 0, -4
Z2ItemFAIRY:
 .byte 4
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_4}, $01, 0, -4
Z2ItemHEART:
 .byte 8
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_4}, $01, 0, -8
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_4}, $41, 0, 0
Z2ItemFIRE:
 .byte 4
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_4}, $01, 0, -4
Z2ItemGLOVE:
 .byte 4
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_4}, $01, 0, -4
Z2ItemBLUE:
 .byte 4
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_4}, $01, 0, -4
Z2ItemRED:
 .byte 4
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_4}, $03, 0, -4
Z2ItemBAG:
 .byte 4
 .byte MetaspriteVramOffset{$0e}, {SPRITE_BANK_4}, $01, 0, -4
Z2ItemBEAM:
 .byte 4
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_4}, $01, 0, -4
Z2ItemPtrLo:
 .byte <Z2ItemMAGIC,<Z2ItemSWORD,<Z2ItemFAIRY,<Z2ItemHEART,<Z2ItemFIRE,<Z2ItemGLOVE,<Z2ItemBLUE,<Z2ItemRED,<Z2ItemBAG,<Z2ItemBEAM
Z2ItemPtrHi:
 .byte >Z2ItemMAGIC,>Z2ItemSWORD,>Z2ItemFAIRY,>Z2ItemHEART,>Z2ItemFIRE,>Z2ItemGLOVE,>Z2ItemBLUE,>Z2ItemRED,>Z2ItemBAG,>Z2ItemBEAM
.popseg
