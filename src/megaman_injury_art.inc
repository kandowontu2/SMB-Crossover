; Exact raw2.02 white injury pixels; source oracle is independent.
.pushseg
.segment "SAMUS_GFX"
MmHurtFx0:
 .byte 24
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $02, -13, -12
 .byte MetaspriteVramOffset{$02}, {SPRITE_BANK_0}, $42, -13, -4
 .byte MetaspriteVramOffset{$00}, {SPRITE_BANK_0}, $42, -13, 4
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $82, 3, -12
 .byte MetaspriteVramOffset{$06}, {SPRITE_BANK_0}, $c2, 3, -4
 .byte MetaspriteVramOffset{$04}, {SPRITE_BANK_0}, $c2, 3, 4
MmHurtFx1:
 .byte 4
 .byte MetaspriteVramOffset{$08}, {SPRITE_BANK_0}, $c2, -3, -2
MmHurtFx2:
 .byte 4
 .byte MetaspriteVramOffset{$0a}, {SPRITE_BANK_0}, $c2, -2, -2
MmHurtFx3:
 .byte 4
 .byte MetaspriteVramOffset{$0c}, {SPRITE_BANK_0}, $c2, -1, -3
MmHurtFxLo:
 .byte <MmHurtFx0,<MmHurtFx1,<MmHurtFx2,<MmHurtFx3
MmHurtFxHi:
 .byte >MmHurtFx0,>MmHurtFx1,>MmHurtFx2,>MmHurtFx3
.popseg
MM_HURT_BODY_BANK=$81
BASS_HURT_BODY_BANK=$82
MM_HURT_NORMAL_BANK=64
BASS_HURT_NORMAL_BANK=224
