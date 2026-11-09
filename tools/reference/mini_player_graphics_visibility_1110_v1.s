; Exact MMC5 PlayerGfxHandler extent in physical PRG1.
; FAST=0 reproduces the incumbent linked code for the preimage check.
.setcpu "6502"
.export PlayerGraphics, CommonGraphics, GraphicsEnd
.segment "CODE"

Selected = $6002
Death = $6007
Engine = $0f
MarioVariant = $730a
ObjectMetasprite = $06e1
GuestVisible = $912b
SavedA = $016a
TargetLo = $016c
TargetHi = $016d
FarCall = $015a
FindPlayerAction = $a392
DoChangeSize = $a398
PlayerKilled = $a39e

.macro Packet target, bank
    sta SavedA
    lda #<target
    sta TargetLo
    lda #>target
    sta TargetHi
    lda #bank
.endmacro

.macro GraphicsTail target, bank
    Packet target, bank
    .if FAST
        bne FarTail             ; all three existing bank tags are nonzero
    .else
        jsr FarCall
        rts
    .endif
.endmacro

PlayerGraphics:
.if FAST
    pha
    lda Selected
    cmp #41
    bne Visibility
    lda Death
    bne Visibility
    pla
    bcs CommonGraphics          ; common route replaces NZC and all SMC
Variant:
    lda MarioVariant
    cmp #3
    bcc CommonGraphics
    sta SavedA
    lda #$90
    sta TargetLo
    lda #$b6
    sta TargetHi
    bcs VariantTail             ; carry is set by the variant comparison
Visibility:
    pla
    jsr GuestVisible
    bcc ClearMario
Visible:
    lda Selected
    beq Variant
    lda Death
    beq CommonGraphics
    lda Engine
    cmp #$0b
    bne ClearMario
.else
    jsr GuestVisible
    bcs Visible
    jmp ClearMario
Visible:
    lda Selected
    beq DeathGraphicsReady
    lda Death
    beq DeathGraphicsReady
    lda Engine
    cmp #$0b
    beq DeathGraphicsReady
    lda #0
    sta ObjectMetasprite
    rts
DeathGraphicsReady:
    lda Selected
    bne CommonGraphics
    lda MarioVariant
    cmp #3
    bcc CommonGraphics
    Packet $b690, $be
    jmp FarCall
.endif

CommonGraphics:
    .assert CommonGraphics-PlayerGraphics = $3c, error, "keep KmNativeGraphics entry fixed"
    lda Selected
    cmp #6
    bcc Roster
    GraphicsTail $b3c2, $c2
.if FAST
VariantTail:
    lda #$be
FarTail:
    jmp FarCall
ClearMario:
    lda #0
    sta ObjectMetasprite
    rts
.endif
Roster:
    cmp #3
    bcc Samus
    GraphicsTail $a8ba, $d2
Samus:
    cmp #2
    bne MegaMan
    GraphicsTail $bb1c, $df
MegaMan:
    cmp #1
    bne Vanilla
    jmp $ab87
Vanilla:
    lda Engine
    cmp #$0b
KilledBranch:
    .byte $f0, <(PlayerKilled - ($a2cd + (KilledBranch - PlayerGraphics) + 2))
    lda $070d
SizeBranch:
    .byte $d0, <(DoChangeSize - ($a2cd + (SizeBranch - PlayerGraphics) + 2))
    jsr FindPlayerAction
    lda $0706
    beq Exit
    lda $1e
    beq Exit
    lda $0e
    and #4
    bne Exit
    lda ObjectMetasprite
    cmp #$3b
    beq GlitchySprite
    cmp #$3d
    beq GlitchySprite
    clc
    adc #3
    sta ObjectMetasprite
    bne Exit
GlitchySprite:
    inc ObjectMetasprite
Exit:
    rts
.if FAST
    .res 1,$ea
.else
ClearMario:
    lda #0
    sta ObjectMetasprite
    rts
.endif
GraphicsEnd:
.assert GraphicsEnd-PlayerGraphics = $c5, error, "keep following player graphics entries fixed"
