.setcpu "6502"
.export BackgroundGuard, BackgroundHeight, ProbeFloor, ProbeSides, MiniBackground
.import MiniFireballTail,MiniFireballDrawReturn
.export MiniFireballDrawEntry,MiniFireballWeaponEntry,MiniFireballFresh
SelectedCharacter = $6002
SafecallA = $016a
FarcallTarget = $016c
FarCall = $015a

.macro target addr, bank
 lda #<addr
 sta FarcallTarget
 lda #>addr
 sta FarcallTarget+1
 lda #bank
.endmacro

.segment "MINI_CONSTANT_GATE"
MiniConstants:
 ; Existing B83B ingress performs CMP#41 in the source-owned five bytes
 ; ending with the unlabeled .word$FFFF immediately before GmOnlyCommon.
 bne OtherConstant
 cpy #34
 bne NonWeaponConstant
 lda $075b
 lsr
 ora $25
 beq HandledConstant
OtherConstant:
 jmp ConstantForeign
NonWeaponConstant:
 cpy #9
 beq HandledConstant
 cpy #29
 bne OtherConstant
 pla
 tay
 plp
 lda SafecallA
 clc
 rts
HandledConstant:
 jmp ConstantHandled
.segment "MINI_CONSTANT_FOREIGN"
ConstantForeign:
 cmp #34
 jmp $bf7e
ConstantHandled:
 pla
 tay
 plp
 lda SafecallA
 sec
 rts

.segment "DRAW_GATE"
.export MiniDrawGate
MiniDrawGate:
 php
 pha
 lda SelectedCharacter
 cmp #41
 bne DrawLegacy
 lda $0f
 cmp #8
 bne DrawLegacy
 lda $7ff7
 ora $079c
 ora $6f1d
 ora $6007
 ora $7387
 bne DrawLegacy
MiniDrawGoto:
 .byte $f0, <($bd86-($bd28+(MiniDrawGoto-MiniDrawGate)+2))
DrawLegacy:
 pla
 plp
 sta SafecallA
 target $b3c5, $be
 jmp FarCall
TileInert:
 tax
 beq InertYes
 lda $ef36,x
 and #3
 cmp #1
 bne InertNo
 txa
 eor #$c2
 lsr a
 beq InertNo
InertYes:
 sec
 rts
InertNo:
 clc
 rts
.segment "BG_SIDES"
BackgroundExit:
 lda #0
 sta $03
 lda #19
 sta $0106
 dey
 ldx #0
 lda #0
 sec
 rts

.segment "DRAW_FAST"
CheckObjects:
 pla
 plp
 target $b07c, $9a
 jsr FarCall
 jsr $e7bd
 lda #1
 sta $6c0b
 target $acf7, $c8
 jsr FarCall
 target $a325, $84
 jsr FarCall
 lda #0
 sta $6c07
 sta SafecallA
 lda $7da1
 pha
 lda #2
 sta $7da1
 sta $5116
 target $a006, 3
 jsr FarCall
 pla
 jsr $80c2
 target $a155, $84
 jmp FarCall

.segment "GFX_GATE"
.export MiniGraphicsGate
MiniGraphicsGate:
 php
 pha
 lda SelectedCharacter
 cmp #41
 bne GraphicsLegacy
 lda $0f
 cmp #8
 bne GraphicsLegacy
 pla
 plp
 jmp MiniGraphics
GraphicsLegacy:
 pla
 plp
 php
 pha
 txa
 jmp $b3c5
GraphicsTail:
 lda #1
 sta $73ee
 sta $0146
 sec
 rts

.segment "GFX_BODY"
MiniGraphics:
 ; Exact MiniHostGraphics writes in the active game engine.
 lda #$c8
 sta $014b
 sta $7e06
 lda #$83
 sta $73e4
 lda #3
 sta $73ec
 lda #1
 sta $7e05
 lda #0
 sta $06e1
 lda #4
 sta $6b05
 lda #$05
 sta $6b06
 lda #$6b
 sta $6b07
 jmp MiniFireballGraphics

.segment "GFX_FIREBALL"
MiniFireballGraphics:
 lda #$c7
 sta $014c
 lda #$83
 sta $73e5
 jmp GraphicsTail

.segment "MINI_FB_META"
MiniFireballDrawEntry:
 php
 sta SafecallA
 target MiniFireballDrawReturn, $d9
 jsr FarCall
 plp
 sec
 rts
MiniFireballWeaponEntry:
 target MiniFireballTail, $d9
 jmp FarCall

.segment "MINI_FB_LIFE"
MiniFireballFresh:
 lda #0
 sta $25
 sta $26
 sta $06e8
 sta $06e9
 ; MiniInit's exact final address is bound by the builder after relinking.
 .import MiniLinkedInit
 jmp MiniLinkedInit

.segment "BG_WRAPPER"
MiniBackground:
 jsr BackgroundGuard
 bcc BackgroundLegacy
 lda #$ff
 sta $063c
 lda $04
 beq AirState
 lda #0
 sta $1e
 sta $8e
 sta $0602
 sta $063b
 jmp BackgroundExit
AirState:
 lda $1e
 cmp #1
 beq AirDone
AirFall:
 lda #2
 sta $1e
AirDone:
 jmp BackgroundExit
BackgroundLegacy:
 jmp $9b5b

.segment "BG_GUARD"
BackgroundGuard:
 lda SelectedCharacter
 cmp #41
 bne GuardNo
 lda $0f
 eor #8
 ora $0719
 ora $0706
 ora $0711
 ora $6006
 bne GuardNo
 jsr BackgroundHeight
 bcc GuardNo
 ldy #14
 jsr $9587
 jsr TileInert
 bcc GuardNo
 jsr ProbeFloor
 bcc GuardNo
 jmp ProbeSides
GuardNo:
 clc
 rts

.segment "BG_PROBES"
ProbeFloor:
 ldy #14
 jsr $9586
 sta $04
 jsr $9586
 cmp $04
 bne FloorNo
 cmp #0
 beq FloorReady
 cmp #$54
 bne FloorNo
 ldx $8e
 bmi FloorNo
 lda $bd
 and #15
 bne FloorNo
FloorReady:
 sec
 rts
FloorNo:
 clc
 rts

.segment "BG_SIDES"
BackgroundHeight:
 lda $a4
 cmp #1
 bne SidesNo
 lda $bd
 cmp #32
 bcc SidesNo
 cmp #207
 bcs SidesNo
 sec
 rts
ProbeSides:
 ldy #17
SideLoop:
 jsr $958b
 jsr TileInert
 bcc SidesNo
 iny
 cpy #21
 bne SideLoop
 rts
SidesNo:
 clc
 rts
